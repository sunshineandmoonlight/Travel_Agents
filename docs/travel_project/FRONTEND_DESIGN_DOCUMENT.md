# 旅行系统前端设计文档

## 1. 设计理念

### 1.1 核心设计原则
- **简约至上**: 去除冗余元素，聚焦核心功能
- **情感连接**: 通过视觉设计激发用户的旅行向往
- **智能交互**: 预测用户需求，提供流畅体验
- **可信可靠**: 专业的设计语言建立用户信任

### 1.2 设计语言
- **现代简约**: 扁平化设计 + 微阴影 + 圆角
- **高端精致**: 精致的间距、排版和色彩搭配
- **动态流畅**: 优雅的过渡动画和交互反馈

## 2. 视觉系统

### 2.1 配色方案

#### 主色调 (Primary Colors)
```
品牌主色 - 深海蓝
- Primary-50:  #E3F2FD
- Primary-100: #BBDEFB
- Primary-200: #90CAF9
- Primary-300: #64B5F6
- Primary-400: #42A5F5
- Primary-500: #2196F3  // 主色
- Primary-600: #1E88E5
- Primary-700: #1976D2
- Primary-800: #1565C0
- Primary-900: #0D47A1
```

#### 辅助色调 (Secondary Colors)
```
夕阳橙 - 温暖、活力
- Secondary-50:  #FFF3E0
- Secondary-100: #FFE0B2
- Secondary-200: #FFCC80
- Secondary-300: #FFB74D
- Secondary-400: #FFA726
- Secondary-500: #FF9800  // 辅助色
- Secondary-600: #FB8C00
- Secondary-700: #F57C00
- Secondary-800: #EF6C00
- Secondary-900: #E65100

森野绿 - 安全、自然
- Success-50:   #E8F5E9
- Success-100:  #C8E6C9
- Success-200:  #A5D6A7
- Success-300:  #81C784
- Success-400:  #66BB6A
- Success-500:  #4CAF50  // 成功色
- Success-600:  #43A047
- Success-700:  #388E3C
- Success-800:  #2E7D32
- Success-900:  #1B5E20
```

#### 功能色调 (Functional Colors)
```
警告色 - 琥珀黄
- Warning-500:  #FFC107
- Warning-600:  #FFB300

危险色 - 珊瑚红
- Danger-50:   #FFEBEE
- Danger-100:  #FFCDD2
- Danger-200:  #EF9A9A
- Danger-300:  #E57373
- Danger-400:  #EF5350
- Danger-500:  #F44336  // 危险色
- Danger-600:  #E53935
- Danger-700:  #D32F2F
- Danger-800:  #C62828
- Danger-900:  #B71C1C

信息色 - 天空蓝
- Info-500:    #00BCD4
- Info-600:    #00ACC1
```

#### 中性色调 (Neutral Colors)
```
灰色系
- Gray-50:   #FAFAFA   // 背景色
- Gray-100:  #F5F5F5   // 次级背景
- Gray-200:  #EEEEEE   // 边框
- Gray-300:  #E0E0E0   // 分割线
- Gray-400:  #BDBDBD   // 禁用边框
- Gray-500:  #9E9E9E   // 禁用文本
- Gray-600:  #757575   // 次级文本
- Gray-700:  #616161   // 正文
- Gray-800:  #424242   // 标题
- Gray-900:  #212121   // 主标题
```

### 2.2 字体系统

#### 字体族
```css
/* 中文 */
--font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI",
                    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                    "Helvetica Neue", Helvetica, Arial, sans-serif;

/* 英文/数字 */
--font-family-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
                     Consolas, "Courier New", monospace;
```

#### 字体规范
```
特大标题   48px / 600 / Line-height: 1.2  / Letter-spacing: -0.02em
大标题     36px / 600 / Line-height: 1.2  / Letter-spacing: -0.01em
标题       24px / 600 / Line-height: 1.3  / Letter-spacing: 0
副标题     20px / 500 / Line-height: 1.4  / Letter-spacing: 0
正文大     16px / 400 / Line-height: 1.5  / Letter-spacing: 0
正文       14px / 400 / Line-height: 1.6  / Letter-spacing: 0
辅助文本   12px / 400 / Line-height: 1.5  / Letter-spacing: 0.02em
标签       10px / 500 / Line-height: 1.4  / Letter-spacing: 0.05em
```

