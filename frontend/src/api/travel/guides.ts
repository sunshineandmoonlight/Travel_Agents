/**
 * 旅行攻略API服务
 * 用于攻略保存到攻略中心和导出PDF
 */

import axios from 'axios'
import md5 from 'crypto-js/md5'

const API_BASE = '/api/guides-center'
const IMAGES_API_BASE = '/api/travel/images'

/**
 * 城市英文名称映射
 */
const CITY_NAME_MAP: Record<string, string> = {
  // 中国城市
  "北京": "beijing", "上海": "shanghai", "广州": "guangzhou", "深圳": "shenzhen",
  "成都": "chengdu", "重庆": "chongqing", "西安": "xian", "杭州": "hangzhou",
  "南京": "nanjing", "苏州": "suzhou", "武汉": "wuhan", "厦门": "xiamen",
  "青岛": "qingdao", "大连": "dalian", "桂林": "guilin", "丽江": "lijiang",
  "大理": "dali", "三亚": "sanya", "拉萨": "lhasa", "香港": "hong+kong",
  "乌鲁木齐": "urumqi", "哈尔滨": "harbin", "台北": "taipei",
  // 东南亚
  "曼谷": "bangkok", "清迈": "chiang+mai", "普吉岛": "phuket", "芭提雅": "pattaya",
  "新加坡": "singapore", "吉隆坡": "kuala+lumpur", "槟城": "penang",
  "巴厘岛": "bali", "河内": "hanoi", "胡志明市": "ho+chi+minh", "岘港": "da+nang",
  // 日本韩国
  "东京": "tokyo", "京都": "kyoto", "大阪": "osaka", "奈良": "nara",
  "首尔": "seoul", "釜山": "busan", "济州岛": "jeju", "富士山": "mount+fuji",
  "冲绳": "okinawa",
  // 欧洲
  "巴黎": "paris", "伦敦": "london", "罗马": "rome", "威尼斯": "venice",
  "巴塞罗那": "barcelona", "阿姆斯特丹": "amsterdam", "雅典": "athens",
  "圣托里尼": "santorini", "布拉格": "prague", "维也纳": "vienna",
  // 美国美洲
  "纽约": "new+york", "洛杉矶": "los+angeles", "旧金山": "san+francisco",
  "拉斯维加斯": "las+vegas", "芝加哥": "chicago", "迈阿密": "miami",
  "多伦多": "toronto", "温哥华": "vancouver", "里约": "rio",
  // 澳大利亚新西兰
  "悉尼": "sydney", "墨尔本": "melbourne", "奥克兰": "auckland", "皇后镇": "queenstown",
  // 中东
  "迪拜": "dubai", "阿布扎比": "abu+dhabi", "伊斯坦布尔": "istanbul",
  // 其他
  "开罗": "cairo", "开普敦": "cape+town", "孟买": "mumbai", "德里": "new+delhi"
}

/**
 * 获取城市的英文名称（用于图片搜索）
 */
function getCityEnglishName(city: string): string {
  return CITY_NAME_MAP[city] || city.toLowerCase().replace(/\s+/g, '+').replace(/-/g, '+')
}

/**
 * 生成一致的种子（相同城市总是返回相同图片）
 */
function generateSeed(destination: string): string {
  const normalized = destination.toLowerCase().replace(/\s+/g, '').replace(/-/g, '')
  return md5(normalized).toString().substring(0, 10)
}

/**
 * 生成高质量的Unsplash图片URL
 *
 * ⚠️ 注意：此函数已废弃，source.unsplash.com API已不再维护
 * 请使用 getGuideImageUrlAsync 来获取从后端API的图片
 *
 * Unsplash提供高质量的真实景区照片
 * @deprecated 使用 getGuideImageUrlAsync 代替
 */
