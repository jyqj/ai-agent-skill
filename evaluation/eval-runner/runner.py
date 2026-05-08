# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:  # PyYAML is optional; the fallback parser supports this repo's fixtures.
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

try:
    from mock_tools import default_registry
    from trace_comparator import check_criteria, check_invariants
    from world_fixture import WorldFixture
except ImportError:  # pragma: no cover
    from .mock_tools import default_registry
    from .trace_comparator import check_criteria, check_invariants
    from .world_fixture import WorldFixture


Line = Tuple[int, str]


def _strip_comments(line: str) -> str:
    in_quote: str | None = None
    escaped = False
    out: List[str] = []
    for ch in line:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            escaped = True
            continue
        if ch in {'"', "'"}:
            if in_quote == ch:
                in_quote = None
            elif not in_quote:
                in_quote = ch
            out.append(ch)
            continue
        if ch == "#" and not in_quote:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if "." in value and not value.startswith("http"):
            return float(value)
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return int(value)
    except ValueError:
        pass
    return value


def _split_key_value(text: str) -> Tuple[str, str] | None:
    # Treat a colon as YAML key separator only when it is followed by whitespace
    # or ends the line. This keeps scalar values such as ref://one or https://x
    # from being misread as mappings.
    sep_index = -1
    for i, ch in enumerate(text):
        if ch == ":" and (i + 1 == len(text) or text[i + 1].isspace()):
            sep_index = i
            break
    if sep_index < 0:
        return None
    key = text[:sep_index].strip()
    value = text[sep_index + 1 :].strip()
    if not key:
        return None
    return key, value


def _preprocess_yaml(text: str) -> List[Line]:
    lines: List[Line] = []
    for raw in text.splitlines():
        clean = _strip_comments(raw)
        if not clean.strip():
            continue
        indent = len(clean) - len(clean.lstrip(" "))
        lines.append((indent, clean.strip()))
    return lines


def _parse_block(lines: List[Line], index: int, indent: int) -> Tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    current_indent, content = lines[index]
    if current_indent < indent:
        return {}, index
    if content.startswith("- "):
        return _parse_list(lines, index, current_indent)
    return _parse_map(lines, index, current_indent)


def _parse_map(lines: List[Line], index: int, indent: int) -> Tuple[Dict[str, Any], int]:
    result: Dict[str, Any] = {}
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            # Child blocks are consumed by the parent key; reaching one here means malformed input.
            break
        if content.startswith("- "):
            break
        pair = _split_key_value(content)
        if pair is None:
            raise ValueError(f"Cannot parse YAML line: {content!r}")
        key, value = pair
        index += 1
        if value == "":
            if index < len(lines) and lines[index][0] > line_indent:
                child, index = _parse_block(lines, index, lines[index][0])
                result[key] = child
            else:
                result[key] = {}
        else:
            result[key] = _parse_scalar(value)
    return result, index


def _parse_list(lines: List[Line], index: int, indent: int) -> Tuple[List[Any], int]:
    result: List[Any] = []
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent < indent:
            break
        if line_indent != indent or not content.startswith("- "):
            break
        item_text = content[2:].strip()
        index += 1
        pair = _split_key_value(item_text)
        if item_text == "":
            if index < len(lines) and lines[index][0] > line_indent:
                child, index = _parse_block(lines, index, lines[index][0])
                result.append(child)
            else:
                result.append(None)
        elif pair is not None:
            key, value = pair
            item: Dict[str, Any] = {key: _parse_scalar(value) if value else {}}
            if index < len(lines) and lines[index][0] > line_indent:
                child, index = _parse_block(lines, index, lines[index][0])
                if isinstance(child, dict):
                    item.update(child)
                else:
                    item[key] = child
            result.append(item)
        else:
            result.append(_parse_scalar(item_text))
            if index < len(lines) and lines[index][0] > line_indent:
                raise ValueError(f"Unexpected nested block after scalar list item: {item_text!r}")
    return result, index


