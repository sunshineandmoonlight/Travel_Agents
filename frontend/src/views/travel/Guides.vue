<template>
  <div class="guides-page">
    <div class="guides-container">
      <!-- 页面标题 -->
      <div class="guides-header">
        <div class="header-content">
          <h1 class="guides-title">我的攻略</h1>
          <p class="guides-subtitle">管理和分享您的旅行攻略</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" size="large" @click="createNewGuide">
            <el-icon><Plus /></el-icon>
            新建攻略
          </el-button>
        </div>
      </div>

      <!-- 筛选和排序 -->
      <div class="guides-filter">
        <div class="filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索攻略标题、目的地..."
            :prefix-icon="Search"
            size="large"
            class="search-input"
            clearable
          />
        </div>
        <div class="filter-right">
          <el-select v-model="filterStatus" placeholder="状态" size="large" class="filter-select">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
          </el-select>
          <el-select v-model="sortBy" size="large" class="filter-select">
            <el-option label="最新创建" value="created" />
            <el-option label="最多访问" value="views" />
            <el-option label="最近更新" value="updated" />
          </el-select>
        </div>
      </div>

      <!-- 攻略列表 -->
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在加载攻略...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredGuides.length === 0" class="empty-state">
        <el-empty description="暂无攻略">
          <el-button type="primary" @click="loadGuides">重新加载</el-button>
          <el-button @click="createNewGuide">创建新攻略</el-button>
        </el-empty>
      </div>

      <!-- 攻略卡片列表 -->
      <div v-if="!loading && filteredGuides.length > 0" class="guides-grid">
        <div
          v-for="guide in filteredGuides"
          :key="guide.id"
          class="guide-card"
          @click="openGuideDetail(guide)"
        >
          <!-- 攻略封面 -->
          <div class="guide-cover">
            <!-- 占位符（始终显示，作为背景） -->
            <div class="cover-placeholder-bg">
              <svg viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="url(#cover-gradient)" />
                <path d="M24 16L28 22H36L30 28L32 36L24 31L16 36L18 28L12 22H20L24 16Z" fill="white" fill-opacity="0.3"/>
                <defs>
                  <linearGradient id="cover-gradient" x1="0" y1="0" x2="48" y2="48">
                    <stop offset="0%" stop-color="#0EA5E9"/>
                    <stop offset="100%" stop-color="#F97316"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <!-- 实际图片（加载后覆盖在占位符上） -->
            <div v-if="guide.cover" class="image-wrapper" :class="{ 'image-loaded': isImageLoaded[guide.id] }">
              <img
                :src="guide.cover"
                :alt="guide.title"
                @load="(e) => handleImageLoad(e, guide.id)"
                @error="(e) => handleImageError(e, guide.id)"
                :class="{ 'img-loaded': isImageLoaded[guide.id] }"
                loading="lazy"
              />
            </div>
            <div class="cover-badge">
              <el-tag :type="getStatusType(guide.status)" size="small" effect="plain">
                {{ getStatusLabel(guide.status) }}
              </el-tag>
            </div>
          </div>

          <!-- 攻略信息 -->
          <div class="guide-info">
            <h3 class="guide-title">{{ guide.title }}</h3>
            <div class="guide-meta">
              <span class="meta-item">
                <el-icon><Calendar /></el-icon>
                {{ guide.days }}天{{ guide.nights }}夜
              </span>
              <span class="meta-item">
                <el-icon><Location /></el-icon>
                {{ guide.destination }}
              </span>
              <span class="meta-item">
                <el-icon><Coin /></el-icon>
                {{ getBudgetLabel(guide.budget) }}
              </span>
            </div>

            <!-- 攻略标签 -->
            <div class="guide-tags">
              <el-tag
                v-for="tag in guide.tags"
                :key="tag"
                size="small"
                effect="plain"
              >
                #{{ tag }}
              </el-tag>
            </div>

            <!-- 攻略统计 -->
            <div class="guide-stats">
              <div class="stat-item">
                <el-icon><View /></el-icon>
                <span>{{ formatNumber(guide.views) }}</span>
              </div>
              <div class="stat-item">
                <el-icon><StarFilled /></el-icon>
                <span>{{ guide.favorites || 0 }}</span>
              </div>
              <div class="stat-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatDate(guide.updated_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 攻略操作 -->
          <div class="guide-actions" @click.stop>
            <el-dropdown trigger="click" @command="handleAction($event, guide)">
              <el-button circle>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate">
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-dropdown-item>
                  <el-dropdown-item divided command="delete">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-guides">
        <div class="empty-card">
          <el-icon class="empty-icon"><Document /></el-icon>
          <h3>还没有攻略</h3>
          <p>创建您的第一个旅行攻略，记录美好旅程</p>
          <el-button type="primary" size="large" @click="createNewGuide">
            <el-icon><Plus /></el-icon>
            创建第一个攻略
          </el-button>
        </div>
      </div>

      <!-- 攻略知识库板块 -->
      <div class="knowledge-section">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><Reading /></el-icon>
            攻略知识库
          </h2>
          <p class="section-subtitle">精选旅行攻略、实用技巧和目的地指南</p>
        </div>

        <!-- 分类标签 -->
        <div class="category-tabs">
          <div
            v-for="cat in knowledgeCategories"
            :key="cat.id"
            class="category-tab"
            :class="{ active: selectedKnowledgeCategory === cat.id }"
            @click="selectedKnowledgeCategory = cat.id"
          >
            <el-icon><component :is="cat.icon" /></el-icon>
            <span>{{ cat.name }}</span>
            <span class="count">({{ cat.count }})</span>
          </div>
        </div>

        <!-- 知识库文章列表 -->
        <div class="knowledge-articles">
          <div
            v-for="article in filteredKnowledgeArticles"
            :key="article.id"
            class="article-card"
            @click="openKnowledgeArticle(article)"
          >
            <div class="article-image">
              <img
                  :src="article.image"
                  :alt="article.title"
                  @error="(e) => handleImageError(e, 'kb-' + article.id)"
                  loading="lazy"
              />
              <div class="article-badge">{{ getCategoryName(article.category) }}</div>
            </div>
            <div class="article-content">
              <h3 class="article-title">{{ article.title }}</h3>
              <p class="article-desc">{{ article.description }}</p>
              <div class="article-meta">
                <span class="meta-item">
                  <el-icon><View /></el-icon>
                  {{ article.views }}
                </span>
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>
                  {{ article.readTime }}
                </span>
              </div>
              <div class="article-tags">
                <span v-for="tag in article.tags" :key="tag" class="tag">#{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识库文章详情弹窗 -->
    <el-dialog
      v-model="showKnowledgeModal"
      :title="currentKnowledgeArticle?.title"
      width="70%"
      class="knowledge-modal"
      destroy-on-close
    >
      <div class="knowledge-detail" v-if="currentKnowledgeArticle">
        <div class="article-header">
          <el-tag type="info" size="large">{{ getCategoryName(currentKnowledgeArticle.category) }}</el-tag>
          <div class="article-meta">
            <span><el-icon><View /></el-icon> {{ currentKnowledgeArticle.views }}</span>
            <span><el-icon><Clock /></el-icon> {{ currentKnowledgeArticle.readTime }}</span>
          </div>
        </div>
        <div class="article-cover">
          <img :src="currentKnowledgeArticle.image" :alt="currentKnowledgeArticle.title">
        </div>
        <div class="article-body" v-html="currentKnowledgeArticle.content"></div>
        <div class="article-tags-section">
          <span v-for="tag in currentKnowledgeArticle.tags" :key="tag" class="tag">#{{ tag }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 用户攻略详情弹窗 -->
    <el-dialog
      v-model="showGuideDetailModal"
      :title="currentGuideDetail?.title || '攻略详情'"
      width="70%"
      class="knowledge-modal"
      destroy-on-close
    >
      <!-- 加载状态 -->
      <div v-if="loadingDetail" class="detail-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在加载攻略详情...</p>
      </div>

      <!-- 攻略详情内容 -->
      <div class="knowledge-detail" v-else-if="currentGuideDetail">
        <div class="article-header">
          <el-tag :type="getStatusType(currentGuideDetail.status)" size="large">{{ getStatusLabel(currentGuideDetail.status) }}</el-tag>
          <div class="article-meta">
            <span><el-icon><Location /></el-icon> {{ currentGuideDetail.destination }}</span>
            <span><el-icon><Calendar /></el-icon> {{ currentGuideDetail.total_days }}天</span>
            <span><el-icon><Wallet /></el-icon> ¥{{ currentGuideDetail.budget }}</span>
          </div>
        </div>

        <!-- 每日行程 -->
        <div class="guide-itinerary" v-if="currentGuideDetail.guide_data?.daily_itineraries">
          <div v-for="day in currentGuideDetail.guide_data.daily_itineraries" :key="day.day" class="itinerary-day">
            <h4 class="day-title">第{{ day.day }}天：{{ day.title }}</h4>
            <p v-if="day.description" class="day-description">{{ day.description }}</p>

            <div class="schedule-list">
              <div v-for="(item, index) in day.schedule" :key="index" class="schedule-item">
                <div class="item-time">{{ item.time_range || item.time }}</div>
                <div class="item-content">
                  <div class="item-header">
                    <span class="item-activity">{{ item.activity }}</span>
                    <el-tag size="small" :type="item.period === 'lunch' || item.period === 'dinner' ? 'warning' : 'primary'">
                      {{ getPeriodLabel(item.period) }}
                    </el-tag>
                  </div>
                  <div v-if="item.location" class="item-location">
                    <el-icon><Location /></el-icon> {{ item.location }}
                  </div>
                  <div v-if="item.description" class="item-description">
                    {{ item.description }}
                  </div>
                  <div v-if="item.highlights && item.highlights.length" class="item-highlights">
                    <strong>亮点：</strong>
                    <ul>
                      <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 无攻略数据提示 -->
        <div v-else class="no-guide-data">
          <el-empty description="暂无攻略详情数据" />
        </div>

        <!-- 操作按钮区 -->
        <div class="article-actions">
          <el-button size="large" @click="showGuideDetailModal = false">
            关闭
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, shallowRef, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Plus,
  Calendar,
  Location,
  Coin,
  View,
  StarFilled,
  Clock,
  MoreFilled,
  Edit,
  CopyDocument,
  Download,
  Delete,
  Document,
  Reading,
  Suitcase,
  Camera,
  MapLocation,
  Food,
  Sunny,
  FirstAidKit,
  Wallet,
  Loading
} from '@element-plus/icons-vue'

