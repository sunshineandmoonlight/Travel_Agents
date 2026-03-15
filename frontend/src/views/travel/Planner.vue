<template>
  <div class="travel-planner-app">
    <!-- Agent Progress Overlay - 显示智能体工作进度 -->
    <AgentGenerationProgress
      :isVisible="store.loading"
      :guide="store.detailedGuide"
      :stepResults="store.stepResults"
      :progress="store.progress"
      @update:isVisible="handleProgressClose"
      @completed="handleProgressComplete"
      @close="handleProgressClose"
    />

    <!-- Progress Steps -->
    <div class="progress-bar">
      <div class="progress-container">
        <div class="steps">
          <div
            v-for="(step, index) in steps"
            :key="index"
            :class="['step', { active: store.currentStep === index, completed: store.currentStep > index }]"
            @click="goToStep(index)"
          >
            <div class="step-number">
              <el-icon v-if="store.currentStep > index"><Check /></el-icon>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="step-label">{{ step.label }}</div>
          </div>
        </div>
        <div class="progress-line">
          <div class="progress-fill" :style="{ width: store.progress + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay - 仅在初始加载时显示（智能体进度组件会处理详细进度） -->
    <Transition name="fade">
      <div v-if="store.loading && store.stepResults.length === 0" class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner">
            <el-icon class="is-loading" :size="50"><Loading /></el-icon>
          </div>
          <p class="loading-text">{{ store.loadingText }}</p>
          <div class="loading-progress-wrapper">
            <el-progress :percentage="store.progress" :show-text="false" :stroke-width="3" />
          </div>
        </div>
      </div>
    </Transition>

    <!-- Page Content -->
    <div class="page-content">
      <Transition name="slide-fade" mode="out-in">
        <!-- Step 1: Select Scope -->
        <ScopeSelector v-if="store.currentStep === 0" @select="store.setScope" />

        <!-- Step 2: Requirements Form -->
        <RequirementsForm
          v-else-if="store.currentStep === 1"
          :scope="store.travelScope"
          @submit="store.setRequirements"
          @back="store.goBack"
        />

        <!-- Step 3: Destination Cards -->
        <DestinationCards
          v-else-if="store.currentStep === 2"
          :destinations="store.destinations"
          :user-portrait="store.userPortrait"
          :loading="store.stepLoading"
          @select="handleDestinationSelect"
          @back="store.goBack"
        />

        <!-- Step 4: Style Selection -->
        <StyleSelection
          v-else-if="store.currentStep === 3"
          :destination="store.selectedDestination"
          :styles="store.styleProposals"
          :loading="store.stepLoading"
          @select="handleStyleSelect"
          @back="store.goBack"
        />

        <!-- Step 5: Detailed Guide -->
        <DetailedGuide
          v-else-if="store.currentStep === 4"
          :guide="store.detailedGuide"
          @restart="store.reset"
        />
      </Transition>
    </div>

    <!-- Navigation Buttons (已隐藏，使用界面内部导航) -->
    <Transition name="slide-up">
      <div v-if="false && store.currentStep > 0 && store.currentStep < 4" class="bottom-nav">
        <el-button size="large" class="nav-btn" @click="store.goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button
          v-if="store.currentStep < 3"
          type="primary"
          size="large"
          class="nav-btn nav-btn-primary"
          :disabled="!canContinue"
          @click="handleContinue"
        >
          继续
          <el-icon class="ml-1"><ArrowRight /></el-icon>
        </el-button>
        <el-button
          v-else
          type="primary"
          size="large"
          class="nav-btn nav-btn-cta"
          @click="handleGenerate"
          :loading="store.loading"
        >
          生成攻略
          <el-icon class="ml-1"><MagicStick /></el-icon>
        </el-button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading, ArrowLeft, ArrowRight, MagicStick, Check } from '@element-plus/icons-vue'
import { useStagedPlannerStore } from '@/stores/stagedPlanner'
import ScopeSelector from './steps/ScopeSelector.vue'
import RequirementsForm from './steps/RequirementsForm.vue'
import DestinationCards from './steps/DestinationCards.vue'
import StyleSelection from './steps/StyleSelection.vue'
import DetailedGuide from './steps/DetailedGuide.vue'
import AgentGenerationProgress from '@/components/AgentGenerationProgress.vue'

const steps = [
  { label: '选择范围' },
  { label: '旅行需求' },
  { label: '选择目的地' },
  { label: '选择风格' },
  { label: '生成攻略' }
]

const store = useStagedPlannerStore()

const canContinue = computed(() => {
  switch (store.currentStep) {
    case 1:
      return store.requirements !== null
    case 2:
      return store.selectedDestination !== ''
    case 3:
      return store.selectedStyle !== ''
    default:
      return false
  }
})

const goToStep = (step: number) => {
  if (step <= store.currentStep || step === store.currentStep + 1) {
    if (step === 2 && store.destinations.length === 0) {
      return
    }
    if (step === 3 && store.styleProposals.length === 0) {
      return
    }
    store.currentStep = step
  }
}

