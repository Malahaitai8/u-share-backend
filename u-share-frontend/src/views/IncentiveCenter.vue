<template>
  <div class="incentive-page with-bottom-nav">
    <div class="top-header">
      <div class="status-bar">
        <div class="time">{{ currentTime }}</div>
        <div class="status-icons">
          <span>📶</span><span>📶</span><span>🔋</span>
        </div>
      </div>

      <div class="nav-bar">
        <el-button class="back-button" circle size="small" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>积分商城</h2>
        <div class="placeholder" />
      </div>
    </div>

    <div class="content-wrap">
      <div class="seg-tabs">
        <button :class="['seg-tab', { active: activeTab === 'mall' }]" @click="activeTab = 'mall'">红果园商城</button>
        <button :class="['seg-tab', { active: activeTab === 'leaderboard' }]" @click="activeTab = 'leaderboard'">先锋榜</button>
        <button :class="['seg-tab', { active: activeTab === 'records' }]" @click="activeTab = 'records'">兑换记录</button>
      </div>

      <section v-if="activeTab === 'mall'" class="section-card">
        <div class="points-overview compact">
          <div class="points-main two-col">
            <div class="points-item current">
              <span class="label">当前积分</span>
              <strong>{{ overview.current_points }}</strong>
            </div>
            <div class="points-item consumed">
              <span class="label">累计消耗</span>
              <strong>{{ displayConsumedPoints }}</strong>
            </div>
          </div>
        </div>

        <div class="category-scroll">
          <button
            v-for="cat in mall.categories"
            :key="cat"
            :class="['category-chip', { active: selectedCategory === cat }]"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>

        <div v-if="mallLoading" class="skeleton-list">
          <div v-for="n in 4" :key="n" class="skeleton-card" />
        </div>

        <div v-else class="mall-grid">
          <div v-for="item in filteredItems" :key="item.id" class="mall-card">
            <div :class="['item-img-wrap', { 'is-voucher': isVoucherItem(item) }]">
              <img
                :src="resolveItemImage(item)"
                :class="['item-img', { 'item-img--contain': isVoucherItem(item) }]"
                @error="handleImageError($event, item)"
              />
            </div>
            <div class="item-title">{{ item.title }}</div>
            <div class="item-sub">{{ item.subtitle }}</div>
            <div class="item-points">{{ item.points_cost }} 积分</div>

            <div class="stock-row">
              <el-progress :percentage="stockPercent(item)" :stroke-width="8" color="#4CAF50" :show-text="false" />
              <span class="stock-text">库存 {{ item.stock_remaining }}/{{ item.stock_total }}</span>
            </div>

            <el-button
              class="exchange-btn"
              type="success"
              :disabled="overview.current_points < item.points_cost || item.stock_remaining <= 0"
              @click="submitExchange(item)"
            >
              {{ overview.current_points < item.points_cost ? '积分不足' : '立即兑换' }}
            </el-button>
          </div>
        </div>
      </section>

      <section v-if="activeTab === 'leaderboard'" class="section-card">
        <div class="board-switch">
          <button :class="['board-btn', { active: boardType === 'personal' }]" @click="switchBoard('personal')">个人榜</button>
          <button :class="['board-btn', { active: boardType === 'dormitory' }]" @click="switchBoard('dormitory')">寝室榜</button>
        </div>

        <div v-if="leaderboardLoading" class="skeleton-list">
          <div v-for="n in 6" :key="n" class="skeleton-row" />
        </div>

        <div v-else class="board-list">
          <div v-for="row in leaderboard.entries" :key="`${boardType}-${row.rank}-${row.name}`" class="board-row">
            <div class="rank">
              <span v-if="row.is_top_three">👑</span>
              <span v-else>{{ row.rank }}</span>
            </div>
            <div class="meta">
              <div class="name">{{ row.name }}</div>
              <div class="title">{{ row.title }} <span v-if="row.badge" class="badge">{{ row.badge }}</span></div>
            </div>
            <div class="score">{{ row.score }} 次</div>
          </div>
        </div>
      </section>

      <section v-if="activeTab === 'records'" class="section-card records-section">
        <div class="points-overview compact">
          <div class="points-main two-col">
            <div class="points-item current">
              <span class="label">当前积分</span>
              <strong>{{ overview.current_points }}</strong>
            </div>
            <div class="points-item consumed">
              <span class="label">累计消耗</span>
              <strong>{{ displayConsumedPoints }}</strong>
            </div>
          </div>
        </div>

        <div class="record-card only-page stretched">
          <div class="record-head">
            <h3>兑换记录</h3>
            <span>{{ exchangeRecords.length }} 条</span>
          </div>
          <div v-if="!exchangeRecords.length" class="record-empty">暂无兑换记录，快去兑换你喜欢的商品吧</div>
          <div v-else class="record-list">
            <div v-for="rec in exchangeRecords" :key="rec.id" class="record-row">
              <div class="left">
                <div class="title">{{ rec.title }}</div>
                <div class="meta">{{ rec.time }} · {{ rec.category }}</div>
                <div class="status-line">
                  <el-tag
                    size="small"
                    :type="rec.offline_status === 'completed' ? 'success' : 'warning'"
                    effect="light"
                  >
                    {{ rec.offline_status === 'completed' ? '已线下兑换' : '未线下兑换' }}
                  </el-tag>
                </div>
              </div>
              <div class="right">-{{ rec.points_cost }} 积分</div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="showSuccess" width="320px" center :show-close="false">
      <div class="success-modal">
        <div class="checkmark-wrap">
          <div class="checkmark" />
        </div>
        <h3>兑换成功</h3>
        <p>请前往学活1 楼后勤处领取</p>
      </div>
      <template #footer>
        <el-button type="success" @click="showSuccess = false">好的</el-button>
      </template>
    </el-dialog>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import BottomNav from '@/components/BottomNav.vue'
