<template>
  <div class="admin-stats">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <label>开始日期：</label>
        <el-date-picker
          v-model="startDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择开始日期"
          :clearable="false"
        />
      </div>
      <div class="filter-item">
        <label>结束日期：</label>
        <el-date-picker
          v-model="endDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择结束日期"
          :clearable="false"
        />
      </div>
      <el-button type="primary" @click="fetchAllData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-button @click="exportData">
        <el-icon><Download /></el-icon>
        导出CSV
      </el-button>
    </div>

    <!-- 四宫格数字卡片 -->
    <div class="overview-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.total_classifications }}</div>
          <div class="stat-label">总分类次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon yellow">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.total_points }}</div>
          <div class="stat-label">总获得积分</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.week_active_users }}</div>
          <div class="stat-label">本周活跃用户</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Location /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ locationStats.length }}</div>
          <div class="stat-label">投放点数量</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 趋势图 -->
      <div class="chart-card">
        <h3>分类趋势</h3>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>
      <!-- 垃圾类型柱状图 -->
      <div class="chart-card">
        <h3>垃圾类型分布</h3>
        <div ref="typeChartRef" class="chart-container"></div>
      </div>
      <!-- 识别方式饼图 -->
      <div class="chart-card">
        <h3>识别方式占比</h3>
        <div ref="methodChartRef" class="chart-container"></div>
      </div>
      <!-- 垃圾类型占比饼图 -->
      <div class="chart-card">
        <h3>垃圾类型占比</h3>
        <div ref="typePieChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- 投放点排行榜 -->
    <div class="location-section">
      <h3>投放点使用排行榜</h3>
      <el-table :data="locationStats" border stripe max-height="400">
        <el-table-column type="index" label="排名" width="70" />
        <el-table-column prop="dustbin_name" label="站点名称" min-width="150" />
        <el-table-column prop="count" label="分类次数" width="100" sortable />
        <el-table-column prop="percentage" label="占比" width="100">
          <template #default="{ row }">
            {{ row.percentage }}%
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="showOnMap(row)">
              查看位置
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 用户排行榜 -->
    <div class="leaderboard-section">
      <h3>用户分类排行榜</h3>
      <el-table :data="leaderboard" border stripe>
        <el-table-column type="index" label="排名" width="70" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="total_classifications" label="分类次数" width="120" sortable />
        <el-table-column prop="total_points" label="获得积分" width="120" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Coin, User, Location, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import 'echarts/theme/macarons'
import request from '@/api/request'

const loading = ref(false)
const startDate = ref('')
const endDate = ref('')

const overview = reactive({
  total_classifications: 0,
  total_points: 0,
  total_users: 0,
  station_count: 0,
  week_classifications: 0,
  week_points: 0,
  week_active_users: 0
})

const trendData = ref([])
const typeStats = ref([])
const methodStats = ref([])
const locationStats = ref([])
const leaderboard = ref([])

const trendChartRef = ref(null)
const typeChartRef = ref(null)
const methodChartRef = ref(null)
const typePieChartRef = ref(null)

let trendChart = null
let typeChart = null
let methodChart = null
let typePieChart = null

const getDefaultDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  startDate.value = start.toISOString().split('T')[0]
  endDate.value = end.toISOString().split('T')[0]
}

// 垃圾类型名称映射
const getGarbageTypeName = (type) => {
  const typeMap = {
    'recyclable': '可回收',
    'kitchen': '厨余',
    'hazardous': '有害',
    'other': '其他',
    '??': '可回收',
    '???': '厨余',
    '????': '有害',
    '?????': '其他'
  }
  return typeMap[type] || type || '其他'
}

// 识别方式名称映射
const getMethodName = (method) => {
  const methodMap = {
    'text': '文字识别',
    'voice': '语音识别',
    'image': '图像识别'
  }
  return methodMap[method] || method || '其他'
}

const fetchOverview = async () => {
  try {
    const data = await request({ url: '/admin/stats/overview', method: 'get' })
    Object.assign(overview, data)
  } catch (error) {
    console.error('Failed to fetch overview:', error)
  }
}

const fetchTrend = async () => {
  try {
    const data = await request({
      url: '/admin/stats/trend',
      method: 'get',
      params: { start_date: startDate.value, end_date: endDate.value, period: 'day' }
    })
    trendData.value = data.trend || []
    renderTrendChart()
  } catch (error) {
    console.error('Failed to fetch trend:', error)
  }
}

const fetchTypeStats = async () => {
  try {
    const data = await request({
      url: '/admin/stats/by-type',
      method: 'get',
      params: { start_date: startDate.value, end_date: endDate.value }
    })
    typeStats.value = data.stats || []
    renderTypeChart()
    renderTypePieChart()
  } catch (error) {
    console.error('Failed to fetch type stats:', error)
  }
}

