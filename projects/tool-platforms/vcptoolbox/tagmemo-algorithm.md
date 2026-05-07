# TagMemo 浪潮算法 V8.1

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 核心哲学

> 向量空间中语义密度不均匀。标签向量在高密度区域形成聚集点，查询向量根据与标签的余弦相似度进行加权调整。

## 四阶段工作流

```
┌─────────────────────────────────────────────┐
│ 阶段一：感应 (Sensing)                       │
│ • 净化处理：去除 HTML、JSON、Emoji、工具标记 │
│ • EPA 投影：计算逻辑深度与跨域共振           │
├─────────────────────────────────────────────┤
│ 阶段二：分解 (Decomposition)                 │
│ • 残差金字塔：Gram-Schmidt 正交化投影        │
│ • 能量截断：剩余能量 < 10% 时停止            │
├─────────────────────────────────────────────┤
│ 阶段三：扩张 (Expansion)                     │
│ • LIF 脉冲扩散：神经元激发网络               │
│ • 虫洞路由：跨域长尾知识喷射                 │
│ • 核心标签补全：强行捞取缺失锚点             │
├─────────────────────────────────────────────┤
│ 阶段四：重塑 (Reshaping)                     │
│ • 动态参数计算：Beta & K 值实时调整          │
│ • 语义去重：SVD 主题建模                     │
│ • 测地线重排：地形贴地距离 (V8)              │
└─────────────────────────────────────────────┘
```

## 核心模块

### EPA 模块 (Embedding Projection Analysis)
```javascript
// 逻辑深度 = 1 - 归一化熵
logicDepth = 1 - entropy / log2(K)

// 跨域共振 = 多轴同时激活的能量
coActivation = sqrt(E1 × E2)
resonance = sum(bridges.strength)

// 世界观门控：识别当前语义维度
queryWorld = dominantAxes[0].label  // "技术"/"情感"/"社会"
```

### 残差金字塔 (Residual Pyramid)
```javascript
// Gram-Schmidt 正交化
for level in 0..maxLevels:
  topTags = searchTagIndex(residualVector, k)

  // 构建正交基
  for tag in topTags:
    v = tag.vector
    for basis in orthoBasis:
      v = v - dot(v, basis) * basis
    orthoBasis.append(normalize(v))

  // 计算残差
  projection = sum(dot(query, basis) * basis)
  residual = query - projection

  // 能量截断
  if ||residual||² / ||original||² < 0.1:
    break
```

### LIF 脉冲扩散 (V6+)
```javascript
// 基于共现矩阵的神经元激发
activeSpikes = new Map()  // id → { energy, momentum }
accumulatedEnergy = new Map()

for hop in 0..MAX_HOPS:
  for [nodeId, spike] of activeSpikes:
    if spike.energy < FIRING_THRESHOLD: continue

    for [neighborId, coocWeight] of matrix.get(nodeId):
      // 张力检测：高残差边触发虫洞
      tension = coocWeight × neighborResidual
      isWormhole = tension >= TENSION_THRESHOLD

      // 衰减策略
      decay = isWormhole ? 0.70 : 0.25
      injectedCurrent = spike.energy × coocWeight × (1 - decay)

      accumulatedEnergy[neighborId] += injectedCurrent

// 涌现节点：未在初始种子中但被激活
emergentNodes = accumulatedEnergy
  .filter(id => !originalSeeds.has(id))
  .sort((a, b) => b.energy - a.energy)
  .slice(0, 50)
```

### 测地线重排 (V8)
```javascript
// 复用脉冲扩散的距离场
lastEnergyField = accumulatedEnergy  // 缓存

geodesicRerank(candidates, options) {
  for chunk of candidates:
    // 查询 chunk 关联的 Tags 在距离场中的能量
    tags = getChunkTags(chunk.id)
    hitEnergies = tags.map(t => lastEnergyField.get(t.id) || 0)

    geoScore = sum(hitEnergies) / hitCount

  // 混合分数
  finalScore = (1 - α) × knnScore + α × normalize(geoScore)

  return candidates.sort(by: finalScore)
}
```

## 动态参数公式

```javascript
// 动态增强因子
dynamicBoostFactor = (logicDepth × (1 + log(1 + resonance)))
                   / (1 + entropyPenalty × 0.5)
                   × activationMultiplier

// 核心标签加权 (1.20 ~ 1.40)
coreMetric = logicDepth × 0.5 + (1 - coverage) × 0.5
dynamicCoreBoost = coreRange[0] + coreMetric × (coreRange[1] - coreRange[0])

// 最终融合
alpha = min(1.0, effectiveTagBoost)
fused = (1 - alpha) × originalVector + alpha × contextVector
```

## 版本演进

| 版本 | 关键创新 |
|------|---------|
| V3.7 | 残差金字塔 + EPA + 动态 Beta |
| V4 | SVD 智能去重 + 偏振语义舵 |
| V6 | LIF 脉冲扩散 + 语言门控 |
| V7 | 有向序位势能 + 虫洞路由 |
| V8 | 测地线重排 + 距离场复用 |

## 设计启示

1. **物理隐喻指导实现**: 能量、引力、脉冲 → 清晰的算法直觉
2. **多层级防御**: 每层都有退化策略，最坏情况 = 不改动原结果
3. **零额外计算优化**: 复用已有计算结果（如距离场）
4. **热参数调控**: 99% 参数可外部配置，支持 A/B 测试
