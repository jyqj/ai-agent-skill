# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from models import ModelProfile, ModelRole


# ---------------------------------------------------------------------------
# PlanStep — unit of work produced by the Planner
# ---------------------------------------------------------------------------

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNED = "replanned"


@dataclass
class PlanStep:
    """A single step in a Planner-generated execution plan.

    Mirrors the DAG task decomposition described in
    paradigms/reasoning-model-integration.md § 模式 2 — Planner-Executor with Budget Awareness.
    """

    step_id: int
    description: str
    tool: str
    args: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)  # step_ids this step depends on
    estimated_tokens: int = 0
    status: StepStatus = StepStatus.PENDING


# ---------------------------------------------------------------------------
# Planner — uses a reasoning model to decompose tasks
# ---------------------------------------------------------------------------

class Planner:
    """Generates a plan (list of PlanSteps) for a high-level goal.

    In production this would call a heavy reasoning model (Opus / o3-pro)
    with extended thinking enabled.  Here we provide the structural skeleton
    that shows how the Planner fits into the multi-model architecture.

    Role: ModelRole.PLANNER
    Reasoning need: HIGH (deep thinking)
    Cost sensitivity: LOW (called infrequently)
    """

    def __init__(self, model: ModelProfile) -> None:
        self.model = model
        self.role = ModelRole.PLANNER

    def plan(self, goal: str, context: Dict[str, Any] | None = None) -> List[PlanStep]:
        """Decompose *goal* into ordered PlanSteps.

        A real implementation would:
        1. Format a prompt with *goal* and *context*.
        2. Call the reasoning model with effort=high (extended thinking).
        3. Parse the structured output into PlanStep objects.

        Returns a placeholder plan for demonstration purposes.
        """
        # --- placeholder: real impl calls reasoning LLM ---
        return [
            PlanStep(
                step_id=1,
                description=f"Analyze requirements for: {goal}",
                tool="think",
                estimated_tokens=500,
            ),
            PlanStep(
                step_id=2,
                description="Execute primary action",
                tool="tool_call",
                depends_on=[1],
                estimated_tokens=200,
            ),
            PlanStep(
                step_id=3,
                description="Verify result against success criteria",
                tool="verify",
                depends_on=[2],
                estimated_tokens=300,
            ),
        ]


# ---------------------------------------------------------------------------
# Executor — uses a lightweight model to run tool calls
# ---------------------------------------------------------------------------

@dataclass
class ExecutionResult:
    step_id: int
    success: bool
    output: Any = None
    error: Optional[str] = None


class Executor:
    """Executes individual PlanSteps using a lightweight model.

    In production this would call a fast model (Haiku / Flash / o4-mini)
    with no extended thinking, optimised for tool-calling throughput.

    Role: ModelRole.EXECUTOR
    Reasoning need: LOW (no thinking)
    Cost sensitivity: HIGH (called frequently)
    """

    def __init__(self, model: ModelProfile) -> None:
        self.model = model
        self.role = ModelRole.EXECUTOR

    def execute(self, step: PlanStep) -> ExecutionResult:
        """Execute a single PlanStep.

        A real implementation would:
        1. Format a minimal prompt with step.description and step.args.
        2. Call the lightweight model (no extended thinking).
        3. Invoke the specified tool and capture the result.
        """
        # --- placeholder: real impl calls fast LLM + tool ---
        step.status = StepStatus.COMPLETED
        return ExecutionResult(
            step_id=step.step_id,
            success=True,
            output=f"[stub] executed: {step.description}",
        )


# ---------------------------------------------------------------------------
# plan_then_execute — the core orchestration loop
# ---------------------------------------------------------------------------

@dataclass
class PlanExecutionResult:
    """Aggregate result of a full plan-then-execute cycle."""

    goal: str
    steps: List[PlanStep]
    results: List[ExecutionResult]
    success: bool
    replan_count: int = 0
    summary: str = ""


def plan_then_execute(
    goal: str,
    planner: Planner,
    executor: Executor,
    max_replans: int = 2,
) -> PlanExecutionResult:
    """Run the Planner-Executor loop with optional replanning.

    Flow:
      1. Planner generates PlanSteps (reasoning model, extended thinking).
      2. Executor runs each step sequentially (lightweight model).
      3. On failure, Planner is re-invoked to generate an amended plan
         (up to *max_replans* times).

    This matches the "Planner-Executor with Budget Awareness" pattern from
    paradigms/reasoning-model-integration.md.  Budget tracking is omitted
    here for clarity — see router.py for the budget constraint mechanism.
    """
    replan_count = 0
    steps = planner.plan(goal)
    all_results: List[ExecutionResult] = []

    while True:
        for step in steps:
            if step.status != StepStatus.PENDING:
                continue

            step.status = StepStatus.RUNNING
            result = executor.execute(step)
            all_results.append(result)

            if not result.success:
                step.status = StepStatus.FAILED
                if replan_count < max_replans:
                    # Deviation exceeds threshold -> trigger replan
                    replan_count += 1
                    remaining_goals = [
                        s.description for s in steps if s.status == StepStatus.PENDING
                    ]
                    context = {
                        "failed_step": step.description,
                        "error": result.error,
                        "remaining": remaining_goals,
                    }
                    steps = planner.plan(goal, context=context)
                    break  # restart loop with new plan
                else:
                    return PlanExecutionResult(
                        goal=goal,
                        steps=steps,
                        results=all_results,
                        success=False,
                        replan_count=replan_count,
                        summary=f"Failed at step {step.step_id} after {replan_count} replans.",
                    )
        else:
            # All steps completed without break
            break

    success = all(r.success for r in all_results)
    return PlanExecutionResult(
        goal=goal,
        steps=steps,
        results=all_results,
        success=success,
        replan_count=replan_count,
        summary="All steps completed." if success else "Completed with failures.",
    )
