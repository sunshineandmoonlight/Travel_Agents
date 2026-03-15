/**
 * 认证相关API
 */
import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

// ============================================================
// 类型定义
// ============================================================

export interface UserRegisterRequest {
  email: string
  username: string
  password: string
  phone?: string
}

export interface UserLoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserInfo {
  id: string
  email: string
  username: string
  phone?: string
  avatar?: string
  bio?: string
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  success: boolean
  message: string
  data?: T
}

export interface UpdateUserRequest {
  email?: string
  phone?: string
  bio?: string
  avatar?: string
}

// ============================================================
// API 函数
// ============================================================

/**
 * 用户注册
 */
export const register = (data: UserRegisterRequest): Promise<AxiosResponse<ApiResponse<UserInfo>>> => {
  return request.post('/travel/auth/register', data)
}

/**
 * 用户登录
 */
export const login = (data: UserLoginRequest): Promise<AxiosResponse<ApiResponse<TokenResponse>>> => {
  return request.post('/travel/auth/login', data)
}

/**
 * 刷新令牌
 */
export const refreshToken = (refreshToken: string): Promise<AxiosResponse<ApiResponse<TokenResponse>>> => {
  return request.post('/travel/auth/refresh', null, {
    params: { refresh_token: refreshToken }
  })
}

/**
 * 用户登出
 */
export const logout = (refreshToken: string): Promise<AxiosResponse<ApiResponse<null>>> => {
  return request.post('/travel/auth/logout', null, {
    params: { refresh_token: refreshToken }
  })
}

/**
 * 获取当前用户信息
 */
export const getUserInfo = (): Promise<AxiosResponse<ApiResponse<UserInfo>>> => {
  return request.get('/travel/auth/me')
}

/**
 * 更新用户信息
 */
export const updateUserInfo = (data: UpdateUserRequest): Promise<AxiosResponse<ApiResponse<UserInfo>>> => {
  return request.put('/travel/auth/me', data)
}

/**
 * 修改密码
 */
export const changePassword = (oldPassword: string, newPassword: string): Promise<AxiosResponse<ApiResponse<null>>> => {
  return request.post('/travel/auth/change-password', null, {
    params: { old_password: oldPassword, new_password: newPassword }
  })
}

/**
 * 删除账户
 */
export const deleteAccount = (): Promise<AxiosResponse<ApiResponse<null>>> => {
  return request.delete('/travel/auth/me')
}
