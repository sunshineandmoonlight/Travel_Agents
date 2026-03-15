<template>
  <div class="scope-selector">
    <div class="container">
      <!-- Hero Content -->
      <div class="hero-section">
        <div class="hero-badge">
          <el-icon><Compass /></el-icon>
          <span>AI 智能旅行规划</span>
        </div>
        <h1 class="hero-title">开始规划您的<br><em>完美旅程</em></h1>
        <p class="hero-subtitle">选择您的旅行范围，AI将为您量身定制专属行程</p>
      </div>

      <!-- Scope Cards -->
      <div class="cards-container">
        <div
          class="scope-card"
          :class="{ selected: selectedScope === 'domestic' }"
          @click="handleSelect('domestic')"
        >
          <div class="card-background domestic"></div>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><LocationFilled /></el-icon>
            </div>
            <h2 class="card-title">国内游</h2>
            <p class="card-desc">探索大好河山，发现中华之美</p>
            <div class="card-features">
              <span class="feature-tag">
                <el-icon><Place /></el-icon>
                历史文化
              </span>
              <span class="feature-tag">
                <el-icon><Picture /></el-icon>
                自然风光
              </span>
              <span class="feature-tag">
                <el-icon><Food /></el-icon>
                地道美食
              </span>
            </div>
            <div class="card-check" v-if="selectedScope === 'domestic'">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>

        <div
          class="scope-card"
          :class="{ selected: selectedScope === 'international' }"
          @click="handleSelect('international')"
        >
          <div class="card-background international"></div>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Position /></el-icon>
            </div>
            <h2 class="card-title">出境游</h2>
            <p class="card-desc">环游世界，体验异域风情</p>
            <div class="card-features">
              <span class="feature-tag">
                <el-icon><Place /></el-icon>
                异域文化
              </span>
              <span class="feature-tag">
                <el-icon><Camera /></el-icon>
                打卡胜地
              </span>
              <span class="feature-tag">
                <el-icon><ShoppingBag /></el-icon>
                购物体验
              </span>
            </div>
            <div class="card-check" v-if="selectedScope === 'international'">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="info-section">
        <div class="info-card">
          <el-icon class="info-icon"><MagicStick /></el-icon>
          <div class="info-text">
            <h4>AI 智能规划</h4>
            <p>12个专业智能体协同工作</p>
          </div>
        </div>
        <div class="info-card">
          <el-icon class="info-icon"><Document /></el-icon>
          <div class="info-text">
            <h4>5阶段渐进式</h4>
            <p>每个环节都可自由选择</p>
          </div>
        </div>
        <div class="info-card">
          <el-icon class="info-icon"><Star /></el-icon>
          <div class="info-text">
            <h4>个性化定制</h4>
            <p>根据您的喜好量身打造</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Compass,
  LocationFilled,
  Position,
  Place,
  Picture,
  Food,
  ShoppingBag,
  Camera,
  MagicStick,
  Document,
  Star,
  Check
} from '@element-plus/icons-vue'

const emit = defineEmits<{
  select: [scope: 'domestic' | 'international']
}>()

const selectedScope = ref<'domestic' | 'international' | null>(null)

const handleSelect = (scope: 'domestic' | 'international') => {
  selectedScope.value = scope
  // Small delay for visual feedback before emitting
  setTimeout(() => {
    emit('select', scope)
  }, 200)
}
</script>

<style scoped>
/* ==================== */
/* Design System Variables  */
/* ==================== */
.scope-selector {
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

  min-height: calc(100vh - 180px);
  padding: 2rem 1rem;
}

/* ==================== */
/* Hero Section          */
/* ==================== */
.hero-section {
  text-align: center;
  margin-bottom: 3rem;
  animation: fadeInUp 0.6s ease-out;
}

.hero-badge {
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
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-title {
  font-family: 'Bodoni Moda', serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-white);
  margin-bottom: 1rem;
}

.hero-title em {
  font-style: italic;
  background: linear-gradient(135deg, #FDE68A 0%, #F97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.85);
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ==================== */
/* Scope Cards            */
/* ==================== */
.cards-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  max-width: 800px;
  margin: 0 auto 3rem;
}

@media (min-width: 768px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }
}

.scope-card {
  position: relative;
  height: 320px;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-lg);
}

.scope-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl), var(--shadow-soft);
}

.scope-card.selected {
  transform: scale(1.02);
  box-shadow: var(--shadow-xl), 0 0 0 4px var(--color-primary);
}

.card-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.card-background.domestic {
  background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 50%, #8B5CF6 100%);
}

.card-background.international {
  background: linear-gradient(135deg, #F97316 0%, #EF4444 50%, #EC4899 100%);
}

.card-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--color-white);
  text-align: center;
}

.card-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.card-title {
  font-family: 'Bodoni Moda', serif;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.card-desc {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 1.5rem;
  max-width: 280px;
  line-height: 1.5;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-check {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  background: var(--color-success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  animation: scaleIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
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
/* Info Section           */
/* ==================== */
.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--color-white);
  transition: all 0.3s ease;
}

.info-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.info-icon {
  font-size: 2rem;
  opacity: 0.9;
}

.info-text h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.info-text p {
  font-size: 0.75rem;
  opacity: 0.75;
  margin: 0;
}

/* ==================== */
/* Animations             */
/* ==================== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== */
/* Responsive             */
/* ==================== */
@media (max-width: 480px) {
  .scope-card {
    height: 280px;
  }

  .card-icon {
    font-size: 3rem;
  }

  .card-title {
    font-size: 1.5rem;
  }

  .info-card {
    padding: 0.875rem 1rem;
  }

  .info-icon {
    font-size: 1.5rem;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .scope-card,
  .info-card,
  .card-icon,
  .card-check {
    animation: none;
    transition: none;
  }

  .scope-card:hover,
  .info-card:hover {
    transform: none;
  }
}
</style>