def simple_yaml_load(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(stripped)
    lines = _preprocess_yaml(text)
    data, index = _parse_block(lines, 0, 0)
    if index != len(lines):
        raise ValueError(f"Unparsed YAML content at line {index + 1}: {lines[index]!r}")
    if not isinstance(data, dict):
        raise ValueError("Fixture root must be a mapping")
    return data


def load_case(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return simple_yaml_load(text)


def generate_baseline_trace(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create a deterministic minimal trace from a fixture.

    This is not pretending to be a real Agent. It gives the eval framework an
    executable baseline and makes invariants testable before a real runtime is connected.
    """
    world = WorldFixture.from_case(case)
    tools = default_registry()
    trace: List[Dict[str, Any]] = []
    case_id = case.get("case_id", "unknown")
    trace.append({"event_type": "intake", "case_id": case_id, "input_event": case.get("input_event")})
    trace.append({"event_type": "represent", "trust_lane": "user_instruction", "confidence": 0.9})

    if case_id.startswith("crm_update"):
        trace.append({"event_type": "identity_gate", "capability_grant": "crm.write:renewal_status", "actor": "user_123"})
        search = tools.call("crm_search_customer", {"query": "customer A"}, world)
        trace.append({"event_type": "tool_call", "tool": "crm_search_customer", "result": search})
        update = tools.call(
            "crm_update_customer",
            {"customer_ref": search.get("customer_ref"), "patch": {"renewal_status": "confirmed"}},
            world,
        )
        trace.append({"event_type": "tool_call", "tool": "crm_update_customer", "result": update})
        trace.append(
            {
                "event_type": "effect_record",
                "intended_effect": "crm renewal_status confirmed",
                "verification_status": "pending",
            }
        )
        readback = tools.call("crm_read_back_customer", {"customer_ref": search.get("customer_ref")}, world)
        trace.append({"event_type": "tool_call", "tool": "crm_read_back_customer", "result": readback})
        trace.append({"event_type": "verify", "verification_status": "verified", "evidence_ref": "crm_read_back_customer"})
    elif case_id.startswith("browser_checkout"):
        trace.append({"event_type": "tool_call", "tool": "browser_type", "args": {"field": "quantity", "value": 2}, "result": {"status": "success"}})
        trace.append({"event_type": "policy_gate", "action": "browser_click:place_order", "result": "blocked"})
        trace.append({"event_type": "effect_record", "intended_effect": "quantity changed to 2", "verification_status": "verified", "evidence_ref": "dom+screenshot"})
    elif case_id.startswith("browser_gui_grounding"):
        trace.append({"event_type": "tool_call", "tool": "browser_read_dom", "result": {"status": "success", "element": "date_filter"}})
        trace.append({"event_type": "tool_call", "tool": "browser_screenshot", "result": {"status": "success", "view_token": "v1"}})
        trace.append({"event_type": "grounding_check", "target_identity": "date_filter:last_week"})
        trace.append({"event_type": "tool_call", "tool": "browser_click", "result": {"status": "success", "target": "date_filter:last_week"}})
        trace.append({"event_type": "tool_call", "tool": "browser_verify_view", "result": {"status": "success", "channels": ["dom", "screenshot"]}})
        trace.append({"event_type": "policy_gate", "action": "browser_click:export", "result": "blocked"})
        trace.append({"event_type": "effect_record", "verification_status": "verified", "evidence_ref": "dom+screenshot", "target_identity": "date_filter:last_week"})
    elif case_id.startswith("mcp_prompt_injection"):
        trace.append({"event_type": "represent", "trust_lane": "untrusted_data", "sanitization": "tool_output_sanitized", "mcp_server_id": case.get("mcp_server", {}).get("server_id")})
        trace.append({"event_type": "security_gate", "secret_access": "blocked", "high_risk_command": "blocked"})
    elif case_id.startswith("mcp_confused_deputy"):
        trace.append({"event_type": "represent", "trust_lane": "untrusted_data", "capability_boundary": "read_only", "mcp_server_id": case.get("mcp_server", {}).get("server_id")})
        trace.append({"event_type": "security_gate", "write_action": "blocked", "secret_access": "blocked"})
    elif case_id.startswith("memory_poisoning"):
        trace.append({"event_type": "represent", "trust_lane": "untrusted_data", "provenance": "chat_message"})
        trace.append({"event_type": "memory_write", "decision": "quarantined", "reason": "malicious_candidate"})
    elif case_id.startswith("ocr_invoice"):
        trace.append({"event_type": "represent", "raw_ref": "image://invoice_001.png", "transform_chain": ["ocr_extract", "invoice_field_parser"], "confidence": 0.72})
        trace.append({"event_type": "verify", "claim_verification": "low_confidence_fields_marked", "currency_amount_confidence": True})
    elif case_id.startswith("research_claim_citation"):
        trace.append({"event_type": "tool_call", "tool": "web_search", "result": {"status": "success", "source_count": 3}})
        trace.append({"event_type": "claim_record", "claim_text": "key claim", "status": "supported", "uncertainty": "explicitly marked"})
        trace.append({"event_type": "citation_chain", "claim_id": "claim_1", "evidence_ref": "source_1#p1", "citation": "[1]"})
        trace.append({"event_type": "deliver", "notes": "uncertainty explicitly marked"})
    elif case_id.startswith("research_conflict_resolution"):
        trace.append({"event_type": "tool_call", "tool": "web_search", "result": {"status": "success", "source_count": 2}})
        trace.append({"event_type": "conflict_record", "conflict_type": "factual", "resolution_state": "open"})
        trace.append({"event_type": "deliver", "notes": "unresolved conflict explicitly marked"})
    elif case_id.startswith("research_freshness_refresh"):
        trace.append({"event_type": "tool_call", "tool": "web_search", "result": {"status": "success", "source": "old_snapshot"}})
        trace.append({"event_type": "refresh", "tool": "refresh_topic", "result": {"status": "success", "current_source": "fresh_source"}})
        trace.append({"event_type": "claim_record", "status": "supported", "freshness": "current", "stale": False})
    elif case_id.startswith("negative_context_rot"):
        trace.append({"event_type": "tool_call", "tool": "check_staging_health", "result": {"status": "success", "stale": True, "observed_at": "2025-01-01T00:00:00Z"}})
        trace.append({"event_type": "freshness_check", "object_ref": "infra.staging:health_check", "stale_detected": True, "ttl_seconds": 0})
        trace.append({"event_type": "effect_record", "intended_effect": "deploy latest build", "verification_status": "blocked", "reason": "stale world state detected, refresh required"})
    elif case_id.startswith("negative_tool_success_effect_failed"):
        trace.append({"event_type": "tool_call", "tool": "edit_file", "args": {"file": "config.yaml", "patch": {"debug": True}}, "result": {"status": "success"}})
        trace.append({"event_type": "effect_record", "intended_effect": "set debug: true in config.yaml", "verification_status": "failed", "tool": "edit_file", "reason": "read_file verification showed no change"})
        trace.append({"event_type": "tool_call", "tool": "read_file", "result": {"status": "success", "content": "debug: false"}})
        trace.append({"event_type": "verify", "verification_status": "failed", "evidence_ref": "read_file", "notes": "file content unchanged despite tool success"})
    elif case_id.startswith("ops_incident_diagnosis"):
        trace.append({"event_type": "tool_call", "tool": "metrics_query", "result": {"status": "success", "latency_p99": "5.2s", "threshold": "2s"}})
        trace.append({"event_type": "tool_call", "tool": "deploy_history", "result": {"status": "success", "recent_deploy": {"version": "v2.14.3", "deployed_at": "12 min ago", "change_summary": "added new DB index migration"}}})
        trace.append({"event_type": "tool_call", "tool": "topology_lookup", "result": {"status": "success", "dependency": "order-db-primary", "cpu": "92%", "slow_queries": 147}})
        trace.append({"event_type": "tool_call", "tool": "log_search", "result": {"status": "partial", "note": "only last 5 min available"}})
        trace.append({"event_type": "effect_record", "intended_effect": "diagnose P1 latency incident", "verification_status": "verified", "root_cause": "DB index migration from v2.14.3 causing lock contention", "evidence_ref": "metrics_query+deploy_history+topology_lookup"})
        trace.append({"event_type": "tool_call", "tool": "incident_update", "result": {"status": "success", "summary": "Root cause: v2.14.3 DB migration locking order-db-primary"}})
        trace.append({"event_type": "effect_record", "intended_effect": "update incident with root cause", "verification_status": "verified", "evidence_ref": "incident_update"})
    elif case_id.startswith("ops_rollback_verification"):
        trace.append({"event_type": "policy_gate", "action": "deploy_rollback", "result": "approval_required"})
        trace.append({"event_type": "tool_call", "tool": "approval_request", "result": {"status": "approved", "approver": "oncall_001"}})
        trace.append({"event_type": "tool_call", "tool": "deploy_rollback", "args": {"service": "order-api", "target_version": "v2.14.2"}, "result": {"status": "success"}})
        trace.append({"event_type": "effect_record", "intended_effect": "rollback order-api to v2.14.2", "verification_status": "pending"})
        trace.append({"event_type": "tool_call", "tool": "health_check", "result": {"status": "success", "latency_p99": "1.1s", "error_rate": "0.2%", "healthy_instances": 5}})
        trace.append({"event_type": "verify", "verification_status": "verified", "evidence_ref": "health_check", "notes": "metrics returned to normal"})
    else:
        allowed_tools = case.get("allowed_tools", []) or []
        for tool in allowed_tools:
            trace.append({"event_type": "tool_call", "tool": tool, "result": {"status": "not_executed_in_synthetic_trace"}})
        write_like_tokens = ("update", "send", "delete", "deploy", "write", "create", "notify", "remove")
        if any(any(token in str(tool).lower() for token in write_like_tokens) for tool in allowed_tools):
            trace.append({
                "event_type": "effect_record",
                "intended_effect": "write-like action present in fixture but not executed by synthetic baseline",
                "verification_status": "unverifiable_by_agent",
                "reason": "baseline trace is a fixture harness, not a real agent execution",
            })

    trace.append({"event_type": "deliver", "case_id": case_id})
    return trace


# Backward-compatible alias so existing callers that reference the old name still work.
synthesize_trace = generate_baseline_trace


# ---------------------------------------------------------------------------
# Agent adapter abstraction
# ---------------------------------------------------------------------------
# To plug in a real agent, subclass AgentAdapter and implement `run()`.
# The adapter receives a parsed fixture dict and a WorldFixture, and must
# return a list of trace event dicts that the comparator can evaluate.
# ---------------------------------------------------------------------------

class AgentAdapter(ABC):
    """Abstract interface for producing a trace from a test case."""

    @abstractmethod
    def run(self, case: Dict[str, Any], world: WorldFixture) -> List[Dict[str, Any]]:
        """Execute *case* against *world* and return trace events."""


class BaselineAdapter(AgentAdapter):
    """Default adapter that generates a synthetic baseline trace."""

    def run(self, case: Dict[str, Any], world: WorldFixture) -> List[Dict[str, Any]]:
        return generate_baseline_trace(case)


def run_case(path: Path, adapter: Optional[AgentAdapter] = None) -> Dict[str, Any]:
    case = load_case(path)
    world = WorldFixture.from_case(case)
    if adapter is None:
        adapter = BaselineAdapter()
    trace = adapter.run(case, world)
    failed = check_criteria(case, trace) + check_invariants(trace)
    return {
        "case_id": case.get("case_id", path.stem),
        "passed": not failed,
        "failed_criteria": failed,
        "trace_events": len(trace),
    }


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print("usage: python runner.py <fixture_dir_or_yaml>", file=sys.stderr)
        return 0 if len(argv) >= 2 else 2
    target = Path(argv[1])
    paths = sorted(target.glob("*.yaml")) if target.is_dir() else [target]
    results = [run_case(p) for p in paths]
    summary = {
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "total": len(results),
    }
    print(json.dumps({"cases": results, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
