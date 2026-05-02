# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
# llm.py -- 封装 Claude API 调用，将 LLM 响应解析为 Decision
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

import anthropic

from models import Decision

SYSTEM_PROMPT = """\
You are a ReAct agent that completes tasks by iteratively using tools.

Follow this loop for every step:
1. Observe -- review the current state and tool results so far.
2. Reason  -- decide what to do next and why (one sentence).
3. Act     -- call exactly one tool, or finalize if the goal is met.

IMPORTANT -- Tool success != world-state confirmation (IS-02 principle):
- A tool returning "success" only means the tool ran without error.
- You must VERIFY that the intended effect actually happened (e.g., read_file after edit_file).
- In your reasoning text, always include an EFFECT block describing the expected change:
  EFFECT: <what should change in the world>
  VERIFY: <readback|test|none> <how to verify after execution>
  POSTCONDITIONS: <comma-separated list of conditions that should be true>
- After each tool call result, check whether the effect was achieved before moving on.
- If verification fails, diagnose the cause and retry or adjust.

Constraints:
- When all success criteria are satisfied, finalize with a summary.
- Never call the same tool with identical arguments more than twice in a row.
- Keep your reasoning concise.
"""

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024


def decide(
    client: anthropic.Anthropic,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
) -> Decision:
    """调用 Claude API，返回一个 Decision。"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=tools,
    )

    # 解析 response content blocks
    reasoning = ""
    for block in response.content:
        if block.type == "text":
            reasoning += block.text
        elif block.type == "tool_use":
            intended_effect, verification_method, postconditions = _parse_effect_block(reasoning)
            return Decision(
                type="tool_call",
                tool_name=block.name,
                args=dict(block.input) if block.input else {},
                reasoning=reasoning,
                intended_effect=intended_effect,
                postconditions=postconditions,
                verification_method=verification_method,
            )

    # 没有 tool_use block 意味着 LLM 认为任务完成（或需要向用户提问）
    if response.stop_reason == "end_turn":
        return Decision(type="finalize", reasoning=reasoning)

    return Decision(type="finalize", reasoning=reasoning)


def _parse_effect_block(reasoning: str) -> tuple[str, str, list[str]]:
    """从 LLM reasoning 文本中提取 EFFECT / VERIFY / POSTCONDITIONS 结构化字段。"""
    intended_effect = ""
    verification_method = "none"
    postconditions: list[str] = []

    effect_match = re.search(r"EFFECT:\s*(.+)", reasoning)
    if effect_match:
        intended_effect = effect_match.group(1).strip()

    verify_match = re.search(r"VERIFY:\s*(\S+)", reasoning)
    if verify_match:
        method = verify_match.group(1).strip().lower()
        if method in ("readback", "test", "external_ack", "human_confirm", "none"):
            verification_method = method

    post_match = re.search(r"POSTCONDITIONS:\s*(.+)", reasoning)
    if post_match:
        postconditions = [c.strip() for c in post_match.group(1).split(",") if c.strip()]

    return intended_effect, verification_method, postconditions
