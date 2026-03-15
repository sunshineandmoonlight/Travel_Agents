<!--
简洁的详细攻略显示组件

直接显示智能体生成的原始内容，可点击查看详细文本
-->
<template>
  <div class="simple-detailed-guide" v-if="guide">
    <!-- 头部信息 -->
    <div class="guide-header">
      <h1>{{ guide.destination }} 攻略</h1>
      <div class="header-info">
        <span>共 {{ guide.total_days }} 天</span>
        <span>预算 ¥{{ guide.budget_breakdown?.total_budget || guide.total_budget }}</span>
      </div>
    </div>

    <!-- 每日行程 - 简洁显示 -->
    <div v-for="day in guide.daily_itineraries" :key="day.day" class="day-section">
      <div class="day-title">
        第{{ day.day }}天：{{ day.title || day.theme }}
      </div>
      <div class="day-info">
        {{ day.date }} | {{ day.pace }} | 约 ¥{{ day.daily_budget || day.estimated_cost }}
      </div>

      <!-- 每个时间段 - 直接显示文本 -->
      <div v-for="(item, idx) in day.schedule" :key="idx" class="schedule-item">
        <div class="time-section">
          <div class="time">{{ item.time_range }}</div>
          <div class="period">{{ getPeriodName(item.period) }}</div>
        </div>

        <!-- 活动内容 - 可展开查看详情 -->
        <div class="activity-content">
          <div class="activity-name">{{ item.activity }}</div>
          <div class="location">{{ item.location || item.attraction }}</div>

          <!-- 智能体生成的内容（可展开） -->
          <div
            v-if="item.agent_content || item.description || item.recommendations"
            class="agent-output"
          >
            <div class="agent-output-header" @click="toggleAgentOutput(item)">
              <span>智能体生成内容</span>
              <el-icon class="toggle-icon" :class="{ expanded: item.expanded }">
                <ArrowDown />
              </el-icon>
            </div>

            <div v-show="item.expanded" class="agent-output-content">
              <!-- 景点详情智能体输出 -->
              <div v-if="item.description" class="agent-section">
                <div class="agent-label">景点详情智能体：</div>
                <div class="agent-text">{{ item.description }}</div>

                <div v-if="item.highlights?.length" class="agent-subsection">
                  <div class="subsection-label">必看亮点：</div>
                  <ul>
                    <li v-for="(h, i) in item.highlights" :key="i">{{ h }}</li>
                  </ul>
                </div>

                <div v-if="item.suggested_route" class="agent-subsection">
                  <div class="subsection-label">推荐路线：</div>
                  <div class="agent-text">{{ item.suggested_route }}</div>
                </div>

                <div v-if="item.tickets" class="agent-subsection">
                  <div class="subsection-label">门票信息：</div>
                  <div class="agent-text">
                    ¥{{ item.tickets.price }}
                    <span v-if="item.tickets.notes">（{{ item.tickets.notes }}）</span>
                  </div>
                </div>

                <div v-if="item.tips?.length" class="agent-subsection">
                  <div class="subsection-label">游览贴士：</div>
                  <ul>
                    <li v-for="(t, i) in item.tips" :key="i">{{ t }}</li>
                  </ul>
                </div>
              </div>

              <!-- 餐厅推荐智能体输出 -->
              <div v-if="item.recommendations" class="agent-section">
                <div class="agent-label">餐厅推荐智能体：</div>
                <div class="agent-text">
                  <strong>{{ item.recommendations.restaurant || item.recommendations.name }}</strong>
                </div>
                <div v-if="item.recommendations.address" class="agent-text">
                  地址：{{ item.recommendations.address }}
                </div>

                <div v-if="item.recommendations.signature_dishes?.length" class="agent-subsection">
                  <div class="subsection-label">招牌菜：</div>
                  <ul>
                    <li v-for="(dish, i) in item.recommendations.signature_dishes" :key="i">
                      {{ dish.name }} - ¥{{ dish.price }}
                      <span v-if="dish.description">（{{ dish.description }}）</span>
                    </li>
                  </ul>
                </div>

                <div v-if="item.recommendations.average_cost" class="agent-text">
                  人均消费：约 ¥{{ item.recommendations.average_cost }}
                </div>

                <div v-if="item.recommendations.tips" class="agent-text">
                  小贴士：{{ item.recommendations.tips }}
                </div>
              </div>

              <!-- 交通规划智能体输出 -->
              <div v-if="item.transport" class="agent-section">
                <div class="agent-label">交通规划智能体：</div>
                <div class="agent-text">
                  方式：{{ item.transport.method || item.transport.recommended_method }}
                </div>
                <div v-if="item.transport.duration" class="agent-text">
                  时长：{{ item.transport.duration }}
                </div>
                <div v-if="item.transport.cost" class="agent-text">
                  费用：约 ¥{{ item.transport.cost }}
                </div>
                <div v-if="item.transport.tips" class="agent-text">
                  小贴士：{{ item.transport.tips }}
                </div>
              </div>
            </div>
          </div>

          <!-- 图片 -->
          <div v-if="item.imageUrl" class="activity-image">
            <img :src="item.imageUrl" :alt="item.activity" @error="handleImageError(item, $event)" />
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="$emit('restart')">重新规划</el-button>
      <el-button @click="handleExport">导出PDF</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

