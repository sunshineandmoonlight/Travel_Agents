/**
 * 天行数据旅游景区API
 * 提供真实景点数据
 */

import axios from 'axios'

const API_BASE = '/api/travel/tianapi'

/**
 * 景点数据接口
 */
export interface ScenicAttraction {
  name: string
  description: string
  province: string
  city: string
  sub_attractions: string[]
  source: string
}

/**
 * 获取景点列表响应
 */
export interface AttractionsResponse {
  code: number
  msg: string
  data: ScenicAttraction[]
  total: number
}

/**
 * 获取热门景点响应
 */
export interface PopularAttractionsResponse {
  code: number
  msg: string
  data: ScenicAttraction[]
  total: number
  cached: boolean
}

/**
 * 验证景点名称响应
 */
export interface ValidateAttractionsResponse {
  code: number
  msg: string
  data: {
    valid: string[]
    invalid: string[]
    details: Record<string, ScenicAttraction>
  }
}

/**
 * 获取景点列表
 *
 * @param city 城市名称（如"苏州"、"杭州"）
 * @param options 查询选项
 * @returns 景点列表
 */
export async function getAttractions(
  city: string,
  options: {
    province?: string
    keyword?: string
    page?: number
    num?: number
  } = {}
): Promise<AttractionsResponse> {
  const params = new URLSearchParams()
  params.append('city', city)

  if (options.province) params.append('province', options.province)
  if (options.keyword) params.append('keyword', options.keyword)
  if (options.page) params.append('page', options.page.toString())
  if (options.num) params.append('num', options.num.toString())

  const response = await axios.get<AttractionsResponse>(
    `${API_BASE}/attractions?${params.toString()}`
  )
  return response.data
}

/**
 * 搜索景点（全国范围）
 *
 * @param keyword 搜索关键词
 * @param page 页码
 * @param num 每页数量
 * @returns 景点列表
 */
export async function searchAttractions(
  keyword: string,
  page = 1,
  num = 20
): Promise<AttractionsResponse> {
  const response = await axios.get<AttractionsResponse>(
    `${API_BASE}/attractions/search`,
    {
      params: { keyword, page, num }
    }
  )
  return response.data
}

/**
 * 获取省份所有景点
 *
 * @param province 省份名称
 * @param page 页码
 * @param num 每页数量
 * @returns 景点列表
 */
export async function getAttractionsByProvince(
  province: string,
  page = 1,
  num = 50
): Promise<AttractionsResponse> {
  const response = await axios.get<AttractionsResponse>(
    `${API_BASE}/attractions/province/${encodeURIComponent(province)}`,
    {
      params: { page, num }
    }
  )
  return response.data
}

/**
 * 获取热门城市景点（带缓存）
 *
 * @param city 城市名称
 * @param limit 返回数量
 * @returns 景点列表
 */
export async function getPopularAttractions(
  city: string,
  limit = 20
): Promise<PopularAttractionsResponse> {
  const response = await axios.get<PopularAttractionsResponse>(
    `${API_BASE}/attractions/popular/${encodeURIComponent(city)}`,
    {
      params: { limit }
    }
  )
  return response.data
}

/**
 * 验证景点名称
 *
 * 检查给定的景点名称是否存在于天行数据中
 *
 * @param attractionNames 景点名称列表
 * @param city 城市名称
 * @returns 验证结果
 */
export async function validateAttractionNames(
  attractionNames: string[],
  city: string
): Promise<ValidateAttractionsResponse> {
  const response = await axios.post<ValidateAttractionsResponse>(
    `${API_BASE}/attractions/validate`,
    {
      attraction_names: attractionNames,
      city
    }
  )
  return response.data
}

/**
 * 获取景点建议（用于自动完成）
 *
 * @param keyword 搜索关键词
 * @param city 城市名称（可选）
 * @returns 景点名称列表
 */
export async function getAttractionSuggestions(
  keyword: string,
  city?: string
): Promise<string[]> {
  try {
    const params: any = { keyword }
    if (city) params.city = city

    const response = await axios.get<AttractionsResponse>(
      `${API_BASE}/attractions`,
      { params }
    )

    // 只返回景点名称
    return response.data.data.map(attr => attr.name)
  } catch (error) {
    console.error('获取景点建议失败:', error)
    return []
  }
}

/**
 * 根据城市获取所有景点名称（用于选择器）
 *
 * @param city 城市名称
 * @returns 景点名称列表
 */
export async function getCityAttractionNames(city: string): Promise<string[]> {
  try {
    const response = await axios.get<AttractionsResponse>(
      `${API_BASE}/attractions`,
      {
        params: { city, num: 100 } // 获取更多结果
      }
    )

    return response.data.data.map(attr => attr.name)
  } catch (error) {
    console.error('获取城市景点名称失败:', error)
    return []
  }
}

export default {
  getAttractions,
  searchAttractions,
  getAttractionsByProvince,
  getPopularAttractions,
  validateAttractionNames,
  getAttractionSuggestions,
  getCityAttractionNames
}
