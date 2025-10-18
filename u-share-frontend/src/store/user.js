import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  // 登录
  const userLogin = async (credentials) => {
    loading.value = true
    try {
      const response = await login(credentials)
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      
      // 获取用户信息
      await getUserProfile()
      
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 注册
  const userRegister = async (userData) => {
    loading.value = true
    try {
      const response = await register(userData)
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  const getUserProfile = async () => {
    if (!token.value) return
    
    try {
      const response = await getUserInfo()
      userInfo.value = response
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，清除token
      logout()
      throw error
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  // 初始化用户状态
  const initUser = async () => {
    if (token.value) {
      try {
        await getUserProfile()
      } catch (error) {
        console.error('初始化用户状态失败:', error)
      }
    }
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    userLogin,
    userRegister,
    getUserProfile,
    logout,
    initUser
  }
})

