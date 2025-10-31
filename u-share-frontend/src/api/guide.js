import axios from 'axios'

/**
 * 投放引导相关 API
 */

/**
 * 获取所有垃圾桶坐标
 * @returns {Promise} 垃圾桶列表
 */
export const getDustbins = async () => {
  try {
    const response = await axios.get('/guide/dustbins', {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return { data: response.data }
  } catch (error) {
    console.error('获取垃圾桶列表失败:', error)
    throw handleApiError(error, '获取垃圾桶列表')
  }
}

/**
 * 根据用户坐标获取最近垃圾桶及导航信息
 * @param {number} lng - 经度
 * @param {number} lat - 纬度
 * @returns {Promise} 最近垃圾桶信息
 */
export const getNearestDustbin = async (lng, lat) => {
  try {
    // 输入验证
    if (typeof lng !== 'number' || typeof lat !== 'number') {
      throw new Error('经纬度必须为数字')
    }

    if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
      throw new Error('经纬度范围无效')
    }

    const response = await axios.get('/guide/nearest', {
      params: {
        lng,
        lat
      },
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return { data: response.data }
  } catch (error) {
    console.error('获取最近垃圾桶失败:', error)
    throw handleApiError(error, '获取最近垃圾桶')
  }
}

/**
 * 处理API错误
 * @param {Error} error - 错误对象
 * @param {string} operation - 操作名称
 * @returns {Error} 处理后的错误
 */
const handleApiError = (error, operation) => {
  if (error.response) {
    // 服务器返回错误响应
    const { status, data } = error.response
    const message = data?.detail || data?.message || `服务器错误: ${status}`
    return new Error(`${operation}失败: ${message}`)
  } else if (error.request) {
    // 请求已发送但没有收到响应
    return new Error(`${operation}失败: 网络连接异常，请检查网络`)
  } else {
    // 请求配置出错
    return new Error(`${operation}失败: ${error.message}`)
  }
}