### 2.3 间距系统

#### 基础间距单位
```css
--spacing-xs:  4px;    /* 极小间距 */
--spacing-sm:  8px;    /* 小间距 */
--spacing-md:  16px;   /* 中等间距 */
--spacing-lg:  24px;   /* 大间距 */
--spacing-xl:  32px;   /* 超大间距 */
--spacing-2xl: 48px;   /* 特大间距 */
--spacing-3xl: 64px;   /* 巨大间距 */
```

#### 组件内边距
```css
/* 按钮 */
--padding-btn-sm:  8px 16px;
--padding-btn-md:  12px 24px;
--padding-btn-lg:  16px 32px;

/* 输入框 */
--padding-input:   12px 16px;

/* 卡片 */
--padding-card:    24px;
```

### 2.4 圆角系统

```css
--radius-xs:  4px;    /* 小元素 */
--radius-sm:  8px;    /* 按钮、输入框 */
--radius-md:  12px;   /* 卡片 */
--radius-lg:  16px;   /* 大卡片 */
--radius-xl:  24px;   /* 模态框 */
--radius-full: 9999px; /* 圆形 */
```

### 2.5 阴影系统

```css
--shadow-xs:  0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-sm:  0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
--shadow-md:  0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
--shadow-lg:  0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
--shadow-xl:  0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.15);

/* 内阴影 */
--shadow-inner: inset 0 2px 4px rgba(0, 0, 0, 0.06);
```

### 2.6 动画系统

#### 缓动函数
```css
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

#### 动画时长
```css
--duration-fast:   150ms;
--duration-normal: 250ms;
--duration-slow:   350ms;
--duration-slower: 500ms;
```

## 3. 布局系统

### 3.1 响应式断点

```css
/* 移动设备优先 */
--breakpoint-xs:  375px;   /* 小手机 */
--breakpoint-sm:  640px;   /* 手机横屏 */
--breakpoint-md:  768px;   /* 平板竖屏 */
--breakpoint-lg:  1024px;  /* 平板横屏 */
--breakpoint-xl:  1280px;  /* 笔记本 */
--breakpoint-2xl: 1536px;  /* 桌面显示器 */
```

### 3.2 容器宽度

```css
--container-sm:  640px;
--container-md:  768px;
--container-lg:  1024px;
--container-xl:  1280px;
--container-2xl: 1536px;
```

### 3.3 网格系统

12列网格系统，支持灵活的布局组合。

```
┌─────────────────────────────────────────────┐
│  1    2    3    4    5    6    7    8    9  │
│  │    │    │    │    │    │    │    │    │  │
│  10   11   12                               │
│  │    │    │                                │
└─────────────────────────────────────────────┘
```

## 4. 组件设计

### 4.1 按钮 (Button)

#### 主要按钮 (Primary Button)
```css
/* 默认状态 */
background: var(--primary-500);
color: white;
padding: 12px 24px;
border-radius: var(--radius-sm);
font-weight: 500;
font-size: 14px;
transition: all var(--duration-normal) var(--ease-out-quart);

/* 悬停状态 */
background: var(--primary-600);
transform: translateY(-1px);
box-shadow: var(--shadow-md);

/* 点击状态 */
background: var(--primary-700);
transform: translateY(0);
```

#### 次要按钮 (Secondary Button)
```css
background: transparent;
color: var(--primary-500);
border: 1px solid var(--primary-300);
/* 悬停时背景变为 Primary-50 */
```

#### 文本按钮 (Text Button)
```css
background: transparent;
color: var(--primary-500);
padding: 8px 16px;
/* 悬停时背景变为 Primary-50 */
```

#### 按钮尺寸
```
Large:  高度 48px, 内边距 16px 32px
Medium: 高度 40px, 内边距 12px 24px
Small:  高度 32px, 内边径 8px 16px
```

### 4.2 输入框 (Input)

```css
.input-field {
  padding: 12px 16px;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
  font-size: 14px;
  transition: all var(--duration-normal);

  /* 聚焦状态 */
  &:focus {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
    outline: none;
  }

  /* 错误状态 */
  &.error {
    border-color: var(--danger-500);
  }
}

