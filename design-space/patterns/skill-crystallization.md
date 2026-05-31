# Skill Crystallization

> **Evidence Status** — grounded. 源自 Generic Agent 的 self-evolution 机制，以及多类 Agent 对项目约定、成功路径和 SOP 复用的共同需求。需要注意：技能固化若缺乏验证和退役机制，容易把偶然成功固化成长期错误。

Agent 每次遇到相似任务都从头摸索（重复装依赖、重复探索解法、重复踩坑），这是巨大的浪费。技能固化（Skill Crystallization）让 Agent 把经过验证的执行路径提炼为可复用的技能（Skill），下次遇到相似任务时直接召回执行。核心挑战是"如何只记住对的东西"。

## 固化流程

整个流程是一条从探索到复用的管线：

1. **首次探索**：Agent 自主安装依赖、编写脚本、调试验证，完成任务。
2. **提炼候选**：从成功的执行路径中抽取前置条件、关键步骤、脚本、典型坑点和验证方法，形成候选技能（Candidate Skill）。
3. **验证与治理**：通过二次运行、fixture eval 或人工审查后，候选技能才能激活。未经验证的路径不能直接成为 active skill。
4. **召回与执行**：相似任务通过 `skill_search` 召回匹配技能，直接执行或作为计划骨架。
5. **监控与退役**：命中后成功率下降时自动降权或停用，避免过时技能持续误导。

```python
def task_loop(task):
    skill = skill_search(task.description)
    if skill and skill.status == "active" and skill.confidence > 0.8:
        return execute_skill(skill)

    result = autonomous_explore(task)
    if result.success:
        candidate = crystallize(task, result.execution_path)
        validate_and_activate(candidate)
    return result
```

## Skill Schema

每个技能是一个结构化记录，包含作用域、前置条件、步骤、所需工具、验证方法、已知失败场景和生命周期状态：

```yaml
skill_id: string
scope:
  project: string | null
  domain: coding | research | workflow | memory | ops
preconditions: []
steps: []
tools_required: []
verification: []
known_failures: []
do_not_use_when: []
evidence:
  successful_runs: []
  failed_runs: []
expiry_policy:
  review_after: datetime | null
  invalidation_triggers: []
permissions_required: []
status: candidate | active | deprecated | rolled_back
```

## 固化什么、不固化什么

核心原则：只固化**经过行动验证、可追溯、可再次验证**的信息。

值得固化的包括：环境事实（路径、配置、项目约定）、关键前置条件、典型坑点及其解法、可复用脚本和验证方法。不应进入技能的包括：临时变量、随机试错过程、未验证的假设、一次性外部状态。

## 权衡

技能固化对重复性任务的效率提升非常显著，尤其是长期运行的个人或团队 Agent，能逐步形成项目和领域专属的技能树。失败路径同样有价值，可以沉淀为 `do_not_use_when` 条件，避免后续踩同样的坑。

但技能会过时。项目依赖升级、API 变更、环境迁移都可能让一个曾经有效的技能变成错误指导。如果没有作用域治理、证据回放和退役机制，技能库会逐渐被污染。召回精度也是问题：任务描述相似不代表执行路径相同，错误召回比没有召回更危险。`expiry_policy` 和 `invalidation_triggers` 是这个模式能否长期运行的关键。

## 参考实现

- `projects/general-agents/generic-agent/self-evolution.md`
