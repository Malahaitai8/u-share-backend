<template>
  <div class="guide-container with-bottom-nav">
    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="time">{{ currentTime }}</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">🔋</span>
      </div>
    </div>

    <!-- 顶部导航栏（浅蓝色） -->
    <div class="nav-bar">
      <div class="nav-content">
        <el-button 
          class="back-button" 
          @click="goBack"
          circle
          size="small"
        >
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2 class="nav-title">投放引导</h2>
        <div class="nav-buttons">
          <!-- 选择位置按钮 -->
          <el-button 
            class="select-position-button" 
            :class="{ 'is-success': selectingPosition }"
            @click="toggleSelectPosition"
            circle
            plain
            size="small"
          >
            <el-icon><Aim /></el-icon>
          </el-button>

          <!-- 定位按钮 -->
          <el-button 
            class="location-button" 
            @click="handleLocation"
            circle
            plain
            size="small"
            :loading="locating"
          >
            <el-icon><LocationFilled /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 地图容器 -->
    <div id="map-container" class="map-container">
      <!-- 经纬度显示（地图左上角） -->
      <div v-if="userPosition" class="map-coordinates">
        {{ formatCoordinates(userPosition.lng, userPosition.lat) }}
      </div>
      <div v-if="mapError" class="map-error-panel">
        <div class="map-error-title">地图加载失败</div>
        <div class="map-error-text">{{ mapError }}</div>
        <img class="map-fallback-image" :src="fallbackMapUrl" alt="地图静态预览" />
      </div>
    </div>

    <!-- 最近垃圾桶信息卡片（可展开/收起） -->
    <div v-if="displayInfo" class="nearest-info-card" :class="{ 'expanded': cardExpanded }">
      <!-- 卡片头部（可点击展开/收起） -->
      <div class="info-header" @click="toggleCard">
        <div class="header-left">
          <el-icon class="info-icon"><Location /></el-icon>
          <span class="info-title">最近垃圾站点</span>
        </div>
        <el-icon class="expand-icon" :class="{ 'expanded': cardExpanded }">
          <ArrowUp />
        </el-icon>
      </div>
      
      <!-- 卡片内容（展开时显示） -->
      <div v-show="cardExpanded" class="info-content">
        <div class="info-name">{{ displayInfo.dustbin.name }}</div>
        <div v-if="displayInfo.dustbin.description" class="info-description">
          {{ displayInfo.dustbin.description }}
        </div>
        
        <!-- 如果是近距离（<10米），突出显示提示信息 -->
        <div v-if="displayInfo.nearby" class="nearby-alert">
          <div class="nearby-icon">📍</div>
          <div class="nearby-text">
            <div class="nearby-title">已到达附近</div>
            <div class="nearby-distance">距离不到 {{ displayInfo.distance }}米</div>
            <div class="nearby-tip">请就近投放垃圾</div>
          </div>
        </div>
        
        <!-- 如果距离较远（≥10米），显示详细导航信息 -->
        <template v-else>
          <div v-if="displayInfo.distance" class="info-distance">
            <span class="distance-label">距离：</span>
            <span class="distance-value">{{ displayInfo.distance }}米</span>
          </div>
          <div v-if="displayInfo.duration" class="info-duration">
            <span class="duration-label">预计时间：</span>
            <span class="duration-value">约{{ formatDuration(displayInfo.duration) }}</span>
          </div>
          <div v-if="displayInfo.message" class="info-message">
            {{ displayInfo.message }}
          </div>
        </template>
        
        <!-- 有导航链接时显示导航按钮 -->
        <div v-if="nearestInfo && (nearestInfo.nav_url || nearestInfo.deeplink)" class="info-buttons">
          <el-button 
            type="primary" 
            size="small" 
            class="nav-button"
            @click="openNavigation"
          >
            <el-icon><Guide /></el-icon>
            <span>开始导航</span>
          </el-button>
        </div>
        <div v-if="isManualStationSelected" class="info-buttons secondary-actions">
          <el-button
            size="small"
            class="reset-nearest-button"
            @click="resetToRecommendedStation"
          >
            返回最近站点
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载提示 -->
    <div v-if="loading" class="loading-overlay">
      <el-icon class="loading-icon is-loading"><Loading /></el-icon>
      <span class="loading-text">加载中...</span>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Location, LocationFilled, Guide, Loading, ArrowUp, Aim } from '@element-plus/icons-vue'
import BottomNav from '@/components/BottomNav.vue'
import { getDustbins, getNearestDustbin, getDustbinRoute } from '@/api/guide'

const router = useRouter()

// 高德地图API Key - 支持从环境变量读取
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY
const AMAP_SECURITY_JS_CODE = import.meta.env.VITE_AMAP_SECURITY_JS_CODE
const AMAP_SERVICE_HOST = '/_AMapService'

// 响应式数据
const loading = ref(false)
const map = ref(null)
const markers = ref([])
const infoWindow = ref(null)
const currentTime = ref('9:41')
const nearestInfo = ref(null)
const recommendedInfo = ref(null)
const activeDustbin = ref(null)
const userPosition = ref(null)
const cardExpanded = ref(true) // 卡片默认展开
const locating = ref(false) // 定位按钮加载状态
const selectingPosition = ref(false) // 是否在选择位置模式
const autoLocatedPosition = ref(null) // 自动定位的位置（用于比较）
const manualSelectedDustbin = ref(null) // 用户手动选择的站点

// 初始化时间显示
const mapError = ref('')

const fallbackMapUrl = computed(() => {
  const lng = userPosition.value?.lng || 116.351
  const lat = userPosition.value?.lat || 39.954
  return `https://restapi.amap.com/v3/staticmap?location=${lng},${lat}&zoom=16&size=750*500&markers=mid,0xFF0000,A:${lng},${lat}&key=${AMAP_KEY || ''}`
})

const sameDustbin = (first, second) => {
  if (!first || !second) return false

  const firstLng = parseFloat(first.lng)
  const firstLat = parseFloat(first.lat)
  const secondLng = parseFloat(second.lng)
  const secondLat = parseFloat(second.lat)

  return Math.abs(firstLng - secondLng) < 0.0001 &&
    Math.abs(firstLat - secondLat) < 0.0001
}

const isManualStationSelected = computed(() => {
  return Boolean(
    activeDustbin.value &&
    recommendedInfo.value?.dustbin &&
    !sameDustbin(activeDustbin.value, recommendedInfo.value.dustbin)
  )
})

const buildDustbinNavigation = (dustbin) => {
  const lng = parseFloat(dustbin?.lng)
  const lat = parseFloat(dustbin?.lat)

  if (Number.isNaN(lng) || Number.isNaN(lat)) {
    return {
      nav_url: null,
      deeplink: null
    }
  }

  const name = encodeURIComponent(dustbin?.name || '垃圾站点')
  return {
    nav_url: `https://uri.amap.com/navigation?to=${lng},${lat},${name}&mode=walk&src=u-share`,
    deeplink: `amapuri://route/plan/?dlat=${lat}&dlon=${lng}&dname=${name}&t=1&sourceApplication=u-share`
  }
}

const buildPendingRouteInfo = (dustbin) => ({
  nearby: false,
  message: '正在获取该站点的导航信息...',
  distance: null,
  duration: null,
  dustbin,
  nav_url: null,
  deeplink: null
})

const displayInfo = computed(() => {
  if (isManualStationSelected.value && nearestInfo.value) {
    return nearestInfo.value
  }

  return recommendedInfo.value || nearestInfo.value
})

const updateTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return ''
  if (seconds < 60) {
    return `${seconds}秒`
  }
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (remainingSeconds === 0) {
    return `${minutes}分钟`
  }
  return `${minutes}分${remainingSeconds}秒`
}

// 格式化坐标显示
const formatCoordinates = (lng, lat) => {
  if (!lng || !lat) return ''
  return `${lng.toFixed(6)}, ${lat.toFixed(6)}`
}

