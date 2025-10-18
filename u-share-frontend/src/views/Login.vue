<template>
  <div class="mobile-login-container">
    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="time">9:41</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">🔋</span>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="login-content">
      <!-- 顶部logo区域 -->
      <div class="logo-section">
        <div class="app-icon">
          <el-icon class="icon"><Recycle /></el-icon>
        </div>
        <h1 class="app-title">U分U享</h1>
        <p class="app-subtitle">智能垃圾分类，共享绿色生活</p>
      </div>

      <!-- 登录表单 -->
      <div class="form-section">
        <h2 class="form-title">欢迎登录</h2>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="mobile-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                class="mobile-input"
                clearable
              />
            </div>
          </el-form-item>
          
          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                class="mobile-input"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>
          
          <div class="form-actions">
            <el-button
              type="primary"
              class="login-button"
              :loading="userStore.loading"
              @click="handleLogin"
            >
              <span v-if="!userStore.loading">登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </div>
        </el-form>

        <!-- 忘记密码 -->
        <div class="forgot-password">
          <el-link type="primary" class="forgot-link">忘记密码？</el-link>
        </div>
      </div>

      <!-- 底部注册链接 -->
      <div class="bottom-section">
        <div class="divider">
          <span class="divider-text">或</span>
        </div>
        
        <div class="register-link">
          <span class="register-text">还没有账户？</span>
          <el-link type="primary" class="register-btn" @click="goToRegister">
            立即注册
          </el-link>
        </div>
      </div>
    </div>

    <!-- 底部安全区域 -->
    <div class="safe-area-bottom"></div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    await userStore.userLogin(loginForm)
    ElMessage.success('登录成功！')
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style lang="scss" scoped>
.mobile-login-container {
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

// 主要内容区域
.login-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 24px 24px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

// Logo区域
.logo-section {
  text-align: center;
  margin-bottom: 60px;
  
  .app-icon {
    width: 80px;
    height: 80px;
    background: white;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    
    .icon {
      font-size: 36px;
      color: #4CAF50;
    }
  }
  
  .app-title {
    font-size: 32px;
    font-weight: 700;
    color: white;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
  }
  
  .app-subtitle {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
    margin: 0;
    font-weight: 400;
  }
}

// 表单区域
.form-section {
  flex: 1;
  
  .form-title {
    font-size: 24px;
    font-weight: 600;
    color: white;
    margin: 0 0 32px 0;
    text-align: center;
  }
  
  .mobile-form {
    .el-form-item {
      margin-bottom: 20px;
      
      .input-wrapper {
        position: relative;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        width: 100%;
        height: 56px;
        display: flex;
        align-items: center;
        
        .input-icon {
          position: absolute;
          left: 16px;
          top: 50%;
          transform: translateY(-50%);
          color: #9E9E9E;
          font-size: 18px;
          z-index: 2;
        }
        
        .mobile-input {
          width: 100%;
          
          :deep(.el-input__wrapper) {
            background: transparent;
            border: none;
            box-shadow: none;
            padding-left: 48px;
            padding-right: 16px;
            height: 48px;
            border-radius: 12px;
            font-size: 16px;
            width: 100%;
            
            &:hover {
              box-shadow: none;
            }
            
            &.is-focus {
              box-shadow: none;
            }
          }
          
          :deep(.el-input__inner) {
            color: #333;
            font-size: 16px;
            
            &::placeholder {
              color: #9E9E9E;
            }
          }
        }
      }
    }
    
    .form-actions {
      margin-top: 32px;
      
      .login-button {
        width: 100%;
        height: 56px;
        background: white;
        color: #4CAF50;
        border: none;
        border-radius: 16px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        
        &:hover {
          background: #f8f8f8;
          transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }
        
        &:active {
          transform: translateY(0);
        }
      }
    }
  }
  
  .forgot-password {
    text-align: center;
    margin-top: 20px;
    
    .forgot-link {
      color: rgba(255, 255, 255, 0.9);
      font-size: 14px;
      text-decoration: none;
      
      &:hover {
        color: white;
      }
    }
  }
}

// 底部区域
.bottom-section {
  margin-top: 40px;
  
  .divider {
    position: relative;
    text-align: center;
    margin: 24px 0;
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: rgba(255, 255, 255, 0.3);
    }
    
    .divider-text {
      background: linear-gradient(180deg, #4CAF50 0%, #81C784 100%);
      color: rgba(255, 255, 255, 0.7);
      padding: 0 16px;
      font-size: 14px;
      position: relative;
      z-index: 1;
    }
  }
  
  .register-link {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    
    .register-text {
      color: rgba(255, 255, 255, 0.8);
      font-size: 14px;
    }
    
    .register-btn {
      color: white;
      font-weight: 600;
      font-size: 14px;
      text-decoration: none;
      
      &:hover {
        color: rgba(255, 255, 255, 0.9);
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
  .login-content {
    padding: 32px 20px 20px;
  }
  
  .logo-section {
    margin-bottom: 48px;
    
    .app-icon {
      width: 72px;
      height: 72px;
      
      .icon {
        font-size: 32px;
      }
    }
    
    .app-title {
      font-size: 28px;
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

.logo-section,
.form-section,
.bottom-section {
  animation: fadeInUp 0.6s ease-out;
}

.form-section {
  animation-delay: 0.2s;
}

.bottom-section {
  animation-delay: 0.4s;
}
</style>
