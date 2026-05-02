# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT.parent / "fixtures"
sys.path.insert(0, str(ROOT))

from runner import load_case, run_case, simple_yaml_load

# Support both old and new names
try:
    from runner import generate_baseline_trace
except ImportError:
    from runner import synthesize_trace as generate_baseline_trace

try:
    from runner import AgentAdapter, BaselineAdapter
except ImportError:
    AgentAdapter = None  # type: ignore[assignment,misc]
    BaselineAdapter = None  # type: ignore[assignment,misc]

from trace_comparator import check_criteria, check_invariants
from mock_tools import default_registry, MockToolRegistry
from world_fixture import WorldFixture, WorldObject


# ---------------------------------------------------------------------------
# Original tests (kept as-is)
# ---------------------------------------------------------------------------

class EvalRunnerTests(unittest.TestCase):
    def test_simple_yaml_load_nested_fixture(self) -> None:
        data = simple_yaml_load(
            '''
case_id: sample
input_event:
  source: chat
  raw_refs:
    - ref://one
world_state:
  - object_ref: obj:1
    state:
      value: 2
success_criteria:
  - effect verification recorded
'''
        )
        self.assertEqual(data["input_event"]["raw_refs"], ["ref://one"])
        self.assertEqual(data["world_state"][0]["state"]["value"], 2)

    def test_run_case_passes_without_external_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "research_claim_citation_001.yaml"
            path.write_text(
                '''
case_id: research_claim_citation_001
success_criteria:
  - key claim has citation chain
  - final answer cites evidence refs
  - final answer marks uncertainty explicitly
''',
                encoding="utf-8",
            )
            result = run_case(path)
            self.assertTrue(result["passed"])


# ---------------------------------------------------------------------------
# TestFixtureExecution – run each real fixture through run_case()
# ---------------------------------------------------------------------------

class TestFixtureExecution(unittest.TestCase):
    """Run each existing fixture YAML through run_case() and assert it passes."""

    def _run_fixture(self, filename: str) -> None:
        path = FIXTURES_DIR / filename
        self.assertTrue(path.exists(), f"Fixture not found: {path}")
        result = run_case(path)
        self.assertTrue(
            result["passed"],
            f"{filename} failed criteria: {result.get('failed_criteria')}",
        )
        self.assertGreater(result["trace_events"], 0)

    def test_crm_update_effect_001(self) -> None:
        self._run_fixture("crm_update_effect_001.yaml")

    def test_browser_checkout_guard_001(self) -> None:
        self._run_fixture("browser_checkout_guard_001.yaml")

    def test_browser_gui_grounding_001(self) -> None:
        self._run_fixture("browser_gui_grounding_001.yaml")

    def test_mcp_prompt_injection_001(self) -> None:
        self._run_fixture("mcp_prompt_injection_001.yaml")

    def test_mcp_confused_deputy_001(self) -> None:
        self._run_fixture("mcp_confused_deputy_001.yaml")

    def test_memory_poisoning_001(self) -> None:
        self._run_fixture("memory_poisoning_001.yaml")

    def test_ocr_invoice_parse_001(self) -> None:
        self._run_fixture("ocr_invoice_parse_001.yaml")

    def test_research_claim_citation_001(self) -> None:
        self._run_fixture("research_claim_citation_001.yaml")

    def test_research_conflict_resolution_001(self) -> None:
        self._run_fixture("research_conflict_resolution_001.yaml")

    def test_research_freshness_refresh_001(self) -> None:
        self._run_fixture("research_freshness_refresh_001.yaml")


# ---------------------------------------------------------------------------
# TestTraceComparator – unit tests for trace_comparator
# ---------------------------------------------------------------------------

