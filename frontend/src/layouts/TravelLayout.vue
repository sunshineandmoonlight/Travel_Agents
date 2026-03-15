<template>
  <div class="travel-layout" :class="{ 'mobile': isMobile }">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-container">
        <!-- Logo -->
        <div class="header-logo" @click="goHome">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <defs>
              <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#0EA5E9"/>
                <stop offset="100%" stop-color="#F97316"/>
              </linearGradient>
            </defs>
            <circle cx="18" cy="18" r="16" fill="url(#logo-gradient)" fill-opacity="0.1"/>
            <path d="M18 4L22 13H30L24 19L26 28L18 23L10 28L12 19L6 13H14L18 4Z" fill="url(#logo-gradient)"/>
          </svg>
          <span class="logo-text">智能旅行</span>
        </div>

        <!-- 桌面端导航 -->
        <nav class="header-nav desktop-only">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActive(item.path), 'external-link': item.external }"
          >
            <component :is="item.icon" class="nav-icon" />
            {{ item.title }}
            <el-icon v-if="item.external" class="external-icon"><Right /></el-icon>
          </router-link>
        </nav>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 用户信息 -->
          <template v-if="isAuthenticated">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="36" :src="userAvatar">
                  <UserFilled />
                </el-avatar>
                <span class="user-name">{{ userDisplayName }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <!-- 未登录 -->
          <template v-else>
            <el-button text @click="goToLogin">登录</el-button>
            <el-button type="primary" @click="goToRegister">注册</el-button>
          </template>

          <!-- 移动端菜单按钮 -->
          <el-button
            class="mobile-only"
            :icon="isMenuOpen ? Close : Menu"
            circle
            @click="toggleMenu"
          />
        </div>
      </div>
    </header>

    <!-- 移动端侧边菜单 -->
    <div class="mobile-menu" :class="{ open: isMenuOpen }">
      <div class="menu-overlay" @click="closeMenu"></div>
      <div class="menu-content">
        <div class="menu-header">
          <div class="header-logo" @click="goHome">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="12" fill="currentColor" fill-opacity="0.1"/>
              <path d="M14 3L17 11H24L19 16L21 23L14 19L7 23L9 16L4 11H11L14 3Z" fill="currentColor"/>
            </svg>
            <span class="logo-text">智能旅行</span>
          </div>
        </div>

        <nav class="menu-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="menu-link"
            :class="{ active: isActive(item.path) }"
            @click="closeMenu"
          >
            <component :is="item.icon" class="menu-icon" />
            {{ item.title }}
          </router-link>
        </nav>

        <div class="menu-footer">
          <template v-if="isAuthenticated">
            <div class="menu-user">
              <el-avatar :size="48" :src="userAvatar">
                <UserFilled />
              </el-avatar>
              <div class="menu-user-info">
                <div class="menu-user-name">{{ userDisplayName }}</div>
                <div class="menu-user-email">{{ userInfo?.email }}</div>
              </div>
            </div>
            <el-button class="menu-logout" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </template>
          <template v-else>
            <el-button class="menu-login" @click="goToLogin">登录</el-button>
            <el-button class="menu-register" type="primary" @click="goToRegister">注册</el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="layout-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚 -->
    <footer class="layout-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-section">
            <h4 class="footer-title">关于我们</h4>
            <p class="footer-text">智能旅行规划平台，让每一次旅行都成为美好回忆</p>
          </div>
          <div class="footer-section">
            <h4 class="footer-title">快速链接</h4>
            <div class="footer-links">
              <router-link to="/travel/planner">旅行规划</router-link>
              <router-link to="/travel/guides">我的攻略</router-link>
              <router-link to="/travel/intelligence">目的地情报</router-link>
            </div>
          </div>
          <div class="footer-section">
            <h4 class="footer-title">项目地址</h4>
            <div class="footer-contact">
              <div class="contact-item">
                <el-icon><Link /></el-icon>
                <a href="https://github.com/sunshineandmoonlight/travel_agent" target="_blank" rel="noopener">
                  github.com/sunshineandmoonlight/travel_agent
                </a>
              </div>
              <div class="contact-item">
                <el-icon><Star /></el-icon>
                <span>Star us on GitHub ⭐</span>
              </div>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 智能旅行规划. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  House,
  Location,
  Notebook,
  InfoFilled,
  User,
  Setting,
  SwitchButton,
  ArrowDown,
  Right,
  Menu,
  Close,
  Link,
  Star,
  UserFilled
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useTravelAuthStore } from '@/stores/travelAuth'

const router = useRouter()
const route = useRoute()
const authStore = useTravelAuthStore()

