"""Contract-safe fallback generator for failure modes (M4-07)."""

from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    ResultTypes,
    StepGroup,
    ValidationDeeplink,
)


def get_safe_fallback_goal(reason: str = "general_fallback") -> Goal:
    """Generate a contract-safe, schema-valid fallback Goal response."""
    action = Action(
        name="Display Settings",
        description="It will optimize general device screen settings",
        steps=[
            StepGroup(step="Open Settings on your Galaxy device"),
            StepGroup(step="Tap Display options menu"),
            StepGroup(step="Verify brightness and screen settings"),
        ],
        category=CategoryEnum.AUTO,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(
                uri="bixby://com.samsung.android.settings.display/DisplaySettingsActivity"
            ),
            resultTypes=[ResultTypes(type="DEFAULT")],
        ),
    )

    variations = [
        "How to open display settings on Galaxy",
        "Troubleshoot general device screen issue",
        "Galaxy display settings configuration guide",
        "Fix screen settings on Samsung phone",
        "Device settings inspection guide",
        "Steps to check display options",
        "Galaxy screen configuration options",
        "Check device display settings",
    ]

    return Goal(
        goal="Follow these steps to perform this Display Troubleshooting",
        title="Fix display issue",
        score=0.5,
        actions=[action],
        query_variations=variations,
    )
