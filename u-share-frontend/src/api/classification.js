import request from './request'
import axios from 'axios'

/**
 * 垃圾分类识别相关 API
 */

/**
 * 文字识别垃圾分类
 * @param {string} text - 垃圾名称文本
 * @returns {Promise} 识别结果
 */
export const classifyByText = async (text) => {
  try {
    // 输入验证
    if (!text || typeof text !== 'string') {
      throw new Error('请输入有效的文字内容')
    }
    
    const trimmedText = text.trim()
    if (trimmedText.length === 0) {
      throw new Error('请输入要识别的垃圾名称')
    }
    
    if (trimmedText.length > 100) {
      throw new Error('输入内容不能超过100个字符')
    }

    const response = await axios.post('/nlp/recognize/text', {
      text: trimmedText
    }, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 处理响应数据
    const { input_text, category } = response.data
    
    // 转换为前端需要的格式
    const result = {
      name: input_text,
      type: category,
      typeClass: getTypeClass(category),
      description: getDescription(category),
      tips: getTips(category)
    }

    return { data: result }
  } catch (error) {
    console.error('文字识别失败:', error)
    throw handleApiError(error, '文字识别')
  }
}

/**
 * 语音识别垃圾分类
 * @param {File} audioFile - 音频文件
 * @returns {Promise} 识别结果
 */
export const speechToText = async (audioFile) => {
  try {
    // 输入验证
    if (!audioFile || !(audioFile instanceof File)) {
      throw new Error('请提供有效的音频文件')
    }

    // 检查文件类型
    const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/webm', 'audio/ogg']
    if (!allowedTypes.includes(audioFile.type)) {
      throw new Error('不支持的音频格式，请使用 WAV、MP3、WebM 或 OGG 格式')
    }

    // 检查文件大小 (10MB)
    const maxSize = 10 * 1024 * 1024
    if (audioFile.size > maxSize) {
      throw new Error('音频文件过大，请选择小于10MB的文件')
    }

    const formData = new FormData()
    formData.append('file', audioFile)

    const response = await axios.post('/nlp/recognize/voice', formData, {
      timeout: 30000, // 语音识别可能需要更长时间
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 处理响应数据
    const { result: recognizedText, category } = response.data
    
    if (!recognizedText || recognizedText.trim().length === 0) {
      throw new Error('语音识别失败，请重新录音')
    }

    // 转换为前端需要的格式
    const data = {
      name: recognizedText.trim(),
      type: category,
      typeClass: getTypeClass(category),
      description: getDescription(category),
      tips: getTips(category)
    }

    return { data }
  } catch (error) {
    console.error('语音识别失败:', error)
    throw handleApiError(error, '语音识别')
  }
}

/**
 * 图像识别垃圾分类
 * @param {File} imageFile - 图片文件
 * @returns {Promise} 识别结果
 */
export const recognizeImage = async (imageFile) => {
  try {
    // 输入验证
    if (!imageFile || !(imageFile instanceof File)) {
      throw new Error('请提供有效的图片文件')
    }

    // 检查文件类型
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(imageFile.type)) {
      throw new Error('不支持的图片格式，请使用 JPG、PNG、GIF 或 WebP 格式')
    }

    // 检查文件大小 (10MB)
    const maxSize = 10 * 1024 * 1024
    if (imageFile.size > maxSize) {
      throw new Error('图片文件过大，请选择小于10MB的图片')
    }

    const formData = new FormData()
    formData.append('file', imageFile)

    const response = await axios.post('/image/recognize/image', formData, {
      timeout: 20000, // 图像识别可能需要较长时间
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 处理响应数据
    const { category, confidence } = response.data
    
    // 转换为前端需要的格式
    const result = {
      name: `识别物品 (${Math.round(confidence * 100)}% 置信度)`,
      type: category,
      typeClass: getTypeClass(category),
      description: getDescription(category),
      tips: getTips(category),
      confidence: Math.round(confidence * 100),
      similar: generateSimilarItems(category)
    }

    return { data: result }
  } catch (error) {
    console.error('图像识别失败:', error)
    throw handleApiError(error, '图像识别')
  }
}

/**
 * 获取识别历史记录
 * @param {number} limit - 返回记录数量
 * @returns {Promise} 历史记录列表
 */
export const getRecognitionHistory = (limit = 10) => {
  return request({
    url: '/classification/history',
    method: 'get',
    params: { limit }
  })
}

/**
 * 保存识别记录
 * @param {object} data - 识别记录数据
 * @returns {Promise} 保存结果
 */
export const saveRecognitionRecord = (data) => {
  return request({
    url: '/classification/record',
    method: 'post',
    data
  })
}

/**
 * 获取垃圾分类类型对应的CSS类名
 * @param {string} category - 分类名称
 * @returns {string} CSS类名
 */
const getTypeClass = (category) => {
  const typeMap = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return typeMap[category] || 'other'
}

/**
 * 获取分类描述
 * @param {string} category - 分类名称
 * @returns {string} 描述
 */
const getDescription = (category) => {
  const descMap = {
    '可回收物': '投放至蓝色可回收物垃圾桶',
    '有害垃圾': '投放至红色有害垃圾桶',
    '厨余垃圾': '投放至绿色厨余垃圾桶',
    '其他垃圾': '投放至灰色其他垃圾桶'
  }
  return descMap[category] || '投放至灰色其他垃圾桶'
}

/**
 * 获取分类提示
 * @param {string} category - 分类名称
 * @returns {string} 提示
 */
const getTips = (category) => {
  const tipsMap = {
    '可回收物': '请清洗干净后投放，提高回收利用率',
    '有害垃圾': '有害垃圾需单独投放，避免污染环境',
    '厨余垃圾': '沥干水分后投放，包装物请单独处理',
    '其他垃圾': '无法回收利用的垃圾统一投放至此'
  }
  return tipsMap[category] || '无法回收利用的垃圾统一投放至此'
}

/**
 * 生成相似物品推荐
 * @param {string} category - 分类名称
 * @returns {Array} 相似物品列表
 */
const generateSimilarItems = (category) => {
  const similarMap = {
    '可回收物': [
      { name: '塑料瓶', match: 95 },
      { name: '废纸', match: 90 },
      { name: '玻璃瓶', match: 85 }
    ],
    '有害垃圾': [
      { name: '废电池', match: 95 },
      { name: '过期药品', match: 90 },
      { name: '荧光灯管', match: 85 }
    ],
    '厨余垃圾': [
      { name: '果皮', match: 95 },
      { name: '剩菜', match: 90 },
      { name: '茶叶渣', match: 85 }
    ],
    '其他垃圾': [
      { name: '烟蒂', match: 95 },
      { name: '尘土', match: 90 },
      { name: '污染纸张', match: 85 }
    ]
  }
  return similarMap[category] || []
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
        message = data?.detail || '请求参数错误'
        break
      case 401:
        message = '未授权访问，请重新登录'
        break
      case 403:
        message = '没有权限访问该功能'
        break
      case 404:
        message = '服务暂时不可用，请稍后重试'
        break
      case 413:
        message = '文件过大，请选择较小的文件'
        break
      case 415:
        message = '不支持的文件格式'
        break
      case 500:
        message = '服务器内部错误，请稍后重试'
        break
      case 502:
        message = '服务暂时不可用，请稍后重试'
        break
      case 503:
        message = '服务繁忙，请稍后重试'
        break
      default:
        message = data?.detail || `${operation}失败，请稍后重试`
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

/**
 * 模拟文字识别（用于测试）
 * @param {string} text - 垃圾名称
 * @returns {Promise} 模拟结果
 */
export const mockClassifyByText = (text) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const lowerText = text.toLowerCase().trim()
      
      let result = {
        name: text,
        type: '其他垃圾',
        typeClass: 'other',
        description: '投放至灰色其他垃圾桶',
        tips: '无法回收利用的垃圾统一投放至此'
      }
      
      if (lowerText.includes('塑料') || lowerText.includes('瓶') || 
          lowerText.includes('纸') || lowerText.includes('玻璃') || 
          lowerText.includes('金属') || lowerText.includes('衣')) {
        result = {
          name: text,
          type: '可回收物',
          typeClass: 'recyclable',
          description: '投放至蓝色可回收物垃圾桶',
          tips: '请清洗干净后投放，提高回收利用率'
        }
      } else if (lowerText.includes('电池') || lowerText.includes('药') || 
                 lowerText.includes('灯') || lowerText.includes('温度计')) {
        result = {
          name: text,
          type: '有害垃圾',
          typeClass: 'harmful',
          description: '投放至红色有害垃圾桶',
          tips: '有害垃圾需单独投放，避免污染环境'
        }
      } else if (lowerText.includes('果') || lowerText.includes('菜') || 
                 lowerText.includes('剩') || lowerText.includes('皮') || 
                 lowerText.includes('骨') || lowerText.includes('茶')) {
        result = {
          name: text,
          type: '厨余垃圾',
          typeClass: 'kitchen',
          description: '投放至绿色厨余垃圾桶',
          tips: '沥干水分后投放，包装物请单独处理'
        }
      }
      
      resolve({ data: result })
    }, 1500)
  })
}

