<template>
  <div class="guide-edit-page" v-loading="loading">
    <div class="edit-header">
      <div class="header-container">
        <el-button class="back-btn" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-title">
          <h1>{{ isEditMode ? '编辑攻略' : '新建攻略' }}</h1>
          <p v-if="guideForm.title">{{ guideForm.title }}</p>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            <el-icon><Select /></el-icon>
            保存
          </el-button>
        </div>
      </div>
    </div>

    <div class="edit-content">
      <el-form :model="guideForm" label-width="100px" class="edit-form">
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
          </template>

          <el-form-item label="攻略标题" required>
            <el-input
              v-model="guideForm.title"
              placeholder="请输入攻略标题"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="目的地" required>
            <el-input v-model="guideForm.destination" disabled />
          </el-form-item>

          <el-form-item label="天数" required>
            <el-input-number v-model="guideForm.total_days" :min="1" :max="30" />
          </el-form-item>

          <el-form-item label="预算">
            <el-input-number
              v-model="guideForm.budget"
              :min="0"
              :step="100"
              :precision="0"
              placeholder="总预算"
            />
            <span class="unit">元</span>
          </el-form-item>

          <el-form-item label="标签">
            <el-select
              v-model="guideForm.tags"
              multiple
              filterable
              allow-create
              placeholder="请选择或输入标签"
              style="width: 100%"
            >
              <el-option label="海滨" value="海滨" />
              <el-option label="美食" value="美食" />
              <el-option label="文化" value="文化" />
              <el-option label="历史" value="历史" />
              <el-option label="自然" value="自然" />
              <el-option label="休闲" value="休闲" />
              <el-option label="摄影" value="摄影" />
              <el-option label="购物" value="购物" />
              <el-option label="探险" value="探险" />
            </el-select>
          </el-form-item>

          <el-form-item label="状态">
            <el-radio-group v-model="guideForm.status">
              <el-radio label="draft">草稿</el-radio>
              <el-radio label="published">已发布</el-radio>
              <el-radio label="archived">已归档</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="公开设置">
            <el-switch
              v-model="guideForm.is_public"
              active-text="公开"
              inactive-text="私密"
            />
            <div class="form-tip">公开后其他用户可以看到此攻略</div>
          </el-form-item>
        </el-card>

        <!-- 行程编辑 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Calendar /></el-icon>
              <span>行程安排</span>
              <el-button
                type="primary"
                size="small"
                @click="addDay"
                :disabled="guideForm.total_days >= dailyItinerary.length"
              >
                <el-icon><Plus /></el-icon>
                添加一天
              </el-button>
            </div>
          </template>

          <div class="days-container">
            <div
              v-for="(day, dayIndex) in dailyItinerary"
              :key="day.day"
              class="day-section"
            >
              <div class="day-section-header">
                <h3>第{{ day.day }}天</h3>
                <div class="day-actions">
                  <el-input
                    v-model="day.title"
                    placeholder="当天标题"
                    size="small"
                    style="width: 200px"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    plain
                    @click="removeDay(dayIndex)"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </div>

              <el-input
                v-model="day.description"
                type="textarea"
                placeholder="当天简介"
                :rows="2"
                class="day-description"
              />

              <div class="activities-list">
                <div class="activities-header">
                  <span>活动安排</span>
                  <el-button size="small" @click="addActivity(dayIndex)">
                    <el-icon><Plus /></el-icon>
                    添加活动
                  </el-button>
                </div>

                <div
                  v-for="(activity, index) in day.activities"
                  :key="activity.id"
                  class="activity-item"
                >
                    <div class="activity-drag">
                      <el-icon class="drag-handle"><Rank /></el-icon>
                    </div>
                    <div class="activity-time">
                      <el-time-picker
                        v-model="activity.timeValue"
                        format="HH:mm"
                        value-format="HH:mm"
                        size="small"
                        placeholder="时间"
                      />
                    </div>
                    <div class="activity-type">
                      <el-select
                        v-model="activity.type"
                        size="small"
                        placeholder="类型"
                      >
                        <el-option label="景点" value="attraction" />
                        <el-option label="交通" value="transport" />
                        <el-option label="餐饮" value="meal" />
                        <el-option label="购物" value="shopping" />
                        <el-option label="住宿" value="hotel" />
                        <el-option label="其他" value="other" />
                      </el-select>
                    </div>
                    <div class="activity-name">
                      <el-input
                        v-model="activity.name"
                        size="small"
                        placeholder="活动名称"
                      />
                    </div>
                    <div class="activity-cost">
                      <el-input-number
                        v-model="activity.cost"
                        size="small"
                        :min="0"
                        :precision="0"
                        placeholder="费用"
                      />
                    </div>
                    <div class="activity-actions">
                      <el-button
                        type="primary"
                        size="small"
                        text
                        @click="editActivity(dayIndex, index)"
                      >
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button
                        type="danger"
                        size="small"
                        text
                        @click="removeActivity(dayIndex, index)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
            </div>
          </div>
        </el-card>

        <!-- 预算详情 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Wallet /></el-icon>
              <span>预算详情</span>
            </div>
          </template>

          <div class="budget-items">
            <div class="budget-row">
              <span class="budget-label">住宿</span>
              <el-input-number
                v-model="budgetBreakdown.accommodation"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <div class="budget-row">
              <span class="budget-label">交通</span>
              <el-input-number
                v-model="budgetBreakdown.transport"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <div class="budget-row">
              <span class="budget-label">餐饮</span>
              <el-input-number
                v-model="budgetBreakdown.dining"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <div class="budget-row">
              <span class="budget-label">门票</span>
              <el-input-number
                v-model="budgetBreakdown.tickets"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <div class="budget-row">
              <span class="budget-label">购物</span>
              <el-input-number
                v-model="budgetBreakdown.shopping"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <div class="budget-row">
              <span class="budget-label">其他</span>
              <el-input-number
                v-model="budgetBreakdown.other"
                :min="0"
                :precision="0"
              />
              <span class="budget-unit">元</span>
            </div>
            <el-divider />
            <div class="budget-row total">
              <span class="budget-label">总计</span>
              <span class="budget-total">¥{{ totalBudget.toLocaleString() }}</span>
            </div>
          </div>
        </el-card>

        <!-- 旅行贴士 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>旅行贴士</span>
            </div>
          </template>

          <el-form-item label="综合建议">
            <el-input
              v-model="tips.general"
              type="textarea"
              :rows="3"
              placeholder="填写综合建议..."
            />
          </el-form-item>

          <el-form-item label="行李准备">
            <el-input
              v-model="tips.packing"
              type="textarea"
              :rows="2"
              placeholder="填写行李准备建议..."
            />
          </el-form-item>

          <el-form-item label="天气提醒">
            <el-input
              v-model="tips.weather"
              type="textarea"
              :rows="2"
              placeholder="填写天气相关提醒..."
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>

    <!-- 活动详情编辑对话框 -->
    <el-dialog
      v-model="activityDialogVisible"
      title="编辑活动详情"
      width="600px"
    >
      <el-form :model="editingActivity" label-width="80px">
        <el-form-item label="活动名称">
          <el-input v-model="editingActivity.name" />
        </el-form-item>
        <el-form-item label="详细描述">
          <el-input
            v-model="editingActivity.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editingActivity.address" />
        </el-form-item>
        <el-form-item label="时长">
          <el-input v-model="editingActivity.duration" placeholder="如：2小时" />
        </el-form-item>
        <el-form-item label="费用">
          <el-input-number v-model="editingActivity.cost" :min="0" />
        </el-form-item>
        <el-form-item label="贴士">
          <el-input
            v-model="editingActivity.tips"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="activityDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveActivityDetail">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, InfoFilled, Calendar, Wallet, Plus, Delete, Edit,
  Select, Rank
} from '@element-plus/icons-vue'
import { getGuideDetail, updateGuide, saveGuide } from '@/api/travel/guides'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const isEditMode = ref(false)

