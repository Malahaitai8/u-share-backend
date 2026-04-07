<template>
  <div class="image-recognition-container">
    <!-- AI对话框 -->
    <AIChatDialog v-model="showAIChat" />
    
    <!-- 顶部导航栏 -->
    <div class="nav-bar">
      <el-button 
        class="back-button" 
        @click="goBack"
        circle
        size="small"
      >
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h1 class="nav-title">图像识别</h1>
      <el-button
        class="ai-chat-button"
        @click="openAIChat"
        circle
        size="small"
      >
        <el-icon><ChatDotRound /></el-icon>
      </el-button>
    </div>

    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 上传卡片 -->
      <div class="upload-card">
        <div class="card-header">
          <div class="icon-wrapper">
            <el-icon class="camera-icon"><Camera /></el-icon>
          </div>
          <h3 class="card-title">图像识别</h3>
          <p class="card-subtitle">上传图片识别垃圾分类</p>
        </div>

        <!-- 图片预览区域 -->
        <div class="image-preview" v-if="previewImage">
          <img :src="previewImage" alt="预览图片" />
          <div class="image-overlay">
            <el-button 
              circle
              size="large"
              @click="removeImage"
              class="remove-button"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 上传区域 -->
        <div v-else class="upload-area" @click="triggerUpload">
          <input 
            ref="fileInput" 
            type="file" 
            accept="image/*"
            @change="handleFileChange"
            style="display: none"
          />
          <div class="upload-icon">
            <el-icon><Plus /></el-icon>
          </div>
          <p class="upload-text">点击上传图片</p>
          <p class="upload-hint">支持 JPG、PNG、GIF 格式</p>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons" v-if="previewImage && !result">
          <el-button 
            type="primary" 
            size="large"
            @click="handleRecognize"
            :loading="recognizing"
          >
            <el-icon v-if="!recognizing"><Search /></el-icon>
            <span>{{ recognizing ? '识别中...' : '开始识别' }}</span>
          </el-button>
          <el-button 
            size="large"
            @click="removeImage"
          >
            <el-icon><RefreshRight /></el-icon>
            <span>重新上传</span>
          </el-button>
        </div>
      </div>

      <!-- 结果卡片 -->
      <transition name="fade-slide">
        <div v-if="result" class="result-card">
          <div class="result-header">
            <div class="result-icon" :class="resultIconClass">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <h3 class="result-title">识别结果</h3>
            <div class="confidence-badge">
              置信度: {{ result.confidence }}%
            </div>
          </div>

          <div class="result-content">
            <div class="result-item">
              <span class="result-label">垃圾名称：</span>
              <span class="result-value">{{ result.name }}</span>
            </div>
            
            <div class="result-item highlight">
              <span class="result-label">分类类型：</span>
              <span class="result-value type-badge" :class="result.typeClass">
                {{ result.type }}
              </span>
            </div>
            
            <div class="result-item">
              <span class="result-label">投放说明：</span>
              <span class="result-value">{{ result.description }}</span>
            </div>

            <div v-if="result.tips" class="tips-box">
              <div class="tips-header">
                <el-icon><InfoFilled /></el-icon>
                <span>温馨提示</span>
              </div>
              <p class="tips-content">{{ result.tips }}</p>
            </div>

            <!-- 相似物品 -->
            <div v-if="result.similar" class="similar-items">
              <h4 class="similar-title">相似物品</h4>
              <div class="similar-list">
                <div 
                  v-for="item in result.similar" 
                  :key="item.name"
                  class="similar-item"
                >
                  <span class="similar-name">{{ item.name }}</span>
                  <span class="similar-match">{{ item.match }}%</span>
                </div>
              </div>
            </div>
          </div>

          <el-button 
            type="primary" 
            size="large"
            class="new-recognition-button"
            @click="resetAll"
          >
            <el-icon><Plus /></el-icon>
            <span>识别新的图片</span>
          </el-button>
        </div>
      </transition>

      <!-- 使用说明 -->
      <div class="tips-section">
        <h4 class="tips-title">📷 拍摄技巧</h4>
        <div class="tips-list">
          <div class="tip-item">
            <span class="tip-number">1</span>
            <span class="tip-text">确保光线充足，避免阴影遮挡</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">2</span>
            <span class="tip-text">将物品放在纯色背景上拍摄</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">3</span>
            <span class="tip-text">保持镜头清晰，避免模糊</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">4</span>
            <span class="tip-text">物品尽量占据画面中心位置</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部安全区域 -->
    <div class="safe-area-bottom"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { recognizeImage, addClassificationRecord } from '@/api/classification'
