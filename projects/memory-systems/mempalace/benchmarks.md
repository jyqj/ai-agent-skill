# Benchmarks 方法论


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **从 96.6% 到 100% 的渐进优化路径**

## 数据集

| 数据集 | 规模 | 评估焦点 |
|-------|------|---------|
| **LongMemEval** | 500 问 | 长上下文检索（~53 会话/问） |
| **LoCoMo** | 1,986 QA | 多跳推理、跨会话连接 |
| **ConvoMem** | 75,000+ QA | 6 类对话记忆 |

## 评估指标

| 指标 | 含义 |
|-----|------|
| **Recall@K** | Top-K 结果中至少包含 1 个正确答案的比例 |
| **NDCG@K** | 折扣累积增益 / 理想折扣累积增益（考虑排序位置） |

## 三种检索模式

### Raw Mode（96.6%）

- 纯语义检索，无后处理
- 会话文本 → ChromaDB 嵌入 → 余弦相似度排序
- **最高零 API 分数**

### AAAK Mode（84.2%）

- 会话摘要压缩 + 语义检索
- **不推荐**：压缩丢信息，下降 12.4 点

### Hybrid Mode（渐进优化）

| 版本 | R@5 | 增量改进 |
|-----|-----|---------|
| Hybrid v1 | 97.8% | + 关键词重排 |
| Hybrid temporal variant | 98.4% | + 时间增强 |
| Hybrid v3 + rerank | 99.4% | + 偏好模式提取 + Haiku |
| **Hybrid v4 + rerank** | **100%** | + 引文/人名/记忆模式 |

---

## Hybrid 优化详解

### v1: 关键词重排

```python
fused_dist = dist × (1.0 - 0.30 × keyword_overlap)
```

- 从问题提取 3+ 字符非停用词关键词
- 计算关键词在会话中的覆盖率
- 词汇匹配高的会话距离减少最多 30%

### 时间增强变体

- 解析问题中的时间引用（"N 周前"、"上月"）
- 计算会话时间与目标时间的接近度
- 时间窗口内的会话最多距离减少 40%

### v3: 偏好模式提取

- 16 个正则检测隐含偏好（"通常更喜欢"、"一直在苦恼"）
- 为每个会话生成合成文档
- 同时存储原始会话，通过 corpus_id 映射

### v4: 精准修复

1. **引文短语提取**：单引号内精确短语 → 60% 距离减少
2. **人名增强**：大写专有名词 → 40% 距离减少
3. **记忆/怀旧模式**："我还记得"、"高中时" → 合成偏好文档

---

## LLM Rerank

**可选的最后一层排序（仅需 API key）**

```
① Hybrid 检索 → top-10 会话
② 构造最小化提示
③ 发送到 Haiku → 选择最相关会话
④ 将最优会话提升至排名 1
```

| 模型 | 成本/查询 | R@5 |
|-----|---------|-----|
| 无 rerank | $0 | 98.4% |
| +Haiku | ~$0.001 | **100%** |
| +Sonnet | ~$0.003 | **100%** |

---

## 按问题类型细分（v4 + Haiku）

| 类型 | R@5 | R@10 |
|-----|-----|------|
| Knowledge-update | 100% | 100% |
| Multi-session | 100% | 100% |
| Single-session-user | 100% | 100% |
| Temporal-reasoning | 99.2% | 99.2% |
| Single-session-assistant | 98.2% | 100% |
| Single-session-preference | 96.7% | 100% |

---

## 对标发表系统

| 排名 | 系统 | R@5 | LLM 要求 |
|-----|-----|-----|---------|
| 1 | **MemPal Hybrid v4 + rerank** | **100%** | Optional |
| 2 | Supermemory ASMR | ~99% | Yes |
| 3 | MemPal Hybrid v3 + rerank | 99.4% | Optional |
| 4 | Mastra | 94.87% | GPT |
| **⭐** | **MemPal Raw (无 LLM)** | **96.6%** | **无** |
| 6 | Hindsight | 91.4% | Gemini |
| 7 | Mem0 | ~85% | Yes |

---

## 复现命令

```bash
# Raw 模式（96.6%, 离线）
python benchmarks/longmemeval_bench.py data.json

# Hybrid v3（98.4%, 离线）
python benchmarks/longmemeval_bench.py data.json --mode hybrid_v3

# Hybrid v4 + Rerank（100%, 需 API）
export ANTHROPIC_API_KEY=sk-ant-...
python benchmarks/longmemeval_bench.py data.json --mode hybrid_v4 --llm-rerank
```

---

## 关键设计决策

| 决策 | 理由 |
|-----|------|
| **30% 关键词权重** | 足够翻转模糊文档，不压倒更好的语义匹配 |
| **Top-50 检索 → 重排** | 更大候选池给关键词重排更多素材 |
| **无 LLM（raw/hybrid）** | 保持离线承诺 |
| **40% 时间上限** | 强但非决定性 |
| **偏好合成文档** | 保留原始会话 + 添加桥接文档，不丢信息 |

---

## 已知限制

| 问题 | 现状 | 前景 |
|-----|------|------|
| 偏好类别最弱 | 86-96.7% | 可扩展模式库 |
| LoCoMo 多跳 | baseline 60.3% | Sonnet rerank → 100% |
| AAAK 损失信息 | 84.2% < 96.6% | 实验中，不推荐 |