// 导入攻略API
import { getUserGuides, getPublicGuides, deleteGuide, getGuideDetail, type GuideListItem, type GuideDetail, getGuideImageUrlAsync } from '@/api/travel/guides'

const router = useRouter()

// 状态
const searchQuery = ref('')
const filterStatus = ref('')
const sortBy = ref('created')
const exportDialogVisible = ref(false)
const currentGuide = ref<any>(null)
const selectedKnowledgeCategory = ref('all')
const showKnowledgeModal = ref(false)
const currentKnowledgeArticle = ref<any>(null)
const showGuideDetailModal = ref(false)
const currentGuideDetail = ref<GuideDetail | null>(null)
const isImageLoaded = ref<Record<string, boolean>>({})
const hasImageError = ref<Record<string, boolean>>({})
const loading = ref(true)
const loadingDetail = ref(false)

// 攻略列表（从API加载）
const guides = ref<GuideListItem[]>([])

// 加载攻略列表
const loadGuides = async () => {
  loading.value = true
  try {
    // 使用 demo_user ID 来获取用户自己的攻略
    const userId = 'demo_user'
    const data = await getUserGuides(userId, undefined, 20, 0)
    // 直接使用后端返回的 thumbnail_url，不再异步加载
    const guidesWithImages = data.map((guide: any) => {
      // 后端已经返回了 thumbnail_url，直接使用
      let coverUrl = guide.thumbnail_url || guide.cover_image
      // 如果后端没有返回，使用占位图
      if (!coverUrl) {
        coverUrl = `https://placehold.co/600x400?text=${encodeURIComponent(guide.destination)}`
      }
      return {
        ...guide,
        days: guide.total_days,
        nights: guide.total_days - 1,
        budget: guide.budget < 1500 ? 'economy' : guide.budget < 3000 ? 'comfort' : 'luxury',
        status: guide.status === 'published' ? 'completed' : guide.status,
        views: guide.view_count || 0,
        favorites: guide.like_count || 0,
        cover: coverUrl,
        content: '' // 内容从详情页获取
      }
    })
    guides.value = guidesWithImages
    console.log('加载我的攻略列表成功:', guides.value.length)
  } catch (error) {
    console.error('加载攻略列表失败:', error)
    ElMessage.error('加载攻略列表失败')
  } finally {
    loading.value = false
  }
}

