# 法律 AI 幻觉：1,348 起案件、$145K+ 制裁

> **Evidence Status** — grounded. 来自 Damien Charlotin 全球 AI 幻觉案件数据库（持续更新至 2026-04）、ComplianceHub 2026 法律 AI 清算报告、Sullivan & Cromwell 紧急道歉事件。
> https://www.damiencharlotin.com/hallucinations/
> https://compliancehub.wiki/legal-ai-hallucination-reckoning-2026/
> https://abovethelaw.com/2026/04/sullivan-cromwell-files-emergency-please-dont-sanction-us-for-all-these-ai-hallucinations-letter/

---

## 研究背景

截至 2026-04-24，全球已记录 **1,348 起**法律 AI 幻觉案件（915 起来自美国法院），涉及 AI 生成的虚假案例引用、伪造判例法和不存在的法规条文。增长速率从 2025 年初的约 2 起/周加速到 2025 年末的 2-3 起/天。

这不是个别律师的使用不当——商业法律 AI 平台（如 Thomson Reuters CoCounsel）同样产生幻觉。问题的根因在于 LLM 的概率生成机制与法律领域对引用精确性的刚性要求之间的根本矛盾。

### 重大制裁案例

| 案件 | 法院 | 后果 | 金额 |
|------|------|------|------|
| Oregon 葡萄园案 | 俄勒冈联邦地区法院 | 记录最高罚款 | $110,000 |
| Greg Lake 案 | 内布拉斯加最高法院 | 美国历史首次因 AI 幻觉无限期停牌 | N/A（执业资格） |
| Sullivan & Cromwell | 联邦法院 | 紧急公开道歉，28 条错误引用 | 声誉损失 |
| 第六巡回上诉案 | 联邦上诉法院 | 罚款 + 案件驳回 | $30,000 |
| 南俄亥俄案 | 联邦地区法院 | 罚款 + 藐视法庭 + 纪律转介 | $7,500+ |

**累计已知制裁金额超过 $145,000**，另有多起涉及执业资格处分的案件。

---

## 故障链

```text
1. 律师/律所使用 AI 工具（ChatGPT、CoCounsel 等）生成法律研究报告
   │
2. AI 以高置信度语气输出包含虚假案例引用的内容
   │  （LLM 的概率生成机制产生"统计上合理但事实上不存在"的引用）
   │
3. 律师未独立验证 AI 输出的每条引用
   │  （信任偏差：AI 的"权威"语气降低了人工核查意愿）
   │
4. 虚假引用被纳入正式法律文件提交给法院
   │
5. 对方律师或法官发现引用不存在
   │
6. 法院发起制裁程序
   │
7. 部分律师试图掩盖 AI 使用事实——触发额外的独立违规指控
   │  （掩盖行为比原始错误更严重）
```

### 关键恶化因素

- **置信度-准确度倒挂**：AI 对虚假引用的表达与真实引用同样自信，甚至更详细（包含虚构的页码、段落编号）
- **掩盖比错误更致命**：多个案件中，律师试图隐瞒 AI 使用事实，导致额外的欺诈/藐视法庭指控
- **商业工具同样中招**：Thomson Reuters CoCounsel 等专业法律 AI 也产生幻觉，说明这不是"免费工具才有的问题"

---

## 根因分析

**核心根因：LLM 的概率生成机制无法保证引用级精确性，而法律领域对引用的容错率为零。**

### 技术层面

- LLM 生成的是"统计上最可能的下一个 token"，不是"经过验证的事实"
- 法律引用的格式高度规范化（案件名 + 卷号 + 页码），LLM 擅长模仿这种格式，但不保证内容对应真实案例
- 幻觉在法律引用上特别隐蔽：格式完全正确，看起来高度可信，但引用的案件根本不存在

### 使用层面

- **原则 MC-01 违反**：Agent 未显式表达不确定性——AI 以确定性语气输出未经验证的引用
- **原则 MC-03 违反**：不知道自己不知道什么——AI 无法区分"确定知道的引用"和"概率生成的引用"
- **原则 IS-01 违反**：操作的是表示，不是现实——AI 的"法律知识"是训练数据的压缩表示，不是对法律数据库的实时查询

### 制度层面

- 法律职业的核心义务之一是"引用核实"（duty of candor），AI 未改变这一义务
- 多个州已开始要求律师在法律文件中披露 AI 使用情况
- 法院对"AI 生成"的容忍度正在快速下降

