# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
"""
Multi-Model Agent — starter-kit entry point.

Demonstrates two patterns from paradigms/reasoning-model-integration.md:
  1. Adaptive Reasoning Router   — route tasks by complexity.
  2. Planner-Executor separation — reasoning model plans, lightweight model executes.

Usage (conceptual, not runnable):
    python main.py
"""
from __future__ import annotations

from models import TaskComplexity
from planner_executor import Executor, Planner, plan_then_execute
from router import FAST_MODEL, REASONING_MODEL, BudgetConstraint, ModelRouter


def demo_routing() -> None:
    """Show how the ModelRouter selects different models by complexity."""
    router = ModelRouter()

    print("=== Routing Demo ===\n")

    for complexity, description in [
        (TaskComplexity.SIMPLE, "Retrieve the current weather in Tokyo"),
        (TaskComplexity.MODERATE, "Summarise the top-5 HN posts and compare sentiments"),
        (TaskComplexity.COMPLEX, "Plan a migration from PostgreSQL to CockroachDB with zero downtime"),
    ]:
        decision = router.route(description, complexity)
        print(
            f"[{complexity.value:>8}] {decision.selected_model.name} "
            f"(role={decision.role.value}, est=${decision.estimated_cost:.4f})"
        )
        print(f"           reason: {decision.reason}\n")

    # Budget-constrained routing: forces downgrade
    budget = BudgetConstraint(max_cost_usd=0.0001)
    decision = router.route(
        "Design a fault-tolerant distributed consensus protocol",
        TaskComplexity.COMPLEX,
        budget=budget,
    )
    print(f"[budget-constrained] {decision.selected_model.name}")
    print(f"           reason: {decision.reason}\n")


def demo_planner_executor() -> None:
    """Show the Planner-Executor loop with separate models."""
    print("=== Planner-Executor Demo ===\n")

    planner = Planner(model=REASONING_MODEL)
    executor = Executor(model=FAST_MODEL)

    result = plan_then_execute(
        goal="Refactor the authentication module to use OAuth 2.0 PKCE flow",
        planner=planner,
        executor=executor,
        max_replans=2,
    )

    print(f"Goal   : {result.goal}")
    print(f"Success: {result.success}")
    print(f"Replans: {result.replan_count}")
    print(f"Summary: {result.summary}")
    print(f"Steps  : {len(result.steps)}")
    for step in result.steps:
        print(f"  [{step.step_id}] {step.status.value:>10} | {step.description}")
    print()


if __name__ == "__main__":
    demo_routing()
    demo_planner_executor()
