"""Deeplink integrity validator prohibiting fabricated URIs (P0-06, P0-07, P0-12)."""

from typing import List

from fixgraph.contracts.internal import ValidationIssue
from fixgraph.contracts.public import actionCategory, Goal
from fixgraph.data.deeplink_catalog import DeeplinkCatalog


class DeeplinkIntegrityValidator:
    def __init__(self, catalog: DeeplinkCatalog):
        self.catalog = catalog

    def validate_goal(self, goal: Goal) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for idx, action in enumerate(goal.actions):
            field_prefix = f"goal.actions[{idx}]"
            has_deeplink = False
            uri = None
            if action.stepGroups and len(action.stepGroups) > 0:
                sg = action.stepGroups[0]
                if sg.actionableDeeplink or sg.validationDeeplink:
                    has_deeplink = True
                    if sg.actionableDeeplink:
                        uri = sg.actionableDeeplink.deeplink
                    elif sg.validationDeeplink:
                        uri = sg.validationDeeplink.deeplink

            if action.category == actionCategory.manual:
                # Manual actions MUST NOT carry an actionable deeplink (P0-12)
                if has_deeplink:
                    issues.append(
                        ValidationIssue(
                            code="MANUAL_ACTION_DEEPLINK_PROHIBITED",
                            message=f"Manual category action '{action.actionName}' must have deeplink = None",
                            field=f"{field_prefix}.stepGroups",
                        )
                    )
            else:
                # Auto and critical actions MUST carry a valid, existing catalog deeplink (P0-06)
                if not has_deeplink or not uri:
                    issues.append(
                        ValidationIssue(
                            code="MISSING_DEEPLINK",
                            message=f"Action '{action.actionName}' with category '{action.category}' requires a catalog deeplink",
                            field=f"{field_prefix}.stepGroups",
                        )
                    )
                else:
                    if not self.catalog.exists_uri(uri):
                        issues.append(
                            ValidationIssue(
                                code="FABRICATED_DEEPLINK_REJECTED",
                                message=f"Deeplink URI '{uri}' does not exist in the official catalog",
                                field=f"{field_prefix}.stepGroups.deeplink",
                            )
                        )
        return issues
