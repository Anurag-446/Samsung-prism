"""Cache invalidation and compatibility checking module (M5-05)."""

from fixgraph.contracts.internal import (
    CacheEntry,
    CaseSignature,
    CompatibilityResult,
    PipelineFingerprint,
)


class CacheCompatibilityValidator:
    def validate_pipeline(self, entry: CacheEntry, runtime_fingerprint: PipelineFingerprint) -> CompatibilityResult:
        failures = []
        reasons = []

        # Must match exactly for safe reuse
        if entry.pipeline_fingerprint.catalog_sha256 != runtime_fingerprint.catalog_sha256:
            failures.append("catalog_mismatch")

        if entry.pipeline_fingerprint.schema_sha256 != runtime_fingerprint.schema_sha256:
            failures.append("schema_mismatch")

        if entry.pipeline_fingerprint.embedder_id != runtime_fingerprint.embedder_id:
            failures.append("embedder_mismatch")

        if entry.pipeline_fingerprint.embedding_dimension != runtime_fingerprint.embedding_dimension:
            failures.append("dimension_mismatch")

        if entry.pipeline_fingerprint.validator_version != runtime_fingerprint.validator_version:
            failures.append("validator_version_mismatch")

        if not failures:
            reasons.append("pipeline_compatible")

        return CompatibilityResult(
            compatible=len(failures) == 0,
            score=1.0 if not failures else 0.0,
            reasons=reasons,
            hard_failures=failures
        )

    def validate_semantics(self, cached_signature: CaseSignature, current_signature: CaseSignature) -> CompatibilityResult:
        failures = []
        reasons = []

        if current_signature.device_family != cached_signature.device_family:
            failures.append("device_family_conflict")

        # Hard conflict if current constraint prohibits something
        for action in current_signature.prohibited_actions:
            if action not in cached_signature.prohibited_actions:
                failures.append("prohibited_action_conflict")

        for neg in current_signature.negated_symptoms:
            if neg not in cached_signature.negated_symptoms:
                failures.append("negated_symptom_conflict")

        # Must have same symptoms broadly (cache entry must address what user is asking)
        for sym in current_signature.symptoms:
            if sym not in cached_signature.symptoms:
                failures.append("symptom_conflict")

        # Same primary domain required for semantic reuse
        if current_signature.domains and cached_signature.domains:
            if current_signature.domains[0] != cached_signature.domains[0]:
                failures.append("primary_domain_conflict")

        if not failures:
            reasons.append("semantic_compatible")

        return CompatibilityResult(
            compatible=len(failures) == 0,
            score=1.0 if not failures else 0.0,
            reasons=reasons,
            hard_failures=failures
        )
