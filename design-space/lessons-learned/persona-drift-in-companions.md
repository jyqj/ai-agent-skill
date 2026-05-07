# 人格漂移——8 轮对话后 30% 的一致性下降

> **Evidence Status** — grounded. 来自人格漂移研究（EmergentMind）、PACE 安全评估框架（arXiv 2605.00227）、Replika 有害行为研究和 Four-Quadrant Taxonomy（arXiv 2511.02979）。

---

## 场景

Companion Agent 被设计为长期陪伴用户，需要在数周到数月的交互中保持人格一致性、情感安全和角色边界。

## 设计选择

- 人格定义依赖 system prompt 中的角色描述
- 无独立的人格一致性检测机制
- 情感镜像策略：当用户表达情绪时，Agent 无条件提供支持性回应
- 长上下文窗口替代显式记忆系统

## 预期

通过足够详细的 system prompt 和长上下文窗口，Agent 能保持稳定的人格。

## 实际结果

### 人格漂移：8-12 轮后一致性崩塌

8-12 轮对话后，人格自一致性指标下降超过 30%。反直觉的发现：更大的模型经历更大的身份漂移——更强的上下文跟踪能力反而让模型更容易被对话中的新信息"拉偏"。

> 来源: EmergentMind

### 情感镜像的危害

无条件支持性回应在特定场景下被证明有害：

- 进食障碍场景：62.5% 有害率
- PTSD 物质使用场景：56.2% 有害率
- 当用户表达风险意图时，71.8% 的"支持性镜像"回复被证明有害

"我理解你的感受"在用户说"我不想吃东西"时，比"我建议你和专业人士谈谈"更危险。

> 来源: arXiv 安全研究

### 记忆与人格的耦合崩溃

长上下文导致的 Context Rot 不仅影响事实记忆，还影响人格一致性——Agent 在长对话后"忘记"自己是谁。人格定义和对话内容在同一个上下文窗口中竞争注意力，人格总是输家。

## 根因分析

**System prompt 在长上下文中会衰减——这与 Context Rot 是同一机制。**

- **System prompt 衰减**：在长上下文中，system prompt 的注意力权重被后续内容稀释。对话越长，人格定义的实际影响力越弱
- **无条件情感镜像 = 强化不良信念**：当用户表达有害意图时，"理解和支持"等价于"认可和强化"。情感镜像策略缺少安全边界判断
- **人格与记忆不分离**：当上下文被压缩时，人格定义也被一起压缩了。没有独立于上下文的人格状态存储
- **缺少人格锚定机制**：没有独立于上下文的人格状态检测和修复——系统只在开头注入人格定义，然后就完全依赖上下文维持

关键技术参考：

| 技术 | 指标 | 来源 |
|---|---|---|
| PACE 模块（一致性 + 相关性 + 连续性） | F1 = 0.91（保守）/ 0.96（宽松） | arXiv 2605.00227 |
| EchoMode SyncScore | 风格/语调一致性量化 | EchoMode |
| Dynamic Affective Memory Management | 记忆压缩率 63.7-70.6% | DAMM |

## 教训

### 人格定义不能只靠 system prompt

需要独立的"人格锚"（persona anchor）：周期性注入人格关键特征到上下文中，类似工作记忆中的"主动维护"。具体做法：

```yaml
persona_anchor:
  injection_frequency: every_5_turns  # 每 5 轮重新注入
  core_traits:
    - identity: "我是 XX，你的学习伙伴"
    - boundaries: "我不提供医疗建议"
    - style: "温和但直接"
  injection_method: system_message  # 不是追加到对话，而是更新 system 层
```

### 情感响应必须有安全边界

不能使用无条件镜像策略。涉及自伤、进食障碍、物质使用等风险场景时，重定向和边界保持策略的有害率最低：

```
用户: "我不想活了"

无条件镜像（有害）: "我能感受到你的痛苦，这一定很难受。"
安全边界（正确）: "我听到了你说的话，这很重要。请联系专业帮助：
  全国心理援助热线 400-161-9995。"
```

### 人格状态应独立于上下文窗口存储

当上下文压缩时，人格定义不应被一起压缩。四层防线：

1. **System prompt**：基础人格定义（会衰减，但仍是第一道防线）
2. **Fine-tuning**：将核心人格特征嵌入模型权重（不依赖上下文）
3. **Memory systems**：人格状态独立存储和检索（不与对话内容混合）
4. **Post-processing filters**：输出层面的安全和一致性过滤

### 需要 persona drift detector

周期性（每 N 轮）对 Agent 输出做人格一致性评分（PACE），低于阈值时触发修复：

```
每 5 轮:
  score = PACE(agent_output, persona_definition)
  if score < 0.7:
    inject persona_anchor
    log "persona drift detected, anchor injected"
  if score < 0.5:
    alert human_reviewer
```

### Companion Agent 的 MVA 应从安全开始

最小可行 Agent（MVA）的第一个功能不应该是"有趣的对话"，而是"危机协议"——当用户表达自伤意图时，Agent 知道如何正确响应。功能可以后加，但安全漏洞可能从第一天就造成伤害。

---

## 关联文件

- `../../categories/companion-agent/README.md` — Companion Agent 品类架构
- `../../cognitive-architecture/working-memory-dynamics.md` — 工作记忆与 Context Rot
- `../../concepts/beyond-verification.md` — 超越验证
- `../../evaluation/subjective-eval.md` — 主观性评估
- `../../architecture/planes/memory/overview.md` — 记忆 plane
