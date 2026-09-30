"""Risk and action sequencing validator enforcing safe execution ordering (P0-13)."""

from typing import List

from fixgraph.contracts.internal import ValidationIssue
from fixgraph.contracts.public import actionCategory, Goal


class RiskOrderValidator:
    def validate_goal(self, goal: Goal) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        found_critical = False

        for idx, action in enumerate(goal.actions):
            if action.category == actionCategory.critical:
                found_critical = True
            elif found_critical and action.category in (actionCategory.auto, actionCategory.manual):
                # Non-critical action found AFTER a critical action!
                issues.append(
                    ValidationIssue(
                        code="CRITICAL_ORDER_VIOLATION",
                        message=f"Action '{action.actionName}' ({action.category}) is ordered after a critical action at index {idx}",
                        field=f"goal.actions[{idx}]",
                    )
                )
        return issues