const isMenuOpen = ref(false)
const windowWidth = ref(window.innerWidth)

// 导航菜单项
const navItems = [
  { path: '/travel', title: '首页', icon: House },
  { path: '/travel/planner', title: '旅行规划', icon: Location },
  { path: '/travel/guides', title: '我的攻略', icon: Notebook },
  { path: '/travel/intelligence', title: '目的地情报', icon: InfoFilled }
]

// 计算属性
const isMobile = computed(() => windowWidth.value < 768)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userInfo = computed(() => authStore.userInfo)
const userDisplayName = computed(() => authStore.userDisplayName)
const userAvatar = computed(() => authStore.userAvatar)

// 方法
const isActive = (path: string) => {
  // 外部链接不激活
  if (path === '/dashboard') return false
  return route.path === path || route.path.startsWith(path + '/')
}

const goHome = () => {
  router.push('/travel')
}

const goToLogin = () => {
  closeMenu()
  router.push('/travel/login')
}

const goToRegister = () => {
  closeMenu()
  router.push('/travel/register')
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/travel/profile')
      break
    case 'settings':
      router.push('/travel/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    closeMenu()
    ElMessage.success('已退出登录')
    router.push('/travel/login')
  } catch {
    // 用户取消
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (windowWidth.value >= 768) {
    isMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* 导入 DM Sans 字体 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

.travel-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 顶部导航栏 */
.layout-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(14, 165, 233, 0.08);
  box-shadow: 0 2px 20px rgba(14, 165, 233, 0.06);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.25s;
}

.header-logo:hover {
  transform: scale(1.02);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #0EA5E9 0%, #F97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-nav {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  color: #64748B;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.25s;
}

.nav-link:hover {
  background: #F0F9FF;
  color: #0EA5E9;
  transform: translateY(-1px);
}

.nav-link.active {
  background: linear-gradient(135deg, #F0F9FF, #E0F2FE);
  color: #0EA5E9;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
}

.nav-link.external-link {
  color: #64748B;
  opacity: 0.8;
}

.nav-link.external-link:hover {
  background: #FEF3C7;
  color: #F59E0B;
}

.external-icon {
  font-size: 12px;
  margin-left: 4px;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.25s;
  border: 1px solid rgba(14, 165, 233, 0.1);
}

.user-info:hover {
  background: #F0F9FF;
  border-color: rgba(14, 165, 233, 0.2);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.dropdown-icon {
  font-size: 12px;
  color: #9CA3AF;
}

/* 移动端菜单 */
.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 200;
  pointer-events: none;
}

.mobile-menu.open {
  pointer-events: auto;
}

.menu-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s;
}

.mobile-menu.open .menu-overlay {
  opacity: 1;
}

.menu-content {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 280px;
  background: white;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.mobile-menu.open .menu-content {
  transform: translateX(0);
}

.menu-header {
  padding: 20px;
  border-bottom: 1px solid #E5E7EB;
}

.menu-nav {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.menu-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 14px;
  color: #64748B;
  text-decoration: none;
  font-size: 16px;
  margin-bottom: 6px;
  transition: all 0.25s;
  font-weight: 500;
}

.menu-link:hover {
  background: #F0F9FF;
  color: #0EA5E9;
}

.menu-link.active {
  background: linear-gradient(135deg, #F0F9FF, #E0F2FE);
  color: #0EA5E9;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
}

.menu-icon {
  width: 20px;
  height: 20px;
}

.menu-footer {
  padding: 20px;
  border-top: 1px solid #E5E7EB;
}

.menu-user {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.menu-user-info {
  flex: 1;
}

.menu-user-name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.menu-user-email {
  font-size: 12px;
  color: #9CA3AF;
}

.menu-logout {
  width: 100%;
}

.menu-login,
.menu-register {
  width: 100%;
  margin-bottom: 8px;
}

/* 主内容区 */
.layout-main {
  flex: 1;
  min-height: calc(100vh - 64px - 200px);
}

/* 页脚 */
.layout-footer {
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  border-top: 1px solid rgba(14, 165, 233, 0.1);
  padding: 48px 0 24px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 48px;
  margin-bottom: 32px;
}

.footer-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
}

.footer-text {
  font-size: 14px;
  color: #6B7280;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-links a {
  color: #64748B;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.25s;
}

.footer-links a:hover {
  color: #0EA5E9;
}

.footer-contact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6B7280;
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #E5E7EB;
}

.footer-bottom p {
  font-size: 14px;
  color: #9CA3AF;
  margin: 0;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}

/* 响应式 */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: flex;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
</style>
