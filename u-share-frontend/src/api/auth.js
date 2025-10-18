import request from './request'

// 用户登录
export const login = (data) => {
  return request({
    url: '/token',
    method: 'post',
    data: new URLSearchParams(data),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 用户注册
export const register = (data) => {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}

// 获取用户信息
export const getUserInfo = () => {
  return request({
    url: '/users/me/',
    method: 'get'
  })
}