function getUnsplashUrl(destination: string, width: number, height: number): string {
  const cityEn = getCityEnglishName(destination)
  const keywords = `${cityEn},landmark,scenic,travel`

  // 使用Unsplash Source API - 无需API key，有速率限制但质量高
  // 签名：在 unsplash.com 注册应用获得
  const signature = 'f5518d8e9c1a4e6b2c8d4e6f8a0b2c4d6e8f0a2'
  return `https://source.unsplash.com/${width}x${height}/?${keywords}&sig=${signature}`
}

/**
 * 从后端API获取图片URL（异步）
 *
 * 通过后端API调用Unsplash/Pexels，使用真实的API key
 * 能获得更准确的搜索结果
 */
async function getImageUrlFromBackend(destination: string, width: number, height: number): Promise<string> {
  try {
    const response = await axios.get(`${IMAGES_API_BASE}/destination/${encodeURIComponent(destination)}`, {
      params: { width, height }
    })
    return response.data.url
  } catch (error) {
    console.warn(`[图片] 后端API获取失败，使用占位图: ${destination}`, error)
    // 如果后端API失败，使用占位图
    return `https://placehold.co/${width}x${height}?text=${encodeURIComponent(destination)}`
  }
}

/**
 * 获取攻略封面图片URL（通过后端API）
 *
 * 使用后端API获取图片，支持Unsplash和Pexels
 * 能获得更准确的搜索结果
 *
 * @param destination 目的地名称
 * @param width 图片宽度
 * @param height 图片高度
 * @returns 图片URL
 */
export function getGuideImageUrl(destination: string, width: number = 600, height: number = 400): string {
  // 同步版本：使用占位图或缓存的URL
  // 实际使用时建议使用 getGuideImageUrlAsync
  return `https://placehold.co/${width}x${height}?text=${encodeURIComponent(destination)}`
}

/**
 * 异步获取攻略封面图片URL（推荐使用）
 *
 * 通过后端API获取图片，支持Unsplash和Pexels
 *
 * @param destination 目的地名称
 * @param width 图片宽度
 * @param height 图片高度
 * @returns Promise<string> 图片URL
 */
export async function getGuideImageUrlAsync(destination: string, width: number = 600, height: number = 400): Promise<string> {
  return getImageUrlFromBackend(destination, width, height)
}

/**
 * 获取渐进式图片URL数组（按优先级排序）
 *
 * 返回URL用于渐进式加载：
 * 1. Unsplash (最高质量，立即可用)
 * 2. Pexels (需要通过后端API获取，使用占位符标记)
 *
 * 注意：Pexels URL需要异步获取，这里返回一个特殊标记
 * 在Home.vue中会异步获取真实的Pexels URL
 *
 * @param destination 目的地名称
 * @param width 图片宽度
 * @param height 图片高度
 * @returns 图片URL数组
 */
export function getProgressiveImageUrls(destination: string, width: number = 600, height: number = 400): string[] {
  return [
    getUnsplashUrl(destination, width, height),  // 优先：Unsplash高质量（立即可用）
    '__PEXELS_API__'  // 标记：需要通过后端API获取Pexels图片
  ]
}

/**
 * 获取默认图片URL（最后的保底选项）
 * @param destination 目的地名称（可选）
 * @param width 图片宽度
 * @param height 图片高度
 */
export function getDefaultImageUrl(destination: string = '', width: number = 600, height: number = 400): string {
  // 使用Unsplash的固定高质量旅游照片
  const defaultImages = [
    'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop', // 旅行
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop', // 风景
    'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&h=600&fit=crop', // 自然
  ]
  const index = destination
    ? Math.abs(md5(destination).toNumber()) % defaultImages.length
    : 0
  return defaultImages[index]
}

export interface SaveGuideRequest {
  user_id: string
  title: string
  destination: string
  total_days: number
  guide_data: any
  budget: number
  tags?: string[]
  is_public?: boolean
}

export interface GuideListItem {
  id: string
  title: string
  destination: string
  total_days: number
  budget: number
  tags: string[]
  status: 'draft' | 'published' | 'archived'
  created_at: string
  updated_at: string
  thumbnail_url?: string
}