import { useUserStore } from '@/store/user'
import { convertToVolunteerHours, getLeaderboard, getMallItems, getVolunteerOverview } from '@/api/incentive'

const EXCHANGE_RECORDS_KEY = 'incentive_exchange_records'

const CULTURAL_ITEMS = [
  {
    id: 'cultural-theme-file-bag',
    category: '文创',
    title: '主题文件袋',
    subtitle: '收纳讲义资料，学习整理好帮手',
    points_cost: 150,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'zhuti-wenjiandai',
    image_url: ''
  },
  {
    id: 'cultural-campus-card-holder',
    category: '文创',
    title: '校园卡套',
    subtitle: '简洁实用，保护校园卡防磨损',
    points_cost: 200,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'xiaoyuan-katao',
    image_url: ''
  },
  {
    id: 'cultural-wood-fridge-magnet',
    category: '文创',
    title: '木质冰箱贴',
    subtitle: '环保木质工艺，校园主题纪念款',
    points_cost: 250,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'muzhi-bingxiangtie',
    image_url: ''
  },
  {
    id: 'cultural-theme-canvas-bag',
    category: '文创',
    title: '主题帆布袋',
    subtitle: '轻便耐用，日常通勤和上课都适用',
    points_cost: 300,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'zhuti-fanbudai',
    image_url: ''
  },
  {
    id: 'cultural-fine-mouse-pad',
    category: '文创',
    title: '精致鼠标垫',
    subtitle: '细腻布面材质，办公学习更舒适',
    points_cost: 350,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'jingzhi-shubiaodian',
    image_url: ''
  },
  {
    id: 'cultural-fine-notebook',
    category: '文创',
    title: '精致笔记本',
    subtitle: '高颜值封面，书写顺滑手感好',
    points_cost: 400,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'jingzhi-bijiben',
    image_url: ''
  },
  {
    id: 'cultural-slide-fridge-magnet',
    category: '文创',
    title: '滑动冰箱贴',
    subtitle: '趣味滑动设计，互动感十足',
    points_cost: 405,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'huadong-bingxiangtie',
    image_url: ''
  },
  {
    id: 'cultural-fluid-fridge-magnet',
    category: '文创',
    title: '流体冰箱贴',
    subtitle: '流体视觉效果，创意装饰感更强',
    points_cost: 500,
    stock_total: 100,
    stock_remaining: 100,
    image_name: 'liuti-bingxiangtie',
    image_url: ''
  }
]