// 页面加载时获取攻略列表
onMounted(() => {
  loadGuides()
})

// 当组件从 keep-alive 激活时重新加载
onActivated(() => {
  loadGuides()
})

// 攻略知识库数据 - 硬编码内容
// 使用 Unsplash 图片（和攻略卡片相同的图片源）
const knowledgeArticles = ref([
  {
    id: 1,
    title: '旅行前必做的10项准备工作',
    description: '出行前充分准备是旅行顺利的关键。本文详细介绍旅行前需要完成的各项准备工作，包括证件办理、行程规划、预算制定等重要事项。',
    category: 'planning',
    tags: ['行前准备', '旅行规划', '实用技巧'],
    views: 12450,
    readTime: '8分钟',
    image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600',
    content: `<div class="knowledge-content">
      <h2>📋 证件与文件准备</h2>
      <p><strong>1. 护照与签证</strong><br/>确保护照有效期在6个月以上，提前办理目的地国家签证。</p>
      <p><strong>2. 身份证件备份</strong><br/>将护照、身份证等重要证件拍照保存在手机云端。</p>
      <h3>💰 预算与支付</h3>
      <p><strong>3. 制定详细预算</strong><br/>交通费占30-40%，住宿费占25-35%，餐饮费占20-25%。</p>
      <p><strong>4. 支付方式准备</strong><br/>准备至少两种支付方式：信用卡 + 现金。</p>
      <h3>🏥 健康与安全</h3>
      <p><strong>5. 旅行保险</strong><br/>购买综合旅行保险，保额建议不低于50万元。</p>
    </div>`
  },
  {
    id: 2,
    title: '国际机票预订省钱攻略',
    description: '掌握机票预订技巧，可以节省大量旅行预算。本文分享实用的机票比价方法、最佳预订时机、航线选择策略等。',
    category: 'budget',
    tags: ['机票预订', '省钱技巧', '比价策略'],
    views: 8920,
    readTime: '6分钟',
    image: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600',
    content: `<div class="knowledge-content">
      <h2>🔍 最佳预订时机</h2>
      <p><strong>国内航班：</strong>提前4-6周预订价格最优</p>
      <p><strong>国际航班：</strong>提前8-12周预订价格最优</p>
      <h3>📊 机票比价工具</h3>
      <ul>
        <li>Skyscanner（天巡）- 全球最大比价平台</li>
        <li>Google Flights - 强大的日历视图和价格预测</li>
        <li>Kayak - 价格趋势图和价格提醒功能</li>
      </ul>
      <h3>💡 省钱技巧</h3>
      <p>灵活日期搜索、选择邻近机场、中转航班可节省30-50%费用</p>
    </div>`
  },
  {
    id: 3,
    title: '旅行摄影全指南：拍出大片感',
    description: '旅行摄影是记录美好回忆的重要方式。从构图技巧到光线运用，从后期处理到器材选择，本文全面解析旅行摄影的精髓。',
    category: 'photography',
    tags: ['摄影技巧', '构图方法', '后期处理'],
    views: 15780,
    readTime: '10分钟',
    image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600',
    content: `<div class="knowledge-content">
      <h2>📷 器材选择</h2>
      <p><strong>入门级：</strong>手机 + 轻便三脚架</p>
      <p><strong>进阶级：</strong>微单相机 + 24-70mm镜头</p>
      <h3>🎨 构图技巧</h3>
      <p><strong>三分法</strong> - 将画面分为九宫格，主体放置在交点处</p>
      <p><strong>引导线构图</strong> - 利用道路、河流等线条引导视线</p>
      <p><strong>框架构图</strong> - 透过窗户、门洞拍摄形成天然画框</p>
      <h3>☀️ 光线运用</h3>
      <p><strong>黄金时段：</strong>日出后1小时和日落前1小时</p>
    </div>`
  },
  {
    id: 4,
    title: '日本深度游：东京京都7天攻略',
    description: '日本是亚洲最受欢迎的旅行目的地之一。本攻略涵盖东京现代都市风光与京都传统文化体验，包含景点推荐、美食指南、交通攻略。',
    category: 'destinations',
    tags: ['日本', '东京', '京都', '7天行程'],
    views: 21300,
    readTime: '12分钟',
    image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600',
    content: `<div class="knowledge-content">
      <h2>🗾 行程概览</h2>
      <p><strong>最佳旅行时间：</strong>春季（3-5月）樱花季，秋季（9-11月）红叶季</p>
      <p><strong>推荐天数：</strong>7-10天</p>
      <p><strong>预算参考：</strong>人均1.5-2.5万元（含机票）</p>
      <h3>📅 详细行程</h3>
      <p><strong>Day 1-3：东京现代都市</strong></p>
      <ul><li>浅草寺 - 东京最古老寺庙</li><li>涩谷十字路口 - 世界最繁忙路口</li><li>东京塔/晴空塔 - 俯瞰东京全景</li></ul>
      <p><strong>Day 4-7：京都古都风韵</strong></p>
      <ul><li>清水寺 - 京都标志性寺庙</li><li>伏见稻荷大社 - 千本鸟居</li><li>金阁寺 - 金碧辉煌的日式庭园</li></ul>
    </div>`
  },
  {
    id: 5,
    title: '旅行健康与安全指南',
    description: '旅途中保持健康安全是享受旅行的基础。本文涵盖旅行常见疾病预防、意外处理、紧急情况应对等实用知识。',
    category: 'safety',
    tags: ['旅行安全', '健康防护', '紧急处理'],
    views: 9800,
    readTime: '7分钟',
    image: 'https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=600',
    content: `<div class="knowledge-content">
      <h2>🏥 出行前健康准备</h2>
      <p><strong>1. 健康检查</strong> - 出发前进行全面体检</p>
      <p><strong>2. 疫苗接种</strong> - 查询目的地疫苗接种要求</p>
      <p><strong>3. 旅行保险</strong> - 保额建议不低于50万元</p>
      <h3>💊 常备药品清单</h3>
      <p>感冒药、肠胃药、止痛药、抗过敏药、晕车药</p>
      <h3>📞 紧急联系</h3>
      <p>全球紧急求助：112</p>
      <p>中国外交部领保热线：+86-10-12308</p>
    </div>`
  },
  {
    id: 6,
    title: '泰国普吉岛7天自由行攻略',
    description: '普吉岛是泰国最大的岛屿，拥有美丽海滩、丰富水上活动。本攻略涵盖海滩推荐、出海行程、美食指南和实用贴士。',
    category: 'destinations',
    tags: ['泰国', '普吉岛', '海岛游'],
    views: 18650,
    readTime: '10分钟',
    image: 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=600',
    content: `<div class="knowledge-content">
      <h2>🏝️ 目的地概况</h2>
      <p><strong>最佳旅行时间：</strong>11月至次年4月（旱季）</p>
      <p><strong>推荐天数：</strong>5-7天</p>
      <h3>🏖️ 海滩推荐</h3>
      <p>巴东海滩 - 最热门，水上活动丰富</p>
      <p>卡伦海滩 - 浪大适合冲浪</p>
      <p>卡塔海滩 - 家庭友好，设施完善</p>
      <h3>🍜 必尝美食</h3>
      <p>冬阴功汤、泰式炒河粉、芒果糯米饭</p>
    </div>`
  },
  {
    id: 7,
    title: '东南亚美食完全指南',
    description: '东南亚是美食天堂。本文详细介绍泰国、越南、新加坡等国家的代表性菜肴、街头美食文化和必吃推荐。',
    category: 'food',
    tags: ['东南亚', '美食攻略', '街头小吃'],
    views: 13800,
    readTime: '8分钟',
    image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600',
    content: `<div class="knowledge-content">
      <h2>🍜 泰国美食</h2>
      <p>冬阴功汤、泰式炒河粉、芒果糯米饭</p>
      <h3>🥢 越南美食</h3>
      <p>越南河粉、越式法棍、越南咖啡</p>
      <h3>🇸🇬 新加坡美食</h3>
      <p>海南鸡饭、叻沙、肉骨茶</p>
    </div>`
  },
  {
    id: 8,
    title: '云南大理丽江7天浪漫之旅',
    description: '云南大理丽江以其美丽的自然风光和浓郁的民族文化吸引无数游客。本攻略涵盖古城漫步、洱海骑行、雪山登顶等精华内容。',
    category: 'destinations',
    tags: ['云南', '大理', '丽江', '国内游'],
    views: 24500,
    readTime: '11分钟',
    image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=600',
    content: `<div class="knowledge-content">
      <h2>🏔️ 目的地概况</h2>
      <p><strong>最佳旅行时间：</strong>3-5月春季、9-11月秋季</p>
      <h3>📅 详细行程</h3>
      <p><strong>大理：</strong>大理古城、洱海骑行、双廊古镇</p>
      <p><strong>丽江：</strong>丽江古城、玉龙雪山、蓝月谷</p>
      <h3>🍜 美食推荐</h3>
      <p>过桥米线、腊排骨火锅、鲜花饼</p>
    </div>`
  }
])

