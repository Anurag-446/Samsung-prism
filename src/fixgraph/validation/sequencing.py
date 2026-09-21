"""Risk and action sequencing validator enforcing safe execution ordering (P0-13)."""

from typing import List
from fixgraph.contracts.internal import ValidationIssue
from fixgraph.contracts.public import CategoryEnum, Goal


class RiskOrderValidator:
    def validate_goal(self, goal: Goal) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        found_critical = False

        for idx, action in enumerate(goal.actions):
            if action.category == CategoryEnum.CRITICAL:
                found_critical = True
            elif found_critical and action.category in (CategoryEnum.AUTO, CategoryEnum.MANUAL):
                # Non-critical action found AFTER a critical action!
                issues.append(
                    ValidationIssue(
                        code="CRITICAL_ORDER_VIOLATION",
                        message=f"Action '{action.name}' ({action.category}) is ordered after a critical action at index {idx}",
                        field=f"goal.actions[{idx}]",
                    )
                )
        return issues
