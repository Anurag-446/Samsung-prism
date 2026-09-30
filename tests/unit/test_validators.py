"""Unit tests for URL leak, textual rule, deeplink integrity, and risk order validators."""

from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    actionCategory,
    Goal,
    StepGroup,
    ValidationDeepLink,
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
        actionName="Location Settings",
        description="It will enable location services accurately",
        stepGroups=[
            StepGroup(
                steps=["Toggle Location switch to ON"],
                validationDeeplink=ValidationDeepLink(
                    deeplink="bixby://com.samsung.android.settings.location/LocationSettingsActivity",
                    key="dummy"
                )
            )
        ],
        category=actionCategory.auto,
    )

    valid_goal = Goal(
        goal="Follow these steps to perform this Location Troubleshooting",
        title="Fix location accuracy",
        score=0.9,
        actions=[valid_action],
    )

    issues = validator.validate_goal(valid_goal)
    assert len(issues) == 0

    # Invalid title (> 3 words)
    invalid_title_goal = valid_goal.model_copy(
        update={"title": "Fix the location accuracy issue now"}
    )
    issues = validator.validate_goal(invalid_title_goal)
    assert any(i.code == "TITLE_WORD_COUNT_INVALID" for i in issues)


def test_deeplink_integrity_validator():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    validator = DeeplinkIntegrityValidator(catalog)

    # Fabricated deeplink
    fabricated_action = Action(
        actionName="Unknown Settings",
        description="It will open fake settings screen",
        stepGroups=[
            StepGroup(
                steps=["Tap unknown button"],
                validationDeeplink=ValidationDeepLink(
                    deeplink="bixby://com.samsung.fake.settings/FakeActivity",
                    key="dummy"
                )
            )
        ],
        category=actionCategory.auto,
    )

    goal = Goal(
        goal="Follow these steps to perform this Unknown Troubleshooting",
        title="Fix unknown issue",
        score=0.8,
        actions=[fabricated_action],
    )

    issues = validator.validate_goal(goal)
    assert any(i.code == "FABRICATED_DEEPLINK_REJECTED" for i in issues)


def test_risk_order_validator():
    validator = RiskOrderValidator()

    critical_action = Action(
        actionName="Reset Mobile Network Settings",
        description="It will reset all network parameters",
        stepGroups=[
            StepGroup(
                steps=["Tap Reset Network Settings"],
                validationDeeplink=ValidationDeepLink(
                    deeplink="bixby://com.samsung.android.settings.reset/ResetNetworkSettingsActivity",
                    key="dummy"
                )
            )
        ],
        category=actionCategory.critical,
    )

    auto_action = Action(
        actionName="Wi-Fi Settings",
        description="It will connect to wireless network",
        stepGroups=[
            StepGroup(
                steps=["Tap Wi-Fi Settings"],
                validationDeeplink=ValidationDeepLink(
                    deeplink="bixby://com.samsung.android.settings.wifi/WifiSettingsActivity",
                    key="dummy"
                )
            )
        ],
        category=actionCategory.auto,
    )

    # Invalid order: CRITICAL before AUTO
    bad_order_goal = Goal(
        goal="Follow these steps to perform this Network Troubleshooting",
        title="Fix network connection",
        score=0.85,
        actions=[critical_action, auto_action],
    )

    issues = validator.validate_goal(bad_order_goal)
    assert any(i.code == "CRITICAL_ORDER_VIOLATION" for i in issues)
