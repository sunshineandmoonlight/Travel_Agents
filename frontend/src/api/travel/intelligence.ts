/**
 * 目的地情报 API
 */

import axios from 'axios'

const API_BASE = '/api/travel/intelligence'

// ============================================================
// 新闻模块API
// ============================================================

/**
 * 获取旅游新闻
 */
export async function getTravelNews(
  destination: string,
  limit: number = 10
): Promise<{ destination: string; news_type: string; news: NewsItem[]; total: number; source: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/news/travel`, {
    params: { limit }
  })
  return response.data
}

/**
 * 获取地区新闻
 */
export async function getAreaNews(
  destination: string,
  limit: number = 10
): Promise<{ destination: string; news_type: string; news: NewsItem[]; total: number; source: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/news/area`, {
    params: { limit }
  })
  return response.data
}

/**
 * 获取综合新闻
 */
export async function getGeneralNews(
  destination: string,
  limit: number = 10
): Promise<{ destination: string; news_type: string; news: NewsItem[]; total: number; source: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/news/general`, {
    params: { limit }
  })
  return response.data
}

export interface DestinationIntelligence {
  destination: string
  generated_at: string
  travel_date?: string
  news: NewsItem[]
  weather: WeatherInfo
  exchange_rate: ExchangeRate
  attractions: Attraction[]
  risk_assessment: RiskAssessment
  recommendations: string[]
}

export interface NewsItem {
  title: string
  source: string
  published_at: string
  url: string
  summary: string
  sentiment: 'positive' | 'neutral' | 'negative'
  category: string
}

export interface WeatherInfo {
  city: string
  current: {
    temperature: string
    weather: string
    wind: string
    humidity: string
  }
  forecast: Array<{
    date: string
    day_temp: string
    night_temp: string
    weather: string
    week: string
  }>
  tips: string
}

export interface ExchangeRate {
  available: boolean
  from?: string
  to?: string
  rate?: number
  inverse?: number
  example?: string
  updated?: number
  reason?: string
}

export interface Attraction {
  name: string
  rating: number
  reviews: number
  address: string
  phone: string
  description: string
  thumbnail: string
}

export interface RiskAssessment {
  overall_risk_text: string
  risk_level: number
  recommendation: string
  risk_categories: {
    political?: { status: string; description: string }
    safety?: { status: string; description: string }
    health?: { status: string; description: string }
    natural?: { status: string; description: string }
    social?: { status: string; description: string }
  }
}

/**
 * 获取目的地完整情报（整合所有真实API）
 */
export async function getDestinationIntelligence(
  destination: string,
  travelDate?: string
): Promise<{ success: boolean; data: DestinationIntelligence; sources: any }> {
  const response = await axios.get(`${API_BASE}/${destination}/realtime`, {
    params: { travel_date: travelDate }
  })
  return response.data
}

/**
 * 获取天气信息
 */
export async function getDestinationWeather(
  destination: string
): Promise<{ success: boolean; destination: string; weather: WeatherInfo; source: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/weather`)
  return response.data
}

/**
 * 获取汇率信息
 */
export async function getDestinationExchangeRate(
  destination: string
): Promise<{ success: boolean; destination: string; exchange_rate: ExchangeRate; updated_at: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/exchange-rate`)
  return response.data
}

/**
 * 获取景点信息
 */
export async function getDestinationAttractions(
  destination: string,
  limit: number = 10
): Promise<{ success: boolean; destination: string; attractions: Attraction[]; total: number; source: string }> {
  const response = await axios.get(`${API_BASE}/${destination}/attractions`, {
    params: { limit }
  })
  return response.data
}

/**
 * 获取新闻信息
 */
export async function getDestinationNews(
  destination: string,
  days: number = 7,
  limit: number = 10
): Promise<{ destination: string; news: NewsItem[]; total: number; search_days: number }> {
  const response = await axios.get(`${API_BASE}/${destination}/news`, {
    params: { days, limit }
  })
  return response.data
}

/**
 * 刷新情报
 */
export async function refreshIntelligence(
  destination: string,
  travelDate?: string
): Promise<{ success: boolean; destination: string; message: string; generated_at: string }> {
  const response = await axios.post(`${API_BASE}/refresh`, null, {
    params: { destination, travel_date }
  })
  return response.data
}

export default {
  getDestinationIntelligence,
  getDestinationWeather,
  getDestinationExchangeRate,
  getDestinationAttractions,
  getDestinationNews,
  refreshIntelligence
}
