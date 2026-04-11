<template>
  <div class="classification-container with-bottom-nav">
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
      <h1 class="nav-title">垃圾分类识别</h1>
      <div class="nav-placeholder"></div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 标题卡片 -->
      <div class="header-card">
        <img src="/beijingfuben.png" alt="垃圾分类示意图" class="header-image" />
        <p class="header-subtitle">选择一种识别方式开始使用</p>
      </div>

      <!-- 功能选择卡片 -->
      <div class="function-cards">
        <div class="function-card" @click="goToTextRecognition">
          <div class="card-icon text-icon">
            <el-icon><EditPen /></el-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">文字识别</h3>
            <p class="card-description">输入文字，智能识别垃圾类型</p>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="function-card" @click="goToVoiceRecognition">
          <div class="card-icon voice-icon">
            <el-icon><Microphone /></el-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">语音识别</h3>
            <p class="card-description">说出垃圾名称，语音转文字识别</p>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="function-card" @click="goToImageRecognition">
          <div class="card-icon image-icon">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">图像识别</h3>
            <p class="card-description">拍照或上传图片，AI智能识别</p>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 使用提示 -->
      <div class="tips-section">
        <h4 class="tips-title">💡 使用提示</h4>
        <div class="tips-list">
          <div class="tip-item">
            <span class="tip-number">1</span>
            <span class="tip-text">文字识别：直接输入垃圾名称，如"塑料瓶"</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">2</span>
            <span class="tip-text">语音识别：点击录音按钮说出垃圾名称</span>
          </div>
          <div class="tip-item">
            <span class="tip-number">3</span>
            <span class="tip-text">图像识别：上传清晰的垃圾照片</span>
          </div>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import BottomNav from '@/components/BottomNav.vue'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goToTextRecognition = () => {
  router.push('/classification/text')
}

const goToVoiceRecognition = () => {
  router.push('/classification/voice')
}

const goToImageRecognition = () => {
  router.push('/classification/image')
}
</script>

<style lang="scss" scoped>
.classification-container {
  height: 100vh;
  background: linear-gradient(180deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// 导航栏样式
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 1100;
  
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
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: calc(20px + 88px);
}

// 标题卡片
.header-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 16px 24px;
  text-align: center;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  
  .header-image {
    width: 100%;
    max-width: 260px;
    height: auto;
    border-radius: 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .header-subtitle {
    font-size: 13px;
    color: #333;
    margin: 0;
    font-weight: 500;
  }
}

// 功能卡片
.function-cards {
  margin-bottom: 24px;
  
  .function-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateX(4px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }
    
    &:active {
      transform: translateX(2px);
    }
    
    .card-icon {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      
      .el-icon {
        font-size: 28px;
        color: white;
      }
      
      &.text-icon {
        background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
      }
      
      &.voice-icon {
        background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
      }
      
      &.image-icon {
        background: linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%);
      }
    }
    
    .card-content {
      flex: 1;
      
      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin: 0 0 4px 0;
      }
      
      .card-description {
        font-size: 13px;
        color: #666;
        margin: 0;
      }
    }
    
    .card-arrow {
      .el-icon {
        font-size: 20px;
        color: #999;
      }
    }
  }
}

// 使用提示
.tips-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  
  .tips-title {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin: 0 0 12px 0;
  }
  
  .tips-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    
    .tip-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      
      .tip-number {
        width: 20px;
        height: 20px;
        background: #4CAF50;
        color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 600;
        flex-shrink: 0;
      }
      
      .tip-text {
        font-size: 13px;
        color: #666;
        line-height: 20px;
      }
    }
  }
}

// 底部安全区域
.safe-area-bottom {
  height: 88px;
  background: transparent;
}

.with-bottom-nav {
  padding-bottom: 88px;
}

// 响应式设计
@media (max-width: 375px) {
  .content {
    padding: 16px;
  }
  
  .header-card {
    padding: 12px 20px;
    
    .header-image {
      max-width: 220px;
    }
    
    .header-subtitle {
      font-size: 12px;
    }
  }
  
  .function-card {
    padding: 16px;
    
    .card-icon {
      width: 48px;
      height: 48px;
      
      .el-icon {
        font-size: 24px;
      }
    }
  }
}

// 动画效果
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

.header-card,
.function-cards,
.tips-section {
  animation: fadeInUp 0.6s ease-out;
}

.function-cards {
  animation-delay: 0.2s;
}

.tips-section {
  animation-delay: 0.4s;
}
</style>


