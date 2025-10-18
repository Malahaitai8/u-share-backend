import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { 
      title: '注册',
      requiresAuth: false 
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { 
      title: '垃圾分类管理',
      requiresAuth: true 
    }
  },
  {
    path: '/classification',
    name: 'GarbageClassification',
    component: () => import('@/views/GarbageClassification/Index.vue'),
    meta: { 
      title: '垃圾分类识别',
      requiresAuth: true 
    }
  },
  {
    path: '/classification/text',
    name: 'TextRecognition',
    component: () => import('@/views/GarbageClassification/TextRecognition.vue'),
    meta: { 
      title: '文字识别',
      requiresAuth: true 
    }
  },
  {
    path: '/classification/voice',
    name: 'VoiceRecognition',
    component: () => import('@/views/GarbageClassification/VoiceRecognition.vue'),
    meta: { 
      title: '语音识别',
      requiresAuth: true 
    }
  },
  {
    path: '/classification/image',
    name: 'ImageRecognition',
    component: () => import('@/views/GarbageClassification/ImageRecognition.vue'),
    meta: { 
      title: '图像识别',
      requiresAuth: true 
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 垃圾分类管理系统`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router

