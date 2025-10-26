import axios from 'axios'

/**
 * AI对话相关 API
 */

/**
 * 向AI发送问题并获取回答
 * @param {string} question - 用户问题
 * @param {string} conversationId - 会话ID（可选）
 * @returns {Promise} AI回答
 */
export const askAI = async (question, conversationId = null) => {
  try {
    // 输入验证
    if (!question || typeof question !== 'string') {
      throw new Error('请输入有效的问题')
    }
    
    const trimmedQuestion = question.trim()
    if (trimmedQuestion.length === 0) {
      throw new Error('问题不能为空')
    }
    
    if (trimmedQuestion.length > 500) {
      throw new Error('问题长度不能超过500个字符')
    }

    // 准备请求数据
    const requestData = {
      question: trimmedQuestion
    }
    
    // 如果有会话ID，添加到请求中
    if (conversationId) {
      requestData.conversation_id = conversationId
    }

    const response = await axios.post('/ai/ask-ai', requestData, {
      timeout: 30000, // 30秒超时
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 处理响应数据
    const { answer } = response.data
    
    // 返回格式统一的数据
    return {
      answer: answer || '抱歉，我现在无法回答这个问题。',
      conversation_id: conversationId || null, // 保持原有的conversation_id
      response: response.data
    }
  } catch (error) {
    console.error('AI对话失败:', error)
    throw handleApiError(error, 'AI对话')
  }
}

/**
 * 处理API错误
 * @param {Error} error - 错误对象
 * @param {string} operation - 操作名称
 * @returns {Error} 处理后的错误
 */
const handleApiError = (error, operation) => {
  let message = `${operation}失败`
  
  if (error.response) {
    // 服务器响应错误
    const { status, data } = error.response
    switch (status) {
      case 400:
        message = data?.detail || data?.message || '请求参数错误'
        break
      case 401:
        message = '未授权访问，请重新登录'
        break
      case 403:
        message = '没有权限访问该功能'
        break
      case 404:
        message = 'AI服务暂时不可用，请稍后重试'
        break
      case 429:
        message = '请求过于频繁，请稍后再试'
        break
      case 500:
        message = 'AI服务内部错误，请稍后重试'
        break
      case 502:
        message = 'AI服务暂时不可用，请稍后重试'
        break
      case 503:
        message = 'AI服务繁忙，请稍后重试'
        break
      default:
        message = data?.detail || data?.message || `${operation}失败，请稍后重试`
    }
  } else if (error.request) {
    // 网络错误
    if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查网络连接'
    } else {
      message = '网络连接失败，请检查网络设置'
    }
  } else if (error.message) {
    // 其他错误
    message = error.message
  }
  
  const newError = new Error(message)
  newError.originalError = error
  newError.operation = operation
  return newError
}

export default {
  askAI
}

