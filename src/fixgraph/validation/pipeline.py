"""Aggregated validation pipeline for total P0 compliance checking (M4-05)."""

from typing import List
from fixgraph.contracts.internal import ValidationIssue, ValidationReport
from fixgraph.contracts.public import Goal
from fixgraph.data.deeplink_catalog import DeeplinkCatalog
from fixgraph.validation.deeplink_integrity import DeeplinkIntegrityValidator
from fixgraph.validation.sequencing import RiskOrderValidator
from fixgraph.validation.text_rules import TextualRuleValidator
from fixgraph.validation.url_hygiene import URLLeakValidator


class ValidationPipeline:
    def __init__(self, catalog: DeeplinkCatalog):
        self.catalog = catalog
        self.url_validator = URLLeakValidator()
        self.text_validator = TextualRuleValidator()
        self.integrity_validator = DeeplinkIntegrityValidator(catalog)
        self.risk_validator = RiskOrderValidator()

    def validate(self, goal: Goal) -> ValidationReport:
        all_issues: List[ValidationIssue] = []

        # 1. Textual rule validation
        all_issues.extend(self.text_validator.validate_goal(goal))

        # 2. Deeplink catalog integrity validation
        all_issues.extend(self.integrity_validator.validate_goal(goal))

        # 3. Risk sequencing validation
        all_issues.extend(self.risk_validator.validate_goal(goal))

        # 4. URL hygiene leak validation across all visible text fields
        all_issues.extend(self.url_validator.validate_text(goal.goal, "goal.goal"))
        all_issues.extend(self.url_validator.validate_text(goal.title, "goal.title"))

        for idx, act in enumerate(goal.actions):
            all_issues.extend(self.url_validator.validate_text(act.name, f"goal.actions[{idx}].name"))
            all_issues.extend(
                self.url_validator.validate_text(act.description, f"goal.actions[{idx}].description")
            )
            for s_idx, step in enumerate(act.steps):
                all_issues.extend(
                    self.url_validator.validate_text(
                        step.step, f"goal.actions[{idx}].steps[{s_idx}].step"
                    )
                )

        for q_idx, q_var in enumerate(goal.query_variations):
            all_issues.extend(
                self.url_validator.validate_text(q_var, f"goal.query_variations[{q_idx}]")
            )

        errors = [i for i in all_issues if i.severity == "ERROR"]
        return ValidationReport(is_valid=len(errors) == 0, issues=all_issues)