// 加载高德地图
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    // 如果已经加载，直接resolve
    if (window.AMap && window.AMap.Map) {
      console.log('高德地图SDK已加载')
      resolve()
      return
    }

    // 如果已有脚本正在加载，等待它完成
    const existingScript = document.querySelector('script[src*="amap.com/maps"]')
    if (existingScript) {
      console.log('高德地图脚本正在加载，等待中...')
      const checkInterval = setInterval(() => {
        if (window.AMap && window.AMap.Map) {
          clearInterval(checkInterval)
          console.log('高德地图SDK加载完成（等待现有脚本）')
          resolve()
        }
      }, 100)
      
      setTimeout(() => {
        clearInterval(checkInterval)
        if (!window.AMap) {
          reject(new Error('高德地图加载超时'))
        }
      }, 10000)
      return
    }

    // 验证 API Key
    if (!AMAP_KEY || AMAP_KEY === 'YOUR_AMAP_KEY' || AMAP_KEY === 'your-amap-api-key') {
      reject(new Error('高德地图 API Key 未配置，请在前端 .env 文件中设置 VITE_AMAP_KEY'))
      return
    }

    window._AMapSecurityConfig = AMAP_SECURITY_JS_CODE
      ? { securityJsCode: AMAP_SECURITY_JS_CODE }
      : { serviceHost: AMAP_SERVICE_HOST }

    // 创建唯一的回调函数名
    const callbackName = `initAMap_${Date.now()}`
    let scriptLoaded = false
    let timeoutId = null
    
    window[callbackName] = () => {
      scriptLoaded = true
      delete window[callbackName]
      // 等待一下确保 AMap 完全初始化
      setTimeout(() => {
        if (window.AMap && window.AMap.Map) {
          console.log('高德地图SDK加载成功')
          if (timeoutId) clearTimeout(timeoutId)
          resolve()
        } else {
          console.error('高德地图API未正确加载')
          if (timeoutId) clearTimeout(timeoutId)
          reject(new Error('高德地图API未正确加载'))
        }
      }, 100)
    }
    
    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.crossOrigin = 'anonymous'
    // 加载地图主库、定位插件和逆地理编码插件
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.Geolocation,AMap.Geocoder&callback=${callbackName}`
    script.async = true
    script.defer = true
    
    script.onerror = (error) => {
      console.error('高德地图脚本加载错误:', error)
      delete window[callbackName]
      if (timeoutId) clearTimeout(timeoutId)
      
      // 检查网络连接
      if (!navigator.onLine) {
        reject(new Error('网络连接已断开，请检查网络后重试'))
      } else {
        reject(new Error('高德地图脚本加载失败，请检查 VITE_AMAP_KEY、域名白名单或安全配置'))
      }
    }
    
    script.onload = () => {
      console.log('高德地图脚本标签加载完成')
      // 如果回调函数在脚本加载后 3 秒内未执行，说明可能有问题
      if (!scriptLoaded) {
        setTimeout(() => {
          if (!window.AMap) {
            console.error('脚本已加载但 AMap 对象未初始化，可能是 API Key 无效或网络问题')
          }
        }, 3000)
      }
    }
    
    document.head.appendChild(script)
    console.log('开始加载高德地图SDK...')
    
    // 超时保护（增加到 20 秒）
    timeoutId = setTimeout(() => {
      if (!window.AMap) {
        script.remove()
        delete window[callbackName]
        reject(new Error('高德地图加载超时，请检查网络连接'))
      }
    }, 20000)
  })
}

// 初始化地图
const initMap = async () => {
  try {
    loading.value = true
    mapError.value = ''
    
    // 加载高德地图脚本（带重试机制）
    let retryCount = 0
    const maxRetries = 2
    
    while (retryCount <= maxRetries) {
      try {
        await loadAMapScript()
        break // 成功则退出循环
      } catch (error) {
        retryCount++
        if (retryCount > maxRetries) {
          throw error // 达到最大重试次数，抛出错误
        }
        console.warn(`高德地图加载失败，正在重试 (${retryCount}/${maxRetries})...`)
        // 等待 1 秒后重试
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
    
    // 确保 AMap 已加载
    if (!window.AMap || !window.AMap.Map) {
      throw new Error('高德地图API未正确初始化')
    }
    
    // 等待DOM元素准备好
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // 检查地图容器是否存在
    const mapContainer = document.getElementById('map-container')
    if (!mapContainer) {
      throw new Error('地图容器不存在')
    }
    
    // 创建地图实例
    // 使用北京交通大学的坐标作为初始显示位置
    // 北京交通大学（本部）：东经116.351，北纬39.954
    const bjtuCenter = [116.351, 39.954] // 北京交通大学坐标
    const baseLayer = new window.AMap.TileLayer({
      visible: true,
      opacity: 1,
      zIndex: 1
    })
    
    map.value = new window.AMap.Map('map-container', {
      zoom: 17, // 提高初始缩放级别，更聚焦校园
      center: bjtuCenter, // 默认显示交大位置
      viewMode: '2D',
      layers: [baseLayer]
    })

    // 等待地图加载完成
    await new Promise((resolve) => {
      map.value.on('complete', () => {
        console.log('地图加载完成')
        resolve()
      })
      // 超时保护，5秒后强制继续
      setTimeout(() => {
        console.warn('地图加载超时，继续执行')
        resolve()
      }, 5000)
    })

    // 创建信息窗口（固定大小）
    try {
      infoWindow.value = new window.AMap.InfoWindow({
        offset: new window.AMap.Pixel(0, -35),
        closeWhenClickMap: true,
        isCustom: true,
        autoMove: true
      })
    } catch (error) {
      console.error('创建信息窗口失败:', error)
      // 使用默认配置重试
      infoWindow.value = new window.AMap.InfoWindow({
        closeWhenClickMap: true,
        isCustom: true
      })
    }

    // 再次验证地图对象是否可用
    if (!map.value || !map.value.getContainer) {
      throw new Error('地图对象初始化失败')
    }

    // 添加地图点击事件监听（用于手动选择位置）
    map.value.on('click', handleMapClick)

    // 获取用户位置（不等待完成，避免阻塞地图加载）
    getUserLocation().then(() => {
      console.log('用户位置获取完成')
    }).catch((error) => {
      console.error('获取用户位置时发生错误:', error)
    })
    
    // 加载垃圾桶数据（并行加载，不依赖定位）
    await loadDustbins()
    
    console.log('地图初始化完成，地图已显示在北京交通大学范围')
    
  } catch (error) {
    console.error('地图初始化失败:', error)
    mapError.value = error?.message || '请检查高德地图配置和浏览器控制台报错'
    ElMessage.error('地图加载失败: ' + (error.message || '请检查网络连接'))
  } finally {
    loading.value = false
  }
}

// 使用逆地理编码验证定位地址
const verifyLocationWithGeocoder = async (lng, lat) => {
  return new Promise((resolve) => {
    if (!window.AMap || !window.AMap.Geocoder) {
      resolve(null)
      return
    }
    
    try {
      const geocoder = new window.AMap.Geocoder({
        city: '北京市',
        radius: 500
      })
      
      geocoder.getAddress([lng, lat], (status, result) => {
        if (status === 'complete' && result.info === 'OK') {
          const address = result.regeocode.formattedAddress || result.regeocode.addressComponent?.district || ''
          console.log('逆地理编码结果:', address, result.regeocode)
          resolve({
            address,
            addressComponent: result.regeocode.addressComponent,
            pois: result.regeocode.pois || []
          })
        } else {
          console.warn('逆地理编码失败:', result)
          resolve(null)
        }
      })
    } catch (error) {
      console.error('逆地理编码错误:', error)
      resolve(null)
    }
  })
}

// 获取用户位置（使用高德地图定位插件，自动进行坐标转换）
const getUserLocation = () => {
  return new Promise((resolve) => {
    console.log('开始获取用户位置...')
    
    // 优先使用高德地图定位插件（自动处理坐标转换）
    if (window.AMap && window.AMap.Geolocation && map.value) {
      try {
        const geolocation = new window.AMap.Geolocation({
          enableHighAccuracy: true, // 使用高精度定位（GPS）
          timeout: 20000, // 增加到20秒，给更多时间获取精确定位
          maximumAge: 0, // 定位结果缓存0毫秒，每次都重新定位
          convert: true, // 自动偏移坐标，偏移后的坐标为高德坐标（GCJ02）
          showButton: false, // 不显示定位按钮
          buttonDom: '', // 定位按钮的停靠位置
          showMarker: false, // 不显示定位标记
          showCircle: false, // 不显示精度圆圈
          panToLocation: false, // 定位成功后不自动调整地图视野
          zoomToAccuracy: false, // 定位成功后不自动调整地图缩放级别
          useNative: true, // 优先使用原生定位
          extensions: 'base' // 返回基本定位信息
        })

        geolocation.getCurrentPosition(async (status, result) => {
          if (status === 'complete') {
            // 定位成功，result.position 已经是GCJ02坐标系
            const { lng, lat } = result.position
            const locationType = result.location_type || 'unknown'
            const accuracy = result.accuracy || 0
            
            console.log('高德定位成功:', { 
              lng, 
              lat, 
              address: result.formattedAddress,
              accuracy: accuracy ? `${accuracy.toFixed(1)}米` : '未知',
              location_type: locationType,
              isOffline: result.isOffline // 是否为离线定位
            })
            
            // 验证坐标有效性
            if (isNaN(lng) || isNaN(lat)) {
              console.error('获取的位置坐标无效')
              resolve()
              return
            }
            
            // 检查定位类型，拒绝使用精度太低的定位方式
            // location_type: 'ip' 表示IP定位（精度差），'gps' 表示GPS定位（精度高）
            // 'ip' 定位的精度通常很差，可能显示在城市中心或其他错误位置
            if (locationType === 'ip' || (typeof result.isOffline !== 'undefined' && result.isOffline)) {
              console.warn('检测到IP定位或离线定位，精度可能不准确，尝试使用浏览器原生GPS定位')
              // 如果检测到IP定位，回退到浏览器原生定位（可能更准确）
              fallbackToBrowserGeolocation(resolve)
              return
            }
            
            // 验证定位精度，如果精度太差（大于100米），可能定位不准确
            if (accuracy > 0 && accuracy > 100) {
              console.warn('定位精度较差，可能影响准确性:', accuracy, '米')
            }
            
            // 使用逆地理编码验证定位地址
            const geocodeResult = await verifyLocationWithGeocoder(lng, lat)
            let isValidLocation = true
            
            if (geocodeResult) {
              console.log('定位验证地址:', geocodeResult.address)
              const address = geocodeResult.address
              const addressLower = address.toLowerCase()
              
              // 验证是否在北京交通大学附近（包括各种可能的表述）
              const keywords = ['交大', '交通大学', 'bjtu', '北京交通大学', '海淀', '上园村']
              const isNearBJTU = keywords.some(keyword => addressLower.includes(keyword.toLowerCase()))
              
              if (!isNearBJTU && accuracy > 50) {
                console.warn('定位地址可能不在交大附近:', address)
                // 如果精度差且地址不对，提示用户但继续使用（可能是网络定位偏差）
                isValidLocation = false
              }
            }
            
            // 更新用户位置
            userPosition.value = { lng, lat }
            // 保存自动定位的位置
            autoLocatedPosition.value = { lng, lat }
            
            // 强制设置地图中心为用户位置（确保使用最新的定位结果）
            if (map.value && window.AMap) {
              try {
                const validLng = parseFloat(lng)
                const validLat = parseFloat(lat)
                if (!isNaN(validLng) && !isNaN(validLat) &&
                    validLng >= -180 && validLng <= 180 &&
                    validLat >= -90 && validLat <= 90) {
                  // 强制更新地图中心，使用 panTo 确保平滑移动
                  map.value.panTo([validLng, validLat])
                  // 延迟一下再设置缩放，确保中心点先更新
                  setTimeout(() => {
                    if (map.value) {
                      map.value.setZoom(17)
                    }
                  }, 100)
                  
                  console.log('地图中心已更新到定位位置:', { lng: validLng, lat: validLat })
                } else {
                  console.warn('用户位置坐标无效，跳过设置地图中心:', { lng, lat })
                }
              } catch (error) {
                console.error('设置地图中心失败:', error)
              }
            }

            // 添加用户位置标记（会清除旧的标记）
            addUserMarker(lng, lat)
            
            // 获取最近垃圾桶
            loadNearestDustbin(lng, lat).then(() => {
              if (!isValidLocation && accuracy > 50) {
                console.warn('定位可能不准确，建议在室外使用GPS定位获得更精确的位置')
              }
              resolve()
            }).catch(() => resolve())
          } else {
            console.error('高德定位失败:', result)
            const errorInfo = result.info || result.message || '未知错误'
            console.warn('高德定位错误信息:', errorInfo)
            
            // 显示友好的错误提示
            if (errorInfo.includes('Geolocation permission denied')) {
              ElMessage.warning('定位权限被拒绝，请在浏览器设置中允许定位权限')
            }
            
            // 如果高德定位失败，尝试使用浏览器原生定位（需要手动转换坐标）
            console.log('尝试使用浏览器原生定位...')
            fallbackToBrowserGeolocation(resolve)
          }
        })
      } catch (error) {
        console.error('高德定位插件初始化失败:', error)
        // 如果插件初始化失败，回退到浏览器原生定位
        fallbackToBrowserGeolocation(resolve)
      }
    } else {
      // 如果高德地图未加载，使用浏览器原生定位
      fallbackToBrowserGeolocation(resolve)
    }
  })
}

// 回退到浏览器原生定位（需要手动转换坐标）
const fallbackToBrowserGeolocation = (resolve) => {
  if (!navigator.geolocation) {
    console.warn('浏览器不支持地理定位API')
    ElMessage.warning('您的浏览器不支持定位功能，将使用默认位置（北京交通大学）')
    resolve()
    return
  }

  console.log('使用浏览器原生定位API...')
  
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const { longitude, latitude, accuracy } = position.coords
      console.log('浏览器原生定位（WGS84）:', { 
        longitude, 
        latitude, 
        accuracy: accuracy ? `${accuracy.toFixed(1)}米` : '未知'
      })
      
      // 验证定位精度
      if (accuracy && accuracy > 100) {
        console.warn('浏览器定位精度较差:', accuracy, '米')
      }
      
      // 将WGS84坐标转换为GCJ02坐标（使用更精确的转换算法）
      const converted = convertWGS84ToGCJ02(longitude, latitude)
      console.log('坐标转换后（GCJ02）:', converted)
      
      // 验证坐标有效性
      if (isNaN(converted.lng) || isNaN(converted.lat)) {
        console.error('坐标转换失败')
        resolve()
        return
      }
      
      // 使用逆地理编码验证定位地址
      const geocodeResult = await verifyLocationWithGeocoder(converted.lng, converted.lat)
      if (geocodeResult) {
        console.log('定位验证地址:', geocodeResult.address)
      }
      
      userPosition.value = { lng: converted.lng, lat: converted.lat }
      // 保存自动定位的位置
      autoLocatedPosition.value = { lng: converted.lng, lat: converted.lat }
      
      // 强制设置地图中心为用户位置（确保使用最新的定位结果）
      if (map.value && window.AMap) {
        try {
          const validLng = parseFloat(converted.lng)
          const validLat = parseFloat(converted.lat)
          if (!isNaN(validLng) && !isNaN(validLat) &&
              validLng >= -180 && validLng <= 180 &&
              validLat >= -90 && validLat <= 90) {
            // 使用 panTo 强制更新地图中心
            map.value.panTo([validLng, validLat])
            setTimeout(() => {
              if (map.value) {
                map.value.setZoom(17)
              }
            }, 100)
            
            console.log('地图中心已更新到定位位置（浏览器原生定位）:', { lng: validLng, lat: validLat })
          } else {
            console.warn('用户位置坐标无效，跳过设置地图中心:', converted)
          }
        } catch (error) {
          console.error('设置地图中心失败:', error)
        }
      }

      // 添加用户位置标记
      addUserMarker(converted.lng, converted.lat)
      
      // 获取最近垃圾桶
      await loadNearestDustbin(converted.lng, converted.lat)
      
      resolve()
    },
    (error) => {
      console.error('浏览器原生定位失败:', error)
      let message = '获取位置失败，将使用默认位置（北京交通大学）'
      
      switch(error.code) {
        case error.PERMISSION_DENIED:
          message = '定位权限被拒绝。请点击地址栏的定位图标，允许此网站访问您的位置'
          console.warn('用户拒绝了定位权限请求')
          break
        case error.POSITION_UNAVAILABLE:
          message = '位置信息不可用，请检查设备定位设置'
          console.warn('位置信息不可用')
          break
        case error.TIMEOUT:
          message = '定位请求超时，请重试'
          console.warn('定位请求超时')
          break
        default:
          console.warn('未知的定位错误:', error)
      }
      
      ElMessage({
        message,
        type: 'warning',
        duration: 5000,
        showClose: true
      })
      
      resolve()
    },
    {
      enableHighAccuracy: true, // 启用高精度定位（GPS）
      timeout: 20000, // 增加到20秒
      maximumAge: 0 // 不使用缓存，每次都重新定位
    }
  )
}

// WGS84坐标转GCJ02坐标（火星坐标系）
const convertWGS84ToGCJ02 = (lng, lat) => {
  const a = 6378245.0 // 长半轴
  const ee = 0.00669342162296594323 // 偏心率平方
  let dLat = transformLat(lng - 105.0, lat - 35.0)
  let dLng = transformLng(lng - 105.0, lat - 35.0)
  const radLat = (lat / 180.0) * Math.PI
  let magic = Math.sin(radLat)
  magic = 1 - ee * magic * magic
  const sqrtMagic = Math.sqrt(magic)
  dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI)
  dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI)
  return {
    lng: lng + dLng,
    lat: lat + dLat
  }
}

const transformLat = (lng, lat) => {
  let ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng))
  ret += (20.0 * Math.sin(6.0 * lng * Math.PI) + 20.0 * Math.sin(2.0 * lng * Math.PI)) * 2.0 / 3.0
  ret += (20.0 * Math.sin(lat * Math.PI) + 40.0 * Math.sin(lat / 3.0 * Math.PI)) * 2.0 / 3.0
  ret += (160.0 * Math.sin(lat / 12.0 * Math.PI) + 320 * Math.sin(lat * Math.PI / 30.0)) * 2.0 / 3.0
  return ret
}

const transformLng = (lng, lat) => {
  let ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng))
  ret += (20.0 * Math.sin(6.0 * lng * Math.PI) + 20.0 * Math.sin(2.0 * lng * Math.PI)) * 2.0 / 3.0
  ret += (20.0 * Math.sin(lng * Math.PI) + 40.0 * Math.sin(lng / 3.0 * Math.PI)) * 2.0 / 3.0
  ret += (150.0 * Math.sin(lng / 12.0 * Math.PI) + 300.0 * Math.sin(lng / 30.0 * Math.PI)) * 2.0 / 3.0
  return ret
}

// 添加用户位置标记
const addUserMarker = (lng, lat) => {
  if (!map.value || !window.AMap) return

  const validLng = parseFloat(lng)
  const validLat = parseFloat(lat)
  
  if (isNaN(validLng) || isNaN(validLat)) {
    console.warn('无效的用户位置坐标')
    return
  }

  try {
    // 验证地图对象是否完全初始化
    if (!map.value || typeof map.value.getContainer !== 'function') {
      console.error('地图对象未完全初始化，无法添加用户位置标记')
      return
    }

    // 使用蓝色定位图标（高德默认样式）标记用户位置
    const iconSize = 48
    const gradientId = `blueGradient_${Date.now()}_${Math.random()}`
    const svg = `
      <svg width="${iconSize}" height="${iconSize}" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#4095FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3a86e6;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- 水滴形状 -->
        <path d="M24 2 C16 2, 8 8, 8 18 C8 26, 24 46, 24 46 C24 46, 40 26, 40 18 C40 8, 32 2, 24 2 Z" 
              fill="url(#${gradientId})" 
              stroke="#FFFFFF" 
              stroke-width="2"/>
        <!-- 内部圆圈 -->
        <circle cx="24" cy="18" r="8" fill="#FFFFFF" opacity="0.9"/>
        <!-- 中心点 -->
        <circle cx="24" cy="18" r="4" fill="#4095FF"/>
      </svg>
    `
    const base64 = btoa(unescape(encodeURIComponent(svg)))
    
    // 简化 Icon 创建，使用 offset 而不是 imageOffset
    let icon
    try {
      icon = new window.AMap.Icon({
        size: new window.AMap.Size(iconSize, iconSize),
        image: `data:image/svg+xml;base64,${base64}`,
        imageSize: new window.AMap.Size(iconSize, iconSize)
      })
    } catch (iconError) {
      console.error('创建用户位置图标失败，使用默认标记:', iconError)
      icon = undefined
    }
    
    const markerConfig = {
      position: [validLng, validLat],
      title: '我的位置',
      zIndex: 1000,
      offset: new window.AMap.Pixel(-iconSize / 2, -iconSize) // 使用 offset 将锚点设置在底部中心
    }
    
    // 只有当图标创建成功时才添加
    if (icon) {
      markerConfig.icon = icon
    }
    
    const marker = new window.AMap.Marker(markerConfig)
    
    // 标记为用户位置标记
    marker.isUserMarker = true

    // 添加到地图（优先使用 add 方法）
    if (map.value && map.value.add) {
      map.value.add(marker)
      markers.value.push(marker)
      console.log('成功添加用户位置标记（使用add）')
    } else {
      marker.setMap(map.value)
      markers.value.push(marker)
      console.log('成功添加用户位置标记（使用setMap）')
    }
  } catch (error) {
    console.error('添加用户位置标记失败:', error)
  }
}

// 加载垃圾桶数据
const loadDustbins = async () => {
  try {
    if (!map.value || !window.AMap) {
      console.error('地图未初始化')
      return
    }

    const response = await getDustbins()
    let dustbins = response.data || []
    
    // 验证数据格式
    if (!Array.isArray(dustbins)) {
      console.error('垃圾桶数据格式错误:', dustbins)
      ElMessage.warning('垃圾桶数据格式错误')
      return
    }
    
    console.log('获取到垃圾桶数据:', dustbins.length, '个')
    
    // 过滤无效数据
    dustbins = dustbins.filter(item => {
      if (!item || typeof item !== 'object') {
        console.warn('跳过无效的垃圾桶数据项:', item)
        return false
      }
      return true
    })
    
    if (dustbins.length === 0) {
      ElMessage.warning('暂无有效的垃圾桶数据')
      return
    }

    // 清除旧的垃圾桶标记（保留用户位置标记）
    markers.value.forEach(marker => {
      // 只清除非用户位置标记
      if (marker && marker.setMap && !marker.isUserMarker) {
        marker.setMap(null)
      }
    })
    // 只保留用户位置标记
    markers.value = markers.value.filter(marker => marker && marker.isUserMarker)

    // 验证并添加垃圾桶标记
    const validDustbins = []
    dustbins.forEach(dustbin => {
      // 检查 dustbin 对象是否存在且包含坐标
      if (!dustbin || dustbin.lng === undefined || dustbin.lng === null || 
          dustbin.lat === undefined || dustbin.lat === null) {
        console.warn('垃圾桶数据缺少坐标:', dustbin)
        return
      }
      
      // 验证坐标是否有效
      let lng = parseFloat(dustbin.lng)
      let lat = parseFloat(dustbin.lat)
      
      if (isNaN(lng) || isNaN(lat)) {
        console.warn('无效的垃圾桶坐标:', dustbin, { lng: dustbin.lng, lat: dustbin.lat })
        return
      }
      
      if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
        console.warn('坐标超出范围:', dustbin, { lng, lat })
        return
      }
      
      // 后端返回的坐标应该已经是GCJ02坐标系（高德地图坐标系）
      // 如果后端数据是WGS84坐标系，需要转换
      // 根据实际情况，如果发现坐标错位，可能需要启用转换
      // 暂时不使用转换，直接使用后端返回的坐标
      // const converted = convertWGS84ToGCJ02(lng, lat)
      // console.log(`垃圾桶坐标转换: ${dustbin.name || '未知'} WGS84(${lng}, ${lat}) -> GCJ02(${converted.lng}, ${converted.lat})`)
      
      // 直接使用后端返回的坐标
      const validDustbin = { ...dustbin, lng, lat }
      validDustbins.push(validDustbin)
      addDustbinMarker(validDustbin)
    })
    
    console.log('有效垃圾桶数量:', validDustbins.length, '个')

    // 如果有有效的垃圾桶数据，调整地图视野
    if (validDustbins.length > 0 && map.value && window.AMap) {
      try {
        const validCoords = []
        
        // 收集所有有效坐标
        validDustbins.forEach(dustbin => {
          const lng = parseFloat(dustbin.lng)
          const lat = parseFloat(dustbin.lat)
          if (!isNaN(lng) && !isNaN(lat) && 
              lng >= -180 && lng <= 180 && 
              lat >= -90 && lat <= 90) {
            validCoords.push([lng, lat])
          }
        })
        
        // 验证并添加用户位置坐标
        if (userPosition.value) {
          const userLng = parseFloat(userPosition.value.lng)
          const userLat = parseFloat(userPosition.value.lat)
          if (!isNaN(userLng) && !isNaN(userLat) && 
              userLng >= -180 && userLng <= 180 && 
              userLat >= -90 && userLat <= 90) {
            validCoords.push([userLng, userLat])
          }
        }
        
        // 只有在有有效坐标时才设置 bounds
        if (validCoords.length > 0) {
          const bounds = new window.AMap.Bounds()
          
          // 逐个添加坐标，捕获可能的错误
          for (const coord of validCoords) {
            try {
              const [lng, lat] = coord
              // 再次验证（三重保险）
              if (!isNaN(lng) && !isNaN(lat) && 
                  typeof lng === 'number' && typeof lat === 'number' &&
                  lng >= -180 && lng <= 180 && 
                  lat >= -90 && lat <= 90) {
                bounds.extend([lng, lat])
              }
            } catch (error) {
              console.warn('添加坐标到 bounds 失败:', coord, error)
            }
          }
          
          // 验证 bounds 是否有效
          try {
            if (bounds.getSouthWest && bounds.getNorthEast) {
              const sw = bounds.getSouthWest()
              const ne = bounds.getNorthEast()
              if (sw && ne && 
                  sw.getLng && sw.getLat && ne.getLng && ne.getLat &&
                  !isNaN(sw.getLng()) && !isNaN(sw.getLat()) &&
                  !isNaN(ne.getLng()) && !isNaN(ne.getLat())) {
                map.value.setBounds(bounds, false, [20, 20, 20, 20])
              } else {
                console.warn('bounds 无效，跳过设置地图视野')
              }
            }
          } catch (error) {
            console.warn('验证 bounds 失败:', error)
          }
        }
      } catch (error) {
        console.error('调整地图视野失败:', error)
      }
    }

  } catch (error) {
    console.error('加载垃圾桶数据失败:', error)
    ElMessage.error('加载垃圾桶数据失败')
  }
}

// 创建绿色定位图标（高德定位图标样式）
const createGreenLocationIcon = () => {
  // 创建绿色水滴形状的定位图标（SVG）
  // 图标尺寸为 48x48 像素，确保足够大
  // 使用时间戳确保渐变 ID 唯一
  const gradientId = `greenGradient_${Date.now()}_${Math.random()}`
  const svg = `
    <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#45a049;stop-opacity:1" />
        </linearGradient>
      </defs>
      <!-- 水滴形状 -->
      <path d="M24 2 C16 2, 8 8, 8 18 C8 26, 24 46, 24 46 C24 46, 40 26, 40 18 C40 8, 32 2, 24 2 Z" 
            fill="url(#${gradientId})" 
            stroke="#FFFFFF" 
            stroke-width="2"/>
      <!-- 内部圆圈 -->
      <circle cx="24" cy="18" r="8" fill="#FFFFFF" opacity="0.9"/>
      <!-- 中心点 -->
      <circle cx="24" cy="18" r="4" fill="#4CAF50"/>
    </svg>
  `
  const base64 = btoa(unescape(encodeURIComponent(svg)))
  return `data:image/svg+xml;base64,${base64}`
}

// 创建红色定位图标（用于最近垃圾桶标记）
const createRedLocationIcon = () => {
  // 创建红色水滴形状的定位图标（SVG）
  // 图标尺寸为 48x48 像素，确保足够大
  // 使用时间戳确保渐变 ID 唯一
  const gradientId = `redGradient_${Date.now()}_${Math.random()}`
  const svg = `
    <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#F44336;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#D32F2F;stop-opacity:1" />
        </linearGradient>
      </defs>
      <!-- 水滴形状 -->
      <path d="M24 2 C16 2, 8 8, 8 18 C8 26, 24 46, 24 46 C24 46, 40 26, 40 18 C40 8, 32 2, 24 2 Z" 
            fill="url(#${gradientId})" 
            stroke="#FFFFFF" 
            stroke-width="2"/>
      <!-- 内部圆圈 -->
      <circle cx="24" cy="18" r="8" fill="#FFFFFF" opacity="0.9"/>
      <!-- 中心点 -->
      <circle cx="24" cy="18" r="4" fill="#F44336"/>
    </svg>
  `
  const base64 = btoa(unescape(encodeURIComponent(svg)))
  return `data:image/svg+xml;base64,${base64}`
}

// 添加垃圾桶标记
const addDustbinMarker = (dustbin, isNearest = false) => {
  // 验证地图对象是否完全初始化
  if (!map.value || !window.AMap) {
    console.error('地图未初始化，无法添加标记')
    return
  }

  // 验证地图对象是否有必要的方法
  if (typeof map.value.getContainer !== 'function') {
    console.error('地图对象未完全初始化')
    return
  }

  // 验证坐标
  const lng = parseFloat(dustbin.lng)
  const lat = parseFloat(dustbin.lat)
  
  if (isNaN(lng) || isNaN(lat) || 
      lng < -180 || lng > 180 || 
      lat < -90 || lat > 90) {
    console.warn('无效的坐标，跳过标记:', dustbin)
    return
  }

  try {
    // 根据是否为最近垃圾桶选择图标颜色
    const iconSize = 48 // 图标尺寸
    const iconUrl = isNearest ? createRedLocationIcon() : createGreenLocationIcon()
    
    // 创建 Icon，确保所有参数都正确
    let icon
    try {
      icon = new window.AMap.Icon({
        size: new window.AMap.Size(iconSize, iconSize),
        image: iconUrl,
        imageSize: new window.AMap.Size(iconSize, iconSize)
      })
    } catch (iconError) {
      console.error('创建图标失败，使用默认标记:', iconError)
      // 如果自定义图标失败，使用默认标记样式
      icon = undefined
    }

    const markerConfig = {
      position: [lng, lat],
      title: dustbin.name || '垃圾桶',
      zIndex: isNearest ? 1000 : 999, // 最近垃圾桶标记层级更高
      offset: new window.AMap.Pixel(-iconSize / 2, -iconSize) // 使用 offset 将锚点设置在底部中心
    }
    
    // 只有当图标创建成功时才添加
    if (icon) {
      markerConfig.icon = icon
    }

    const marker = new window.AMap.Marker(markerConfig)

    // 标记为垃圾桶标记（非用户位置标记）
    marker.isUserMarker = false
    // 存储 dustbin 信息，方便后续更新颜色
    marker.dustbinData = dustbin
    // 标记是否为最近垃圾桶
    marker.isNearest = isNearest

    // 点击标记显示信息窗口
    marker.on('click', () => {
      showInfoWindow(marker, dustbin)
      activateDustbinSelection(dustbin)
    })

    // 确保地图对象可用后再添加标记
    if (map.value && map.value.add) {
      map.value.add(marker)
      markers.value.push(marker)
      console.log('成功添加垃圾桶标记:', dustbin.name, '位置:', [lng, lat], isNearest ? '(最近)' : '')
    } else {
      // 如果 add 方法不存在，使用 setMap
      marker.setMap(map.value)
      markers.value.push(marker)
      console.log('成功添加垃圾桶标记（使用setMap）:', dustbin.name, '位置:', [lng, lat], isNearest ? '(最近)' : '')
    }
  } catch (error) {
    console.error('添加标记失败:', error, dustbin)
  }
}

// 显示信息窗口（固定大小）
const showInfoWindow = (marker, dustbin) => {
  if (!map.value || !infoWindow.value || !window.AMap) {
    console.error('无法显示信息窗口: 地图或信息窗口未初始化')
    return
  }

  try {
    const escapeHtml = (text) => {
      if (!text) return ''
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }

    const description = dustbin.description || ''
    const content = `
      <div class="custom-info-window">
        <div class="info-window-title">${escapeHtml(dustbin.name || '垃圾桶')}</div>
        ${description ? `<div class="info-window-desc">${escapeHtml(description)}</div>` : ''}
      </div>
    `

    const position = marker.getPosition()
    if (!position || !position.getLng || !position.getLat) {
      console.error('无效的标记位置')
      return
    }

    infoWindow.value.setContent(content)
    infoWindow.value.open(map.value, position)
  } catch (error) {
    console.error('显示信息窗口失败:', error)
  }
}


// 更新标记颜色
const loadRouteForDustbin = async (lng, lat, dustbin) => {
  const validLng = parseFloat(lng)
  const validLat = parseFloat(lat)
  const dustbinLng = parseFloat(dustbin?.lng)
  const dustbinLat = parseFloat(dustbin?.lat)

  if ([validLng, validLat, dustbinLng, dustbinLat].some(value => Number.isNaN(value))) {
    throw new Error('路线坐标无效')
  }

  return getDustbinRoute(validLng, validLat, dustbinLng, dustbinLat)
}

const activateDustbinSelection = async (dustbin) => {
  if (!dustbin) {
    return
  }

  if (!userPosition.value) {
    ElMessage.warning('请先获取您的位置，再点击选择站点')
    return
  }

  activeDustbin.value = dustbin
  manualSelectedDustbin.value = dustbin
  
  nearestInfo.value = {
    nearby: false,
    message: '正在获取路线信息...',
    distance: null,
    duration: null,
    dustbin,
    ...buildDustbinNavigation(dustbin)
  }
  updateAllDustbinMarkersColor()

  try {
    const response = await loadRouteForDustbin(userPosition.value.lng, userPosition.value.lat, dustbin)
    nearestInfo.value = {
      ...response.data,
      dustbin,
      ...buildDustbinNavigation(dustbin)
    }
  } catch (error) {
    console.error('获取站点路线失败:', error)
    nearestInfo.value = {
      nearby: false,
      distance: null,
      duration: null,
      dustbin,
      ...buildDustbinNavigation(dustbin)
    }
  } finally {
    updateAllDustbinMarkersColor()
  }
}

const resetToRecommendedStation = () => {
  if (!recommendedInfo.value) {
    ElMessage.warning('暂无最近站点推荐')
    return
  }

  manualSelectedDustbin.value = null
  nearestInfo.value = recommendedInfo.value
  updateAllDustbinMarkersColor()
}

const updateMarkerColor = (marker, isNearest) => {
  if (!marker || !window.AMap) return
  
  try {
    const iconSize = 48
    const iconUrl = isNearest ? createRedLocationIcon() : createGreenLocationIcon()
    
    const icon = new window.AMap.Icon({
      size: new window.AMap.Size(iconSize, iconSize),
      image: iconUrl,
      imageSize: new window.AMap.Size(iconSize, iconSize)
    })
    
    marker.setIcon(icon)
    marker.isNearest = isNearest
    marker.setZIndex(isNearest ? 1000 : 999)
    
    console.log('更新标记颜色:', marker.dustbinData?.name, isNearest ? '(最近-红色)' : '(普通-绿色)')
  } catch (error) {
    console.error('更新标记颜色失败:', error)
  }
}

// 更新所有垃圾桶标记颜色
const updateAllDustbinMarkersColor = () => {
  if (!nearestInfo.value || !nearestInfo.value.dustbin) {
    // 如果没有最近垃圾桶信息，将所有标记设为绿色
    markers.value.forEach(marker => {
      if (!marker.isUserMarker && marker.isNearest) {
        updateMarkerColor(marker, false)
      }
    })
    return
  }
  
  const nearestDustbin = nearestInfo.value.dustbin
  const nearestLng = parseFloat(nearestDustbin.lng)
  const nearestLat = parseFloat(nearestDustbin.lat)
  
  // 遍历所有垃圾桶标记，更新颜色
  markers.value.forEach(marker => {
    if (marker.isUserMarker) return // 跳过用户位置标记
    
    if (!marker.dustbinData) return // 跳过没有数据的标记
    
    const markerLng = parseFloat(marker.dustbinData.lng)
    const markerLat = parseFloat(marker.dustbinData.lat)
    
    // 判断是否为最近垃圾桶（坐标比较，允许微小误差）
    const isNearest = !isNaN(nearestLng) && !isNaN(nearestLat) &&
                      !isNaN(markerLng) && !isNaN(markerLat) &&
                      Math.abs(markerLng - nearestLng) < 0.0001 &&
                      Math.abs(markerLat - nearestLat) < 0.0001
    
    // 如果当前标记状态与目标状态不一致，更新颜色
    if (marker.isNearest !== isNearest) {
      updateMarkerColor(marker, isNearest)
    }
  })
}

// 加载最近垃圾桶信息
const loadNearestDustbin = async (lng, lat) => {
  try {
    // 验证坐标有效性
    const validLng = parseFloat(lng)
    const validLat = parseFloat(lat)
    
    if (isNaN(validLng) || isNaN(validLat)) {
      console.warn('无法获取最近垃圾桶: 坐标无效', { lng, lat })
      return
    }
    
    if (validLng < -180 || validLng > 180 || validLat < -90 || validLat > 90) {
      console.warn('无法获取最近垃圾桶: 坐标超出范围', { lng: validLng, lat: validLat })
      return
    }
    
    const response = await getNearestDustbin(validLng, validLat)
    recommendedInfo.value = response.data

    if (manualSelectedDustbin.value && sameDustbin(manualSelectedDustbin.value, response.data.dustbin)) {
      manualSelectedDustbin.value = null
      nearestInfo.value = response.data
      updateAllDustbinMarkersColor()
      return
    }

    if (manualSelectedDustbin.value) {
      await activateDustbinSelection(manualSelectedDustbin.value)
      return
    }

    nearestInfo.value = response.data

    // 更新所有垃圾桶标记的颜色（最近垃圾桶显示红色，其他显示绿色）
    updateAllDustbinMarkersColor()
  } catch (error) {
    console.error('获取最近垃圾桶失败:', error)
    // 不显示错误消息，避免打扰用户
  }
}

// 定位按钮处理函数（使用高德地图定位插件或坐标转换）
const handleLocation = () => {
  locating.value = true
  
  // 优先使用高德地图定位插件（自动处理坐标转换）
  if (window.AMap && window.AMap.Geolocation && map.value) {
    try {
      const geolocation = new window.AMap.Geolocation({
        enableHighAccuracy: true, // 使用高精度定位（GPS）
        timeout: 20000, // 增加到20秒，给更多时间获取精确定位
        maximumAge: 0, // 不使用缓存，每次都重新定位
        convert: true, // 自动偏移坐标，偏移后的坐标为高德坐标（GCJ02）
        showButton: false,
        showMarker: false,
        showCircle: false,
        panToLocation: false,
        zoomToAccuracy: false,
        useNative: true, // 优先使用原生定位
        extensions: 'base' // 返回基本定位信息
      })

      geolocation.getCurrentPosition(async (status, result) => {
        if (status === 'complete') {
          const { lng, lat } = result.position
          const locationType = result.location_type || 'unknown'
          const accuracy = result.accuracy || 0
          
          console.log('高德定位成功（按钮点击）:', { 
            lng, 
            lat, 
            address: result.formattedAddress,
            accuracy: accuracy ? `${accuracy.toFixed(1)}米` : '未知',
            location_type: locationType,
            isOffline: result.isOffline
          })
          
          if (isNaN(lng) || isNaN(lat)) {
            ElMessage.error('获取的位置坐标无效')
            locating.value = false
            return
          }
          
          // 检查定位类型，拒绝使用精度太低的定位方式
          if (locationType === 'ip' || (typeof result.isOffline !== 'undefined' && result.isOffline)) {
            console.warn('检测到IP定位或离线定位，精度可能不准确，尝试使用浏览器原生GPS定位')
            handleLocationFallback()
            return
          }
          
          // 验证定位精度
          if (accuracy > 0 && accuracy > 100) {
            console.warn('定位精度较差:', accuracy, '米')
          }
          
          // 使用逆地理编码验证定位地址
          const geocodeResult = await verifyLocationWithGeocoder(lng, lat)
          if (geocodeResult) {
            console.log('定位验证地址:', geocodeResult.address)
          }
          
          userPosition.value = { lng, lat }
          // 保存自动定位的位置
          autoLocatedPosition.value = { lng, lat }
          
          // 强制设置地图中心为用户位置
          if (map.value && window.AMap) {
            try {
              // 使用 panTo 强制更新地图中心
              map.value.panTo([lng, lat])
              setTimeout(() => {
                if (map.value) {
                  map.value.setZoom(17)
                }
              }, 100)
              
              // 清除旧的用户位置标记
              const existingUserMarker = markers.value.find(m => m.isUserMarker)
              if (existingUserMarker) {
                existingUserMarker.setMap(null)
                const index = markers.value.indexOf(existingUserMarker)
                if (index > -1) {
                  markers.value.splice(index, 1)
                }
              }
              
              // 添加新的用户位置标记
              addUserMarker(lng, lat)
              
              // 获取最近垃圾桶
              loadNearestDustbin(lng, lat).then(() => {
                ElMessage.success('定位成功')
                locating.value = false
              }).catch(() => {
                ElMessage.success('定位成功')
                locating.value = false
              })
            } catch (error) {
              console.error('设置地图中心失败:', error)
              ElMessage.error('定位失败')
              locating.value = false
            }
          }
        } else {
          console.error('高德定位失败（按钮点击）:', result)
          // 回退到浏览器原生定位
          handleLocationFallback()
        }
      })
    } catch (error) {
      console.error('高德定位插件初始化失败（按钮点击）:', error)
      // 回退到浏览器原生定位
      handleLocationFallback()
    }
  } else {
    // 回退到浏览器原生定位
    handleLocationFallback()
  }
}

// 定位按钮的回退方法（使用浏览器原生定位并转换坐标）
const handleLocationFallback = () => {
  if (!navigator.geolocation) {
    ElMessage.warning('浏览器不支持定位功能')
    locating.value = false
    return
  }
  
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const { longitude, latitude, accuracy } = position.coords
      console.log('浏览器原生定位（按钮点击，WGS84）:', { 
        longitude, 
        latitude,
        accuracy: accuracy ? `${accuracy.toFixed(1)}米` : '未知'
      })
      
      // 验证定位精度
      if (accuracy && accuracy > 100) {
        console.warn('浏览器定位精度较差:', accuracy, '米')
      }
      
      // 将WGS84坐标转换为GCJ02坐标（使用更精确的转换算法）
      const converted = convertWGS84ToGCJ02(longitude, latitude)
      console.log('坐标转换后（按钮点击，GCJ02）:', converted)
      
      if (isNaN(converted.lng) || isNaN(converted.lat)) {
        ElMessage.error('获取的位置坐标无效')
        locating.value = false
        return
      }
      
      const validLng = parseFloat(converted.lng)
      const validLat = parseFloat(converted.lat)
      
      if (validLng < -180 || validLng > 180 || validLat < -90 || validLat > 90) {
        ElMessage.error('位置坐标超出范围')
        locating.value = false
        return
      }
      
      // 使用逆地理编码验证定位地址
      const geocodeResult = await verifyLocationWithGeocoder(validLng, validLat)
      if (geocodeResult) {
        console.log('定位验证地址:', geocodeResult.address)
      }
      
      userPosition.value = { lng: validLng, lat: validLat }
      // 保存自动定位的位置
      autoLocatedPosition.value = { lng: validLng, lat: validLat }
      
      // 强制设置地图中心为用户位置（确保使用最新的定位结果）
      if (map.value && window.AMap) {
        try {
          // 使用 panTo 强制更新地图中心
          map.value.panTo([validLng, validLat])
          setTimeout(() => {
            if (map.value) {
              map.value.setZoom(17)
            }
          }, 100)
          
          console.log('地图中心已更新到定位位置（按钮点击-浏览器原生定位）:', { lng: validLng, lat: validLat })
          
          // 清除旧的用户位置标记
          const existingUserMarker = markers.value.find(m => m.isUserMarker)
          if (existingUserMarker) {
            existingUserMarker.setMap(null)
            const index = markers.value.indexOf(existingUserMarker)
            if (index > -1) {
              markers.value.splice(index, 1)
            }
          }
          
          // 添加新的用户位置标记
          addUserMarker(validLng, validLat)
          
          // 获取最近垃圾桶
          await loadNearestDustbin(validLng, validLat)
          
          ElMessage.success('定位成功')
        } catch (error) {
          console.error('设置地图中心失败:', error)
          ElMessage.error('定位失败')
        }
      }
      
      locating.value = false
    },
    (error) => {
      console.error('获取位置失败:', error)
      let message = '获取位置失败'
      switch(error.code) {
        case error.PERMISSION_DENIED:
          message = '定位权限被拒绝，请在浏览器设置中允许定位'
          break
        case error.POSITION_UNAVAILABLE:
          message = '位置信息不可用'
          break
        case error.TIMEOUT:
          message = '定位超时，请重试'
          break
      }
      ElMessage.error(message)
      locating.value = false
    },
    {
      enableHighAccuracy: true, // 启用高精度定位（GPS）
      timeout: 20000, // 增加到20秒
      maximumAge: 0 // 不使用缓存，每次都重新定位
    }
  )
}

// 切换卡片展开/收起状态
const toggleCard = () => {
  cardExpanded.value = !cardExpanded.value
}

// 打开导航
const openNavigation = () => {
  if (!nearestInfo.value) {
    ElMessage.warning('暂无导航信息')
    return
  }
  
  // 优先使用 deeplink（尝试打开高德地图App）
  if (nearestInfo.value.deeplink) {
    try {
      // 尝试打开高德地图App
      window.location.href = nearestInfo.value.deeplink
      
      // 如果App未安装，延迟后打开H5导航作为备选
      if (nearestInfo.value.nav_url) {
        setTimeout(() => {
          window.open(nearestInfo.value.nav_url, '_blank')
        }, 2000)
      }
    } catch (error) {
      console.error('打开导航失败:', error)
      // 如果deeplink失败，回退到H5导航
      if (nearestInfo.value.nav_url) {
        window.open(nearestInfo.value.nav_url, '_blank')
      } else {
        ElMessage.error('无法打开导航，请稍后重试')
      }
    }
  } else if (nearestInfo.value.nav_url) {
    // 如果没有deeplink，直接使用H5导航
    window.open(nearestInfo.value.nav_url, '_blank')
  } else {
    ElMessage.warning('暂无可用导航信息')
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 切换选择位置模式
const toggleSelectPosition = () => {
  selectingPosition.value = !selectingPosition.value
  if (selectingPosition.value) {
    // 改变地图容器鼠标样式，提示用户可以选择位置
    const mapContainer = document.getElementById('map-container')
    if (mapContainer) {
      mapContainer.style.cursor = 'crosshair'
    }
    ElMessage({
      message: '✅ 已开启选择定位模式，请在地图上点击标记位置',
      type: 'success',
      duration: 3000,
      showClose: false,
      customClass: 'select-position-message'
    })
  } else {
    // 恢复默认鼠标样式
    const mapContainer = document.getElementById('map-container')
    if (mapContainer) {
      mapContainer.style.cursor = 'default'
    }
    ElMessage({
      message: 'ℹ️ 已关闭选择定位模式',
      type: 'info',
      duration: 2000,
      showClose: false
    })
  }
}

// 处理地图点击事件（用于手动选择位置）
const handleMapClick = async (e) => {
  // 只有在选择位置模式下才处理点击
  if (!selectingPosition.value) {
    return
  }
  
  const { lng, lat } = e.lnglat
  const selectedLng = parseFloat(lng)
  const selectedLat = parseFloat(lat)
  
  // 验证坐标有效性
  if (isNaN(selectedLng) || isNaN(selectedLat) ||
      selectedLng < -180 || selectedLng > 180 ||
      selectedLat < -90 || selectedLat > 90) {
    ElMessage.error('选择的位置坐标无效')
    return
  }
  
  // 检查是否与自动定位的位置不同
  const isDifferentFromAuto = !autoLocatedPosition.value || 
    Math.abs(selectedLng - parseFloat(autoLocatedPosition.value.lng)) > 0.0001 ||
    Math.abs(selectedLat - parseFloat(autoLocatedPosition.value.lat)) > 0.0001
  
  // 如果与自动定位的位置不同，移除自动定位的标记
  if (isDifferentFromAuto && autoLocatedPosition.value) {
    // 查找并移除自动定位的标记（如果存在且仍在标记列表中）
    const autoMarker = markers.value.find(m => {
      if (!m.isUserMarker) return false
      const markerLng = parseFloat(m.getPosition().lng)
      const markerLat = parseFloat(m.getPosition().lat)
      const autoLng = parseFloat(autoLocatedPosition.value.lng)
      const autoLat = parseFloat(autoLocatedPosition.value.lat)
      return Math.abs(markerLng - autoLng) < 0.0001 && 
             Math.abs(markerLat - autoLat) < 0.0001
    })
    
    if (autoMarker) {
      autoMarker.setMap(null)
      const index = markers.value.indexOf(autoMarker)
      if (index > -1) {
        markers.value.splice(index, 1)
      }
      console.log('已移除自动定位的标记')
    }
  }
  
  // 移除当前所有用户标记（包括手动选择的）
  const existingUserMarkers = markers.value.filter(m => m.isUserMarker)
  existingUserMarkers.forEach(marker => {
    marker.setMap(null)
    const index = markers.value.indexOf(marker)
    if (index > -1) {
      markers.value.splice(index, 1)
    }
  })
  
  // 添加新的用户位置标记（手动选择的）
  addUserMarker(selectedLng, selectedLat)
  
  // 更新用户位置
  userPosition.value = { lng: selectedLng, lat: selectedLat }
  
  // 关闭选择位置模式
  selectingPosition.value = false
  
  // 恢复地图容器鼠标样式
  const mapContainer = document.getElementById('map-container')
  if (mapContainer) {
    mapContainer.style.cursor = 'default'
  }
  
  // 获取最近垃圾桶
  try {
    await loadNearestDustbin(selectedLng, selectedLat)
    ElMessage.success('位置已设置')
  } catch (error) {
    console.error('获取最近垃圾桶失败:', error)
    ElMessage.success('位置已设置')
  }
}

// 全局错误处理（捕获高德地图内部错误）
const handleAMapError = (event) => {
  // 过滤掉 NaN 相关的错误，这些我们已经通过验证处理了
  const errorMessage = event.error?.message || event.message || ''
  if (errorMessage.includes('Invalid Object') && errorMessage.includes('NaN')) {
    // 阻止这些已知的错误显示在控制台
    event.preventDefault()
    console.warn('已拦截高德地图 NaN 坐标错误（已通过验证处理）')
    return false
  }
}

// 组件挂载
let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 60000) // 每分钟更新一次
  
  // 添加全局错误监听
  window.addEventListener('error', handleAMapError, true)
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason
    if (reason && typeof reason === 'object' && reason.message) {
      if (reason.message.includes('Invalid Object') && reason.message.includes('NaN')) {
        event.preventDefault()
        console.warn('已拦截高德地图 NaN 坐标 Promise 错误（已通过验证处理）')
        return false
      }
    }
  }, true)
  
  // 初始化地图
  initMap()
  
  // 延迟3秒后，如果还没有获取到用户位置，提示用户授予定位权限
  setTimeout(() => {
    if (!userPosition.value) {
      ElMessage({
        message: '💡 提示：为了获得更精准的导航，请在浏览器中允许定位权限',
        type: 'info',
        duration: 6000,
        showClose: true
      })
    }
  }, 3000)
})

// 组件卸载
onUnmounted(() => {
  // 移除全局错误监听
  window.removeEventListener('error', handleAMapError, true)
  
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (map.value) {
    try {
      map.value.destroy()
    } catch (error) {
      console.warn('销毁地图失败:', error)
    }
  }
  // 清除标记
  if (markers.value && markers.value.length > 0) {
    markers.value.forEach(marker => {
      try {
        if (marker && marker.setMap) {
          marker.setMap(null)
        }
      } catch (error) {
        console.warn('清除标记失败:', error)
      }
    })
    markers.value = []
  }
  // 清除信息窗口
  if (infoWindow.value) {
    try {
      infoWindow.value.close()
    } catch (error) {
      console.warn('关闭信息窗口失败:', error)
    }
    infoWindow.value = null
  }
  // 清除高德地图脚本
  const script = document.querySelector('script[src*="amap.com/maps"]')
  if (script) {
    script.remove()
  }
  // 清理全局变量（谨慎操作，因为可能被其他组件使用）
  // delete window.AMap
  // delete window.initAMap
})
</script>

<style lang="scss" scoped>
.guide-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.with-bottom-nav {
  padding-bottom: 72px;
}

// 状态栏样式
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

// 导航栏样式（浅蓝色）
.nav-bar {
  background: #87CEEB; // 浅蓝色
  backdrop-filter: blur(10px);
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 100%;
    margin: 0 auto;
    position: relative;
    
    .back-button {
      background: rgba(255, 255, 255, 0.3);
      border: none;
      color: white;
      width: 40px;
      height: 40px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.4);
      }
    }
    
    .nav-title {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      font-size: 18px;
      font-weight: 600;
      color: white;
      margin: 0;
      text-align: center;
      pointer-events: none;
    }
    
    .nav-buttons {
      display: flex;
      flex-direction: row;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
      
      .select-position-button,
      .location-button {
        width: 32px;
        height: 32px;
        min-width: 32px;
        padding: 0;
        background: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.4) !important;
          transform: scale(1.1);
        }
        
        &:active {
          transform: scale(0.95);
        }
        
        :deep(.el-icon) {
          font-size: 16px;
          color: white;
        }
        
        // 覆盖Element Plus的默认样式
        :deep(.el-button__inner) {
          color: white;
        }
      }
      
      .select-position-button {
        // 选择模式下的样式
        &.is-success {
          background: rgba(103, 194, 58, 0.7) !important;
          border-color: rgba(103, 194, 58, 0.9) !important;
          
          &:hover {
            background: rgba(103, 194, 58, 0.8) !important;
          }
        }
      }
    }
  }
}

// 地图容器
.map-container {
  flex: 1;
  width: 100%;
  position: relative;
  overflow: hidden;
  
  // 经纬度显示（地图右上角）
  .map-coordinates {
    position: absolute;
    top: 10px;
    right: 10px;
    color: black;
    font-size: 12px;
    font-weight: 500;
    font-family: 'Courier New', monospace;
    z-index: 100;
    white-space: nowrap;
    user-select: none;
  }

  .map-error-panel {
    position: absolute;
    inset: 12px;
    z-index: 120;
    background: rgba(255, 255, 255, 0.96);
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .map-error-title {
    font-size: 16px;
    font-weight: 700;
    color: #d32f2f;
  }

  .map-error-text {
    font-size: 13px;
    color: #555;
    line-height: 1.5;
    word-break: break-word;
  }

  .map-fallback-image {
    width: 100%;
    height: auto;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    object-fit: cover;
  }
}

// 最近垃圾桶信息卡片（可展开/收起）
.nearest-info-card {
  position: absolute;
  // 底部有导航栏时，整体上移，避免“开始导航”按钮被遮挡
  bottom: 96px;
  left: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  z-index: 100;
  max-width: 400px;
  margin: 0 auto;
  transition: all 0.3s ease;
  overflow: hidden;

  .info-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    cursor: pointer;
    user-select: none;
    transition: border-bottom 0.3s ease;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .info-icon {
      font-size: 20px;
      color: #4CAF50;
    }
    
    .info-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
    
    .expand-icon {
      font-size: 18px;
      color: #666;
      transition: transform 0.3s ease;
      
      &.expanded {
        transform: rotate(180deg);
      }
    }
    
    &:hover {
      background: rgba(0, 0, 0, 0.02);
    }
  }
  
  // 展开时显示底部边框
  &.expanded .info-header {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }
  
  .info-content {
    padding: 16px;
    
    .info-name {
      font-size: 15px;
      font-weight: 600;
      color: #333;
      margin-bottom: 6px;
    }

    .info-description {
      font-size: 13px;
      color: #666;
      margin-bottom: 12px;
      line-height: 1.4;
    }
    
    // 近距离提示样式（<10米）
    .nearby-alert {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
      
      .nearby-icon {
        font-size: 32px;
        line-height: 1;
        flex-shrink: 0;
      }
      
      .nearby-text {
        flex: 1;
        color: white;
        
        .nearby-title {
          font-size: 16px;
          font-weight: 700;
          margin-bottom: 6px;
          letter-spacing: 0.5px;
        }
        
        .nearby-distance {
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 4px;
          opacity: 0.95;
        }
        
        .nearby-tip {
          font-size: 13px;
          opacity: 0.9;
          font-weight: 500;
        }
      }
    }

    .info-distance {
      font-size: 13px;
      color: #666;
      margin-bottom: 8px;
      
      .distance-label {
        color: #999;
      }
      
      .distance-value {
        color: #4CAF50;
        font-weight: 600;
      }
    }

    .info-duration {
      font-size: 13px;
      color: #666;
      margin-bottom: 8px;
      
      .duration-label {
        color: #999;
      }
      
      .duration-value {
        color: #2196F3;
        font-weight: 600;
      }
    }

    .info-message {
      font-size: 12px;
      color: #666;
      line-height: 1.5;
      margin-bottom: 16px;
    }

    .info-buttons {
      display: flex;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid rgba(0, 0, 0, 0.06);
      
      .nav-button {
        flex: 1;
        height: 44px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        border: none;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        color: #fff;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        
        &:hover {
          background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
          box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
          transform: translateY(-2px);
        }
        
        &:active {
          transform: translateY(0);
          box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        }
        
        .el-icon {
          font-size: 18px;
        }
        
        span {
          font-size: 15px;
          font-weight: 600;
        }
      }

      &.secondary-actions {
        margin-top: 10px;
        padding-top: 0;
        border-top: none;
      }

      .reset-nearest-button {
        width: 100%;
        height: 40px;
        border-radius: 8px;
        border: 1px solid rgba(76, 175, 80, 0.28);
        color: #2e7d32;
        background: rgba(76, 175, 80, 0.08);
        font-weight: 600;
      }
    }
  }
}

// 加载提示
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  
  .loading-icon {
    font-size: 32px;
    color: #4CAF50;
    margin-bottom: 12px;
  }
  
  .loading-text {
    font-size: 14px;
    color: #666;
  }
}

// 自定义信息窗口样式（全局样式，需要在style标签中定义）
</style>

<style>
/* 自定义信息窗口样式 - 固定大小，美观可见 */
.custom-info-window {
  width: 140px;
  min-height: 36px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
  text-align: center;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.info-window-title {
  font-size: 12px;
  font-weight: 500;
  color: #333;
  word-break: break-all;
  line-height: 1.4;
  margin: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.info-window-desc {
  font-size: 10px;
  color: #666;
  line-height: 1.3;
  margin-top: 4px;
  word-break: break-all;
}

/* 自定义消息提示样式 */
.select-position-message {
  font-size: 14px;
  font-weight: 500;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