const fetchMethodStats = async () => {
  try {
    const data = await request({
      url: '/admin/stats/by-method',
      method: 'get',
      params: { start_date: startDate.value, end_date: endDate.value }
    })
    methodStats.value = data.stats || []
    renderMethodChart()
  } catch (error) {
    console.error('Failed to fetch method stats:', error)
  }
}

const fetchLocationStats = async () => {
  try {
    const data = await request({
      url: '/admin/stats/by-location',
      method: 'get',
      params: { start_date: startDate.value, end_date: endDate.value }
    })
    locationStats.value = data.stats || []
  } catch (error) {
    console.error('Failed to fetch location stats:', error)
  }
}

const fetchLeaderboard = async () => {
  try {
    const data = await request({
      url: '/admin/stats/leaderboard',
      method: 'get',
      params: { limit: 10 }
    })
    leaderboard.value = data.users || []
  } catch (error) {
    console.error('Failed to fetch leaderboard:', error)
  }
}

const fetchAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchOverview(),
      fetchTrend(),
      fetchTypeStats(),
      fetchMethodStats(),
      fetchLocationStats(),
      fetchLeaderboard()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const exportData = async () => {
  try {
    const response = await request({
      url: '/admin/stats/export',
      method: 'get',
      params: { start_date: startDate.value, end_date: endDate.value },
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `stats_${startDate.value}_${endDate.value}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const showOnMap = (row) => {
  ElMessage.info(`站点: ${row.dustbin_name}, 位置: ${row.dustbin_lng}, ${row.dustbin_lat}`)
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  
  trendChart = echarts.init(trendChartRef.value)
  const dates = trendData.value.map(item => item.date)
  const counts = trendData.value.map(item => item.count)
  const points = trendData.value.map(item => item.points)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['分类次数', '获得积分'] },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: [
      { type: 'value', name: '次数' },
      { type: 'value', name: '积分' }
    ],
    series: [
      { name: '分类次数', type: 'line', data: counts, smooth: true, itemStyle: { color: '#4CAF50' } },
      { name: '获得积分', type: 'line', yAxisIndex: 1, data: points, smooth: true, itemStyle: { color: '#FFC107' } }
    ]
  })
}

const renderTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()
  
  typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: typeStats.value.map(item => getGarbageTypeName(item.type)) },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: typeStats.value.map(item => item.count),
      itemStyle: { color: '#4CAF50' }
    }]
  })
}

const renderMethodChart = () => {
  if (!methodChartRef.value) return
  if (methodChart) methodChart.dispose()
  
  methodChart = echarts.init(methodChartRef.value)
  methodChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: methodStats.value.map(item => ({
        name: item.method === 'text' ? '文字识别' : item.method === 'voice' ? '语音识别' : '图像识别',
        value: item.count
      }))
    }]
  })
}

const renderTypePieChart = () => {
  if (!typePieChartRef.value) return
  if (typePieChart) typePieChart.dispose()
  
  typePieChart = echarts.init(typePieChartRef.value)
  const colors = { '可回收': '#4CAF50', '厨余': '#8BC34A', '有害': '#F44336', '其他': '#9E9E9E' }
  typePieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: typeStats.value.map(item => ({
        name: getGarbageTypeName(item.type),
        value: item.count,
        itemStyle: { color: colors[getGarbageTypeName(item.type)] || '#4CAF50' }
      }))
    }]
  })
}

const handleResize = () => {
  trendChart?.resize()
  typeChart?.resize()
  methodChart?.resize()
  typePieChart?.resize()
}

onMounted(() => {
  getDefaultDateRange()
  fetchAllData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  typeChart?.dispose()
  methodChart?.dispose()
  typePieChart?.dispose()
})
</script>

<style scoped lang="scss">
.admin-stats {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 48px);
}

.filter-bar {
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;

  .filter-item {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 14px;
      color: #606266;
    }
  }
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;

  .stat-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      color: white;

      &.blue { background: linear-gradient(135deg, #667eea, #764ba2); }
      &.yellow { background: linear-gradient(135deg, #f093fb, #f5576c); }
      &.green { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
      &.purple { background: linear-gradient(135deg, #9C27B0, #673AB7); }
    }

    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #303133;
      }
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;

  .chart-card {
    background: white;
    border-radius: 8px;
    padding: 16px;

    h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
    }

    .chart-container {
      height: 280px;
    }
  }
}

.location-section,
.leaderboard-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;

  h3 {
    margin: 0 0 12px 0;
    font-size: 16px;
    color: #303133;
  }
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
