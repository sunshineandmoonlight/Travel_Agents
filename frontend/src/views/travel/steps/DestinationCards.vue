<template>
  <div class="destination-cards">
    <div class="container">
      <div class="header">
        <h2 class="title">为您推荐的目的地</h2>
        <p class="subtitle" v-if="userPortrait && userPortrait.description">{{ userPortrait.description }}</p>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <el-icon class="is-loading" :size="50"><Loading /></el-icon>
        </div>
        <p class="loading-text">正在为您分析最佳目的地...</p>
        <div class="loading-progress-wrapper">
          <el-progress :percentage="60" :show-text="false" :stroke-width="3" />
        </div>
      </div>

      <div v-else class="cards-grid">
        <div
          v-for="(dest, index) in destinationsWithImages"
          :key="dest.destination"
          class="destination-card"
          :class="{ selected: selectedIndex === index }"
          @click="handleSelect(dest.destination, index)"
        >
          <div class="card-badge">匹配度 {{ dest.match_score }}%</div>
          <div class="card-image">
            <img
              :src="dest.imageUrl"
              :alt="dest.destination"
              @error="handleImageError(dest, $event)"
              @load="handleImageLoad(dest)"
              :class="{ 'image-loaded': !dest.imageLoading }"
            >
            <div class="card-overlay"></div>
          </div>
          <div class="card-content">
            <h3 class="card-title">{{ dest.destination }}</h3>
            <p class="card-reason">{{ dest.recommendation_reason }}</p>

            <div class="card-info">
              <div class="info-item">
                <el-icon class="info-icon budget"><Wallet /></el-icon>
                <span>¥{{ dest.estimated_budget.per_person }}/人起</span>
              </div>
              <div class="info-item">
                <el-icon class="info-icon weather"><Sunny /></el-icon>
                <span>{{ dest.best_season }}</span>
              </div>
            </div>

            <div class="card-tags">
              <span
                v-for="tag in dest.suitable_for.slice(0, 3)"
                :key="tag"
                class="tag"
              >{{ tag }}</span>
            </div>

            <div class="card-highlights">
              <div class="highlights-title">
                <el-icon><Star /></el-icon>
                亮点
              </div>
              <div class="highlights-list">
                <span v-for="highlight in dest.highlights.slice(0, 3)" :key="highlight" class="highlight-item">
                  {{ highlight }}
                </span>
              </div>
            </div>

            <div class="card-check" v-if="selectedIndex === index">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Outputs Section -->
      <div v-if="stepResults.length > 0" class="agent-outputs-section">
        <div class="agent-outputs-header">
          <h3 class="agent-outputs-title">
            <el-icon><View /></el-icon>
            智能体分析过程
          </h3>
          <p class="agent-outputs-subtitle">点击展开查看每个智能体的详细分析结果</p>
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
                <div class="llm-label">📝 智能体分析</div>
                <div class="llm-text">{{ result.llm_description }}</div>
              </div>

              <!-- 显示结构化数据 -->
              <div v-if="result.data && Object.keys(result.data).length > 0" class="agent-output-data">
                <div class="data-label">📊 详细数据</div>
                <pre>{{ formatAgentData(result.data) }}</pre>
              </div>

              <div class="agent-output-time">
                完成时间: {{ formatTime(result.timestamp) }}
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
          v-if="selectedIndex !== null"
          type="primary"
          size="large"
          class="nav-btn nav-btn-primary"
          @click="handleConfirm"
          :loading="confirming"
        >
          确认选择
          <el-icon class="ml-1"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { Loading, ArrowLeft, ArrowRight, Wallet, Sunny, Star, Check, View, ArrowDown } from '@element-plus/icons-vue'
import { useStagedPlannerStore } from '@/stores/stagedPlanner'
import { formatAgentName } from '@/utils/agentNames'
import { getGuideImageUrlAsync } from '@/api/travel/guides'

const props = defineProps<{
  destinations: any[]
  userPortrait: any
}>()

const emit = defineEmits<{
  select: [destination: string]
  back: []
}>()

const store = useStagedPlannerStore()
const loading = computed(() => store.stepLoading)
const confirming = ref(false)
const selectedIndex = ref<number | null>(null)

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

// 为每个目的地添加图片URL
interface DestinationWithImage {
  destination: string
  imageUrl: string
  imageLoading: boolean
  imageError: boolean
  [key: string]: any
}