/**
 * 模拟图像识别（用于测试）
 * @returns {Promise} 模拟结果
 */
export const mockRecognizeImage = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const results = [
        {
          name: '塑料饮料瓶',
          type: '可回收物',
          typeClass: 'recyclable',
          description: '投放至蓝色可回收物垃圾桶',
          tips: '请清洗干净后投放，瓶盖和瓶身可分开投放',
          confidence: 95,
          similar: [
            { name: '矿泉水瓶', match: 92 },
            { name: '可乐瓶', match: 88 },
            { name: '塑料杯', match: 76 }
          ]
        },
        {
          name: '废电池',
          type: '有害垃圾',
          typeClass: 'harmful',
          description: '投放至红色有害垃圾桶',
          tips: '有害垃圾需单独投放，避免污染环境',
          confidence: 92,
          similar: [
            { name: '纽扣电池', match: 89 },
            { name: '充电电池', match: 85 },
            { name: '蓄电池', match: 78 }
          ]
        },
        {
          name: '苹果果皮',
          type: '厨余垃圾',
          typeClass: 'kitchen',
          description: '投放至绿色厨余垃圾桶',
          tips: '沥干水分后投放，包装物请单独处理',
          confidence: 89,
          similar: [
            { name: '香蕉皮', match: 87 },
            { name: '橙子皮', match: 84 },
            { name: '西瓜皮', match: 80 }
          ]
        }
      ]
      
      const result = results[Math.floor(Math.random() * results.length)]
      resolve({ data: result })
    }, 2500)
  })
}

export default {
  classifyByText,
  speechToText,
  recognizeImage,
  getRecognitionHistory,
  saveRecognitionRecord,
  mockClassifyByText,
  mockRecognizeImage
}

