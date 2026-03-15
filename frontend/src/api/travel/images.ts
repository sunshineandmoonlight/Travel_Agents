/**
 * 旅行图片API服务
 */

import axios from 'axios'

const API_BASE = '/api/travel/images'  // 匹配后端实际路径结构

export interface AttractionImageRequest {
  attraction_name: string
  city: string
  width?: number
  height?: number
}

export interface AttractionImageResponse {
  url: string
  source: 'unsplash' | 'pexels' | 'public' | 'placeholder' | 'unknown'
  attraction_name: string
  city: string
  width: number
  height: number
}

export interface DestinationImageResponse {
  url: string
  source: string
  city: string
  width: number
  height: number
}

export interface BatchImageRequest {
  attractions: Array<{ name: string; city: string }>
}

export interface BatchImageResponse {
  images: Record<string, { url: string; source: string; city: string }>
}

export interface ImageServiceStatus {
  status: string
  services: {
    unsplash?: { configured: boolean; working: boolean }
    pexels?: { configured: boolean; working: boolean }
    bing_search?: { configured: boolean; working: boolean }
    public_search?: { configured: boolean; working: boolean }
  }
}

/**
 * 获取景点图片URL
 */
export async function getAttractionImage(params: AttractionImageRequest): Promise<AttractionImageResponse> {
  const response = await axios.get<AttractionImageResponse>(`${API_BASE}/attraction`, { params })
  return response.data
}

/**
 * 获取景点图片URL (POST方式)
 */
export async function getAttractionImagePost(request: AttractionImageRequest): Promise<AttractionImageResponse> {
  const response = await axios.post<AttractionImageResponse>(`${API_BASE}/attraction`, request)
  return response.data
}

/**
 * 批量获取景点图片URL
 */
export async function getBatchImages(request: BatchImageRequest): Promise<BatchImageResponse> {
  const response = await axios.post<BatchImageResponse>(`${API_BASE}/batch`, request)
  return response.data
}

/**
 * 获取目的地城市图片
 */
export async function getDestinationImage(
  city: string,
  width: number = 1200,
  height: number = 600
): Promise<DestinationImageResponse> {
  const response = await axios.get<DestinationImageResponse>(`${API_BASE}/destination/${city}`, {
    params: { width, height }
  })
  return response.data
}

/**
 * 获取图片服务状态
 */
export async function getImageServiceStatus(): Promise<ImageServiceStatus> {
  const response = await axios.get<ImageServiceStatus>(`${API_BASE}/status`)
  return response.data
}

/**
 * 图片缓存服务（本地缓存避免重复请求）
 */
class ImageCacheService {
  private cache: Map<string, { url: string; timestamp: number }> = new Map()
  private CACHE_TTL = 1000 * 60 * 60 // 1小时缓存

  /**
   * 生成缓存键
   */
  private getKey(attraction: string, city: string): string {
    return `${attraction}:${city}`
  }

  /**
   * 获取缓存的图片URL
   */
  getCached(attraction: string, city: string): string | null {
    const key = this.getKey(attraction, city)
    const cached = this.cache.get(key)

    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.url
    }

    // 过期或不存在
    this.cache.delete(key)
    return null
  }

  /**
   * 设置缓存
   */
  setCached(attraction: string, city: string, url: string): void {
    const key = this.getKey(attraction, city)
    this.cache.set(key, { url, timestamp: Date.now() })
  }

  /**
   * 清除缓存
   */
  clear(): void {
    this.cache.clear()
  }
}

export const imageCacheService = new ImageCacheService()

/**
 * 带缓存的获取景点图片
 */
export async function getAttractionImageWithCache(
  attraction: string,
  city: string,
  width: number = 800,
  height: number = 600
): Promise<string> {
  // 先查缓存
  const cached = imageCacheService.getCached(attraction, city)
  if (cached) {
    return cached
  }

  // 请求API
  const response = await getAttractionImage({ attraction_name: attraction, city, width, height })

  // 存入缓存
  imageCacheService.setCached(attraction, city, response.url)

  return response.url
}

/**
 * 带缓存的获取目的地图片
 */
export async function getDestinationImageWithCache(
  city: string,
  width: number = 1200,
  height: number = 600
): Promise<string> {
  // 先查缓存
  const cached = imageCacheService.getCached(city, city)
  if (cached) {
    return cached
  }

  // 请求API
  const response = await getDestinationImage(city, width, height)

  // 存入缓存
  imageCacheService.setCached(city, city, response.url)

  return response.url
}

/**
 * 热门目的地图片（用于预加载）
 */
export interface PopularDestinationImage {
  city: string
  url: string
  source: 'unsplash' | 'pexels' | 'public' | 'placeholder' | 'unknown'
  width: number
  height: number
}

export interface PopularDestinationsResponse {
  destinations: PopularDestinationImage[]
  total: number
}

export interface DestinationsListResponse {
  destinations?: string[]
  region?: string
  total?: number
  regions?: string[]
}

/**
 * 获取热门城市图片URL列表（用于预加载）
 */
