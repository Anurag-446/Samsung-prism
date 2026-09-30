"""Contract-safe fallback generator for failure modes (M4-07)."""

from fixgraph.contracts.public import (
    Action,
    CategoryEnum,
    Goal,
    StepGroup,
)


def get_safe_fallback_goal(reason: str = "general_fallback") -> Goal:
    """Generate a contract-safe, schema-valid fallback Goal response."""
    title = "Troubleshoot unknown issue"
    desc = "It will guide you to manual support"
    steps = [
        StepGroup(step="Open the Samsung Members application"),
        StepGroup(step="Navigate to the Get Help section"),
        StepGroup(step="Contact customer support for assistance"),
    ]
    goal_stmt = "Follow these steps to perform this Support Troubleshooting"

    if reason == "no_evidence":
        title = "Issue not recognized"
        desc = "It will direct you to official support"
        goal_stmt = "Follow these steps to perform this Diagnostic Troubleshooting"
    elif reason == "provider_timeout" or reason == "provider_error":
        title = "Service currently unavailable"
        desc = "It will instruct you to try later"
        steps = [
            StepGroup(step="Check your internet connection status"),
            StepGroup(step="Wait for a few minutes"),
            StepGroup(step="Retry your troubleshooting request"),
        ]
        goal_stmt = "Follow these steps to perform this Service Troubleshooting"
    elif reason == "invalid_plan":
        title = "Safety validation failed"
        desc = "It will help contact a technician directly"
        goal_stmt = "Follow these steps to perform this Safety Troubleshooting"

    action = Action(
        name="Seek Manual Support",
        description=desc,
        steps=steps,
        category=CategoryEnum.MANUAL,
        deeplink=None,
    )

    variations = [
        "How to contact Samsung support",
        "Get help with my Galaxy device",
        "Samsung Members troubleshooting guide",
        "Request technical assistance for issue",
        "Seek manual device support steps",
        "Find official customer service",
        "Steps to get expert diagnosis",
        "Contact help desk for Galaxy",
    ]

    return Goal(
        goal=goal_stmt,
        title=title,
        score=0.1,
        actions=[action],
        query_variations=variations,
    )
