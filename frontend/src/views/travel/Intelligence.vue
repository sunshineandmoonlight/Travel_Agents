<template>
  <div class="intelligence-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-bg">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><Compass /></el-icon>
          <span>目的地情报</span>
        </div>
        <h1 class="hero-title">探索世界<br><em class="gradient-text">了解目的地</em></h1>
        <p class="hero-subtitle">实时获取目的地新闻、天气、汇率、风险评估</p>

        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索目的地，如：杭州、北京、日本..."
            size="large"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>

        <div class="quick-search">
          <span
            v-for="dest in quickSearchDestinations"
            :key="dest"
            class="quick-tag"
            :class="{ active: searchKeyword === dest }"
            @click="quickSearch(dest)"
          >
            {{ dest }}
          </span>
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在获取目的地情报...</p>
    </div>

    <!-- Intelligence Content -->
    <div v-else-if="intelligence" class="content-section">
      <!-- Overview Card -->
      <div class="overview-card">
        <div class="overview-header">
          <div>
            <h2 class="destination-name">{{ intelligence.destination }}</h2>
            <p class="destination-meta">
              <el-icon><Clock /></el-icon>
              {{ formatDate(intelligence.generated_at) }} 更新
              <span class="api-source" v-if="apiSources">
                | 数据来源: {{ getSourceLabel(intelligence.weather?.source) }}、{{ getSourceLabel('exchange') }}
              </span>
            </p>
          </div>
        </div>

        <!-- 实时状态栏 -->
        <div class="status-bar">
          <div class="status-item weather" v-if="intelligence.weather?.current">
            <span class="status-icon">{{ getWeatherIcon(intelligence.weather.current.weather) }}</span>
            <span class="status-value">{{ intelligence.weather.current.temperature }} {{ intelligence.weather.current.weather }}</span>
          </div>
          <div class="status-item risk">
            <span class="status-icon">{{ getRiskIcon(intelligence.risk_assessment?.risk_level) }}</span>
            <span class="status-value">{{ getRiskLabel(intelligence.risk_assessment?.risk_level) }}</span>
          </div>
          <div class="status-item exchange" v-if="intelligence.exchange_rate?.available">
            <span class="status-icon">💴</span>
            <span class="status-value">1{{ getCurrencySymbol(intelligence.exchange_rate.from) }}={{ intelligence.exchange_rate.rate }}{{ getCurrencySymbol(intelligence.exchange_rate.to) }}</span>
          </div>
          <div class="status-item updated">
            <span class="status-icon">🕐</span>
            <span class="status-value">实时数据</span>
          </div>
        </div>
      </div>

      <!-- 主内容网格 -->
      <div class="bento-grid">
        <!-- 天气卡片 -->
        <div class="bento-card weather-card">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon weather">
                <span>{{ getWeatherIcon(intelligence.weather?.current?.weather) }}</span>
              </div>
              <h3>天气预报</h3>
            </div>
          </div>
          <div class="weather-content" v-if="intelligence.weather">
            <div class="current-weather">
              <div class="current-temp">{{ intelligence.weather.current?.temperature }}</div>
              <div class="current-desc">{{ intelligence.weather.current?.weather }}</div>
              <div class="current-detail">{{ intelligence.weather.current?.wind }} | {{ intelligence.weather.current?.humidity }}</div>
            </div>
            <div class="weather-forecast" v-if="intelligence.weather.forecast">
              <div v-for="(day, index) in intelligence.weather.forecast.slice(0, 3)" :key="index" class="forecast-item">
                <div class="forecast-date">
                  <div class="forecast-week">{{ day.week }}</div>
                  <div class="forecast-day">{{ day.date.split('-')[2] }}日</div>
                </div>
                <div class="forecast-temps">
                  <span class="forecast-icon">{{ getWeatherIcon(day.weather) }}</span>
                  <span class="forecast-range">{{ day.day_temp }} / {{ day.night_temp }}</span>
                </div>
              </div>
            </div>
            <div class="weather-tips" v-if="intelligence.weather.tips">
              <el-icon><InfoFilled /></el-icon>
              {{ intelligence.weather.tips }}
            </div>
          </div>
        </div>

        <!-- 风险评估 -->
        <div class="bento-card risk-card">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon risk">
                <el-icon><Warning /></el-icon>
              </div>
              <h3>风险评估</h3>
            </div>
            <el-tag :type="getRiskType(intelligence.risk_assessment?.risk_level)" size="large">
              {{ getRiskLabel(intelligence.risk_assessment?.risk_level) }}
            </el-tag>
          </div>
          <div class="risk-content" v-if="intelligence.risk_assessment">
            <div class="risk-bar">
              <div
                v-for="i in 5"
                :key="i"
                :class="['risk-segment', { active: i <= (intelligence.risk_assessment?.risk_level || 1) }]"
              ></div>
            </div>
            <div class="risk-recommendation">
              {{ intelligence.risk_assessment.recommendation }}
            </div>
            <div class="risk-categories" v-if="intelligence.risk_assessment?.risk_categories">
              <div
                v-for="(category, key) in intelligence.risk_assessment.risk_categories"
                :key="key"
                class="risk-category-item"
              >
                <div class="category-header">
                  <span class="category-status" :class="category.status">
                    {{ category.status === 'safe' ? '✓' : category.status === 'attention' ? '⚠️' : '✗' }}
                  </span>
                  <span class="category-name">{{ getCategoryLabel(key) }}</span>
                </div>
                <div class="category-desc">{{ category.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 汇率信息 -->
        <div class="bento-card exchange-card" v-if="intelligence.exchange_rate?.available">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon exchange">
                <span>💱</span>
              </div>
              <h3>汇率信息</h3>
            </div>
          </div>
          <div class="exchange-content">
            <div class="exchange-main">
              <div class="exchange-rate">
                <span class="rate-from">1 {{ getCurrencySymbol(intelligence.exchange_rate.from) }}</span>
                <span class="rate-equals">=</span>
                <span class="rate-to">{{ intelligence.exchange_rate.rate }} {{ getCurrencySymbol(intelligence.exchange_rate.to) }}</span>
              </div>
              <div class="exchange-inverse">
                <span class="inverse-text">1 {{ getCurrencySymbol(intelligence.exchange_rate.to) }} = {{ intelligence.exchange_rate.inverse }} {{ getCurrencySymbol(intelligence.exchange_rate.from) }}</span>
              </div>
            </div>
            <div class="exchange-tips">
              <el-icon><Wallet /></el-icon>
              <span>建议关注汇率变化，提前兑换少量现金</span>
            </div>
          </div>
        </div>

        <!-- 新闻资讯 - 三个独立模块 -->
        <div class="bento-card news-card" style="grid-column: span 2; grid-row: span 2;">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon news">
                <el-icon><Document /></el-icon>
              </div>
              <h3>新闻资讯</h3>
            </div>
          </div>

          <!-- 新闻标签页 -->
          <el-tabs v-model="activeNewsTab" class="news-tabs">
            <el-tab-pane label="旅游新闻" name="travel">
              <template #label>
                <span class="tab-label">
                  <span class="tab-icon">✈️</span>
                  旅游新闻
                  <el-badge :value="travelNews.length" :max="99" type="primary" />
                </span>
              </template>
              <div class="news-timeline" v-if="travelNews.length > 0">
                <div class="timeline-line"></div>
                <div v-for="(news, index) in travelNews.slice(0, 5)" :key="index" class="news-item">
                  <div class="timeline-dot" :class="news.sentiment"></div>
                  <div class="news-card-content">
                    <div class="news-header">
                      <el-tag type="success" size="small">旅游</el-tag>
                      <span class="news-time">{{ formatNewsTime(news.published_at) }}</span>
                    </div>
                    <div v-if="news.picUrl" class="news-image">
                      <img :src="news.picUrl" :alt="news.title" @error="handleImageError" />
                    </div>
                    <h4 class="news-title">{{ news.title }}</h4>
                    <p class="news-summary">{{ news.summary }}</p>
                    <div class="news-footer">
                      <span class="news-source">{{ news.source }}</span>
                      <a v-if="news.url && news.url !== '#'" :href="news.url" target="_blank" class="news-link">阅读更多 →</a>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-news">
                <el-icon><Document /></el-icon>
                <p>暂无旅游新闻</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="地区新闻" name="area">
              <template #label>
                <span class="tab-label">
                  <span class="tab-icon">📍</span>
                  地区新闻
                  <el-badge :value="areaNews.length" :max="99" type="warning" />
                </span>
              </template>
              <div class="news-timeline" v-if="areaNews.length > 0">
                <div class="timeline-line"></div>
                <div v-for="(news, index) in areaNews.slice(0, 5)" :key="index" class="news-item">
                  <div class="timeline-dot" :class="news.sentiment"></div>
                  <div class="news-card-content">
                    <div class="news-header">
                      <el-tag type="warning" size="small">本地</el-tag>
                      <span class="news-time">{{ formatNewsTime(news.published_at) }}</span>
                    </div>
                    <div v-if="news.picUrl" class="news-image">
                      <img :src="news.picUrl" :alt="news.title" @error="handleImageError" />
                    </div>
                    <h4 class="news-title">{{ news.title }}</h4>
                    <p class="news-summary">{{ news.summary }}</p>
                    <div class="news-footer">
                      <span class="news-source">{{ news.source }}</span>
                      <a v-if="news.url && news.url !== '#'" :href="news.url" target="_blank" class="news-link">阅读更多 →</a>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-news">
                <el-icon><Document /></el-icon>
                <p>暂无地区新闻</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="综合新闻" name="general">
              <template #label>
                <span class="tab-label">
                  <span class="tab-icon">📰</span>
                  综合新闻
                  <el-badge :value="generalNews.length" :max="99" type="info" />
                </span>
              </template>
              <div class="news-timeline" v-if="generalNews.length > 0">
                <div class="timeline-line"></div>
                <div v-for="(news, index) in generalNews.slice(0, 5)" :key="index" class="news-item">
                  <div class="timeline-dot" :class="news.sentiment"></div>
                  <div class="news-card-content">
                    <div class="news-header">
                      <el-tag :type="getNewsType(news.category)" size="small">{{ getCategoryLabel(news.category) }}</el-tag>
                      <span class="news-time">{{ formatNewsTime(news.published_at) }}</span>
                    </div>
                    <div v-if="news.picUrl" class="news-image">
                      <img :src="news.picUrl" :alt="news.title" @error="handleImageError" />
                    </div>
                    <h4 class="news-title">{{ news.title }}</h4>
                    <p class="news-summary">{{ news.summary }}</p>
                    <div class="news-footer">
                      <span class="news-source">{{ news.source }}</span>
                      <a v-if="news.url && news.url !== '#'" :href="news.url" target="_blank" class="news-link">阅读更多 →</a>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-news">
                <el-icon><Document /></el-icon>
                <p>暂无综合新闻</p>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 景点推荐 -->
        <div class="bento-card attractions-card">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon attraction">
                <el-icon><Location /></el-icon>
              </div>
              <h3>必游景点</h3>
            </div>
            <el-badge :value="intelligence.attractions?.length || 0" :max="99" />
          </div>
          <div class="attractions-list">
            <div
              v-for="(attr, index) in (intelligence.attractions || []).slice(0, 4)"
              :key="index"
              class="attraction-item"
            >
              <div class="attraction-rating">
                <span class="rating-stars">{{ '★'.repeat(Math.round(attr.rating)) }}</span>
                <span class="rating-score">{{ attr.rating }}</span>
              </div>
              <div class="attraction-name">{{ attr.name }}</div>
            </div>
          </div>
        </div>

        <!-- 智能建议 -->
        <div class="bento-card tips-card">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon tips">
                <el-icon><InfoFilled /></el-icon>
              </div>
              <h3>智能建议</h3>
            </div>
          </div>
          <div class="tips-list">
            <div
              v-for="(tip, index) in (intelligence.recommendations || []).slice(0, 5)"
              :key="index"
              class="tip-item"
            >
              <el-icon class="tip-icon"><Check /></el-icon>
              <span class="tip-text">{{ tip }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-section">
      <div class="empty-card">
        <div class="empty-icon">
          <el-icon><Search /></el-icon>
        </div>
        <h3>探索目的地情报</h3>
        <p>输入目的地名称，获取实时新闻、天气、汇率和风险评估</p>
        <el-button type="primary" size="large" @click="quickSearch('杭州')">
          搜索杭州
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Document, Calendar, Warning, InfoFilled, Clock,
  Compass, Location, Check, Wallet
} from '@element-plus/icons-vue'
import * as intelligenceAPI from '@/api/travel/intelligence'

const searchKeyword = ref('')
const loading = ref(false)
const intelligence = ref<any>(null)
const apiSources = ref<any>(null)

// 新闻模块状态
const activeNewsTab = ref('travel')
const travelNews = ref<any[]>([])
const areaNews = ref<any[]>([])
const generalNews = ref<any[]>([])

const quickSearchDestinations = ref(['杭州', '北京', '成都', '三亚', '厦门', '西安', '日本', '泰国'])

const quickSearch = async (keyword: string) => {
  searchKeyword.value = keyword
  await handleSearch()
}

const handleSearch = async () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入目的地')
    return
  }

  loading.value = true

  try {
    // 并行获取完整情报和三种新闻
    const [intelligentResult, travelResult, areaResult, generalResult] = await Promise.all([
      intelligenceAPI.getDestinationIntelligence(searchKeyword.value),
      intelligenceAPI.getTravelNews(searchKeyword.value, 10),
      intelligenceAPI.getAreaNews(searchKeyword.value, 10),
      intelligenceAPI.getGeneralNews(searchKeyword.value, 10)
    ])

    if (intelligentResult.success) {
      intelligence.value = intelligentResult.data
      apiSources.value = intelligentResult.sources
    }

    // 更新三种新闻数据
    travelNews.value = travelResult.news || []
    areaNews.value = areaResult.news || []
    generalNews.value = generalResult.news || []

    ElMessage.success(`成功获取 ${searchKeyword.value} 的情报数据`)
  } catch (error: any) {
    console.error('获取情报失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取情报失败')
  } finally {
    loading.value = false
  }
}