// 攻略知识库分类（使用 shallowRef 避免组件被响应式化）
const knowledgeCategories = shallowRef([
  { id: 'all', name: '全部', icon: markRaw(Reading), count: 0 },
  { id: 'planning', name: '行前准备', icon: markRaw(Suitcase), count: 0 },
  { id: 'photography', name: '摄影技巧', icon: markRaw(Camera), count: 0 },
  { id: 'destinations', name: '目的地指南', icon: markRaw(MapLocation), count: 0 },
  { id: 'food', name: '美食攻略', icon: markRaw(Food), count: 0 },
  { id: 'safety', name: '安全健康', icon: markRaw(FirstAidKit), count: 0 },
  { id: 'budget', name: '省钱攻略', icon: markRaw(Wallet), count: 0 }
])

// 计算每个分类的文章数量
knowledgeCategories.value.forEach(cat => {
  if (cat.id === 'all') {
    cat.count = knowledgeArticles.value.length
  } else {
    cat.count = knowledgeArticles.value.filter(a => a.category === cat.id).length
  }
})

// 过滤后的知识库文章
const filteredKnowledgeArticles = computed(() => {
  if (selectedKnowledgeCategory.value === 'all') {
    return knowledgeArticles.value
  }
  return knowledgeArticles.value.filter(a => a.category === selectedKnowledgeCategory.value)
})

