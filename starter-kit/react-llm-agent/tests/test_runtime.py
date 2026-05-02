# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
"""
Tests for ReactAgent runtime -- effect verification behaviour.

Validates the IS-02 principle: tool execution success != effect verification.
The runtime separates tool execution from effect verification via _verify_effect().

Decision fields:
  - intended_effect, postconditions (List[str]), verification_method
EffectRecord.verification_status values:
  verified | partially_verified | failed | unverifiable_by_agent | blocked | pending

All LLM calls are mocked so no API key or network is required.
"""
from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Provide a stub ``anthropic`` module so ``agent_runtime`` can be imported
# without the real SDK installed.
if "anthropic" not in sys.modules:
    _anthropic_stub = types.ModuleType("anthropic")
    _anthropic_stub.Anthropic = MagicMock  # type: ignore[attr-defined]
    sys.modules["anthropic"] = _anthropic_stub

from models import Decision, EffectRecord, TaskEnvelope  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_decision(
    tool_name: str,
    args: Dict[str, Any],
    reasoning: str = "",
    intended_effect: str = "",
    postconditions: List[str] | None = None,
    verification_method: str = "readback",
) -> Decision:
    """Build a tool_call Decision."""
    return Decision(
        type="tool_call",
        tool_name=tool_name,
        args=args,
        reasoning=reasoning,
        intended_effect=intended_effect,
        postconditions=postconditions or [],
        verification_method=verification_method,
    )


def _finalize_decision(reasoning: str = "done") -> Decision:
    return Decision(type="finalize", reasoning=reasoning)


def _side_effects(*decisions: Decision):
    """Return a side_effect list for patching ``llm.decide``.

    Appends a finalize decision so the loop always terminates.
    """
    return list(decisions) + [_finalize_decision()]