// 格式化函数
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleDateString('zh-CN')
}

const formatNewsTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)

  if (hours < 1) return '刚刚'
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

// 图标和标签
const getWeatherIcon = (weather?: string) => {
  if (!weather) return '☀️'
  const map: Record<string, string> = {
    '晴': '☀️',
    '多云': '⛅',
    '阴': '☁️',
    '雨': '🌧️',
    '雪': '❄️'
  }
  for (const [key, icon] of Object.entries(map)) {
    if (weather?.includes(key)) return icon
  }
  return '☀️'
}

const getRiskIcon = (level?: number) => {
  if (!level || level <= 1) return '✓'
  if (level <= 2) return '⚠️'
  return '✗'
}

const getRiskLabel = (level?: number) => {
  if (!level || level <= 1) return '低风险'
  if (level <= 2) return '中等风险'
  if (level <= 3) return '高风险'
  return '极高风险'
}

const getRiskType = (level?: number) => {
  if (!level || level <= 1) return 'success'
  if (level <= 2) return 'warning'
  return 'danger'
}

const getCurrencySymbol = (code?: string) => {
  const symbols: Record<string, string> = {
    'CNY': '¥',
    'JPY': '¥',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'THB': '฿',
    'VND': '₫',
    'KRW': '₩'
  }
  return symbols[code] || ''
}

