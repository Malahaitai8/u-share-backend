<template>
  <div class="voice-recognition-container">
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
      <h1 class="nav-title">语音识别</h1>
      <div class="nav-placeholder"></div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 录音卡片 -->
      <div class="recording-card">
        <div class="card-header">
          <div class="icon-wrapper">
            <el-icon class="microphone-icon"><Microphone /></el-icon>
          </div>
          <h3 class="card-title">语音识别垃圾分类</h3>
          <p class="card-subtitle">点击录音按钮说出垃圾名称</p>
        </div>

        <!-- 录音按钮 -->
        <div class="recording-control">
          <div 
            class="record-button" 
            :class="{ recording: isRecording, processing: isProcessing }"
            @click="toggleRecording"
          >
            <div class="button-waves" v-if="isRecording">
              <div class="wave"></div>
              <div class="wave"></div>
              <div class="wave"></div>
            </div>
            <el-icon class="record-icon">
              <Microphone v-if="!isRecording && !isProcessing" />
              <Loading v-else-if="isProcessing" />
              <VideoPause v-else />
            </el-icon>
          </div>
          <p class="record-status">
            {{ recordStatus }}
          </p>
        </div>

        <!-- 识别文本显示 -->
        <div v-if="recognizedText" class="recognized-text">
          <div class="text-label">识别到的文字：</div>
          <div class="text-content">{{ recognizedText }}</div>
        </div>

        <!-- 操作按钮 -->
        <div v-if="recognizedText && !result" class="action-buttons">
          <el-button 
            type="primary" 
            size="large"
            @click="handleAnalyze"
            :loading="analyzing"
          >
            <el-icon><Search /></el-icon>
            <span>{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </el-button>
          <el-button 
            size="large"
            @click="resetRecording"
          >
            <el-icon><RefreshRight /></el-icon>
            <span>重新录音</span>
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
          </div>

          <el-button 
            type="primary" 
            size="large"
            class="new-record-button"
            @click="resetAll"
          >
            <el-icon><Plus /></el-icon>
            <span>识别新的垃圾</span>
          </el-button>
        </div>
      </transition>

      <!-- 使用说明 -->
      <div class="tips-section">
        <h4 class="tips-title">💡 使用说明</h4>
        <div class="tips-list">
          <div class="tip-item">
            <span class="tip-number">1</span>
            <span class="tip-text">点击中央麦克风按钮开始录音</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">2</span>
            <span class="tip-text">清晰地说出垃圾名称，如"塑料瓶"</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">3</span>
            <span class="tip-text">再次点击按钮停止录音，开始识别</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">4</span>
            <span class="tip-text">查看识别结果和投放建议</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部安全区域 -->
    <div class="safe-area-bottom"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { speechToText } from '@/api/classification'

const router = useRouter()

const isRecording = ref(false)
const isProcessing = ref(false)
const analyzing = ref(false)
const recognizedText = ref('')
const result = ref(null)
const recordingStartTime = ref(0)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const stream = ref(null)

const goBack = () => {
  router.back()
}

const recordStatus = computed(() => {
  if (isProcessing.value) return '正在处理语音...'
  if (isRecording.value) return '正在录音...点击停止'
  return '点击按钮开始录音'
})

const toggleRecording = async () => {
  if (isProcessing.value) return
  
  if (!isRecording.value) {
    // 开始录音
    await startRecording()
  } else {
    // 停止录音
    stopRecording()
  }
}

const startRecording = async () => {
  try {
    // 请求麦克风权限
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
      } 
    })
    
    // 创建 MediaRecorder
    mediaRecorder.value = new MediaRecorder(stream.value, {
      mimeType: 'audio/webm;codecs=opus'
    })
    
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    mediaRecorder.value.onstop = () => {
      processRecording()
    }
    
    // 开始录音
    mediaRecorder.value.start(100) // 每100ms收集一次数据
    isRecording.value = true
    recordingStartTime.value = Date.now()
    recognizedText.value = ''
    result.value = null
    
    ElMessage.info('开始录音，请说出垃圾名称')
  } catch (error) {
    console.error('录音启动失败:', error)
    ElMessage.error('无法访问麦克风，请检查权限设置')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    
    // 停止所有音频轨道
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
    }
  }
}

