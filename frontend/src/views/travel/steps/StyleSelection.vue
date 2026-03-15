<template>
  <div class="style-selection">
    <div class="container">
      <div class="header">
        <div class="header-badge">
          <el-icon><MagicStick /></el-icon>
          <span>个性化方案</span>
        </div>
        <h2 class="title">选择您的旅行风格</h2>
        <p class="subtitle">为 {{ destination }} 设计专属方案</p>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <el-icon class="is-loading" :size="50"><Loading /></el-icon>
        </div>
        <p class="loading-text">正在为您生成个性化方案...</p>
        <div class="loading-progress-wrapper">
          <el-progress :percentage="75" :show-text="false" :stroke-width="3" />
        </div>
      </div>

      <div v-else class="styles-grid">
        <div
          v-for="style in styleProposals"
          :key="style.style_type"
          class="style-card"
          :class="{ selected: selectedStyle === style.style_type }"
          @click="handleSelect(style.style_type)"
        >
          <div class="style-header" :class="`style-${style.style_type}`">
            <div class="style-icon">
              <el-icon><component :is="getStyleIcon(style.style_type)" /></el-icon>
            </div>
            <div class="style-name">{{ style.style_name }}</div>
            <div class="style-check" v-if="selectedStyle === style.style_type">
              <el-icon><Check /></el-icon>
            </div>
          </div>

          <div class="style-content">
            <div class="style-description">{{ style.style_description }}</div>

            <div class="style-meta">
              <div class="meta-item">
                <el-icon class="meta-icon"><Timer /></el-icon>
                <span class="meta-label">节奏</span>
                <span class="meta-value">{{ style.daily_pace }}</span>
              </div>
              <div class="meta-item">
                <el-icon class="meta-icon"><TrendCharts /></el-icon>
                <span class="meta-label">强度</span>
                <div class="intensity-bar">
                  <div
                    v-for="i in 5"
                    :key="i"
                    class="intensity-dot"
                    :class="{ active: i <= style.intensity_level }"
                  ></div>
                </div>
              </div>
            </div>

            <div class="style-preview">
              <div class="preview-title">
                <el-icon><View /></el-icon>
                行程预览
              </div>
              <div class="preview-list">
                <div
                  v-for="(preview, index) in style.preview_itinerary.slice(0, 2)"
                  :key="index"
                  class="preview-item"
                >
                  <span class="preview-day">D{{ preview.day }}</span>
                  <span class="preview-attractions">{{ preview.attractions.join(' · ') }}</span>
                </div>
              </div>
            </div>

            <div class="style-footer">
              <div class="style-price">
                <span class="price-label">预算</span>
                <span class="price-value">¥{{ style.estimated_cost }}</span>
              </div>
              <div class="style-best-for">
                <el-icon class="best-icon"><User /></el-icon>
                <span class="best-value">{{ style.best_for }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions">
        <el-button size="large" class="nav-btn" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button
          type="primary"
          size="large"
          class="nav-btn nav-btn-primary"
          :disabled="!selectedStyle"
          @click="handleContinue"
        >
          生成攻略
          <el-icon class="ml-1"><MagicStick /></el-icon>
        </el-button>
      </div>

      <!-- Agent Outputs Section -->
      <div v-if="stepResults.length > 0" class="agent-outputs-section">
        <div class="agent-outputs-header">
          <h3 class="agent-outputs-title">
            <el-icon><View /></el-icon>
            智能体设计过程
          </h3>
          <p class="agent-outputs-subtitle">点击展开查看每个智能体的详细设计方案</p>
        </div>
        <div class="agent-outputs-list">
          <div
            v-for="(result, index) in stepResults"
            :key="index"
            class="agent-output-item"
            :class="{ expanded: result.expanded }"
          >
            <div class="agent-output-header" @click="toggleExpand(result)">
              <div class="agent-output-info">
                <span class="agent-badge">{{ formatAgentName(result.agent) }}</span>
                <span class="agent-step-title">{{ result.title }}</span>
              </div>
              <el-icon class="expand-icon" :class="{ rotated: result.expanded }">
                <ArrowDown />
              </el-icon>
            </div>
            <div v-if="result.expanded" class="agent-output-content">
              <!-- 优先显示LLM描述 -->
              <div v-if="result.llm_description" class="agent-llm-description">
                <div class="llm-label">📝 智能体设计方案</div>
                <div class="llm-text">{{ result.llm_description }}</div>
              </div>

              <!-- 显示结构化数据 -->
              <div v-if="result.data && Object.keys(result.data).length > 0" class="agent-output-data">
                <div class="data-label">📊 方案详情</div>
                <pre>{{ formatAgentData(result.data) }}</pre>
              </div>

              <div class="agent-output-time">
                完成时间: {{ formatTime(result.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  Loading,
  ArrowLeft,
  MagicStick,
  Check,
  Timer,
  TrendCharts,
  View,
  User,
  Sunny,
  Moon,
  Compass,
  Camera,
  Flag,
  ArrowDown
} from '@element-plus/icons-vue'
import { useStagedPlannerStore } from '@/stores/stagedPlanner'
import { formatAgentName } from '@/utils/agentNames'

const props = defineProps<{
  destination: string
  styles: any[]
}>()

const emit = defineEmits<{
  select: [style: string]
  back: []
}>()

const store = useStagedPlannerStore()
const loading = ref(true)
const selectedStyle = ref<string | null>(null)

const styleProposals = ref(props.styles)

// Get step results from store
const stepResults = computed(() => store.stepResults)

// Toggle expand for agent output
const toggleExpand = (result: any) => {
  result.expanded = !result.expanded
}

// Format agent data for display
const formatAgentData = (data: any) => {
  if (typeof data === 'string') {
    return data
  }
  return JSON.stringify(data, null, 2)
}

// Format timestamp
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

// 监听props.styles的变化，当有数据时关闭loading
import { watch } from 'vue'
watch(() => props.styles, (newStyles) => {
  if (newStyles && newStyles.length > 0) {
    styleProposals.value = newStyles
    loading.value = false
  }
}, { immediate: true })

const getStyleIcon = (styleType: string) => {
  const iconMap: Record<string, any> = {
    leisure: Sunny,
    adventure: Compass,
    culture: Camera,
    classic: Flag,
    relax: Moon
  }
  return iconMap[styleType] || Compass
}

const handleSelect = (styleType: string) => {
  selectedStyle.value = styleType
}

const handleContinue = () => {
  if (selectedStyle.value) {
    emit('select', selectedStyle.value)
  }
}

const handleBack = () => {
  emit('back')
}
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.style-selection {
  --color-primary: #0EA5E9;
  --color-primary-dark: #0284C7;
  --color-primary-light: #38BDF8;
  --color-cta: #F97316;
  --color-success: #10B981;
  --color-white: #FFFFFF;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-soft: 0 8px 30px rgba(14, 165, 233, 0.2);

  padding: 2rem 0 6rem;
}

/* ==================== */
/* Container              */
/* ==================== */
.container {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeInUp 0.4s ease-out;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 9999px;
  color: var(--color-white);
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.title {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-white);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.125rem;
}

/* ==================== */
/* Loading                */
/* ==================== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
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
/* Styles Grid            */
/* ==================== */
.styles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.style-card {
  background: var(--color-white);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-lg);
  border: 3px solid transparent;
  animation: fadeInUp 0.4s ease-out both;
}

.style-card:nth-child(1) { animation-delay: 0.05s; }
.style-card:nth-child(2) { animation-delay: 0.1s; }
.style-card:nth-child(3) { animation-delay: 0.15s; }
.style-card:nth-child(4) { animation-delay: 0.2s; }

.style-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-xl), var(--shadow-soft);
}

