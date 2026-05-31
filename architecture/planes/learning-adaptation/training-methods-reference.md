## 训练时学习方法参考

> **Evidence Status** — grounded. 综合 PPO/DPO/RLVR/SICA/AlphaEvolve 公开文献和技术报告。

运行时在线学习之外，Agent 能力的另一个提升路径是离线训练反馈环。以下方法不在运行时直接使用，但影响 Agent 的底层能力：

| 方法 | 机制 | 适用 |
|---|---|---|
| **PPO** | 收集交互 → 评估策略 → Clipping 约束更新幅度 | 通用 RL 微调 |
| **DPO** | 跳过 reward model，直接从偏好对学习 | 高效对齐 |
| **RLVR** | 用可验证答案（数学/代码）的奖励训练推理模型 | 推理能力提升 |
| **SICA** | 迭代自改进循环：审查历史 → 选最佳版本 → 修改 → 测试 → 记录 | Coding Agent 自进化 |
| **AlphaEvolve** | 多模型集成（Flash 初稿 + Pro 精化）→ 自动评估 → 迭代优化 | 算法发现、系统优化 |

SICA 的工具演化路径：Basic file-overwriting → Smart Editor → Diff-Enhanced → AST Symbol Locator → Hybrid。这说明 Agent 不仅优化策略，还能**优化自身工具链**，与本 plane 的 CandidateRecord 和 Skill Curator 模式呼应。
