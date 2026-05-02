# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

try:
    from world_fixture import WorldFixture
except ImportError:  # pragma: no cover
    from .world_fixture import WorldFixture


ToolFn = Callable[[Dict[str, Any], WorldFixture], Dict[str, Any]]


@dataclass
class MockToolRegistry:
    tools: Dict[str, ToolFn] = field(default_factory=dict)
    calls: List[Dict[str, Any]] = field(default_factory=list)

    def register(self, name: str, fn: ToolFn) -> None:
        self.tools[name] = fn

    def call(self, name: str, args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        if name not in self.tools:
            raise KeyError(f"unknown tool: {name}")
        result = self.tools[name](args, world)
        self.calls.append({"tool": name, "args": args, "result": result})
        return result



def default_registry() -> MockToolRegistry:
    registry = MockToolRegistry()

    def crm_search_customer(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        for ref in world.refs():
            if ref.startswith("crm.customer:"):
                return {"customer_ref": ref, "evidence_ref": "world_fixture"}
        return {"customer_ref": None, "error": "not_found"}

    def crm_update_customer(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        ref = args.get("customer_ref") or "crm.customer:customer_a"
        patch = args.get("patch") or {"renewal_status": "confirmed"}
        state = world.update(ref, patch)
        return {"status": "success", "object_ref": ref, "state": state}

    def crm_read_back_customer(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        ref = args.get("customer_ref") or "crm.customer:customer_a"
        return {"object_ref": ref, "state": world.read(ref)}

    def browser_click(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        target = args.get("target")
        if target in {"place_order", "export"}:
            return {"status": "blocked", "reason": "unsafe_action", "target": target}
        return {"status": "success", "target": target}

    def browser_type(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        return {"status": "success", "field": args.get("field"), "value": args.get("value")}

    def passthrough(args: Dict[str, Any], world: WorldFixture) -> Dict[str, Any]:
        return {"status": "success", "args": args}

    for name, fn in {
        "crm_search_customer": crm_search_customer,
        "crm_update_customer": crm_update_customer,
        "crm_read_back_customer": crm_read_back_customer,
        "browser_click": browser_click,
        "browser_type": browser_type,
        "browser_read_dom": passthrough,
        "browser_screenshot": passthrough,
        "browser_read_network": passthrough,
        "browser_verify_view": passthrough,
        "mcp_issue_reader": passthrough,
        "mcp_resource_reader": passthrough,
        "local_search": passthrough,
        "answer_writer": passthrough,
        "ocr_extract": passthrough,
        "invoice_field_parser": passthrough,
        "highlight_low_confidence_regions": passthrough,
        "web_search": passthrough,
        "open_url": passthrough,
        "read_pdf": passthrough,
        "bind_citation": passthrough,
        "compare_claims": passthrough,
        "refresh_topic": passthrough,
        "memory_read": passthrough,
        "memory_write": passthrough,
    }.items():
        registry.register(name, fn)
    return registry