.input-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 4px;
  display: block;
}
```

### 4.3 卡片 (Card)

```css
.card {
  background: white;
  border-radius: var(--radius-md);
  padding: var(--padding-card);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-normal) var(--ease-out-quart);

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
}

.card-header {
  border-bottom: 1px solid var(--gray-100);
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
}

.card-body {
  /* 内容区域 */
}

.card-footer {
  border-top: 1px solid var(--gray-100);
  padding-top: 16px;
  margin-top: 16px;
}
```

### 4.4 标签 (Tag/Chip)

```css
.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  gap: 4px;
}

/* 标签变体 */
.tag-primary { background: var(--primary-50); color: var(--primary-700); }
.tag-success { background: var(--success-50); color: var(--success-700); }
.tag-warning { background: var(--warning-50); color: var(--warning-700); }
.tag-danger  { background: var(--danger-50); color: var(--danger-700); }
.tag-neutral { background: var(--gray-100); color: var(--gray-700); }
```

### 4.5 风险等级指示器

```css
/* 5级风险等级显示 */
.risk-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.risk-level-1 { color: var(--success-500); } /* 低风险 */
.risk-level-2 { color: var(--success-600); }
.risk-level-3 { color: var(--warning-500); } /* 中等风险 */
.risk-level-4 { color: var(--danger-400); }
.risk-level-5 { color: var(--danger-500); } /* 高风险 */

.risk-bar {
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--gray-200);
  overflow: hidden;

  .risk-fill {
    height: 100%;
    border-radius: var(--radius-full);
    transition: width var(--duration-slow) var(--ease-out-quart);
  }
}
```

### 4.6 进度指示器

```css
/* 步骤进度条 */
.progress-steps {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--gray-200);
  color: var(--gray-500);
  font-size: 14px;
  font-weight: 500;
}

.step.active {
  background: var(--primary-500);
  color: white;
}

.step.completed {
  background: var(--success-500);
  color: white;
}

.step-connector {
  flex: 1;
  height: 2px;
  background: var(--gray-200);
}

/* 线性进度条 */
.progress-linear {
  height: 4px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;

  .progress-fill {
    height: 100%;
    background: var(--primary-500);
    transition: width var(--duration-normal) var(--ease-out-quart);
  }
}
```

### 4.7 模态框 (Modal)

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  animation: fadeIn var(--duration-normal);
}

.modal-content {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  animation: slideUp var(--duration-normal) var(--ease-out-quart);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, -45%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}
```

### 4.8 加载状态

```css
/* 脉冲加载 */
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 骨架屏 */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### 4.9 提示消息 (Toast)

```css
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 320px;
  animation: slideInRight var(--duration-normal) var(--ease-out-quart);
}

.toast-success { border-left: 4px solid var(--success-500); }
.toast-error   { border-left: 4px solid var(--danger-500); }
.toast-warning { border-left: 4px solid var(--warning-500); }
.toast-info    { border-left: 4px solid var(--info-500); }

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

## 5. 页面设计

### 5.1 登录/注册页面

#### 布局结构
```
┌─────────────────────────────────────────────────────┐
│  ┌─────────────────┐           ┌─────────────────┐  │
│  │                 │           │                 │  │
│  │                 │           │   登录表单      │  │
│  │   品牌插图      │    ───▶   │                 │  │
│  │   (可选)        │           │   [邮箱输入]    │  │
│  │                 │           │   [密码输入]    │  │
│  │                 │           │   [登录按钮]    │  │
│  │                 │           │                 │  │
│  └─────────────────┘           └─────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 设计要点
- 居中布局，左右分栏（桌面端）
- 左侧：品牌视觉元素/插图
- 右侧：登录表单
- 移动端：上下堆叠

#### 表单字段
```
邮箱/手机号
  [输入框]

