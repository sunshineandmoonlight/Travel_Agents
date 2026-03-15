<template>
  <div class="settings-page">
    <div class="settings-container">
      <el-empty description="设置页面开发中...">
        <el-button type="primary" @click="$router.push('/travel/planner')">返回旅行规划</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 设置页面 - 开发中
</script>

<style scoped>
.settings-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
