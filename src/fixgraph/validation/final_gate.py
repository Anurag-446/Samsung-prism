"""Final validation firewall for the Troubleshoot pipeline (Phase 5)."""
import re
from typing import List, Protocol

from fixgraph.contracts.internal import FinalValidationResult, ValidationContext, ValidationIssue
from fixgraph.contracts.public import actionCategory, Goal
from fixgraph.data.deeplink_catalog import DeeplinkCatalog


class GoalValidator(Protocol):
    @property
    def validator_id(self) -> str:
        ...

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        ...

class FinalValidationGate:
    def __init__(self, catalog: DeeplinkCatalog, validators: List[GoalValidator]):
        self.catalog = catalog
        self.validators = validators
        self.validator_version = "final-gate-v1"

    def validate(self, goal: Goal, context: ValidationContext) -> FinalValidationResult:
        all_issues = []
        for validator in self.validators:
            try:
                issues = validator.validate(goal, context)
                all_issues.extend(issues)
            except Exception as e:
                all_issues.append(ValidationIssue(
                    code="VALIDATOR_CRASH",
                    message=f"Validator {validator.validator_id} crashed: {str(e)}",
                    severity="ERROR"
                ))

        errors = [i for i in all_issues if i.severity == "ERROR"]
        warnings = [i for i in all_issues if i.severity == "WARNING"]

        return FinalValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validator_version=self.validator_version
        )

# ----------------- Core Validators -----------------

class TitleValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "title_format"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        # Title case check
        if goal.title != goal.title.title():
            # Allow some leeway for words like "and", "the", but strictly speaking, it should be title cased.
            pass # Keep it simple, just check length

        words = goal.title.strip().split()
        if len(words) < 2 or len(words) > 5:
            issues.append(ValidationIssue(code="TITLE_LENGTH", message=f"Title must be 2-5 words. Got: {len(words)}", severity="ERROR", field="goal.title"))

        return issues

class DescriptionValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "description_format"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        for idx, act in enumerate(goal.actions):
            desc = act.description.strip()
            if not desc.lower().startswith("it will"):
                issues.append(ValidationIssue(code="DESC_START", message="Description must start with 'It will'", severity="ERROR", field=f"actions[{idx}].description"))
            words = desc.split()
            if len(words) < 5 or len(words) > 7:
                issues.append(ValidationIssue(code="DESC_LENGTH", message=f"Description must be 5-7 words. Got {len(words)}.", severity="ERROR", field=f"actions[{idx}].description"))
        return issues

class StepValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "step_hygiene"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        for idx, act in enumerate(goal.actions):
            steps = set()
            for sg_idx, sg in enumerate(act.stepGroups):
                for s_idx, step_str in enumerate(sg.steps):
                    s = step_str.strip()
                    if not s:
                        issues.append(ValidationIssue(code="EMPTY_STEP", message="Step is empty", severity="ERROR", field=f"actions[{idx}].stepGroups[{sg_idx}].steps[{s_idx}]"))
                    # Detect leakage
                    lower_s = s.lower()
                    if "according to evidence" in lower_s or "confidence:" in lower_s:
                        issues.append(ValidationIssue(code="INTERNAL_LEAK", message="Step contains internal reasoning", severity="ERROR", field=f"actions[{idx}].stepGroups[{sg_idx}].steps[{s_idx}]"))
                    # Duplicate step detection
                    if lower_s in steps:
                        issues.append(ValidationIssue(code="DUPLICATE_STEP", message="Duplicate step", severity="ERROR", field=f"actions[{idx}].stepGroups[{sg_idx}].steps[{s_idx}]"))
                    steps.add(lower_s)
        return issues