密码
  [输入框] [显示/隐藏]
  忘记密码？

[登录按钮]

还没有账号？[立即注册]
```

### 5.2 主布局 (Main Layout)

#### 导航栏
```css
.navbar {
  height: 64px;
  background: white;
  border-bottom: 1px solid var(--gray-100);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-600);
}

.navbar-nav {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.nav-link {
  padding: 8px 16px;
  color: var(--gray-600);
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);

  &:hover, &.active {
    background: var(--primary-50);
    color: var(--primary-600);
  }
}
```

#### 侧边栏 (移动端)
```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 280px;
  background: white;
  border-right: 1px solid var(--gray-100);
  transform: translateX(-100%);
  transition: transform var(--duration-normal);
  z-index: 200;
}

.sidebar.open {
  transform: translateX(0);
}
```

### 5.3 旅行规划页面

#### 页面布局
```
┌─────────────────────────────────────────────────────┐
│  标题: 智能旅行规划                    [保存草稿]  │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  第一步: 选择目的地                            │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  📍 目的地                              │  │  │
│  │  │  [输入框: 请输入目的地名称]              │  │  │
│  │  │  推荐: 杭州 北京 成都 三亚 厦门          │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  📅 出行日期                            │  │  │
│  │  │  [开始日期] → [结束日期] (共 X 天)       │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  👥 人数 & 💰 预算                      │  │  │
│  │  │  成人 [1] 儿童 [0]                      │  │  │
│  │  │  预算: ○ 经济型 ○ 舒适型 ● 高端型       │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  🎨 兴趣偏好                            │  │  │
│  │  │  ☑ 风景 ☑ 美食 ☐ 历史 ☐ 购物           │  │  │
│  │  │  ☐ 文化 ☐ 夜生活 ☐ 亲子 ☐ 冒险         │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│              [开始规划]                              │
└─────────────────────────────────────────────────────┘

规划中状态:
┌─────────────────────────────────────────────────────┐
│  正在为您规划杭州之旅...                             │
│  ●●●●●○○○○○ 50%                                    │
│  ✓ 正在分析目的地情报                               │
│  ○ 正在推荐热门景点                                 │
│  ○ 正在规划行程路线                                 │
└─────────────────────────────────────────────────────┘
```

#### 目的地情报卡片
```css
.intelligence-card {
  background: linear-gradient(135deg, var(--primary-50), white);
  border: 1px solid var(--primary-100);
  border-radius: var(--radius-md);
  padding: 24px;
}

.intelligence-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: var(--success-50);
  color: var(--success-700);
  font-size: 12px;
  font-weight: 500;
}
```

### 5.4 目的地情报页面

#### 页面结构
```
┌─────────────────────────────────────────────────────┐
│  [← 返回]  目的地情报                        [分享]  │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  ┌─ 目的地 ─────────────────────────────────────┐   │
│  │  杭州                                        │   │
│  │  浙江省省会，以西湖美景闻名                 │   │
│  │                                              │   │
│  │  风险等级:  ████░ 1/5 低风险                │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ 新闻资讯 ────────────────────────────────────┐  │
│  │  [2024-03-10] 杭州推出新一轮旅游优惠政策      │  │
│  │  来源: 新华文旅 | 情感: 积极                 │  │
│  │  ────────────────────────────────────────    │  │
│  │  [2024-03-08] 杭州西湖龙井茶文化节开幕       │  │
│  │  来源: 新浪旅游 | 情感: 积极                 │  │
│  │  ────────────────────────────────────────    │  │
│  │  [查看更多 →]                                │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 风险评估 ────────────────────────────────────┐  │
│  │  政治:  ✓ 安全                               │  │
│  │  安全:  ✓ 安全                               │  │
│  │  健康:  ⚠ 注意天气变化                       │  │
│  │  自然:  ✓ 无极端天气预警                     │  │
│  │  社会:  ✓ 治安良好                           │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 近期活动 ────────────────────────────────────┐  │
│  │  🎊 西湖龙井茶文化节  3月15日-4月15日        │  │
│  │  🎭 清明文化体验活动  4月2日-4月8日          │  │
│  │  🎉 中国国际动漫节     4月28日-5月3日        │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 文化推荐 ────────────────────────────────────┐  │
│  │  🏛️ 博物馆: 浙江省博物馆、中国丝绸博物馆     │  │
│  │  🎭 表演: 印象西湖实景演出                   │  │
│  │  🍜 美食: 西湖醋鱼、龙井虾仁、东坡肉         │  │
│  │  🎁 特产: 龙井茶、西湖绸伞                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 智能建议 ────────────────────────────────────┐  │
│  │  1. ✅ 目的地安全，可以放心前往               │  │
│  │  2. 🎉 近期有龙井茶文化节，推荐参加           │  │
│  │  3. 🌸 春季赏花好时节，建议提前预订酒店       │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 5.5 攻略管理页面

