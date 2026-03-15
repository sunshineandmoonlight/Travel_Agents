<template>
  <div class="requirements-form">
    <div class="container">
      <!-- Header -->
      <div class="header">
        <div class="header-badge">
          <el-icon><EditPen /></el-icon>
          <span>完善行程信息</span>
        </div>
        <h2 class="title">告诉我们您的旅行计划</h2>
        <p class="subtitle">填写基本信息，我们将为您推荐最合适的行程</p>
      </div>

      <!-- Progress Indicator -->
      <div class="progress-indicator">
        <div class="progress-item" :class="{ active: progress >= 1 }">
          <div class="progress-dot">
            <el-icon v-if="progress >= 1"><Check /></el-icon>
            <span v-else>1</span>
          </div>
          <span class="progress-label">行程基础</span>
        </div>
        <div class="progress-line" :class="{ active: progress >= 2 }"></div>
        <div class="progress-item" :class="{ active: progress >= 2 }">
          <div class="progress-dot">
            <el-icon v-if="progress >= 2"><Check /></el-icon>
            <span v-else>2</span>
          </div>
          <span class="progress-label">预算偏好</span>
        </div>
        <div class="progress-line" :class="{ active: progress >= 3 }"></div>
        <div class="progress-item" :class="{ active: progress >= 3 }">
          <div class="progress-dot">
            <el-icon v-if="progress >= 3"><Check /></el-icon>
            <span v-else>3</span>
          </div>
          <span class="progress-label">兴趣选择</span>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="form"
        size="large"
      >
        <!-- Section 1: Trip Basics -->
        <div class="form-section trip-basics">
          <div class="section-header">
            <div class="section-number">01</div>
            <div class="section-info">
              <h3 class="section-title">行程基础</h3>
              <p class="section-desc">选择您的出行时间和人数</p>
            </div>
          </div>

          <div class="section-content">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="出发日期" prop="startDate">
                  <el-date-picker
                    v-model="form.startDate"
                    type="date"
                    placeholder="选择出发日期"
                    :disabled-date="disabledDate"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    class="date-picker"
                  />
                </el-form-item>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-form-item label="旅行天数" prop="days">
                  <div class="number-input-wrapper">
                    <el-input-number
                      v-model="form.days"
                      :min="1"
                      :max="30"
                      controls-position="right"
                      style="width: 100%"
                    />
                    <span class="input-suffix">天</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="成人数量" prop="adults">
                  <div class="number-input-wrapper">
                    <el-input-number
                      v-model="form.adults"
                      :min="1"
                      :max="20"
                      controls-position="right"
                      style="width: 100%"
                    />
                    <span class="input-suffix">人</span>
                  </div>
                </el-form-item>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-form-item label="儿童数量" prop="children">
                  <div class="number-input-wrapper">
                    <el-input-number
                      v-model="form.children"
                      :min="0"
                      :max="10"
                      controls-position="right"
                      style="width: 100%"
                    />
                    <span class="input-suffix">人</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- Section 2: Budget -->
        <div class="form-section budget-section">
          <div class="section-header">
            <div class="section-number">02</div>
            <div class="section-info">
              <h3 class="section-title">预算范围</h3>
              <p class="section-desc">选择适合您的消费档次</p>
            </div>
          </div>

          <div class="section-content">
            <el-form-item prop="budget">
              <div class="budget-options">
                <div
                  class="budget-card"
                  :class="{ selected: form.budget === 'economy' }"
                  @click="form.budget = 'economy'"
                >
                  <div class="budget-icon economy">
                    <el-icon><Wallet /></el-icon>
                  </div>
                  <div class="budget-content">
                    <div class="budget-name">经济型</div>
                    <div class="budget-price">200-400元/人天</div>
                    <div class="budget-features">
                      <span class="feature-tag">实惠</span>
                      <span class="feature-tag">高性价比</span>
                    </div>
                  </div>
                  <div class="budget-check" v-if="form.budget === 'economy'">
                    <el-icon><Check /></el-icon>
                  </div>
                </div>

                <div
                  class="budget-card recommended"
                  :class="{ selected: form.budget === 'medium' }"
                  @click="form.budget = 'medium'"
                >
                  <div class="recommended-badge">推荐</div>
                  <div class="budget-icon medium">
                    <el-icon><Trophy /></el-icon>
                  </div>
                  <div class="budget-content">
                    <div class="budget-name">舒适型</div>
                    <div class="budget-price">400-800元/人天</div>
                    <div class="budget-features">
                      <span class="feature-tag">品质</span>
                      <span class="feature-tag">体验佳</span>
                    </div>
                  </div>
                  <div class="budget-check" v-if="form.budget === 'medium'">
                    <el-icon><Check /></el-icon>
                  </div>
                </div>

                <div
                  class="budget-card"
                  :class="{ selected: form.budget === 'luxury' }"
                  @click="form.budget = 'luxury'"
                >
                  <div class="budget-icon luxury">
                    <el-icon><Star /></el-icon>
                  </div>
                  <div class="budget-content">
                    <div class="budget-name">豪华型</div>
                    <div class="budget-price">800-1500元/人天</div>
                    <div class="budget-features">
                      <span class="feature-tag">奢华</span>
                      <span class="feature-tag">尊享</span>
                    </div>
                  </div>
                  <div class="budget-check" v-if="form.budget === 'luxury'">
                    <el-icon><Check /></el-icon>
                  </div>
                </div>
              </div>
            </el-form-item>
          </div>
        </div>

        <!-- Section 3: Interests -->
        <div class="form-section interests-section">
          <div class="section-header">
            <div class="section-number">03</div>
            <div class="section-info">
              <h3 class="section-title">兴趣爱好</h3>
              <p class="section-desc">至少选择一项您感兴趣的内容</p>
            </div>
            <div class="selection-count" :class="{ valid: form.interests.length >= 1 }">
              已选择 {{ form.interests.length }}/8
            </div>
          </div>

          <div class="section-content">
            <el-form-item prop="interests">
              <div class="interests-grid">
                <div
                  v-for="interest in interestOptions"
                  :key="interest.value"
                  class="interest-card"
                  :class="[
                    `interest-${interest.theme}`,
                    { selected: form.interests.includes(interest.value) }
                  ]"
                  @click="toggleInterest(interest.value)"
                >
                  <div class="interest-icon">{{ interest.icon }}</div>
                  <div class="interest-name">{{ interest.label }}</div>
                  <div class="interest-check" v-if="form.interests.includes(interest.value)">
                    <el-icon><Check /></el-icon>
                  </div>
                </div>
              </div>

              <div class="interests-actions">
                <el-button size="small" @click="selectAllInterests">全选</el-button>
                <el-button size="small" @click="clearInterests">清空</el-button>
              </div>
            </el-form-item>
          </div>
        </div>

        <!-- Section 4: Special Requests (Optional) -->
        <div class="form-section optional-section">
          <div class="section-header collapsible" @click="toggleOptional">
            <div class="section-number optional">
              <el-icon><Plus /></el-icon>
            </div>
            <div class="section-info">
              <h3 class="section-title">特殊需求</h3>
              <p class="section-desc">选填 - 有特殊要求请告诉我们</p>
            </div>
            <el-icon class="collapse-icon" :class="{ expanded: showOptional }"><ArrowDown /></el-icon>
          </div>

          <div class="section-content" v-show="showOptional">
            <el-form-item label=" ">
              <el-input
                v-model="form.specialRequests"
                type="textarea"
                :rows="3"
                placeholder="如有特殊需求请填写（选填）"
                maxlength="500"
                show-word-limit
                class="textarea-input"
              />
            </el-form-item>
          </div>
        </div>
      </el-form>

      <!-- Actions -->
      <div class="actions">
        <el-button size="large" class="nav-btn" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button type="primary" size="large" class="nav-btn nav-btn-primary" @click="handleSubmit" :loading="loading">
          下一步
          <el-icon class="ml-1"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ArrowLeft, ArrowRight, Wallet, Trophy, Star, Check, EditPen, Plus, ArrowDown } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const props = defineProps<{
  scope: string
}>()

