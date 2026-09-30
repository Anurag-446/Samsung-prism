import pytest

from fixgraph.contracts.internal import CaseSignature, ValidationContext
from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    StepGroup,
    ValidationDeeplink,
)
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.validation.final_gate import (
    DeeplinkIntegrityValidator,
    DescriptionValidator,
    FinalValidationGate,
    RiskOrderValidator,
    StepValidator,
    TitleValidator,
    URLLeakValidator,
)


@pytest.fixture
def mock_catalog():
    return DeeplinkCatalog(records=[DeeplinkRecord(
        record_id="1",
        uri="bixby://com.samsung.android.settings.wifi/WifiSettingsActivity",
        name="Wifi Settings",
        description="Settings for Wifi"
    )])

@pytest.fixture
def gate(mock_catalog):
    return FinalValidationGate(
        catalog=mock_catalog,
        validators=[
            TitleValidator(),
            DescriptionValidator(),
            StepValidator(),
            DeeplinkIntegrityValidator(mock_catalog),
            URLLeakValidator(),
            RiskOrderValidator()
        ]
    )

@pytest.fixture
def val_ctx():
    return ValidationContext(
        request_id="test",
        original_query_hash="hash",
        case_signature=CaseSignature(
            signature_hash="sig", canonical_string="can", device_family="Galaxy",
            domains=[], symptoms=[], negated_symptoms=[], prohibited_actions=[],
            completed_actions=[], entities={}
        ),
        catalog_fingerprint="fp",
        pipeline_fingerprint="pfp"
    )

def test_compiler_blocks_url_leak(gate, val_ctx):
    bad_goal = Goal(
        goal="Follow these steps to perform this Troubleshooting",
        title="Fix Issue",
        score=0.9,
        actions=[Action(
            name="Check URL",
            description="It will check http://malicious.com",
            steps=[StepGroup(step="Click link")],
            category=CategoryEnum.MANUAL,
            deeplink=None
        )],
        query_variations=["var 1", "var 2", "var 3", "var 4", "var 5", "var 6", "var 7", "var 8"]
    )
    result = gate.validate(bad_goal, val_ctx)
    assert not result.valid
    assert any(e.code == "TEXT_LEAK" for e in result.errors)

def test_compiler_blocks_unauthorized_deeplink(gate, val_ctx):
    bad_goal = Goal(
        goal="Follow these steps to perform this Troubleshooting",
        title="Fix Issue",
        score=0.9,
        actions=[Action(
            name="Open Settings",
            description="It will open the settings menu",
            steps=[StepGroup(step="Do this")],
            category=CategoryEnum.AUTO,
            deeplink=ValidationDeeplink(baseDeeplink=BaseDeeplink(uri="bixby://fake/uri"))
        )],
        query_variations=["var 1", "var 2", "var 3", "var 4", "var 5", "var 6", "var 7", "var 8"]
    )
    result = gate.validate(bad_goal, val_ctx)
    assert not result.valid
    assert any(e.code == "UNKNOWN_URI" for e in result.errors)

def test_compiler_blocks_risk_inversion(gate, val_ctx):
    bad_goal = Goal(
        goal="Follow these steps to perform this Troubleshooting",
        title="Fix Issue",
        score=0.9,
        actions=[
            Action(
                name="Critical Reset",
                description="It will reset all data correctly",
                steps=[StepGroup(step="Do this")],
                category=CategoryEnum.CRITICAL,
                deeplink=ValidationDeeplink(baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.wifi/WifiSettingsActivity"))
            ),
            Action(
                name="Auto Setting",
                description="It will open the settings menu",
                steps=[StepGroup(step="Do that")],
                category=CategoryEnum.AUTO,
                deeplink=ValidationDeeplink(baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.wifi/WifiSettingsActivity")) # Intentionally using same just to check risk order
            )
        ],
        query_variations=["var 1", "var 2", "var 3", "var 4", "var 5", "var 6", "var 7", "var 8"]
    )
    result = gate.validate(bad_goal, val_ctx)
    assert not result.valid
    assert any(e.code == "RISK_ORDER" for e in result.errors)

