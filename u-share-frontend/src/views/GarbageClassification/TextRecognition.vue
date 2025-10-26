<template>
  <div class="text-recognition-container">
    <!-- AI对话框 -->
    <AIChatDialog v-model="showAIChat" />
    
    <!-- 顶部导航栏 -->
    <div class="nav-bar">
      <el-button
          class="back-button"
          @click="goBack"
          circle
          size="small"
      >
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h1 class="nav-title">文字识别</h1>
      <el-button
          class="ai-chat-button"
          @click="openAIChat"
          circle
          size="small"
      >
        <el-icon><ChatDotRound /></el-icon>
      </el-button>
    </div>

    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 输入卡片 -->
      <div class="input-card">
        <div class="card-header">
          <div class="icon-wrapper">
            <el-icon class="input-icon"><EditPen /></el-icon>
          </div>
          <h3 class="card-title">请输入垃圾名称</h3>
        </div>

        <div class="input-wrapper">
          <el-input
              v-model="inputText"
              type="textarea"
              :rows="4"
              placeholder="例如：塑料瓶、废纸、电池、果皮..."
              maxlength="100"
              show-word-limit
              class="text-input"
          />
        </div>

        <el-button
            type="primary"
            size="large"
            class="recognize-button"
            @click="handleRecognize"
            :loading="loading"
            :disabled="!inputText.trim()"
        >
          <el-icon v-if="!loading"><Search /></el-icon>
          <span>{{ loading ? '识别中...' : '开始识别' }}</span>
        </el-button>
      </div>

      <!-- 结果卡片 -->
      <transition name="fade-slide">
        <div v-if="result" class="result-card">
          <div class="result-header">
            <div class="result-icon" :class="resultIconClass">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <h3 class="result-title">识别结果</h3>
          </div>

          <div class="result-content">
            <div class="result-item">
              <span class="result-label">垃圾名称：</span>
              <span class="result-value">{{ result.name }}</span>
            </div>

            <div class="result-item highlight">
              <span class="result-label">分类类型：</span>
              <span class="result-value type-badge" :class="result.typeClass">
                {{ result.type }}
              </span>
            </div>

            <div class="result-item">
              <span class="result-label">投放说明：</span>
              <span class="result-value">{{ result.description }}</span>
            </div>

            <div v-if="result.tips" class="tips-box">
              <div class="tips-header">
                <el-icon><InfoFilled /></el-icon>
                <span>温馨提示</span>
              </div>
              <p class="tips-content">{{ result.tips }}</p>
            </div>
          </div>
        </div>
      </transition>

      <!-- 历史记录 -->
      <div v-if="history.length > 0" class="history-section">
        <div class="history-header">
          <h4 class="history-title">识别历史</h4>
          <el-button text size="small" @click="clearHistory">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>

        <div class="history-list">
          <div
              v-for="(item, index) in history"
              :key="index"
              class="history-item"
              @click="selectHistory(item)"
          >
            <div class="history-name">{{ item }}</div>
            <el-icon class="history-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 快捷示例 -->
      <div class="examples-section">
        <h4 class="examples-title">快捷示例</h4>
        <div class="examples-grid">
          <div
              v-for="example in examples"
              :key="example"
              class="example-tag"
              @click="selectExample(example)"
          >
            {{ example }}
          </div>
        </div>
      </div>
    </div>

    <!-- 底部安全区域 -->
    <div class="safe-area-bottom"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { classifyByText } from '@/api/classification'
import AIChatDialog from '@/components/AIChatDialog.vue'

const router = useRouter()

const inputText = ref('')
const loading = ref(false)
const result = ref(null)
const history = ref([])
const showAIChat = ref(false)

const examples = [
  '塑料瓶', '废纸', '电池', '果皮', '玻璃瓶',
  '易拉罐', '过期药品', '旧衣服', '剩菜剩饭'
]

const goBack = () => {
  router.back()
}

const openAIChat = () => {
  showAIChat.value = true
}

const handleRecognize = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入垃圾名称')
    return
  }

  loading.value = true

  try {
    // 调用真实的NLP服务API
    const response = await classifyByText(inputText.value.trim())

    // 处理识别结果
    result.value = response.data

    // 添加到历史记录
    const trimmedText = inputText.value.trim()
    if (!history.value.includes(trimmedText)) {
      history.value.unshift(trimmedText)
      if (history.value.length > 5) {
        history.value.pop()
      }
    }

    ElMessage.success('识别成功')
  } catch (error) {
    console.error('Recognition error:', error)
    ElMessage.error(error.message || '识别失败，请重试')
  } finally {
    loading.value = false
  }
}