import AIChatDialog from '@/components/AIChatDialog.vue'

const router = useRouter()

const fileInput = ref(null)
const previewImage = ref('')
const recognizing = ref(false)
const result = ref(null)
const uploadedFile = ref(null)
const showAIChat = ref(false)

const goBack = () => {
  router.back()
}

const openAIChat = () => {
  showAIChat.value = true
}

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('请上传 JPG、PNG、GIF 或 WebP 格式的图片')
    return
  }
  
  // 检查文件大小（限制10MB）
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    return
  }
  
  uploadedFile.value = file
  
  // 读取并预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target?.result
    result.value = null
  }
  reader.readAsDataURL(file)
  
  ElMessage.success('图片上传成功')
}

const removeImage = () => {
  previewImage.value = ''
  uploadedFile.value = null
  result.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleRecognize = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }
  
  recognizing.value = true
  
  try {
    // 调用真实的图像识别API
    const response = await recognizeImage(uploadedFile.value)
    
    // 处理识别结果
    result.value = response.data
    
    // 添加分类记录并获得积分
    await addClassificationRecord(response.data.type, 'image')
    
    ElMessage.success('识别成功')
  } catch (error) {
    console.error('Recognition error:', error)
    ElMessage.error(error.message || '识别失败，请重试')
  } finally {
    recognizing.value = false
  }
}


const resetAll = () => {
  removeImage()
}

const resultIconClass = computed(() => {
  if (!result.value) return ''
  return result.value.typeClass
})
</script>

<style lang="scss" scoped>
.image-recognition-container {
  height: 100vh;
  background: linear-gradient(180deg, #9C27B0 0%, #BA68C8 100%);
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  overflow-y: auto;
}

// 导航栏样式
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  
  .back-button,
  .ai-chat-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 40px;
    height: 40px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
  
  .ai-chat-button {
    .el-icon {
      font-size: 18px;
    }
  }
  
  .nav-title {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin: 0;
  }
}

// 主要内容
.content {
  flex: 1;
  padding: 20px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

// 上传卡片
.upload-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  
  .card-header {
    text-align: center;
    margin-bottom: 24px;
    
    .icon-wrapper {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      box-shadow: 0 8px 20px rgba(156, 39, 176, 0.3);
      
      .camera-icon {
        font-size: 32px;
        color: white;
      }
    }
    
    .card-title {
      font-size: 20px;
      font-weight: 600;
      color: #333;
      margin: 0 0 8px 0;
    }
    
    .card-subtitle {
      font-size: 14px;
      color: #666;
      margin: 0;
    }
  }
  
  .image-preview {
    position: relative;
    width: 100%;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    background: #f5f5f5;
    
    img {
      width: 100%;
      height: auto;
      display: block;
      max-height: 400px;
      object-fit: contain;
    }
    
    .image-overlay {
      position: absolute;
      top: 12px;
      right: 12px;
      
      .remove-button {
        background: rgba(0, 0, 0, 0.6);
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        
        &:hover {
          background: rgba(0, 0, 0, 0.8);
        }
      }
    }
  }
  
  .upload-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    border: 2px dashed #BA68C8;
    border-radius: 16px;
    background: #F3E5F5;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 20px;
    
    &:hover {
      border-color: #9C27B0;
      background: #E1BEE7;
      transform: translateY(-2px);
    }
    
    .upload-icon {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%);
      border-radius: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      
      .el-icon {
        font-size: 32px;
        color: white;
      }
    }
    
    .upload-text {
      font-size: 16px;
      font-weight: 600;
      color: #9C27B0;
      margin: 0 0 8px 0;
    }
    
    .upload-hint {
      font-size: 13px;
      color: #999;
      margin: 0;
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 12px;
    
    .el-button {
      flex: 1;
      height: 48px;
      font-size: 15px;
      font-weight: 600;
      border-radius: 12px;
    }
  }
}

