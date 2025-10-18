<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

onMounted(() => {
  // 初始化用户状态
  userStore.initUser()
})
</script>

<style lang="scss">
// 移动端APP样式已在全局样式中定义
</style>