// 表单数据
const guideForm = ref({
  id: '',
  title: '',
  destination: '',
  total_days: 3,
  budget: 0,
  tags: [] as string[],
  status: 'draft' as 'draft' | 'published' | 'archived',
  is_public: false
})

// 每日行程
const dailyItinerary = ref<any[]>([])

// 预算明细
const budgetBreakdown = ref({
  accommodation: 0,
  transport: 0,
  dining: 0,
  tickets: 0,
  shopping: 0,
  other: 0
})

// 旅行贴士
const tips = ref({
  general: '',
  packing: '',
  weather: ''
})

// 活动编辑
const activityDialogVisible = ref(false)
const editingActivity = ref<any>({})
const currentDayIndex = ref(-1)
const currentActivityIndex = ref(-1)

// 计算总预算
const totalBudget = computed(() => {
  return Object.values(budgetBreakdown.value).reduce((sum, val) => sum + (val || 0), 0)
})

// 添加一天
const addDay = () => {
  const newDay = dailyItinerary.value.length + 1
  dailyItinerary.value.push({
    day: newDay,
    title: `第${newDay}天`,
    description: '',
    activities: [],
    summary: ''
  })
  guideForm.value.total_days = Math.max(guideForm.value.total_days, newDay)
}

// 删除一天
const removeDay = (index: number) => {
  dailyItinerary.value.splice(index, 1)
  // 重新编号
  dailyItinerary.value.forEach((day, i) => {
    day.day = i + 1
    day.title = `第${i + 1}天`
  })
  guideForm.value.total_days = dailyItinerary.value.length
}

