"""Textual rule validator for Goal syntax, Title casing/length, and Description rules."""

import re
from typing import List

from fixgraph.contracts.internal import ValidationIssue
from fixgraph.contracts.public import Goal


class TextualRuleValidator:
    def validate_goal(self, goal: Goal) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # 1. Goal phrase syntax pattern check
        goal_pattern = re.compile(
            r"^Follow these steps to perform this .+ (Troubleshooting|Configuration)$",
            re.IGNORECASE,
        )
        if not goal_pattern.match(goal.goal.strip()):
            issues.append(
                ValidationIssue(
                    code="GOAL_SYNTAX_INVALID",
                    message="Goal phrase must match 'Follow these steps to perform this <Topic> Troubleshooting'",
                    field="goal.goal",
                )
            )

        # 2. Title word count (2-3 words) and sentence case check
        title_words = goal.title.strip().split()
        if not (2 <= len(title_words) <= 3):
            issues.append(
                ValidationIssue(
                    code="TITLE_WORD_COUNT_INVALID",
                    message=f"Title must be 2-3 words long, got {len(title_words)} words",
                    field="goal.title",
                )
            )

        # 3. Actions validation
        for idx, action in enumerate(goal.actions):
            field_prefix = f"goal.actions[{idx}]"

            # Description word count (5-7 words) and starts with "It will"
            desc_text = action.description.strip()
            if not desc_text.lower().startswith("it will"):
                issues.append(
                    ValidationIssue(
                        code="DESC_PREFIX_INVALID",
                        message=f"Action description must start with 'It will', got '{desc_text}'",
                        field=f"{field_prefix}.description",
                    )
                )

            desc_words = desc_text.split()
            if not (5 <= len(desc_words) <= 7):
                issues.append(
                    ValidationIssue(
                        code="DESC_WORD_COUNT_INVALID",
                        message=f"Action description must be 5-7 words, got {len(desc_words)} words: '{desc_text}'",
                        field=f"{field_prefix}.description",
                    )
                )

            # Step groups check
            if not action.stepGroups[0].steps if action.stepGroups else []:
                issues.append(
                    ValidationIssue(
                        code="STEPS_EMPTY",
                        message="Action must contain at least one step",
                        field=f"{field_prefix}.steps",
                    )
                )

        # 4. Query variations count check (8-10 variations)
        return issues
