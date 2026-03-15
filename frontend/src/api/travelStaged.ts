/**
 * 分阶段旅行规划 API
 * 连接到组A、组B、组C智能体API
 */

import axios from 'axios'

const STAGED_API_BASE = '/api/travel/staged'

export interface TravelRequirement {
  travel_scope: 'domestic' | 'international'
  start_date: string
  days: number
  adults: number
  children: number
  budget: 'economy' | 'medium' | 'luxury'
  interests: string[]
  special_requests: string
}

export interface Destination {
  destination: string
  image: string
  match_score: number
  recommendation_reason: string
  estimated_budget: {
    total: number
    per_person: number
    currency: string
  }
  best_season: string
  suitable_for: string[]  // Changed from suitableFor
  highlights: string[]
}

export interface StyleProposal {
  style_name: string
  style_icon: string
  style_type: 'immersive' | 'exploration' | 'relaxation' | 'hidden_gem'
  style_description: string
  daily_pace: string
  intensity_level: number
  preview_itinerary: Array<{
    day: number
    title: string
    attractions: string[]
  }>
  estimated_cost: number
  best_for: string
  highlights: string[]
}

export interface DetailedGuide {
  destination: string
  style_name: string
  style_type: string
  total_days: number
  start_date: string
  daily_itineraries: any[]
  summary: {
    total_attractions: number
    budget_per_day: number
    accommodation_area: string
  }
  budget_breakdown: {
    total_budget: number
    attractions: number
    transport: number
    dining: number
    accommodation: number
  }
  packing_list: string[]
  travel_tips: string[]
}

