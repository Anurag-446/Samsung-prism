"""Contract-safe fallback generator for failure modes (M4-07)."""

from fixgraph.contracts.public import (
    Action,
    Goal,
    StepGroup,
    actionCategory,
)


def get_safe_fallback_goal(reason: str = "general_fallback") -> Goal:
    """Generate a contract-safe, schema-valid fallback Goal response."""
    title = "Troubleshoot unknown issue"
    desc = "It will guide you to manual support"

    # Needs to match StepGroup(steps=[...])
    step_groups = [
        StepGroup(steps=["Open the Samsung Members application", "Navigate to the Get Help section", "Contact customer support for assistance"])
    ]

    goal_stmt = "Follow these steps to perform this Support Troubleshooting"

    if reason == "no_evidence":
        title = "Issue not recognized"
        desc = "It will direct you to official support"
        goal_stmt = "Follow these steps to perform this Diagnostic Troubleshooting"
    elif reason == "provider_timeout" or reason == "provider_error":
        title = "Service currently unavailable"
        desc = "It will instruct you to try later"
        step_groups = [
            StepGroup(steps=["Check your internet connection status", "Wait for a few minutes", "Retry your troubleshooting request"])
        ]
        goal_stmt = "Follow these steps to perform this Service Troubleshooting"
    elif reason == "invalid_plan":
        title = "Safety validation failed"
        desc = "It will help contact a technician directly"
        goal_stmt = "Follow these steps to perform this Safety Troubleshooting"

    action = Action(
        actionName="Seek Manual Support",
        description=desc,
        stepGroups=step_groups,
        category=actionCategory.manual,
    )

    return Goal(
        goal=goal_stmt,
        title=title,
        score=0.1,
        actions=[action],
    )
