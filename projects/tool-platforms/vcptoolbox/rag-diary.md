# VCPToolBox RAG 日记系统

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 四种日记调用模式

### 1. `{{...日记本}}` - 直接引入
```
触发: 正则 /\{\{(.*?)日记本(.*?)\}\}/g
行为: 直接注入 RAG 检索结果
修饰符: ::Time (时间感知), ::Group (语义组), :1.5 (K值倍率)
```

### 2. `[[...日记本]]` - AIMemo 记忆链
```
触发: 正则 /\[\[(.*?)日记本(.*?)\]\]/g
特性: 结果以"记忆块"组织，支持标签追踪
聚合: [[日记本1|日记本2|日记本3:1.5]]
```

### 3. `<<...日记本>>` - 全文检索
```
触发: 正则 /<<(.*?)日记本(.*?)>>/g
特性: 跨日记本搜索，双阈值机制
阈值: avgThreshold (聚合), truncateThreshold (截断)
```

### 4. `《《...日记本》》` - 混合聚合
```
触发: 正则 /《《(.*?)日记本(.*?)》》/g
特性: 语义组 + 时间感知的高级检索
最复杂模式，整合所有增强策略
```

## 时间感知检索 (::Time)

```javascript
// 时间表达式解析
TimeExpressionParser.parse(userContent)

支持:
  - 硬编码: "今天"、"昨天"、"本周"、"上月末"
  - 动态: "X天前"、"X周前"、"上周三"

// 时间权重
w_time = decay(距离当前天数)
  当天: 1.0
  1-7天: 0.8 ~ 1.0
  8-30天: 0.5 ~ 0.8
  30天+: ≤ 0.5

// 最终分数
final_score = similarity × w_time
```

## 语义组增强 (::Group)

```javascript
// 组定义
{
  "物理学": {
    "words": ["力学", "热学", "光学"],
    "weight": 1.2,
    "vector_id": "uuid"
  }
}

// 激活流程
1. 词元匹配: userContent 中匹配组词
2. 激活强度: matched_words / total_words
3. 向量混合: enhanced = weighted_avg([Q_orig, V_group1, ...])
4. 预计算: 组向量一次性 embed，存储复用
```

## 动态 K 值计算

### 基础 K
```javascript
if (userLen > 100) k_base = 6      // 长查询
else if (userLen > 30) k_base = 4  // 中等
else k_base = 3                    // 短查询
```

### 三维动态调整 (V3)

```javascript
// 逻辑深度 L: 向量能量集中度
L = (topK能量占比 - 随机占比) / (1 - 随机占比)
L ≈ 1 → K *= 0.8 (足量)
L ≈ 0 → K *= 1.3 (多检索)

// 共振指数 R: 与历史的相似度
R = max(聚合历史向量.similarity(当前向量))
高R (0.7+) → K *= 0.9 (相同话题)
低R (<0.3) → K *= 1.5 (新话题)

// 语义宽度 S: 归一化熵
S = entropy(向量分布) / log(维度)
S ≈ 1 → K *= 1.2 (宽泛)
S ≈ 0 → K *= 0.9 (精准)

// 综合公式
β = σ(L · log(1 + R) - S · noise_penalty)
最终K = max(1, round(k_base × β × kMultiplier))
```

## 上下文向量衰减

```javascript
// 历史向量指数衰减
const decayRate = 0.75
const maxContextWindow = 10

for (i, vector) of historyVectors:
  age = messages_count - i
  weight = decayRate^age

// 示例: 10条消息
weights = [0.056, 0.075, ..., 0.75]

// 聚合
aggregated = weighted_average(vectors, weights)
aggregated = normalize(aggregated)
```

## 上下文分段

```javascript
segmentContext(messages, threshold = 0.70) {
  // 相邻消息相似度 ≥ 阈值 → 同一段
  // 相似度 < 阈值 → 新段

  return [{
    vector: 段平均向量,
    text: 段内容,
    range: [start, end],
    count: 消息数
  }]
}
```

## 检索缓存

```javascript
// 缓存键
cacheKey = hash(模式 + dbName + modifiers + queryVector_hash)

// 去重补偿
contextDiaryPrefixes = new Set()  // 已返回的日记
dedupBuffer = contextDiaryPrefixes.size
kForSearch = finalK + dedupBuffer
```

## 完整 RAG 流程

```
用户消息
    ↓
1. 提取 Query Vector (清理 + embedding)
    ↓
2. 计算动态参数 (L, R, S → K)
    ↓
3. 解析时间表达式 (::Time)
    ↓
4. 语义组激活 (::Group → 向量混合)
    ↓
5. 识别日记调用模式 ({{}} [[]] <<>> 《《》》)
    ↓
6. 执行检索 (并行，finalK 条)
    ↓
7. 结果聚合 (去重 + Rerank)
    ↓
8. 缓存和存储
    ↓
最终 System Message
```

## 设计启示

1. **多模式适配**: 四种语法覆盖不同场景需求
2. **自适应 K 值**: 根据查询特征动态调整，避免过多或过少
3. **时间感知**: 支持自然语言时间表达，增强时序查询
4. **语义组**: 预定义主题词，增强领域检索
5. **衰减聚合**: 近期上下文权重更高，远期逐渐淡化