.style-card.selected {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-xl), 0 0 0 4px rgba(14, 165, 233, 0.2);
  transform: scale(1.02);
}

/* ==================== */
/* Style Header           */
/* ==================== */
.style-header {
  position: relative;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.style-header.style-leisure {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
}

.style-header.style-adventure {
  background: linear-gradient(135deg, #FED7AA 0%, #FCA5A5 100%);
}

.style-header.style-culture {
  background: linear-gradient(135deg, #E9D5FF 0%, #C4B5FD 100%);
}

.style-header.style-classic {
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
}

.style-header.style-relax {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
}

.style-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: #0F172A;
  box-shadow: var(--shadow-sm);
}

.style-name {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0F172A;
}

.style-check {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  background: var(--color-success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  animation: scaleIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ==================== */
/* Style Content          */
/* ==================== */
.style-content {
  padding: 1.5rem;
}

.style-description {
  text-align: center;
  color: #64748B;
  margin-bottom: 1rem;
  line-height: 1.6;
  font-size: 0.9375rem;
}

/* ==================== */
/* Style Meta             */
/* ==================== */
.style-meta {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #F0F9FF;
  border-radius: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
}

.meta-icon {
  font-size: 1rem;
  color: var(--color-primary);
}

.meta-label {
  font-size: 0.75rem;
  color: #64748B;
  font-weight: 500;
}

.meta-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0F172A;
}

.intensity-bar {
  display: flex;
  gap: 0.25rem;
}

.intensity-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #E2E8F0;
  transition: background 0.2s ease;
}

.intensity-dot.active {
  background: var(--color-primary);
}

/* ==================== */
/* Style Preview          */
/* ==================== */
.style-preview {
  margin-bottom: 1rem;
}

.preview-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.625rem;
}

.preview-title .el-icon {
  color: var(--color-cta);
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.5rem;
  background: #F8FAFC;
  border-radius: 8px;
}

.preview-day {
  font-weight: 600;
  color: var(--color-primary);
  white-space: nowrap;
}

.preview-attractions {
  color: #64748B;
}

/* ==================== */
/* Style Footer           */
/* ==================== */
.style-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #E2E8F0;
}

