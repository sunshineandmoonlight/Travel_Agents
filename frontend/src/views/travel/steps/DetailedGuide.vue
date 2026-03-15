<template>
  <div class="detailed-guide">
    <!-- 加载/进度显示 -->
    <AgentGenerationProgress
      v-if="!isContentReady"
      :is-visible="showProgress"
      :guide="guide"
      :step-results="stagedPlanner.stepResults"
      @update:isVisible="showProgress = $event"
      @completed="handleGenerationComplete"
      ref="progressRef"
    />

    <!-- 加载遮罩（初始加载） -->
    <div class="loading-overlay" v-if="isInitialLoading">
      <div class="loading-content">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>正在准备您的攻略...</p>
      </div>
    </div>

    <!-- 攻略内容（只在准备好时显示） -->
    <div class="container" v-if="guide && isContentReady">
      <!-- 图片加载进度提示 -->
      <div v-if="imagesLoading > 0" class="images-loading-banner">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在加载景点图片... ({{ imagesLoading }})</span>
      </div>

      <!-- Success Message -->
      <div class="success-banner">
        <div class="success-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="success-content">
          <h2>您的专属攻略已生成!</h2>
          <p>共 {{ guide.total_days }} 天精彩旅程，预算 ¥{{ guide.budget_breakdown.total_budget }}</p>
        </div>
      </div>

      <!-- Budget Summary -->
      <div class="budget-summary">
        <div class="budget-card">
          <div class="budget-header">
            <el-icon class="budget-icon"><Wallet /></el-icon>
            <div class="budget-title">总预算</div>
          </div>
          <div class="budget-amount">¥{{ guide.budget_breakdown.total_budget }}</div>
          <div class="budget-breakdown">
            <div class="breakdown-item">
              <el-icon class="item-icon attractions"><Ticket /></el-icon>
              <div class="item-content">
                <span class="item-label">景点</span>
                <span class="item-value">¥{{ guide.budget_breakdown.attractions }}</span>
              </div>
            </div>
            <div class="breakdown-item">
              <el-icon class="item-icon transport"><Operation /></el-icon>
              <div class="item-content">
                <span class="item-label">交通</span>
                <span class="item-value">¥{{ guide.budget_breakdown.transport }}</span>
              </div>
            </div>
            <div class="breakdown-item">
              <el-icon class="item-icon dining"><Food /></el-icon>
              <div class="item-content">
                <span class="item-label">餐饮</span>
                <span class="item-value">¥{{ guide.budget_breakdown.dining }}</span>
              </div>
            </div>
            <div class="breakdown-item">
              <el-icon class="item-icon accommodation"><House /></el-icon>
              <div class="item-content">
                <span class="item-label">住宿</span>
                <span class="item-value">¥{{ guide.budget_breakdown.accommodation }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Daily Itineraries -->
      <div class="itineraries">
        <h3 class="section-title">
          <el-icon><Calendar /></el-icon>
          每日行程
        </h3>

        <div v-for="day in guideWithImages" :key="day.day" class="day-card">
          <div class="day-header">
            <div class="day-number">{{ day.day }}</div>
            <div class="day-info">
              <h4 class="day-title">{{ day.title }}</h4>
              <div class="day-meta">
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ day.date }}
                </span>
                <span class="meta-item weather-info">
                  <el-icon><Sunny /></el-icon>
                  <span>{{ getDayWeather(day) }}</span>
                </span>
                <span class="meta-item">
                  <el-icon><Odometer /></el-icon>
                  {{ day.pace }}
                </span>
                <span class="meta-item">
                  <el-icon><Wallet /></el-icon>
                  ¥{{ day.daily_budget }}
                </span>
              </div>
            </div>
          </div>

          <div class="day-schedule">
            <div v-for="(item, index) in day.schedule" :key="index" class="schedule-item">
              <div class="item-time">{{ item.time_range }}</div>
              <div class="item-content">
                <div class="item-header">
                  <el-icon class="item-period-icon" :class="`period-${item.period}`">
                    <component :is="getPeriodIcon(item.period)" />
                  </el-icon>
                  <span class="item-activity">{{ item.activity }}</span>
                </div>

                <!-- Attraction Image Thumbnail -->
                <div v-if="shouldShowImage(item)" class="item-image">
                  <img
                    :src="item.imageUrl"
                    :alt="item.activity"
                    @load="handleImageLoad(item)"
                    @error="handleImageError(item, $event)"
                    class="attraction-image"
                  >
                </div>

                <div v-if="item.location" class="item-location">
                  <el-icon><LocationFilled /></el-icon>
                  {{ item.location }}
                </div>

                <!-- 详细描述 -->
                <div v-if="item.description" class="item-description">
                  {{ item.description }}
                </div>

                <!-- 活动亮点 -->
                <div v-if="item.highlights && item.highlights.length" class="item-highlights">
                  <div class="highlights-title">
                    <el-icon><Sunny /></el-icon>
                    <span>必看亮点</span>
                  </div>
                  <ul class="highlights-list">
                    <li v-for="(highlight, idx) in item.highlights" :key="idx">{{ highlight }}</li>
                  </ul>
                </div>

                <!-- 实用信息 -->
                <div v-if="item.practical_info" class="item-practical">
                  <div class="practical-header">
                    <el-icon class="practical-icon"><InfoFilled /></el-icon>
                    <span>实用信息</span>
                  </div>
                  <div class="practical-details">
                    <div v-if="item.practical_info.address" class="practical-item">
                      <span class="practical-label">📍 地址</span>
                      <span class="practical-value">{{ item.practical_info.address }}</span>
                    </div>
                    <div v-if="item.practical_info.opening_hours" class="practical-item">
                      <span class="practical-label">🕐 开放时间</span>
                      <span class="practical-value">{{ item.practical_info.opening_hours }}</span>
                    </div>
                    <div v-if="item.practical_info.ticket_price" class="practical-item">
                      <span class="practical-label">🎫 门票</span>
                      <span class="practical-value">{{ item.practical_info.ticket_price }}</span>
                    </div>
                    <div v-if="item.practical_info.recommended_duration" class="practical-item">
                      <span class="practical-label">⏱️ 建议时长</span>
                      <span class="practical-value">{{ item.practical_info.recommended_duration }}</span>
                    </div>
                    <div v-if="item.practical_info.best_time_to_visit" class="practical-item">
                      <span class="practical-label">⭐ 最佳时间</span>
                      <span class="practical-value">{{ item.practical_info.best_time_to_visit }}</span>
                    </div>
                  </div>
                </div>

                <!-- Transport Info -->
                <div v-if="item.transport" class="item-transport">
                  <div class="transport-header">
                    <el-icon class="transport-icon"><Operation /></el-icon>
                    <span>交通方式</span>
                  </div>
                  <div class="transport-details">
                    <div class="transport-row">
                      <span class="transport-label">方式:</span>
                      <span class="transport-value">{{ item.transport.method }}</span>
                      <span class="transport-duration">({{ item.transport.duration }})</span>
                    </div>
                    <div v-if="item.transport.route" class="transport-row route-info">
                      <span class="transport-label">路线:</span>
                      <span class="transport-value">{{ item.transport.route }}</span>
                    </div>
                    <div v-if="item.transport.cost" class="transport-row">
                      <span class="transport-label">费用:</span>
                      <span class="transport-value">¥{{ item.transport.cost }}</span>
                    </div>
                    <div v-if="item.transport.tips" class="transport-tips">
                      <el-icon><InfoFilled /></el-icon>
                      {{ item.transport.tips }}
                    </div>
                  </div>
                </div>

                <!-- 餐厅详细信息 -->
                <div v-if="item.recommendations" class="item-restaurant">
                  <div class="restaurant-header">
                    <el-icon class="restaurant-icon"><Food /></el-icon>
                    <span class="restaurant-name">{{ item.recommendations.restaurant }}</span>
                  </div>
                  <div v-if="item.recommendations.address" class="restaurant-address">
                    <el-icon><LocationFilled /></el-icon>
                    {{ item.recommendations.address }}
                  </div>
                  <div v-if="item.recommendations.opening_hours" class="restaurant-hours">
                    <el-icon><Clock /></el-icon>
                    <span>营业时间: {{ item.recommendations.opening_hours }}</span>
                  </div>
                  <div v-if="item.recommendations.recommended_reason" class="restaurant-reason">
                    <el-icon><Star /></el-icon>
                    <span>{{ item.recommendations.recommended_reason }}</span>
                  </div>
                  <div v-if="item.recommendations.signature_dishes && item.recommendations.signature_dishes.length" class="restaurant-dishes">
                    <div class="dishes-title">招牌菜品:</div>
                    <div class="dishes-list">
                      <div v-for="(dish, idx) in item.recommendations.signature_dishes" :key="idx" class="dish-item">
                        <span class="dish-name">{{ dish.name }}</span>
                        <span class="dish-price">¥{{ dish.price }}</span>
                      </div>
                    </div>
                  </div>
                  <div v-if="item.recommendations.tips" class="restaurant-tips">
                    <el-icon><InfoFilled /></el-icon>
                    {{ item.recommendations.tips }}
                  </div>
                </div>

                <!-- 简单餐饮信息 -->
                <div v-else-if="item.dining" class="item-dining">
                  <el-icon class="dining-icon"><Food /></el-icon>
                  <span>{{ item.dining.recommended_area }}</span>
                  <span v-if="item.dining.estimated_cost" class="dining-cost">约 ¥{{ item.dining.estimated_cost }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="summary-section">
        <h3 class="section-title">
          <el-icon><TrendCharts /></el-icon>
          行程汇总
        </h3>
        <div class="summary-grid">
          <div class="summary-item">
            <el-icon class="summary-icon"><Place /></el-icon>
            <div class="summary-content">
              <div class="summary-label">总景点数</div>
              <div class="summary-value">{{ guide.summary.total_attractions }}个</div>
            </div>
          </div>
          <div class="summary-item">
            <el-icon class="summary-icon"><Wallet /></el-icon>
            <div class="summary-content">
              <div class="summary-label">日均预算</div>
              <div class="summary-value">¥{{ guide.summary.budget_per_day }}</div>
            </div>
          </div>
          <div class="summary-item">
            <el-icon class="summary-icon"><House /></el-icon>
            <div class="summary-content">
              <div class="summary-label">住宿区域</div>
              <div class="summary-value">{{ guide.summary.accommodation_area }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 智能体生成内容展示 -->
      <div class="agent-results-section">
        <h3 class="section-title">
          <el-icon><View /></el-icon>
          智能体分析过程
        </h3>
        <div class="agent-results-list">
          <div
            v-for="(result, index) in stagedPlanner.stepResults"
            :key="index"
            class="agent-result-item"
            :class="{ expanded: result.expanded }"
          >
            <div class="result-header" @click="toggleResult(index)">
              <div class="result-title-row">
                <el-icon class="result-icon" :class="getAgentIconClass(result.agent)">
                  <component :is="getAgentIcon(result.agent)" />
                </el-icon>
                <div class="result-title-info">
                  <div class="result-title">{{ result.title }}</div>
                  <div class="result-agent">{{ result.agent }}</div>
                </div>
                <el-icon class="expand-icon" :class="{ rotated: result.expanded }">
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
            <div class="result-content" v-if="result.expanded">
              <div class="result-summary">{{ result.summary }}</div>
              <div class="result-description" v-if="result.llm_description">
                {{ result.llm_description }}
              </div>
              <div class="result-data" v-if="result.data && Object.keys(result.data).length > 0">
                <el-collapse>
                  <el-collapse-item title="查看详细数据" name="data">
                    <pre class="data-preview">{{ JSON.stringify(result.data, null, 2) }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions">
        <el-button size="large" class="action-btn" @click="handleSave">
          <el-icon><FolderOpened /></el-icon>
          保存到攻略中心
        </el-button>
        <el-button type="primary" size="large" class="action-btn action-btn-primary" @click="handleRestart">
          <el-icon><Refresh /></el-icon>
          开始新的规划
        </el-button>
      </div>
    </div>

    <!-- 保存成功提示 -->
    <el-dialog v-model="saveDialogVisible" title="保存成功" width="400px">
      <div class="save-success-content">
        <el-icon class="success-icon-dialog"><CircleCheck /></el-icon>
        <p>攻略已保存到攻略中心</p>
        <el-button type="primary" @click="goToGuideCenter">前往查看</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import {
  Download,
  Share,
  Refresh,
  CircleCheck,
  Wallet,
  Ticket,
  Operation,
  Food,
  House,
  Calendar,
  Odometer,
  LocationFilled,
  TrendCharts,
  Place,
  Box,
  ChatLineSquare,
  InfoFilled,
  Sunny,
  Moon,
  Cloudy,
  FolderOpened,
  Clock,
  Loading,
  View,
  ArrowRight,
  User,
  Location,
  Trophy,
  Brush,
  Guide,
  Tools,
  Star,
  Picture
} from '@element-plus/icons-vue'
import { getAttractionImageWithCache } from '@/api/travel/images'
import { saveGuide, downloadGuidePDF } from '@/api/travel/guides'
import { generateDetailedGuideStream, type StreamEvent } from '@/api/travel/streamingGuide'
import AgentGenerationProgress from '@/components/AgentGenerationProgress.vue'
import {
  getAttractionDetails,
  getRestaurantRecommendation,
  getTransportInfo
} from '@/utils/smartTravelContent'
import { useStagedPlannerStore } from '@/stores/stagedPlanner'

const router = useRouter()
const stagedPlanner = useStagedPlannerStore()

const props = defineProps<{
  guide: any
}>()

const emit = defineEmits<{
  restart: []
}>()

const saveDialogVisible = ref(false)
const savedGuideId = ref('')

// 加载状态
const isInitialLoading = ref(true)  // 初始加载状态
const showProgress = ref(false)      // 是否显示进度弹窗
const isContentReady = ref(false)    // 内容是否完全准备好
const progressRef = ref<InstanceType<typeof AgentGenerationProgress>>()

// 为攻略添加景点图片
interface ScheduleItemWithImage {
  time_range: string
  period: string
  activity: string
  location?: string
  description?: string
  transport?: any
  ticket?: any
  dining?: any
  imageUrl?: string
  imageLoading?: boolean
  city?: string
}

interface DayWithImages {
  day: number
  title: string
  date: string
  pace: string
  daily_budget: number
  schedule: ScheduleItemWithImage[]
}

const guideWithImages = ref<DayWithImages[]>([])
const imagesLoading = ref(0)  // 正在加载的图片数量

// 图片加载状态追踪（防止重复加载）
const loadedImages = new Set<string>()
const loadingImages = new Map<string, Promise<string>>()

// 生成图片唯一标识
const getImageKey = (attraction: string, city: string): string => {
  return `${attraction}:${city}`
}

// 预设图片（用于立即显示，避免等待API）
const getPresetImage = (activityName: string, city: string): string => {
  // 为常见景点提供预设图片（高质量Unsplash图片）
  const presetImages: Record<string, string> = {
    // 成都
    '大熊猫繁育研究基地': 'https://images.unsplash.com/photo-1564349680130-6dd6a3b71e18?w=400&q=80',
    '熊猫基地': 'https://images.unsplash.com/photo-1564349680130-6dd6a3b71e18?w=400&q=80',
    '宽窄巷子': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',
    '锦里': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',
    '武侯祠': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',
    '杜甫草堂': 'https://images.unsplash.com/photo-1467880705-1c937a43ee75?w=400&q=80',
    '春熙路': 'https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80',

    // 北京
    '故宫': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80',
    '长城': 'https://images.unsplash.com/photo-1508804055797-1dd1497653b2?w=400&q=80',
    '天坛': 'https://images.unsplash.com/photo-1599571236865-327ad48e6b69?w=400&q=80',
    '颐和园': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',

    // 上海
    '外滩': 'https://images.unsplash.com/photo-1548940003-8266a381af4c?w=400&q=80',
    '东方明珠': 'https://images.unsplash.com/photo-1548940003-8266a381af4c?w=400&q=80',
    '豫园': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',

    // 西安
    '兵马俑': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80',
    '大雁塔': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80',
    '古城墙': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80',

    // 杭州
    '西湖': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80',
    '雷峰塔': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80',
    '灵隐寺': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',

    // 桂林
    '漓江': 'https://images.unsplash.com/photo-1557424447-218bcce82d2d?w=400&q=80',
    '象鼻山': 'https://images.unsplash.com/photo-1557424447-218bcce82d2d?w=400&q=80',
    '阳朔': 'https://images.unsplash.com/photo-1557424447-218bcce82d2d?w=400&q=80',

    // 三亚
    '亚龙湾': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80',
    '天涯海角': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
    '蜈支洲岛': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80',

    // 黄山
    '迎客松': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
    '天都峰': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '光明顶': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
    '莲花峰': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '西海大峡谷': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',

    // 张家界
    '张家界国家森林公园': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',
    '张家界': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',
    '天门山': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '大溪地玻璃桥': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80',
    '玻璃桥': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80',
    '云天渡': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80',
    '宝峰湖': 'https://images.unsplash.com/photo-1409458661355-89fccc3d8920?w=400&q=80',
    '黄龙洞': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '金鞭溪': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
    '袁家界': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',
    '天子山': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '黄石寨': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',

    // 通用景点类型（根据活动类型关键词）
    '古镇': 'https://images.unsplash.com/photo-1543085830-9814b1f3a900?w=400&q=80',
    '山': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80',
    '水': 'https://images.unsplash.com/photo-1409458661355-89fccc3d8920?w=400&q=80',
    '公园': 'https://images.unsplash.com/photo-1490786778127-891bc8d89c95?w=400&q=80',
    '街': 'https://images.unsplash.com/photo-1496417263034-43cfaa8c8f74?w=400&q=80',
  }

  // 先精确匹配
  if (presetImages[activityName]) {
    return presetImages[activityName]
  }

  // 模糊匹配
  for (const [key, url] of Object.entries(presetImages)) {
    if (activityName.includes(key)) {
      return url
    }
  }

  // 通用城市图片（最后兜底）
  const cityImages: Record<string, string> = {
    '成都': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=400&q=80',
    '北京': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80',
    '上海': 'https://images.unsplash.com/photo-1548940003-8266a381af4c?w=400&q=80',
    '杭州': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=400&q=80',
    '三亚': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400&q=80',
    '西安': 'https://images.unsplash.com/photo-1528164344705-47542687000d?w=400&q=80',
    '黄山': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
    '张家界': 'https://images.unsplash.com/photo-1548264523-21714b07302d?w=400&q=80',
  }

  return cityImages[city] || cityImages['成都']
}

// 获取景点图片（优化版：先显示内容，图片异步加载）
const loadAttractionImages = async () => {
  if (!props.guide || !props.guide.daily_itineraries) {
    return
  }

  const guideCopy = JSON.parse(JSON.stringify(props.guide))

  // 🔥 第一步：立即显示预设图片（不等待API）
  guideWithImages.value = guideCopy.daily_itineraries.map((day: any) => ({
    ...day,
    schedule: day.schedule.map((item: any) => {
      // 如果后端已经提供了 image_url，直接使用
      if (item.image_url) {
        return {
          ...item,
          imageUrl: item.image_url,
          imageLoading: false
        }
      }

      // 如果后端没有提供，使用预设图片作为后备
      return {
        ...item,
        imageUrl: getPresetImage(
          item.activity || item.attraction_name || item.location,
          props.guide.destination
        ),
        imageLoading: true  // 标记为正在加载真实图片
      }
    })
  }))

  // 标记内容已准备好
  isContentReady.value = true
  isInitialLoading.value = false

  console.log('✅ 图片加载完成：使用预设图片快速显示')

  // 🔥 第二步：后台异步加载真实图片（不阻塞显示）
  loadRealImagesForGuide()
}

// 异步加载真实图片（替换预设图片）- 简化版，类似 DestinationCards
const loadRealImagesForGuide = async () => {
  console.log('🔄 [后台加载] 开始异步获取真实图片...')

  // 餐饮活动关键词（不加载图片）
  const diningKeywords = ['午餐', '晚餐', '用餐', '中餐', '餐厅', '午饭', '晚饭']
  const diningPeriods = ['lunch', 'dinner']

  // 收集所有需要加载图片的景点（去重）
  const attractionsToLoad = new Map<string, Array<{ dayIndex: number; itemIndex: number }>>()

  guideWithImages.value.forEach((day: any, dayIndex: number) => {
    day.schedule.forEach((item: any, itemIndex: number) => {
      const activityName = item.activity || item.location || ''
      const period = item.period || ''

      // 检查是否为餐饮活动
      const isDining = diningPeriods.includes(period) ||
                       diningKeywords.some(keyword => activityName.includes(keyword))

      // 餐饮活动不加载图片
      if (isDining) {
        if (guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
          guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
        }
        return
      }

      // 收集景点（按名称分组，同一景点只调用一次API）
      if (!attractionsToLoad.has(activityName)) {
        attractionsToLoad.set(activityName, [])
      }
      attractionsToLoad.get(activityName)!.push({ dayIndex, itemIndex })
    })
  })

  console.log(`🔄 [后台加载] 共 ${attractionsToLoad.size} 个独特景点需要加载图片`)

  // 逐个加载景点图片
  for (const [attractionName, positions] of attractionsToLoad) {
    try {
      console.log(`🔄 [后台加载] 正在获取 ${attractionName} 的真实图片...`)

      const city = extractCityFromGuide()
      const imageUrl = await getAttractionImageWithCache(attractionName, city, 400, 300)

      console.log(`✅ [后台加载] ${attractionName} 图片获取成功: ${imageUrl?.substring(0, 50)}...`)

      // 更新所有使用此景点的位置
      positions.forEach(({ dayIndex, itemIndex }) => {
        if (guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
          guideWithImages.value[dayIndex].schedule[itemIndex].imageUrl = imageUrl
          guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
        }
      })
    } catch (error) {
      console.warn(`⚠️ [后台加载] ${attractionName} 图片获取失败，保留预设图片:`, error)
      // 失败时保持预设图片，标记为加载完成
      positions.forEach(({ dayIndex, itemIndex }) => {
        if (guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
          guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
        }
      })
    }
  }

  console.log('✅ [后台加载] 所有图片加载完成')
}

// 后台轮询更新图片
const updateInterval = ref<number | null>(null)
const updateAttempts = ref(0)
const MAX_UPDATE_ATTEMPTS = 6  // 最多轮询6次（30秒）
const UPDATE_INTERVAL = 5000  // 每5秒检查一次

const startBackgroundImageUpdate = () => {
  console.log('🔄 [后台更新] 启动后台图片更新轮询...')
  console.log(`🔄 [后台更新] 更新间隔: ${UPDATE_INTERVAL}ms, 最大尝试次数: ${MAX_UPDATE_ATTEMPTS}`)

  // 清除之前的轮询
  if (updateInterval.value) {
    console.log('🔄 [后台更新] 清除之前的轮询')
    clearInterval(updateInterval.value)
  }

  updateAttempts.value = 0

  updateInterval.value = window.setInterval(async () => {
    updateAttempts.value++
    console.log(`🔄 [后台更新] ========== 第 ${updateAttempts.value} 次检查开始 ==========`)

    if (updateAttempts.value > MAX_UPDATE_ATTEMPTS) {
      console.log('⏰ [后台更新] 达到最大尝试次数，停止轮询')
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
        updateInterval.value = null
      }
      return
    }

    try {
      // 调用后端API获取最新图片
      const hasUpdates = await checkAndUpdateImages()

      if (hasUpdates) {
        console.log('✅ [后台更新] 本轮有图片更新成功')
      } else {
        console.log('ℹ️ [后台更新] 本轮没有图片更新')
      }

      // 检查是否所有图片都已更新
      const totalImages = guideWithImages.value.reduce((count, day) => {
        return count + day.schedule.filter(item =>
          item.image_source !== 'preset' &&
          item.image_source !== undefined &&
          item.period !== 'lunch' &&
          item.period !== 'dinner'
        ).length
      }, 0)

      const presetImages = guideWithImages.value.reduce((count, day) => {
        return count + day.schedule.filter(item =>
          item.image_source === 'preset' &&
          item.period !== 'lunch' &&
          item.period !== 'dinner'
        ).length
      }, 0)

      console.log(`📊 [后台更新] 图片统计: 真实图=${totalImages}, 预设图=${presetImages}`)

      // 如果所有图片都已更新为真实图片，停止轮询
      if (presetImages === 0) {
        console.log('✅ [后台更新] 所有图片已更新为真实图片，停止轮询')
        if (updateInterval.value) {
          clearInterval(updateInterval.value)
          updateInterval.value = null
        }
      }

    } catch (error) {
      console.error('❌ [后台更新] 图片更新检查失败:', error)
    }

    console.log(`🔄 [后台更新] ========== 第 ${updateAttempts.value} 次检查结束 ==========\n`)
  }, UPDATE_INTERVAL)

  console.log('✅ [后台更新] 轮询定时器已启动')
}

// 检查并更新图片
const checkAndUpdateImages = async (): Promise<boolean> => {
  console.log('[图片更新] 开始检查图片更新...')

  if (!props.guide || !props.guide.destination) {
    console.log('[图片更新] 没有攻略数据，跳过更新')
    return false
  }

  let updateCount = 0
  const attractionsToUpdate: Array<{ name: string; dayIndex: number; itemIndex: number }> = []

  // 收集所有需要更新的景点
  guideWithImages.value.forEach((day: any, dayIndex: number) => {
    day.schedule.forEach((item: any, itemIndex: number) => {
      const isPreset = item.image_source === 'preset'
      const hasActivity = item.activity || item.location
      const isNotDining = item.period !== 'lunch' && item.period !== 'dinner'

      console.log(`[图片更新] 检查: ${item.activity}, source=${item.image_source}, period=${item.period}`)

      // 只更新来源为 preset 的景点图片
      if (isPreset && hasActivity && isNotDining) {
        attractionsToUpdate.push({
          name: item.activity || item.location,
          dayIndex,
          itemIndex
        })
      }
    })
  })

  console.log(`[图片更新] 需要更新的景点数量: ${attractionsToUpdate.length}`)

  if (attractionsToUpdate.length === 0) {
    console.log('[图片更新] 没有需要更新的景点')
    return false
  }

  // 批量检查图片更新
  for (const attraction of attractionsToUpdate) {
    try {
      console.log(`[图片更新] 正在获取 ${attraction.name} 的真实图片...`)

      const imageUrl = await getAttractionImageWithCache(
        attraction.name,
        props.guide.destination,
        400,
        300
      )

      console.log(`[图片更新] ${attraction.name} API返回: ${imageUrl?.substring(0, 60)}...`)

      // 如果获取到新的图片URL（不同于预设图片）
      const currentItem = guideWithImages.value[attraction.dayIndex].schedule[attraction.itemIndex]
      const currentUrl = currentItem.imageUrl

      if (imageUrl && imageUrl !== currentUrl && !imageUrl.includes('placehold.co')) {
        console.log(`✨ [图片更新] 更新图片: ${attraction.name}`)
        console.log(`   旧URL: ${currentUrl}`)
        console.log(`   新URL: ${imageUrl}`)

        guideWithImages.value[attraction.dayIndex].schedule[attraction.itemIndex].imageUrl = imageUrl
        guideWithImages.value[attraction.dayIndex].schedule[attraction.itemIndex].image_source = 'api'
        updateCount++
      } else {
        console.log(`[图片更新] ${attraction.name} 图片未变化或为占位图，跳过`)
      }
    } catch (error) {
      console.error(`[图片更新] ${attraction.name} 更新失败:`, error)
      // 单个景点更新失败不影响其他景点
      continue
    }
  }

  console.log(`[图片更新] 更新完成，共更新 ${updateCount} 张图片`)
  return updateCount > 0
}

// 异步加载真实图片（替换预设图片）
const loadRealImagesAsync = async (days: any[]) => {
  const imagePromises: Promise<void>[] = []

  // 餐饮活动关键词（不加载图片）
  const diningKeywords = ['午餐', '晚餐', '用餐', '中餐', '晚餐', '餐厅', '午饭', '晚饭']
  const diningPeriods = ['lunch', 'dinner']

  days.forEach((day: any, dayIndex: number) => {
    day.schedule.forEach((item: any, itemIndex: number) => {
      const activityName = item.activity || ''
      const period = item.period || ''

      // 检查是否为餐饮活动
      const isDining = diningPeriods.includes(period) ||
                       diningKeywords.some(keyword => activityName.includes(keyword))

      // 餐饮活动不加载图片
      if (isDining) {
        if (guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
          guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
        }
        return
      }

      // 获取景点名称
      const attractionName = item.attraction_name || item.location || item.activity
      const city = extractCityFromGuide()

      // 使用活动名称作为唯一key（同一活动在不同天使用同一张图片）
      const imageKey = attractionName

      // 检查是否已经加载过或正在加载
      if (loadedImages.has(imageKey)) {
        // 已加载，直接使用本地缓存的URL
        const cachedUrl = imageUrlCache.get(imageKey)
        if (cachedUrl && guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
          guideWithImages.value[dayIndex].schedule[itemIndex].imageUrl = cachedUrl
          guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
        }
        return
      }

      // 检查是否正在加载
      if (loadingImages.has(imageKey)) {
        // 等待现有加载完成
        imagePromises.push(
          loadingImages.get(imageKey)!.then(url => {
            if (guideWithImages.value[dayIndex]?.schedule[itemIndex]) {
              guideWithImages.value[dayIndex].schedule[itemIndex].imageUrl = url
              guideWithImages.value[dayIndex].schedule[itemIndex].imageLoading = false
            }
          })
        )
        return
      }

      // 开始加载
      imagesLoading.value++
      loadedImages.add(imageKey) // 标记为已加载（防止重复）

      const loadPromise = (async () => {
        try {
          // 使用更小的尺寸加快加载
          const imageUrl = await getAttractionImageWithCache(attractionName, city, 200, 150)

          // 保存到本地缓存
          imageUrlCache.set(imageKey, imageUrl)

          // 更新所有使用此图片的项
          guideWithImages.value.forEach((day: any, di: number) => {
            day.schedule.forEach((schedItem: any, si: number) => {
              const itemName = schedItem.attraction_name || schedItem.location || schedItem.activity
              if (itemName === attractionName && guideWithImages.value[di]?.schedule[si]) {
                guideWithImages.value[di].schedule[si].imageUrl = imageUrl
                guideWithImages.value[di].schedule[si].imageLoading = false
              }
            })
          })

          return imageUrl
        } catch (error) {
          console.warn('加载景点图片失败:', item.activity, error)
          // 失败不影响显示
          return ''
        } finally {
          imagesLoading.value--
        }
      })()

      loadingImages.set(imageKey, loadPromise)
      imagePromises.push(loadPromise)

      // 加载完成后从loadingImages中移除
      loadPromise.finally(() => {
        loadingImages.delete(imageKey)
      })
    })
  })

  // 等待所有图片加载完成（可选，用于统计）
  Promise.allSettled(imagePromises).then(() => {
    console.log('所有图片加载完成')
  })
}

// 从攻略中提取城市名称
const extractCityFromGuide = (): string => {
  // 尝试从攻略中获取目的地城市
  if (props.guide.destination) {
    return props.guide.destination
  }

  // 尝试从第一天行程中获取
  if (props.guide.daily_itineraries && props.guide.daily_itineraries[0]) {
    const firstLocation = props.guide.daily_itineraries[0].schedule[0]?.location
    if (firstLocation) {
      // 简单的城市提取（可以优化）
      return firstLocation.split(' ')[0]
    }
  }

  return '' // 如果找不到城市，返回空字符串
}

// 本地图片URL缓存（避免重复请求）
const imageUrlCache = new Map<string, string>()

// 判断是否应该显示图片（非餐饮活动）
const shouldShowImage = (item: any): boolean => {
  const diningKeywords = ['午餐', '晚餐', '用餐', '中餐', '餐厅', '午饭', '晚饭']
  const diningPeriods = ['lunch', 'dinner']

  const activityName = item.activity || ''
  const period = item.period || ''

  const isDining = diningPeriods.includes(period) ||
                   diningKeywords.some(keyword => activityName.includes(keyword))

  return !isDining && !!item.imageUrl
}

// 判断是否为餐饮活动（不加载图片）
const isDiningActivity = (item: any): boolean => {
  const diningKeywords = ['午餐', '晚餐', '用餐', '中餐', '晚餐', '餐厅', '午饭', '晚饭']
  const diningPeriods = ['lunch', 'dinner']

  const activityName = item.activity || ''
  const period = item.period || ''

  return diningPeriods.includes(period) ||
         diningKeywords.some(keyword => activityName.includes(keyword))
}

const getPeriodIcon = (period: string) => {
  const iconMap: Record<string, any> = {
    morning: Sunny,
    lunch: Food,
    afternoon: Cloudy,
    dinner: Food,
    evening: Moon
  }
  return iconMap[period] || Sunny
}

// 根据目的地获取模拟天气信息
const getDayWeather = (day: any) => {
  const destination = props.guide?.destination || ''
  const month = parseInt(day.date?.split('-')[1]) || 3

  // 不同城市的天气特点
  const weatherMap: Record<string, { condition: string; temp: string; icon: any }> = {
    '胡志明': { condition: '晴朗', temp: '28-35°C', icon: Sunny },
    '河内': { condition: '多云', temp: '22-28°C', icon: Cloudy },
    '岘港': { condition: '晴朗', temp: '25-30°C', icon: Sunny },
    '胡志明市': { condition: '晴朗', temp: '28-35°C', icon: Sunny },
    '杭州': { condition: '多云', temp: '15-22°C', icon: Cloudy },
    '北京': { condition: '晴朗', temp: '10-18°C', icon: Sunny },
    '西安': { condition: '多云', temp: '12-20°C', icon: Cloudy },
    '成都': { condition: '阴天', temp: '16-22°C', icon: Cloudy },
    '三亚': { condition: '晴朗', temp: '25-30°C', icon: Sunny },
    '上海': { condition: '小雨', temp: '14-20°C', icon: Cloudy },
    '厦门': { condition: '晴朗', temp: '18-25°C', icon: Sunny },
    '广州': { condition: '多云', temp: '20-28°C', icon: Cloudy },
    '深圳': { condition: '晴朗', temp: '22-30°C', icon: Sunny },
  }

  // 默认天气
  const defaultWeather = { condition: '晴朗', temp: '20-26°C', icon: Sunny }

  const weather = weatherMap[destination] || defaultWeather

  return `${weather.condition} ${weather.temp}`
}

// 获取天气图标
const getWeatherIcon = (day: any) => {
  const destination = props.guide?.destination || ''
  const weatherMap: Record<string, any> = {
    '胡志明': Sunny,
    '河内': Cloudy,
    '胡志明市': Sunny,
    '杭州': Cloudy,
    '北京': Sunny,
    '西安': Cloudy,
    '成都': Cloudy,
    '三亚': Sunny,
    '上海': Cloudy,
    '厦门': Sunny,
    '广州': Cloudy,
    '深圳': Sunny,
  }
  return weatherMap[destination] || Sunny
}

const handleSave = async () => {
  try {
    await saveGuideToServer()
    ElMessage.success('攻略保存成功！')
    saveDialogVisible.value = true
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

const saveGuideToServer = async () => {
  // 模拟用户ID（实际应从登录状态获取）
  const userId = 'demo_user'

  // 构建保存请求
  const saveRequest = {
    user_id: userId,
    title: props.guide.destination + ' ' + props.guide.total_days + '日攻略',
    destination: props.guide.destination || '未知目的地',
    total_days: props.guide.total_days || 0,
    guide_data: props.guide,
    budget: props.guide.budget_breakdown?.total_budget || 0,
    tags: [props.guide.destination, props.guide.total_days + '天'],
    is_public: false
  }

  // 调用保存API
  const response = await saveGuide(saveRequest)
  savedGuideId.value = response.guide_id

  return response
}

const goToGuideCenter = () => {
  saveDialogVisible.value = false
  router.push('/travel/guides')
}

const handleRestart = () => {
  emit('restart')
}

// 智能体结果展示相关函数
const toggleResult = (index: number) => {
  const result = stagedPlanner.stepResults[index]
  if (result) {
    result.expanded = !result.expanded
  }
}

const getAgentIcon = (agentName: string) => {
  // 根据智能体名称返回对应图标
  const iconMap: Record<string, any> = {
    'UserRequirementAnalyst': User,
    'DestinationMatcher': Location,
    'RankingScorer': Trophy,
    'StyleDesigner': Brush,
    'AttractionScheduler': Calendar,
    'TransportPlanner': Guide,
    'DiningRecommender': Food,
    'AccommodationAdvisor': House,
    'WeatherService': Cloudy,
    'default': Tools
  }
  return iconMap[agentName] || Tools
}

const getAgentIconClass = (agentName: string) => {
  // 根据智能体名称返回对应的CSS类
  const classMap: Record<string, string> = {
    'UserRequirementAnalyst': 'icon-analyst',
    'DestinationMatcher': 'icon-matcher',
    'RankingScorer': 'icon-scorer',
    'StyleDesigner': 'icon-designer',
    'AttractionScheduler': 'icon-scheduler',
    'TransportPlanner': 'icon-transport',
    'DiningRecommender': 'icon-dining',
    'AccommodationAdvisor': 'icon-accommodation'
  }
  return classMap[agentName] || 'icon-default'
}

onMounted(async () => {
  try {
    // 第一步：加载基础数据（图片异步加载）
    isInitialLoading.value = true
    loadAttractionImages()  // 不再等待，立即返回
    isInitialLoading.value = false

    // 第二步：开始流式生成详细内容
    await startStreamingGeneration()
  } catch (error) {
    console.error('初始化失败:', error)
    isInitialLoading.value = false
    // 即使失败也显示基础内容
    isContentReady.value = true
  }
})

// 🔥 组件卸载时清理定时器，防止内存泄漏
onUnmounted(() => {
  // 清理图片更新轮询定时器
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
    updateInterval.value = null
  }

  // 清理图片加载缓存
  loadedImages.clear()
  loadingImages.clear()
  imageUrlCache.clear()
})

// 监听guide变化，重新加载图片
watch(() => props.guide, (newGuide) => {
  if (newGuide && newGuide.daily_itineraries) {
    console.log('[详细攻略] 检测到攻略数据变化，重新加载')
    isContentReady.value = false
    loadAttractionImages()
  }
}, { immediate: false })

// 开始流式生成详细内容
const startStreamingGeneration = async () => {
  try {
    // TODO: 这个API endpoint暂时不存在，跳过流式生成
    // 直接使用已有的guide数据
    console.log('[详细攻略] 跳过流式生成，直接使用已有数据')

    // 模拟进度更新
    progressRef.value?.updateProgress(100, '详细内容已加载完成', '系统')

    // 标记内容为就绪状态
    isContentReady.value = true
    showProgress.value = false

    return
  } catch (error) {
    console.error('流式生成失败:', error)
    // 即使失败也显示基础内容
    isContentReady.value = true
    showProgress.value = false
  }
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 处理生成完成
const handleGenerationComplete = () => {
  setTimeout(() => {
    showProgress.value = false
    isContentReady.value = true
  }, 500)
}

// 加载详细攻略内容
const isLoadingDetails = ref(false)
const detailLoadingProgress = ref('')

const loadDetailedContent = async () => {
  if (!props.guide) return

  isLoadingDetails.value = true

  try {
    detailLoadingProgress.value = '正在生成详细攻略...'

    const response = await generateDetailedGuide(props.guide)

    if (response.success && response.detailed_guide) {
      // 合并详细信息到现有攻略
      mergeDetailedContent(response.detailed_guide)
      ElMessage.success('详细攻略生成完成！')
    }
  } catch (error) {
    console.warn('生成详细攻略失败，使用基础内容:', error)
    // 失败时使用基础内容
  } finally {
    isLoadingDetails.value = false
    detailLoadingProgress.value = ''
  }
}

// 合并详细内容
const mergeDetailedContent = (detailedGuide: any) => {
  console.log('[mergeDetailedContent] 输入数据:', detailedGuide)

  // 首先尝试从API获取的详细数据
  const detailedDays = detailedGuide.detailed_days || detailedGuide.daily_itineraries

  // 如果API没有返回详细数据，使用智能内容库
  const useSmartContent = !detailedDays || detailedDays.length === 0

  console.log('[mergeDetailedContent] 使用智能内容库:', useSmartContent)

  if (useSmartContent) {
    // 直接使用智能内容库
    mergeSmartContent()
    return
  }

  console.log('[mergeDetailedContent] 提取的每日行程:', detailedDays)

  if (!detailedDays) {
    console.warn('[mergeDetailedContent] 没有找到详细数据')
    return
  }

  console.log('[mergeDetailedContent] 当前 guideWithImages:', guideWithImages.value)

  // 将详细的每日信息合并到guideWithImages
  guideWithImages.value = guideWithImages.value.map((day: any) => {
    const detailedDay = detailedDays.find((d: any) => d.day === day.day)

    console.log(`[mergeDetailedContent] 第${day.day}天 - 详细数据:`, detailedDay)

    if (detailedDay) {
      // 合并schedule，添加详细信息
      const enhancedSchedule = day.schedule.map((item: any) => {
        // 在详细行程中找到对应的详细项
        const detailedItem = detailedDay.schedule?.find((d: any) =>
          d.time_range === item.time_range || d.period === item.period
        )

        console.log(`[mergeDetailedContent] 项目 ${item.activity} - 详细项:`, detailedItem)

        if (detailedItem && detailedItem.has_details) {
          // 合并详细信息
          const merged = {
            ...item,
            description: detailedItem.description || item.description,
            highlights: detailedItem.highlights || [],
            suggested_route: detailedItem.suggested_route || '',
            photography_spots: detailedItem.photography_spots || [],
            tips: detailedItem.tips || item.tips,
            recommendations: detailedItem.recommendations || item.recommendations,
            tickets: detailedItem.tickets || item.ticket,
            transport: detailedItem.transport || item.transport,
            hasDetails: true
          }

          console.log(`[mergeDetailedContent] 合并后的项目:`, merged)
          return merged
        }

        return item
      })

      // 添加当天贴士
      return {
        ...day,
        schedule: enhancedSchedule,
        tips: detailedDay.day_tips || {}
      }
    }

    return day
  })

  console.log('[mergeDetailedContent] 最终合并结果:', guideWithImages.value)
}

// 使用智能内容库合并详细内容
const mergeSmartContent = () => {
  console.log('[mergeSmartContent] 开始使用智能内容库')

  const destination = props.guide?.destination || ''
  console.log('[mergeSmartContent] 目的地:', destination)

  guideWithImages.value = guideWithImages.value.map((day: any) => {
    const enhancedSchedule = day.schedule.map((item: any) => {
      const period = item.period || ''
      const location = item.location || item.activity || ''

      console.log(`[mergeSmartContent] 处理项目: ${item.activity} (${period}) - 位置: ${location}`)

      const enhanced: any = { ...item, hasDetails: true }

      // 景点详情
      if (period === 'morning' || period === 'afternoon' || period === 'evening') {
        const attractionDetails = getAttractionDetails(destination, location)
        if (attractionDetails) {
          enhanced.description = attractionDetails.description
          enhanced.highlights = attractionDetails.highlights
          enhanced.suggested_route = attractionDetails.suggestedRoute
          enhanced.tickets = attractionDetails.tickets
          enhanced.tips = attractionDetails.tips
          console.log(`[mergeSmartContent] 找到景点详情: ${attractionDetails.name}`)
        } else {
          console.log(`[mergeSmartContent] 未找到景点详情: ${destination}/${location}`)
        }

        // 交通信息
        const transportInfo = getTransportInfo(destination)
        if (transportInfo) {
          enhanced.transport = transportInfo
        }
      }

      // 餐厅推荐
      if (period === 'lunch' || period === 'dinner') {
        const restaurantInfo = getRestaurantRecommendation(destination, period)
        if (restaurantInfo) {
          enhanced.recommendations = {
            restaurant: restaurantInfo.name,
            address: restaurantInfo.address,
            signature_dishes: restaurantInfo.signatureDishes,
            average_cost: restaurantInfo.averageCost,
            tips: restaurantInfo.tips
          }
          console.log(`[mergeSmartContent] 找到餐厅: ${restaurantInfo.name}`)
        } else {
          console.log(`[mergeSmartContent] 未找到餐厅: ${destination}/${period}`)
        }

        // 交通信息
        const transportInfo = getTransportInfo(destination)
        if (transportInfo) {
          enhanced.transport = transportInfo
        }
      }

      return enhanced
    })

    return {
      ...day,
      schedule: enhancedSchedule
    }
  })

  console.log('[mergeSmartContent] 智能内容合并完成')
}

// 图片加载成功处理（去重日志）
const loggedSuccessfulLoads = new Set<string>()
const handleImageLoad = (item: ScheduleItemWithImage) => {
  const logKey = `${item.activity}:${item.imageUrl}`
  if (!loggedSuccessfulLoads.has(logKey)) {
    console.log('图片加载成功:', item.activity)
    loggedSuccessfulLoads.add(logKey)
  }
}

// 图片加载失败处理
const loggedFailedLoads = new Set<string>()
const handleImageError = (item: ScheduleItemWithImage, event: Event) => {
  const logKey = item.activity
  if (!loggedFailedLoads.has(logKey)) {
    console.warn('图片加载失败:', item.activity)
    loggedFailedLoads.add(logKey)
  }
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.detailed-guide {
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
  background: linear-gradient(135deg, var(--color-primary) 0%, #6366F1 100%);
  min-height: 100vh;
  position: relative;
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.loading-content {
  text-align: center;
  color: white;
}

.loading-icon {
  font-size: 4rem;
  animation: spin 1.5s linear infinite;
  margin-bottom: 1rem;
}

.loading-content p {
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

/* ==================== */
/* Container              */
/* ==================== */
.container {
  max-width: 900px;
  margin: 0 auto;
}

/* ==================== */
/* Images Loading Banner   */
/* ==================== */

.images-loading-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  padding: 12px 24px;
  margin-bottom: 20px;
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
  animation: fadeInDown 0.3s ease-out;
}

.images-loading-banner .loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== */
/* Success Banner         */
/* ==================== */
.success-banner {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: var(--shadow-xl), var(--shadow-soft);
  animation: fadeInUp 0.4s ease-out;
}

.success-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-success) 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  font-size: 1.75rem;
  flex-shrink: 0;
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

.success-content h2 {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 0.25rem;
}

.success-content p {
  color: #64748B;
  font-size: 1rem;
}

/* ==================== */
/* Budget Summary         */
/* ==================== */
.budget-summary {
  margin-bottom: 2rem;
  animation: fadeInUp 0.5s ease-out 0.1s both;
}

.budget-card {
  background: linear-gradient(135deg, var(--color-primary) 0%, #6366F1 100%);
  border-radius: 20px;
  padding: 2rem;
  color: var(--color-white);
  box-shadow: var(--shadow-xl), var(--shadow-soft);
}

.budget-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.budget-icon {
  font-size: 1.5rem;
}

.budget-title {
  font-size: 0.875rem;
  opacity: 0.9;
}

.budget-amount {
  font-family: 'Bodoni Moda', serif;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.budget-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.breakdown-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.item-icon {
  font-size: 1.25rem;
}

.item-icon.attractions { color: #FBBF24; }
.item-icon.transport { color: #60A5FA; }
.item-icon.dining { color: #F97316; }
.item-icon.accommodation { color: #34D399; }

.item-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-label {
  font-size: 0.75rem;
  opacity: 0.8;
}

.item-value {
  font-weight: 600;
  font-size: 0.9375rem;
}

/* ==================== */
/* Section Title          */
/* ==================== */
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Bodoni Moda', serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-white);
  margin-bottom: 1rem;
}

.section-title .el-icon {
  color: var(--color-cta);
  font-size: 1.375rem;
}

/* ==================== */
/* Itineraries            */
/* ==================== */
.itineraries {
  margin-bottom: 2rem;
  animation: fadeInUp 0.5s ease-out 0.2s both;
}

.day-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}

.day-card:hover {
  box-shadow: var(--shadow-xl);
  transform: translateY(-2px);
}

.day-header {
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  padding: 1rem 1.5rem;
  display: flex;
  gap: 1rem;
}

.day-number {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-white);
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.day-info {
  flex: 1;
}

.day-title {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.375rem;
}

.day-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748B;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.weather-info {
  color: #F97316;
  font-weight: 500;
}

.weather-info .el-icon {
  color: #F97316;
}

.day-schedule {
  padding: 1rem 1.5rem;
}

.schedule-item {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #F1F5F9;
}

.schedule-item:last-child {
  border-bottom: none;
}

.item-time {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 0.9375rem;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-period-icon {
  font-size: 1.25rem;
}

.item-period-icon.period-morning { color: #FBBF24; }
.item-period-icon.period-lunch { color: #F97316; }
.item-period-icon.period-afternoon { color: #60A5FA; }
.item-period-icon.period-dinner { color: #8B5CF6; }
.item-period-icon.period-evening { color: #6366F1; }

.item-activity {
  font-weight: 600;
  color: #0F172A;
}

/* ==================== */
/* Item Image (NEW)       */
/* ==================== */
.item-image {
  width: 100%;
  min-height: 200px;
  max-height: 500px;
  border-radius: 12px;
  overflow: hidden;
  background: #f0f0f0;
  margin-top: 0.5rem;
}

.attraction-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: transform 0.3s ease;
  cursor: pointer;
  display: block;
}

.item-image:hover .attraction-image {
  transform: scale(1.02);
}

/* 图片加载占位符 - 已禁用 */
.image-placeholder {
  width: 100%;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
}

.placeholder-icon {
  font-size: 48px;
  color: #94a3b8;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

/* 旧的图片样式已替换为 .attraction-image */
.item-location {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #64748B;
}

.item-description {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.6;
}

.item-transport,
.item-ticket,
.item-dining {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  background: #F0F9FF;
  border-radius: 8px;
}

.transport-icon { color: var(--color-primary); }
.ticket-icon { color: var(--color-cta); }
.dining-icon { color: #F97316; }

.transport-info {
  display: flex;
  gap: 0.25rem;
}

.transport-cost,
.dining-cost {
  color: var(--color-primary);
  font-weight: 600;
  margin-left: auto;
}

/* ==================== */
/* Summary Section        */
/* ==================== */
.summary-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.5s ease-out 0.3s both;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #F0F9FF;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.summary-item:hover {
  background: #E0F2FE;
  transform: translateY(-2px);
}

.summary-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.875rem;
  color: #64748B;
}

.summary-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0F172A;
}

/* ==================== */
/* Agent Results Section  */
/* ==================== */
.agent-results-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.5s ease-out 0.4s both;
}

.agent-results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.agent-result-item {
  background: #F8FAFC;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #E2E8F0;
}

.agent-result-item.expanded {
  background: #FFFFFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  padding: 1rem 1.25rem;
  cursor: pointer;
  user-select: none;
}

.result-header:hover {
  background: #F1F5F9;
}

.result-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.result-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.result-icon.icon-analyst {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.result-icon.icon-matcher {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.result-icon.icon-scorer {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.result-icon.icon-designer {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.result-icon.icon-scheduler {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.result-icon.icon-transport {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
  color: white;
}

.result-icon.icon-dining {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: white;
}

.result-icon.icon-accommodation {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
}

.result-icon.icon-default {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  color: white;
}

.result-title-info {
  flex: 1;
}

.result-title {
  font-size: 1rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.25rem;
}

.result-agent {
  font-size: 0.875rem;
  color: #64748B;
}

.expand-icon {
  font-size: 1.25rem;
  color: #94A3B8;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(90deg);
}

.result-content {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #E2E8F0;
  margin-top: 0.5rem;
  padding-top: 1rem;
}

.result-summary {
  font-size: 0.9375rem;
  color: #475569;
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.result-description {
  font-size: 0.9375rem;
  color: #0F172A;
  line-height: 1.7;
  background: #F8FAFC;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  white-space: pre-wrap;
}

.result-data {
  margin-top: 0.75rem;
}

.data-preview {
  background: #1E293B;
  color: #E2E8F0;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

/* ==================== */
/* Actions                */
/* ==================== */
.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 1rem 0 2rem;
  animation: fadeInUp 0.5s ease-out 0.5s both;
}

.action-btn {
  min-width: 140px;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #0F172A !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn:hover {
  background: var(--color-white);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.action-btn-primary {
  background: linear-gradient(135deg, var(--color-cta) 0%, #EA580C 100%);
  border: none;
  color: var(--color-white) !important;
}

.action-btn-primary:hover {
  background: linear-gradient(135deg, #FB923C 0%, var(--color-cta) 100%);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
}

/* ==================== */
/* Save Dialog            */
/* ==================== */
.save-success-content {
  text-align: center;
  padding: 1rem;
}

.success-icon-dialog {
  font-size: 4rem;
  color: var(--color-success);
  margin-bottom: 1rem;
}

.save-success-content p {
  font-size: 1.125rem;
  color: #475569;
  margin-bottom: 1.5rem;
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
  .success-banner {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .budget-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .day-header {
    flex-direction: column;
    text-align: center;
  }

  .day-meta {
    justify-content: center;
    flex-wrap: wrap;
  }

  .schedule-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .item-time {
    font-size: 0.875rem;
    color: #64748B;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .packing-list {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .day-card,
  .breakdown-item,
  .summary-item,
  .packing-item,
  .action-btn {
    animation: none;
    transition: none;
  }

  .day-card:hover,
  .breakdown-item:hover,
  .summary-item:hover,
  .action-btn:hover {
    transform: none;
  }
}

/* ==================== */
/* Detailed Content Styles */
/* ==================== */
.item-description {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(14, 165, 233, 0.05);
  border-radius: 8px;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.6;
}

.item-highlights {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
  border-radius: 8px;
  border-left: 3px solid #F59E0B;
}

.highlights-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #B45309;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.highlights-list {
  margin: 0;
  padding-left: 1.25rem;
  list-style: disc;
}

.highlights-list li {
  color: #78716C;
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 0.25rem;
}

/* ==================== */
/* Practical Info          */
/* ==================== */
.item-practical {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
  border-radius: 8px;
  border-left: 3px solid #0EA5E9;
}

.practical-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #0369A1;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.practical-icon {
  color: #0EA5E9;
}

.practical-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.practical-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.practical-label {
  font-size: 0.75rem;
  color: #64748B;
  font-weight: 500;
}

.practical-value {
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.4;
}

/* ==================== */
/* Transport Details      */
/* ==================== */
.item-transport {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(96, 165, 250, 0.08);
  border-radius: 8px;
}

.transport-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1E40AF;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.transport-icon {
  color: #3B82F6;
}

.transport-details {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.transport-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.transport-row.route-info {
  flex-direction: column;
  align-items: flex-start;
  background: rgba(59, 130, 246, 0.05);
  padding: 0.5rem;
  border-radius: 6px;
}

.transport-row.route-info .transport-label {
  margin-bottom: 0.25rem;
}

.transport-label {
  color: #64748B;
  font-weight: 500;
}

.transport-value {
  color: #334155;
  font-weight: 500;
}

.transport-duration {
  color: #94A3B8;
  font-size: 0.8rem;
}

.transport-cost {
  color: #059669;
  font-weight: 600;
  margin-left: auto;
}

.transport-tips {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  font-size: 0.8rem;
  color: #475569;
}

.transport-tips .el-icon {
  flex-shrink: 0;
  margin-top: 0.1rem;
  color: #3B82F6;
}

/* ==================== */
/* Ticket Details         */
/* ==================== */
.item-ticket {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  border-radius: 8px;
}

.ticket-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #065F46;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.ticket-icon {
  color: #10B981;
}

.ticket-details {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.ticket-price {
  font-size: 1.1rem;
  font-weight: 700;
  color: #059669;
}

.ticket-notes {
  font-size: 0.8rem;
  color: #64748B;
  line-height: 1.4;
}

/* ==================== */
/* Restaurant Details     */
/* ==================== */
.item-restaurant {
  margin-top: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, rgba(251, 146, 60, 0.05) 100%);
  border-radius: 8px;
  border-left: 3px solid #F97316;
}

.restaurant-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.restaurant-icon {
  color: #F97316;
  font-size: 1.1rem;
}

.restaurant-name {
  font-weight: 700;
  color: #C2410C;
  font-size: 1rem;
}

.restaurant-address {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #64748B;
  margin-bottom: 0.5rem;
}

.restaurant-hours {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #0EA5E9;
  margin-bottom: 0.5rem;
}

.restaurant-reason {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #F59E0B;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 6px;
}

.restaurant-reason .el-icon {
  color: #F59E0B;
}

.restaurant-dishes {
  margin-bottom: 0.75rem;
}

.dishes-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #9A3412;
  margin-bottom: 0.4rem;
}

.dishes-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.dish-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.6rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
}

.dish-name {
  font-size: 0.85rem;
  color: #475569;
}

.dish-price {
  font-weight: 600;
  color: #EA580C;
  font-size: 0.85rem;
}

.restaurant-tips {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  font-size: 0.8rem;
  color: #475569;
  margin-bottom: 0.5rem;
}

.restaurant-tips .el-icon {
  flex-shrink: 0;
  margin-top: 0.1rem;
  color: #F97316;
}

.restaurant-cost {
  text-align: right;
  font-size: 0.9rem;
  font-weight: 600;
  color: #059669;
}

/* ==================== */
/* Daily Tips Section     */
/* ==================== */
.day-tips {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 12px;
  border: 1px dashed rgba(99, 102, 241, 0.3);
}

.tips-section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #4F46E5;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #64748B;
  line-height: 1.5;
}

.tip-item .el-icon {
  flex-shrink: 0;
  margin-top: 0.15rem;
  color: #818CF8;
}

.photography-tips {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.08) 0%, rgba(244, 114, 182, 0.05) 100%);
  border-radius: 8px;
}

.photo-tips-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  color: #BE185D;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.photo-tips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.photo-tip-item {
  padding: 0.3rem 0.6rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  font-size: 0.8rem;
  color: #9D174D;
}

/* ==================== */
/* Responsive Styles      */
/* ==================== */
@media (max-width: 768px) {
  .budget-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .restaurant-dishes .dish-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
}
</style>
