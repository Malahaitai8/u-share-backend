<template>
  <div class="mobile-register-container">
    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="time">9:41</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">🔋</span>
      </div>
    </div>

    <!-- 顶部导航 -->
    <div class="nav-bar">
      <el-button 
        class="back-button" 
        @click="goToLogin"
        circle
        size="small"
      >
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h1 class="nav-title">创建账户</h1>
      <div class="nav-placeholder"></div>
    </div>

    <!-- 主要内容区域 -->
    <div class="register-content">
      <!-- 顶部logo区域 -->
      <div class="logo-section">
        <div class="app-icon">
          <el-icon class="icon"><UserFilled /></el-icon>
        </div>
        <h2 class="section-title">加入垃圾分类</h2>
        <p class="section-subtitle">让我们一起为环保贡献力量</p>
      </div>

      <!-- 注册表单 -->
      <div class="form-section">
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="mobile-form"
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="registerForm.username"
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
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                class="mobile-input"
                show-password
              />
            </div>
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                class="mobile-input"
                show-password
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>
          
          <div class="form-actions">
            <el-button
              type="primary"
              class="register-button"
              :loading="userStore.loading"
              @click="handleRegister"
            >
              <span v-if="!userStore.loading">创建账户</span>
              <span v-else>创建中...</span>
            </el-button>
          </div>
        </el-form>

        <!-- 用户协议 -->
        <div class="terms-section">
          <p class="terms-text">
            注册即表示您同意我们的
            <el-link type="primary" class="terms-link">服务条款</el-link>
            和
            <el-link type="primary" class="terms-link">隐私政策</el-link>
          </p>
        </div>
      </div>

      <!-- 底部登录链接 -->
      <div class="bottom-section">
        <div class="divider">
          <span class="divider-text">或</span>
        </div>
        
        <div class="login-link">
          <span class="login-text">已有账户？</span>
          <el-link type="primary" class="login-btn" @click="goToLogin">
            立即登录
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

const registerFormRef = ref()

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    
    const { confirmPassword, ...userData } = registerForm
    await userStore.userRegister(userData)
    
    ElMessage.success('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('注册失败，请重试')
    }
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.mobile-register-container {
  height: 100vh;
  background: linear-gradient(180deg, #2196F3 0%, #64B5F6 100%);
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
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  
  .back-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 36px;
    height: 36px;
    
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
    width: 36px;
  }
}

// 主要内容区域
.register-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 24px 24px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

// Logo区域
.logo-section {
  text-align: center;
  margin-bottom: 40px;
  
  .app-icon {
    width: 72px;
    height: 72px;
    background: white;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    
    .icon {
      font-size: 32px;
      color: #2196F3;
    }
  }
  
  .section-title {
    font-size: 28px;
    font-weight: 700;
    color: white;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
  }
  
  .section-subtitle {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
    margin: 0;
    font-weight: 400;
  }
}

// 表单区域
.form-section {
  flex: 1;
  
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
      
      .register-button {
        width: 100%;
        height: 56px;
        background: white;
        color: #2196F3;
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
  
  .terms-section {
    margin-top: 20px;
    text-align: center;
    
    .terms-text {
      color: rgba(255, 255, 255, 0.8);
      font-size: 12px;
      line-height: 1.5;
      margin: 0;
      
      .terms-link {
        color: white;
        font-weight: 500;
        text-decoration: none;
        
        &:hover {
          color: rgba(255, 255, 255, 0.9);
        }
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
      background: linear-gradient(180deg, #2196F3 0%, #64B5F6 100%);
      color: rgba(255, 255, 255, 0.7);
      padding: 0 16px;
      font-size: 14px;
      position: relative;
      z-index: 1;
    }
  }
  
  .login-link {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    
    .login-text {
      color: rgba(255, 255, 255, 0.8);
      font-size: 14px;
    }
    
    .login-btn {
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
  .register-content {
    padding: 20px 20px 20px;
  }
  
  .logo-section {
    margin-bottom: 32px;
    
    .app-icon {
      width: 64px;
      height: 64px;
      
      .icon {
        font-size: 28px;
      }
    }
    
    .section-title {
      font-size: 24px;
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

// 页面切换动画
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.mobile-register-container {
  animation: slideInRight 0.3s ease-out;
}
</style>
