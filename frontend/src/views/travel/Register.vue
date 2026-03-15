<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- 左侧品牌区 -->
      <div class="auth-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="40" cy="40" r="36" fill="white" fill-opacity="0.1"/>
              <path d="M40 12L48 28H64L52 40L56 56L40 46L24 56L28 40L16 28H32L40 12Z" fill="white"/>
              <circle cx="58" cy="22" r="6" fill="#FFC107"/>
            </svg>
          </div>
          <h1 class="brand-title">加入我们</h1>
          <p class="brand-subtitle">开启您的智能旅行之旅</p>

          <div class="brand-benefits">
            <div class="benefit-item">
              <div class="benefit-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="white"/>
                </svg>
              </div>
              <div class="benefit-text">
                <div class="benefit-title">智能推荐</div>
                <div class="benefit-desc">AI根据您的喜好定制行程</div>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="white" stroke-width="2"/>
                  <path d="M12 6V12L16 14" stroke="white" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="benefit-text">
                <div class="benefit-title">实时更新</div>
                <div class="benefit-desc">目的地情报即时同步</div>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 8V12L15 15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="12" r="9" stroke="white" stroke-width="2"/>
                </svg>
              </div>
              <div class="benefit-text">
                <div class="benefit-title">节省时间</div>
                <div class="benefit-desc">一键生成完整旅行计划</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="auth-form">
        <div class="form-container">
          <div class="form-header">
            <h2>创建账户</h2>
            <p>填写信息开始您的旅行规划</p>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            @submit.prevent="handleRegister"
            class="register-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="用户名"
                size="large"
                :prefix-icon="User"
              >
                <template #suffix>
                  <span class="input-hint">{{ form.username.length }}/20</span>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="form.email"
                placeholder="邮箱地址"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="phone">
              <el-input
                v-model="form.phone"
                placeholder="手机号（可选）"
                size="large"
                :prefix-icon="Phone"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
              <div class="password-strength">
                <div
                  v-for="i in 4"
                  :key="i"
                  class="strength-bar"
                  :class="{ active: i <= passwordStrength }"
                ></div>
              </div>
              <div class="password-hint">{{ passwordHint }}</div>
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>

            <el-form-item prop="agree">
              <el-checkbox v-model="form.agree">
                我已阅读并同意
                <el-link type="primary" :underline="false">《用户协议》</el-link>
                和
                <el-link type="primary" :underline="false">《隐私政策》</el-link>
              </el-checkbox>
            </el-form-item>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!form.agree"
              class="submit-btn"
              @click="handleRegister"
            >
              创建账户
            </el-button>
          </el-form>

          <div class="form-footer">
            <span>已有账号？</span>
            <el-link type="primary" :underline="false" @click="goToLogin">立即登录</el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Phone } from '@element-plus/icons-vue'
import { useTravelAuthStore } from '@/stores/travelAuth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useTravelAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = form.password
  if (!password) return 0

  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 10) strength++
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++

  return Math.min(strength, 4)
})

const passwordHint = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return ''
  if (strength <= 1) return '弱：建议使用更复杂的密码'
  if (strength === 2) return '中等：可以更强'
  if (strength === 3) return '强：密码安全性良好'
  return '很强：密码非常安全'
})

const validateUsername = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请输入用户名'))
  }
  if (value.length < 3) {
    return callback(new Error('用户名至少3位'))
  }
  if (value.length > 20) {
    return callback(new Error('用户名最多20位'))
  }
  if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(value)) {
    return callback(new Error('用户名只能包含字母、数字、下划线和中文'))
  }
  callback()
}

const validateEmail = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请输入邮箱'))
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    return callback(new Error('请输入有效的邮箱地址'))
  }
  callback()
}

const validatePassword = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请输入密码'))
  }
  if (value.length < 6) {
    return callback(new Error('密码至少6位'))
  }
  if (!/[A-Za-z]/.test(value)) {
    return callback(new Error('密码必须包含字母'))
  }
  if (!/\d/.test(value)) {
    return callback(new Error('密码必须包含数字'))
  }
  callback()
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请确认密码'))
  }
  if (value !== form.password) {
    return callback(new Error('两次输入的密码不一致'))
  }
  callback()
}

const rules: FormRules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  agree: [
    {
      validator: (rule: any, value: boolean, callback: any) => {
        if (!value) {
          return callback(new Error('请阅读并同意用户协议'))
        }
        callback()
      },
      trigger: 'change'
    }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const result = await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined
      })

      if (result.success) {
        ElMessage.success('注册成功，正在跳转...')
        setTimeout(() => {
          router.push('/travel/planner')
        }, 1000)
      } else {
        ElMessage.error(result.message || '注册失败')
      }
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/travel/login')
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  padding: 20px;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1100px;
  min-height: 700px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(76, 175, 80, 0.15);
  overflow: hidden;
}

/* 品牌区 */
.auth-brand {
  flex: 1;
  background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.auth-brand::before {
  content: '';
  position: absolute;
  top: -30%;
  left: -20%;
  width: 60%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.15; }
  50% { transform: scale(1.1); opacity: 0.25; }
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 32px;
  animation: logoFloat 4s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.95;
  margin-bottom: 48px;
}

.brand-benefits {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.benefit-icon {
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.benefit-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.benefit-desc {
  font-size: 13px;
  opacity: 0.85;
}

/* 表单区 */
.auth-form {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: white;
  overflow-y: auto;
}

.form-container {
  width: 100%;
  max-width: 420px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #212121;
  margin-bottom: 8px;
}

.form-header p {
  color: #757575;
  font-size: 14px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 16px;
  height: 48px;
  box-shadow: 0 0 0 1px #E0E0E0 inset;
  transition: all 0.25s;
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #C8E6C9 inset;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.input-hint {
  font-size: 12px;
  color: #9E9E9E;
}

.password-strength {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #E0E0E0;
  border-radius: 2px;
  transition: all 0.3s;
}

.strength-bar.active:nth-child(1) { background: #F44336; }
.strength-bar.active:nth-child(2) { background: #FF9800; }
.strength-bar.active:nth-child(3) { background: #FFC107; }
.strength-bar.active:nth-child(4) { background: #4CAF50; }

.password-hint {
  font-size: 12px;
  color: #757575;
  margin-top: 8px;
}

.submit-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
  border: none;
  transition: all 0.25s;
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  color: #757575;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .auth-container {
    flex-direction: column;
    max-width: 500px;
    min-height: auto;
  }

  .auth-brand {
    padding: 48px 32px;
    min-height: 300px;
  }

  .brand-title {
    font-size: 28px;
  }

  .auth-form {
    padding: 48px 32px;
  }
}

@media (max-width: 480px) {
  .auth-page {
    padding: 12px;
  }

  .auth-brand {
    padding: 36px 20px;
  }

  .auth-form {
    padding: 36px 20px;
  }

  .form-header h2 {
    font-size: 24px;
  }
}
</style>
