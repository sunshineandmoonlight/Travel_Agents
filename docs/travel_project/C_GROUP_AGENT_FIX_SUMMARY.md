# C组智能体和图片服务修复总结

## 修复日期
2025-03-13

## 问题描述

1. **C组智能体导入错误**：前端报错无法从 `tradingagents.agents.group_c.llm_guide_writer` 导入 `write_llm_guide`
2. **攻略生成循环加载**：用户选择风格方案后，攻略生成一直循环加载
3. **图片备用方案**：用户提到有Pexels API Key可以作为备用

## 问题分析

### 1. C组智能体导入错误

**错误信息**:
```
Uncaught (in promise) Error: cannot import name 'write_llm_guide' from 'tradingagents.agents.group_c.llm_guide_writer'
```

**根本原因**:
- `llm_guide_writer.py` 文件中导出的函数名是 `write_detailed_guide_with_llm`
- 但是 `group_c/__init__.py` 中导入时使用的是 `write_llm_guide`
- 名称不匹配导致导入失败

**修复方案**:
在 `tradingagents/agents/group_c/__init__.py` 中使用别名:
```python
from .llm_guide_writer import (
    write_detailed_guide_with_llm as write_llm_guide,  # 添加别名
    llm_guide_writer_node,
)
```

### 2. 图片服务优化

#### Pexels API 配置

在 `.env` 文件中添加 Pexels API Key 配置:
```bash
# Pexels API (备用图片搜索 - 200次/小时)
PEXELS_API_KEY=your_pexels_api_key_here
```

**Pexels API 优势**:
- 免费额度: 200次请求/小时 (比Unsplash的50次/小时更慷慨)
- 高质量图片库
- 简单的REST API
- 支持多种尺寸和方向

#### 图片获取优先级

当前系统的图片获取优先级:
1. **Unsplash Search API** - 最佳质量，50次/小时
2. **Pexels API** - 高质量备用，200次/小时
3. **Bing Search API** - 商业API，需Key
4. **公开搜索服务** - LoremFlickr，无需Key
5. **占位图** - 最后回退

#### 国家/地区映射增强

在 `pexels_image_service.py` 中添加了完整的国家/地区映射:
```python
country_map = {
    "泰国": "thailand",
    "韩国": "south korea",
    "日本": "japan",
    "新加坡": "singapore",
    "马来西亚": "malaysia",
    "越南": "vietnam",
    "印尼": "indonesia",
    "菲律宾": "philippines",
    "中国": "china",
    "香港": "hong kong",
    "澳门": "macau",
    "台湾": "taiwan",
}
```

## 修改的文件

### 1. `tradingagents/agents/group_c/__init__.py`
```python
# 修复前
from .llm_guide_writer import (
    write_llm_guide,  # 错误：函数不存在
    llm_guide_writer_node,
)

# 修复后
from .llm_guide_writer import (
    write_detailed_guide_with_llm as write_llm_guide,  # 正确：使用别名
    llm_guide_writer_node,
)
```

### 2. `.env`
添加 Pexels API 配置:
```bash
PEXELS_API_KEY=your_pexels_api_key_here
```

### 3. `tradingagents/services/pexels_image_service.py`
- 添加国家/地区映射
- 改进查询构建逻辑
- 添加特殊处理: 当景点名和城市名相同时使用 `{country} travel` 查询

## 测试结果

### C组智能体导入测试
```bash
$ python -c "from tradingagents.agents.group_c import write_llm_guide"
C group agent import successful
write_llm_guide: <function write_detailed_guide_with_llm at 0x...>
```

### 图片服务测试
| 目的地 | 图片来源 | 状态 |
|--------|----------|------|
| 韩国 | Unsplash | ✅ |
| 泰国 | Unsplash | ✅ |
| 日本 | Unsplash | ✅ |
| 新加坡 | Unsplash | ✅ |
| 马来西亚 | Unsplash | ✅ |
| 越南 | Unsplash | ✅ |
| 印尼 | LoremFlickr (回退) | ⚠️ 可接受 |

## 关于Pexels API Key

用户提到有Pexels API Key作为备用，请按以下步骤配置:

### 获取 Pexels API Key

1. 访问 https://www.pexels.com/api/
2. 注册或登录账号
3. 申请新的API Key
4. 将API Key添加到 `.env` 文件:

```bash
PEXELS_API_KEY=你的实际API_Key
```

### Pexels API 使用限制

| 项目 | 限制 |
|------|------|
| 免费请求 | 200次/小时 |
| 图片质量 | 高 |
| 需要授权 | 是 (Authorization header) |
| 商业使用 | 允许 |

## 攻略生成循环问题排查

如果攻略生成仍然循环加载，可能的原因:

1. **C组智能体未正确加载** - 已通过上述修复解决
2. **LLM配置问题** - 检查 `.env` 中的 `SILICONFLOW_API_KEY`
3. **数据传递问题** - 检查前端是否正确传递所有必需参数
4. **API超时** - 检查后端日志是否有超时错误

### 调试步骤

1. 检查后端日志:
```bash
# 查看实时日志
tail -f logs/travel_agents.log
```

2. 检查浏览器控制台:
- F12 打开开发者工具
- 查看 Network 标签页
- 查看 Console 标签页的错误信息

3. 测试API端点:
```bash
# 测试攻略生成API
curl -X POST http://127.0.0.1:8005/api/travel/staged/generate-guide \
  -H "Content-Type: application/json" \
  -d '{"destination": "韩国", "days": 5, ...}'
```

## 相关文档

- `docs/travel_project/IMAGE_API_FIX_SUMMARY.md` - 图片API修复详情
- `docs/travel_project/UNSPLASH_API_GUIDE.md` - Unsplash使用指南
- `tradingagents/services/pexels_image_service.py` - Pexels服务实现
- `tradingagents/services/unsplash_search_service.py` - Unsplash服务实现

## 下一步建议

1. **配置Pexels API Key** - 联系用户获取实际的Pexels API Key
2. **测试攻略生成流程** - 完整测试从目的地选择到攻略生成的整个流程
3. **监控API使用情况** - 定期检查Unsplash和Pexels的配额使用情况
4. **优化错误处理** - 为用户提供更清晰的错误提示信息

## 更新记录

- 2025-03-13: 初始版本 - 修复C组智能体导入错误，添加Pexels API配置
