<template>
  <div class="guide-center">
    <div class="container">
      <!-- Header -->
      <div class="header">
        <h1 class="title">
          <el-icon class="title-icon"><Tickets /></el-icon>
          攻略中心
        </h1>
        <p class="subtitle">全面的旅行攻略、实用技巧和目的地指南</p>
      </div>

      <!-- Search -->
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索知识、攻略、目的地..."
          size="large"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- Category Tabs -->
      <div class="categories">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-tab"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <el-icon class="category-icon">
            <component :is="category.icon" />
          </el-icon>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-count">{{ category.count }}</span>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="content-grid">
        <!-- Featured Articles -->
        <div class="featured-section" v-if="selectedCategory === 'all' || selectedCategory === 'featured'">
          <h2 class="section-title">
            <el-icon><Star /></el-icon>
            精选攻略
          </h2>
          <div class="featured-cards">
            <div
              v-for="article in featuredArticles"
              :key="article.id"
              class="featured-card"
              @click="openArticle(article)"
            >
              <div class="card-image">
                <img :src="article.image" :alt="article.title">
                <div class="card-badge">{{ article.category }}</div>
              </div>
              <div class="card-content">
                <h3 class="card-title">{{ article.title }}</h3>
                <p class="card-excerpt">{{ article.excerpt }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><View /></el-icon>
                    {{ article.views }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ article.readTime }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Knowledge Articles -->
        <div class="articles-section">
          <h2 class="section-title">
            <el-icon><Document /></el-icon>
            {{ getCategoryTitle() }}
          </h2>
          <div class="articles-list">
            <div
              v-for="article in filteredArticles"
              :key="article.id"
              class="article-item"
              @click="openArticle(article)"
            >
              <div class="article-icon" :style="{ background: article.color }">
                <el-icon>
                  <component :is="article.icon" />
                </el-icon>
              </div>
              <div class="article-content">
                <h3 class="article-title">{{ article.title }}</h3>
                <p class="article-description">{{ article.description }}</p>
                <div class="article-tags">
                  <span
                    v-for="tag in article.tags"
                    :key="tag"
                    class="article-tag"
                  >{{ tag }}</span>
                </div>
              </div>
              <el-icon class="article-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Article Modal -->
      <el-dialog
        v-model="showArticleModal"
        :title="currentArticle?.title"
        width="80%"
        class="article-modal"
        destroy-on-close
      >
        <div class="article-content" v-if="currentArticle">
          <div class="article-header">
            <div class="article-meta-info">
              <span class="meta-tag">{{ currentArticle.category }}</span>
              <span class="meta-time">{{ currentArticle.readTime }}</span>
            </div>
          </div>
          <div class="article-body" v-html="currentArticle.content"></div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Tickets, Search, Star, Document, View, Clock, ArrowRight,
  Suitcase, Camera, MapLocation, Food, Sunny, FirstAidKit, Wallet
} from '@element-plus/icons-vue'

const route = useRoute()
const searchQuery = ref('')
const selectedCategory = ref('all')
const showArticleModal = ref(false)
const currentArticle = ref<any>(null)