// 获取分类名称
const getCategoryName = (categoryId: string) => {
  const cat = knowledgeCategories.value.find(c => c.id === categoryId)
  return cat?.name || ''
}

// 获取分类图标
const getCategoryIcon = (categoryId: string) => {
  const icons = {
    'planning': '✈️',
    'budget': '💰',
    'photography': '📷',
    'destinations': '🗺️',
    'food': '🍜',
    'safety': '🏥',
    'all': '📚'
  }
  return icons[categoryId] || '📖'
}

// 打开知识库文章
const openKnowledgeArticle = (article: any) => {
  currentKnowledgeArticle.value = article
  showKnowledgeModal.value = true
}

// 过滤后的攻略列表
const filteredGuides = computed(() => {
  let result = [...guides.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(g =>
      g.title.toLowerCase().includes(query) ||
      g.destination.toLowerCase().includes(query) ||
      g.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // 状态过滤
  if (filterStatus.value) {
    result = result.filter(g => g.status === filterStatus.value)
  }

  // 排序
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'views':
        return b.views - a.views
      case 'updated':
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      case 'created':
      default:
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
  })

  return result
})

// 方法
const createNewGuide = () => {
  router.push('/travel/planner')
}

const viewGuide = (guide: any) => {
  router.push(`/travel/guides/${guide.id}`)
}

