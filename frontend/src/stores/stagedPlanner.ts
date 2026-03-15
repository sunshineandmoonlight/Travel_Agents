/**
 * 分阶段旅行规划 Store
 * 使用Pinia管理旅行规划状态
 */

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import * as StagedAPI from '@/api/travelStaged'

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

export interface StepResult {
  title: string
  summary: string
  data?: any
  timestamp: number
  agent?: string
  expanded?: boolean
  llm_description?: string  // 添加LLM描述字段
  step_number?: number  // 添加步骤编号（1-5）
}

export const useStagedPlannerStore = defineStore('stagedPlanner', () => {
  // State
  const currentStep = ref(0)
  const loading = ref(false)
  const stepLoading = ref(false)
  const loadingText = ref('')
  const progress = ref(0)  // 添加生成进度 (0-100)
  const stepResults = ref<StepResult[]>([])  // 添加智能体输出记录

  const travelScope = ref<'domestic' | 'international'>('domestic')
  const requirements = ref<TravelRequirement | null>(null)

  const destinations = ref<Destination[]>([])
  const userPortrait = ref<any>(null)

  const selectedDestination = ref<string>('')
  const styleProposals = ref<StyleProposal[]>([])
  const selectedStyle = ref<string>('')
  const detailedGuide = ref<any>(null)

  // Computed
  const totalSteps = 5

  const canGoNext = computed(() => {
    switch (currentStep.value) {
      case 0:
        return true // Scope is always selected
      case 1:
        return requirements.value !== null
      case 2:
        return selectedDestination.value !== ''
      case 3:
        return selectedStyle.value !== ''
      default:
        return false
    }
  })

  // Actions
  const setScope = (scope: 'domestic' | 'international') => {
    travelScope.value = scope
    currentStep.value = 1
  }

  const setRequirements = async (req: any) => {
    requirements.value = req
    loading.value = true
    loadingText.value = '正在为您分析最佳目的地...'
    progress.value = 0
    // 不再清空之前的步骤结果，而是累积所有结果
    // stepResults.value = []

    try {
      // Transform camelCase to snake_case for backend
      const apiRequest = {
        travel_scope: req.travelScope || req.travel_scope || travelScope.value,
        start_date: req.startDate,
        days: req.days,
        adults: req.adults,
        children: req.children,
        budget: req.budget,
        interests: req.interests,
        special_requests: req.specialRequests || req.special_requests || ''
      }

      // 使用流式API获取目的地
      const result = await StagedAPI.getDestinationsStream(
        apiRequest,
        (event: any) => {
          if (event.type === 'progress') {
            loadingText.value = `${event.agent}: ${event.step}...`
            if (event.progress !== undefined) {
              progress.value = event.progress
            }
          } else if (event.type === 'step_result') {
            const stepResult: StepResult = {
              title: event.step,
              summary: `智能体 ${event.agent} 完成了任务`,
              data: event.data || {},
              llm_description: event.data?.llm_description || event.llm_description || '',
              timestamp: Date.now(),
              agent: event.agent,
              expanded: false,
              step_number: 2  // 步骤2：选择目的地（Group A智能体）
            }
            stepResults.value.push(stepResult)
            console.log(`[智能体完成] ${event.agent}: ${event.step}`, event.data)
          }
        }
      )

      destinations.value = result.destinations || []
      userPortrait.value = result.user_portrait || {
        description: '',
        preferences: [],
        budget_level: req.budget
      }
      currentStep.value = 2
    } catch (error: any) {
      // Set default values on error
      destinations.value = []
      userPortrait.value = {
        description: '',
        preferences: [],
        budget_level: req.budget
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  const setSelectedDestination = (destination: string) => {
    selectedDestination.value = destination
  }

  const loadStyles = async () => {
    stepLoading.value = true
    progress.value = 0
    // 清空之前的步骤结果，只保留步骤1-2的结果
    stepResults.value = stepResults.value.filter(r => (r.step_number || 0) < 3)

    try {
      // 用于跟踪已处理的事件，防止重复
      const processedEvents = new Set<string>()

      // 使用流式API获取风格方案
      const result = await StagedAPI.getStylesStream(
        selectedDestination.value,
        {
          travel_scope: travelScope.value,
          days: requirements.value?.days || 5,
          user_portrait: userPortrait.value
        },
        (event: any) => {
          if (event.type === 'progress') {
            loadingText.value = `${event.agent}: ${event.step}...`
            if (event.progress !== undefined) {
              progress.value = event.progress
            }
          } else if (event.type === 'step_result') {
            // 生成唯一ID来防止重复添加
            const eventId = `${event.step}_${event.agent}_${event.progress || 0}`

            if (!processedEvents.has(eventId)) {
              processedEvents.add(eventId)

              const stepResult: StepResult = {
                title: event.step,
                summary: `智能体 ${event.agent} 完成了任务`,
                data: event.data || {},
                llm_description: event.data?.llm_description || event.llm_description || '',
                timestamp: Date.now(),
                agent: event.agent,
                expanded: false,
                step_number: 3  // 步骤3：选择风格（Group B智能体）
              }
              stepResults.value.push(stepResult)
              console.log(`[智能体完成] ${event.agent}: ${event.step}`, event.data)
            }
          }
        }
      )

      styleProposals.value = result.styles
      currentStep.value = 3
    } catch (error: any) {
      throw error
    } finally {
      stepLoading.value = false
    }
  }

  const setSelectedStyle = (style: string) => {
    selectedStyle.value = style
  }

  const generateGuide = async () => {
    loading.value = true
    loadingText.value = '正在为您生成详细攻略...'
    progress.value = 0  // 重置进度
    // 清空之前的步骤结果，避免重复累积
    stepResults.value = []

    try {
      const userRequirements = {
        travel_scope: travelScope.value,
        start_date: requirements.value?.start_date || new Date().toISOString().split('T')[0],
        days: requirements.value?.days || 5,
        user_portrait: userPortrait.value
      }

      // 用于跟踪已处理的事件，防止重复
      const processedEvents = new Set<string>()

      // 使用流式API生成攻略
      const result = await StagedAPI.generateGuideStream(
        selectedDestination.value,
        selectedStyle.value,
        userRequirements,
        (event: any) => {
          // 实时更新进度
          if (event.type === 'progress') {
            loadingText.value = `${event.agent}: ${event.step}...`
            if (event.progress !== undefined) {
              progress.value = event.progress
            }
          } else if (event.type === 'step_result') {
            // 生成唯一ID来防止重复添加
            const eventId = `${event.step}_${event.agent}_${event.progress || 0}`

            if (!processedEvents.has(eventId)) {
              processedEvents.add(eventId)

              // 记录智能体输出
              const stepResult: StepResult = {
                title: event.step,
                summary: `智能体 ${event.agent} 完成了任务`,
                data: event.data || {},
                llm_description: event.data?.llm_description || event.llm_description || '',
                timestamp: Date.now(),
                agent: event.agent,
                expanded: false,
                step_number: 4  // 步骤4：生成攻略（Group C智能体）
              }
              stepResults.value.push(stepResult)
              console.log(`[智能体完成] ${event.agent}: ${event.step}`, event.data)
            }
          }
        }
      )

      detailedGuide.value = result.guide
      currentStep.value = 4
    } catch (error: any) {
      throw error
    } finally {
      // 不设置loading为false，让用户可以看到完成的步骤
      // loading.value = false
    }
  }

  const reset = () => {
    currentStep.value = 0
    loading.value = false
    stepLoading.value = false
    loadingText.value = ''
    progress.value = 0
    stepResults.value = []  // 只在reset时清空
    travelScope.value = 'domestic'
    requirements.value = null
    destinations.value = []
    userPortrait.value = null
    selectedDestination.value = ''
    styleProposals.value = []
    selectedStyle.value = ''
    detailedGuide.value = null
  }

  // 新增：清空当前步骤之后的结果（用于重新生成当前步骤）
  const clearAfterStep = (stepNumber: number) => {
    stepResults.value = stepResults.value.filter(r => (r.step_number || 0) <= stepNumber)
  }

  const goBack = () => {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  return {
    // State
    currentStep,
    loading,
    stepLoading,
    loadingText,
    progress,
    stepResults,
    travelScope,
    requirements,
    destinations,
    userPortrait,
    selectedDestination,
    styleProposals,
    selectedStyle,
    detailedGuide,

    // Computed
    totalSteps,
    canGoNext,

    // Actions
    setScope,
    setRequirements,
    setSelectedDestination,
    loadStyles,
    setSelectedStyle,
    generateGuide,
    reset,
    clearAfterStep,
    goBack
  }
})