export interface GuideDetail {
  id: string
  user_id: string
  title: string
  destination: string
  total_days: number
  budget: number
  tags: string[]
  status: 'draft' | 'published' | 'archived'
  is_public: boolean
  guide_data: any
  thumbnail_url?: string
  view_count: number
  like_count: number
  created_at: string
  updated_at: string
}

/**
 * 保存攻略到攻略中心
 */
export async function saveGuide(request: SaveGuideRequest): Promise<{ success: boolean; guide_id: string; message: string }> {
  const response = await axios.post(`${API_BASE}/save`, request)
  return response.data
}

/**
 * 获取用户的攻略列表
 */
export async function getUserGuides(
  userId: string,
  status?: 'draft' | 'published' | 'archived',
  limit: number = 20,
  offset: number = 0
): Promise<GuideListItem[]> {
  const params: any = {
    user_id: userId,
    limit,
    offset
  }
  if (status) {
    params.status = status
  }

  const response = await axios.get<GuideListItem[]>(`${API_BASE}/list`, { params })
  return response.data
}

/**
 * 获取公开的攻略列表（攻略中心）
 */
export async function getPublicGuides(
  destination?: string,
  limit: number = 20,
  offset: number = 0
): Promise<GuideListItem[]> {
  const params: any = {
    limit,
    offset
  }
  if (destination) {
    params.destination = destination
  }

  const response = await axios.get<GuideListItem[]>(`${API_BASE}/public`, { params })
  return response.data
}

/**
 * 获取攻略详情
 */
export async function getGuideDetail(guideId: string): Promise<GuideDetail> {
  const response = await axios.get<GuideDetail>(`${API_BASE}/guide/${guideId}`)
  return response.data
}

/**
 * 导出攻略为PDF
 */
export async function exportGuidePDF(guideId: string): Promise<Blob> {
  const response = await axios.get(`${API_BASE}/guide/${guideId}/export/pdf`, {
    responseType: 'blob'
  })
  return response.data
}

/**
 * 下载PDF文件
 */
export async function downloadGuidePDF(guideId: string, filename?: string) {
  try {
    const blob = await exportGuidePDF(guideId)

    // 从响应头获取文件名，如果没有则使用默认
    const contentDisposition = blob.type || 'application/pdf'
    const defaultFilename = filename || `travel_guide_${guideId}.pdf`

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = defaultFilename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return true
  } catch (error) {
    console.error('下载PDF失败:', error)
    throw error
  }
}

/**
 * 更新攻略
 */
export async function updateGuide(request: {
  guide_id: string
  title?: string
  guide_data?: any
  tags?: string[]
  is_public?: boolean
  status?: 'draft' | 'published' | 'archived'
}): Promise<{ success: boolean; message: string }> {
  const response = await axios.put(`${API_BASE}/update`, request)
  return response.data
}

/**
 * 删除攻略
 */
export async function deleteGuide(guideId: string, userId: string): Promise<{ success: boolean; message: string }> {
  const response = await axios.delete(`${API_BASE}/guide/${guideId}`, {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * 点赞攻略
 */
export async function likeGuide(guideId: string): Promise<{ success: boolean; like_count: number }> {
  const response = await axios.post(`${API_BASE}/guide/${guideId}/like`)
  return response.data
}

/**
 * 获取热门目的地列表
 */
export async function getPopularDestinations(): Promise<string[]> {
  const response = await axios.get<string[]>(`${API_BASE}/destinations`)
  return response.data
}

export default {
  saveGuide,
  getUserGuides,
  getPublicGuides,
  getGuideDetail,
  exportGuidePDF,
  downloadGuidePDF,
  deleteGuide,
  likeGuide,
  getPopularDestinations,
  getGuideImageUrl,
  getGuideImageUrlAsync,
  getProgressiveImageUrls,
  getDefaultImageUrl
}
