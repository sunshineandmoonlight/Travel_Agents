<!--
  详细攻略显示组件
  显示完整的旅行攻略，包括每日行程、景点详情、餐厅推荐等
-->
<template>
  <div class="detailed-guide">
    <!-- 占位符内容 - 测试是否能编译 -->
    <div class="test-section">
      <h1>{{ guide?.destination || '旅行攻略' }}</h1>
      <p>共 {{ guide?.total_days || 0 }} 天</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  guide: any
}>()

const emit = defineEmits<{
  restart: []
}>()

onMounted(() => {
  console.log('DetailedGuide mounted with guide:', props.guide)
})
</script>

<style scoped>
.detailed-guide {
  padding: 2rem 0;
}

.test-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
}
</style>
