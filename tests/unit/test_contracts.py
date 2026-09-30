"""Unit tests for public and internal data contracts."""

import pytest
from pydantic import ValidationError

from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    actionCategory,
    Goal,
    StepGroup,
    TroubleshootRequest,
    ValidationDeepLink,
)


def test_troubleshoot_request_validation():
    req = TroubleshootRequest(query="phone battery draining fast")
    assert req.query == "phone battery draining fast"
    assert req.siis_response is None

    with pytest.raises(ValidationError):
        TroubleshootRequest(query="")


def test_goal_validation_success():
    action = Action(
        actionName="Battery Protection Settings",
        description="It will optimize power saving mode performance",
        stepGroups=[
            StepGroup(
                steps=["Tap Battery Protection in Settings"],
                validationDeeplink=ValidationDeepLink(
                    deeplink="bixby://com.samsung.android.settings.battery/BatteryProtectionActivity",
                    key="dummy"
                )
            )
        ],
        category=actionCategory.auto,
    )
    goal = Goal(
        goal="Follow these steps to perform this Battery Troubleshooting",
        title="Fix battery drain",
        score=0.95,
        actions=[action],
    )
    assert goal.score == 0.95
    assert len(goal.actions) == 1


