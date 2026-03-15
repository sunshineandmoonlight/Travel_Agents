/**
 * 旅行规划 Store
 * 管理表单式 AI 交互式旅行规划流程的状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { travelPlanningApi } from '@/api/travel'
import { ElMessage } from 'element-plus'

export const useTravelPlannerStore = defineStore('travelPlanner', () => {
  // 状态
  const step = ref(1)
  const isLoading = ref(false)
  const generatedPlans = ref<any[]>([])
  const selectedPlan = ref<any>(null)
  const generatedGuide = ref<any>(null)

  // 计算属性
  const currentStep = computed(() => step.value)
  const hasPlans = computed(() => generatedPlans.value.length > 0)
  const hasGuide = computed(() => generatedGuide.value !== null)

  // 方法
  const reset = () => {
    step.value = 1
    isLoading.value = false
    generatedPlans.value = []
    selectedPlan.value = null
    generatedGuide.value = null
  }

  const submitRequirements = async (requirements: {
    destination: string
    days: number
    adults: number
    children: number
    budget: string
    styles: string[]
    special_requests?: string
  }) => {
    isLoading.value = true
    try {
      const response = await travelPlanningApi.generatePlans(requirements)
      generatedPlans.value = response.data.plans || []
      return generatedPlans.value
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '生成方案失败')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const selectPlan = async (plan: any) => {
    selectedPlan.value = plan
    isLoading.value = true
    try {
      // 使用实际的 plan 数据
      const cleanPlan = {
        name: plan.name || '方案',
        days: plan.days || 5,
        budget: plan.budget || 'medium',
        destination: plan.destination || '',
        description: plan.description || ''
      }

      const requirementsStr = `为${cleanPlan.days}天的${cleanPlan.destination || ''}旅行生成详细攻略`

      console.log('=== generateGuide Debug ===')
      console.log('Sending:', { cleanPlan, requirements: requirementsStr })

      // 直接使用 axios 调用
      const axios = (await import('axios')).default
      const response = await axios.post('http://localhost:8004/api/travel/plans/ai/generate-guide', {
        selected_plan: cleanPlan,
        requirements: requirementsStr
      }, {
        headers: { 'Content-Type': 'application/json' }
      })

      console.log('Response:', response.data)
      generatedGuide.value = response.data.guide
      ElMessage.success('攻略生成成功！')
    } catch (error: any) {
      console.error('=== generateGuide Error ===')
      console.error('Error:', error.response?.data)
      ElMessage.error(`生成攻略失败: ${JSON.stringify(error.response?.data)}`)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const savePlan = async (title?: string) => {
    isLoading.value = true
    try {
      const requestData = {
        title: title || '我的旅行计划',
        destination: selectedPlan.value?.destination || '目的地',
        days: selectedPlan.value?.days || 5,
        plan_data: {
          name: selectedPlan.value?.name || '方案',
          description: selectedPlan.value?.description || '',
          budget: selectedPlan.value?.budget || 'medium',
          highlights: selectedPlan.value?.highlights || [],
          itinerary: selectedPlan.value?.itinerary || []
        }
      }

      console.log('Saving plan:', requestData)

      // 直接使用 axios 调用
      const axios = (await import('axios')).default
      const response = await axios.post('http://localhost:8004/api/travel/plans/ai/save-plan', requestData, {
        headers: { 'Content-Type': 'application/json' }
      })

      console.log('Save response:', response.data)
      step.value = 5
      ElMessage.success('计划已保存！')
      return response.data
    } catch (error: any) {
      console.error('Save error:', error.response?.data)
      ElMessage.error(`保存失败: ${JSON.stringify(error.response?.data)}`)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 辅助函数：从用户输入中提取信息
  const extractDestination = (input: string): string => {
    // 尝试匹配城市名
    const cities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '重庆', '南京', '武汉', '苏州', '厦门', '三亚', '青岛', '大连', '桂林', '丽江', '拉萨', '乌鲁木齐', '哈尔滨', '长春', '沈阳', '济南', '郑州', '长沙', '南昌', '合肥', '福州', '昆明', '贵阳', '南宁', '海口', '兰州', '西宁', '呼和浩特', '银川', '太原', '石家庄', '天津', '日本', '韩国', '泰国', '新加坡', '马来西亚', '越南', '柬埔寨', '印度尼西亚', '菲律宾', '马尔代夫', '土耳其', '希腊', '意大利', '法国', '德国', '瑞士', '英国', '美国', '加拿大', '澳大利亚', '新西兰']

    for (const city of cities) {
      if (input.includes(city)) {
        return city
      }
    }
    return input.split('旅行')[0]?.split('去')[1]?.split('游')[0] || '目的地'
  }

  const extractDays = (input: string): number => {
    const match = input.match(/(\d+)天/)
    return match ? parseInt(match[1]) : 5
  }

  const extractTravelers = (input: string) => {
    const adults = input.match(/(\d+)成人/) ? parseInt(input.match(/(\d+)成人/)[1]) : 2
    const children = input.match(/(\d+)儿童/) ? parseInt(input.match(/(\d+)儿童/)[1]) : 0
    return { adults, children }
  }

  const extractBudget = (input: string): string => {
    if (input.includes('经济') || input.includes('便宜')) return 'economy'
    if (input.includes('奢华') || input.includes('豪华')) return 'luxury'
    if (input.includes('品质') || input.includes('舒适')) return 'premium'
    return 'comfort'
  }

  const extractPreferences = (input: string): string[] => {
    const prefs = []
    if (input.includes('休闲')) prefs.push('休闲')
    if (input.includes('文化') || input.includes('历史')) prefs.push('文化')
    if (input.includes('美食') || input.includes('小吃')) prefs.push('美食')
    if (input.includes('购物') || input.includes('血拼')) prefs.push('购物')
    if (input.includes('自然') || input.includes('风景')) prefs.push('自然')
    if (input.includes('探险') || input.includes('户外')) prefs.push('探险')
    if (input.includes('亲子') || input.includes('家庭')) prefs.push('亲子')
    if (input.includes('蜜月') || input.includes('情侣')) prefs.push('蜜月')
    return prefs.length > 0 ? prefs : ['休闲', '观光']
  }

  return {
    // 状态
    step,
    isLoading,
    generatedPlans,
    selectedPlan,
    generatedGuide,
    // 计算属性
    currentStep,
    hasPlans,
    hasGuide,
    // 方法
    reset,
    submitRequirements,
    selectPlan,
    savePlan
  }
})