const emit = defineEmits<{
  submit: [data: any]
  back: []
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const showOptional = ref(false)

// 获取今天的日期（YYYY-MM-DD格式）
const getTodayDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const form = reactive({
  startDate: getTodayDate(),  // 默认当天日期
  days: 3,                      // 默认3天
  adults: 1,                     // 默认1人
  children: 0,
  budget: 'medium',
  interests: ['自然风光'] as string[],  // 默认选择自然风光
  specialRequests: ''
})

// 组件挂载时初始化日期
onMounted(() => {
  if (!form.startDate) {
    form.startDate = getTodayDate()
  }
})

const rules: FormRules = {
  startDate: [{ required: true, message: '请选择出发日期', trigger: 'change' }],
  days: [{ required: true, message: '请输入旅行天数', trigger: 'blur' }],
  adults: [{ required: true, message: '请输入成人数量', trigger: 'blur' }],
  budget: [{ required: true, message: '请选择预算范围', trigger: 'change' }],
  interests: [{ type: 'array', min: 1, message: '请至少选择一个兴趣', trigger: 'change' }]
}

// Progress tracking
const progress = computed(() => {
  let p = 0
  if (form.startDate && form.days && form.adults) p = 1
  if (form.budget) p = 2
  if (form.interests.length >= 1) p = 3
  return p
})

const interestOptions = [
  { label: '历史文化', value: '历史文化', icon: '🏯', theme: 'history' },
  { label: '自然风光', value: '自然风光', icon: '🏔️', theme: 'nature' },
  { label: '美食', value: '美食', icon: '🍜', theme: 'food' },
  { label: '购物', value: '购物', icon: '🛍️', theme: 'shopping' },
  { label: '休闲度假', value: '休闲度假', icon: '🏖️', theme: 'leisure' },
  { label: '冒险探险', value: '冒险探险', icon: '🧗', theme: 'adventure' },
  { label: '艺术文化', value: '艺术文化', icon: '🎨', theme: 'art' },
  { label: '夜生活', value: '夜生活', icon: '🌃', theme: 'nightlife' }
]

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const toggleInterest = (value: string) => {
  const index = form.interests.indexOf(value)
  if (index > -1) {
    form.interests.splice(index, 1)
  } else {
    form.interests.push(value)
  }
}

const selectAllInterests = () => {
  form.interests = interestOptions.map(i => i.value)
}

const clearInterests = () => {
  form.interests = []
}

const toggleOptional = () => {
  showOptional.value = !showOptional.value
}

const handleBack = () => {
  emit('back')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      // 移除延迟，立即提交
      emit('submit', {
        ...form,
        travelScope: props.scope
      })
      loading.value = false
    }
  })
}
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.requirements-form {
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

  padding: 2rem 1rem 6rem;
}

