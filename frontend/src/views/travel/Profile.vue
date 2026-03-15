<template>
  <div class="profile-page">
    <div class="profile-container">
      <el-empty description="个人中心页面开发中...">
        <el-button type="primary" @click="$router.push('/travel/planner')">返回旅行规划</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 个人中心页面 - 开发中
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