const openGuideDetail = async (guide: any) => {
  try {
    loadingDetail.value = true
    // 调用API获取完整的攻略详情（包含 guide_data）
    const detail = await getGuideDetail(guide.id)
    currentGuideDetail.value = detail
    showGuideDetailModal.value = true
    console.log('攻略详情加载成功:', detail)
  } catch (error) {
    console.error('加载攻略详情失败:', error)
    ElMessage.error('加载攻略详情失败，请重试')
  } finally {
    loadingDetail.value = false
  }
}

const handleImageLoad = (event: any, guideId: string) => {
  isImageLoaded.value[guideId] = true
  hasImageError.value[guideId] = false
}

const handleImageError = (event: any, guideId: string) => {
  const img = event.target
  const originalSrc = img.src

  // 如果是 Pixabay 图片加载失败，替换为 Unsplash 图片
  if (originalSrc.includes('pixabay.com')) {
    // 根据不同的 guideId 生成不同的 Unsplash 图片
    const unsplashImages = [
      'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600',
      'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600',
      'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600',
      'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600',
      'https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=600',
      'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600',
      'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600',
      'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=600'
    ]
    // 使用 guideId 的 hash 来选择一个固定的图片
    const hash = guideId.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0)
      return a & a
    }, 0)
    const index = Math.abs(hash) % unsplashImages.length
    img.src = unsplashImages[index]
    hasImageError.value[guideId] = false
  } else {
    isImageLoaded.value[guideId] = false
    hasImageError.value[guideId] = true
  }
}

const handleAction = async (command: string, guide: any) => {
  switch (command) {
    case 'duplicate':
      ElMessage.success('攻略已复制')
      break
    case 'delete':
      await handleDelete(guide)
      break
  }
}

