# L0-L4 五层记忆系统

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 核心哲学：**No Execution, No Memory** — 只存行动验证的信息

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│ L0: META RULES (memory_management_sop.md)                  │
│ • 核心公理：行动验证原则、禁止易变状态                    │
│ • 信息分类决策树、层级同步规则                             │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ L1: 全局索引 (global_mem_insight.txt)                      │
│ ≤30行，<1K tokens，极简导航                               │
│ • 高频场景 key→value 直接定位                             │
│ • 低频场景仅列关键词                                       │
│ • [RULES] 压缩版避坑准则                                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ L2: 全局事实库 (global_mem.txt)                            │
│ • 环境特异性：路径、凭证、配置、ID                        │
│ • 按 ## [SECTION] 组织，可膨胀                            │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ L3: 任务 Skills/SOPs (../memory/*.md, *.py)               │
│ • 精简 SOP：关键前置条件 + 典型坑点                       │
│ • 工具脚本：可复用的自动化代码                            │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ L4: 会话历史归档 (L4_raw_sessions/)                        │
│ • 原始日志：model_responses_PID.txt                        │
│ • 压缩格式：MMDD_HHMM-MMDD_HHMM.txt                       │
│ • 聚合索引：all_histories.txt                              │
│ • 月度存档：YYYY-MM.zip                                    │
└─────────────────────────────────────────────────────────────┘
```

## L1 示例格式

```
浏览器自动化: web_scan/web_execute_js直接调用 | 特殊:tmwebdriver_sop(...)
键鼠模拟: ljqCtrl_sop+.py(仅win，禁pyautogui/先activate窗口)
定时任务: scheduled_task_sop(报告→sche_tasks/done/)

[RULES]
1. 搜索先行: 信息用google, 项目内os.listdir, 禁猜路径
2. 交叉验证: 禁信搜索摘要, 数值必进详情页核实
3. 编码安全: 改前必读源码; import memory用sys.path.append
```

## 工作记忆工具

### update_working_checkpoint

```python
def do_update_working_checkpoint(self, args, response):
    '''设定临时工作记忆，传递给下一轮'''
    if "key_info" in args:
        self.working['key_info'] = args['key_info']
    if "related_sop" in args:
        self.working['related_sop'] = args['related_sop']
    self.working['passed_sessions'] = 0  # 重置代龄

    next_prompt = self._get_anchor_prompt()
    return StepOutcome({"result": "updated"}, next_prompt=next_prompt)
```

### start_long_term_update

```python
def do_start_long_term_update(self, args, response):
    '''任务完成时触发长期记忆结算'''
    prompt = '''### [总结提炼经验]
    提取【事实验证成功且长期有效】的信息：
    - **环境事实** → file_patch 更新 L2 + 同步 L1
    - **复杂任务经验** → L3 精简 SOP

    禁止：临时变量、推理过程、未验证信息、通用常识
    '''
    result = get_global_memory()  # 注入现有 L1+L2
    return StepOutcome(result, next_prompt=prompt)
```

## 信息分类决策树

```python
def decide_layer(info):
    if is_environment_specific(info):  # IP/路径/凭证/API密钥
        return "L2"
    if is_generic_principle(info):      # 全局避坑指南
        return "L1 [RULES] (压缩为1句)"
    if is_task_specific_expertise(info): # 艰难尝试+长期有用
        return "L3 SOP/Script"
    return None  # 通用常识 → 不存储
```

## L4 压缩流程

```python
def batch_process(src, l4_dir):
    # P1: 压缩 + 提取历史
    for fp in raw_files:
        if mtime > cutoff:  # 跳过最近2小时
            continue
        dst, info = compress_session(fp, tmp_dir)
        results.append((sn, dst, extract_history(dst), info, fp))

    # P2: 追加历史到聚合文件
    with open('all_histories.txt', 'a') as f:
        for sn, _, hist, _, _ in results:
            f.write(format_history_block(sn, hist))

    # P3: 按月归档到 zip
    for mk, items in by_month.items():
        with ZipFile(f"{mk}.zip", 'a') as zf:
            for sn, cp in items:
                zf.write(cp, f"{sn}.txt")

    # P4: 删除源文件
```

---

## Summary 强制抽取机制（第二轮审计补充）

每轮 LLM 响应末尾被要求输出 `<summary>...</summary>` 标签，内含本轮关键信息摘要。
若 LLM 遗漏该标签，下一轮注入惩罚提示迫使补交：

```python
# turn_end_callback 中检测
if "<summary>" not in response.content:
    next_prompt += "\n[系统] 你遗漏了 <summary> 标签。立即补充本轮摘要，否则关键信息将丢失。"
```

抽取的 summary 存入 `working['earlier_context']`，在上下文截断时作为保底摘要保留。
这是"只传最新消息"极简架构的配套保障——没有累积历史，全靠 summary 链条维持连续性。

---

## Anchor Prompt 完整注入结构（第二轮审计补充）

`_get_anchor_prompt()` 是每轮消息的骨架，由三段拼接：

```python
def _get_anchor_prompt(self):
    parts = []
    # 1. earlier_context: 过往轮次的 summary 拼接（压缩历史）
    if self.working.get('earlier_context'):
        parts.append(f"<history>\n{self.working['earlier_context']}\n</history>")
    # 2. history: 最近 N 轮的原始交互（短期窗口）
    if self.working.get('history'):
        parts.append(f"<recent>\n{self.working['history']}\n</recent>")
    # 3. key_info: 任务关键信息（由 update_working_checkpoint 设置）
    if self.working.get('key_info'):
        parts.append(f"<key_info>\n{self.working['key_info']}\n</key_info>")
    return "\n".join(parts)
```

这三段构成从远到近的上下文梯度：压缩摘要 → 近期原文 → 任务锚点。

---

## passed_sessions 代龄计数器（第二轮审计补充）

`working['passed_sessions']` 记录工作记忆在多少个会话间被携带。每次新会话启动时递增：

```python
# 新会话开始时
self.working['passed_sessions'] = self.working.get('passed_sessions', 0) + 1
# 超过阈值 → 工作记忆过期，提示 Agent 重新读取或丢弃
if self.working['passed_sessions'] > 3:
    next_prompt += "\n[系统] 工作记忆已跨越 3 个会话，可能已过时。请验证后决定保留或丢弃。"
```

`update_working_checkpoint` 调用时重置为 0。这是对"跨会话漂移"的轻量级防护。

---

## 存在性编码理论（第二轮审计补充）

记忆系统遵循 ROI 公式决定信息是否值得持久化：

```
ROI = (复现代价 × 复用概率) / 存储成本
```

- **高 ROI**：环境特异性事实（路径/凭证/API 行为怪癖）→ L2
- **中 ROI**：经过艰难调试的多步 SOP → L3
- **低 ROI**：通用常识、单次推理过程 → 不存储

L0 元规则 `memory_management_sop.md` 将此公式编码为决策树，Agent 在 `start_long_term_update` 时自动执行。
核心约束：**行动验证原则**——仅存储已通过执行验证的信息，推理猜测一律丢弃。
