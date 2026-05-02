# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_runtime import StatefulAgent, task_from_dict
from models import EffectRecord, TaskCheckpoint, TraceEvent, WorldStateSnapshot
from state_store import StateStore
from tools import ToolRegistry


def _make_task(actions, goal="test goal"):
    """Build a TaskEnvelope from a list of action dicts."""
    return task_from_dict({"goal": goal, "actions": actions})


def _simple_action(name, path, value, on_failure="stop"):
    """Shortcut for an edit_file action with contains-verification."""
    return {
        "tool": "edit_file",
        "args": {"path": path, "old_text": "", "new_text": value, "mode": "append"},
        "intended_effect": f"{path} contains {value}",
        "verification": {"kind": "contains", "path": path, "value": value},
        "on_failure": on_failure,
    }


class TestCheckpointSaveAndRestore(unittest.TestCase):
    """Verify that checkpoints are persisted after each step and that a new
    agent instance can resume from the saved checkpoint, skipping completed steps."""

    def test_checkpoint_save_and_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")

            # Seed a file so edit_file (append mode) can work.
            (workspace / "out.txt").write_text("", encoding="utf-8")

            actions = [
                _simple_action("step1", "out.txt", "AAA"),
                _simple_action("step2", "out.txt", "BBB"),
                _simple_action("step3", "out.txt", "CCC"),
            ]
            task = _make_task(actions)

            # --- First run: execute all 3 steps ---
            agent1 = StatefulAgent(workspace, store)
            result1 = agent1.run(task, resume=False)
            self.assertTrue(result1.success)

            # On success the checkpoint is cleaned up, so let's instead test the
            # partial-run scenario: run 2 steps, then interrupt.
            # Reset workspace.
            (workspace / "out.txt").write_text("", encoding="utf-8")
            store2 = StateStore(workspace / ".checkpoints2")

            # Use a registry that raises before executing step 3.
            call_count = {"n": 0}
            real_registry = agent1.registry

            def counting_call(ws, name, args):
                if name == "edit_file":
                    call_count["n"] += 1
                    if call_count["n"] >= 3:
                        raise RuntimeError("simulated crash at step 3")
                return real_registry.call(ws, name, args)

            mock_registry = MagicMock(spec=ToolRegistry)
            mock_registry.call.side_effect = counting_call

            agent2 = StatefulAgent(workspace, store2, registry=mock_registry)
            result2 = agent2.run(task, resume=False)
            # Should have stopped at step 3 due to the simulated crash.
            self.assertFalse(result2.success)

            tid = StatefulAgent.task_id(task.goal)
            checkpoint = store2.load(tid)
            self.assertIsNotNone(checkpoint)
            # Steps 1 and 2 completed; step 3 failed, checkpoint records step 2.
            self.assertEqual(checkpoint.completed_step, 2)

            # --- Second run: resume from checkpoint ---
            # Use the real registry so step 3 succeeds.
            agent3 = StatefulAgent(workspace, store2)
            result3 = agent3.run(task, resume=True)
            # The run completes, but the failure from the first attempt is
            # carried over, so success is False (recovered failure).
            self.assertIn("Completed", result3.summary)

            # Verify the resume trace event exists.
            resume_events = [t for t in result3.trace if t.event_type == "resume"]
            self.assertEqual(len(resume_events), 1)
            self.assertEqual(resume_events[0].payload["from_step"], 2)

            # The trace carries forward events from the checkpoint (including
            # decide events from steps 1-2) plus new ones for step 3.
            # Only step 3 should appear as a NEW decide event after resume.
            resume_idx = next(
                i for i, t in enumerate(result3.trace) if t.event_type == "resume"
            )
            new_decide_events = [
                t for t in result3.trace[resume_idx:]
                if t.event_type == "decide"
            ]
            self.assertEqual(len(new_decide_events), 1)
            self.assertEqual(new_decide_events[0].payload["step"], 3)

            # All effects should be verified.
            self.assertTrue(
                all(e.verification_status == "verified" for e in result3.effects)
            )


