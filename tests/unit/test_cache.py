"""Unit tests for semantic case signature, persistent cache store, and matcher."""

import os
import tempfile
from fixgraph.cache.matcher import TwoStageCacheMatcher
from fixgraph.cache.store import CaseCacheStore
from fixgraph.contracts.internal import SymptomAtom
from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    StepGroup,
    ValidationDeeplink,
)
from fixgraph.query.case_signature import CaseSignatureGenerator


def test_case_signature_paraphrase_equivalence():
    sig_gen = CaseSignatureGenerator()

    atom1 = SymptomAtom(
        device="Galaxy",
        domains=["battery protection"],
        symptoms=["battery_drain"],
        trigger="post_app_install",
    )
    atom2 = SymptomAtom(
        device="Galaxy",
        domains=["battery protection"],
        symptoms=["battery_drain"],
        trigger="post_app_install",
    )

    sig1 = sig_gen.generate_signature(atom1)
    sig2 = sig_gen.generate_signature(atom2)

    # Paraphrases collapse to the same canonical signature hash
    assert sig1.signature_hash == sig2.signature_hash


def test_case_cache_store_and_lookup():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        store = CaseCacheStore(db_path=db_path)
        sig_gen = CaseSignatureGenerator()

        atom = SymptomAtom(
            device="Galaxy",
            domains=["location"],
            symptoms=["location_inaccuracy"],
        )
        sig = sig_gen.generate_signature(atom)

        action = Action(
            name="Location Settings",
            description="It will enable location services accurately",
            steps=[StepGroup(step="Toggle Location to ON")],
            category=CategoryEnum.AUTO,
            deeplink=ValidationDeeplink(
                baseDeeplink=BaseDeeplink(uri="bixby://com.samsung.android.settings.location/LocationSettingsActivity")
            ),
        )

        goal = Goal(
            goal="Follow these steps to perform this Location Troubleshooting",
            title="Fix location accuracy",
            score=0.9,
            actions=[action],
            query_variations=[f"var {i}" for i in range(8)],
        )

        catalog_fp = "test_catalog_fp_123"

        # Write validated plan to cache
        store.put_validated_plan(
            signature_hash=sig.signature_hash,
            canonical_query=sig.canonical_query,
            query_embedding=[0.1] * 256,
            validated_plan_json=goal.model_dump_json(),
            catalog_fingerprint=catalog_fp,
        )

        matcher = TwoStageCacheMatcher(store=store, similarity_threshold=0.8)

        # Stage 1 lookup test
        entry, score, reason = matcher.lookup(sig, "fix location permissions", catalog_fp)
        assert entry is not None
        assert reason == "exact_signature_match"
        assert score == 1.0

    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            pass