const destinationsWithImages = ref<DestinationWithImage[]>([])

// 预设的可靠图片URL（硬编码，避免后端API调用延迟）
const getPresetImage = (destination: string): string => {
  const presetImages: Record<string, string> = {
    '杭州': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=600&q=80',
    '九寨沟': 'https://images.unsplash.com/photo-1544197150-b9a2ce2bb4dd?w=600&q=80',
    '张家界': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=600&q=80',
    '桂林': 'https://images.unsplash.com/photo-1557424447-218bcce82d2d?w=600&q=80',
    '三亚': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=600&q=80',
    '北京': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=600&q=80',
    '成都': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80',
    '西安': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=600&q=80',
    '厦门': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    '上海': 'https://images.unsplash.com/photo-1548948485-9b29adda8fad?w=600&q=80',
    '云南': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=600&q=80',
    '苏州': 'https://images.unsplash.com/photo-1543085888-4f1b0bb73d6a?w=600&q=80',
    '丽江': 'https://images.unsplash.com/photo-1548044672-797fa481224d?w=600&q=80',
    '大理': 'https://images.unsplash.com/photo-1543085888-4f1b0bb73d6a?w=600&q=80',
    '青海': 'https://images.unsplash.com/photo-1548044672-797fa481224d?w=600&q=80',
    '新疆': 'https://images.unsplash.com/photo-1469854529868-34159c27506d?w=600&q=80',
    '西藏': 'https://images.unsplash.com/photo-1548044672-797fa481224d?w=600&q=80',
    '日本': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80',
    '泰国': 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=600&q=80',
    '新加坡': 'https://images.unsplash.com/photo-1525625296488-f6bc9439556f?w=600&q=80',
    '韩国': 'https://images.unsplash.com/photo-1528150298250-299893f5bb60?w=600&q=80',
    '马来西亚': 'https://images.unsplash.com/photo-1512453973156-27e7a38db048?w=600&q=80',
    '越南': 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=600&q=80',
    '美国': 'https://images.unsplash.com/photo-1501598866897-766ffaef2c54a?w=600&q=80',
    '英国': 'https://images.unsplash.com/photo-1513635269975-9cf5f38b90e6?w=600&q=80',
    '法国': 'https://images.unsplash.com/photo-1502602814073-475a3cdb33f6?w=600&q=80',
    '意大利': 'https://images.unsplash.com/photo-1523453122-9a4e12851895?w=600&q=80',
    '瑞士': 'https://images.unsplash.com/photo-1530276462442-1c477079c8c1?w=600&q=80',
    '澳大利亚': 'https://images.unsplash.com/photo-1523482530692-6bae4cb3ff0e?w=600&q=80',
    '新西兰': 'https://images.unsplash.com/photo-1507699622106-6e7c8e4e1d78?w=600&q=80'
  }
  return presetImages[destination] || presetImages['杭州']
}

// 获取目的地图片（优化版：先显示内容，图片异步加载）
const loadDestinationImages = async () => {
  const destinations = props.destinations || []

  // 立即显示目的地卡片，使用预设图片
  destinationsWithImages.value = destinations.map((dest: any) => ({
    ...dest,
    imageUrl: getPresetImage(dest.destination),  // 先用预设图片
    imageLoading: true,  // 标记正在加载真实图片
    imageError: false
  }))

  // 异步加载真实图片（不阻塞显示）
  loadRealImagesAsync(destinations)
}

// 异步加载真实图片
const loadRealImagesAsync = async (destinations: any[]) => {
  for (let i = 0; i < destinations.length; i++) {
    const dest = destinations[i]
    try {
      // 通过后端API获取地点相关的图片URL
      const imageUrl = await getGuideImageUrlAsync(dest.destination, 600, 400)

      // 更新图片URL
      if (destinationsWithImages.value[i]) {
        destinationsWithImages.value[i].imageUrl = imageUrl
        destinationsWithImages.value[i].imageLoading = false
      }
    } catch (error) {
      console.warn(`获取${dest.destination}图片失败，保留预设图片:`, error)
      // 保持预设图片，标记为非加载状态
      if (destinationsWithImages.value[i]) {
        destinationsWithImages.value[i].imageLoading = false
      }
    }
  }
}

// 图片加载失败处理
const handleImageError = (dest: DestinationWithImage, event: Event) => {
  console.warn(`图片加载失败: ${dest.destination}`)
  // 使用预设图片作为后备
  dest.imageUrl = getPresetImage(dest.destination)
  dest.imageError = true
}

