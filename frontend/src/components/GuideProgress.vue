/**
 * 攻略生成进度组件
 * 显示每个智能体的生成进度和结果
 */
<template>
  <div class="guide-progress" v-if="showProgress">
    <div class="progress-header">
      <el-icon class="progress-icon"><Loading /></el-icon>
      <span class="progress-title">正在生成详细攻略...</span>
      <span class="progress-percent">{{ Math.round(progress) }}%</span>
    </div>

    <!-- 进度条 -->
    <el-progress
      :percentage="progress"
      :stroke-width="8"
      :show-text="false"
      class="progress-bar"
    />

    <!-- 当前步骤 -->
    <div class="current-step" v-if="currentStep">
      <el-icon class="step-icon"><Clock /></el-icon>
      <span>{{ currentStep }}</span>
    </div>

    <!-- 已完成的步骤 -->
    <div class="completed-steps" v-if="completedSteps.length > 0">
      <div
        v-for="(step, index) in completedSteps"
        :key="index"
        class="completed-step"
      >
        <el-icon class="step-icon completed"><CircleCheck /></el-icon>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-result" v-if="step.result">
            {{ step.result }}
          </div>
        </div>
      </div>
    </div>

    <!-- 完成提示 -->
    <div class="completion-message" v-if="progress >= 100">
      <el-icon class="success-icon"><CircleCheck /></el-icon>
      <span>详细攻略生成完成！</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Loading, Clock, CircleCheck } from '@element-plus/icons-vue'

interface CompletedStep {
  title: string
  result: string
  timestamp: number
}

const props = defineProps<{
  showProgress: boolean
}>()

const emit = defineEmits<{
  'update:showProgress': [value: boolean]
}>()

const progress = ref(0)
const currentStep = ref('')
const completedSteps = ref<CompletedStep[]>([])

// 更新进度
const updateProgress = (percent: number, step?: string) => {
  progress.value = percent
  if (step) {
    currentStep.value = step
  }
}

// 添加完成的步骤
const addCompletedStep = (title: string, result: string) => {
  completedSteps.value.push({
    title,
    result,
    timestamp: Date.now()
  })
  currentStep.value = ''
}

// 完成进度
const complete = () => {
  progress.value = 100
  currentStep.value = ''
  setTimeout(() => {
    emit('update:showProgress', false)
  }, 1500)
}

// 重置
const reset = () => {
  progress.value = 0
  currentStep.value = ''
  completedSteps.value = []
}

defineExpose({
  updateProgress,
  addCompletedStep,
  complete,
  reset
})
</script>

<style scoped>
.guide-progress {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 9999;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.progress-icon {
  font-size: 2rem;
  color: #0EA5E9;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #334155;
  flex: 1;
}

.progress-percent {
  font-size: 1.2rem;
  font-weight: 700;
  color: #0EA5E9;
}

.progress-bar {
  margin-bottom: 1.5rem;
}

.current-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #F0F9FF;
  border-radius: 8px;
  margin-bottom: 1rem;
  color: #0369A1;
  font-size: 0.9rem;
}

.current-step .el-icon {
  font-size: 1.1rem;
}

.completed-steps {
  margin-top: 1rem;
  max-height: 200px;
  overflow-y: auto;
}

.completed-step {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #F0FDF4;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.completed-step .step-icon {
  color: #10B981;
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: #065F46;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.step-result {
  color: #64748B;
  font-size: 0.85rem;
  line-height: 1.4;
}

.completion-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  margin-top: 1rem;
}

.success-icon {
  font-size: 1.5rem;
}
</style>