#### 攻略列表
```
┌─────────────────────────────────────────────────────┐
│  我的攻略                        [+ 新建攻略]       │
│  ─────────────────────────────────────────────────  │
│  筛选: [全部 ▼] [排序: 最新创建 ▼]                 │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  [缩略图]  杭州三日游                       │   │
│  │           2024-03-10 | 3天2夜 | 舒适型     │   │
│  │                                            │   │
│  │  标签: #风景 #美食 #文化                   │   │
│  │                                            │   │
│  │  [查看详情] [导出] [分享] [删除]            │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  [缩略图]  北京五日深度游                   │   │
│  │           2024-02-15 | 5天4夜 | 高端型     │   │
│  │                                            │   │
│  │  标签: #历史 #文化 #博物馆                 │   │
│  │                                            │   │
│  │  [查看详情] [导出] [分享] [删除]            │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### 攻略详情
```
┌─────────────────────────────────────────────────────┐
│  [← 返回]  杭州三日游               [编辑] [导出]  │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  ┌─ 行程概览 ────────────────────────────────────┐  │
│  │  目的地: 杭州 | 天数: 3天 | 预算: 舒适型      │  │
│  │  出行日期: 2024-04-15 ~ 2024-04-17            │  │
│  │  旅行者: 2成人 | 兴趣: 风景、美食             │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 每日行程 ────────────────────────────────────┐  │
│  │  Day 1 - 4月15日 (周一)                       │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  上午: 西湖十景游览                     │  │  │
│  │  │    · 断桥残雪 → 平湖秋月 → 苏堤春晓     │  │  │
│  │  │                                         │  │  │
│  │  │  午餐: 楼外楼 (推荐: 西湖醋鱼)          │  │  │
│  │  │                                         │  │  │
│  │  │  下午: 雷峰塔 → 净慈寺 → 花港观鱼       │  │  │
│  │  │                                         │  │  │
│  │  │  晚上: 印象西湖实景演出                 │  │  │
│  │  │  晚餐: 知味观 (推荐: 龙井虾仁)          │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  Day 2 - 4月16日 (周二)                       │  │
│  │  ...                                          │  │
│  │                                               │  │
│  │  Day 3 - 4月17日 (周三)                       │  │
│  │  ...                                          │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ 目的地情报 ──────────────────────────────────┐  │
│  │  风险等级: 1/5 低风险                         │  │
│  │  近期活动: 龙井茶文化节进行中                 │  │
│  │  天气预报: 多云转晴，15-22℃                  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 6. 响应式设计

### 6.1 移动端适配

#### 断点适配策略
```
xs (375px): 单列布局, 底部导航
sm (640px): 单列布局, 汉堡菜单
md (768px): 两列布局开始
lg (1024px): 标准桌面布局
xl (1280px): 大屏优化布局
```

#### 秕动端特殊处理
- 触摸友好的交互元素（最小 44x44px）
- 底部导航栏（拇指操作友好）
- 滑动手势支持
- 虚拟键盘适配