// 图片加载成功处理
const handleImageLoad = (dest: DestinationWithImage) => {
  dest.imageLoading = false
}

const handleSelect = (destination: string, index: number) => {
  selectedIndex.value = index
  // 不再自动跳转，让用户点击确认按钮
}

const handleConfirm = () => {
  if (selectedIndex.value === null) return

  confirming.value = true
  const destination = props.destinations[selectedIndex.value].destination

  // 延迟一点以便用户看到按钮的加载状态
  setTimeout(() => {
    emit('select', destination)
  }, 300)
}

const handleBack = () => {
  emit('back')
}

onMounted(() => {
  // 立即初始化，先显示卡片和预设图片
  loadDestinationImages()

  // 立即显示，不延迟
  loading.value = false
})

// 监听destinations变化
watch(() => props.destinations, (newDestinations) => {
  if (newDestinations && newDestinations.length > 0) {
    console.log('[目的地卡片] 检测到新目的地数据，重新加载')
    loadDestinationImages()
  }
}, { deep: true, immediate: false })
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.destination-cards {
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
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeInUp 0.4s ease-out;
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
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
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
/* Cards Grid             */
/* ==================== */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.destination-card {
  position: relative;
  background: var(--color-white);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.4s ease-out both;
}

.destination-card:nth-child(1) { animation-delay: 0.05s; }
.destination-card:nth-child(2) { animation-delay: 0.1s; }
.destination-card:nth-child(3) { animation-delay: 0.15s; }
.destination-card:nth-child(4) { animation-delay: 0.2s; }

.destination-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl), var(--shadow-soft);
}

.destination-card.selected {
  transform: scale(1.02);
  box-shadow: var(--shadow-xl), 0 0 0 4px var(--color-primary);
}

/* ==================== */
/* Card Badge             */
/* ==================== */
.card-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
  z-index: 2;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
}

/* ==================== */
/* Card Image             */
/* ==================== */
.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;
}

.card-image img.image-loaded {
  opacity: 1;
}

.destination-card:hover .card-image img.image-loaded {
  transform: scale(1.08);
}

.image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgba(255, 255, 255, 0.8);
  font-size: 2rem;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.1) 100%);
  pointer-events: none;
}

.image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--color-primary);
  font-size: 2rem;
}

/* ==================== */
/* Card Content           */
/* ==================== */
.card-content {
  padding: 1.5rem;
  position: relative;
}

.card-check {
  position: absolute;
  top: -20px;
  right: 1.5rem;
  width: 40px;
  height: 40px;
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

.card-title {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 0.5rem;
}

.card-reason {
  color: #64748B;
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ==================== */
/* Card Info              */
/* ==================== */
.card-info {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: #F0F9FF;
  border-radius: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #475569;
  font-weight: 500;
}

.info-icon {
  font-size: 1.125rem;
}

.info-icon.budget {
  color: #059669;
}

.info-icon.weather {
  color: #F97316;
}

/* ==================== */
/* Card Tags              */
/* ==================== */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: var(--color-primary);
  font-weight: 500;
}

/* ==================== */
/* Card Highlights        */
/* ==================== */
.card-highlights {
  border-top: 1px solid #E2E8F0;
  padding-top: 1rem;
}

.highlights-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.625rem;
}

.highlights-title .el-icon {
  color: var(--color-cta);
  font-size: 1rem;
}

.highlights-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.highlight-item {
  font-size: 0.8125rem;
  color: #64748B;
}

.highlight-item::after {
  content: "·";
  margin-left: 0.5rem;
  color: #CBD5E1;
}

.highlight-item:last-child::after {
  content: "";
}

/* ==================== */
/* Actions                */
/* ==================== */
.actions {
  display: flex;
  justify-content: center;
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

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nav-btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-color: transparent;
}

.nav-btn-primary:hover {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
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
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .card-info {
    flex-direction: column;
    gap: 0.75rem;
  }

  .nav-btn {
    width: 100%;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .destination-card,
  .card-image img,
  .nav-btn,
  .card-check {
    animation: none;
    transition: none;
  }

  .destination-card:hover,
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
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
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
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(56, 189, 248, 0.1) 100%);
  border-radius: 12px;
  border-left: 4px solid rgba(14, 165, 233, 0.8);
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
  color: rgba(14, 165, 233, 0.9);
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