class TestWorldStateTTLExpiry(unittest.TestCase):
    """Verify that the agent refreshes a stale world-state snapshot."""

    def test_stale_snapshot_triggers_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")

            # Prepare world-state file.
            world_dir = workspace / ".world"
            world_dir.mkdir()
            import json
            (world_dir / "myservice.json").write_text(
                json.dumps({"status": "healthy"}), encoding="utf-8"
            )

            # Seed out.txt for edit verification.
            (workspace / "out.txt").write_text("", encoding="utf-8")

            actions = [
                {
                    "tool": "edit_file",
                    "args": {
                        "path": "out.txt",
                        "old_text": "",
                        "new_text": "done",
                        "mode": "append",
                        "world_state_target": "myservice",
                    },
                    "intended_effect": "out.txt contains done",
                    "verification": {"kind": "contains", "path": "out.txt", "value": "done"},
                }
            ]
            task = _make_task(actions, goal="world state test")

            # Use TTL=0 so every snapshot is immediately stale.
            agent = StatefulAgent(
                workspace, store, world_state_ttl=timedelta(seconds=0)
            )
            result = agent.run(task, resume=False)
            self.assertTrue(result.success)

            # The trace should contain a world_state_refresh event.
            ws_events = [t for t in result.trace if t.event_type == "world_state_refresh"]
            self.assertGreaterEqual(len(ws_events), 1)
            self.assertEqual(ws_events[0].payload["target"], "myservice")

    def test_fresh_snapshot_reused(self) -> None:
        """With a long TTL, a pre-existing fresh snapshot is reused (no extra tool call)."""
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")

            world_dir = workspace / ".world"
            world_dir.mkdir()
            import json
            (world_dir / "myservice.json").write_text(
                json.dumps({"status": "ok"}), encoding="utf-8"
            )
            (workspace / "out.txt").write_text("", encoding="utf-8")

            actions = [
                {
                    "tool": "edit_file",
                    "args": {
                        "path": "out.txt",
                        "old_text": "",
                        "new_text": "A",
                        "mode": "append",
                        "world_state_target": "myservice",
                    },
                    "intended_effect": "out.txt contains A",
                    "verification": {"kind": "contains", "path": "out.txt", "value": "A"},
                },
                {
                    "tool": "edit_file",
                    "args": {
                        "path": "out.txt",
                        "old_text": "",
                        "new_text": "B",
                        "mode": "append",
                        "world_state_target": "myservice",
                    },
                    "intended_effect": "out.txt contains B",
                    "verification": {"kind": "contains", "path": "out.txt", "value": "B"},
                },
            ]
            task = _make_task(actions, goal="fresh snapshot test")

            call_log: list[str] = []
            real_registry = StatefulAgent(workspace, store).registry

            def tracking_call(ws, name, args):
                call_log.append(name)
                return real_registry.call(ws, name, args)

            mock_registry = MagicMock(spec=ToolRegistry)
            mock_registry.call.side_effect = tracking_call

            # Long TTL so the snapshot created at step 1 is still fresh at step 2.
            agent = StatefulAgent(
                workspace, store, registry=mock_registry,
                world_state_ttl=timedelta(hours=1),
            )
            result = agent.run(task, resume=False)
            self.assertTrue(result.success)

            # check_world_state should only be called once (step 1).
            cws_calls = [c for c in call_log if c == "check_world_state"]
            self.assertEqual(len(cws_calls), 1)