// 硬编码的攻略内容数据
const guideContent = {
  articles: [
    {
      id: 1,
      title: '旅行前必做的10项准备工作',
      description: '出行前充分准备是旅行顺利的关键。本文详细介绍旅行前需要完成的各项准备工作，包括证件办理、行程规划、预算制定等重要事项，让你的旅程更加安心愉快。',
      category: 'planning',
      icon: 'Suitcase',
      tags: ['行前准备', '旅行规划', '实用技巧', '新手必看'],
      featured: true,
      views: 12450,
      readTime: '8分钟',
      image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>📋 证件与文件准备</h2>
        <p><strong>1. 护照与签证</strong><br/>确保护照有效期在6个月以上，提前办理目的地国家签证。热门目的地签证处理时间：欧盟申根签证需15-30天，美国签证需预约面试，日本电子签证约5个工作日。</p>
        <p><strong>2. 身份证件备份</strong><br/>将护照、身份证等重要证件拍照保存在手机云端，并打印纸质复印件分开存放。建议使用加密云存储（如iCloud、Google Drive）备份电子版。</p>
        <p><strong>3. 驾驶证件</strong><br/>如计划自驾，需办理国际驾照（IDP）或了解目的地驾照使用规定。部分国家承认中国驾照（如阿联酋、新西兰），但需翻译公证。</p>
        <h3>💰 预算与支付</h3>
        <p><strong>4. 制定详细预算</strong><br/>使用预算规划工具，列出预期花费：</p>
        <ul><li>交通费（往返机票+当地交通）：占总预算30-40%</li><li>住宿费：占总预算25-35%</li><li>餐饮费：占总预算20-25%</li><li>景点门票：占总预算10-15%</li><li>购物预留：占总预算10-20%</li><li>应急资金：建议预留总预算的15%作为应急金</li></ul>
        <h3>📱 行程规划</h3>
        <p><strong>5. 支付方式准备</strong><br/>准备至少两种支付方式：信用卡（Visa/Mastercard）+ 现金（部分小额货币+美元作为通用储备）。</p>
        <p><strong>6. 预订机票与住宿</strong><br/>提前2-3个月预订可获最优价格。关注机票比价网站设置价格提醒。</p>
        <h3>🏥 健康与安全</h3>
        <p><strong>7. 旅行保险</strong><br/>购买综合旅行保险，覆盖医疗、航班延误、行李丢失等。保额建议医疗报销不低于50万元人民币。</p>
        <p><strong>8. 疫苗接种与药品</strong><br/>查询目的地疫苗接种要求。准备常用药品：感冒药、肠胃药、止痛药、创可贴、晕车药。</p>
        <h3>📦 打包清单</h3>
        <p><strong>9. 智能打包</strong><br/>使用行李打包清单APP，避免遗漏。分类打包：衣物、电子设备、洗漱用品、药品、重要文件。</p>
      </div>`
    },
    {
      id: 2,
      title: '国际机票预订省钱攻略',
      description: '掌握机票预订技巧，可以节省大量旅行预算。本文分享实用的机票比价方法、最佳预订时机、航线选择策略等，助你用最优惠的价格预订心仪航班。',
      category: 'budget',
      icon: 'Ticket',
      tags: ['机票预订', '省钱技巧', '比价策略', '旅行预算'],
      featured: true,
      views: 8920,
      readTime: '6分钟',
      image: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🔍 最佳预订时机</h2>
        <p><strong>国内航班：</strong>提前4-6周预订价格最优。周二下午和周三晚上的航班通常最便宜。</p>
        <p><strong>国际航班：</strong>提前8-12周预订价格最优。周二和周三出发的机票比周末便宜15-20%。</p>
        <h3>📊 机票比价工具</h3>
        <ul>
          <li><strong>Skyscanner（天巡）</strong>：全球最大比价平台，支持灵活日期搜索</li>
          <li><strong>Google Flights</strong>：强大的日历视图和价格预测功能</li>
          <li><strong>Kayak</strong>：价格趋势图和价格提醒功能</li>
          <li><strong>携程/飞猪</strong>：国内航线价格优势明显</li>
        </ul>
        <h3>💡 省钱技巧</h3>
        <p><strong>1. 灵活日期搜索</strong> - 使用比价网站的灵活日期功能，查看一周内价格波动</p>
        <p><strong>2. 选择邻近机场</strong> - 大都市周边机场价格可能不同</p>
        <p><strong>3. 中转航班</strong> - 可节省30-50%费用，注意中转时间不低于2小时</p>
        <p><strong>4. 航空公司会员</strong> - 注册会员计划累积里程兑换免费机票</p>
      </div>`
    },
    {
      id: 3,
      title: '旅行摄影全指南：拍出大片感',
      description: '旅行摄影是记录美好回忆的重要方式。从构图技巧到光线运用，从后期处理到器材选择，本文全面解析旅行摄影的精髓，让你的照片充满故事感和艺术感。',
      category: 'photography',
      icon: 'Camera',
      tags: ['摄影技巧', '构图方法', '后期处理', '器材推荐'],
      featured: true,
      views: 15780,
      readTime: '10分钟',
      image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>📷 器材选择</h2>
        <ul>
          <li><strong>入门级：</strong>手机（iPhone 15 Pro/华为Mate60）+ 轻便三脚架</li>
          <li><strong>进阶级：</strong>微单相机（Sony A7C系列/Fuji X系列）+ 24-70mm镜头</li>
          <li><strong>专业级：</strong>全画幅相机 + 16-35mm广角 + 70-200mm长焦</li>
        </ul>
        <h3>🎨 构图技巧</h3>
        <p><strong>1. 三分法则</strong> - 将画面分为九宫格，主体放置在交点处</p>
        <p><strong>2. 前景运用</strong> - 利用前景增加画面层次感</p>
        <p><strong>3. 引导线构图</strong> - 利用道路、河流、栏杆等线条引导视线至主体</p>
        <p><strong>4. 框架构图</strong> - 透过窗户、门洞拍摄，形成天然画框</p>
        <h3>☀️ 光线运用</h3>
        <p><strong>黄金时段：</strong>日出后1小时和日落前1小时，光线柔和温暖</p>
        <p><strong>蓝调时刻：</strong>日落后30分钟，天空呈现深蓝色，适合拍摄城市夜景</p>
        <h3>📱 手机摄影技巧</h3>
        <p><strong>1. 使用专业模式</strong> - 调整ISO、快门速度、白平衡</p>
        <p><strong>2. 开启HDR模式</strong> - 在强对比场景下平衡明暗细节</p>
        <h3>🎬 后期处理</h3>
        <ul>
          <li><strong>Lightroom Mobile</strong>：专业级调色工具</li>
          <li><strong>VSCO</strong>：丰富滤镜预设</li>
          <li><strong>Snapseed</strong>：全能免费编辑工具</li>
          <li><strong>醒图</strong>：人像美化效果出色</li>
        </ul>
      </div>`
    },
    {
      id: 4,
      title: '日本深度游：东京京都7天攻略',
      description: '日本是亚洲最受欢迎的旅行目的地之一。本攻略涵盖东京现代都市风光与京都传统文化体验，包含景点推荐、美食指南、交通攻略和实用贴士，助你畅游东瀛。',
      category: 'destinations',
      icon: 'MapLocation',
      tags: ['日本', '东京', '京都', '7天行程', '文化体验'],
      featured: true,
      views: 21300,
      readTime: '12分钟',
      image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🗾 行程概览</h2>
        <p><strong>最佳旅行时间：</strong>春季（3-5月）樱花季，秋季（9-11月）红叶季</p>
        <p><strong>推荐天数：</strong>7-10天</p>
        <p><strong>预算参考：</strong>人均1.5-2.5万元（含机票）</p>
        <h3>📅 详细行程</h3>
        <p><strong>Day 1-3：东京现代都市</strong></p>
        <ul>
          <li><strong>浅草寺</strong>：东京最古老寺庙，体验传统日本文化</li>
          <li><strong>涩谷十字路口</strong>：世界最繁忙路口</li>
          <li><strong>东京塔/晴空塔</strong>：俯瞰东京全景</li>
          <li><strong>秋叶原</strong>：动漫、电器天堂</li>
        </ul>
        <p><strong>Day 4-7：京都古都风韵</strong></p>
        <ul>
          <li><strong>清水寺</strong>：京都标志性寺庙</li>
          <li><strong>伏见稻荷大社</strong>：千本鸟居，摄影打卡胜地</li>
          <li><strong>金阁寺</strong>：金碧辉煌的日式庭园</li>
          <li><strong>岚山竹林</strong>：漫步竹林小径，感受禅意</li>
        </ul>
        <h3>🍣 美食推荐</h3>
        <p><strong>东京必吃：</strong>寿司、拉面、天妇罗</p>
        <p><strong>京都必吃：</strong>怀石料理、抹茶甜品、豆腐料理</p>
        <h3>🚃 交通攻略</h3>
        <p><strong>JR Pass</strong>：如计划跨城市旅行，购买JR Pass（7日券约29,650日元）</p>
        <p><strong>东京→京都</strong>：新干线Nozomi号约2小时15分钟</p>
      </div>`
    },
    {
      id: 5,
      title: '旅行健康与安全指南',
      description: '旅途中保持健康安全是享受旅行的基础。本文涵盖旅行常见疾病预防、意外处理、紧急情况应对等实用知识，让你的旅程更加安心无忧。',
      category: 'safety',
      icon: 'FirstAidKit',
      tags: ['旅行安全', '健康防护', '紧急处理', '医疗指南'],
      featured: true,
      views: 9800,
      readTime: '7分钟',
      image: 'https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🏥 出行前健康准备</h2>
        <p><strong>1. 健康检查</strong> - 出发前进行全面体检，确认身体状况适合旅行</p>
        <p><strong>2. 疫苗接种</strong> - 查询目的地疫苗接种要求</p>
        <p><strong>3. 旅行保险</strong> - 购买包含医疗救援的旅行保险，保额建议不低于50万元</p>
        <h3>💊 常备药品清单</h3>
        <p><strong>基础药品：</strong></p>
        <ul>
          <li>感冒药：泰诺、白加黑</li>
          <li>肠胃药：思密达、黄连素</li>
          <li>止痛药：布洛芬、对乙酰氨基酚</li>
          <li>抗过敏药：开瑞坦、西替利嗪</li>
          <li>晕车药：茶苯海明</li>
        </ul>
        <h3>⚠️ 安全注意事项</h3>
        <p><strong>1. 证件安全</strong> - 护照、身份证分开存放，使用酒店保险箱</p>
        <p><strong>2. 财物安全</strong> - 避免展示贵重物品，使用贴身腰包或防盗背包</p>
        <p><strong>3. 人身安全</strong> - 避免夜间独自前往偏僻地区</p>
        <h3>📞 紧急联系信息</h3>
        <p><strong>全球紧急求助：</strong>112</p>
        <p><strong>中国外交部全球领保热线：</strong>+86-10-12308</p>
      </div>`
    },
    {
      id: 6,
      title: '泰国普吉岛7天自由行全攻略',
      description: '普吉岛是泰国最大的岛屿，拥有美丽海滩、丰富水上活动和热闹夜生活。本攻略涵盖海滩推荐、出海行程、美食指南、购物攻略和实用贴士，帮你打造完美海岛假期。',
      category: 'destinations',
      icon: 'MapLocation',
      tags: ['泰国', '普吉岛', '海岛游', '7天行程', '海滩'],
      featured: false,
      views: 18650,
      readTime: '10分钟',
      image: 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🏝️ 目的地概况</h2>
        <p><strong>最佳旅行时间：</strong>11月至次年4月（旱季）</p>
        <p><strong>推荐天数：</strong>5-7天</p>
        <p><strong>预算参考：</strong>人均5,000-10,000元（含机票）</p>
        <h3>🏖️ 海滩推荐</h3>
        <p><strong>1. 巴东海滩</strong> - 普吉岛最热门海滩，沙质细腻，水上活动丰富</p>
        <p><strong>2. 卡伦海滩</strong> - 海滩狭长，浪大适合冲浪</p>
        <p><strong>3. 卡塔海滩</strong> - 家庭友好，海滩坡度平缓，设施完善</p>
        <h3>🚤 出海行程</h3>
        <p><strong>推荐1：皮皮岛一日游</strong> - 马雅湾、碧绿湾浮潜、猴子海滩</p>
        <p><strong>推荐2：攀牙湾一日游</strong> - 喀斯特地貌、水上村庄、皮划艇探险</p>
        <h3>🍜 美食指南</h3>
        <p><strong>必尝泰式料理：</strong>冬阴功汤、泰式炒河粉、绿咖喱鸡、芒果糯米饭</p>
      </div>`
    },
    {
      id: 7,
      title: '手机旅行摄影后期APP推荐',
      description: '后期处理是提升旅行照片质量的关键环节。本文推荐5款最实用的手机摄影后期APP，从基础调整到专业调色，满足不同水平用户的修图需求。',
      category: 'photography',
      icon: 'Camera',
      tags: ['手机摄影', '后期APP', '修图技巧', '调色'],
      featured: false,
      views: 7650,
      readTime: '5分钟',
      image: 'https://images.unsplash.com/photo-1495121553079-4c61bc894600?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>📱 手机后期APP推荐</h2>
        <p><strong>1. Lightroom Mobile</strong> - 专业级手机修图工具，支持RAW格式编辑</p>
        <p><strong>2. VSCO</strong> - 以精美滤镜著称的修图APP</p>
        <p><strong>3. Snapseed</strong> - Google出品的全能免费修图工具</p>
        <p><strong>4. 醒图</strong> - 美图旗下专业修图APP，人像美容功能强大</p>
        <p><strong>5. 泼辣修图</strong> - 国产专业级修图工具，功能接近Lightroom</p>
        <h3>🎨 调色技巧</h3>
        <p><strong>基础调整步骤：</strong></p>
        <ol><li>裁剪和旋转 - 校正水平线，优化构图</li><li>曝光调整 - 提亮暗部，压暗高光</li><li>对比度 - 增强画面层次感</li><li>色彩 - 调整色温、色调、饱和度</li><li>锐化 - 适当增强细节</li></ol>
      </div>`
    },
    {
      id: 8,
      title: '云南大理丽江7天浪漫之旅',
      description: '云南是国内最受欢迎的旅游目的地之一，大理丽江以其美丽的自然风光和浓郁的民族文化吸引无数游客。本攻略涵盖古城漫步、洱海骑行、雪山登顶、美食体验等精华内容。',
      category: 'destinations',
      icon: 'MapLocation',
      tags: ['云南', '大理', '丽江', '7天行程', '国内游'],
      featured: false,
      views: 24500,
      readTime: '11分钟',
      image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🏔️ 目的地概况</h2>
        <p><strong>最佳旅行时间：</strong>3-5月（春季花开）、9-11月（秋季天高气爽）</p>
        <p><strong>推荐天数：</strong>5-7天</p>
        <h3>📅 详细行程</h3>
        <p><strong>Day 1-3：大理慢生活</strong></p>
        <ul>
          <li><strong>大理古城</strong>：漫步古城，感受白族文化</li>
          <li><strong>洱海骑行</strong>：环湖骑行，欣赏苍山洱海美景</li>
          <li><strong>双廊古镇</strong>：文艺青年聚集地，拍照打卡</li>
        </ul>
        <p><strong>Day 4-7：丽江浪漫之旅</strong></p>
        <ul>
          <li><strong>丽江古城</strong>：世界文化遗产，四方街、酒吧街</li>
          <li><strong>玉龙雪山</strong>：乘大索道登顶4680米</li>
          <li><strong>蓝月谷</strong>：雪山脚下的蓝色湖泊</li>
        </ul>
        <h3>🍜 美食推荐</h3>
        <p><strong>大理必吃：</strong>过桥米线、喜洲粑粑、酸辣鱼、乳扇</p>
        <p><strong>丽江必吃：</strong>腊排骨火锅、鸡豆凉粉、纳西烤鱼、鲜花饼</p>
      </div>`
    },
    {
      id: 9,
      title: '东南亚美食完全指南',
      description: '东南亚是美食天堂，各国风味独特、食材丰富。本文详细介绍泰国、越南、新加坡、马来西亚等国家的代表性菜肴、街头美食文化和必吃餐厅推荐，让你吃遍东南亚。',
      category: 'food',
      icon: 'Food',
      tags: ['东南亚', '美食攻略', '街头小吃', '文化体验'],
      featured: false,
      views: 13800,
      readTime: '8分钟',
      image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🍜 泰国美食</h2>
        <ul>
          <li><strong>冬阴功汤</strong>：酸辣虾汤，泰国国汤</li>
          <li><strong>泰式炒河粉</strong>：河粉+豆芽+虾仁+花生，经典街头美食</li>
          <li><strong>芒果糯米饭</strong>：甜而不腻的完美收尾</li>
        </ul>
        <h3>🥢 越南美食</h3>
        <ul>
          <li><strong>越南河粉</strong>：清汤牛肉河粉，牛肉片+豆芽+香草</li>
          <li><strong>越式法棍</strong>：法式面包+越南馅料，完美融合</li>
          <li><strong>越南咖啡</strong>：滴漏咖啡，浓郁香甜</li>
        </ul>
        <h3>🇸🇬 新加坡美食</h3>
        <ul>
          <li><strong>海南鸡饭</strong>：白斩鸡+香米饭+辣椒酱</li>
          <li><strong>叻沙</strong>：椰奶咖喱面汤</li>
          <li><strong>肉骨茶</strong>：胡椒猪肉汤，滋补暖胃</li>
        </ul>
      </div>`
    },
    {
      id: 10,
      title: '旅行中如何保持身体健康',
      description: '旅途中保持身体健康是享受旅行的前提。本文介绍旅行中常见健康问题的预防和处理方法，包括饮食安全、作息调整、运动锻炼、疾病预防等实用建议。',
      category: 'safety',
      icon: 'Sunny',
      tags: ['旅行健康', '疾病预防', '饮食安全', '身体保健'],
      featured: false,
      views: 8200,
      readTime: '6分钟',
      image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>🥗 饮食安全</h2>
        <p><strong>1. 饮水安全</strong> - 选择瓶装水（确保密封完好），避免冰块</p>
        <p><strong>2. 食物选择</strong> - 选择现做现卖的食物，避免生食</p>
        <p><strong>3. 饮食规律</strong> - 保持定时进餐，不暴饮暴食</p>
        <h3>😴 作息调整</h3>
        <p><strong>1. 应对时差</strong> - 提前2-3天调整作息时间，飞行中补充水分</p>
        <p><strong>2. 保证睡眠</strong> - 选择安静舒适的住宿，携带耳塞、眼罩</p>
        <h3>🏃 运动锻炼</h3>
        <p><strong>1. 旅途中保持运动</strong> - 步行探索城市，酒店房间内简单拉伸</p>
        <p><strong>2. 预防静脉曲张</strong> - 长途飞行中定期活动腿部，穿着压缩袜</p>
      </div>`
    },
    {
      id: 11,
      title: '欧洲背包旅行预算攻略',
      description: '欧洲背包旅行是许多旅行者的梦想。本文详细介绍如何在预算有限的情况下畅游欧洲，涵盖交通、住宿、餐饮、景点等各方面省钱技巧，助你实现欧洲梦。',
      category: 'budget',
      icon: 'Wallet',
      tags: ['欧洲', '背包客', '省钱攻略', '穷游', '预算规划'],
      featured: false,
      views: 11200,
      readTime: '9分钟',
      image: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>💰 预算规划</h2>
        <p><strong>基础预算参考：</strong></p>
        <ul>
          <li><strong>东欧</strong>：200-300元/天</li>
          <li><strong>南欧</strong>：250-400元/天</li>
          <li><strong>西欧</strong>：400-600元/天</li>
          <li><strong>北欧</strong>：600-800元/天</li>
        </ul>
        <h3>✈️ 交通省钱</h3>
        <p><strong>1. 机票预订</strong> - 提前2-3个月预订，价格可节省50%</p>
        <p><strong>2. 欧洲境内交通</strong></p>
        <ul>
          <li><strong>Eurail Pass</strong>：欧洲火车通票可节省30-50%</li>
          <li><strong>廉航</strong>：瑞安航空、易捷航空等廉航机票低至€10-30</li>
          <li><strong>FlixBus</strong>：长途巴士，价格比火车便宜50-70%</li>
        </ul>
        <h3>🏨 住宿选择</h3>
        <p><strong>预算住宿：</strong></p>
        <ul>
          <li><strong>青旅</strong>：床位€15-35/晚</li>
          <li><strong>爱彼迎</strong>：合租房间€25-50/晚</li>
          <li><strong>Couchsurfing</strong>：免费沙发客体验</li>
        </ul>
      </div>`
    },
    {
      id: 12,
      title: '风景摄影构图技巧大全',
      description: '构图是摄影的灵魂。本文深入讲解三分法、引导线、框架构图、对称构图等多种构图技巧，并通过实例分析帮助你掌握如何运用构图拍摄出令人惊叹的风景照片。',
      category: 'photography',
      icon: 'Camera',
      tags: ['风景摄影', '构图技巧', '拍摄角度', '光影运用'],
      featured: false,
      views: 9500,
      readTime: '9分钟',
      image: 'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=800&q=80',
      contentTemplate: `<div class='article-section'>
        <h2>📐 基础构图法则</h2>
        <p><strong>1. 三分法</strong> - 将画面分为九宫格，主体放置在交点或线条上</p>
        <p><strong>2. 引导线构图</strong> - 利用场景中的线条引导观众视线至主体</p>
        <p><strong>3. 框架构图</strong> - 透过门框、窗户、树枝等天然框架拍摄</p>
        <p><strong>4. 对称构图</strong> - 利用场景的对称性创造稳定、平衡的画面</p>
        <h3>🎨 进阶构图技巧</h3>
        <p><strong>5. 黄金分割</strong> - 比三分法更精确的构图比例（1:0.618）</p>
        <p><strong>6. 前景运用</strong> - 在画面中加入前景元素增加层次感</p>
        <p><strong>7. 负空间</strong> - 在主体周围留出空白区域，增强视觉冲击力</p>
        <h3>🌅 特殊场景构图</h3>
        <p><strong>日出日落：</strong>太阳放在1/3位置，水面倒影增加对称感</p>
        <p><strong>山脉：</strong>前景引导线至山体，山体放置在黄金分割点</p>
      </div>`
    }
  ]
}

// Handle URL query parameters for category filtering
onMounted(() => {
  const tab = route.query.tab as string
  if (tab && ['planning', 'photography', 'destinations', 'food', 'safety', 'budget'].includes(tab)) {
    selectedCategory.value = tab
  }
})

// Categories
const categories = ref([
  { id: 'all', name: '全部', icon: 'Reading', count: guideContent.articles.length },
  { id: 'planning', name: '行前准备', icon: Suitcase, count: 0 },
  { id: 'photography', name: '摄影技巧', icon: Camera, count: 0 },
  { id: 'destinations', name: '目的地指南', icon: MapLocation, count: 0 },
  { id: 'food', name: '美食攻略', icon: Food, count: 0 },
  { id: 'safety', name: '安全健康', icon: FirstAidKit, count: 0 },
  { id: 'budget', name: '省钱攻略', icon: Wallet, count: 0 }
])

// Count articles per category
categories.value.forEach(cat => {
  if (cat.id !== 'all') {
    cat.count = guideContent.articles.filter(a => a.category === cat.id).length
  }
})

// Featured articles
const featuredArticles = computed(() => {
  return guideContent.articles
    .filter(a => a.featured)
    .slice(0, 4)
    .map(article => ({
      ...article,
      image: article.image || getDefaultImage(article.category),
      excerpt: article.description?.substring(0, 100) + '...'
    }))
})

// All articles
const allArticles = computed(() => {
  return guideContent.articles.map(article => ({
    ...article,
    color: getCategoryColor(article.category)
  }))
})

// Filtered articles
const filteredArticles = computed(() => {
  let articles = allArticles.value

  // Filter by category
  if (selectedCategory.value !== 'all' && selectedCategory.value !== 'featured') {
    articles = articles.filter(a => a.category === selectedCategory.value)
  }

  // Filter by search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    articles = articles.filter(a =>
      a.title.toLowerCase().includes(query) ||
      a.description.toLowerCase().includes(query) ||
      a.tags.some(t => t.toLowerCase().includes(query))
    )
  }

  return articles
})

// Methods
const selectCategory = (categoryId: string) => {
  selectedCategory.value = categoryId
}

const getCategoryTitle = () => {
  const cat = categories.value.find(c => c.id === selectedCategory.value)
  return cat?.name || '全部攻略'
}

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    planning: '#3B82F6',
    photography: '#8B5CF6',
    destinations: '#10B981',
    food: '#F59E0B',
    safety: '#EF4444',
    budget: '#6366F1'
  }
  return colors[category] || '#64748B'
}

const getDefaultImage = (category: string) => {
  const images: Record<string, string> = {
    planning: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
    photography: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800',
    destinations: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800',
    food: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800',
    safety: 'https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800',
    budget: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800'
  }
  return images[category] || 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800'
}

const openArticle = (article: any) => {
  currentArticle.value = {
    ...article,
    content: generateArticleContent(article)
  }
  showArticleModal.value = true
}

const generateArticleContent = (article: any) => {
  // Generate full article content based on article type
  if (article.contentTemplate) {
    return article.contentTemplate
  }
  return `
    <div class="article-section">
      <h2>关于${article.title}</h2>
      <p>${article.description}</p>
      <h3>主要内容</h3>
      <ul>
        ${article.tags.map(tag => `<li>${tag}相关内容</li>`).join('')}
      </ul>
    </div>
  `
}
</script>

<style scoped>
.guide-center {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0 4rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Header */
.header {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.title-icon {
  font-size: 3rem;
}

.subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
}

/* Search */
.search-section {
  margin-bottom: 2rem;
}

.search-input {
  max-width: 600px;
  margin: 0 auto;
  display: block;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 50px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Categories */
.categories {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  margin-bottom: 2rem;
  scrollbar-width: none;
}

.categories::-webkit-scrollbar {
  display: none;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: white;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.category-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.category-tab.active {
  background: white;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
}

.category-tab.active .category-icon {
  color: #0EA5E9;
}

.category-icon {
  font-size: 1.25rem;
  color: #64748B;
}

.category-name {
  font-weight: 500;
  color: #0F172A;
}

.category-count {
  background: #F1F5F9;
  padding: 0.125rem 0.5rem;
  border-radius: 99px;
  font-size: 0.75rem;
  color: #64748B;
}

/* Content Grid */
.content-grid {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* Section Title */
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1.5rem;
}

.section-title .el-icon {
  font-size: 1.75rem;
}

/* Featured Cards */
.featured-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.featured-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.featured-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 0.375rem 0.75rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #0F172A;
}

.card-content {
  padding: 1.25rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.5rem;
}

.card-excerpt {
  font-size: 0.875rem;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.card-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #94A3B8;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Articles List */
.articles-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.article-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #F1F5F9;
}

.article-item:last-child {
  border-bottom: none;
}

.article-item:hover {
  background: #F8FAFC;
}

.article-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-size: 1.5rem;
}

.article-content {
  flex: 1;
  min-width: 0;
}

.article-title {
  font-size: 1rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 0.25rem;
}

.article-description {
  font-size: 0.875rem;
  color: #64748B;
  margin-bottom: 0.5rem;
}

.article-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.article-tag {
  padding: 0.25rem 0.5rem;
  background: #F1F5F9;
  border-radius: 6px;
  font-size: 0.7rem;
  color: #64748B;
}

.article-arrow {
  color: #CBD5E1;
  font-size: 1.25rem;
  flex-shrink: 0;
}

/* Article Modal */
.article-modal :deep(.el-dialog__body) {
  padding: 0;
}

.article-content {
  padding: 2rem;
}

.article-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #E5E7EB;
}

.article-meta-info {
  display: flex;
  gap: 1rem;
}

.meta-tag {
  background: #0EA5E9;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
}

.meta-time {
  color: #64748B;
  font-size: 0.875rem;
}

.article-body {
  font-size: 1rem;
  line-height: 1.8;
  color: #374151;
}

.article-body h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #0F172A;
}

.article-body h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #1F2937;
}

.article-body p {
  margin-bottom: 1rem;
}

.article-body ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.article-body li {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .title {
    font-size: 1.75rem;
  }

  .featured-cards {
    grid-template-columns: 1fr;
  }

  .article-item {
    flex-wrap: wrap;
  }
}
</style>
