/**
 * 旅行系统 API 客户端
 * 连接到独立的旅行系统后端 (端口 8004)
 */

import axios from 'axios'

const TRAVEL_API_BASE = 'http://localhost:8006/api/travel'

// Token 存储键名（与 travelAuth store 保持一致）
const TRAVEL_TOKEN_KEY = 'travel_access_token'

// 创建旅行系统专用的 axios 实例
const travelApi = axios.create({
  baseURL: TRAVEL_API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 token
travelApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TRAVEL_TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误和保存 token
travelApi.interceptors.response.use(
  (response) => {
    // 登录/注册成功后自动保存 token
    const data = response.data
    if (data && data.access_token) {
      localStorage.setItem(TRAVEL_TOKEN_KEY, data.access_token)
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，清除并跳转登录
      localStorage.removeItem(TRAVEL_TOKEN_KEY)
      localStorage.removeItem('travel_user_info')
      // 只在旅行系统页面时跳转
      if (window.location.pathname.startsWith('/travel')) {
        window.location.href = '/travel/login'
      }
    }
    return Promise.reject(error)
  }
)

// ==================== 认证 API ====================

export const travelAuthApi = {
  // 用户注册
  register: (data: { username: string; email: string; password: string; full_name?: string; phone?: string }) =>
    travelApi.post('/auth/register', data),

  // 用户登录 - 使用 FormData 格式 (OAuth2PasswordRequestForm)
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return travelApi.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取当前用户信息
  getCurrentUser: () =>
    travelApi.get('/auth/me'),

  // 更新用户信息
  updateProfile: (data: any) =>
    travelApi.put('/auth/me', data),

  // 修改密码
  changePassword: (oldPassword: string, newPassword: string) =>
    travelApi.post('/auth/change-password', null, {
      params: { old_password: oldPassword, new_password: newPassword }
    })
}

// ==================== AI 旅行规划 API ====================

export const travelPlanningApi = {
  // AI 对话接口
  chat: (message: string, sessionId?: string) =>
    travelApi.post('/plans/ai/chat', { message, session_id: sessionId }),

  // 收集旅行需求
  collectInfo: (userInput: string) =>
    travelApi.post('/plans/ai/collect-info', { user_input: userInput }),

  // 生成旅行方案
  generatePlans: (requirements: any) =>
    travelApi.post('/plans/ai/generate-plans', requirements),

  // 生成详细攻略
  generateGuide: (selectedPlan: any, requirements: any) =>
    travelApi.post('/plans/ai/generate-guide', { selected_plan: selectedPlan, requirements }),

  // 保存 AI 生成的计划
  savePlan: (planData: any) =>
    travelApi.post('/plans/ai/save-plan', planData)
}

// ==================== 旅行计划 API ====================

export const travelPlansApi = {
  // 获取计划列表
  getPlans: (params?: { page?: number; page_size?: number; status?: string }) =>
    travelApi.get('/plans', { params }),

  // 获取计划详情
  getPlan: (planId: number) =>
    travelApi.get(`/plans/${planId}`),

  // 创建计划
  createPlan: (data: any) =>
    travelApi.post('/plans', data),

  // 更新计划
  updatePlan: (planId: number, data: any) =>
    travelApi.put(`/plans/${planId}`, data),

  // 删除计划
  deletePlan: (planId: number) =>
    travelApi.delete(`/plans/${planId}`),

  // 点赞计划
  likePlan: (planId: number) =>
    travelApi.post(`/plans/${planId}/like`)
}

// ==================== 目的地情报 API ====================

export const travelIntelligenceApi = {
  // 获取目的地列表
  getDestinations: (params?: { page?: number; page_size?: number; country?: string; category?: string; search?: string }) =>
    travelApi.get('/intelligence/destinations', { params }),

  // 获取目的地详情
  getDestination: (destinationId: number) =>
    travelApi.get(`/intelligence/destinations/${destinationId}`),

  // 获取目的地天气
  getWeather: (destinationId: number) =>
    travelApi.get(`/intelligence/destinations/${destinationId}/weather`),

  // 获取目的地新闻
  getNews: (destinationId: number) =>
    travelApi.get(`/intelligence/destinations/${destinationId}/news`),

  // 搜索地点
  searchPlaces: (keyword: string, city?: string) =>
    travelApi.get('/intelligence/search/places', { params: { keyword, city } }),

  // 刷新目的地情报
  refreshIntelligence: (destinationId: number) =>
    travelApi.post(`/intelligence/destinations/${destinationId}/refresh`),

  // 获取热门目的地
  getHotDestinations: (limit?: number) =>
    travelApi.get('/intelligence/hot', { params: { limit } })
}

// ==================== 导出 ====================

export default travelApi