const props = defineProps<{
  guide: any
}>()

const emit = defineEmits<{
  restart: []
}>()

const getPeriodName = (period: string) => {
  const names: Record<string, string> = {
    morning: '上午',
    lunch: '午餐',
    afternoon: '下午',
    dinner: '晚餐',
    evening: '晚上'
  }
  return names[period] || period
}

const toggleAgentOutput = (item: any) => {
  item.expanded = !item.expanded
}

const handleImageError = (item: any, event: Event) => {
  console.warn('图片加载失败:', item.activity)
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

const handleExport = () => {
  // TODO: 实现导出功能
  console.log('导出PDF')
}
</script>

<style scoped>
.simple-detailed-guide {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  min-height: 100vh;
}

.guide-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.guide-header h1 {
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  color: #333;
}

.header-info {
  display: flex;
  justify-content: center;
  gap: 2rem;
  color: #666;
}

.day-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.day-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.day-info {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.schedule-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 0.8rem;
}

.time-section {
  flex-shrink: 0;
  width: 100px;
  text-align: center;
}

.time {
  font-size: 1.1rem;
  font-weight: bold;
  color: #0EA5E9;
}

.period {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.25rem;
}

.activity-content {
  flex: 1;
}

.activity-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.location {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.agent-output {
  margin-top: 0.8rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.agent-output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  background: #f0f9ff;
  cursor: pointer;
  user-select: none;
  font-size: 0.9rem;
  color: #0369A1;
}

.agent-output-header:hover {
  background: #e0f2fe;
}

.toggle-icon {
  transition: transform 0.3s;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.agent-output-content {
  padding: 1rem;
  background: #fafafa;
}

.agent-section {
  margin-bottom: 1rem;
}

.agent-section:last-child {
  margin-bottom: 0;
}

.agent-label {
  font-weight: 600;
  color: #0EA5E9;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.agent-text {
  color: #444;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.agent-subsection {
  margin-top: 0.8rem;
  padding-left: 1rem;
}

.subsection-label {
  font-weight: 500;
  color: #555;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
}

.agent-subsection ul {
  margin: 0;
  padding-left: 1.2rem;
  list-style-type: disc;
}

.agent-subsection li {
  color: #444;
  line-height: 1.6;
  margin-bottom: 0.2rem;
}

.activity-image {
  margin-top: 0.8rem;
}

.activity-image img {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: contain;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.3s;
}

.activity-image img:hover {
  transform: scale(1.02);
}

.actions {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