const router = useRouter()
const userStore = useUserStore()
const currentTime = ref('')
const activeTab = ref('mall')
const selectedCategory = ref('校内餐饮')
const boardType = ref('personal')

const mallLoading = ref(true)
const leaderboardLoading = ref(true)
const showSuccess = ref(false)

const mall = ref({ categories: [], items: [] })
const exchangeRecords = ref([])
const overview = ref({
  current_points: 0,
  total_points: 0,
  consumed_points: 0,
  total_classifications: 0,
  convertible_hours: 0,
  conversion_ratio: '每100积分可申请0.5小时志愿工时'
})
const leaderboard = ref({ board_type: 'personal', entries: [] })

let timeTimer = null

const filteredItems = computed(() => mall.value.items.filter(i => i.category === selectedCategory.value))
const displayConsumedPoints = computed(() => Number(overview.value.consumed_points || 0))

const localShopImageModules = import.meta.glob('../assets/shop/**/*.{png,jpg,jpeg,webp}', {
  eager: true,
  import: 'default'
})

const localShopImageMap = Object.entries(localShopImageModules).reduce((acc, [path, url]) => {
  const fileName = path.split('/').pop() || ''
  const key = fileName.replace(/\.(png|jpe?g|webp)$/i, '')
  if (key) acc[key] = url
  return acc
}, {})

const fallbackImage = (imageName) => {
  if (!imageName) return 'https://via.placeholder.com/800x500?text=mall-image'

  const localImage = localShopImageMap[imageName]
  if (localImage) return localImage

  return `https://via.placeholder.com/800x500?text=${encodeURIComponent(imageName)}`
}

const resolveItemImage = (item) => {
  const imageName = item?.image_name
  const localImage = imageName ? localShopImageMap[imageName] : ''

  if (localImage) return localImage
  if (item?.image_url) return item.image_url

  return fallbackImage(imageName)
}

const handleImageError = (event, item) => {
  const imageName = item?.image_name
  const localImage = imageName ? localShopImageMap[imageName] : ''
  const fallback = localImage || fallbackImage(imageName)

  if (event?.target && event.target.src !== fallback) {
    event.target.src = fallback
  }
}