const getSourceLabel = (source: string) => {
  const labels: Record<string, string> = {
    'amap': '高德',
    'mock': '模拟',
    'exchangerate-api': '实时',
    'serpapi': 'Google',
    'tianapi': '天行数据'
  }
  return labels[source] || source
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    'safety': '安全',
    'policy': '政策',
    'transport': '交通',
    'weather': '天气',
    'tourism': '旅游',
    'event': '活动',
    'general': '综合'
  }
  return labels[category] || '综合'
}

const getNewsType = (category: string) => {
  const types: Record<string, any> = {
    'safety': 'danger',
    'policy': 'success',
    'transport': 'warning',
    'weather': 'info',
    'tourism': 'primary',
    'event': 'success',
    'general': 'info',
    'local': 'info'
  }
  return types[category] || 'info'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style lang="scss" scoped>
.intelligence-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

// Hero Section
.hero-section {
  position: relative;
  padding: 80px 20px 60px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  animation: float 6s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  top: -100px;
  right: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  bottom: -50px;
  left: 10%;
  animation-delay: -3s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  color: #a78bfa;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  color: #94a3b8;
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.search-box {
  max-width: 500px;
  margin: 0 auto;
}

.quick-search {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.quick-tag {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: #a78bfa;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.875rem;
}

.quick-tag:hover {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
}

.quick-tag.active {
  background: rgba(102, 126, 234, 0.5);
  border-color: #667eea;
}

// Loading
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.3);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #94a3b8;
  margin-top: 1rem;
}

// Content Section
.content-section {
  padding: 40px 20px;
  max-width: 1400px;
  margin: 0 auto;
}

// Overview Card
.overview-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 16px;
}

