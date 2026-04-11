<template>
  <nav class="bottom-nav" role="navigation" aria-label="底部导航">
    <button
      v-for="item in navItems"
      :key="item.key"
      class="nav-item"
      :class="{ active: isActive(item) }"
      @click="go(item.path)"
    >
      <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
      <span class="nav-label">{{ item.label }}</span>
    </button>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  Camera,
  Reading,
  Trophy,
  UserFilled,
  DataAnalysis,
  Guide
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const navItems = [
  { key: 'home', label: '主页', path: '/dashboard' },
  { key: 'classification', label: '识别', path: '/classification', icon: Camera },
  { key: 'knowledge', label: '知识', path: '/dashboard?tab=knowledge', icon: Reading },
  { key: 'mall', label: '商城', path: '/incentive', icon: Trophy },
  { key: 'community', label: '活动', path: '/dashboard?tab=community', icon: UserFilled },
  { key: 'stats', label: '统计', path: '/stats', icon: DataAnalysis },
  { key: 'guide', label: '投放', path: '/guide', icon: Guide }
]

// 补齐主页图标（保持上方数组结构紧凑）
navItems[0].icon = House

const go = (path) => {
  if (route.fullPath !== path) {
    router.push(path)
  }
}

const isActive = (item) => {
  if (item.key === 'home') {
    return route.path === '/dashboard' && !route.query.tab
  }
  if (item.key === 'classification') {
    return route.path.startsWith('/classification')
  }
  if (item.key === 'mall') {
    return route.path === '/incentive'
  }
  if (item.key === 'stats') {
    return route.path === '/stats'
  }
  if (item.key === 'guide') {
    return route.path === '/guide'
  }
  if (item.key === 'knowledge') {
    return route.path === '/dashboard' && route.query.tab === 'knowledge'
  }
  if (item.key === 'community') {
    return route.path === '/dashboard' && route.query.tab === 'community'
  }
  return false
}
</script>

<style scoped lang="scss">
.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0 auto;
  z-index: 1200;
  width: min(100vw, 414px);
  height: 72px;
  background: #ffffff;
  border-top: 1px solid #e9ecef;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  box-sizing: border-box;
}

.nav-item {
  border: none;
  background: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #8a8f98;
  padding: 4px 2px;

  .nav-icon {
    font-size: 18px;
  }

  .nav-label {
    font-size: 10px;
    line-height: 1.2;
    text-align: center;
  }

  &.active {
    color: #4caf50;
    font-weight: 600;
  }
}
</style>
