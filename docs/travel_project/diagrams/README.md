# Draw.io 图表使用说明

本目录包含旅行规划系统的架构图表，使用 draw.io 格式保存。

## 📊 包含的图表

### 1. 系统架构图 (`01_system_architecture.drawio`)

展示了系统的整体架构，包括：

- **前端层**: Vue 3 用户界面
- **API层**: FastAPI 服务接口
- **业务逻辑层**: 多智能体协作系统
  - Group A: 分析层智能体
  - Group B: 设计层智能体
  - Group C: 生成层智能体
- **数据层**: MongoDB、Redis、外部API

### 2. 智能体协作流程图 (`02_agent_flow.drawio`)

展示了智能体之间的协作关系：

- **用户输入** → 需求分析 → 目的地匹配
- **并行处理**: 景点推荐 + 目的地情报
- **数据汇聚**: 行程规划 + 预算分析
- **最终输出**: LLM 攻略生成

### 3. 数据流设计图 (`03_data_flow.drawio`)

展示了数据在系统中的流动：

- 用户需求数据的采集与处理
- 各智能体之间的数据传递
- 外部API的数据获取
- 最终攻略的生成与导出

## 🎨 如何使用这些图表

### 方法1: 在线编辑 (推荐)

1. 访问 [app.diagrams.net](https://app.diagrams.net)
2. 点击 **File** → **Open from** → **Device**
3. 选择 `.drawio` 文件上传
4. 编辑图表后可以：
   - 导出为 PNG/SVG/PDF
   - 分享链接
   - 继续编辑

### 方法2: 桌面客户端

1. 下载 draw.io 桌面版
   - Windows: [draw.io-xx.x.x.exe](https://github.com/jgraph/drawio-desktop/releases)
   - macOS: [draw.io-xx.x.x.dmg](https://github.com/jgraph/drawio-desktop/releases)
2. 安装并打开应用
3. 打开 `.drawio` 文件
4. 编辑和导出

### 方法3: VS Code 插件

1. 在 VS Code 中安装 **Draw.io Integration** 插件
2. 打开 `.drawio` 文件
3. 可以直接在 VS Code 中编辑

### 方法4: 嵌入到 Markdown

如果使用支持 draw.io 的 Markdown 编辑器（如某些文档系统）：

```markdown
```drawio
<mxfile host="app.diagrams.net" ...>
  <!-- 直接粘贴 drawio XML 内容 -->
</mxfile>
```
```

## 📝 图表元素说明

### 颜色编码

| 颜色 | 含义 |
|------|------|
| 🟢 绿色 | 用户界面 / 输入输出 |
| 🟠 橙色 | Group A 分析层智能体 |
| 🔵 蓝色 | Group C 生成层智能体 |
| 🟡 黄色 | API 接口层 |
| 🟣 紫色 | 业务逻辑协调层 |
| ⚪ 灰色 | 数据存储 / 外部服务 |

### 线条样式

| 样式 | 含义 |
|------|------|
| ______ 实线 | 主要数据流 |
| ----- 虚线 | 辅助数据流 / 依赖关系 |

## 🔄 更新图表

当系统架构或流程发生变化时，请按以下步骤更新图表：

1. 打开对应的 `.drawio` 文件
2. 修改需要更新的部分
3. 保存文件
4. 导出新的 PNG/SVG (如果需要在文档中使用)
5. 更新相关文档引用

## 📦 导出格式

推荐导出格式：

- **PNG**: 用于 Word 文档、PPT
- **SVG**: 用于 Web 页面（可缩放）
- **PDF**: 用于打印或正式文档
- **Draw.io**: 用于后续编辑

## 🤝 贡献指南

如果您需要修改或新增图表：

1. 保持图表风格的一致性
2. 使用相同的颜色编码
3. 确保文字清晰可读
4. 添加适当的注释和说明
5. 提交 PR 时包含 `.drawio` 源文件

## 📧 联系方式

如有疑问，请：
- 提交 GitHub Issue
- 发送邮件至: hsliup@163.com
- 加入 QQ 群: 782124367
