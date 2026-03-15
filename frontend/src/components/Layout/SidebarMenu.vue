<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="appStore.sidebarCollapsed"
    :unique-opened="true"
    router
    class="sidebar-menu"
  >
    <!-- 智能旅行系统 -->
    <el-menu-item index="/travel">
      <el-icon><Location /></el-icon>
      <template #title>智能旅行</template>
    </el-menu-item>

    <el-menu-item index="/travel/planner">
      <el-icon><MagicStick /></el-icon>
      <template #title>
        <span style="color: var(--el-color-primary);">旅行规划</span>
      </template>
    </el-menu-item>

    <el-menu-item index="/travel/intelligence">
      <el-icon><TrendCharts /></el-icon>
      <template #title>
        <span style="color: var(--el-color-primary);">目的地情报</span>
      </template>
    </el-menu-item>

    <el-menu-item index="/travel/guides">
      <el-icon><Tickets /></el-icon>
      <template #title>
        <span style="color: var(--el-color-primary);">我的攻略</span>
      </template>
    </el-menu-item>

    <!-- 分隔线 -->
    <el-menu-item disabled>
      <template #title>
        <div style="height: 1px; background: var(--el-border-color); margin: 8px 0;"></div>
      </template>
    </el-menu-item>

    <!-- 设置 -->
    <el-sub-menu index="/settings">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>设置</span>
      </template>

      <el-menu-item index="/settings">通用设置</el-menu-item>
      <el-menu-item index="/settings?tab=appearance">外观设置</el-menu-item>
      <el-menu-item index="/settings/config">配置管理</el-menu-item>
      <el-menu-item index="/settings/cache">缓存管理</el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/about">
      <el-icon><InfoFilled /></el-icon>
      <template #title>关于</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  Location,
  MagicStick,
  Setting,
  InfoFilled,
  Tickets,
  TrendCharts
} from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()

const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
.sidebar-menu {
  border: none;
  height: 100%;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;
  }

  :deep(.el-menu-item.is-active) {
    background-color: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }
}
</style>
