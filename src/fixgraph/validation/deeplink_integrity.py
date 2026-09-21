"""Deeplink integrity validator prohibiting fabricated URIs (P0-06, P0-07, P0-12)."""

from typing import List
from fixgraph.contracts.internal import ValidationIssue
from fixgraph.contracts.public import CategoryEnum, Goal
from fixgraph.data.deeplink_catalog import DeeplinkCatalog


class DeeplinkIntegrityValidator:
    def __init__(self, catalog: DeeplinkCatalog):
        self.catalog = catalog

    def validate_goal(self, goal: Goal) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for idx, action in enumerate(goal.actions):
            field_prefix = f"goal.actions[{idx}]"

            if action.category == CategoryEnum.MANUAL:
                # Manual actions MUST NOT carry an actionable deeplink (P0-12)
                if action.deeplink is not None:
                    issues.append(
                        ValidationIssue(
                            code="MANUAL_ACTION_DEEPLINK_PROHIBITED",
                            message=f"Manual category action '{action.name}' must have deeplink = None",
                            field=f"{field_prefix}.deeplink",
                        )
                    )
            else:
                # Auto and critical actions MUST carry a valid, existing catalog deeplink (P0-06)
                if action.deeplink is None or not action.deeplink.baseDeeplink.uri:
                    issues.append(
                        ValidationIssue(
                            code="MISSING_DEEPLINK",
                            message=f"Action '{action.name}' with category '{action.category}' requires a catalog deeplink",
                            field=f"{field_prefix}.deeplink",
                        )
                    )
                else:
                    uri = action.deeplink.baseDeeplink.uri
                    if not self.catalog.exists_uri(uri):
                        issues.append(
                            ValidationIssue(
                                code="FABRICATED_DEEPLINK_REJECTED",
                                message=f"Deeplink URI '{uri}' does not exist in the official catalog",
                                field=f"{field_prefix}.deeplink.baseDeeplink.uri",
                            )
                        )
        return issues
