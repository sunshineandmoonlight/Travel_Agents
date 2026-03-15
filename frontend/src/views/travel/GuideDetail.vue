<template>
  <div class="guide-detail-page" v-loading="loading">
    <!-- Header -->
    <div class="guide-header" :style="{ backgroundImage: `url(${guideData.thumbnail_url})` }" v-if="!loading">
      <div class="header-overlay"></div>
      <div class="header-content">
        <el-button class="back-btn" @click="$router.push('/travel')">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-info">
          <span class="status-badge" :class="`status-${guideData.status}`">
            {{ statusMap[guideData.status] || guideData.status }}
          </span>
          <h1 class="guide-title">{{ guideData.title }}</h1>
          <div class="guide-meta">
            <span class="meta-item">
              <el-icon><Location /></el-icon>
              {{ guideData.destination }}
            </span>
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ guideData.total_days }}天
            </span>
            <span class="meta-item">
              <el-icon><Wallet /></el-icon>
              ¥{{ formatBudget(guideData.budget) }}
            </span>
          </div>
          <div class="guide-tags" v-if="guideData.tags?.length">
            <el-tag v-for="tag in guideData.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="guide-content" v-if="!loading">
      <div class="content-container">
        <!-- Actions Bar -->
        <div class="actions-bar">
          <div class="stats">
            <span class="stat-item">
              <el-icon><View /></el-icon>
              {{ guideData.view_count || 0 }} 浏览
            </span>
            <span class="stat-item">
              <el-icon><Star /></el-icon>
              {{ guideData.like_count || 0 }} 收藏
            </span>
            <span class="stat-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(guideData.created_at) }}
            </span>
          </div>
          <div class="actions">
            <el-button type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button @click="handleExportPDF">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
            <el-button @click="handleShare">
              <el-icon><Share /></el-icon>
              分享
            </el-button>
            <el-button type="danger" plain @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>

        <!-- Overview Section -->
        <div class="overview-section" v-if="guideData.guide_data">
          <h2 class="section-title">行程概览</h2>
          <div class="overview-grid">
            <div class="overview-item">
              <div class="overview-icon">
                <el-icon><Location /></el-icon>
              </div>
              <div class="overview-text">
                <div class="overview-label">目的地</div>
                <div class="overview-value">{{ guideData.destination }}</div>
              </div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="overview-text">
                <div class="overview-label">行程天数</div>
                <div class="overview-value">{{ guideData.total_days }} 天</div>
              </div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="overview-text">
                <div class="overview-label">预算</div>
                <div class="overview-value">¥{{ formatBudget(guideData.budget) }}</div>
              </div>
            </div>
            <div class="overview-item" v-if="guideData.guide_data.budget_level">
              <div class="overview-icon">
                <el-icon><CreditCard /></el-icon>
              </div>
              <div class="overview-text">
                <div class="overview-label">预算等级</div>
                <div class="overview-value">{{ budgetLevelMap[guideData.guide_data.budget_level] || guideData.guide_data.budget_level }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Itinerary -->
        <div class="itinerary-section" v-if="dailyItinerary.length > 0">
          <h2 class="section-title">详细行程</h2>

          <div class="day-list">
            <div v-for="day in dailyItinerary" :key="day.day" class="day-card">
              <div class="day-header">
                <span class="day-number">第{{ day.day }}天</span>
                <span class="day-title">{{ day.title }}</span>
              </div>

              <div class="day-content" v-if="day.description">
                <p class="day-description">{{ day.description }}</p>
              </div>

              <div class="day-activities" v-if="day.activities && day.activities.length > 0">
                <div v-for="(activity, index) in day.activities" :key="index" class="activity-item">
                  <div class="activity-time">
                    {{ activity.time }}
                    <el-tag v-if="activity.period" size="small" class="period-tag">{{ periodMap[activity.period] || activity.period }}</el-tag>
                  </div>
                  <div class="activity-content">
                    <div class="activity-icon" v-if="activity.type !== 'meal'">
                      <el-image
                        v-if="activity.image"
                        :src="activity.image"
                        fit="cover"
                        class="activity-image"
                        :lazy="true"
                      >
                        <template #error>
                          <div class="image-placeholder">
                            <el-icon><Picture /></el-icon>
                          </div>
                        </template>
                      </el-image>
                      <div v-else class="icon-placeholder">
                        <el-icon>
                          <component :is="getActivityIcon(activity.type)" />
                        </el-icon>
                      </div>
                    </div>
                    <div class="activity-meal-icon" v-else>
                      <el-icon><Coffee /></el-icon>
                    </div>
                    <div class="activity-info">
                      <h4>{{ activity.name || activity.title }}</h4>
                      <p class="activity-description" v-if="activity.description">{{ activity.description }}</p>
                      <div class="activity-meta">
                        <el-tag v-if="activity.duration" size="small" type="info">
                          <el-icon><Clock /></el-icon>
                          {{ activity.duration }}
                        </el-tag>
                        <el-tag v-if="activity.cost" size="small" type="warning">
                          <el-icon><Wallet /></el-icon>
                          ¥{{ activity.cost }}
                        </el-tag>
                        <el-tag v-if="activity.address" size="small" type="success">
                          <el-icon><Location /></el-icon>
                          {{ activity.address }}
                        </el-tag>
                      </div>
                      <div class="activity-tips" v-if="activity.tips">
                        <el-icon><InfoFilled /></el-icon>
                        <span>{{ activity.tips }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Daily Summary -->
              <div class="day-summary" v-if="day.summary">
                <h4>今日小结</h4>
                <p>{{ day.summary }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Budget Breakdown -->
        <div class="budget-section" v-if="guideData.guide_data?.budget_breakdown">
          <h2 class="section-title">费用预算</h2>
          <div class="budget-breakdown">
            <div class="budget-item" v-for="(item, key) in displayBudgetItems" :key="key">
              <div class="budget-label">
                <el-icon>
                  <component :is="getBudgetIcon(key)" />
                </el-icon>
                {{ budgetLabelMap[key] || key }}
              </div>
              <div class="budget-value">¥{{ formatNumber(item) }}</div>
            </div>
            <div class="budget-item total">
              <div class="budget-label">
                <el-icon><Wallet /></el-icon>
                总计
              </div>
              <div class="budget-value">¥{{ formatNumber(guideData.guide_data.budget_breakdown.total_budget) }}</div>
            </div>
          </div>
        </div>

        <!-- Tips -->
        <div class="tips-section" v-if="guideData.guide_data?.tips">
          <h2 class="section-title">旅行贴士</h2>
          <div class="tips-content">
            <div v-if="guideData.guide_data.tips.general" class="tip-block">
              <h4><el-icon><InfoFilled /></el-icon> 综合建议</h4>
              <p>{{ guideData.guide_data.tips.general }}</p>
            </div>
            <div v-if="guideData.guide_data.tips.packing" class="tip-block">
              <h4><el-icon><Suitcase /></el-icon> 行李准备</h4>
              <p>{{ guideData.guide_data.tips.packing }}</p>
            </div>
            <div v-if="guideData.guide_data.tips.weather" class="tip-block">
              <h4><el-icon><Sunny /></el-icon> 天气提醒</h4>
              <p>{{ guideData.guide_data.tips.weather }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Location, Calendar, View, Star, Clock, Wallet, CreditCard,
  Edit, Download, Share, Delete, Picture, Coffee, InfoFilled,
  Sunny, Suitcase, Camera, Dining, Moon
} from '@element-plus/icons-vue'
import { getGuideDetail, deleteGuide, downloadGuidePDF } from '@/api/travel/guides'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const guideData = ref<any>({})

// 状态映射
const statusMap: Record<string, string> = {
  'draft': '草稿',
  'published': '已发布',
  'archived': '已归档'
}

// 预算等级映射
const budgetLevelMap: Record<string, string> = {
  'economy': '经济型',
  'standard': '舒适型',
  'luxury': '高端型'
}

// 时段映射
const periodMap: Record<string, string> = {
  'morning': '上午',
  'afternoon': '下午',
  'evening': '晚上',
  'lunch': '午餐',
  'dinner': '晚餐'
}

// 预算标签映射
const budgetLabelMap: Record<string, string> = {
  'accommodation': '住宿',
  'transport': '交通',
  'dining': '餐饮',
  'tickets': '门票',
  'shopping': '购物',
  'other': '其他'
}

// 计算属性：每日行程
const dailyItinerary = computed(() => {
  if (!guideData.value.guide_data) return []

  const guide = guideData.value.guide_data

  // 处理不同格式的行程数据
  if (guide.daily_itinerary && Array.isArray(guide.daily_itinerary)) {
    return guide.daily_itinerary.map((day: any, index: number) => ({
      day: index + 1,
      title: day.title || day.date || `第${index + 1}天`,
      description: day.description || day.summary,
      activities: day.activities || day.schedule || [],
      summary: day.summary
    }))
  }

  // 处理分时段格式
  if (guide.schedule) {
    const days = []
    const maxDays = guideData.value.total_days || 1

    for (let i = 0; i < maxDays; i++) {
      const dayNum = i + 1
      const morningActivities = guide.schedule.morning?.filter((a: any) => a.day === dayNum) || []
      const afternoonActivities = guide.schedule.afternoon?.filter((a: any) => a.day === dayNum) || []
      const eveningActivities = guide.schedule.evening?.filter((a: any) => a.day === dayNum) || []

      days.push({
        day: dayNum,
        title: `第${dayNum}天`,
        activities: [
          ...morningActivities.map((a: any) => ({ ...a, period: 'morning', time: a.time || '09:00' })),
          ...afternoonActivities.map((a: any) => ({ ...a, period: 'afternoon', time: a.time || '14:00' })),
          ...eveningActivities.map((a: any) => ({ ...a, period: 'evening', time: a.time || '19:00' }))
        ]
      })
    }
    return days
  }

  return []
})

// 计算属性：预算项目显示
const displayBudgetItems = computed(() => {
  const breakdown = guideData.value.guide_data?.budget_breakdown
  if (!breakdown) return {}

  const items: Record<string, number> = {}
  if (breakdown.accommodation) items.accommodation = breakdown.accommodation
  if (breakdown.transport) items.transport = breakdown.transport
  if (breakdown.dining) items.dining = breakdown.dining
  if (breakdown.tickets) items.tickets = breakdown.tickets
  if (breakdown.shopping) items.shopping = breakdown.shopping
  if (breakdown.other) items.other = breakdown.other

  return items
})

// 获取活动图标
const getActivityIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    'attraction': Camera,
    'sight': Camera,
    'transport': Location,
    'meal': Coffee,
    'dining': Coffee,
    'shopping': Wallet,
    'hotel': Moon
  }
  return iconMap[type] || Camera
}

// 获取预算图标
const getBudgetIcon = (key: string) => {
  const iconMap: Record<string, any> = {
    'accommodation': Moon,
    'transport': Location,
    'dining': Coffee,
    'tickets': Camera,
    'shopping': Wallet,
    'other': InfoFilled
  }
  return iconMap[key] || Wallet
}

// 格式化预算
const formatBudget = (budget: number) => {
  if (!budget) return '0'
  return budget.toLocaleString()
}

// 格式化数字
const formatNumber = (num: number) => {
  if (!num) return '0'
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

  if (diff === 0) return '今天'
  if (diff === 1) return '昨天'
  if (diff < 7) return `${diff}天前`
  if (diff < 30) return `${Math.floor(diff / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}

// 加载攻略详情
const loadGuideDetail = async () => {
  try {
    loading.value = true
    const guideId = route.params.id as string
    const data = await getGuideDetail(guideId)
    guideData.value = data
  } catch (error) {
    console.error('加载攻略详情失败:', error)
    ElMessage.error('加载攻略详情失败')
    router.push('/travel/guides')
  } finally {
    loading.value = false
  }
}

// 编辑
const handleEdit = () => {
  router.push(`/travel/guides/${guideData.value.id}/edit`)
}

// 导出PDF
const handleExportPDF = async () => {
  try {
    ElMessage.info('正在生成PDF，请稍候...')
    await downloadGuidePDF(guideData.value.id)
    ElMessage.success('PDF下载成功')
  } catch (error) {
    console.error('导出PDF失败:', error)
    ElMessage.error('导出PDF失败')
  }
}

// 分享
const handleShare = () => {
  const url = window.location.href
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 删除
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '删除后无法恢复，确定要删除这个攻略吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const userId = 'demo_user' // 实际应从登录状态获取
    await deleteGuide(guideData.value.id, userId)
    ElMessage.success('删除成功')
    router.push('/travel/guides')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadGuideDetail()
})
</script>

<style scoped>
.guide-detail-page {
  min-height: 100vh;
  background: #f8fafc;
}

/* Header */
.guide-header {
  position: relative;
  height: 400px;
  background-size: cover;
  background-position: center;
  background-color: #e5e7eb;
}

.header-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.7));
}

.header-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
  color: white;
}

.back-btn {
  position: absolute;
  top: 24px;
  left: 24px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.header-info {
  margin-top: auto;
  max-width: 800px;
}

.status-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 16px;
}

.status-badge.status-draft {
  background: rgba(251, 191, 36, 0.9);
  color: #92400e;
}

.status-badge.status-published {
  background: rgba(52, 211, 153, 0.9);
  color: #065f46;
}

.guide-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.guide-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
}

.guide-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Content */
.guide-content {
  padding: 32px 24px;
}

.content-container {
  max-width: 1000px;
  margin: 0 auto;
}

.actions-bar {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 12px;
}

/* Section */
.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 24px 0;
}

.overview-section,
.itinerary-section,
.budget-section,
.tips-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* Overview */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.overview-label {
  font-size: 13px;
  color: #6b7280;
}

.overview-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* Day List */
.day-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.day-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  background: #fafafa;
}

.day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.day-number {
  padding: 8px 16px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.day-description {
  color: #6b7280;
  line-height: 1.8;
  margin-bottom: 20px;
}

.day-activities {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 16px;
  align-items: start;
}

.activity-time {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.period-tag {
  font-size: 11px;
}

.activity-content {
  display: flex;
  gap: 16px;
  flex: 1;
}

.activity-icon {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f3f4f6;
}

.activity-image {
  width: 100%;
  height: 100%;
}

.icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 24px;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  color: #9ca3af;
  font-size: 24px;
}

.activity-meal-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #fef3c7;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
  font-size: 20px;
  flex-shrink: 0;
}

.activity-info {
  flex: 1;
}

.activity-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.activity-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.activity-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.activity-tips {
  display: flex;
  gap: 6px;
  align-items: flex-start;
  font-size: 13px;
  color: #059669;
  background: #ecfdf5;
  padding: 8px 12px;
  border-radius: 8px;
  line-height: 1.5;
}

.day-summary {
  margin-top: 20px;
  padding: 16px;
  background: #eff6ff;
  border-radius: 12px;
  border-left: 4px solid #3b82f6;
}

.day-summary h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
  margin: 0 0 8px 0;
}

.day-summary p {
  font-size: 14px;
  color: #1e3a8a;
  margin: 0;
  line-height: 1.6;
}

/* Budget */
.budget-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.budget-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.budget-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #374151;
}

.budget-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.budget-item.total {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.budget-item.total .budget-label,
.budget-item.total .budget-value {
  color: white;
}

/* Tips */
.tips-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tip-block h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.tip-block p {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.8;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .guide-header {
    height: 300px;
  }

  .guide-title {
    font-size: 28px;
  }

  .actions-bar {
    flex-direction: column;
    gap: 16px;
  }

  .actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
  }

  .activity-item {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .activity-time {
    font-size: 13px;
  }

  .activity-content {
    flex-direction: column;
  }

  .activity-icon {
    width: 100%;
    height: 150px;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