const handleDestinationSelect = (destination: string) => {
  store.setSelectedDestination(destination)
  store.loadStyles()
}

const handleStyleSelect = (style: string) => {
  store.setSelectedStyle(style)
  // 选择风格后直接生成攻略
  store.generateGuide()
}

const handleContinue = () => {
  store.currentStep++
}

const handleGenerate = () => {
  store.generateGuide()
}

// 处理智能体进度弹窗关闭
const handleProgressClose = () => {
  // 只允许用户手动关闭，不自动关闭
  // 这样用户可以在完成后查看智能体输出
  store.loading = false  // 关闭弹窗
}

// 处理智能体进度完成
const handleProgressComplete = (guide: any) => {
  // 攻略生成完成，保持弹窗打开让用户查看智能体输出
  console.log('攻略生成完成:', guide)
  // 不设置 loading = false，让弹窗保持打开
}
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.travel-planner-app {
  --color-primary: #0EA5E9;
  --color-primary-dark: #0284C7;
  --color-primary-light: #38BDF8;
  --color-secondary: #38BDF8;
  --color-cta: #F97316;
  --color-background: #F0F9FF;
  --color-text-primary: #0C4A6E;
  --color-text-secondary: #64748B;
  --color-success: #10B981;
  --color-white: #FFFFFF;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-soft: 0 2px 8px rgba(14, 165, 233, 0.15);

  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-primary) 0%, #6366F1 100%);
  font-family: 'Jost', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ==================== */
/* Progress Bar          */
/* ==================== */
.progress-bar {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 1.25rem 0;
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-container {
  max-width: 768px;
  margin: 0 auto;
  position: relative;
  padding: 0 1rem;
}

.steps {
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.6;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step:hover:not(.active):not(.completed) {
  opacity: 0.8;
  transform: translateY(-2px);
}

.step.active {
  opacity: 1;
}

.step.completed {
  opacity: 1;
  cursor: pointer;
}

.step.completed:hover {
  transform: translateY(-2px);
}

.step-number {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-white);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.step.active .step-number {
  background: var(--color-white);
  color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.3), var(--shadow-md);
  transform: scale(1.1);
}

.step.completed .step-number {
  background: var(--color-success);
  box-shadow: var(--shadow-soft);
}

.step-label {
  font-size: 0.75rem;
  color: var(--color-white);
  font-weight: 500;
  text-align: center;
  letter-spacing: 0.025em;
}

.progress-line {
  position: absolute;
  top: 22px;
  left: calc(22px + 1rem);
  right: calc(22px + 1rem);
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-success) 0%, var(--color-primary) 100%);
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

/* ==================== */
/* Loading Overlay       */
/* ==================== */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-content {
  text-align: center;
  color: var(--color-white);
}

.loading-spinner {
  margin-bottom: 1.5rem;
}

.loading-spinner .el-icon {
  color: var(--color-primary);
  filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.6));
}

.loading-text {
  margin: 0 0 1.5rem 0;
  font-size: 1.125rem;
  font-weight: 500;
  letter-spacing: 0.025em;
}

.loading-progress-wrapper {
  width: 280px;
  margin: 0 auto;
}

.loading-progress-wrapper :deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.loading-progress-wrapper :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--color-success) 0%, var(--color-primary) 100%);
  border-radius: 2px;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

/* ==================== */
/* Page Content          */
/* ==================== */
.page-content {
  padding: 1.5rem 1rem 6rem;
  max-width: 1280px;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .page-content {
    padding: 2rem 2rem 6rem;
  }
}

/* ==================== */
/* Bottom Navigation      */
/* ==================== */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  z-index: 40;
}

.nav-btn {
  min-width: 120px;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.nav-btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  color: var(--color-white) !important;
}

.nav-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
}

.nav-btn-cta {
  background: linear-gradient(135deg, var(--color-cta) 0%, #EA580C 100%);
  border: none;
  color: var(--color-white) !important;
}

.nav-btn-cta:hover:not(:disabled) {
  background: linear-gradient(135deg, #FB923C 0%, var(--color-cta) 100%);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
}

.ml-1 {
  margin-left: 0.25rem;
}

/* ==================== */
/* Transitions            */
/* ==================== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* ==================== */
/* Responsive             */
/* ==================== */
@media (max-width: 640px) {
  .step-label {
    display: none;
  }

  .bottom-nav {
    padding: 0.75rem 1rem;
  }

  .nav-btn {
    min-width: 100px;
    font-size: 0.875rem;
    padding: 0 1rem;
  }

  .nav-btn .el-icon {
    margin: 0 !important;
  }

  .nav-btn span:not(.el-icon) {
    display: none;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .step,
  .step-number,
  .progress-fill,
  .nav-btn,
  .fade-enter-active,
  .fade-leave-active,
  .slide-fade-enter-active,
  .slide-fade-leave-active {
    transition: none;
  }

  .step:hover,
  .nav-btn:hover,
  .step.completed:hover {
    transform: none;
  }
}
</style>