---

## 架构缺陷

| 缺失的 Plane / Pattern | 对应知识库位置 | 说明 |
|------------------------|---------------|------|
| Citation Verification Gate | Effects Plane | AI 输出的引用未经独立验证即被视为事实 |
| Confidence Calibration | Representation Plane | AI 对虚假引用与真实引用的置信度无差异 |
| Uncertainty Expression | Interaction Plane | AI 未标注"此引用需要人工验证" |
| Domain-Specific Grounding | World State Plane | AI 的"法律知识"来自训练数据压缩，非实时数据库查询 |
| Human Verification Mandate | Control Plane | 高风险输出无强制人工验证门控 |
| Output Provenance Tracking | Explainability Plane | 无法追溯每条引用的生成依据 |

---

## 设计教训

1. **AI 无法验证 AI 的输出——在高风险领域，人工核实是强制性的，不是可选的。** 法律引用的容错率为零。任何将 AI 输出直接纳入正式文件的工作流都是架构缺陷。

2. **置信度表达必须区分"确定知道"和"概率生成"。** 当前 LLM 的统一确定性语气是危险的默认设置。法律 AI 的每条引用都应附带可机器验证的来源标注和置信度分级。

3. **格式正确 ≠ 内容正确——法律引用是"高格式、零容错"领域。** LLM 擅长模仿引用格式（案件名 + 卷号 + 页码），这反而使幻觉更隐蔽。格式检查不能替代内容验证。

4. **Grounding 必须连接到权威数据源，而非训练数据。** 法律 AI 的引用验证应直接查询 Westlaw、LexisNexis 等权威法律数据库，而非依赖模型内部的"知识"。RAG 是必要条件，但不是充分条件——RAG 检索到的内容同样可能被模型曲解。

5. **掩盖 AI 使用是比幻觉更严重的架构失败。** 多个案件中，律师的掩盖行为导致了比原始错误更严重的制裁。系统设计应使 AI 使用可追踪、可审计，而非将"是否披露"留给用户自行决定。

6. **商业产品不自动等于安全产品。** Thomson Reuters CoCounsel 的幻觉说明：付费 ≠ 无幻觉，专业化 ≠ 精确化。所有 LLM 产品在引用类任务上都需要独立验证层。

7. **行业监管正在快速跟进——架构设计必须预留合规接口。** 多个司法管辖区已开始或正在考虑要求披露 AI 使用。Agent 系统需要内置审计 trail 和 AI 使用标注机制。

---

## 与知识库的映射

| 知识库位置 | 关联内容 | 本案例的具体关系 |
|-----------|---------|----------------|
| `concepts/foundations/PRINCIPLE-INDEX.md` — MC-01 | 显式表达不确定性 | AI 以确定性语气输出未验证引用 |
| `concepts/foundations/PRINCIPLE-INDEX.md` — MC-03 | 知道自己不知道什么 | AI 无法区分"确知"与"概率生成" |
| `concepts/foundations/PRINCIPLE-INDEX.md` — IS-01 | 操作的是表示，不是现实 | AI "法律知识"是压缩表示，非权威数据 |
| `architecture/planes/representation/overview.md` | 表示层 | 置信度标定缺失 |
| `architecture/planes/effects/overview.md` | 效果层 | 引用验证门缺失 |
| `architecture/planes/world-state/overview.md` | 世界状态层 | 未连接权威法律数据库 |
| `architecture/planes/interaction/overview.md` | 交互层 | 未向用户表达不确定性 |
| `architecture/planes/explainability/overview.md` | 可解释层 | 输出溯源缺失 |
| `design-space/anti-patterns/depth-without-verification.md` | 深度无验证反模式 | AI 生成深层引用但不验证 |
| `evaluation/subjective-eval.md` | 主观性评估 | 法律引用准确性是客观可验证指标 |

---

## 关联文件

- `../../architecture/planes/representation/overview.md` — 表示层
- `../../architecture/planes/effects/overview.md` — 效果层
- `../../architecture/planes/explainability/overview.md` — 可解释层
- `../../concepts/foundations/PRINCIPLE-INDEX.md` — MC-01, MC-03, IS-01
- `../../design-space/anti-patterns/depth-without-verification.md` — 深度无验证反模式
- `./single-model-judge.md` — 单模型评审（相关：AI 评估 AI 的局限性）
