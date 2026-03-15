"""
详细攻略进度显示组件

实时显示每个智能体的生成进度
"""
<template>
  <div class="generation-process" v-if="isVisible">
    <div class="process-overlay" @click="close">
      <div class="process-panel" @click.stop>
        <div class="panel-header">
          <h3>攻略生成进度</h3>
          <el-button
            type="text"
            @click="close"
            :icon="Close"
            class="close-btn"
          >
            {{ progress >= 100 ? '完成' : '关闭' }}
          </el-button>
        </div>

        <div class="progress-section">
          <div class="progress-bar-wrapper">
            <el-progress
              :percentage="progress"
              :status="progressStatus"
              :stroke-width="10"
            />
            <div class="progress-text">{{ Math.round(progress) }}%</div>
          </div>

          <div class="current-step" v-if="currentStep">
            <el-icon class="step-icon"><Loading /></el-icon>
            <span>{{ currentStep }}</span>
          </div>
        </div>

        <!-- 已完成的步骤 -->
        <div class="steps-list" v-if="completedSteps.length > 0">
          <h4>已完成步骤</h4>
          <div
            v-for="(step, index) in completedSteps"
            :key="index"
            class="step-item"
          >
            <div class="step-header">
              <el-icon class="step-icon completed"><CircleCheck /></el-icon>
              <span class="step-title">{{ step.title }}</span>
              <span class="step-time">{{ formatTime(step.timestamp) }}</span>
            </div>
            <div class="step-content" v-if="step.summary">
              {{ step.summary }}
            </div>
            <div class="step-details" v-if="showDetails && step.data">
              <pre>{{ JSON.stringify(step.data, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <!-- 完成状态 -->
        <div class="completion-section" v-if="progress >= 100">
          <div class="success-message">
            <el-icon class="success-icon"><CircleCheck /></el-icon>
            <span>所有内容生成完成！</span>
          </div>
          <el-button type="primary" @click="close" size="large">
            查看攻略
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Loading, CircleCheck, Close } from '@element-plus/icons-vue'

interface StepResult {
  title: string
  summary: string
  data?: any
  timestamp: number
}

const props = defineProps<{
  isVisible: boolean
  guide: any
}>()

const emit = defineEmits<{
  'update:isVisible': [value: boolean]
  'completed': [guide: any]
}>()

const progress = ref(0)
const currentStep = ref('')
const completedSteps = ref<StepResult[]>([])
const showDetails = ref(false)

const progressStatus = computed(() => {
  if (progress.value >= 100) return 'success'
  if (progress.value < 30) return ''
  return null
})

// 添加完成步骤
const addStep = (step: StepResult) => {
  completedSteps.value.push(step)
}

// 更新进度
const updateProgress = (percent: number, step: string) => {
  progress.value = percent
  currentStep.value = step
}

// 完成
const complete = () => {
  progress.value = 100
  currentStep.value = '生成完成！'

  setTimeout(() => {
    emit('completed', props.guide)
    // 自动关闭进度显示
    setTimeout(() => {
      close()
    }, 2000)
  }, 500)
}

// 重置
const reset = () => {
  progress.value = 0
  currentStep.value = ''
  completedSteps.value = []
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const close = () => {
  emit('update:isVisible', false)
}

// 监听props变化，开始生成
watch(() => props.isVisible, (isVisible) => {
  if (isVisible && props.guide) {
    reset()
    simulateGeneration()
  }
})

// 模拟生成过程（实际应该调用后端API）
const simulateGeneration = async () => {
  const destination = props.guide.destination || '未知'
  const days = props.guide.total_days || 5

  // 开始
  addStep({
    title: '开始生成',
    summary: `正在为 ${destination} 生成 ${days} 天详细攻略`,
    timestamp: Date.now()
  })
  updateProgress(5, '开始生成...')

  await sleep(500)

  // 模拟每天生成过程
  for (let day = 1; day <= days; day++) {
    updateProgress(5 + (day * 80 / days), `正在生成第${day}天...`)

    await sleep(300)

    // 添加每天完成步骤
    addStep({
      title: `第${day}天攻略生成完成`,
      summary: `第${day}天的详细行程已生成`,
      data: { day: day },
      timestamp: Date.now()
    })

    updateProgress(5 + (day * 80 / days), `第${day}天完成`)
  }

  // 完成
  complete()
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

defineExpose({
  addStep,
  updateProgress,
  complete
})
</script>

<style scoped>
.generation-process {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.process-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.process-panel {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #E5E7EB;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1F2937;
}

.close-btn {
  font-size: 0.9rem;
}

.progress-section {
  padding: 1.5rem;
  border-bottom: 1px solid #E5E7EB;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.progress-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0EA5E9;
  min-width: 50px;
  text-align: right;
}

.current-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #F0F9FF;
  border-radius: 8px;
  color: #0369A1;
  font-size: 0.9rem;
}

.current-step .el-icon {
  font-size: 1.1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.steps-list {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

.steps-list h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.step-item {
  padding: 1rem;
  background: #F9FAFB;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  border-left: 3px solid #10B981;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.step-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.step-icon.completed {
  color: #10B981;
}

.step-title {
  font-weight: 600;
  color: #065F46;
  flex: 1;
}

.step-time {
  font-size: 0.8rem;
  color: #9CA3AF;
}

.step-content {
  color: #64748B;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.step-details {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #F3F4F6;
  border-radius: 6px;
  font-size: 0.8rem;
}

.step-details pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  color: #475569;
}

.completion-section {
  padding: 1.5rem;
  text-align: center;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  border-radius: 0 0 16px 16px;
}

.success-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #065F46;
  margin-bottom: 1rem;
}

.success-icon {
  font-size: 1.5rem;
  color: #10B981;
}
</style>
