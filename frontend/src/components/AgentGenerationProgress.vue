<!--
多智能体攻略生成进度组件

实时显示每个专业智能体的生成进度和结果
-->
<template>
  <div class="agent-progress-overlay" v-if="isVisible">
    <div class="progress-backdrop" @click="handleBackdropClick">
      <div class="progress-container" @click.stop>
        <!-- 头部 -->
        <div class="progress-header">
          <div class="header-content">
            <el-icon class="header-icon" :class="{ spinning: isGenerating }"><Loading /></el-icon>
            <div class="header-text">
              <h3>{{ title }}</h3>
              <p class="subtitle">{{ subtitle }}</p>
            </div>
          </div>
          <el-button
            v-if="!isGenerating"
            type="primary"
            @click="handleClose"
            size="large"
          >
            查看攻略
          </el-button>
        </div>

        <!-- 等待提示 -->
        <div class="waiting-notice" v-if="isGenerating">
          <div class="notice-content">
            <el-icon class="notice-icon"><Clock /></el-icon>
            <div class="notice-text">
              <p class="notice-main">智能体正在为您精心规划行程</p>
              <p class="notice-sub">这可能需要 2-5 分钟，请耐心等待...</p>
            </div>
          </div>
        </div>

        <!-- 当前步骤 -->
        <div class="current-step-card" v-if="currentStep">
          <div class="step-label">正在执行</div>
          <div class="step-content">
            <el-icon class="step-icon spinning"><Loading /></el-icon>
            <span class="step-text">{{ currentStep }}</span>
          </div>
        </div>

        <!-- 已完成的智能体 -->
        <div class="steps-flow" v-if="displayStepResults.length > 0">
          <div class="flow-header">
            <h4>已完成的工作</h4>
            <span class="flow-count">{{ displayStepResults.length }} 个智能体已完成任务</span>
          </div>

          <div class="flow-list">
            <div
              v-for="(step, index) in displayStepResults"
              :key="index"
              class="flow-item"
            >
              <!-- 连接线 -->
              <div class="flow-line" v-if="index < stepResults.length - 1"></div>

              <!-- 步骤节点 -->
              <div class="flow-node">
                <div class="node-icon completed">
                  <el-icon><CircleCheck /></el-icon>
                </div>
                <div class="node-content">
                  <div class="node-title">
                    {{ step.title }}
                    <el-tag v-if="step.agent" size="small" class="agent-tag">{{ formatAgentName(step.agent) }}</el-tag>
                  </div>
                  <div class="node-summary">{{ step.summary }}</div>
                  <div class="node-time">{{ formatTime(step.timestamp) }}</div>

                  <!-- 查看详情按钮 -->
                  <el-button
                    v-if="step.data && Object.keys(step.data).length > 0"
                    size="small"
                    text
                    type="primary"
                    @click="toggleStepDetail(step)"
                    class="view-detail-btn"
                  >
                    <el-icon><View /></el-icon>
                    查看智能体输出
                  </el-button>

                  <!-- 展开的详细内容 -->
                  <div v-if="step.expanded" class="step-detail-content">
                    <!-- 优先显示LLM描述文本 -->
                    <div v-if="step.llm_description" class="detail-section llm-description">
                      <div class="detail-label">📝 智能体分析</div>
                      <div class="detail-value llm-text">{{ step.llm_description }}</div>
                    </div>

                    <!-- 显示结构化数据 -->
                    <div v-if="step.data && Object.keys(step.data).length > 0" class="detail-section">
                      <div class="detail-label">📊 详细数据</div>
                      <div class="detail-value">
                        <div v-for="(value, key) in step.data" :key="key" class="data-item">
                          <span class="data-key">{{ formatKey(key) }}:</span>
                          <span class="data-value">{{ formatValue(value) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 完成状态 -->
        <div class="completion-card" v-if="!isGenerating && displayStepResults.length > 0">
          <div class="completion-content">
            <el-icon class="completion-icon"><CircleCheck /></el-icon>
            <div class="completion-text">
              <h4>攻略生成完成！</h4>
              <p>所有智能体已完成任务，共 {{ displayStepResults.length }} 个步骤</p>
            </div>
          </div>
        </div>

        <!-- 错误状态 -->
        <div class="error-card" v-if="hasError">
          <el-icon class="error-icon"><Warning /></el-icon>
          <div class="error-content">
            <h4>生成过程中出现错误</h4>
            <p>{{ errorMessage }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Loading, CircleCheck, Clock, Warning, View } from '@element-plus/icons-vue'
import { formatAgentName } from '@/utils/agentNames'

export interface StepResult {
  title: string
  summary: string
  data?: any
  timestamp: number
  agent?: string
  expanded?: boolean
  llm_description?: string
  step_number?: number
}

interface Props {
  isVisible: boolean
  guide: any
  stepResults?: StepResult[]
  progress?: number
}

const props = withDefaults(defineProps<Props>(), {
  stepResults: () => [],
  progress: 0
})

const emit = defineEmits<{
  'update:isVisible': [value: boolean]
  'completed': [guide: any]
  'close': []
}>()

// 状态
const progress = computed(() => props.progress)
const currentStep = ref('')
const hasError = ref(false)
const errorMessage = ref('')

// 使用传入的stepResults或内部状态
const displayStepResults = computed(() => {
  // 如果有传入的stepResults且不为空，使用传入的
  if (props.stepResults && props.stepResults.length > 0) {
    return props.stepResults
  }
  // 否则返回空数组
  return []
})

// 计算属性
const completedSteps = computed(() => displayStepResults.value.length)

// 根据进度和攻略数据判断是否正在生成
const isGenerating = computed(() => {
  // 如果有攻略数据，说明生成完成
  if (props.guide && Object.keys(props.guide).length > 0) {
    return false
  }
  // 如果进度达到100%，说明生成完成
  if (props.progress >= 100) {
    return false
  }
  // 否则正在生成
  return true
})

const title = computed(() => {
  return isGenerating.value ? '智能体正在生成您的攻略' : '攻略生成完成'
})

const subtitle = computed(() => {
  if (isGenerating.value) {
    // 如果有步骤完成，显示进度；否则只显示等待信息
    if (completedSteps.value > 0) {
      return `已完成 ${completedSteps.value} 个步骤，请耐心等待...`
    }
    return '智能体正在为您精心规划行程，这可能需要 2-5 分钟...'
  }
  return `所有智能体已完成任务 - 共 ${completedSteps.value} 个步骤`
})

// 方法
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const handleClose = () => {
  emit('update:isVisible', false)
  emit('close')
}

// 处理背景点击 - 只在完成后才允许关闭
const handleBackdropClick = () => {
  // 只在非生成状态下才允许通过点击背景关闭
  if (!isGenerating.value) {
    handleClose()
  }
}

// 更新进度（注意：progress现在是只读prop，由store控制）
const updateProgress = (_percent: number, step: string, agent?: string) => {
  currentStep.value = step
}

// 切换步骤详情展开/收起
const toggleStepDetail = (step: StepResult) => {
  step.expanded = !step.expanded
}

// 格式化键名
const formatKey = (key: string) => {
  const keyMap: Record<string, string> = {
    'restaurant': '餐厅名称',
    'address': '地址',
    'signature_dishes': '招牌菜品',
    'average_cost': '人均消费',
    'tips': '小贴士',
    'description': '景点描述',
    'highlights': '必看亮点',
    'suggested_route': '推荐路线',
    'tickets': '门票信息',
    'transport': '交通信息',
    'photography_spots': '拍照点',
    'time_needed': '游览时间',
    'best_time_to_visit': '最佳游览时间'
  }
  return keyMap[key] || key
}

// 格式化值
const formatValue = (value: any): string => {
  if (Array.isArray(value)) {
    return value.map((v, i) => `${i + 1}. ${typeof v === 'object' ? JSON.stringify(v) : v}`).join('\n')
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

// 完成
const complete = () => {
  currentStep.value = ''
  emit('completed', props.guide)
}

// 设置错误
const setError = (message: string) => {
  hasError.value = true
  errorMessage.value = message
}

// 重置
const reset = () => {
  currentStep.value = ''
  hasError.value = false
  errorMessage.value = ''
}

// 监听生成状态变化，完成时自动关闭进度条
watch(isGenerating, (newValue, oldValue) => {
  // 从正在生成变为完成时，自动关闭进度条
  if (oldValue === true && newValue === false) {
    currentStep.value = ''
    // 延迟一小段时间让用户看到完成状态，然后自动关闭
    setTimeout(() => {
      handleClose()
    }, 1500) // 1.5秒后自动关闭
  }
})

defineExpose({
  updateProgress,
  complete,
  setError,
  reset
})
</script>

<style scoped>
.agent-progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
}

.progress-backdrop {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.progress-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.4s ease;
  overflow: hidden;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 头部 */
.progress-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 2.5rem;
  color: #0EA5E9;
}

.header-icon.spinning {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-text h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0F172A;
}

.header-text .subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #64748B;
}

/* 等待提示 */
.waiting-notice {
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-bottom: 1px solid #F59E0B;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notice-icon {
  font-size: 2rem;
  color: #F59E0B;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.notice-text {
  flex: 1;
}

.notice-main {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  font-weight: 600;
  color: #92400E;
}

.notice-sub {
  margin: 0;
  font-size: 0.875rem;
  color: #B45309;
}

/* 当前步骤卡片 */
.current-step-card {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
  border-bottom: 1px solid #10B981;
}

.step-label {
  font-size: 0.7rem;
  color: #059669;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.step-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.step-icon {
  font-size: 1.25rem;
  color: #10B981;
}

.step-icon.spinning {
  animation: spin 1s linear infinite;
}

.step-text {
  font-size: 0.95rem;
  color: #065F46;
  font-weight: 500;
}

/* 流程列表 */
.steps-flow {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  min-height: 200px;
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #E5E7EB;
}

.flow-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1F2937;
}

.flow-count {
  font-size: 0.875rem;
  color: #10B981;
  font-weight: 600;
}

.flow-list {
  display: flex;
  flex-direction: column;
}

.flow-item {
  position: relative;
}

.flow-line {
  position: absolute;
  left: 20px;
  top: 40px;
  bottom: -20px;
  width: 2px;
  background: #E5E7EB;
  z-index: 0;
}

.flow-item:last-child .flow-line {
  display: none;
}

.flow-node {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.node-icon.completed {
  background: #10B981;
  color: white;
}

.node-icon .el-icon {
  font-size: 1.25rem;
}

.node-content {
  flex: 1;
  padding: 0.75rem 0;
}

.node-title {
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 0.25rem;
}

.node-summary {
  font-size: 0.875rem;
  color: #64748B;
  line-height: 1.5;
}

.node-time {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin-top: 0.5rem;
}

/* 智能体标签 */
.agent-tag {
  margin-left: 0.5rem;
  font-size: 0.7rem;
}

/* 查看详情按钮 */
.view-detail-btn {
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

/* 步骤详细内容 */
.step-detail-content {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #F9FAFB;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
}

.detail-section {
  margin-bottom: 0.75rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

/* LLM描述文本样式 */
.detail-section.llm-description {
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #0EA5E9;
}

.detail-section.llm-description .detail-label {
  color: #0369A1;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.detail-section.llm-description .llm-text {
  color: #0C4A6E;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 0.8rem;
  color: #6B7280;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 数据项样式 */
.data-item {
  display: flex;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.data-item:last-child {
  margin-bottom: 0;
}

.data-key {
  color: #374151;
  font-weight: 500;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.data-value {
  color: #6B7280;
  flex: 1;
  word-break: break-word;
}

/* 完成卡片 */
.completion-card {
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  border-top: 1px solid #10B981;
  margin-top: auto;
}

.completion-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.completion-icon {
  font-size: 2.5rem;
  color: #10B981;
}

.completion-text h4 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #065F46;
}

.completion-text p {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: #059669;
}

/* 错误卡片 */
.error-card {
  padding: 1.5rem 2rem;
  background: #FEF2F2;
  border-top: 1px solid #EF4444;
}

.error-icon {
  font-size: 2rem;
  color: #EF4444;
  margin-bottom: 0.5rem;
}

.error-content h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: #991B1B;
}

.error-content p {
  margin: 0;
  font-size: 0.875rem;
  color: #B91C1C;
}
</style>
