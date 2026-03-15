/**
 * 流式详细攻略生成 API
 * 使用 Server-Sent Events (SSE) 实现实时进度更新
 */

const API_BASE = '/api/travel'

export interface StreamEvent {
  type: 'start' | 'progress' | 'step_result' | 'complete' | 'error'
  step?: string
  day?: number
  progress?: number
  agent?: string
  data?: any
  summary?: string
  message?: string
}

export type StreamEventHandler = (event: StreamEvent) => void

/**
 * 流式生成详细攻略
 * @param guideData 基础攻略数据
 * @param onProgress 进度回调函数
 * @returns Promise<{success: boolean, detailed_guide?: any}>
 */
export async function generateDetailedGuideStream(
  guideData: any,
  onProgress: StreamEventHandler
): Promise<{success: boolean, detailed_guide?: any}> {
  return new Promise((resolve, reject) => {
    const url = `${API_BASE}/guides/generate-detailed-stream`

    try {
      // 使用 fetch 发送 POST 请求
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ guide_data: guideData })
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
        const steps: any[] = []

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // 处理完整的 SSE 消息
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || '' // 保留不完整的消息

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const event: StreamEvent = JSON.parse(data)

                // 触发进度回调
                onProgress(event)

                // 收集步骤结果
                if (event.type === 'step_result' && event.data) {
                  steps.push({
                    title: event.step,
                    summary: event.summary || '',
                    data: event.data,
                    timestamp: Date.now()
                  })
                }

                // 完成时返回结果
                if (event.type === 'complete') {
                  // 构建详细攻略数据
                  const detailed_guide = {
                    destination: guideData.destination,
                    total_days: guideData.total_days,
                    steps: steps
                  }

                  resolve({
                    success: true,
                    detailed_guide
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
 * 非流式版本的详细攻略生成（备用）
 */
export async function generateDetailedGuide(guideData: any): Promise<{
  success: boolean
  detailed_guide?: any
  message?: string
}> {
  try {
    const response = await fetch(`${API_BASE}/guides/generate-detailed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ guide_data: guideData })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    return result
  } catch (error) {
    console.error('详细攻略生成失败:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : '生成失败'
    }
  }
}