const selectExample = (example) => {
  inputText.value = example
}

const selectHistory = (item) => {
  inputText.value = item
  handleRecognize()
}

const clearHistory = () => {
  history.value = []
  ElMessage.success('历史记录已清空')
}

const resultIconClass = computed(() => {
  if (!result.value) return ''
  return result.value.typeClass
})
</script>

<style lang="scss" scoped>
.text-recognition-container {
  height: 100vh;
  background: linear-gradient(180deg, #2196F3 0%, #64B5F6 100%);
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  overflow-y: auto;
}

// 导航栏样式
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);

  .back-button,
  .ai-chat-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 40px;
    height: 40px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }

  .ai-chat-button {
    .el-icon {
      font-size: 18px;
    }
  }

  .nav-title {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin: 0;
  }
}

// 主要内容
.content {
  flex: 1;
  padding: 20px;
  max-width: 414px;
  margin: 0 auto;
  width: 100%;
}

// 输入卡片
.input-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);

  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;

    .icon-wrapper {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;

      .input-icon {
        font-size: 24px;
        color: white;
      }
    }

    .card-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .input-wrapper {
    margin-bottom: 20px;

    :deep(.text-input) {
      .el-textarea__inner {
        font-size: 15px;
        line-height: 1.6;
        border-radius: 12px;
        border: 2px solid #e0e0e0;

        &:focus {
          border-color: #2196F3;
        }
      }
    }
  }

  .recognize-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
    }
  }
}

// 结果卡片
.result-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);

  .result-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;

    .result-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;

      .el-icon {
        font-size: 24px;
        color: white;
      }

      &.recyclable {
        background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
      }

      &.harmful {
        background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
      }

      &.kitchen {
        background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
      }

      &.other {
        background: linear-gradient(135deg, #757575 0%, #9E9E9E 100%);
      }
    }

    .result-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .result-content {
    .result-item {
      display: flex;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      &.highlight {
        background: linear-gradient(90deg, rgba(33, 150, 243, 0.05) 0%, rgba(33, 150, 243, 0) 100%);
        margin: 0 -12px;
        padding: 12px;
        border-radius: 8px;
      }

      .result-label {
        font-size: 14px;
        color: #666;
        width: 80px;
        flex-shrink: 0;
      }

      .result-value {
        font-size: 15px;
        color: #333;
        font-weight: 500;
        flex: 1;

        &.type-badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 600;
          color: white;

          &.recyclable {
            background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
          }

          &.harmful {
            background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
          }

          &.kitchen {
            background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
          }

          &.other {
            background: linear-gradient(135deg, #757575 0%, #9E9E9E 100%);
          }
        }
      }
    }

    .tips-box {
      margin-top: 16px;
      padding: 16px;
      background: #FFF8E1;
      border-radius: 12px;
      border-left: 4px solid #FFC107;

      .tips-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #F57C00;

        .el-icon {
          font-size: 16px;
        }
      }

      .tips-content {
        font-size: 13px;
        color: #666;
        line-height: 1.6;
        margin: 0;
      }
    }
  }
}

// 历史记录
.history-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .history-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .history-list {
    .history-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #f5f5f5;
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #e0e0e0;
      }

      &:last-child {
        margin-bottom: 0;
      }

      .history-name {
        font-size: 14px;
        color: #333;
      }

      .history-arrow {
        font-size: 16px;
        color: #999;
      }
    }
  }
}

// 快捷示例
.examples-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .examples-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 0 0 12px 0;
  }

  .examples-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .example-tag {
      padding: 8px 16px;
      background: #E3F2FD;
      color: #2196F3;
      border-radius: 20px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #2196F3;
        color: white;
        transform: translateY(-2px);
      }
    }
  }
}

// 底部安全区域
.safe-area-bottom {
  height: 34px;
  background: rgba(0, 0, 0, 0.05);
}

// 过渡动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

// 响应式设计
@media (max-width: 375px) {
  .content {
    padding: 16px;
  }

  .input-card,
  .result-card {
    padding: 20px;
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

.input-card,
.examples-section {
  animation: fadeInUp 0.6s ease-out;
}

.examples-section {
  animation-delay: 0.2s;
}
</style>

