/**
 * 智能体中文名称映射
 */

// 智能体名称映射表（英文 -> 中文）
export const AGENT_NAME_MAP: Record<string, string> = {
  // Group A - 需求分析与目的地匹配组
  'UserRequirementAnalyst': '需求分析专家',
  'DestinationMatcher': '目的地匹配专家',
  'RankingScorer': '排序评分专家',

  // Group B - 风格方案设计组
  'ImmersiveDesigner': '沉浸式设计专家',
  'ExplorationDesigner': '探索式设计专家',
  'RelaxationDesigner': '松弛式设计专家',
  'HiddenGemDesigner': '小众宝藏设计专家',

  // Group C - 详细攻略生成组
  'AttractionScheduler': '景点排程师',
  'TransportPlanner': '交通规划师',
  'DiningRecommender': '餐饮推荐师',
  'AccommodationAdvisor': '住宿顾问',
  'LLMGuideWriter': '攻略撰写师',

  // 组名称映射
  'Group A': 'A组 - 需求分析',
  'Group B': 'B组 - 风格设计',
  'Group C': 'C组 - 攻略生成',
  'System': '系统',
  'Agent': '智能体'
}

// 智能体组信息
export const AGENT_GROUP_INFO: Record<string, {
  name_cn: string
  name_en: string
  icon: string
  description: string
}> = {
  'UserRequirementAnalyst': {
    name_cn: '需求分析专家',
    name_en: 'UserRequirementAnalyst',
    icon: '👤',
    description: '分析您的旅行需求，生成个性化画像'
  },
  'DestinationMatcher': {
    name_cn: '目的地匹配专家',
    name_en: 'DestinationMatcher',
    icon: '🗺️',
    description: '从众多目的地中匹配最适合您的选择'
  },
  'RankingScorer': {
    name_cn: '排序评分专家',
    name_en: 'RankingScorer',
    icon: '📊',
    description: '综合评分，为您推荐最佳目的地'
  },
  'ImmersiveDesigner': {
    name_cn: '沉浸式设计专家',
    name_en: 'ImmersiveDesigner',
    icon: '🏛️',
    description: '为您设计深度文化体验的旅行方案'
  },
  'ExplorationDesigner': {
    name_cn: '探索式设计专家',
    name_en: 'ExplorationDesigner',
    icon: '🧭',
    description: '为您设计探索发现的旅行方案'
  },
  'RelaxationDesigner': {
    name_cn: '松弛式设计专家',
    name_en: 'RelaxationDesigner',
    icon: '🌸',
    description: '为您设计轻松休闲的旅行方案'
  },
  'HiddenGemDesigner': {
    name_cn: '小众宝藏设计专家',
    name_en: 'HiddenGemDesigner',
    icon: '💎',
    description: '为您设计小众秘境的旅行方案'
  },
  'AttractionScheduler': {
    name_cn: '景点排程师',
    name_en: 'AttractionScheduler',
    icon: '🎯',
    description: '为您安排每日的景点游览顺序'
  },
  'TransportPlanner': {
    name_cn: '交通规划师',
    name_en: 'TransportPlanner',
    icon: '🚇',
    description: '为您规划各景点间的交通方式'
  },
  'DiningRecommender': {
    name_cn: '餐饮推荐师',
    name_en: 'DiningRecommender',
    icon: '🍽️',
    description: '为您推荐当地美食和餐厅'
  },
  'AccommodationAdvisor': {
    name_cn: '住宿顾问',
    name_en: 'AccommodationAdvisor',
    icon: '🏨',
    description: '为您推荐合适的住宿区域和酒店'
  },
  'LLMGuideWriter': {
    name_cn: '攻略撰写师',
    name_en: 'LLMGuideWriter',
    icon: '📝',
    description: '为您生成详细的旅行攻略'
  }
}

/**
 * 获取智能体的中文名称
 */
export function getAgentCnName(agentName: string): string {
  return AGENT_NAME_MAP[agentName] || agentName
}

/**
 * 获取智能体的完整信息
 */
export function getAgentInfo(agentName: string) {
  return AGENT_GROUP_INFO[agentName] || {
    name_cn: agentName,
    name_en: agentName,
    icon: '🤖',
    description: '智能体'
  }
}

/**
 * 根据英文名获取中文名（用于显示）
 */
export function formatAgentName(agentName: string): string {
  if (!agentName) return '智能体'
  return getAgentCnName(agentName)
}