const handleDelete = async (guide: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除攻略"${guide.title}"吗？此操作不可恢复。`,
      '删除攻略',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用API删除
    const userId = 'demo_user' // 实际应从登录状态获取
    await deleteGuide(guide.id, userId)

    // 从列表中移除
    const index = guides.value.findIndex(g => g.id === guide.id)
    if (index > -1) {
      guides.value.splice(index, 1)
    }

    ElMessage.success('攻略已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除攻略失败:', error)
      ElMessage.error('删除攻略失败，请重试')
    }
  }
}

const getStatusType = (status: string) => {
  const types = {
    draft: 'info',
    completed: 'success',
    published: 'success'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: '草稿',
    completed: '已完成',
    published: '已发布'
  }
  return labels[status] || status
}

const getPeriodLabel = (period: string) => {
  const labels = {
    morning: '上午',
    lunch: '午餐',
    afternoon: '下午',
    dinner: '晚餐',
    evening: '晚上'
  }
  return labels[period] || period
}

const getBudgetLabel = (budget: string) => {
  const labels = {
    economy: '经济型',
    comfort: '舒适型',
    luxury: '高端型'
  }
  return labels[budget] || budget
}

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

const formatNumber = (num: number) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped>
/* 导入 DM Sans 字体 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

.guides-page {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  padding: 40px 24px;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.guides-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.guides-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 20px;
}

.header-content {
  flex: 1;
}

.guides-title {
  font-size: 42px;
  font-weight: 700;
  color: #0C4A6E;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.guides-subtitle {
  font-size: 18px;
  color: #64748B;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 筛选栏 */
.guides-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.08);
  flex-wrap: wrap;
  gap: 16px;
}

.filter-left,
.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 320px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 2px solid #E0F2FE;
  transition: all 0.3s;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #0EA5E9;
}

.filter-select {
  width: 140px;
}

/* 攻略网格 */
.guides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.guide-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.08);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(14, 165, 233, 0.08);
  position: relative;
}

.guide-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 48px rgba(14, 165, 233, 0.18);
}

/* 攻略封面 */
.guide-cover {
  position: relative;
  height: 200px;
  overflow: hidden;
}

/* 占位符背景（始终显示） */
.cover-placeholder-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: linear-gradient(135deg, #0EA5E9 0%, #F97316 100%);
}

.cover-placeholder-bg svg {
  width: 100%;
  height: 100%;
}

/* 图片层（覆盖在占位符上） */
.image-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.4s ease-in-out;
  z-index: 1;
}

.image-wrapper.image-loaded {
  opacity: 1;
}

.guide-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.guide-cover img.img-loaded {
  opacity: 1;
}

.image-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  z-index: 2;
}

.article-image .image-loading {
  background: transparent;
}

.image-loading .el-icon {
  font-size: 32px;
  color: #0EA5E9;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.cover-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
}

/* 攻略信息 */
.guide-info {
  padding: 24px;
}

.guide-title {
  font-size: 18px;
  font-weight: 700;
  color: #0C4A6E;
  margin-bottom: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.guide-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
}

.meta-item .el-icon {
  color: #0EA5E9;
}

.guide-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.guide-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #F1F5F9;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
}

.stat-item .el-icon {
  color: #94A3B8;
}

.guide-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  opacity: 0;
  transition: opacity 0.25s;
}

.guide-card:hover .guide-actions {
  opacity: 1;
}

.guide-actions .el-button {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 空状态 */
.empty-guides {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-card {
  background: white;
  padding: 60px 40px;
  border-radius: 24px;
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  font-size: 64px;
  color: #CBD5E1;
  margin-bottom: 20px;
}

.empty-card h3 {
  font-size: 22px;
  font-weight: 600;
  color: #0C4A6E;
  margin-bottom: 12px;
}

.empty-card p {
  font-size: 15px;
  color: #64748B;
  margin-bottom: 24px;
}

/* 导出对话框 */
/* 攻略知识库板块 */
.knowledge-section {
  margin-top: 60px;
  padding-top: 60px;
  border-top: 2px solid #E0F2FE;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #0C4A6E;
  margin-bottom: 12px;
}

.section-subtitle {
  font-size: 16px;
  color: #64748B;
  margin: 0;
}

/* 分类标签 */
.category-tabs {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 20px 0;
  margin-bottom: 32px;
  scrollbar-width: none;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.08);
  border: 2px solid transparent;
  font-weight: 500;
  color: #64748B;
}

.category-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
}

.category-tab.active {
  background: linear-gradient(135deg, #0EA5E9, #38BDF8);
  color: white;
  border-color: #0EA5E9;
}

.category-tab .count {
  background: rgba(14, 165, 233, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.category-tab.active .count {
  background: rgba(255, 255, 255, 0.2);
}

/* 知识库文章列表 */
.knowledge-articles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.article-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.08);
}

.article-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(14, 165, 233, 0.18);
}

.article-image {
  position: relative;
  height: 180px;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.article-image .image-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.article-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1;
  transition: transform 0.3s ease-in-out;
}

.article-image img.image-error {
  display: none;
}

.article-card:hover .article-image img.image-loaded {
  transform: scale(1.05);
}

.article-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.95);
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #0EA5E9;
  backdrop-filter: blur(8px);
}

.article-content {
  padding: 20px;
}

.article-title {
  font-size: 16px;
  font-weight: 700;
  color: #0C4A6E;
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-desc {
  font-size: 13px;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.article-meta .meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94A3B8;
}

.article-meta .el-icon {
  font-size: 14px;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.article-tags .tag {
  padding: 4px 10px;
  background: #F0F9FF;
  border-radius: 6px;
  font-size: 11px;
  color: #0EA5E9;
  font-weight: 500;
}

/* 知识库详情弹窗 */
.knowledge-modal :deep(.el-dialog__body) {
  padding: 0;
  max-height: 70vh;
  overflow-y: auto;
}

.knowledge-detail {
  padding: 24px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E5E7EB;
}

.article-meta {
  display: flex;
  gap: 20px;
  color: #64748B;
  font-size: 14px;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.article-cover {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: auto;
  max-height: 600px;
  object-fit: contain;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s;
}

.article-cover img:hover {
  transform: scale(1.02);
}

.article-body {
  font-size: 16px;
  line-height: 1.8;
  color: #374151;
}

/* 攻略详情加载状态 */
.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748B;
}

.detail-loading .el-icon {
  font-size: 48px;
  color: #6366F1;
  margin-bottom: 16px;
}

.detail-loading p {
  font-size: 16px;
  margin: 0;
}

/* 无攻略数据提示 */
.no-guide-data {
  padding: 40px 20px;
  text-align: center;
}

/* 攻略行程样式 */
.guide-itinerary {
  margin-top: 24px;
}

.itinerary-day {
  margin-bottom: 32px;
  padding: 20px;
  background: #F8FAFC;
  border-radius: 12px;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 12px;
}

.day-description {
  color: #64748B;
  margin-bottom: 16px;
  line-height: 1.6;
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.schedule-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
}

.item-time {
  min-width: 100px;
  font-weight: 600;
  color: #6366F1;
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-activity {
  font-weight: 600;
  color: #1F2937;
  font-size: 16px;
}

.item-location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748B;
  margin-bottom: 8px;
  font-size: 14px;
}

.item-description {
  color: #374151;
  line-height: 1.6;
  margin-bottom: 12px;
}

.item-highlights {
  padding: 12px;
  background: #FEF3C7;
  border-radius: 6px;
  font-size: 14px;
}

.item-highlights ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.item-highlights li {
  margin-bottom: 4px;
  color: #92400E;
}

.article-body {
  font-size: 16px;
  line-height: 1.8;
  color: #374151;
  margin-bottom: 24px;
}

.article-body h2 {
  font-size: 24px;
  font-weight: 700;
  margin-top: 32px;
  margin-bottom: 16px;
  color: #0C4A6E;
}

.article-body h3 {
  font-size: 20px;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 12px;
  color: #1F2937;
}

.article-body p {
  margin-bottom: 16px;
}

.article-body ul {
  margin-left: 24px;
  margin-bottom: 16px;
}

.article-body li {
  margin-bottom: 8px;
}

.article-tags-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid #E5E7EB;
}

.article-tags-section .tag {
  padding: 6px 16px;
  background: #F0F9FF;
  border-radius: 20px;
  font-size: 13px;
  color: #0EA5E9;
  font-weight: 500;
}

.article-actions {
  display: flex;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #E5E7EB;
  justify-content: center;
}

.article-actions .el-button {
  min-width: 140px;
}

/* 攻略详情内容样式 */
.guide-content {
  font-size: 16px;
  line-height: 1.8;
  color: #374151;
}

.guide-content h2 {
  font-size: 28px;
  font-weight: 700;
  margin-top: 40px;
  margin-bottom: 20px;
  color: #0C4A6E;
  padding-bottom: 12px;
  border-bottom: 2px solid #E0F2FE;
}

.guide-content h2:first-child {
  margin-top: 0;
}

.guide-content h3 {
  font-size: 20px;
  font-weight: 600;
  margin-top: 28px;
  margin-bottom: 16px;
  color: #1F2937;
}

.guide-content p {
  margin-bottom: 16px;
  text-align: justify;
}

.guide-content ul,
.guide-content li {
  margin-bottom: 12px;
}

.guide-content ul {
  margin-left: 24px;
  margin-bottom: 20px;
}

.guide-content li {
  list-style-type: disc;
}

.guide-content strong {
  color: #0EA5E9;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .guides-page {
    padding: 24px 16px;
  }

  .guides-header {
    flex-direction: column;
    gap: 16px;
  }

  .guides-title {
    font-size: 32px;
  }

  .guides-filter {
    flex-direction: column;
    padding: 20px;
  }

  .filter-left,
  .filter-right {
    width: 100%;
    justify-content: space-between;
  }

  .search-input {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }

  .guides-grid {
    grid-template-columns: 1fr;
  }
}
</style>