/* ==================== */
/* Container              */
/* ==================== */
.container {
  max-width: 800px;
  margin: 0 auto;
}

/* ==================== */
/* Header                 */
/* ==================== */
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
  font-size: 1rem;
}

/* ==================== */
/* Progress Indicator     */
/* ==================== */
.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding: 0 2rem;
  animation: fadeInUp 0.5s ease-out 0.1s both;
}

.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.progress-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.progress-item.active .progress-dot {
  background: var(--color-success);
  color: var(--color-white);
  border-color: var(--color-success);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

.progress-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.progress-item.active .progress-label {
  color: var(--color-white);
}

.progress-line {
  width: 60px;
  height: 2px;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.progress-line.active {
  background: var(--color-success);
}

/* ==================== */
/* Form Sections          */
/* ==================== */
.form {
  margin-bottom: 2rem;
}

.form-section {
  background: var(--color-white);
  border-radius: 20px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease-out both;
}

.form-section:nth-child(2) { animation-delay: 0.1s; }
.form-section:nth-child(3) { animation-delay: 0.2s; }
.form-section:nth-child(4) { animation-delay: 0.3s; }

.form-section:hover {
  box-shadow: var(--shadow-xl);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  border-bottom: 1px solid #E2E8F0;
}

.section-header.collapsible {
  cursor: pointer;
  user-select: none;
}

.section-number {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Bodoni Moda', serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.section-number.optional {
  background: #E2E8F0;
  color: #64748B;
}

.section-info {
  flex: 1;
}

.section-title {
  font-family: 'Bodoni Moda', serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 0.25rem;
}

.section-desc {
  font-size: 0.875rem;
  color: #64748B;
}

.selection-count {
  padding: 0.375rem 0.75rem;
  background: #FEE2E2;
  color: #DC2626;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.selection-count.valid {
  background: #D1FAE5;
  color: #059669;
}

.collapse-icon {
  font-size: 1rem;
  color: #64748B;
  transition: transform 0.3s ease;
}

.collapse-icon.expanded {
  transform: rotate(180deg);
}

.section-content {
  padding: 1.5rem;
}

/* ==================== */
/* Number Input Wrapper    */
/* ==================== */
.number-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-suffix {
  position: absolute;
  right: 12px;
  font-size: 0.875rem;
  color: #64748B;
  pointer-events: none;
}

.number-input-wrapper :deep(.el-input-number) {
  width: 100%;
}

.number-input-wrapper :deep(.el-input-number .el-input__inner) {
  padding-right: 40px;
}

/* ==================== */
/* Budget Cards           */
/* ==================== */
.budget-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.budget-card {
  position: relative;
  padding: 1.25rem;
  border-radius: 16px;
  border: 2px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: var(--color-white);
}

.budget-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.budget-card.selected {
  border-color: var(--color-primary);
  background: #F0F9FF;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
}

.budget-card.recommended {
  border-color: var(--color-cta);
}

.budget-card.recommended.selected {
  background: #FFF7ED;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.15);
}

.recommended-badge {
  position: absolute;
  top: -8px;
  right: 12px;
  padding: 0.25rem 0.5rem;
  background: linear-gradient(135deg, var(--color-cta) 0%, #EA580C 100%);
  color: var(--color-white);
  font-size: 0.625rem;
  font-weight: 600;
  border-radius: 9999px;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.4);
}

.budget-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
  transition: all 0.2s ease;
}

.budget-icon.economy {
  background: #D1FAE5;
  color: #059669;
}

.budget-icon.medium {
  background: #DBEAFE;
  color: #3B82F6;
}

.budget-icon.luxury {
  background: #FEF3C7;
  color: #D97706;
}

.budget-name {
  font-weight: 600;
  color: #0F172A;
  font-size: 0.9375rem;
  margin-bottom: 0.375rem;
}

.budget-price {
  font-size: 0.8125rem;
  color: #64748B;
  margin-bottom: 0.75rem;
}

.budget-features {
  display: flex;
  gap: 0.375rem;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 0.125rem 0.5rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 9999px;
  font-size: 0.6875rem;
  color: #64748B;
  font-weight: 500;
}

.budget-check {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 24px;
  height: 24px;
  background: var(--color-success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  animation: scaleIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* ==================== */
/* Interests Grid         */
/* ==================== */
.interests-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.interest-card {
  position: relative;
  padding: 1rem 0.75rem;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  text-align: center;
  background: #F8FAFC;
}

.interest-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.interest-card.selected {
  border-color: currentColor;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.08);
}

.interest-history { color: #F59E0B; background: #FEF3C7; }
.interest-history.selected { background: #FEF3C7; border-color: #F59E0B; }

.interest-nature { color: #10B981; background: #D1FAE5; }
.interest-nature.selected { background: #D1FAE5; border-color: #10B981; }

.interest-food { color: #F97316; background: #FED7AA; }
.interest-food.selected { background: #FED7AA; border-color: #F97316; }

.interest-shopping { color: #EC4899; background: #FBCFE8; }
.interest-shopping.selected { background: #FBCFE8; border-color: #EC4899; }

.interest-leisure { color: #0EA5E9; background: #BAE6FD; }
.interest-leisure.selected { background: #BAE6FD; border-color: #0EA5E9; }

.interest-adventure { color: #EF4444; background: #FECACA; }
.interest-adventure.selected { background: #FECACA; border-color: #EF4444; }

.interest-art { color: #8B5CF6; background: #E9D5FF; }
.interest-art.selected { background: #E9D5FF; border-color: #8B5CF6; }

.interest-nightlife { color: #6366F1; background: #C7D2FE; }
.interest-nightlife.selected { background: #C7D2FE; border-color: #6366F1; }

.interest-icon {
  font-size: 1.5rem;
}

.interest-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: #475569;
}

.interest-check {
  position: absolute;
  top: 0.375rem;
  right: 0.375rem;
  width: 18px;
  height: 18px;
  background: currentColor;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  font-size: 0.625rem;
  animation: scaleIn 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.interests-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

/* ==================== */
/* Optional Section       */
/* ==================== */
.optional-section {
  opacity: 0.8;
}

.optional-section:hover {
  opacity: 1;
}

/* ==================== */
/* Actions                */
/* ==================== */
.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  animation: fadeInUp 0.5s ease-out 0.4s both;
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

.nav-btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
}

.nav-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
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
/* Responsive             */
/* ==================== */
@media (max-width: 640px) {
  .budget-options {
    grid-template-columns: 1fr;
  }

  .interests-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .actions {
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
  }

  .progress-indicator {
    padding: 0 1rem;
  }

  .progress-line {
    width: 30px;
  }

  .section-header {
    padding: 1rem;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .budget-card,
  .interest-card,
  .nav-btn,
  .form-section {
    animation: none;
    transition: none;
  }

  .budget-card:hover,
  .interest-card:hover,
  .nav-btn:hover,
  .form-section:hover {
    transform: none;
  }
}
</style>
