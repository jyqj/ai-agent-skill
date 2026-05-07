# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ModelRole(Enum):
    """Maps to multi-model architecture roles in paradigms/reasoning-model-integration.md."""

    PLANNER = "planner"  # Heavy reasoning model — DAG task decomposition
    EXECUTOR = "executor"  # Lightweight model — tool call execution
    CRITIC = "critic"  # Mid/heavy reasoning model — result review, quality assessment
    ROUTER = "router"  # Lightweight model or rule engine — complexity assessment


class TaskComplexity(Enum):
    """Complexity tiers driving model selection in the routing decision tree."""

    SIMPLE = "simple"  # Single-step, no or single tool — fast model, no extended thinking
    MODERATE = "moderate"  # Multi-step but structured — standard model, moderate thinking
    COMPLEX = "complex"  # Multi-step with dependencies, needs verification — reasoning model


@dataclass
class ModelProfile:
    """Describes a model's capabilities and cost characteristics.

    Mirrors the tiered reasoning architecture:
      SIMPLE  -> fast (Haiku / Flash / o4-mini)
      MODERATE -> balanced (Sonnet / GPT-4o)
      COMPLEX  -> reasoning (Opus / o3-pro)
    """

    name: str
    reasoning_depth: str  # "none" | "standard" | "extended"
    cost_per_1k_tokens: float  # USD, output tokens
    max_context: int  # token window size
    strengths: List[str] = field(default_factory=list)


@dataclass
class RoutingDecision:
    """Result of the router selecting a model for a given task.

    See: paradigms/reasoning-model-integration.md § RouteLLM 与模型路由实践
    """

    selected_model: ModelProfile
    role: ModelRole
    reason: str
    estimated_cost: float  # USD, rough estimate for the task