class TestInterruptAndResume(unittest.TestCase):
    """Simulate an interruption mid-run and verify the agent resumes
    from the correct step without re-executing completed work."""

    def test_interrupt_and_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")
            (workspace / "log.txt").write_text("", encoding="utf-8")

            actions = [
                _simple_action("s1", "log.txt", "STEP1\n"),
                _simple_action("s2", "log.txt", "STEP2\n"),
                _simple_action("s3", "log.txt", "STEP3\n"),
                _simple_action("s4", "log.txt", "STEP4\n"),
            ]
            task = _make_task(actions, goal="interrupt test")

            # Run all steps first to build a valid checkpoint at step 2.
            # We'll manually craft a checkpoint as if the agent completed 2 steps.
            tid = StatefulAgent.task_id(task.goal)
            fake_checkpoint = TaskCheckpoint(
                task_goal=task.goal,
                completed_step=2,
                total_steps=4,
                effects=[
                    EffectRecord(
                        tool="edit_file",
                        intended_effect="log.txt contains STEP1\\n",
                        verification_kind="contains",
                        verification_status="verified",
                        evidence={},
                    ),
                    EffectRecord(
                        tool="edit_file",
                        intended_effect="log.txt contains STEP2\\n",
                        verification_kind="contains",
                        verification_status="verified",
                        evidence={},
                    ),
                ],
                failures=[],
                trace=[
                    TraceEvent("intake", {"goal": task.goal, "action_count": 4}),
                    TraceEvent("decide", {"step": 1, "tool": "edit_file", "intended_effect": ""}),
                    TraceEvent("decide", {"step": 2, "tool": "edit_file", "intended_effect": ""}),
                ],
                world_snapshots=[],
                context_summary="Steps executed: 2. Effects: 2 verified, 0 failed.",
            )
            store.save(tid, fake_checkpoint)

            # Pre-populate the file as if steps 1-2 ran.
            (workspace / "log.txt").write_text("STEP1\nSTEP2\n", encoding="utf-8")

            # Resume: only steps 3 and 4 should execute.
            agent = StatefulAgent(workspace, store)
            result = agent.run(task, resume=True)
            self.assertTrue(result.success)

            # Verify steps 1-2 were skipped by checking decide events.
            decide_events = [t for t in result.trace if t.event_type == "decide"]
            executed_steps = [d.payload["step"] for d in decide_events]
            # Steps from the restored trace (1, 2) plus newly executed (3, 4).
            self.assertIn(3, executed_steps)
            self.assertIn(4, executed_steps)

            # The new decide events should only be for steps 3 and 4.
            # Count new decide events (after the resume event).
            resume_idx = next(
                i for i, t in enumerate(result.trace) if t.event_type == "resume"
            )
            new_decide_events = [
                t for t in result.trace[resume_idx:]
                if t.event_type == "decide"
            ]
            self.assertEqual(len(new_decide_events), 2)
            self.assertEqual(new_decide_events[0].payload["step"], 3)
            self.assertEqual(new_decide_events[1].payload["step"], 4)

            # Final file should have all 4 steps.
            content = (workspace / "log.txt").read_text(encoding="utf-8")
            self.assertIn("STEP3", content)
            self.assertIn("STEP4", content)


class TestContextCompaction(unittest.TestCase):
    """Verify that _compact_context produces a meaningful summary and that
    the checkpoint preserves the summary after compaction."""

    def test_compact_context_summary_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")
            agent = StatefulAgent(workspace, store)

            trace = [
                TraceEvent("decide", {"step": 1}),
                TraceEvent("decide", {"step": 2}),
                TraceEvent("decide", {"step": 3}),
            ]
            effects = [
                EffectRecord("tool_a", "effect_a", "contains", "verified", {}),
                EffectRecord("tool_b", "effect_b", "contains", "verified", {}),
                EffectRecord("tool_c", "effect_c", "contains", "failed", {}),
            ]

            summary = agent._compact_context(trace, effects)
            self.assertIn("3", summary)  # 3 steps
            self.assertIn("2 verified", summary)
            self.assertIn("1 failed", summary)

    def test_checkpoint_preserves_summary_across_save_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = StateStore(workspace / ".checkpoints")
            (workspace / "f.txt").write_text("", encoding="utf-8")

            actions = [
                _simple_action("s1", "f.txt", "X"),
                _simple_action("s2", "f.txt", "Y"),
            ]
            task = _make_task(actions, goal="compaction test")

            # Make step 2 fail so checkpoint is saved and run stops.
            call_count = {"n": 0}
            real_registry = StatefulAgent(workspace, store).registry

            def fail_on_second(ws, name, args):
                result = real_registry.call(ws, name, args)
                if name == "edit_file":
                    call_count["n"] += 1
                    if call_count["n"] == 2:
                        raise RuntimeError("boom")
                return result

            mock_registry = MagicMock(spec=ToolRegistry)
            mock_registry.call.side_effect = fail_on_second

            agent = StatefulAgent(workspace, store, registry=mock_registry)
            result = agent.run(task, resume=False)
            self.assertFalse(result.success)

            tid = StatefulAgent.task_id(task.goal)
            checkpoint = store.load(tid)
            self.assertIsNotNone(checkpoint)

            # The context_summary should reflect step 1's completion.
            self.assertIn("1 verified", checkpoint.context_summary)
            self.assertIn("Steps executed", checkpoint.context_summary)

            # Ensure the summary survives a round-trip through JSON serialization.
            data = checkpoint.to_dict()
            restored = TaskCheckpoint.from_dict(data)
            self.assertEqual(restored.context_summary, checkpoint.context_summary)


if __name__ == "__main__":
    unittest.main()