### 6.2 暗色模式

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* 背景色 */
    --bg-primary:   #121212;
    --bg-secondary: #1E1E1E;
    --bg-tertiary:  #2C2C2C;

    /* 文本色 */
    --text-primary:   #FFFFFF;
    --text-secondary: #B0B0B0;
    --text-tertiary:  #707070;

    /* 边框色 */
    --border-color: #3C3C3C;
  }
}
```

## 7. 图标系统

### 7.1 图标库选择
- **推荐**: Heroicons / Phosphor Icons
- **风格**: 线性图标 + 实心图标
- **尺寸**: 16px, 20px, 24px, 32px

### 7.2 常用图标映射
```
导航类:
- 首页: home
- 规划: map
- 攻略: book-open
- 情报: information
- 我的: user

功能类:
- 搜索: search / magnifying-glass
- 添加: plus
- 编辑: pencil
- 删除: trash
- 分享: share
- 导出: download
- 收藏: heart / bookmark

状态类:
- 成功: check-circle
- 错误: x-circle
- 警告: exclamation-triangle
- 信息: information-circle

旅行类:
- 目的地: map-pin
- 日期: calendar
- 人数: users
- 预算: currency-yen
- 天气: cloud-sun
- 风险: shield
```

## 8. 动画效果

### 8.1 页面过渡
```css
/* 淡入淡出 */
.fade-enter-active, .fade-leave-active {
  transition: opacity var(--duration-normal);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 滑动 */
.slide-enter-active, .slide-leave-active {
  transition: transform var(--duration-normal) var(--ease-out-quart);
}
.slide-enter-from {
  transform: translateX(100%);
}
.slide-leave-to {
  transform: translateX(-100%);
}
```

### 8.2 列表动画
```css
.list-enter-active {
  transition: all var(--duration-normal) var(--ease-out-quart);
}
.list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
```

## 9. 可访问性

### 9.1 键盘导航
- Tab 键顺序符合视觉顺序
- Enter/Space 触发按钮
- Escape 关闭模态框
- 方向键导航列表

### 9.2 屏幕阅读器
- ARIA 标签完整
- 语义化 HTML
- 焦点指示器清晰

### 9.3 对比度
- 正文文本对比度 ≥ 4.5:1
- 大文本对比度 ≥ 3:1
- 交互元素对比度 ≥ 3:1

## 10. 性能优化

### 10.1 加载优化
- 代码分割 (路由级别)
- 懒加载图片
- 预加载关键资源
- CDN 加速静态资源

### 10.2 渲染优化
- 虚拟滚动 (长列表)
- 防抖/节流 (搜索、滚动)
- 骨架屏占位
- 图片懒加载

## 11. 浏览器兼容

### 11.1 支持范围
- Chrome: 最新 2 个大版本
- Firefox: 最新 2 个大版本
- Safari: 最新 2 个大版本
- Edge: 最新 2 个大版本
- 移动端: iOS 14+, Android 10+

## 12. 实现技术栈

### 12.1 核心框架
```json
{
  "framework": "Vue 3.4+",
  "language": "TypeScript 5.3+",
  "bundler": "Vite 5.0+",
  "router": "Vue Router 4.2+",
  "state": "Pinia 2.1+",
  "ui": "Element Plus 2.5+",
  "http": "Axios 1.6+",
  "utils": [
    "dayjs - 日期处理",
    "lodash-es - 工具函数",
    "clsx - 类名合并",
    "uuid - 唯一ID生成"
  ]
}
```

### 12.2 目录结构
```
src/
├── assets/           # 静态资源
│   ├── images/      # 图片
│   ├── icons/       # 图标
│   └── styles/      # 全局样式
├── components/       # 公共组件
│   ├── common/      # 通用组件
│   ├── form/        # 表单组件
│   └── layout/      # 布局组件
├── composables/      # 组合式函数
├── views/           # 页面组件
│   ├── auth/        # 认证页面
│   ├── travel/      # 旅行页面
│   └── user/        # 用户页面
├── router/          # 路由配置
├── stores/          # 状态管理
├── api/             # API 接口
├── types/           # TypeScript 类型
├── utils/           # 工具函数
└── App.vue          # 根组件
```

---

*本文档由 Claude AI 设计，遵循现代前端设计最佳实践*
*最后更新: 2026-03-10*