// 添加活动
const addActivity = (dayIndex: number) => {
  dailyItinerary.value[dayIndex].activities.push({
    id: Date.now(),
    time: '',
    timeValue: '',
    period: '',
    type: 'attraction',
    name: '',
    description: '',
    address: '',
    cost: 0,
    duration: '',
    tips: ''
  })
}

// 删除活动
const removeActivity = (dayIndex: number, activityIndex: number) => {
  dailyItinerary.value[dayIndex].activities.splice(activityIndex, 1)
}

// 编辑活动详情
const editActivity = (dayIndex: number, activityIndex: number) => {
  currentDayIndex.value = dayIndex
  currentActivityIndex.value = activityIndex
  editingActivity.value = { ...dailyItinerary.value[dayIndex].activities[activityIndex] }
  activityDialogVisible.value = true
}

// 保存活动详情
const saveActivityDetail = () => {
  if (currentDayIndex.value >= 0 && currentActivityIndex.value >= 0) {
    dailyItinerary.value[currentDayIndex.value].activities[currentActivityIndex.value] = {
      ...editingActivity.value,
      time: editingActivity.value.timeValue || editingActivity.value.time
    }
  }
  activityDialogVisible.value = false
}

// 加载攻略数据
const loadGuideData = async () => {
  try {
    loading.value = true
    const guideId = route.params.id as string

    if (guideId && guideId !== 'new') {
      isEditMode.value = true
      const data = await getGuideDetail(guideId)

      // 填充基本信息
      guideForm.value = {
        id: data.id,
        title: data.title,
        destination: data.destination,
        total_days: data.total_days,
        budget: data.budget,
        tags: data.tags || [],
        status: data.status,
        is_public: data.is_public
      }

      // 填充行程数据
      if (data.guide_data?.daily_itinerary) {
        dailyItinerary.value = data.guide_data.daily_itinerary.map((day: any) => ({
          ...day,
          activities: (day.activities || []).map((act: any) => ({
            ...act,
            id: act.id || Date.now() + Math.random(),
            timeValue: act.time || ''
          }))
        }))
      } else if (data.guide_data?.schedule) {
        // 转换旧格式
        dailyItinerary.value = convertScheduleToDaily(data.guide_data.schedule)
      }

      // 填充预算数据
      if (data.guide_data?.budget_breakdown) {
        budgetBreakdown.value = { ...data.guide_data.budget_breakdown }
      }

      // 填充贴士数据
      if (data.guide_data?.tips) {
        tips.value = { ...data.guide_data.tips }
      }
    } else {
      // 新建模式，初始化默认数据
      initDefaultData()
    }
  } catch (error) {
    console.error('加载攻略数据失败:', error)
    ElMessage.error('加载失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 转换schedule格式到daily格式
const convertScheduleToDaily = (schedule: any) => {
  const days = []
  const maxDays = guideForm.value.total_days

  for (let i = 1; i <= maxDays; i++) {
    const activities = []

    // 收集所有时段的活动
    ['morning', 'afternoon', 'evening'].forEach(period => {
      const periodActivities = schedule[period]?.filter((a: any) => a.day === i) || []
      activities.push(...periodActivities.map((a: any) => ({
        ...a,
        id: Date.now() + Math.random(),
        period,
        timeValue: a.time || '',
        type: a.type || 'attraction',
        cost: a.cost || 0
      })))
    })

    days.push({
      day: i,
      title: `第${i}天`,
      description: '',
      activities,
      summary: ''
    })
  }

  return days
}

// 初始化默认数据
const initDefaultData = () => {
  for (let i = 1; i <= guideForm.value.total_days; i++) {
    dailyItinerary.value.push({
      day: i,
      title: `第${i}天`,
      description: '',
      activities: [],
      summary: ''
    })
  }
}

// 保存攻略
const handleSave = async () => {
  try {
    saving.value = true

    // 验证必填项
    if (!guideForm.value.title) {
      ElMessage.warning('请输入攻略标题')
      return
    }

    // 构建guide_data
    const guideData = {
      destination: guideForm.value.destination,
      total_days: guideForm.value.total_days,
      daily_itinerary: dailyItinerary.value,
      budget_breakdown: {
        ...budgetBreakdown.value,
        total_budget: totalBudget.value
      },
      tips: tips.value,
      budget_level: getBudgetLevel()
    }

    // 更新总预算
    guideForm.value.budget = totalBudget.value

    if (isEditMode.value) {
      // 更新现有攻略
      await updateGuide({
        guide_id: guideForm.value.id,
        title: guideForm.value.title,
        guide_data: guideData,
        tags: guideForm.value.tags,
        is_public: guideForm.value.is_public,
        status: guideForm.value.status
      })
      ElMessage.success('更新成功')
    } else {
      // 创建新攻略
      const userId = 'demo_user'
      await saveGuide({
        user_id: userId,
        title: guideForm.value.title,
        destination: guideForm.value.destination,
        total_days: guideForm.value.total_days,
        guide_data: guideData,
        budget: guideForm.value.budget,
        tags: guideForm.value.tags,
        is_public: guideForm.value.is_public
      })
      ElMessage.success('保存成功')
    }

    router.push('/travel/guides')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 获取预算等级
const getBudgetLevel = () => {
  const avg = totalBudget.value / guideForm.value.total_days
  if (avg < 500) return 'economy'
  if (avg < 1500) return 'standard'
  return 'luxury'
}

onMounted(() => {
  loadGuideData()
})
</script>

<style scoped>
.guide-edit-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.edit-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.back-btn {
  flex-shrink: 0;
}

.header-title {
  flex: 1;
}

.header-title h1 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.header-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.edit-content {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px 48px;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.unit {
  margin-left: 8px;
  color: #6b7280;
  font-size: 14px;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

/* Days */
.days-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.day-section {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  background: #fafafa;
}

.day-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.day-section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.day-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.day-description {
  margin-bottom: 16px;
}

/* Activities */
.activities-list {
  margin-top: 16px;
}

.activities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
}

.activity-drag {
  cursor: move;
  color: #9ca3af;
}

.drag-handle:hover {
  color: #6366f1;
}

.activity-time {
  width: 130px;
}

.activity-type {
  width: 100px;
}

.activity-name {
  flex: 1;
}

.activity-cost {
  width: 120px;
}

.activity-actions {
  display: flex;
  gap: 4px;
}

/* Budget */
.budget-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.budget-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.budget-label {
  width: 100px;
  font-size: 14px;
  color: #374151;
}

.budget-unit {
  color: #9ca3af;
  font-size: 14px;
}

.budget-row.total {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.budget-total {
  margin-left: auto;
  font-size: 20px;
  font-weight: 600;
  color: #6366f1;
}

/* Responsive */
@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
    padding: 12px 16px;
  }

  .header-title {
    width: 100%;
    order: -1;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .activity-item {
    flex-wrap: wrap;
  }

  .activity-time,
  .activity-type,
  .activity-cost {
    width: calc(50% - 8px);
  }

  .activity-name {
    width: 100%;
    order: -1;
  }
}
</style>
