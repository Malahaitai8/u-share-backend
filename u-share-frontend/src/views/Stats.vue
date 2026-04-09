<template>
  <div class="mobile-stats-container with-bottom-nav">
    <div class="status-bar">
      <div class="time">{{ currentTime }}</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">🔋</span>
      </div>
    </div>

    <div class="nav-bar">
      <div class="nav-content">
        <el-button class="back-button" @click="goBack" circle size="small">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2 class="nav-title">数据统计</h2>
        <div class="nav-placeholder"></div>
      </div>
    </div>

    <div class="stats-content">
      <div class="stats-card main-card">
        <div class="card-icon">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="card-value">{{ stats.current_points || 0 }}</div>
        <div class="card-label">我的积分</div>
      </div>

      <div class="stats-row">
        <div class="stats-card small-card">
          <div class="card-value small">{{ stats.week_classifications || 0 }}</div>
          <div class="card-label">本周分类次数</div>
        </div>
        <div class="stats-card small-card">
          <div class="card-value small">{{ stats.week_points || 0 }}</div>
          <div class="card-label">本周获得积分</div>
        </div>
      </div>

      <div class="stats-card rank-card">
        <div class="rank-icon">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="rank-content">
          <div class="rank-percent">{{ stats.rank_percentile || 0 }}%</div>
          <div class="rank-desc">超过全校用户</div>
        </div>
      </div>

      <div class="stats-card summary-card">
        <div class="summary-title">累计数据</div>
        <div class="summary-item">
          <span class="summary-label">累计分类次数</span>
          <span class="summary-value">{{ stats.total_classifications || 0 }} 次</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">累计获得积分</span>
          <span class="summary-value">{{ stats.total_points || 0 }} 分</span>
        </div>
      </div>
    </div>

    <div class="safe-area-bottom"></div>
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Coin, Trophy, ArrowLeft } from '@element-plus/icons-vue'
import BottomNav from '@/components/BottomNav.vue'
import request from '@/api/request'

const router = useRouter()

const currentTime = ref('')
const stats = ref({
  current_points: 0,
  total_points: 0,
  total_classifications: 0,
  week_classifications: 0,
  week_points: 0,
  rank_percentile: 0
})

let timeInterval = null

const updateTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

const goBack = () => {
  router.back()
}

const fetchStats = async () => {
  try {
    const data = await request({
      url: '/stats/my',
      method: 'get'
    })
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  fetchStats()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style lang="scss" scoped>
.mobile-stats-container {
  height: 100vh;
  background: linear-gradient(180deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
}

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
}

.stats-content {
  flex: 1;
  padding: 20px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.main-card {
  margin-bottom: 16px;
  padding: 32px 20px;
  
  .card-icon {
    font-size: 32px;
    color: #FFC107;
    margin-bottom: 8px;
  }
  
  .card-value {
    font-size: 48px;
    font-weight: 700;
    color: #4CAF50;
    line-height: 1.2;
    
    &.small {
      font-size: 32px;
    }
  }
  
  .card-label {
    font-size: 14px;
    color: #666;
    margin-top: 4px;
  }
}

.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  
  .small-card {
    flex: 1;
    padding: 20px 12px;
    
    .card-value {
      font-size: 28px;
      font-weight: 700;
      color: #4CAF50;
    }
    
    .card-label {
      font-size: 12px;
      color: #666;
      margin-top: 4px;
    }
  }
}

.rank-card {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  text-align: left;
  
  .rank-icon {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
  }
  
  .rank-content {
    flex: 1;
    
    .rank-percent {
      font-size: 32px;
      font-weight: 700;
      color: #FF9800;
      line-height: 1.2;
    }
    
    .rank-desc {
      font-size: 14px;
      color: #666;
    }
  }
}

.summary-card {
  text-align: left;
  
  .summary-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
  }
  
  .summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    
    .summary-label {
      font-size: 14px;
      color: #666;
    }
    
    .summary-value {
      font-size: 16px;
      font-weight: 600;
      color: #4CAF50;
    }
  }
}

.safe-area-bottom {
  height: 88px;
  background: transparent;
}

.with-bottom-nav {
  padding-bottom: 88px;
}

@media (max-width: 375px) {
  .stats-content {
    padding: 16px;
  }
  
  .main-card {
    padding: 24px 16px;
    
    .card-value {
      font-size: 40px;
    }
  }
  
  .rank-card .rank-percent {
    font-size: 28px;
  }
}
</style>
