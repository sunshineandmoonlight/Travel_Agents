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
              <path d="M20 60L28 52L36 56L28 60L20 64L28 68L36 64L28 60Z" fill="#4CAF50"/>
              <path d="M50 60L58 52L66 56L58 60L50 64L58 68L66 64L58 60Z" fill="#4CAF50"/>
            </svg>
          </div>
          <h1 class="brand-title">智能旅行规划</h1>
          <p class="brand-subtitle">AI驱动的个性化旅行体验</p>

          <div class="brand-stats">
            <div class="stat-item">
              <div class="stat-value">100+</div>
              <div class="stat-label">热门目的地</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">10K+</div>
              <div class="stat-label">满意用户</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">98%</div>
              <div class="stat-label">好评率</div>
            </div>
          </div>

          <div class="brand-features">
            <div class="feature-item">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 2L4 7V10C4 12.7614 6.23858 15 9 15C11.7614 15 14 12.7614 14 10V7L9 2Z" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>实时风险评估</span>
            </div>
            <div class="feature-item">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 3C11.4853 3 13.5 5.01472 13.5 7.5V9H4.5V7.5C4.5 5.01472 6.51472 3 9 3Z" stroke="white" stroke-width="1.5"/>
                <path d="M6 9V12C6 13.6569 7.34315 15 9 15C10.6569 15 12 13.6569 12 12V9" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 1V4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5.5 3L6.5 5" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12.5 3L11.5 5" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>智能行程规划</span>
            </div>
            <div class="feature-item">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="9" r="3" stroke="white" stroke-width="1.5"/>
                <path d="M9 3C11.4853 3 13.5 5.01472 13.5 7.5C13.5 9.98528 11.4853 12 9 12C6.51472 12 4.5 9.98528 4.5 7.5C4.5 5.01472 6.51472 3 9 3Z" stroke="white" stroke-width="1.5"/>
                <path d="M15 16C15 12.6863 12.3137 10 9 10C5.68629 10 3 12.6863 3 16" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>个性化推荐</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="auth-form">
        <div class="form-container">
          <div class="form-header">
            <h2>欢迎回来</h2>
            <p>登录开始您的智能旅行规划之旅</p>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            @submit.prevent="handleLogin"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="邮箱或用户名"
                size="large"
                :prefix-icon="User"
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
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="form.remember">记住我</el-checkbox>
              <el-link type="primary" :underline="false">忘记密码？</el-link>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="submit-btn"
              @click="handleLogin"
            >
              登录
            </el-button>

            <div class="social-login">
              <div class="divider">
                <span>或使用以下方式登录</span>
              </div>
              <div class="social-buttons">
                <el-button class="social-btn" circle>
                  <svg width="20" height="20" viewBox="0 0 20 20">
                    <path d="M10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2ZM10 16C6.68629 16 4 13.3137 4 10C4 6.68629 6.68629 4 10 4C13.3137 4 16 6.68629 16 10C16 13.3137 13.3137 16 10 16Z" fill="#E53935"/>
                    <path d="M13 10C13 11.6569 11.6569 13 10 13C8.34315 13 7 11.6569 7 10C7 8.34315 8.34315 7 10 7C11.6569 7 13 8.34315 13 10Z" fill="white"/>
                  </svg>
                </el-button>
                <el-button class="social-btn" circle>
                  <svg width="20" height="20" viewBox="0 0 20 20">
                    <path d="M10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2ZM8.5 13L7.5 12L8.5 11V13ZM11.5 13L12.5 12L11.5 11V13Z" fill="#07C160"/>
                  </svg>
                </el-button>
              </div>
            </div>
          </el-form>

          <div class="form-footer">
            <span>还没有账号？</span>
            <el-link type="primary" :underline="false" @click="goToRegister">立即注册</el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useTravelAuthStore } from '@/stores/travelAuth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useTravelAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入邮箱或用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const result = await authStore.loginAction({
        username: form.username,
        password: form.password
      })

      if (result.success) {
        ElMessage.success(result.message || '登录成功')
        const redirect = router.currentRoute.value.query.redirect as string
        router.push(redirect || '/travel/planner')
      } else {
        ElMessage.error(result.message || '登录失败')
      }
    } finally {
      loading.value = false
    }
  })
}

const goToRegister = () => {
  router.push('/travel/register')
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  padding: 20px;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1100px;
  min-height: 650px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(33, 150, 243, 0.15);
  overflow: hidden;
}

/* 品牌区 */
.auth-brand {
  flex: 1;
  background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%);
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
  top: -50%;
  right: -30%;
  width: 80%;
  height: 150%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-20px, -20px) rotate(5deg); }
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
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(2deg); }
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.95;
  margin-bottom: 48px;
  font-weight: 400;
}

.brand-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 48px;
  padding: 24px 0;
  border-top: 1px solid rgba(255,255,255,0.2);
  border-bottom: 1px solid rgba(255,255,255,0.2);
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
  font-size: 12px;
  opacity: 0.8;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  opacity: 0.9;
}

/* 表单区 */
.auth-form {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: white;
}

.form-container {
  width: 100%;
  max-width: 420px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
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

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 16px;
  height: 48px;
  box-shadow: 0 0 0 1px #E0E0E0 inset;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #BBDEFB inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.submit-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.social-login {
  margin-top: 24px;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin-bottom: 20px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #E0E0E0;
}

.divider span {
  padding: 0 16px;
  color: #9E9E9E;
  font-size: 12px;
}

.social-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 44px;
  height: 44px;
  border: 1px solid #E0E0E0;
  background: white;
  transition: all 0.25s;
}

.social-btn:hover {
  border-color: #2196F3;
  background: #F5F5F5;
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
    min-height: 280px;
  }

  .brand-title {
    font-size: 28px;
  }

  .brand-stats {
    gap: 24px;
  }

  .stat-value {
    font-size: 24px;
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

  .brand-stats {
    flex-direction: column;
    gap: 16px;
  }

  .auth-form {
    padding: 36px 20px;
  }

  .form-header h2 {
    font-size: 24px;
  }
}
</style>
