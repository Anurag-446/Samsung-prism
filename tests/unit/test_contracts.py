"""Unit tests for public and internal data contracts."""

import pytest
from pydantic import ValidationError
from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    StepGroup,
    TroubleshootRequest,
    ValidationDeeplink,
)


def test_troubleshoot_request_validation():
    req = TroubleshootRequest(query="phone battery draining fast")
    assert req.query == "phone battery draining fast"
    assert req.siis_response is None

    with pytest.raises(ValidationError):
        TroubleshootRequest(query="")


def test_goal_validation_success():
    action = Action(
        name="Battery Protection Settings",
        description="It will optimize power saving mode performance",
        steps=[StepGroup(step="Tap Battery Protection in Settings")],
        category=CategoryEnum.AUTO,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.battery/BatteryProtectionActivity")
        ),
    )
    goal = Goal(
        goal="Follow these steps to perform this Battery Troubleshooting",
        title="Fix battery drain",
        score=0.95,
        actions=[action],
        query_variations=[
            "battery drains fast",
            "phone battery dropping quickly",
            "how to fix high battery drain",
            "battery issue troubleshooting",
            "my battery percentage drops fast",
            "power saving setup",
            "battery life fix galaxy",
            "galaxy phone battery draining rapidly",
        ],
    )
    assert goal.score == 0.95
    assert len(goal.actions) == 1
    assert len(goal.query_variations) == 8


def test_invalid_score_range():
    action = Action(
        name="Display Settings",
        description="It will adjust brightness level for comfort",
        steps=[StepGroup(step="Open Display Settings")],
        category=CategoryEnum.AUTO,
    )
    with pytest.raises(ValidationError):
        Goal(
            goal="Follow these steps to perform this Display Troubleshooting",
            title="Fix screen issue",
            score=1.5,  # Out of range > 1.0
            actions=[action],
            query_variations=["var1", "var2", "var3", "var4", "var5", "var6", "var7", "var8"],
        )
