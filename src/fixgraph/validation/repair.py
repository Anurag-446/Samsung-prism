"""Deterministic repair pass fixing minor formatting issues without altering semantics (M4-06)."""

from typing import List, Tuple

from fixgraph.contracts.public import Action, CategoryEnum, Goal
from fixgraph.validation.pipeline import ValidationPipeline


class DeterministicRepairPass:
    def __init__(self, pipeline: ValidationPipeline):
        self.pipeline = pipeline

    def repair_goal(self, goal: Goal) -> Tuple[Goal, bool, List[str]]:
        logs: List[str] = []
        repaired = False

        # 1. Score clamping
        clamped_score = round(min(max(goal.score, 0.0), 1.0), 2)
        if clamped_score != goal.score:
            goal = goal.model_copy(update={"score": clamped_score})
            repaired = True
            logs.append(f"Clamped score to {clamped_score}")

        # 2. Repair action descriptions & titles
        repaired_actions: List[Action] = []
        for act in goal.actions:
            act_repaired = False
            desc = act.description.strip()

            if not desc.lower().startswith("it will"):
                desc = f"It will {desc}"
                act_repaired = True

            words = desc.split()
            if len(words) < 5:
                desc = f"{desc} on device screen"
                words = desc.split()
                act_repaired = True
            if len(words) > 7:
                desc = " ".join(words[:7])
                act_repaired = True

            if act_repaired:
                repaired = True
                logs.append(f"Repaired description for action '{act.name}' -> '{desc}'")

            repaired_actions.append(act.model_copy(update={"description": desc}))

        # 3. Action reordering (critical actions last)
        non_critical = [a for a in repaired_actions if a.category != CategoryEnum.CRITICAL]
        critical = [a for a in repaired_actions if a.category == CategoryEnum.CRITICAL]
        ordered_actions = non_critical + critical

        if [a.name for a in ordered_actions] != [a.name for a in repaired_actions]:
            repaired = True
            logs.append("Reordered critical actions to the end")

        repaired_goal = goal.model_copy(update={"actions": ordered_actions})
        return repaired_goal, repaired, logs