class TestTraceComparator(unittest.TestCase):
    """Unit tests for check_criteria and check_invariants."""

    def test_empty_trace_fails_invariants(self) -> None:
        """An empty trace should not produce false-positive invariant passes
        when paired with a case that has success_criteria requiring content."""
        case = {
            "case_id": "empty",
            "success_criteria": [
                "effect verification recorded",
                "key claim has citation chain",
            ],
        }
        failed = check_criteria(case, [])
        # At least one criterion should fail on an empty trace
        self.assertTrue(len(failed) > 0, "Empty trace should fail at least one criterion")

    def test_tool_call_without_effect_record_fails(self) -> None:
        """A trace with a write-like tool_call but no effect_record should
        trigger the invariant 'write-like tool call lacks effect record'."""
        trace = [
            {"event_type": "tool_call", "tool": "crm_update_customer", "result": {"status": "success"}},
            {"event_type": "deliver", "case_id": "test"},
        ]
        failures = check_invariants(trace)
        self.assertTrue(
            any("effect record" in f for f in failures),
            f"Expected 'effect record' invariant failure, got: {failures}",
        )

    def test_all_verified_flags_warning(self) -> None:
        """If every event is marked 'verified' but there is a place_order
        action without a block, the invariant check should flag it."""
        trace = [
            {"event_type": "tool_call", "tool": "browser_click", "target": "place_order", "verification_status": "verified"},
            {"event_type": "deliver", "case_id": "test"},
        ]
        failures = check_invariants(trace)
        self.assertTrue(
            any("browser" in f or "place_order" in f or "unsafe" in f for f in failures),
            f"Expected unsafe action invariant failure, got: {failures}",
        )

    def test_valid_trace_passes(self) -> None:
        """A well-formed trace for a research case should pass both criteria and invariants."""
        case = {
            "case_id": "research_claim_citation_001",
            "success_criteria": [
                "key claim has citation chain",
                "final answer cites evidence refs",
                "final answer marks uncertainty explicitly",
            ],
        }
        trace = generate_baseline_trace(case)
        failed_criteria = check_criteria(case, trace)
        failed_invariants = check_invariants(trace)
        self.assertEqual(failed_criteria, [], f"Criteria failures: {failed_criteria}")
        self.assertEqual(failed_invariants, [], f"Invariant failures: {failed_invariants}")


# ---------------------------------------------------------------------------
# TestMockTools – unit tests for mock_tools
# ---------------------------------------------------------------------------

class TestMockTools(unittest.TestCase):
    """Unit tests for MockToolRegistry and default tools."""

    def setUp(self) -> None:
        self.world = WorldFixture(objects={
            "crm.customer:customer_a": WorldObject(
                object_ref="crm.customer:customer_a",
                state={"renewal_status": "pending", "account_owner": "user_123"},
            ),
        })
        self.registry = default_registry()

    def test_crm_search_returns_result(self) -> None:
        result = self.registry.call("crm_search_customer", {"query": "customer A"}, self.world)
        self.assertEqual(result["customer_ref"], "crm.customer:customer_a")
        self.assertIn("evidence_ref", result)

    def test_browser_click_place_order_blocked(self) -> None:
        result = self.registry.call("browser_click", {"target": "place_order"}, self.world)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["target"], "place_order")

    def test_unknown_tool_raises(self) -> None:
        with self.assertRaises(KeyError) as ctx:
            self.registry.call("nonexistent_tool", {}, self.world)
        self.assertIn("nonexistent_tool", str(ctx.exception))


# ---------------------------------------------------------------------------
# TestWorldFixture – unit tests for world_fixture
# ---------------------------------------------------------------------------

class TestWorldFixture(unittest.TestCase):
    """Unit tests for WorldFixture."""

    def test_from_case_creates_objects(self) -> None:
        case = {
            "world_state": [
                {
                    "object_ref": "crm.customer:customer_a",
                    "observed_at": "2024-01-01",
                    "freshness_ttl": "PT10M",
                    "state": {"renewal_status": "pending"},
                },
                {
                    "object_ref": "browser.page:checkout",
                    "state": {"url": "https://shop.example/checkout"},
                },
            ],
        }
        world = WorldFixture.from_case(case)
        self.assertIn("crm.customer:customer_a", world.objects)
        self.assertIn("browser.page:checkout", world.objects)
        self.assertEqual(
            world.objects["crm.customer:customer_a"].observed_at, "2024-01-01"
        )
        self.assertEqual(
            world.objects["crm.customer:customer_a"].freshness_ttl, "PT10M"
        )

    def test_read_returns_state(self) -> None:
        case = {
            "world_state": [
                {
                    "object_ref": "obj:1",
                    "state": {"key": "value", "num": 42},
                },
            ],
        }
        world = WorldFixture.from_case(case)
        state = world.read("obj:1")
        self.assertEqual(state, {"key": "value", "num": 42})
        # read returns a copy, not the original dict
        state["key"] = "mutated"
        self.assertEqual(world.read("obj:1")["key"], "value")

    def test_read_unknown_raises(self) -> None:
        world = WorldFixture()
        with self.assertRaises(KeyError):
            world.read("nonexistent")

    def test_update_applies_patch(self) -> None:
        case = {
            "world_state": [
                {
                    "object_ref": "obj:1",
                    "state": {"a": 1, "b": 2},
                },
            ],
        }
        world = WorldFixture.from_case(case)
        result = world.update("obj:1", {"b": 99, "c": 3})
        self.assertEqual(result, {"a": 1, "b": 99, "c": 3})
        self.assertEqual(world.read("obj:1"), {"a": 1, "b": 99, "c": 3})

    def test_update_creates_new_object(self) -> None:
        world = WorldFixture()
        result = world.update("new:obj", {"x": 10})
        self.assertEqual(result, {"x": 10})
        self.assertIn("new:obj", world.objects)


if __name__ == "__main__":
    unittest.main()
