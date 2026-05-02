# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
# agent_runtime.py -- ReAct 主循环：observe -> decide -> execute -> verify -> loop/finalize
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import anthropic

from llm import decide
from models import Decision, EffectRecord, RunResult, TaskEnvelope, TraceEvent
from tools import ToolRegistry, default_registry

MAX_STEPS = 15
LOOP_DETECT_WINDOW = 3


class ReactAgent:
    def __init__(self, workspace: Path, registry: ToolRegistry | None = None) -> None:
        self.workspace = workspace
        self.registry = registry or default_registry()
        self.client = anthropic.Anthropic()  # 从 ANTHROPIC_API_KEY 环境变量读取

    def _verify_effect(self, decision: Decision, exec_result: Dict[str, Any]) -> EffectRecord:
        """Separate verification step: tool execution result != effect verification (IS-02).

        Verification methods:
        - readback: call read_file to confirm the change is present on disk
        - test: run a command and check exit_code == 0
        - none: no verification possible -> unverifiable_by_agent
        - external_ack / human_confirm: not automatable -> unverifiable_by_agent
        """
        method = decision.verification_method
        intended = decision.intended_effect or decision.reasoning

        # If the tool itself errored, mark failed immediately -- no verification needed
        if exec_result.get("status") == "error":
            return EffectRecord(
                tool=decision.tool_name,
                intended_effect=intended,
                verification_method=method,
                verification_status="failed",
                evidence={"execution_result": exec_result, "reason": "tool returned error"},
            )

        # Readback verification: re-read the file and check postconditions
        if method == "readback":
            return self._verify_readback(decision, exec_result)

        # Test verification: run a command and check exit code
        if method == "test":
            return self._verify_test(decision, exec_result)

        # Methods not automatable by the agent
        if method in ("external_ack", "human_confirm"):
            return EffectRecord(
                tool=decision.tool_name,
                intended_effect=intended,
                verification_method=method,
                verification_status="unverifiable_by_agent",
                evidence={"execution_result": exec_result, "reason": f"{method} requires external input"},
            )

        # Default: no verification method specified
        return EffectRecord(
            tool=decision.tool_name,
            intended_effect=intended,
            verification_method="none",
            verification_status="unverifiable_by_agent",
            evidence={"execution_result": exec_result, "reason": "no verification method specified"},
        )

    def _verify_readback(self, decision: Decision, exec_result: Dict[str, Any]) -> EffectRecord:
        """Read back a file to confirm the intended change landed."""
        intended = decision.intended_effect or decision.reasoning
        path = exec_result.get("path") or decision.args.get("path")
        if not path:
            return EffectRecord(
                tool=decision.tool_name, intended_effect=intended,
                verification_method="readback", verification_status="blocked",
                evidence={"reason": "no file path available for readback"},
            )
        try:
            readback = self.registry.call(self.workspace, "read_file", {"path": path})
        except Exception as exc:
            return EffectRecord(
                tool=decision.tool_name, intended_effect=intended,
                verification_method="readback", verification_status="blocked",
                evidence={"reason": f"readback tool error: {exc}"},
            )

        # Check postconditions against the readback content
        text = readback.get("text", "")
        if decision.postconditions:
            matched = [pc for pc in decision.postconditions if pc in text]
            all_met = len(matched) == len(decision.postconditions)
            status = "verified" if all_met else "partially_verified" if matched else "failed"
        else:
            # No postconditions specified; readback succeeded but nothing to check
            status = "verified" if readback.get("status") == "success" else "failed"

        return EffectRecord(
            tool=decision.tool_name, intended_effect=intended,
            verification_method="readback", verification_status=status,
            evidence={
                "execution_result": exec_result,
                "readback_path": path,
                "postconditions": decision.postconditions,
                "matched": matched if decision.postconditions else [],
            },
        )

    def _verify_test(self, decision: Decision, exec_result: Dict[str, Any]) -> EffectRecord:
        """Run a test command to verify the effect."""
        intended = decision.intended_effect or decision.reasoning
        # Use the first postcondition as the test command, or fall back to a simple check
        test_cmd = decision.postconditions[0] if decision.postconditions else None
        if not test_cmd:
            return EffectRecord(
                tool=decision.tool_name, intended_effect=intended,
                verification_method="test", verification_status="blocked",
                evidence={"reason": "no test command in postconditions"},
            )
        try:
            test_result = self.registry.call(self.workspace, "run_command", {"command": test_cmd})
        except Exception as exc:
            return EffectRecord(
                tool=decision.tool_name, intended_effect=intended,
                verification_method="test", verification_status="blocked",
                evidence={"reason": f"test command error: {exc}"},
            )
        ok = test_result.get("exit_code") == 0
        return EffectRecord(
            tool=decision.tool_name, intended_effect=intended,
            verification_method="test",
            verification_status="verified" if ok else "failed",
            evidence={"execution_result": exec_result, "test_result": test_result},
        )

    def run(self, task: TaskEnvelope) -> RunResult:
        trace: List[TraceEvent] = []
        effects: List[EffectRecord] = []
        messages: List[Dict[str, Any]] = []
        recent_calls: List[Tuple[str, str]] = []  # (tool_name, args_json) 用于循环检测

        # 构建初始 user message
        user_prompt = f"Goal: {task.goal}"
        if task.success_criteria:
            user_prompt += "\nSuccess criteria:\n" + "\n".join(f"- {c}" for c in task.success_criteria)
        messages.append({"role": "user", "content": user_prompt})

        trace.append(TraceEvent("intake", {"goal": task.goal}))

        tools_schema = self.registry.schemas_for_llm()

        for step in range(1, MAX_STEPS + 1):
            # --- LLM Decide ---
            decision = decide(self.client, messages, tools_schema)
            trace.append(TraceEvent("decide", {
                "step": step, "type": decision.type,
                "tool": decision.tool_name, "reasoning": decision.reasoning,
            }))

            if decision.type == "finalize":
                trace.append(TraceEvent("finalize", {"step": step, "reasoning": decision.reasoning}))
                break

            if decision.type == "ask_user":
                trace.append(TraceEvent("ask_user", {"step": step, "reasoning": decision.reasoning}))
                break

            # --- 循环检测 ---
            call_sig = (decision.tool_name or "", json.dumps(decision.args, sort_keys=True))
            recent_calls.append(call_sig)
            if len(recent_calls) >= LOOP_DETECT_WINDOW:
                window = recent_calls[-LOOP_DETECT_WINDOW:]
                if all(c == window[0] for c in window):
                    trace.append(TraceEvent("loop_detected", {
                        "step": step, "tool": decision.tool_name, "args": decision.args,
                    }))
                    break

            # --- Execute Tool ---
            try:
                result = self.registry.call(self.workspace, decision.tool_name, decision.args)
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}

            trace.append(TraceEvent("tool_result", {
                "step": step, "tool": decision.tool_name, "result": result,
            }))

            # --- Verify Effect (IS-02: tool success != world-state confirmation) ---
            effect = self._verify_effect(decision, result)
            effects.append(effect)
            trace.append(TraceEvent("effect_record", {
                "step": step, "tool": decision.tool_name,
                "verification_method": effect.verification_method,
                "verification_status": effect.verification_status,
                "evidence": effect.evidence,
            }))

            # --- 将工具调用和结果追加到 messages，供下一轮 LLM 观察 ---
            messages.append({
                "role": "assistant",
                "content": [
                    {"type": "text", "text": decision.reasoning} if decision.reasoning else None,
                    {
                        "type": "tool_use",
                        "id": f"call_{step}",
                        "name": decision.tool_name,
                        "input": decision.args,
                    },
                ],
            })
            # 过滤掉 None
            messages[-1]["content"] = [b for b in messages[-1]["content"] if b is not None]

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": f"call_{step}",
                        "content": json.dumps(result, ensure_ascii=False)[:4000],
                    }
                ],
            })
        else:
            trace.append(TraceEvent("max_steps", {"limit": MAX_STEPS}))

        # --- 汇总 ---
        verified = sum(1 for e in effects if e.verification_status == "verified")
        failed = sum(1 for e in effects if e.verification_status == "failed")
        unverifiable = sum(1 for e in effects if e.verification_status in ("unverifiable_by_agent", "blocked"))
        total = len(effects)
        # Success requires: no failures, and at least one effect was verified or all are unverifiable
        success = failed == 0 and total > 0 and (verified > 0 or unverifiable == total)
        summary = f"{verified}/{total} verified, {failed} failed, {unverifiable} unverifiable."
        if any(e.event_type == "loop_detected" for e in trace):
            summary += " Stopped due to loop detection."
        if any(e.event_type == "max_steps" for e in trace):
            summary += " Stopped due to max steps limit."

        trace.append(TraceEvent("deliver", {"success": success, "summary": summary}))
        return RunResult(goal=task.goal, success=success, effects=effects, trace=trace, summary=summary)