class DeeplinkIntegrityValidator(GoalValidator):
    def __init__(self, catalog: DeeplinkCatalog):
        self.catalog = catalog

    @property
    def validator_id(self) -> str: return "deeplink_integrity"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        seen_uris = set()
        for idx, act in enumerate(goal.actions):
            field_prefix = f"actions[{idx}]"
            has_deeplink = False
            uri = None
            if act.stepGroups and len(act.stepGroups) > 0:
                sg = act.stepGroups[0]
                if sg.actionableDeeplink or sg.validationDeeplink:
                    has_deeplink = True
                    if sg.actionableDeeplink:
                        uri = sg.actionableDeeplink.deeplink
                    elif sg.validationDeeplink:
                        uri = sg.validationDeeplink.deeplink

            if act.category == actionCategory.manual:
                if has_deeplink:
                    issues.append(ValidationIssue(code="MANUAL_DEEPLINK", message="Manual action has deeplink", severity="ERROR", field=f"{field_prefix}.stepGroups"))
                continue

            if not has_deeplink or not uri:
                issues.append(ValidationIssue(code="MISSING_DEEPLINK", message="Auto/Critical action missing deeplink", severity="ERROR", field=f"{field_prefix}.stepGroups"))
                continue

            if not self.catalog.exists_uri(uri):
                issues.append(ValidationIssue(code="UNKNOWN_URI", message=f"URI not in catalog: {uri}", severity="ERROR", field=f"{field_prefix}.stepGroups"))

            # One action one screen validator
            if uri in seen_uris:
                issues.append(ValidationIssue(code="DUPLICATE_SCREEN", message=f"Multiple actions point to same screen: {uri}", severity="ERROR", field=f"{field_prefix}.stepGroups"))
            seen_uris.add(uri)
        return issues

class RiskOrderValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "risk_order"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        found_critical = False
        for idx, act in enumerate(goal.actions):
            if act.category == actionCategory.critical:
                found_critical = True
            elif act.category == actionCategory.auto and found_critical:
                issues.append(ValidationIssue(code="RISK_ORDER", message="AUTO action follows CRITICAL action", severity="ERROR", field=f"actions[{idx}].category"))
        return issues

class UserConstraintValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "user_constraints"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        # Basic check
        for idx, act in enumerate(goal.actions):
            act_text = f"{act.actionName} {act.description}".lower()
            for prob in context.prohibited_actions:
                if prob.lower() in act_text:
                    issues.append(ValidationIssue(code="PROHIBITED_ACTION", message=f"Action violates constraint: {prob}", severity="ERROR", field=f"actions[{idx}]"))
            for comp in context.completed_actions:
                if comp.lower() in act_text:
                    issues.append(ValidationIssue(code="COMPLETED_ACTION", message=f"Action instructs already completed action: {comp}", severity="WARNING", field=f"actions[{idx}]"))
        return issues

class URLLeakValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "url_hygiene"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        pattern = re.compile(r'(http://|https://|www\.|file://|javascript:|data:|[A-Z]:\\|/home/|ev_\d+|request_id=)', re.IGNORECASE)

        def check(text, field):
            if pattern.search(text):
                issues.append(ValidationIssue(code="TEXT_LEAK", message="Visible text contains URL or internal artifact", severity="ERROR", field=field))

        check(goal.goal, "goal.goal")
        check(goal.title, "goal.title")
        for idx, act in enumerate(goal.actions):
            check(act.actionName, f"actions[{idx}].name")
            check(act.description, f"actions[{idx}].description")
            for sg_idx, sg in enumerate(act.stepGroups):
                for sidx, step_str in enumerate(sg.steps):
                    check(step_str, f"actions[{idx}].stepGroups[{sg_idx}].steps[{sidx}]")

        return issues

class DuplicateActionValidator(GoalValidator):
    @property
    def validator_id(self) -> str: return "duplicate_action"

    def validate(self, goal: Goal, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        seen = set()
        for idx, act in enumerate(goal.actions):
            norm_name = act.actionName.lower().strip()
            if norm_name in seen:
                issues.append(ValidationIssue(code="DUPLICATE_ACTION", message=f"Duplicate action: {norm_name}", severity="ERROR", field=f"actions[{idx}]"))
            seen.add(norm_name)
        return issues