def _find_effect(effects: List[EffectRecord], tool: str) -> EffectRecord | None:
    for e in effects:
        if e.tool == tool:
            return e
    return None


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestEffectVerification(unittest.TestCase):
    """Each test mocks ``llm.decide`` and runs the agent through its public
    ``ReactAgent.run()`` method, then asserts on the resulting
    ``EffectRecord.verification_status``.
    """

    # ---- 1. tool_success_but_effect_failed --------------------------------
    @patch("agent_runtime.decide")
    def test_tool_success_but_effect_failed(self, mock_decide: MagicMock) -> None:
        """edit_file returns success but readback shows postcondition unmet.

        The old_text does not exist in the file, so replace is a no-op.
        Tool returns {"status": "success", "changed": false} but readback
        verification finds the postcondition string missing from the file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "config.yaml"
            target.write_text("key: old_value\n", encoding="utf-8")

            decision = _make_decision(
                tool_name="edit_file",
                args={"path": "config.yaml", "old_text": "NONEXISTENT", "new_text": "key: new_value"},
                reasoning="Replace old_value with new_value",
                intended_effect="config.yaml contains key: new_value",
                postconditions=["new_value"],
                verification_method="readback",
            )
            mock_decide.side_effect = _side_effects(decision)

            from agent_runtime import ReactAgent
            agent = ReactAgent(workspace)
            task = TaskEnvelope(goal="Update config", success_criteria=["config.yaml contains new_value"])
            result = agent.run(task)

            effect = _find_effect(result.effects, "edit_file")
            self.assertIsNotNone(effect, "Expected an EffectRecord for edit_file")
            self.assertEqual(effect.verification_status, "failed",
                             "Readback should detect postcondition 'new_value' is absent")

    # ---- 2. edit_file_success_changed_false --------------------------------
    @patch("agent_runtime.decide")
    def test_edit_file_success_changed_false(self, mock_decide: MagicMock) -> None:
        """edit_file reports changed=false because old_text was not found.

        With readback verification and a postcondition, the verifier should
        detect the mismatch and not blindly trust the tool's success status.
        """
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "readme.txt"
            target.write_text("hello\n", encoding="utf-8")

            decision = _make_decision(
                tool_name="edit_file",
                args={"path": "readme.txt", "old_text": "world", "new_text": "earth"},
                reasoning="Replace world with earth",
                intended_effect="readme.txt contains earth",
                postconditions=["earth"],
                verification_method="readback",
            )
            mock_decide.side_effect = _side_effects(decision)

            from agent_runtime import ReactAgent
            agent = ReactAgent(workspace)
            result = agent.run(TaskEnvelope(goal="Fix readme"))

            effect = _find_effect(result.effects, "edit_file")
            self.assertIsNotNone(effect)
            self.assertEqual(effect.verification_status, "failed",
                             "Postcondition 'earth' is absent -- verification should fail")

    # ---- 3. run_command_exit_0_but_target_unchanged -----------------------
    @patch("agent_runtime.decide")
    def test_run_command_exit_0_but_target_unchanged(self, mock_decide: MagicMock) -> None:
        """Command exits 0 but the intended file modification did not happen.

        The command ``echo done`` succeeds but never creates output.txt.
        With readback verification and a file-content postcondition, the
        verifier should detect the file is absent/empty.
        """
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            decision = _make_decision(
                tool_name="run_command",
                args={"command": "echo done"},
                reasoning="Generate output.txt",
                intended_effect="output.txt is created with results",
                postconditions=["results"],
                verification_method="readback",
            )
            mock_decide.side_effect = _side_effects(decision)

            from agent_runtime import ReactAgent
            agent = ReactAgent(workspace)
            result = agent.run(TaskEnvelope(goal="Generate output"))

            effect = _find_effect(result.effects, "run_command")
            self.assertIsNotNone(effect)

            # run_command result has no "path" key, and decision.args has no
            # "path" key either (it has "command"), so readback cannot determine
            # which file to read -> should be blocked or failed.
            self.assertNotEqual(effect.verification_status, "verified",
                                "Should not be verified when the intended file was never created")

    # ---- 4. unverifiable_effect -------------------------------------------
    @patch("agent_runtime.decide")
    def test_unverifiable_effect(self, mock_decide: MagicMock) -> None:
        """Action with verification_method='none' is unverifiable by the agent.

        Sending a notification has a real-world effect outside the agent's
        observation scope, so the runtime should mark it unverifiable_by_agent.
        """
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            decision = _make_decision(
                tool_name="run_command",
                args={"command": "echo 'notification sent'"},
                reasoning="Send a Slack notification",
                intended_effect="User receives Slack notification",
                verification_method="none",
            )
            mock_decide.side_effect = _side_effects(decision)

            from agent_runtime import ReactAgent
            agent = ReactAgent(workspace)
            result = agent.run(TaskEnvelope(goal="Notify user"))

            effect = _find_effect(result.effects, "run_command")
            self.assertIsNotNone(effect)
            self.assertEqual(effect.verification_status, "unverifiable_by_agent")

    # ---- 5. blocked_verification ------------------------------------------
    @patch("agent_runtime.decide")
    def test_blocked_verification(self, mock_decide: MagicMock) -> None:
        """Readback verification is blocked when read_file raises an exception.

        The registry.call for read_file is sabotaged to raise, triggering the
        except branch in _verify_readback which returns status='blocked'.
        """
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "data.json"
            target.write_text('{"v": 1}', encoding="utf-8")

            decision = _make_decision(
                tool_name="edit_file",
                args={"path": "data.json", "old_text": '"v": 1', "new_text": '"v": 2'},
                reasoning="Bump version in data.json",
                intended_effect='data.json contains "v": 2',
                postconditions=['"v": 2'],
                verification_method="readback",
            )
            mock_decide.side_effect = _side_effects(decision)

            from agent_runtime import ReactAgent
            agent = ReactAgent(workspace)

            # Sabotage read_file to raise an exception so the readback
            # verification hits the except branch -> "blocked".
            original_call = agent.registry.call

            def _sabotaged_call(ws: Path, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
                if name == "read_file":
                    raise OSError("permission denied (simulated)")
                return original_call(ws, name, args)

            agent.registry.call = _sabotaged_call  # type: ignore[assignment]

            result = agent.run(TaskEnvelope(goal="Bump version"))

            effect = _find_effect(result.effects, "edit_file")
            self.assertIsNotNone(effect)
            self.assertEqual(effect.verification_status, "blocked",
                             "Readback tool exception should yield 'blocked' status")


# ---------------------------------------------------------------------------
# Supplementary: loop-detection sanity check
# ---------------------------------------------------------------------------

class TestLoopDetection(unittest.TestCase):
    """Ensure the existing loop-detection guard works."""

    @patch("agent_runtime.decide")
    def test_identical_calls_trigger_loop_detection(self, mock_decide: MagicMock) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "f.txt").write_text("x", encoding="utf-8")

            same = _make_decision(
                tool_name="read_file",
                args={"path": "f.txt"},
                reasoning="check file",
                verification_method="none",
            )
            # Supply enough identical decisions to trigger the 3-window detector
            mock_decide.side_effect = [same, same, same, _finalize_decision()]

            from agent_runtime import ReactAgent
            result = ReactAgent(workspace).run(TaskEnvelope(goal="read"))

            loop_events = [e for e in result.trace if e.event_type == "loop_detected"]
            self.assertTrue(len(loop_events) >= 1, "Loop detection should fire")


if __name__ == "__main__":
    unittest.main()
