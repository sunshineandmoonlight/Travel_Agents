<template>
  <div class="travel-home">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-background">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
        <div class="gradient-orb orb-3"></div>
      </div>

      <div class="hero-container">
        <div class="hero-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          AI 智能规划
        </div>

        <h1 class="hero-title">
          探索世界
          <span class="title-accent">智能规划</span>
        </h1>

        <p class="hero-description">
          AI 驱动的个性化旅行方案，让每一次旅行都成为美好回忆
        </p>

        <div class="hero-actions">
          <button class="btn-primary" @click="$router.push('/travel/planner')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            开始规划行程
          </button>
          <button class="btn-secondary" @click="$router.push('/travel/intelligence')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <path d="M12 6v6l4 2" stroke-width="2" stroke-linecap="round"/>
            </svg>
            探索目的地
          </button>
        </div>

        <!-- Stats -->
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-value">12+</div>
            <div class="stat-label">智能体数量</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">3阶段</div>
            <div class="stat-label">渐进式设计</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">LangGraph</div>
            <div class="stat-label">多智能体编排</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-container">
        <h2 class="section-title">智能旅行规划系统</h2>
        <p class="section-subtitle">为您提供全方位的旅行规划服务</p>

        <div class="features-grid">
          <div class="feature-card" @click="$router.push('/travel/planner')">
            <div class="feature-icon-wrapper primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>AI 行程规划</h3>
            <p>智能分析您的需求，自动生成个性化旅行方案</p>
          </div>

          <div class="feature-card" @click="$router.push('/travel/intelligence')">
            <div class="feature-icon-wrapper success">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>目的地情报</h3>
            <p>获取实时天气、景点推荐、本地新闻等资讯</p>
          </div>

          <div class="feature-card" @click="$router.push('/travel/guides')">
            <div class="feature-icon-wrapper warning">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>我的攻略</h3>
            <p>查看和管理您的旅行计划，导出精美攻略</p>
          </div>
        </div>
      </div>
    </section>

    <!-- My Guides Section -->
    <section class="guides-section">
      <div class="section-container">
        <div class="section-header">
          <div class="header-left">
            <h2 class="section-title">我的攻略</h2>
            <p class="section-subtitle">查看您的旅行计划</p>
          </div>
          <el-button link type="primary" @click="$router.push('/travel/guides')">
            查看全部
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </el-button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="guides-grid">
          <div v-for="i in 3" :key="i" class="guide-card skeleton">
            <div class="guide-image-skeleton"></div>
            <div class="guide-content">
              <div class="skeleton-line skeleton-title"></div>
              <div class="skeleton-line skeleton-meta"></div>
              <div class="skeleton-tags">
                <div class="skeleton-tag"></div>
                <div class="skeleton-tag"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Guides Grid -->
        <div v-else-if="myGuides.length > 0" class="guides-grid">
          <div
            v-for="guide in myGuides"
            :key="guide.id"
            class="guide-card"
            @click="$router.push('/travel/guides')"
          >
            <div class="guide-image">
              <img
                :src="guide.image"
                :alt="guide.destination"
                @load="onImageLoad(guide.id)"
                @error="onImageError(guide.id, $event)"
                loading="lazy"
              />
              <div class="guide-overlay">
                <span class="guide-days">{{ guide.days }}天{{ guide.nights }}夜</span>
                <span class="guide-status" :class="`status-${guide.statusType}`">{{ guide.status }}</span>
              </div>
            </div>
            <div class="guide-content">
              <h3>{{ guide.title }}</h3>
              <div class="guide-meta">
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                    <path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ guide.destination }}
                </span>
                <span class="meta-item budget-type">{{ guide.budgetType }}</span>
                <span class="meta-item">{{ guide.date }}</span>
              </div>
              <div class="guide-tags" v-if="guide.tags.length">
                <span v-for="tag in guide.tags.slice(0, 3)" :key="tag" class="guide-tag">#{{ tag }}</span>
              </div>
              <div class="guide-footer">
                <span class="guide-stats">
                  <span class="stat">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    {{ formatNumber(guide.views) }}
                  </span>
                  <span class="stat">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                      <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    {{ guide.likes }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>还没有攻略</h3>
          <p>创建您的第一个旅行计划吧</p>
          <button class="btn-primary" @click="$router.push('/travel/planner')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            立即创建
          </button>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-container">
        <div class="cta-content">
          <h2>开始您的智能旅行规划</h2>
          <p>AI 辅助规划，让每一次旅行都成为美好回忆</p>
          <button class="cta-btn" @click="$router.push('/travel/planner')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            立即开始
          </button>
        </div>
        <div class="cta-visual">
          <div class="visual-card card-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="visual-card card-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="visual-card card-3">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- 预加载进度提示 -->
    <div v-if="isPreloading" class="preload-toast">
      <div class="toast-content">
        <div class="toast-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="20" height="20">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="toast-text">
          <div class="toast-title">预加载热门目的地图片</div>
          <div class="toast-progress">
            {{ preloadProgress.loaded }}/{{ preloadProgress.total }}
            <span v-if="preloadProgress.current"> - {{ preloadProgress.current }}</span>
          </div>
        </div>
      </div>
      <div class="toast-bar" :style="{ width: (preloadProgress.loaded / preloadProgress.total * 100) + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserGuides, getPublicGuides, type GuideListItem, getGuideImageUrlAsync } from '@/api/travel/guides'
import { imagePreloaderService } from '@/api/travel/images'

const router = useRouter()

// 默认封面图片
const defaultGuideImage = 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop'

// 我的攻略列表（从API加载）
const myGuides = ref<any[]>([])
const isLoading = ref(true)
const imageLoadStates = ref<Record<string, boolean>>({})
const imageRetryTimers = ref<Record<string, NodeJS.Timeout[]>>({})  // 重试定时器数组（每个guide可能有多个定时器）
const retryCount = ref<Record<string, number>>({})  // 记录重试次数

// 预加载状态
const isPreloading = ref(false)
const preloadProgress = ref({ loaded: 0, total: 0, current: '' })

// 图片重试配置
const RETRY_CONFIG = {
  maxDuration: 10000,  // 最大重试时间：10秒
  interval: 2000,       // 重试间隔：2秒
  maxAttempts: 5        // 最大重试次数
}

// 加载攻略列表
const loadGuides = async () => {
  isLoading.value = true
  try {
    // 使用 demo_user ID 来获取用户自己的攻略
    const userId = 'demo_user'
    const data = await getUserGuides(userId, undefined, 6, 0)
    // 异步获取所有攻略的图片URL
    const guidesWithImages = await Promise.all(data.map(async (guide: any) => {
      // 通过后端API获取地点相关的图片URL
      const imageUrl = await getGuideImageUrlAsync(guide.destination, 600, 400)

      return {
        id: guide.id,
        title: guide.title,
        status: guide.status === 'published' ? '已完成' : '草稿',
        statusType: guide.status === 'published' ? 'completed' : 'draft',
        destination: guide.destination,
        days: guide.total_days,
        nights: guide.total_days - 1,
        budgetType: guide.budget < 1500 ? '经济型' : guide.budget < 3000 ? '舒适型' : '高端型',
        tags: guide.tags || [],
        views: guide.view_count || 0,
        likes: guide.like_count || 0,
        date: formatDate(guide.created_at),
        // 使用后端API返回的URL
        image: imageUrl,
        // 已开始重试（标记为已完成，因为已经使用后端API）
        startedPexelsRetry: true,
        // 重试开始时间
        retryStartTime: 0,
        // 当前正在加载的URL
        currentUrl: imageUrl
      }
    }))
    myGuides.value = guidesWithImages
    console.log('加载我的攻略列表成功:', myGuides.value.length)
  } catch (error) {
    console.error('加载攻略失败:', error)
    myGuides.value = []
  } finally {
    isLoading.value = false
  }
}

// 图片加载成功
const onImageLoad = (guideId: string) => {
  imageLoadStates.value[guideId] = true
  // 清除所有重试定时器
  clearRetryTimers(guideId)
  console.log(`[图片] ${guideId} 加载成功`)
}

// 清除指定guide的所有重试定时器
const clearRetryTimers = (guideId: string) => {
  if (imageRetryTimers.value[guideId]) {
    imageRetryTimers.value[guideId].forEach(timer => clearTimeout(timer))
    delete imageRetryTimers.value[guideId]
  }
  if (retryCount.value[guideId] !== undefined) {
    delete retryCount.value[guideId]
  }
}

// 尝试获取Pexels图片
const tryPexelsImage = async (guide: any, img: HTMLImageElement) => {
  const currentAttempt = (retryCount.value[guide.id] || 0) + 1
  retryCount.value[guide.id] = currentAttempt

  const elapsed = Date.now() - guide.retryStartTime

  console.log(`[图片] ${guide.destination} Pexels重试 ${currentAttempt}/${RETRY_CONFIG.maxAttempts} (${elapsed}ms/${RETRY_CONFIG.maxDuration}ms)`)

  try {
    // 从后端API获取Pexels图片URL
    const pexelsUrl = await getPexelsImageUrl(guide.destination, 600, 400)
    guide.image = pexelsUrl
    guide.currentUrl = pexelsUrl
    img.src = pexelsUrl
    console.log(`[图片] ${guide.destination} Pexels URL: ${pexelsUrl}`)
  } catch (error) {
    console.error(`[图片] ${guide.destination} Pexels重试${currentAttempt}失败:`, error)

    // 检查是否可以继续重试
    if (elapsed < RETRY_CONFIG.maxDuration && currentAttempt < RETRY_CONFIG.maxAttempts) {
      // 安排下一次重试
      const timer = setTimeout(() => {
        tryPexelsImage(guide, img)
      }, RETRY_CONFIG.interval)

      // 保存定时器引用以便清理
      if (!imageRetryTimers.value[guide.id]) {
        imageRetryTimers.value[guide.id] = []
      }
      imageRetryTimers.value[guide.id].push(timer)
    } else {
      // 达到最大重试时间或次数，使用默认图片
      console.log(`[图片] ${guide.destination} 达到最大重试(${elapsed}ms, ${currentAttempt}次)，使用默认图片`)
      img.src = defaultGuideImage
      clearRetryTimers(guide.id)
    }
  }
}

// 图片加载失败 - 持续重试Pexels
const onImageError = async (guideId: string, event: Event) => {
  const guide = myGuides.value.find(g => g.id === guideId)
  if (!guide) return

  const img = event.target as HTMLImageElement

  // 清除之前的重试定时器
  clearRetryTimers(guideId)

  // 如果还没有开始尝试Pexels，开始重试流程
  if (!guide.startedPexelsRetry) {
    guide.startedPexelsRetry = true
    guide.retryStartTime = Date.now()
    retryCount.value[guideId] = 0

    console.log(`[图片] ${guide.destination} Unsplash失败，开始Pexels重试流程...`)

    // 立即尝试第一次
    tryPexelsImage(guide, img)
  } else {
    // Pexels重试也失败了，使用默认图片
    console.log(`[图片] ${guide.destination} Pexels重试流程失败，使用默认图片`)
    img.src = defaultGuideImage
  }
}

// 组件卸载时清理所有定时器
onUnmounted(() => {
  // 清理所有重试定时器
  Object.keys(imageRetryTimers.value).forEach(guideId => {
    clearRetryTimers(guideId)
  })
})

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return `${Math.floor(days / 30)}月前`
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// 预加载热门目的地图片
const preloadPopularDestinations = async () => {
  // 延迟启动预加载，避免影响页面首屏渲染
  await new Promise(resolve => setTimeout(resolve, 2000))

  isPreloading.value = true
  console.log('[预加载] 开始预加载热门目的地图片...')

  try {
    const result = await imagePreloaderService.preloadPopularDestinations(
      20, // 预加载TOP 20热门城市
      (loaded, total, current) => {
        preloadProgress.value = { loaded, total, current }
        console.log(`[预加载] ${loaded}/${total}: ${current}`)
      }
    )

    console.log(`[预加载] 完成! 成功: ${result.success.length}, 失败: ${result.failed.length}`)

    // 显示3秒后隐藏预加载状态
    setTimeout(() => {
      isPreloading.value = false
    }, 3000)

  } catch (error) {
    console.error('[预加载] 失败:', error)
    isPreloading.value = false
  }
}

// 页面加载时获取攻略列表
onMounted(() => {
  loadGuides()
  // 启动预加载（不阻塞页面渲染）
  preloadPopularDestinations()
})
</script>

<style scoped>
.travel-home {
  min-height: 100vh;
  background: #f8fafc;
}

/* Hero Section */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  padding: 100px 24px 80px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float-orb 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
  animation-delay: -7s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 20%;
  animation-delay: -14s;
}

