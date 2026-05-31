# 验证全景——从 postcondition 到用户满意度

> **Evidence Status** — synthesized. 基于 ORDA-VU 框架的扩展分析和多品类 Agent 的产品实践。

> **本文是"验证与完成"话题的主文件。** 元认知控制中的验证关卡见 [元认知控制](../cognitive-architecture/metacognitive-control.md)，效果验证的数据模型见 [表示与效果](representation-and-effects.md)。

## 核心框架

验证是一个从客观到主观的连续谱：

```text
postcondition（输出满足规格）
  -> effect（行动改变了现实世界的状态）
    -> user satisfaction（用户对结果的主观满意度）
      -> longitudinal alignment（多次交互中趋势是否正确）
```

每一级验证都有适用的 Agent 品类和工程实现方式。选择哪一级取决于任务性质，不是越高级越好。

---

## 1. Postcondition 验证（客观、可自动化）

适用场景：存在明确的、二值的、可自动化检测的完成条件。

| 示例 | 检测方式 |
|---|---|
| 代码是否通过测试 | 运行测试，pass 或 fail |
| CRM 状态是否更新 | read-after-write，值匹配或不匹配 |
| 邮件是否已发送 | 查发件箱，存在或不存在 |
| 文件是否已创建 | 检查文件系统，有或没有 |

知识库的大部分架构设计——Effects Plane、Effect Ledger、read-after-write 策略——都服务于这个层级。对工程型 Agent（Coding Agent、Workflow Agent），这一层通常就够了。

---

## 2. Effect 验证（行动改变了现实）

适用场景：postcondition 满足不等于目标达成，需要确认行动对外部世界产生了预期效果。

| 示例 | postcondition | 真正需要验证的 effect |
|---|---|---|
| 部署新版本 | 部署脚本执行成功 | 新版本在生产环境正常运行 |
| 发送通知 | API 返回 200 | 接收方实际收到并阅读 |
| 修复 bug | 测试通过 | 用户实际遇到的问题已消失 |

工程决策：在 postcondition 层和 effect 层之间需要 read-after-write 或 health check 来弥合差距。

---

## 3. User Satisfaction 验证（主观满意度）

适用场景：结果质量取决于用户的主观判断，无法用自动化检测替代。

三类典型任务：

- **审美与创造性**：Logo 设计、文案撰写、代码注释风格——"好"没有 postcondition 定义
- **情感与陪伴**：用户情绪变化无法 read-after-write，"被理解"是主观体验
- **价值对齐**：人生建议、决策咨询——"正确答案"取决于用户价值观

### 检测方式

| 方式 | 信号 | 可靠性 |
|---|---|---|
| 用户即时反应 | 继续对话 vs 沉默/离开 | 低——可能只是礼貌 |
| 后续行为 | 是否采纳建议、是否使用生成结果 | 中——有行动支撑 |
| 显式反馈 | 用户评分、"这很有帮助" | 中——受表达意愿影响 |
| 多方共识 | 多个评审者独立评分取一致性 | 较高——减少单人偏差 |

### 工程决策指南

对主观性任务，Verify 阶段应支持 `verification_type` 字段：

```yaml
verify:
  verification_type: resonance
  method: user_feedback
  signal: continuation_rate
  threshold: "3-turn conversation continuation > 70%"
```

---

## 4. Longitudinal Alignment 验证（纵向一致性）

适用场景：效果需要多次交互才能观察，单次检查无意义。

| 示例 | 单次检查的局限 | 纵向指标 |
|---|---|---|
| Companion Agent 的陪伴效果 | 单次对话无法衡量 | 用户是否持续回来、对话深度是否增加 |
| Coaching Agent 的成长效果 | 单次建议无法评估 | 用户行为变化趋势、目标达成率 |
| 偏好学习的准确性 | 单次预测可能偶然正确 | 偏好预测准确率的移动平均 |

趋势比单点更重要。用户满意度的移动平均、建议采纳率的变化——这些纵向指标比任何单次检查都更有意义。

---

## 5. 按品类选择验证策略

不同品类的 Agent 应采用不同的默认验证策略：

| 品类 | 主要验证层级 | 辅助验证层级 |
|---|---|---|
| Coding Agent | postcondition | - |
| Workflow Agent | postcondition + effect | - |
| Research Agent | postcondition + 多方共识 | longitudinal |
| Creative Agent | user satisfaction + 多方共识 | longitudinal |
| Companion Agent | user satisfaction + longitudinal | 多方共识 |
| Coaching Agent | longitudinal | user satisfaction |

**选择决策树**：

1. 结果状态可自动检测？ → postcondition
2. 需要确认对外部世界的实际影响？ → effect
3. 质量取决于单个用户的主观感受？ → user satisfaction
4. 效果需要多次交互才能观察？ → longitudinal
5. 没有单一权威判断者？ → 多方共识

这些层级不互斥，可以组合。一个"帮我写周报"的任务可能同时需要：postcondition（格式正确）+ user satisfaction（语气符合风格）+ 多方共识（同事/领导认可）。

---

## 6. 检查清单

```text
当前任务的验证层级是否正确选择？
postcondition 层是否有 read-after-write 确认？
主观性任务是否定义了 user satisfaction 的检测信号？
长期效果任务是否有纵向指标追踪？
验证策略是否与 Agent 品类匹配？
Verify 阶段的 schema 是否支持多种 verification_type？
```

---

## 延伸阅读

- `../evaluation/subjective-eval.md` — 主观性任务的具体评估框架
- `representation-and-effects.md` — 表示、接口与效果
- `../architecture/planes/effects/overview.md` — Effects Plane 架构
- `../categories/` — 各品类 Agent 的验证需求差异
- `../design-space/lessons-learned/single-model-judge.md` — 同源 Judge 的失败案例