export async function getPopularDestinationsImages(
  limit: number = 20,
  region?: string
): Promise<PopularDestinationsResponse> {
  const params: any = { limit }
  if (region) {
    params.region = region
  }

  const response = await axios.get<PopularDestinationsResponse>(`${API_BASE}/preload/popular`, { params })
  return response.data
}

/**
 * 获取TOP热门城市图片URL列表
 */
export async function getTopDestinationsImages(limit: number = 20): Promise<PopularDestinationsResponse> {
  const response = await axios.get<PopularDestinationsResponse>(`${API_BASE}/preload/top`, {
    params: { limit }
  })
  return response.data
}

/**
 * 获取热门城市列表
 */
export async function getDestinationsList(region?: string): Promise<DestinationsListResponse> {
  const params: any = {}
  if (region) {
    params.region = region
  }

  const response = await axios.get<DestinationsListResponse>(`${API_BASE}/destinations/list`, { params })
  return response.data
}

/**
 * 图片预加载服务
 * 在后台预加载图片到浏览器缓存
 */
class ImagePreloaderService {
  private loadingImages: Map<string, Promise<HTMLImageElement>> = new Map()
  private loadedImages: Set<string> = new Set()
  private failedImages: Set<string> = new Set()

  /**
   * 预加载单个图片
   */
  preloadImage(url: string): Promise<HTMLImageElement> {
    // 如果已经加载过，直接返回
    if (this.loadedImages.has(url)) {
      return Promise.resolve(new Image())
    }

    // 如果正在加载，返回现有的Promise
    if (this.loadingImages.has(url)) {
      return this.loadingImages.get(url)!
    }

    // 如果加载过且失败了，直接返回失败的Promise
    if (this.failedImages.has(url)) {
      return Promise.reject(new Error('Image previously failed to load'))
    }

    // 创建新的加载Promise
    const loadPromise = new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image()

      img.onload = () => {
        this.loadedImages.add(url)
        this.loadingImages.delete(url)
        resolve(img)
      }

      img.onerror = () => {
        this.failedImages.add(url)
        this.loadingImages.delete(url)
        reject(new Error(`Failed to load image: ${url}`))
      }

      // 开始加载
      img.src = url
    })

    // 保存Promise以便复用
    this.loadingImages.set(url, loadPromise)

    return loadPromise
  }

  /**
   * 批量预加载图片
   */
  async preloadImages(urls: string[]): Promise<{
    success: string[]
    failed: string[]
    total: number
  }> {
    const results = await Promise.allSettled(
      urls.map(url => this.preloadImage(url).catch(() => null))
    )

    const success: string[] = []
    const failed: string[] = []

    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        success.push(urls[index])
      } else {
        failed.push(urls[index])
      }
    })

    return {
      success,
      failed,
      total: urls.length
    }
  }

  /**
   * 预加载热门目的地图片
   */
  async preloadPopularDestinations(
    limit: number = 20,
    onProgress?: (loaded: number, total: number, current: string) => void
  ): Promise<{
    success: string[]
    failed: string[]
    total: number
  }> {
    try {
      // 获取热门城市图片列表
      const response = await getTopDestinationsImages(limit)
      const urls = response.destinations.map(d => d.url)

      let loadedCount = 0
      const totalCount = urls.length

      // 逐个加载，报告进度
      const results = await Promise.allSettled(
        urls.map((url, index) => {
          onProgress?.(loadedCount, totalCount, response.destinations[index]?.city || url)

          return this.preloadImage(url)
            .then(img => {
              loadedCount++
              onProgress?.(loadedCount, totalCount, response.destinations[index]?.city || url)
              return img
            })
            .catch(() => {
              loadedCount++
              onProgress?.(loadedCount, totalCount, response.destinations[index]?.city || url)
              return null
            })
        })
      )

      const success: string[] = []
      const failed: string[] = []

      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          success.push(urls[index])
        } else {
          failed.push(urls[index])
        }
      })

      return {
        success,
        failed,
        total: totalCount
      }
    } catch (error) {
      console.error('预加载热门目的地失败:', error)
      return {
        success: [],
        failed: [],
        total: 0
      }
    }
  }

  /**
   * 检查图片是否已加载
   */
  isLoaded(url: string): boolean {
    return this.loadedImages.has(url)
  }

  /**
   * 检查图片是否加载失败
   */
  isFailed(url: string): boolean {
    return this.failedImages.has(url)
  }

  /**
   * 检查图片是否正在加载
   */
  isLoading(url: string): boolean {
    return this.loadingImages.has(url)
  }

  /**
   * 清除缓存
   */
  clear(): void {
    this.loadedImages.clear()
    this.failedImages.clear()
    this.loadingImages.clear()
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      loaded: this.loadedImages.size,
      failed: this.failedImages.size,
      loading: this.loadingImages.size,
      total: this.loadedImages.size + this.failedImages.size + this.loadingImages.size
    }
  }
}

// 导出单例
export const imagePreloaderService = new ImagePreloaderService()

export default {
  getAttractionImage,
  getAttractionImagePost,
  getBatchImages,
  getDestinationImage,
  getImageServiceStatus,
  getAttractionImageWithCache,
  getDestinationImageWithCache,
  getPopularDestinationsImages,
  getTopDestinationsImages,
  getDestinationsList,
  imageCacheService,
  imagePreloaderService
}
