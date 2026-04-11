<template>
  <div class="exchange-admin-page">
    <aside class="sidebar">
      <div class="brand-block">
        <h2>数据工作台</h2>
        <p>后勤线下兑换登记与数据统计系统</p>
      </div>

      <div class="menu-list">
        <button
          class="menu-item"
          :class="{ active: activeMenu === 'stats' }"
          @click="activeMenu = 'stats'"
        >
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </button>

        <button
          class="menu-item"
          :class="{ active: activeMenu === 'register' }"
          @click="activeMenu = 'register'"
        >
          <el-icon><Tickets /></el-icon>
          <span>兑换登记</span>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <section v-if="activeMenu === 'stats'" class="placeholder-panel">
        <h3>数据统计模块</h3>
        <p>该模块待开发，可在此处接入按日/周/月的兑换与核销分析图表。</p>
      </section>

      <section v-else class="register-panel">
        <header class="panel-header">
          <div>
            <h3>兑换登记</h3>
            <p>查看用户兑换记录，完成线下领取核销闭环</p>
          </div>
          <el-tag type="info" effect="light">总记录 {{ filteredRecords.length }} 条</el-tag>
        </header>

        <el-card shadow="never" class="filter-card">
          <el-form :inline="true" class="filters">
            <el-form-item label="用户名">
              <el-input
                v-model="filters.username"
                placeholder="搜索用户名"
                clearable
                style="width: 180px"
              />
            </el-form-item>

            <el-form-item label="线上兑换日期">
              <el-date-picker
                v-model="filters.exchangeDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择兑换日期"
                clearable
                style="width: 180px"
              />
            </el-form-item>

            <el-form-item label="兑换商品">
              <el-input
                v-model="filters.product"
                placeholder="搜索兑换商品"
                clearable
                style="width: 180px"
              />
            </el-form-item>

            <el-form-item label="线下状态">
              <el-select v-model="filters.status" clearable placeholder="全部状态" style="width: 170px">
                <el-option label="未完成" value="pending" />
                <el-option label="已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="table-card">
          <el-table :data="filteredRecords" border stripe height="560">
            <el-table-column prop="username" label="用户名" min-width="120" />
            <el-table-column prop="title" label="兑换商品" min-width="180" />
            <el-table-column prop="time" label="线上兑换时间" min-width="180" />
            <el-table-column label="线下状态" min-width="130">
              <template #default="{ row }">
                <el-tag :type="row.offline_status === 'completed' ? 'success' : 'warning'" effect="light">
                  {{ row.offline_status === 'completed' ? '已线下兑换' : '未线下兑换' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="verifier_name" label="登记人员" min-width="120" />
            <el-table-column prop="verified_at" label="登记时间" min-width="170" />
            <el-table-column label="操作" width="130" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="openRegister(row)">
                  {{ row.offline_status === 'completed' ? '查看' : '登记' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>
    </main>

    <el-dialog v-model="registerDialog.visible" width="520px" :title="registerDialog.mode === 'view' ? '兑换详情' : '线下兑换登记'">
      <div v-if="registerDialog.record" class="dialog-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ registerDialog.record.username }}</el-descriptions-item>
          <el-descriptions-item label="兑换商品">{{ registerDialog.record.title }}</el-descriptions-item>
          <el-descriptions-item label="线上兑换时间">{{ registerDialog.record.time }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            {{ registerDialog.record.offline_status === 'completed' ? '已线下兑换' : '未线下兑换' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-form v-if="registerDialog.mode === 'edit'" label-width="100px" class="verify-form">
          <el-form-item label="是否完成">
            <el-switch v-model="registerDialog.form.completed" inline-prompt active-text="已完成" inactive-text="未完成" />
          </el-form-item>
          <el-form-item label="登记人员">
            <el-input v-model="registerDialog.form.verifier_name" placeholder="请输入工作人员姓名" />
          </el-form-item>
          <el-form-item label="登记说明">
            <el-input
              v-model="registerDialog.form.verification_note"
              type="textarea"
              :rows="3"
              placeholder="可填写领取备注、证件核对情况等"
            />
          </el-form-item>
        </el-form>

        <el-descriptions v-else :column="1" border class="view-desc">
          <el-descriptions-item label="登记人员">{{ registerDialog.record.verifier_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="登记时间">{{ registerDialog.record.verified_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="登记说明">{{ registerDialog.record.verification_note || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="registerDialog.visible = false">取消</el-button>
        <el-button v-if="registerDialog.mode === 'edit'" type="primary" @click="submitRegister">提交登记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Tickets } from '@element-plus/icons-vue'

const EXCHANGE_RECORDS_KEY = 'incentive_exchange_records'

const activeMenu = ref('register')
const records = ref([])

const filters = reactive({
  username: '',
  exchangeDate: '',
  product: '',
  status: ''
})

const registerDialog = reactive({
  visible: false,
  mode: 'edit',
  record: null,
  form: {
    completed: true,
    verifier_name: '',
    verification_note: ''
  }
})

const formatNow = () => {
  const d = new Date()
  const Y = d.getFullYear()
  const M = String(d.getMonth() + 1).padStart(2, '0')
  const D = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${Y}-${M}-${D} ${h}:${m}`
}

const normalizeRecords = (list = []) =>
  list
    .map(item => ({
      ...item,
      username: String(item.username || '').trim(),
      offline_status: item.offline_status === 'completed' ? 'completed' : 'pending',
      verifier_name: item.verifier_name || '',
      verification_note: item.verification_note || '',
      verified_at: item.verified_at || ''
    }))
    .filter(item => !!item.username)

const loadRecords = () => {
  try {
    const raw = localStorage.getItem(EXCHANGE_RECORDS_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    records.value = Array.isArray(parsed) ? normalizeRecords(parsed) : []
  } catch (_) {
    records.value = []
  }
}

const persistRecords = () => {
  localStorage.setItem(EXCHANGE_RECORDS_KEY, JSON.stringify(records.value))
}

const filteredRecords = computed(() => {
  return records.value.filter(item => {
    const usernameHit = !filters.username || item.username.toLowerCase().includes(filters.username.toLowerCase())
    const dateHit = !filters.exchangeDate || (item.time || '').startsWith(filters.exchangeDate)
    const productHit = !filters.product || (item.title || '').toLowerCase().includes(filters.product.toLowerCase())
    const statusHit = !filters.status || item.offline_status === filters.status
    return usernameHit && dateHit && productHit && statusHit
  })
})

const openRegister = (row) => {
  registerDialog.record = { ...row }

  if (row.offline_status === 'completed') {
    registerDialog.mode = 'view'
    registerDialog.visible = true
    return
  }

  registerDialog.mode = 'edit'
  registerDialog.form.completed = true
  registerDialog.form.verifier_name = row.verifier_name || ''
  registerDialog.form.verification_note = row.verification_note || ''
  registerDialog.visible = true
}

const submitRegister = () => {
  if (!registerDialog.record) return
  if (!registerDialog.form.verifier_name.trim()) {
    ElMessage.warning('请填写登记人员姓名')
    return
  }

  const idx = records.value.findIndex(item => item.id === registerDialog.record.id)
  if (idx < 0) {
    ElMessage.error('记录不存在，请刷新重试')
    return
  }

  records.value[idx] = {
    ...records.value[idx],
    offline_status: registerDialog.form.completed ? 'completed' : 'pending',
    verifier_name: registerDialog.form.verifier_name.trim(),
    verification_note: registerDialog.form.verification_note.trim(),
    verified_at: formatNow()
  }

  persistRecords()
  registerDialog.visible = false
  ElMessage.success('兑换登记提交成功')
}

onMounted(() => {
  document.body.classList.add('desktop-admin-mode')
  loadRecords()
})

onUnmounted(() => {
  document.body.classList.remove('desktop-admin-mode')
})
</script>

<style scoped lang="scss">
.exchange-admin-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #eef5ff 0%, #f7fffb 45%, #f3f7ff 100%);
}

.sidebar {
  width: 230px;
  background: linear-gradient(180deg, #113b66 0%, #1b5a8f 100%);
  color: #fff;
  padding: 24px 16px;
  box-shadow: 4px 0 16px rgba(12, 39, 80, 0.18);

  .brand-block {
    margin-bottom: 26px;

    h2 {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 1px;
    }

    p {
      margin: 10px 0 0;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.8);
      line-height: 1.4;
    }
  }

  .menu-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .menu-item {
    width: 100%;
    border: none;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.12);
    color: #fff;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.2s ease;

    &.active,
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: translateX(3px);
    }
  }
}

.main-content {
  flex: 1;
  min-width: 0;
  width: calc(100vw - 230px);
  padding: 24px 6px 24px 24px;
}

.placeholder-panel,
.register-panel {
  width: 100%;
  min-height: calc(100vh - 48px);
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(165, 196, 235, 0.45);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 10px 26px rgba(44, 101, 157, 0.08);
}

.placeholder-panel {
  h3 {
    margin: 0 0 10px;
    color: #1c416e;
  }

  p {
    margin: 0;
    color: #4f6580;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;

  h3 {
    margin: 0;
    font-size: 22px;
    color: #153f69;
  }

  p {
    margin: 8px 0 0;
    color: #5d7590;
    font-size: 14px;
  }
}

.filter-card,
.table-card {
  border-radius: 14px;
  border-color: #d5e5f7;
}

.filter-card {
  margin-bottom: 14px;
}

.filters {
  row-gap: 6px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.verify-form,
.view-desc {
  margin-top: 12px;
}

:deep(.el-table th.el-table__cell) {
  background: #f2f8ff;
  color: #204467;
}

@media (max-width: 1100px) {
  .exchange-admin-page {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;

    .menu-list {
      flex-direction: row;
    }

    .menu-item {
      justify-content: center;
    }
  }

  .main-content {
    width: 100%;
    padding: 16px;
  }
}
</style>
