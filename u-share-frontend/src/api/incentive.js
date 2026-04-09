import request from './request'

export const getMallItems = () => {
  return request({
    url: '/mall/items',
    method: 'get'
  })
}

export const getVolunteerOverview = () => {
  return request({
    url: '/points/volunteer-overview',
    method: 'get'
  })
}

export const convertToVolunteerHours = (pointsToConvert = 50) => {
  return request({
    url: '/points/convert-to-hours',
    method: 'post',
    data: {
      points_to_convert: pointsToConvert
    }
  })
}

export const getLeaderboard = (boardType = 'personal') => {
  return request({
    url: '/leaderboard',
    method: 'get',
    params: {
      board_type: boardType
    }
  })
}