const formatRecordTime = (date = new Date()) => {
  const d = new Date(date)
  const Y = d.getFullYear()
  const M = String(d.getMonth() + 1).padStart(2, '0')
  const D = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${Y}-${M}-${D} ${h}:${m}`
}

const loadExchangeRecords = () => {
  try {
    const raw = localStorage.getItem(EXCHANGE_RECORDS_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    exchangeRecords.value = Array.isArray(parsed)
      ? parsed.map(record => ({
          ...record,
          offline_status: record.offline_status === 'completed' ? 'completed' : 'pending'
        }))
      : []
  } catch (_) {
    exchangeRecords.value = []
  }
}

const persistExchangeRecords = () => {
  localStorage.setItem(EXCHANGE_RECORDS_KEY, JSON.stringify(exchangeRecords.value))
}

const appendExchangeRecord = (item) => {
  const username = String(userStore.userInfo?.username || '').trim()
  const userId = userStore.userInfo?.id ?? userStore.userInfo?.user_id ?? ''

  if (!username) {
    ElMessage.error('未获取到当前用户名，无法完成兑换，请重新登录后重试')
    return false
  }

  exchangeRecords.value.unshift({
    id: `${item.id}-${Date.now()}`,
    item_id: item.id,
    user_id: userId,
    title: item.title,
    category: item.category,
    points_cost: item.points_cost,
    time: formatRecordTime(),
    username,
    offline_status: 'pending',
    verification_note: '',
    verifier_name: '',
    verified_at: ''
  })
  exchangeRecords.value = exchangeRecords.value.slice(0, 30)
  persistExchangeRecords()
  return true
}

const stockPercent = (item) => {
  if (!item?.stock_total) return 0
  return Math.max(0, Math.min(100, Math.round((item.stock_remaining / item.stock_total) * 100)))
}

const VOUCHER_POINTS_BY_FACE_VALUE = [100, 190, 280, 350, 420]

const isVoucherItem = (item) => {
  if (!item) return false
  return item.category === '校内餐饮' || /daijinquan/i.test(item.image_name || '')
}

const applyVoucherPointsRule = (items = []) => {
  const voucherItems = items
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => isVoucherItem(item))
    .map(({ item, index }) => {
      const title = item?.title || ''
      const match = title.match(/(\d+)\s*元代金券/)
      const faceValue = match ? Number(match[1]) : Number.POSITIVE_INFINITY
      return { item, index, faceValue }
    })
    .sort((a, b) => a.faceValue - b.faceValue)

  const pointMap = new Map()
  voucherItems.forEach(({ item }, idx) => {
    const fallbackPoints = VOUCHER_POINTS_BY_FACE_VALUE[VOUCHER_POINTS_BY_FACE_VALUE.length - 1]
    pointMap.set(item.id, VOUCHER_POINTS_BY_FACE_VALUE[idx] ?? fallbackPoints)
  })

  return items.map(item => {
    if (!pointMap.has(item.id)) return item
    return {
      ...item,
      points_cost: pointMap.get(item.id)
    }
  })
}

const updateTime = () => {
  const d = new Date()
  currentTime.value = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const goBack = () => router.back()

const fetchMall = async () => {
  mallLoading.value = true
  try {
    const data = await getMallItems()

    const nextItems = Array.isArray(data?.items) ? data.items : []
    const normalizedItems = applyVoucherPointsRule(nextItems).map(item => {
      if (item?.category === '其他' && /志愿时长/.test(item?.title || '')) {
        const hasLocalImage = item?.image_name && localShopImageMap[item.image_name]
        return {
          ...item,
          image_name: hasLocalImage ? item.image_name : 'zhiyuanshichang'
        }
      }
      return item
    })
    const nonCulturalItems = normalizedItems.filter(item => item.category !== '文创')

    mall.value = {
      ...data,
      items: [...nonCulturalItems, ...CULTURAL_ITEMS]
    }

    if (Array.isArray(data?.categories)) {
      mall.value.categories = data.categories.includes('文创')
        ? data.categories
        : [...data.categories, '文创']
    }

    if (mall.value.categories?.length) {
      selectedCategory.value = mall.value.categories[0]
    }
  } catch (e) {
    ElMessage.error('商城数据加载失败')
  } finally {
    mallLoading.value = false
  }
}

const fetchOverview = async () => {
  try {
    overview.value = await getVolunteerOverview()
  } catch (e) {
    ElMessage.error('积分概览加载失败')
  }
}

const fetchLeaderboard = async () => {
  leaderboardLoading.value = true
  try {
    leaderboard.value = await getLeaderboard(boardType.value)
  } catch (e) {
    ElMessage.error('先锋榜加载失败')
  } finally {
    leaderboardLoading.value = false
  }
}

const switchBoard = async (type) => {
  boardType.value = type
  await fetchLeaderboard()
}

const submitExchange = async (item) => {
  if (overview.value.current_points < item.points_cost) return

  const username = String(userStore.userInfo?.username || '').trim()
  if (!username) {
    ElMessage.error('当前账号缺少用户名信息，无法发起兑换，请联系管理员完善账号')
    return
  }

  try {
    if (item.id === 'volunteer-half-hour') {
      await convertToVolunteerHours(item.points_cost)
      await fetchOverview()
    } else {
      overview.value.current_points = Math.max(0, overview.value.current_points - item.points_cost)
      overview.value.consumed_points += item.points_cost
    }

    const recordAppended = appendExchangeRecord(item)
    if (!recordAppended) return

    showSuccess.value = true
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '兑换失败')
  }
}

onMounted(async () => {
  updateTime()
  loadExchangeRecords()
  timeTimer = setInterval(updateTime, 60000)
  await Promise.all([fetchMall(), fetchOverview(), fetchLeaderboard()])
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
})
</script>

<style scoped lang="scss">
.incentive-page {
  height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 8% 4%, rgba(255, 255, 255, 0.34) 0, rgba(255, 255, 255, 0) 36%),
    radial-gradient(circle at 92% 8%, rgba(196, 255, 230, 0.3) 0, rgba(196, 255, 230, 0) 42%),
    linear-gradient(165deg, #1f9d65 0%, #3fa77b 48%, #2f7c8b 100%);
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 1200;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
}

.status-bar,
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  padding: 14px 16px;
}

.status-bar {
  padding-bottom: 6px;
}

.nav-bar {
  padding-top: 6px;

  h2 {
    font-size: 19px;
    margin: 0;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
  }
}

.back-button {
  background: rgba(255, 255, 255, 0.24);
  border: 1px solid rgba(255, 255, 255, 0.32);
  color: #fff;
  backdrop-filter: blur(8px);
}

.placeholder { width: 32px; }

.content-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  padding: 16px 12px 92px;
}

.with-bottom-nav { padding-bottom: 92px; }

.seg-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;

  .seg-tab {
    flex: 1;
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 999px;
    padding: 10px 8px;
    background: rgba(255, 255, 255, 0.22);
    color: #fff;
    font-weight: 700;
    transition: all 0.2s ease;

    &.active {
      background: #ffffff;
      color: #1b755f;
      box-shadow: 0 8px 20px rgba(13, 83, 60, 0.22);
    }
  }
}

.section-card {
  width: 100%;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(247, 255, 251, 0.96) 100%);
  padding: 14px;
  border: 1px solid rgba(207, 237, 223, 0.9);
  box-shadow:
    0 14px 30px rgba(10, 53, 39, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.records-section {
  min-height: calc(100vh - 250px);
  display: flex;
  flex-direction: column;
}

.points-overview {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 14px;
  background: linear-gradient(130deg, #1f9d65 0%, #2ca866 45%, #2f7c8b 100%);
  color: #fff;

  .points-main {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;

    &.two-col {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      max-width: 260px;
      margin: 0 auto;
    }
  }

  .points-item {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 8px;
    text-align: center;

    .label {
      display: block;
      font-size: 11px;
      opacity: 0.9;
      margin-bottom: 4px;
    }

    strong {
      font-size: 18px;
      line-height: 1;
      font-weight: 800;
    }
  }

  .points-tip {
    margin: 8px 0 0;
    font-size: 12px;
    opacity: 0.92;
    text-align: center;
  }
}

.category-scroll {
  display: flex;
  overflow-x: auto;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 2px;

  &::-webkit-scrollbar { display: none; }

  .category-chip {
    border: none;
    padding: 8px 14px;
    border-radius: 999px;
    white-space: nowrap;
    background: #edf8f1;
    color: #1f7a53;
    font-weight: 600;
    box-shadow: inset 0 0 0 1px #d8efdf;

    &.active {
      background: linear-gradient(135deg, #2fa26c, #35b68a);
      color: #fff;
      box-shadow: 0 8px 16px rgba(53, 182, 138, 0.28);
    }
  }
}

.record-card {
  margin-bottom: 14px;
  border-radius: 14px;
  border: 1px solid #dff0e6;
  background: #fbfffd;
  padding: 10px;

  &.stretched {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .record-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;

    h3 {
      margin: 0;
      font-size: 14px;
      color: #1e4e3d;
    }

    span {
      font-size: 12px;
      color: #5f7a6f;
    }
  }

  .record-empty {
    font-size: 12px;
    color: #6c8178;
    text-align: center;
    padding: 10px 0;
  }

  .record-list {
    display: grid;
    gap: 8px;
    flex: 1;
    min-height: 260px;
    overflow-y: auto;
    align-content: start;
  }

  .record-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 10px;
    padding: 8px 10px;
    background: #f3faf6;

    .title {
      font-size: 13px;
      font-weight: 700;
      color: #1f4f3e;
    }

    .meta {
      margin-top: 2px;
      font-size: 11px;
      color: #6c857b;
    }

    .right {
      font-size: 13px;
      font-weight: 800;
      color: #1f9d65;
      margin-left: 10px;
      white-space: nowrap;
    }
  }
}

.mall-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.mall-card {
  border-radius: 18px;
  padding: 12px;
  background: linear-gradient(160deg, #ffffff 0%, #f3fff9 100%);
  border: 1px solid #d7eee2;
  box-shadow:
    0 10px 24px rgba(30, 112, 82, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.82);

  .item-img-wrap {
    position: relative;
  }

  .item-img {
    width: 100%;
    height: 132px;
    object-fit: cover;
    border-radius: 12px;
    border: 1px dashed #a8d8c0;
    background: linear-gradient(135deg, #e6f7ef 0%, #f4fffa 100%);

    &.item-img--contain {
      object-fit: contain;
      object-position: center;
      background: #fff;
      padding: 6px;
    }
  }

  .item-img-wrap.is-voucher {
    background: #fff;
    border-radius: 12px;
    border: 1px dashed #a8d8c0;
    overflow: hidden;
  }


  .item-title {
    margin-top: 8px;
    font-weight: 800;
    color: #17352b;
    font-size: 14px;
  }

  .item-sub {
    color: #5f7a6f;
    font-size: 12px;
    margin-top: 4px;
    min-height: 32px;
    line-height: 1.35;
  }

  .item-points {
    color: #1c9a61;
    font-weight: 800;
    margin-top: 7px;
    font-size: 15px;
  }

  .stock-row { margin-top: 8px; }

  .stock-text {
    font-size: 12px;
    color: #657870;
  }

  .exchange-btn {
    width: 100%;
    margin-top: 10px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg, #2ca866, #27b48f);
    box-shadow: 0 8px 18px rgba(41, 165, 107, 0.28);
  }
}

.volunteer-card { text-align: center; }

.youth-disk {
  border-radius: 50%;
  width: 236px;
  height: 236px;
  margin: 0 auto 16px;
  background: radial-gradient(circle at 35% 28%, #98e5a7, #39ae74 55%, #1b6f89 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow:
    0 14px 34px rgba(37, 142, 95, 0.34),
    inset 0 1px 10px rgba(255, 255, 255, 0.25);

  .disk-title { font-size: 13px; opacity: 0.97; }
  .disk-main { font-size: 42px; font-weight: 800; line-height: 1.15; }
  .disk-sub,
  .ratio { font-size: 12px; opacity: 0.94; }
}

.convert-btn {
  width: 100%;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2ca866, #27b48f);
}

.hint {
  color: #4e6258;
  font-size: 12px;
  margin-top: 10px;
}

.board-switch {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;

  .board-btn {
    flex: 1;
    border: 1px solid #3ca77a;
    color: #27835e;
    background: #fff;
    border-radius: 10px;
    padding: 8px;
    font-weight: 700;

    &.active {
      background: linear-gradient(135deg, #2ca866, #27b48f);
      color: #fff;
      border-color: transparent;
    }
  }
}

.board-row {
  display: flex;
  align-items: center;
  padding: 10px 4px;
  border-bottom: 1px solid #edf3ef;

  .rank { width: 40px; font-size: 20px; text-align: center; }
  .meta { flex: 1; }
  .name { font-weight: 700; color: #16382d; }
  .title { font-size: 12px; color: #5d7168; }
  .badge { margin-left: 4px; color: #1664a0; font-weight: 700; }
  .score { color: #21915e; font-weight: 800; }
}

.skeleton-list { display: grid; gap: 10px; }

.skeleton-card,
.skeleton-row,
.skeleton-disk {
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 37%, #f2f2f2 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
  border-radius: 14px;
}

.skeleton-card { height: 220px; }
.skeleton-row { height: 60px; }
.skeleton-disk { width: 230px; height: 230px; border-radius: 50%; margin: 0 auto; }

@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

.success-modal { text-align: center; padding: 6px 0; }

.checkmark-wrap {
  width: 74px;
  height: 74px;
  margin: 0 auto 10px;
  border-radius: 50%;
  background: #e8f6ea;
  display: grid;
  place-items: center;
}

.checkmark {
  width: 28px;
  height: 16px;
  border-left: 4px solid #4CAF50;
  border-bottom: 4px solid #4CAF50;
  transform: rotate(-45deg) scale(0);
  animation: check-pop .35s ease forwards;
}

@keyframes check-pop {
  to { transform: rotate(-45deg) scale(1); }
}

:deep(.bottom-nav) {
  transform: translateX(0);
}
</style>
