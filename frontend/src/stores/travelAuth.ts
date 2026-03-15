/**
 * 旅行系统认证状态管理
 * 独立于原有的股票系统认证
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { travelAuthApi } from '@/api/travel'
import type { UserInfo } from '@/api/auth'

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'travel_access_token',
  USER_INFO: 'travel_user_info'
}

export const useTravelAuthStore = defineStore('travelAuth', () => {
  // ============================================================
  // 状态
  // ============================================================

  const accessToken = ref<string | null>(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN))
  const userInfo = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem(STORAGE_KEYS.USER_INFO) || 'null')
  )
  const loading = ref(false)

  // ============================================================
  // 计算属性
  // ============================================================

  const isAuthenticated = computed(() => !!accessToken.value && !!userInfo.value)
  const userDisplayName = computed(() => userInfo.value?.username || '游客')
  const userAvatar = computed(() => userInfo.value?.avatar || '/default-avatar.png')

  // ============================================================
  // 方法
  // ============================================================

  /**
   * 设置令牌
   */
  const setToken = (access: string) => {
    accessToken.value = access
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access)
  }

  /**
   * 设置用户信息
   */
  const setUserInfo = (user: UserInfo) => {
    userInfo.value = user
    localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(user))
  }

  /**
   * 清除所有认证信息
   */
  const clearAuth = () => {
    accessToken.value = null
    userInfo.value = null
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_INFO)
  }

  /**
   * 用户注册
   */
  const register = async (data: { username: string; email: string; password: string; phone?: string }) => {
    loading.value = true
    try {
      const response = await travelAuthApi.register(data)
      // 后端返回 UserWithToken 格式: { access_token, token_type, ...userFields }
      if (response.data && response.data.access_token) {
        // 注册成功，保存 token
        setToken(response.data.access_token)

        // 设置用户信息
        const user: UserInfo = {
          id: String(response.data.id),
          username: response.data.username,
          email: response.data.email,
          avatar: response.data.avatar_url || '',
          is_active: response.data.is_active,
          is_verified: response.data.is_verified,
          is_admin: false,
          created_at: response.data.created_at,
          updated_at: response.data.created_at,
          preferences: {
            default_market: 'A股',
            default_depth: '3',
            ui_theme: 'auto',
            language: 'zh-CN',
            notifications_enabled: true,
            email_notifications: false
          },
          daily_quota: 100,
          concurrent_limit: 3,
          total_analyses: 0,
          successful_analyses: 0,
          failed_analyses: 0
        }
        setUserInfo(user)

        return { success: true, message: '注册成功' }
      }
      return { success: false, message: '注册失败' }
    } catch (error: any) {
      const message = error.response?.data?.detail || '注册失败，请稍后重试'
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登录
   */
  const loginAction = async (data: { username: string; password: string }) => {
    loading.value = true
    try {
      const response = await travelAuthApi.login(data.username, data.password)
      // 后端返回 Token 格式: { access_token, token_type, user }
      if (response.data && response.data.access_token) {
        setToken(response.data.access_token)

        // 设置用户信息
        const userResponse = response.data.user
        if (userResponse) {
          const user: UserInfo = {
            id: String(userResponse.id),
            username: userResponse.username,
            email: userResponse.email,
            avatar: userResponse.avatar_url || '',
            is_active: userResponse.is_active,
            is_verified: userResponse.is_verified,
            is_admin: false,
            created_at: userResponse.created_at,
            updated_at: userResponse.created_at,
            preferences: {
              default_market: 'A股',
              default_depth: '3',
              ui_theme: 'auto',
              language: 'zh-CN',
              notifications_enabled: true,
              email_notifications: false
            },
            daily_quota: 100,
            concurrent_limit: 3,
            total_analyses: 0,
            successful_analyses: 0,
            failed_analyses: 0
          }
          setUserInfo(user)
        }

        return { success: true, message: '登录成功' }
      }
      return { success: false, message: '登录失败' }
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取用户信息
   */
  const fetchUserInfoAction = async () => {
    if (!accessToken.value) {
      return false
    }

    try {
      const response = await travelAuthApi.getCurrentUser()
      if (response.data) {
        const user: UserInfo = {
          id: String(response.data.id),
          username: response.data.username,
          email: response.data.email,
          avatar: response.data.avatar_url || '',
          is_active: response.data.is_active,
          is_verified: response.data.is_verified,
          is_admin: false,
          created_at: response.data.created_at,
          updated_at: response.data.created_at,
          preferences: {
            default_market: 'A股',
            default_depth: '3',
            ui_theme: 'auto',
            language: 'zh-CN',
            notifications_enabled: true,
            email_notifications: false
          },
          daily_quota: 100,
          concurrent_limit: 3,
          total_analyses: 0,
          successful_analyses: 0,
          failed_analyses: 0
        }
        setUserInfo(user)
        return true
      }
      return false
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return false
    }
  }

  /**
   * 用户登出
   */
  const logout = async () => {
    clearAuth()
  }

  /**
   * 更新用户信息
   */
  const updateUserInfoAction = async (data: Partial<UserInfo>) => {
    if (!accessToken.value) {
      return { success: false, message: '请先登录' }
    }

    loading.value = true
    try {
      const response = await travelAuthApi.updateProfile(data)
      if (response.data) {
        const user: UserInfo = {
          id: String(response.data.id),
          username: response.data.username,
          email: response.data.email,
          avatar: response.data.avatar_url || '',
          is_active: response.data.is_active,
          is_verified: response.data.is_verified,
          is_admin: false,
          created_at: response.data.created_at,
          updated_at: response.data.created_at,
          preferences: userInfo.value?.preferences || {
            default_market: 'A股',
            default_depth: '3',
            ui_theme: 'auto',
            language: 'zh-CN',
            notifications_enabled: true,
            email_notifications: false
          },
          daily_quota: 100,
          concurrent_limit: 3,
          total_analyses: 0,
          successful_analyses: 0,
          failed_analyses: 0
        }
        setUserInfo(user)
        return { success: true, message: '更新成功' }
      }
      return { success: false, message: '更新失败' }
    } catch (error: any) {
      const message = error.response?.data?.detail || '更新失败，请稍后重试'
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  /**
   * 初始化：检查本地存储的令牌
   */
  const initialize = async () => {
    const storedToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (storedToken) {
      accessToken.value = storedToken
      await fetchUserInfoAction()
    }
  }

  return {
    // 状态
    accessToken,
    userInfo,
    loading,

    // 计算属性
    isAuthenticated,
    userDisplayName,
    userAvatar,

    // 方法
    setToken,
    setUserInfo,
    clearAuth,
    register,
    loginAction,
    fetchUserInfoAction,
    logout,
    updateUserInfoAction,
    initialize
  }
})
