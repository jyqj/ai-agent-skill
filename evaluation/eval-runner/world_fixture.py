# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional


@dataclass
class WorldObject:
    object_ref: str
    state: Dict[str, Any]
    observed_at: Optional[str] = None
    freshness_ttl: Optional[str] = None


@dataclass
class WorldFixture:
    objects: Dict[str, WorldObject] = field(default_factory=dict)

    @classmethod
    def from_case(cls, case: Dict[str, Any]) -> "WorldFixture":
        fixture = cls()
        for item in case.get("world_state", []) or []:
            ref = item.get("object_ref")
            if ref:
                fixture.objects[ref] = WorldObject(
                    object_ref=ref,
                    state=dict(item.get("state", {}) or {}),
                    observed_at=item.get("observed_at"),
                    freshness_ttl=item.get("freshness_ttl"),
                )
        return fixture

    def read(self, object_ref: str) -> Dict[str, Any]:
        if object_ref not in self.objects:
            raise KeyError(f"unknown world object: {object_ref}")
        return dict(self.objects[object_ref].state)

    def update(self, object_ref: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        if object_ref not in self.objects:
            self.objects[object_ref] = WorldObject(object_ref=object_ref, state={})
        self.objects[object_ref].state.update(patch)
        return dict(self.objects[object_ref].state)

    def refs(self) -> Iterable[str]:
        return self.objects.keys()
