/**
 * 详细攻略API服务
 */

import axios from 'axios'

const API_BASE = '/api/travel'

/**
 * 生成详细攻略
 */
export async function generateDetailedGuide(guideData: any): Promise<{
  success: boolean
  detailed_guide: any
  message: string
}> {
  try {
    const response = await axios.post(`${API_BASE}/guides/generate-detailed`, {
      guide_data: guideData
    })
    return response.data
  } catch (error: any) {
    console.error('生成详细攻略失败:', error)
    throw error
  }
}

/**
 * 增强攻略详情
 */
export async function enhanceGuideWithDetails(guideData: any): Promise<{
  success: boolean
  enhanced_guide: any
  message: string
}> {
  try {
    const response = await axios.post(`${API_BASE}/guides/enhance-with-details`, {
      guide_data: guideData
    })
    return response.data
  } catch (error: any) {
    console.error('增强攻略失败:', error)
    throw error
  }
}

export default {
  generateDetailedGuide,
  enhanceGuideWithDetails
}
