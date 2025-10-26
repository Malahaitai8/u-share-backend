<template>
  <div v-if="modelValue" class="ai-chat-overlay" @click="handleOverlayClick">
    <div class="ai-chat-dialog" @click.stop>
      <!-- 头部 -->
      <div class="dialog-header">
        <div class="header-title">
          <el-icon class="ai-icon"><ChatDotRound /></el-icon>
          <span>AI 智能助手</span>
        </div>
        <el-icon class="close-icon" @click="handleClose"><Close /></el-icon>
      </div>

      <!-- 消息区域 -->
      <div class="message-container" ref="messageContainer">
        <!-- 欢迎语 -->
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-text">👋 您好！我是垃圾分类智能助手</div>
          <div class="welcome-subtitle">有什么可以帮您的吗？</div>
          
          <!-- 快捷问题 -->
          <div class="quick-questions">
            <div 
              v-for="(question, index) in quickQuestions" 
              :key="index"
              class="quick-question-item"
              @click="sendQuickQuestion(question)"
            >
              {{ question }}
            </div>
          </div>
        </div>

        <!-- 对话消息 -->
        <div v-for="(msg, index) in messages" :key="index" class="message-item" :class="msg.type">
          <div class="message-bubble">
            <div class="message-content">{{ msg.content }}</div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <!-- AI 正在输入 -->
        <div v-if="isTyping" class="message-item ai">
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          :maxlength="500"
          show-word-limit
          placeholder="请输入您的问题..."
          :disabled="isTyping || isStreaming"
          @keydown.enter.exact.prevent="handleSend"
        />
        <el-button 
          type="primary" 
          :disabled="!inputText.trim() || isTyping || isStreaming"
          @click="handleSend"
          class="send-button"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { ChatDotRound, Close, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { askAI } from '@/api/ai'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

// 状态
const messages = ref([])
const inputText = ref('')
const isTyping = ref(false)
const messageContainer = ref(null)
const conversationId = ref(null)
const streamingMessage = ref('')
const isStreaming = ref(false)

// 生成唯一的会话ID
const generateConversationId = () => {
  return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 快捷问题
const quickQuestions = [
  '如何区分干垃圾和湿垃圾？',
  '过期药品属于什么垃圾？',
  '塑料瓶应该怎么处理？',
  '垃圾分类有什么好处？'
]

// 发送快捷问题
const sendQuickQuestion = (question) => {
  inputText.value = question
  handleSend()
}

// 发送消息
const handleSend = async () => {
  const question = inputText.value.trim()
  if (!question || isTyping.value) return

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: question,
    time: getCurrentTime()
  })

  inputText.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    // 如果还没有会话ID，生成一个新的
    if (!conversationId.value) {
      conversationId.value = generateConversationId()
    }

    // 调用 AI API
    const response = await askAI(question, conversationId.value)
    
    // 保持会话ID
    if (response.conversation_id) {
      conversationId.value = response.conversation_id
    }

    // 使用打字机效果显示AI回复
    const answer = response.answer || '抱歉，我现在无法回答这个问题。'
    isTyping.value = false  // 先隐藏打字指示器
    await typeWriter(answer)
    
  } catch (error) {
    console.error('AI对话错误:', error)
    isTyping.value = false
    
    // 错误信息也用打字机效果显示
    await typeWriter('抱歉，服务暂时不可用，请稍后再试。')
    
    ElMessage.error('AI服务异常，请稍后重试')
  }
}

// 打字机效果显示AI回答
const typeWriter = async (text) => {
  const words = text.split('')
  streamingMessage.value = ''
  isStreaming.value = true
  
  // 添加流式消息占位符
  const aiMessageIndex = messages.value.length
  messages.value.push({
    type: 'ai',
    content: '',
    time: getCurrentTime()
  })
  
  scrollToBottom()
  
  for (let i = 0; i < words.length; i++) {
    streamingMessage.value += words[i]
    // 更新消息内容
    messages.value[aiMessageIndex].content = streamingMessage.value
    
    await new Promise(resolve => setTimeout(resolve, 30)) // 每个字符延迟30ms
    
    // 每10个字符滚动一次
    if (i % 10 === 0) {
      scrollToBottom()
    }
  }
  
  isStreaming.value = false
  streamingMessage.value = ''
  scrollToBottom()
}

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
  emit('close')
}

// 点击遮罩层关闭
const handleOverlayClick = () => {
  handleClose()
}

// 监听可见性变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    // 如果还没有会话ID，生成一个新的
    if (!conversationId.value) {
      conversationId.value = generateConversationId()
    }
    scrollToBottom()
  }
})
</script>

<style scoped>
.ai-chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.ai-chat-dialog {
  width: 90%;
  max-width: 350px;
  margin: 0 auto;
  height: 70vh;
  max-height: 700px;
  background: white;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 移除未使用的动画 */
@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* 头部 */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 0 0;
  flex-shrink: 0;
  border-top: none;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.ai-icon {
  font-size: 24px;
}

.close-icon {
  font-size: 24px;
  cursor: pointer;
  transition: transform 0.2s;
}

.close-icon:hover {
  transform: rotate(90deg);
}

/* 消息区域 */
.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 30px;
}

.quick-questions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.quick-question-item {
  padding: 12px 16px;
  background: white;
  border: 2px solid #667eea;
  border-radius: 12px;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.quick-question-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 消息项 */
.message-item {
  margin-bottom: 16px;
  display: flex;
  animation: messageIn 0.3s ease;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-item.ai .message-bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-content {
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  margin-top: 6px;
  opacity: 0.7;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 输入区域 */
.input-container {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 20px 20px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-shrink: 0;
}

.input-container :deep(.el-textarea__inner) {
  border-radius: 12px;
  resize: none;
}

.send-button {
  border-radius: 12px;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  transition: all 0.3s;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  background: #e5e7eb;
  color: #9ca3af;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .ai-chat-dialog {
    height: 75vh;
    border-radius: 16px;
    width: 95%;
    overflow: hidden;
  }

  .quick-questions {
    grid-template-columns: 1fr;
  }

  .message-bubble {
    max-width: 85%;
  }

  .dialog-header {
    padding: 16px 20px;
    border-radius: 16px 16px 0 0;
  }

  .header-title {
    font-size: 16px;
  }

  .input-container {
    border-radius: 0 0 16px 16px;
  }
}

/* 滚动条样式 */
.message-container::-webkit-scrollbar {
  width: 6px;
}

.message-container::-webkit-scrollbar-track {
  background: transparent;
}

.message-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.message-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>