const processRecording = async () => {
  const duration = Date.now() - recordingStartTime.value
  
  if (duration < 500) {
    ElMessage.warning('录音时间太短，请重新录音')
    return
  }
  
  isProcessing.value = true
  
  try {
    // 创建音频 Blob
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
    
    // 调用语音识别API
    const response = await speechToText(audioBlob)
    
    // 处理识别结果
    recognizedText.value = response.data.name
    result.value = response.data
    
    ElMessage.success('语音识别成功')
  } catch (error) {
    console.error('语音识别失败:', error)
    ElMessage.error(error.message || '语音识别失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const handleAnalyze = async () => {
  if (!recognizedText.value) return
  
  analyzing.value = true
  
  try {
    // 语音识别已经包含了分类结果，直接使用
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败，请重试')
    console.error('Analysis error:', error)
  } finally {
    analyzing.value = false
  }
}

// 清理资源
const cleanup = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
  if (mediaRecorder.value) {
    mediaRecorder.value = null
  }
  audioChunks.value = []
}

// 组件挂载和卸载时的处理
onMounted(() => {
  // 检查浏览器支持
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    ElMessage.warning('您的浏览器不支持录音功能')
  }
})

onUnmounted(() => {
  cleanup()
})


const resetRecording = () => {
  recognizedText.value = ''
  result.value = null
}

const resetAll = () => {
  recognizedText.value = ''
  result.value = null
  isRecording.value = false
  isProcessing.value = false
}

const resultIconClass = computed(() => {
  if (!result.value) return ''
  return result.value.typeClass
})
</script>

<style lang="scss" scoped>
.voice-recognition-container {
  height: 100vh;
  background: linear-gradient(180deg, #FF9800 0%, #FFB74D 100%);
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
  
  .back-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 40px;
    height: 40px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
  
  .nav-title {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin: 0;
  }
  
  .nav-placeholder {
    width: 40px;
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

// 录音卡片
.recording-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 32px 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  
  .card-header {
    text-align: center;
    margin-bottom: 32px;
    
    .icon-wrapper {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      box-shadow: 0 8px 20px rgba(255, 152, 0, 0.3);
      
      .microphone-icon {
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
  
  .recording-control {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 24px;
    
    .record-button {
      position: relative;
      width: 120px;
      height: 120px;
      background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
      border-radius: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 8px 24px rgba(255, 152, 0, 0.4);
      margin-bottom: 20px;
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 32px rgba(255, 152, 0, 0.5);
      }
      
      &:active {
        transform: scale(0.98);
      }
      
      &.recording {
        background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
        animation: pulse 1.5s ease-in-out infinite;
      }
      
      &.processing {
        background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
        cursor: not-allowed;
      }
      
      .button-waves {
        position: absolute;
        width: 100%;
        height: 100%;
        
        .wave {
          position: absolute;
          width: 100%;
          height: 100%;
          border-radius: 50%;
          border: 2px solid rgba(255, 255, 255, 0.4);
          animation: wave-animation 1.5s ease-out infinite;
          
          &:nth-child(2) {
            animation-delay: 0.5s;
          }
          
          &:nth-child(3) {
            animation-delay: 1s;
          }
        }
      }
      
      .record-icon {
        font-size: 48px;
        color: white;
        z-index: 1;
      }
    }
    
    .record-status {
      font-size: 15px;
      font-weight: 500;
      color: #666;
      margin: 0;
      text-align: center;
    }
  }
  
  .recognized-text {
    background: #F5F5F5;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    
    .text-label {
      font-size: 13px;
      color: #999;
      margin-bottom: 8px;
    }
    
    .text-content {
      font-size: 18px;
      font-weight: 600;
      color: #333;
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
    }
  }
  
  .result-content {
    margin-bottom: 20px;
    
    .result-item {
      display: flex;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      &.highlight {
        background: linear-gradient(90deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 152, 0, 0) 100%);
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
  }
  
  .new-record-button {
    width: 100%;
    height: 48px;
    font-size: 15px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
    border: none;
    
    &:hover {
      background: linear-gradient(135deg, #F57C00 0%, #FFA726 100%);
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
        background: #FF9800;
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

// 动画
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 8px 24px rgba(244, 67, 54, 0.4);
  }
  50% {
    box-shadow: 0 8px 32px rgba(244, 67, 54, 0.6);
  }
}

@keyframes wave-animation {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

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
  
  .recording-card {
    padding: 24px 20px;
  }
  
  .record-button {
    width: 100px !important;
    height: 100px !important;
    
    .record-icon {
      font-size: 40px !important;
    }
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

.recording-card,
.tips-section {
  animation: fadeInUp 0.6s ease-out;
}

.tips-section {
  animation-delay: 0.2s;
}
</style>