.style-price {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.price-label {
  font-size: 0.75rem;
  color: #64748B;
}

.price-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
}

.style-best-for {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
  background: #FEF3C7;
  border-radius: 9999px;
  color: #92400E;
  font-weight: 500;
}

.best-icon {
  font-size: 1rem;
}

/* ==================== */
/* Actions                */
/* ==================== */
.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.nav-btn {
  min-width: 120px;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--color-white) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn-primary {
  background: linear-gradient(135deg, var(--color-cta) 0%, #EA580C 100%);
  border: none;
}

.nav-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #FB923C 0%, var(--color-cta) 100%);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
}

.ml-1 {
  margin-left: 0.25rem;
}

/* ==================== */
/* Animations             */
/* ==================== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== */
/* Responsive             */
/* ==================== */
@media (max-width: 640px) {
  .styles-grid {
    grid-template-columns: 1fr;
  }

  .style-meta {
    flex-direction: row;
    gap: 1rem;
  }

  .actions {
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
  }

  .style-footer {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .style-card,
  .style-check,
  .nav-btn,
  .intensity-dot {
    animation: none;
    transition: none;
  }

  .style-card:hover,
  .nav-btn:hover {
    transform: none;
  }
}

/* ==================== */
/* Agent Outputs Section */
/* ==================== */
.agent-outputs-section {
  margin-top: 2rem;
  margin-bottom: 2rem;
}

.agent-outputs-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.agent-outputs-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: 'Bodoni Moda', serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-white);
  margin-bottom: 0.5rem;
}

.agent-outputs-title .el-icon {
  color: var(--color-primary);
  font-size: 1.5rem;
}

.agent-outputs-subtitle {
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.875rem;
}

.agent-outputs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.agent-output-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}

.agent-output-item:hover {
  background: rgba(255, 255, 255, 0.15);
}

.agent-output-item.expanded {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.agent-output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  cursor: pointer;
  user-select: none;
}

.agent-output-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.agent-badge {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, var(--color-cta) 0%, #EA580C 100%);
  color: var(--color-white);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.agent-step-title {
  color: var(--color-white);
  font-size: 0.9rem;
  font-weight: 500;
}

.expand-icon {
  color: var(--color-white);
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.agent-output-content {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* LLM描述样式 */
.agent-llm-description {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(192, 132, 252, 0.1) 100%);
  border-radius: 12px;
  border-left: 4px solid rgba(168, 85, 247, 0.8);
}

.agent-llm-description .llm-label {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 700;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.agent-llm-description .llm-text {
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9rem;
}

.agent-output-data {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.agent-output-data .data-label {
  color: rgba(192, 132, 252, 0.9);
  font-weight: 600;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.agent-output-data pre {
  margin: 0;
  color: #E2E8F0;
  font-size: 0.8125rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.agent-output-time {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  text-align: right;
}

/* Custom scrollbar for agent output data */
.agent-output-data::-webkit-scrollbar {
  width: 6px;
}

.agent-output-data::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.agent-output-data::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.agent-output-data::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.4);
}
</style>
