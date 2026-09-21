"""Unit tests for URL leak, textual rule, deeplink integrity, and risk order validators."""

from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    StepGroup,
    ValidationDeeplink,
)
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.validation.deeplink_integrity import DeeplinkIntegrityValidator
from fixgraph.validation.sequencing import RiskOrderValidator
from fixgraph.validation.text_rules import TextualRuleValidator
from fixgraph.validation.url_hygiene import URLLeakValidator


def test_url_leak_validator():
    validator = URLLeakValidator()

    # Safe text with bixby URI
    assert len(validator.validate_text("Open Settings and tap Location permissions")) == 0

    # Leak cases
    assert len(validator.validate_text("Visit https://support.samsung.com for help")) > 0
    assert len(validator.validate_text("Go to www.google.com")) > 0
    assert len(validator.validate_text("Click [here](http://example.com)")) > 0
    assert len(validator.validate_text("Obfuscated h t t p : / / malicious.com")) > 0


def test_textual_rule_validator():
    validator = TextualRuleValidator()

    valid_action = Action(
        name="Location Settings",
        description="It will enable location services accurately",
        steps=[StepGroup(step="Toggle Location switch to ON")],
        category=CategoryEnum.AUTO,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.location/LocationSettingsActivity")
        ),
    )

    valid_goal = Goal(
        goal="Follow these steps to perform this Location Troubleshooting",
        title="Fix location accuracy",
        score=0.9,
        actions=[valid_action],
        query_variations=[f"var {i}" for i in range(8)],
    )

    issues = validator.validate_goal(valid_goal)
    assert len(issues) == 0

    # Invalid title (> 3 words)
    invalid_title_goal = valid_goal.model_copy(update={"title": "Fix the location accuracy issue now"})
    issues = validator.validate_goal(invalid_title_goal)
    assert any(i.code == "TITLE_WORD_COUNT_INVALID" for i in issues)


def test_deeplink_integrity_validator():
    catalog = load_deeplink_catalog(None)
    validator = DeeplinkIntegrityValidator(catalog)

    # Fabricated deeplink
    fabricated_action = Action(
        name="Unknown Settings",
        description="It will open fake settings screen",
        steps=[StepGroup(step="Tap unknown button")],
        category=CategoryEnum.AUTO,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.fake.settings/FakeActivity")
        ),
    )

    goal = Goal(
        goal="Follow these steps to perform this Unknown Troubleshooting",
        title="Fix unknown issue",
        score=0.8,
        actions=[fabricated_action],
        query_variations=[f"var {i}" for i in range(8)],
    )

    issues = validator.validate_goal(goal)
    assert any(i.code == "FABRICATED_DEEPLINK_REJECTED" for i in issues)


def test_risk_order_validator():
    validator = RiskOrderValidator()

    critical_action = Action(
        name="Reset Mobile Network Settings",
        description="It will reset all network parameters",
        steps=[StepGroup(step="Tap Reset Network Settings")],
        category=CategoryEnum.CRITICAL,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.reset/ResetNetworkSettingsActivity")
        ),
    )

    auto_action = Action(
        name="Wi-Fi Settings",
        description="It will connect to wireless network",
        steps=[StepGroup(step="Tap Wi-Fi Settings")],
        category=CategoryEnum.AUTO,
        deeplink=ValidationDeeplink(
            baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.wifi/WifiSettingsActivity")
        ),
    )

    # Invalid order: CRITICAL before AUTO
    bad_order_goal = Goal(
        goal="Follow these steps to perform this Network Troubleshooting",
        title="Fix network connection",
        score=0.85,
        actions=[critical_action, auto_action],
        query_variations=[f"var {i}" for i in range(8)],
    )

    issues = validator.validate_goal(bad_order_goal)
    assert any(i.code == "CRITICAL_ORDER_VIOLATION" for i in issues)