// 创建axios实例
const stagedApi = axios.create({
  baseURL: STAGED_API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 提交旅行需求
 */
export async function submitRequirements(requirements: TravelRequirement) {
  const response = await stagedApi.post('/submit-requirements', requirements)
  return response.data
}

/**
 * 获取推荐目的地 (组A智能体) - SSE流式版本
 */
export interface DestinationsStreamEvent {
  type: 'start' | 'progress' | 'step_result' | 'complete' | 'error'
  scope?: string
  llm_enabled?: string
  step?: string
  agent?: string
  progress?: number
  data?: any
  message?: string
  destinations?: Destination[]
  user_portrait?: any
}

export type DestinationsStreamEventHandler = (event: DestinationsStreamEvent) => void

export async function getDestinationsStream(
  requirements: TravelRequirement,
  onProgress: DestinationsStreamEventHandler
): Promise<{
  success: boolean
  destinations: Destination[]
  user_portrait: any
}> {
  return new Promise((resolve, reject) => {
    const url = `${STAGED_API_BASE}/get-destinations-stream`

    try {
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requirements)
      }).then(async (response) => {
        if (!response.ok) {
          // 如果流式API失败，使用非流式API作为后备
          console.warn('流式API不可用，使用非流式API')
          return fetch(`${STAGED_API_BASE}/get-destinations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requirements)
          }).then(async (res) => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
            const data = await res.json()
            // 模拟进度事件
            onProgress({ type: 'progress', step: '处理完成', agent: 'System', progress: 100 })
            resolve({
              success: true,
              destinations: data.destinations || [],
              user_portrait: data.user_portrait || {}
            })
          }).catch(err => {
            reject(err)
          })
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('无法获取响应流')
        }

        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })

          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const event: DestinationsStreamEvent = JSON.parse(data)

                // 触发进度回调
                onProgress(event)

                // 完成时返回结果
                if (event.type === 'complete') {
                  resolve({
                    success: true,
                    destinations: event.destinations || [],
                    user_portrait: event.user_portrait || {}
                  })
                }

                // 错误处理
                if (event.type === 'error') {
                  reject(new Error(event.message || '生成失败'))
                }
              } catch (e) {
                console.warn('解析 SSE 数据失败:', data, e)
              }
            }
          }
        }
      }).catch((error) => {
        console.error('流式获取目的地失败:', error)
        reject(error)
      })
    } catch (error) {
      console.error('发起流式请求失败:', error)
      reject(error)
    }
  })
}

/**
 * 获取推荐目的地 (组A智能体) - 非流式版本
 */
export async function getDestinations(requirements: TravelRequirement): Promise<{
  success: boolean
  destinations: Destination[]
  user_portrait: {
    description: string
    travel_type: string
    pace_preference: string
    budget_level: string
  }
}> {
  const response = await stagedApi.post('/get-destinations', requirements)
  return response.data
}

/**
 * 获取风格方案 (组B智能体)
 */
export async function getStyles(
  destination: string,
  userRequirements: any
): Promise<{
  success: boolean
  styles: StyleProposal[]
  destination_info: {
    destination: string
    highlights: string[]
    best_season: string
    tags: string[]
  }
}> {
  const response = await stagedApi.post('/get-styles', {
    destination,
    user_requirements: userRequirements
  })
  return response.data
}

/**
 * 获取风格方案 (组B智能体) - SSE流式版本
 */
export interface StylesStreamEvent {
  type: 'start' | 'progress' | 'step_result' | 'complete' | 'error'
  destination?: string
  step?: string
  agent?: string
  progress?: number
  data?: any
  message?: string
  styles?: StyleProposal[]
  destination_info?: {
    destination: string
    highlights: string[]
    best_season: string
    tags: string[]
  }
}

export type StylesStreamEventHandler = (event: StylesStreamEvent) => void

export async function getStylesStream(
  destination: string,
  userRequirements: any,
  onProgress: StylesStreamEventHandler
): Promise<{
  success: boolean
  styles: StyleProposal[]
  destination_info: {
    destination: string
    highlights: string[]
    best_season: string
    tags: string[]
  }
}> {
  return new Promise((resolve, reject) => {
    const url = `${STAGED_API_BASE}/get-styles-stream`

    try {
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination,
          user_requirements: userRequirements
        })
      }).then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('无法获取响应流')
        }

        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })

          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const event: StylesStreamEvent = JSON.parse(data)

                // 触发进度回调
                onProgress(event)

                // 完成时返回结果
                if (event.type === 'complete') {
                  resolve({
                    success: true,
                    styles: event.styles || [],
                    destination_info: event.destination_info || {
                      destination: '',
                      highlights: [],
                      best_season: '',
                      tags: []
                    }
                  })
                }

                // 错误处理
                if (event.type === 'error') {
                  reject(new Error(event.message || '生成失败'))
                }
              } catch (e) {
                console.warn('解析 SSE 数据失败:', data, e)
              }
            }
          }
        }
      }).catch((error) => {
        console.error('流式获取风格失败:', error)
        reject(error)
      })
    } catch (error) {
      console.error('发起流式请求失败:', error)
      reject(error)
    }
  })
}

/**
 * 生成详细攻略 (组C智能体)
 */
export async function generateGuide(
  destination: string,
  styleType: string,
  userRequirements: any
): Promise<{
  success: boolean
  guide: DetailedGuide
}> {
  const response = await stagedApi.post('/generate-guide', {
    destination,
    style_type: styleType,
    user_requirements: userRequirements
  })
  return response.data
}

/**
 * 健康检查
 */
export async function testApi() {
  const response = await stagedApi.get('/test')
  return response.data
}

/**
 * 流式生成详细攻略 (SSE)
 */
export interface StreamEvent {
  type: 'start' | 'progress' | 'step_result' | 'complete' | 'error'
  step?: string
  agent?: string
  progress?: number
  data?: any
  message?: string
  guide?: DetailedGuide
}

export type StreamEventHandler = (event: StreamEvent) => void

export async function generateGuideStream(
  destination: string,
  styleType: string,
  userRequirements: any,
  onProgress: StreamEventHandler
): Promise<{success: boolean, guide?: DetailedGuide}> {
  return new Promise((resolve, reject) => {
    const url = `${STAGED_API_BASE}/generate-guide-stream`

    try {
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination,
          style_type: styleType,
          user_requirements: userRequirements
        })
      }).then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('无法获取响应流')
        }

        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })

          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const event: StreamEvent = JSON.parse(data)

                // 触发进度回调
                onProgress(event)

                // 完成时返回结果
                if (event.type === 'complete') {
                  resolve({
                    success: true,
                    guide: event.guide
                  })
                }

                // 错误处理
                if (event.type === 'error') {
                  reject(new Error(event.message || '生成失败'))
                }
              } catch (e) {
                console.warn('解析 SSE 数据失败:', data, e)
              }
            }
          }
        }
      }).catch((error) => {
        console.error('流式生成失败:', error)
        reject(error)
      })
    } catch (error) {
      console.error('发起流式请求失败:', error)
      reject(error)
    }
  })
}

/**
 * 检查PDF支持状态
 */
export async function checkPDFSupport(): Promise<{
  success: boolean
  pdf_support: {
    reportlab: boolean
    weasyprint: boolean
    chinese_font: boolean
  }
  status: string
  message: string
}> {
  const response = await stagedApi.get('/pdf-check')
  return response.data
}

/**
 * 导出攻略为PDF
 */
export async function exportGuidePDF(
  guideData: any,
  filename?: string
): Promise<Blob> {
  const response = await stagedApi.post('/export-pdf', {
    guide_data: guideData,
    filename: filename
  }, {
    responseType: 'blob'
  })
  return response.data
}

export default {
  submitRequirements,
  getDestinations,
  getStyles,
  generateGuide,
  generateGuideStream,
  checkPDFSupport,
  exportGuidePDF,
  testApi
}