@keyframes float-orb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

.hero-container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  color: white;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 24px;
}

.hero-title {
  font-size: 52px;
  font-weight: 700;
  margin: 0 0 20px 0;
  line-height: 1.1;
}

.title-accent {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 18px;
  opacity: 0.9;
  margin: 0 0 40px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 48px;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: white;
  color: #6366f1;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
}

.btn-primary svg,
.btn-secondary svg {
  width: 20px;
  height: 20px;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

/* Features Section */
.features-section {
  padding: 80px 24px;
  background: white;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  text-align: center;
  margin: 0 0 12px 0;
}

.section-subtitle {
  font-size: 16px;
  color: #6b7280;
  text-align: center;
  margin: 0 0 48px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.feature-card {
  text-align: center;
  padding: 40px 32px;
  border-radius: 20px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  background: white;
}

.feature-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: white;
}

.feature-icon-wrapper.primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.feature-icon-wrapper.success {
  background: linear-gradient(135deg, #10b981, #059669);
}

.feature-icon-wrapper.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.feature-icon-wrapper svg {
  width: 28px;
  height: 28px;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.feature-card p {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* Guides Section */
.guides-section {
  padding: 80px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.header-left .section-title {
  text-align: left;
  margin: 0 0 8px 0;
}

.header-left .section-subtitle {
  text-align: left;
  margin: 0;
}

.guides-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.guide-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
}

.guide-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.guide-image {
  height: 160px;
  position: relative;
  background-color: #f3f4f6;
  overflow: hidden;
}

.guide-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.guide-image-fallback {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.guide-image-fallback::after {
  content: '✈️';
  font-size: 48px;
  opacity: 0.5;
}

.guide-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 16px;
}

.guide-days {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.guide-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.guide-status.status-draft {
  background: rgba(251, 191, 36, 0.9);
  color: #92400e;
}

.guide-status.status-completed {
  background: rgba(52, 211, 153, 0.9);
  color: #065f46;
}

.guide-content {
  padding: 20px;
}

.guide-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.guide-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.meta-item.budget-type {
  padding: 4px 10px;
  background: #f3f4f6;
  border-radius: 8px;
  font-weight: 500;
  color: #4b5563;
}

.guide-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.guide-tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-radius: 8px;
  font-size: 12px;
  color: #4b5563;
  font-weight: 500;
}

.guide-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.guide-stats {
  display: flex;
  gap: 16px;
}

.guide-stats .stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.guide-stats .stat svg {
  width: 14px;
  height: 14px;
}

/* Skeleton Loading */
.guide-card.skeleton {
  pointer-events: none;
}

.guide-image-skeleton {
  height: 160px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-line {
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}

.skeleton-title {
  height: 20px;
  width: 70%;
  margin-bottom: 12px;
}

.skeleton-meta {
  height: 14px;
  width: 50%;
  margin-bottom: 16px;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.skeleton-tag {
  width: 50px;
  height: 24px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 40px;
  background: white;
  border-radius: 20px;
}

.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: #f3f4f6;
  border-radius: 20px;
  margin-bottom: 24px;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
  color: #9ca3af;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 24px 0;
}

.empty-state .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-state .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-state .btn-primary svg {
  width: 18px;
  height: 18px;
}

.empty-state .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}

/* CTA Section */
.cta-section {
  padding: 80px 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.cta-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}

.cta-content h2 {
  font-size: 36px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.cta-content p {
  font-size: 18px;
  color: #6b7280;
  margin: 0 0 32px 0;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
}

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
}

.cta-btn svg {
  width: 20px;
  height: 20px;
}

.cta-visual {
  position: relative;
  height: 280px;
}

.visual-card {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.visual-card svg {
  width: 28px;
  height: 28px;
  color: #6366f1;
}

.card-1 {
  width: 100px;
  height: 100px;
  top: 0;
  left: 20px;
  animation: float-card 6s ease-in-out infinite;
}

.card-2 {
  width: 80px;
  height: 80px;
  top: 70px;
  right: 40px;
  animation: float-card 6s ease-in-out infinite 2s;
}

.card-3 {
  width: 70px;
  height: 70px;
  bottom: 20px;
  left: 50%;
  animation: float-card 6s ease-in-out infinite 4s;
}

@keyframes float-card {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* Responsive */
@media (max-width: 1024px) {
  .hero-title {
    font-size: 40px;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .guides-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cta-container {
    grid-template-columns: 1fr;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-stats {
    flex-wrap: wrap;
    gap: 20px;
  }

  .features-grid,
  .guides-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

/* 预加载提示 */
.preload-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 1000;
  min-width: 280px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.toast-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.toast-text {
  flex: 1;
}

.toast-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.toast-progress {
  font-size: 12px;
  color: #6b7280;
}

.toast-bar {
  height: 3px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  transition: width 0.3s ease;
}

@media (max-width: 768px) {
  .preload-toast {
    bottom: 16px;
    right: 16px;
    left: 16px;
    min-width: auto;
  }
}
</style>