// 结果卡片
.result-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  
  .result-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    
    .result-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .el-icon {
        font-size: 24px;
        color: white;
      }
      
      &.recyclable {
        background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
      }
      
      &.harmful {
        background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
      }
      
      &.kitchen {
        background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
      }
      
      &.other {
        background: linear-gradient(135deg, #757575 0%, #9E9E9E 100%);
      }
    }
    
    .result-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0;
      flex: 1;
    }
    
    .confidence-badge {
      padding: 6px 12px;
      background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
      color: white;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }
  }
  
  .result-content {
    margin-bottom: 20px;
    
    .result-item {
      display: flex;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-of-type {
        border-bottom: none;
      }
      
      &.highlight {
        background: linear-gradient(90deg, rgba(156, 39, 176, 0.05) 0%, rgba(156, 39, 176, 0) 100%);
        margin: 0 -12px;
        padding: 12px;
        border-radius: 8px;
      }
      
      .result-label {
        font-size: 14px;
        color: #666;
        width: 80px;
        flex-shrink: 0;
      }
      
      .result-value {
        font-size: 15px;
        color: #333;
        font-weight: 500;
        flex: 1;
        
        &.type-badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 600;
          color: white;
          
          &.recyclable {
            background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
          }
          
          &.harmful {
            background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
          }
          
          &.kitchen {
            background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
          }
          
          &.other {
            background: linear-gradient(135deg, #757575 0%, #9E9E9E 100%);
          }
        }
      }
    }
    
    .tips-box {
      margin-top: 16px;
      padding: 16px;
      background: #FFF8E1;
      border-radius: 12px;
      border-left: 4px solid #FFC107;
      
      .tips-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #F57C00;
        
        .el-icon {
          font-size: 16px;
        }
      }
      
      .tips-content {
        font-size: 13px;
        color: #666;
        line-height: 1.6;
        margin: 0;
      }
    }
    
    .similar-items {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 2px dashed #e0e0e0;
      
      .similar-title {
        font-size: 15px;
        font-weight: 600;
        color: #333;
        margin: 0 0 12px 0;
      }
      
      .similar-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .similar-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 12px;
          background: #f5f5f5;
          border-radius: 8px;
          
          .similar-name {
            font-size: 14px;
            color: #333;
          }
          
          .similar-match {
            font-size: 13px;
            font-weight: 600;
            color: #9C27B0;
          }
        }
      }
    }
  }
  
  .new-recognition-button {
    width: 100%;
    height: 48px;
    font-size: 15px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%);
    border: none;
    
    &:hover {
      background: linear-gradient(135deg, #7B1FA2 0%, #AB47BC 100%);
    }
  }
}

// 使用说明
.tips-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  
  .tips-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 0 0 16px 0;
  }
  
  .tips-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .tip-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      
      .tip-number {
        width: 24px;
        height: 24px;
        background: #9C27B0;
        color: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        flex-shrink: 0;
      }
      
      .tip-text {
        font-size: 14px;
        color: #666;
        line-height: 24px;
      }
    }
  }
}

// 底部安全区域
.safe-area-bottom {
  height: 34px;
  background: rgba(0, 0, 0, 0.05);
}

// 过渡动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

// 响应式设计
@media (max-width: 375px) {
  .content {
    padding: 16px;
  }
  
  .upload-card,
  .result-card {
    padding: 20px;
  }
  
  .upload-area {
    padding: 36px 20px;
  }
}

// 进入动画
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.upload-card,
.tips-section {
  animation: fadeInUp 0.6s ease-out;
}

.tips-section {
  animation-delay: 0.2s;
}
</style>