.destination-name {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.destination-meta {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.api-source {
  color: #10b981;
  font-size: 0.75rem;
}

.overview-actions {
  display: flex;
  gap: 8px;
}

// Status Bar
.status-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.status-icon {
  font-size: 18px;
}

.status-value {
  font-size: 0.875rem;
  color: #cbd5e1;
}

.status-item.weather .status-value {
  color: #fbbf24;
}

.status-item.risk .status-value {
  color: #10b981;
}

.status-item.exchange .status-value {
  color: #8b5cf6;
}

// Bento Grid
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.bento-card {
  background: #1e293b;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.header-icon.weather {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.header-icon.risk {
  background: linear-gradient(135deg, #10b981, #059669);
}

.header-icon.exchange {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}

.header-icon.news {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.header-icon.attraction {
  background: linear-gradient(135deg, #ec4899, #db2777);
}

.header-icon.tips {
  background: linear-gradient(135deg, #10b981, #059669);
}

.header-icon span {
  font-size: 20px;
}

h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
}

// Weather Card
.weather-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.current-weather {
  text-align: center;
  padding: 16px;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 12px;
}

.current-temp {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fbbf24;
}

.current-desc {
  font-size: 1.125rem;
  color: #cbd5e1;
  margin: 4px 0;
}

.current-detail {
  font-size: 0.875rem;
  color: #94a3b8;
}

.weather-forecast {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forecast-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.forecast-date {
  text-align: center;
  min-width: 60px;
}

.forecast-week {
  font-size: 0.75rem;
  color: #94a3b8;
}

.forecast-day {
  font-size: 1rem;
  font-weight: 600;
  color: #cbd5e1;
}

.forecast-temps {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  flex: 1;
}

.forecast-icon {
  font-size: 18px;
}

.forecast-range {
  font-size: 0.875rem;
  color: #cbd5e1;
}

.weather-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  color: #10b981;
  font-size: 0.875rem;
}

// Risk Card
.risk-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-bar {
  display: flex;
  gap: 4px;
}

.risk-segment {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  transition: all 0.3s;
}

.risk-segment.active {
  background: linear-gradient(90deg, #10b981, #059669);
}

.risk-recommendation {
  color: #cbd5e1;
  font-size: 0.875rem;
  line-height: 1.6;
}

.risk-categories {
  display: grid;
  gap: 8px;
}

.risk-category-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.category-status {
  font-size: 18px;
}

.category-status.safe {
  color: #10b981;
}

.category-status.attention {
  color: #f59e0b;
}

.category-name {
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 500;
}

.category-desc {
  color: #94a3b8;
  font-size: 0.75rem;
}

// Exchange Card
.exchange-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exchange-main {
  text-align: center;
  padding: 16px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 12px;
}

.exchange-rate {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.rate-from, .rate-to {
  color: #f1f5f9;
}

.rate-equals {
  color: #94a3b8;
}

.exchange-inverse {
  font-size: 0.875rem;
  color: #a78bfa;
}

.exchange-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
  color: #a78bfa;
  font-size: 0.875rem;
}

// News Card with Tabs
.news-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }

  :deep(.el-tabs__nav-wrap) {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
  }

  :deep(.el-tabs__item) {
    color: #94a3b8;
    padding: 0 20px;

    &.is-active {
      color: #f1f5f9;
    }
  }

  :deep(.el-tabs__active-bar) {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
  }
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;

  .tab-icon {
    font-size: 18px;
  }
}

.empty-news {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;

  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    margin: 0;
    font-size: 0.875rem;
  }
}

.news-timeline {
  position: relative;
  padding-left: 20px;
}

.timeline-line {
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
}

.news-item {
  position: relative;
  padding-bottom: 20px;
  padding-left: 24px;
}

.timeline-dot {
  position: absolute;
  left: -29px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #1e293b;
}

.timeline-dot.positive {
  background: #10b981;
}

.timeline-dot.neutral {
  background: #6b7280;
}

.timeline-dot.negative {
  background: #ef4444;
}

.news-card-content {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 16px;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.news-time {
  color: #94a3b8;
  font-size: 0.75rem;
}

.news-title {
  margin: 0 0 8px;
  color: #f1f5f9;
  font-size: 1rem;
  line-height: 1.5;
}

.news-image {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;

  img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    display: block;
  }
}

.news-summary {
  color: #94a3b8;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 12px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-source {
  color: #6b7280;
  font-size: 0.75rem;
}

.news-link {
  color: #8b5cf6;
  text-decoration: none;
  font-size: 0.875rem;
}

// Attractions Card
.attractions-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.attraction-item {
  padding: 12px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 8px;
}

.attraction-rating {
  margin-bottom: 8px;
}

.rating-stars {
  color: #fbbf24;
  font-size: 0.75rem;
}

.rating-score {
  color: #f1f5f9;
  font-size: 0.75rem;
  margin-left: 4px;
}

.attraction-name {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.attraction-reviews {
  color: #94a3b8;
  font-size: 0.75rem;
}

// Tips Card
.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  background: rgba(16, 185, 129, 0.05);
  border-radius: 8px;
}

.tip-icon {
  color: #10b981;
  margin-top: 2px;
}

.tip-text {
  color: #cbd5e1;
  font-size: 0.875rem;
  line-height: 1.5;
}

// Empty State
.empty-section {
  padding: 100px 20px;
  text-align: center;
}

.empty-card {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 64px;
  color: #6b7280;
  margin-bottom: 16px;
}

.empty-card h3 {
  color: #f1f5f9;
  margin: 0 0 8px 0;
}

.empty-card p {
  color: #94a3b8;
  margin: 0 0 24px 0;
}

// Responsive
@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .news-card {
    grid-column: span 2 !important;
    grid-row: span 1 !important;
  }
}

@media (max-width: 640px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 2rem;
  }

  .status-bar {
    flex-direction: column;
  }

  .attractions-list {
    grid-template-columns: 1fr;
  }

  .exchange-main .exchange-rate {
    flex-direction: column;
    font-size: 1.25rem;
  }
}
</style>
