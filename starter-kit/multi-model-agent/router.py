# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from models import ModelProfile, ModelRole, RoutingDecision, TaskComplexity


# ---------------------------------------------------------------------------
# Default model catalogue — illustrative only
# ---------------------------------------------------------------------------

FAST_MODEL = ModelProfile(
    name="fast-model",
    reasoning_depth="none",
    cost_per_1k_tokens=0.001,
    max_context=200_000,
    strengths=["low-latency", "high-throughput", "tool-calling"],
)

BALANCED_MODEL = ModelProfile(
    name="balanced-model",
    reasoning_depth="standard",
    cost_per_1k_tokens=0.015,
    max_context=200_000,
    strengths=["general-purpose", "moderate-reasoning", "code-generation"],
)

REASONING_MODEL = ModelProfile(
    name="reasoning-model",
    reasoning_depth="extended",
    cost_per_1k_tokens=0.075,
    max_context=200_000,
    strengths=["deep-reasoning", "planning", "self-critique"],
)

DEFAULT_CATALOGUE: Dict[TaskComplexity, ModelProfile] = {
    TaskComplexity.SIMPLE: FAST_MODEL,
    TaskComplexity.MODERATE: BALANCED_MODEL,
    TaskComplexity.COMPLEX: REASONING_MODEL,
}


# ---------------------------------------------------------------------------
# Budget constraint
# ---------------------------------------------------------------------------

@dataclass
class BudgetConstraint:
    """Optional spending cap for a routing decision."""

    max_cost_usd: float
    prefer_cheapest: bool = False


# ---------------------------------------------------------------------------
# ModelRouter
# ---------------------------------------------------------------------------

class ModelRouter:
    """Routes tasks to appropriate models based on complexity and budget.

    Implements the *Adaptive Reasoning Router* pattern:
      User request -> Complexity assessment
        -> SIMPLE  : fast model, no thinking
        -> MODERATE : standard model, moderate thinking
        -> COMPLEX  : reasoning model, deep thinking

    See: paradigms/reasoning-model-integration.md § 模式 1 — Adaptive Reasoning Router
    See: paradigms/reasoning-model-integration.md § RouteLLM 与模型路由实践
    """

    def __init__(
        self,
        catalogue: Dict[TaskComplexity, ModelProfile] | None = None,
    ) -> None:
        self.catalogue = catalogue or dict(DEFAULT_CATALOGUE)

    # ---- public API --------------------------------------------------------

    def route(
        self,
        task_description: str,
        complexity: TaskComplexity,
        budget: Optional[BudgetConstraint] = None,
    ) -> RoutingDecision:
        """Select a model for *task_description* given its *complexity*.

        If *budget* is provided and the ideal model exceeds the budget,
        the router falls back to the cheapest available model (degradation
        strategy described in the decision tree under "Budget 受限").
        """
        model = self.catalogue[complexity]
        role = self._role_for_complexity(complexity)
        estimated_cost = self._estimate_cost(model, task_description)

        if budget and estimated_cost > budget.max_cost_usd:
            model, estimated_cost = self._downgrade(task_description, budget)
            reason = (
                f"Budget cap {budget.max_cost_usd:.4f} USD triggered downgrade "
                f"from {self.catalogue[complexity].name} to {model.name}"
            )
        else:
            reason = (
                f"Complexity={complexity.value} -> {model.name} "
                f"(reasoning_depth={model.reasoning_depth})"
            )

        return RoutingDecision(
            selected_model=model,
            role=role,
            reason=reason,
            estimated_cost=estimated_cost,
        )

    # ---- internals ---------------------------------------------------------

    @staticmethod
    def _role_for_complexity(complexity: TaskComplexity) -> ModelRole:
        mapping = {
            TaskComplexity.SIMPLE: ModelRole.EXECUTOR,
            TaskComplexity.MODERATE: ModelRole.EXECUTOR,
            TaskComplexity.COMPLEX: ModelRole.PLANNER,
        }
        return mapping[complexity]

    @staticmethod
    def _estimate_cost(model: ModelProfile, task_description: str) -> float:
        """Rough cost estimate based on input length heuristic.

        Real implementations would use historical trace data.
        """
        estimated_tokens = len(task_description.split()) * 2  # naive proxy
        return model.cost_per_1k_tokens * (estimated_tokens / 1000)

    def _downgrade(
        self,
        task_description: str,
        budget: BudgetConstraint,
    ) -> tuple[ModelProfile, float]:
        """Find the cheapest model that fits within *budget*."""
        candidates = sorted(
            self.catalogue.values(),
            key=lambda m: m.cost_per_1k_tokens,
        )
        for model in candidates:
            cost = self._estimate_cost(model, task_description)
            if cost <= budget.max_cost_usd:
                return model, cost
        # If even the cheapest exceeds budget, return it anyway with a warning cost.
        cheapest = candidates[0]
        return cheapest, self._estimate_cost(cheapest, task_description)
