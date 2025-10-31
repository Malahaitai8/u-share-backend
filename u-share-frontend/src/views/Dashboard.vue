<template>
  <div class="mobile-dashboard-container">
    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="time">9:41</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">🔋</span>
      </div>
    </div>

    <!-- 顶部导航栏 -->
    <div class="nav-bar">
      <div class="nav-content">
        <div class="user-info">
          <div class="avatar">
            <el-icon class="avatar-icon"><User /></el-icon>
          </div>
          <div class="user-details">
            <h2 class="username">{{ userStore.userInfo?.username || '用户' }}</h2>
            <p class="user-status">已登录</p>
          </div>
        </div>
        <div class="nav-buttons">
          <el-button 
            class="settings-button" 
            @click="showComingSoon('个人设置')"
            circle
            size="small"
          >
            <el-icon><Setting /></el-icon>
          </el-button>
          <el-button 
            class="logout-button" 
            @click="handleLogout"
            circle
            size="small"
          >
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 欢迎卡片 -->
      <div class="welcome-section">
        <div class="welcome-card">
          <img src="/beijingfuben.png" alt="垃圾分类示意图" class="welcome-image" />
          <div class="welcome-text">
            <h3 class="welcome-title">登录成功！</h3>
            <p class="welcome-subtitle">欢迎使用U分U享智能校园垃圾分类APP</p>
          </div>
        </div>
      </div>

      <!-- 功能菜单 -->
      <div class="features-section">
        <h4 class="section-title">功能菜单</h4>
        <div class="features-grid">
          <div class="feature-item" @click="goToClassification">
            <div class="feature-icon">
              <el-icon><Camera /></el-icon>
            </div>
            <span class="feature-label">垃圾分类识别</span>
          </div>
          
          <div class="feature-item" @click="showComingSoon('积分商城')">
            <div class="feature-icon">
              <el-icon><Trophy /></el-icon>
            </div>
            <span class="feature-label">积分商城</span>
          </div>
          
          <div class="feature-item" @click="showComingSoon('数据统计')">
            <div class="feature-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <span class="feature-label">数据统计</span>
          </div>
          
          <div class="feature-item" @click="showComingSoon('环保知识')">
            <div class="feature-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <span class="feature-label">环保知识</span>
          </div>
          
          <div class="feature-item" @click="showComingSoon('社区活动')">
            <div class="feature-icon">
              <el-icon><UserFilled /></el-icon>
            </div>
            <span class="feature-label">社区活动</span>
          </div>
          
          <div class="feature-item" @click="goToGuide">
            <div class="feature-icon">
              <el-icon><Guide /></el-icon>
            </div>
            <span class="feature-label">投放引导</span>
          </div>
        </div>
      </div>

      <!-- 今日数据 -->
      <div class="stats-section">
        <h4 class="section-title">今日数据</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">分类次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">获得积分</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">环保贡献</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部安全区域 -->
    <div class="safe-area-bottom"></div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { 
  User, 
  SwitchButton, 
  Camera, 
  Trophy, 
  DataAnalysis, 
  Reading, 
  UserFilled, 
  Setting,
  Guide
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}

const goToClassification = () => {
  router.push('/classification')
}

const goToGuide = () => {
  router.push('/guide')
}

const showComingSoon = (featureName) => {
  ElMessage.info(`${featureName}功能即将上线，敬请期待！`)
}
</script>

<style lang="scss" scoped>
.mobile-dashboard-container {
  height: 100vh;
  background: linear-gradient(180deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
}

// 状态栏样式
.status-bar {
  height: 44px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  font-size: 14px;
  font-weight: 600;
  
  .time {
    font-size: 16px;
  }
  
  .status-icons {
    display: flex;
    gap: 4px;
    font-size: 12px;
  }
}

// 导航栏样式
.nav-bar {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 16px 20px;
  
  .nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 414px;
    margin: 0 auto;
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .avatar {
        width: 48px;
        height: 48px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        
        .avatar-icon {
          font-size: 24px;
          color: #4CAF50;
        }
      }
      
      .user-details {
        .username {
          font-size: 18px;
          font-weight: 600;
          color: white;
          margin: 0 0 2px 0;
        }
        
        .user-status {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.8);
          margin: 0;
        }
      }
    }
    
    .nav-buttons {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .settings-button,
    .logout-button {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
      width: 40px;
      height: 40px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
      }
    }
  }
}

// 主要内容区域
.dashboard-content {
  flex: 1;
  padding: 20px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

// 欢迎区域
.welcome-section {
  margin-bottom: 32px;
  
  .welcome-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .welcome-image {
      width: 100%;
      max-width: 280px;
      height: auto;
      border-radius: 12px;
      object-fit: cover;
      margin-bottom: 8px;
    }
    
    .welcome-text {
      width: 100%;
      
      .welcome-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin: 0 0 4px 0;
        line-height: 1.2;
      }
      
      .welcome-subtitle {
        font-size: 13px;
        color: #666;
        margin: 0;
        line-height: 1.2;
      }
    }
  }
}

// 功能菜单区域
.features-section {
  margin-bottom: 32px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: white;
    margin: 0 0 16px 0;
    padding-left: 4px;
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    
    .feature-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16px;
      padding: 20px 12px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
      }
      
      &:active {
        transform: translateY(0);
      }
      
      .feature-icon {
        margin-bottom: 8px;
        
        .el-icon {
          font-size: 24px;
          color: #4CAF50;
        }
      }
      
      .feature-label {
        font-size: 12px;
        font-weight: 500;
        color: #333;
        line-height: 1.3;
      }
    }
  }
}

// 数据统计区域
.stats-section {
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: white;
    margin: 0 0 16px 0;
    padding-left: 4px;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    
    .stat-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16px;
      padding: 20px 12px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      
      .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #4CAF50;
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 12px;
        color: #666;
        font-weight: 500;
      }
    }
  }
}

// 底部安全区域
.safe-area-bottom {
  height: 34px;
  background: rgba(0, 0, 0, 0.05);
}

// 响应式设计
@media (max-width: 375px) {
  .dashboard-content {
    padding: 16px;
  }
  
  .features-grid,
  .stats-grid {
    gap: 8px;
  }
  
  .feature-item,
  .stat-item {
    padding: 16px 8px;
  }
  
  .feature-item .feature-icon .el-icon {
    font-size: 20px;
  }
  
  .feature-item .feature-label {
    font-size: 11px;
  }
  
  .stat-item .stat-number {
    font-size: 20px;
  }
  
  .stat-item .stat-label {
    font-size: 11px;
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

.welcome-section,
.features-section,
.stats-section {
  animation: fadeInUp 0.6s ease-out;
}

.features-section {
  animation-delay: 0.2s;
}

.stats-section {
  animation-delay: 0.4s;
}

// 页面切换动画
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.mobile-dashboard-container {
  animation: slideInLeft 0.3s ease-out;
}
</style>
