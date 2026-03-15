import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.2,
  easing: 'ease',
  speed: 500
})

// 路由配置 - 只保留旅行系统
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/travel'
  },
  // 旅行系统路由
  {
    path: '/travel',
    component: () => import('@/layouts/TravelLayout.vue'),
    meta: {
      title: '智能旅行',
      requiresAuth: false
    },
    children: [
      {
        path: '',
        name: 'TravelHome',
        component: () => import('@/views/travel/Home.vue'),
        meta: {
          title: '智能旅行 - 发现世界的每一处精彩',
          requiresAuth: false
        }
      },
      {
        path: 'planner',
        name: 'TravelPlanner',
        component: () => import('@/views/travel/Planner.vue'),
        meta: {
          title: 'AI旅行规划 - 分阶段智能规划您的旅程',
          requiresAuth: false
        }
      },
      {
        path: 'intelligence',
        name: 'TravelIntelligence',
        component: () => import('@/views/travel/Intelligence.vue'),
        meta: {
          title: '目的地情报',
          requiresAuth: false
        }
      },
      {
        path: 'guides',
        name: 'TravelGuides',
        component: () => import('@/views/travel/Guides.vue'),
        meta: {
          title: '我的攻略',
          requiresAuth: true
        }
      },
      {
        path: 'guides/:id',
        name: 'TravelGuideDetail',
        component: () => import('@/views/travel/GuideDetail.vue'),
        meta: {
          title: '攻略详情',
          requiresAuth: true
        }
      },
      {
        path: 'guides/:id/edit',
        name: 'TravelGuideEdit',
        component: () => import('@/views/travel/GuideEdit.vue'),
        meta: {
          title: '编辑攻略',
          requiresAuth: true
        }
      },
      {
        path: 'login',
        name: 'TravelLogin',
        component: () => import('@/views/travel/Login.vue'),
        meta: {
          title: '登录',
          requiresAuth: false
        }
      },
      {
        path: 'register',
        name: 'TravelRegister',
        component: () => import('@/views/travel/Register.vue'),
        meta: {
          title: '注册',
          requiresAuth: false
        }
      },
      {
        path: 'guide-center',
        name: 'GuideCenter',
        component: () => import('@/views/travel/GuideCenter.vue'),
        meta: {
          title: '攻略中心 - 攻略、技巧与指南',
          requiresAuth: false
        }
      },
      {
        path: 'profile',
        name: 'TravelProfile',
        component: () => import('@/views/travel/Profile.vue'),
        meta: {
          title: '个人中心',
          requiresAuth: true
        }
      },
      {
        path: 'settings',
        name: 'TravelSettings',
        component: () => import('@/views/travel/Settings.vue'),
        meta: {
          title: '设置',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/travel'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫 - 只处理旅行系统认证
router.beforeEach(async (to, from, next) => {
  NProgress.start()

  // 设置页面标题
  const title = to.meta.title as string
  if (title) {
    document.title = title
  }

  // 旅行系统认证检查
  try {
    const { useTravelAuthStore } = await import('@/stores/travelAuth')
    const travelAuthStore = useTravelAuthStore()

    // 需要认证但未登录
    if (to.meta.requiresAuth && !travelAuthStore.isAuthenticated) {
      travelAuthStore.setRedirectPath(to.fullPath)
      next('/travel/login')
      return
    }

    // 已登录且访问登录/注册页，重定向到首页
    if (travelAuthStore.isAuthenticated && (to.name === 'TravelLogin' || to.name === 'TravelRegister')) {
      next('/travel')
      return
    }
  } catch (error) {
    // Pinia未初始化，跳过认证检查
    console.warn('Pinia not initialized, skipping auth check')
  }

  next()
})

// 全局后置守卫
router.afterEach((to, from) => {
  NProgress.done()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  NProgress.done()
  ElMessage.error('页面加载失败，请重试')
})

export default router
