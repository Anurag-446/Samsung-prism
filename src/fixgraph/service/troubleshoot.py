"""Troubleshoot service orchestrator assembling end-to-end pipeline execution (M6-01)."""
import hashlib
import json
import time
import uuid
from typing import Optional

from fixgraph.cache.matcher import TwoStageCacheMatcher
from fixgraph.cache.store import CaseCacheStore
from fixgraph.config import settings
from fixgraph.contracts.internal import (
    CacheabilityDecision,
    CacheEntry,
    PipelineFingerprint,
    RunMetrics,
    TroubleshootOutcome,
    ValidationContext,
)
from fixgraph.contracts.public import Goal, TroubleshootRequest
from fixgraph.data.deeplink_catalog import DeeplinkCatalog
from fixgraph.data.fingerprints import compute_sha256_string
from fixgraph.evidence.resolver import EvidenceResolver
from fixgraph.evidence.retriever import LocalEvidenceRetriever
from fixgraph.observability.logging import logger
from fixgraph.planning.action_extractor import ActionExtractor
from fixgraph.planning.compiler import PlanCompiler
from fixgraph.planning.grouping import ScreenGrouper
from fixgraph.planning.risk import RiskClassifier
from fixgraph.planning.sequencing import ActionSequencer
from fixgraph.providers.exceptions import ProviderError
from fixgraph.query.case_signature import CaseSignatureGenerator
from fixgraph.query.fast_features import extract_fast_features
from fixgraph.query.normalizer import QueryNormalizer
from fixgraph.query.symptom_parser import SymptomParser
from fixgraph.retrieval.screen_resolver import ScreenResolver
from fixgraph.validation.fallback import get_safe_fallback_goal
from fixgraph.validation.final_gate import (
    DeeplinkIntegrityValidator,
    DescriptionValidator,
    DuplicateActionValidator,
    FinalValidationGate,
    RiskOrderValidator,
    StepValidator,
    TitleValidator,
    URLLeakValidator,
    UserConstraintValidator,
)
from fixgraph.validation.pipeline import ValidationPipeline
from fixgraph.validation.repair import DeterministicRepairPass


def check_cacheability(goal: Goal) -> CacheabilityDecision:
    # Do not cache safe fallbacks or empty plans
    if "no_supported_actions" in goal.title.lower() or "provider_error" in goal.title.lower() or "internal_error" in goal.title.lower() or "invalid_plan" in goal.title.lower():
        return CacheabilityDecision(cacheable=False, reason="fallback_plan")

    if not goal.actions:
        return CacheabilityDecision(cacheable=False, reason="empty_plan")

    return CacheabilityDecision(cacheable=True, reason="valid_plan")


class TroubleshootService:
    def __init__(
        self,
        catalog: Optional[DeeplinkCatalog] = None,
        cache_db_path: str = "data/cache.db",
    ):
        self.catalog = catalog
        self.normalizer = QueryNormalizer()
        self.symptom_parser = SymptomParser()
        self.sig_generator = CaseSignatureGenerator()
        self.evidence_resolver = EvidenceResolver()
        self.local_retriever = LocalEvidenceRetriever()
        self.screen_resolver = ScreenResolver(self.catalog)
        self.action_extractor = ActionExtractor()
        self.grouper = ScreenGrouper(self.screen_resolver)
        self.risk_classifier = RiskClassifier()
        self.sequencer = ActionSequencer()
        self.compiler = PlanCompiler()

        # We construct the FinalValidationGate here
        self.final_gate = FinalValidationGate(
            catalog=self.catalog,
            validators=[
                TitleValidator(),
                DescriptionValidator(),
                StepValidator(),
                DeeplinkIntegrityValidator(self.catalog),
                RiskOrderValidator(),
                UserConstraintValidator(),
                URLLeakValidator(),
                DuplicateActionValidator()
            ]
        )

        # Keep old ValidationPipeline for the deterministic repair pass
        # to not break it entirely if it relies on it, or pass it to it.
        # DeterministicRepairPass depends on ValidationPipeline in its signature but doesn't actually use it for validation logic inside repair_goal.
        self.repair_pass = DeterministicRepairPass(ValidationPipeline(self.catalog))
        self.cache_store = CaseCacheStore(db_path=cache_db_path)
        self.cache_matcher = TwoStageCacheMatcher(
            store=self.cache_store,
            similarity_threshold=settings.cache_semantic_threshold,
            min_margin=settings.cache_min_margin
        )

    def _generate_runtime_fingerprint(self) -> PipelineFingerprint:
        catalog_fp = self.catalog.fingerprint if self.catalog else "none"
        embedder_fp = self.cache_matcher.embedder.model_fingerprint
        dim = len(self.cache_matcher.embedder.encode_single("test"))

        composite_parts = [
            f"catalog:{catalog_fp}",
            f"embedder:{embedder_fp}",
            f"dim:{dim}",
            "schema:v1",
            "val:v1",
            "provider:" + settings.llm_provider,
            "model:" + settings.llm_model_name
        ]
        composite_sha = compute_sha256_string("|".join(composite_parts))

        return PipelineFingerprint(
            composite_sha256=composite_sha,
            catalog_sha256=catalog_fp,
            embedder_id=embedder_fp,
            embedding_dimension=dim,
            signature_version="case-signature-v2",
            symptom_prompt_version="v1",
            action_prompt_version="v1",
            provider_id=settings.llm_provider,
            model_id=settings.llm_model_name,
            retrieval_policy_version="v1",
            validator_version=self.final_gate.validator_version,
            compiler_version="v1",
            risk_policy_version="v1",
            fallback_policy_version="v1",
        )

    def troubleshoot(self, request: TroubleshootRequest) -> TroubleshootOutcome:
        start_ts = time.time()
        metrics = RunMetrics()
        req_id = str(uuid.uuid4())

        # 1. Normalize query
        norm_query = self.normalizer.normalize(request.query)
        query_hash = hashlib.sha256(norm_query.clean_query.encode('utf-8')).hexdigest()[:8]

        # 2. Extract fast features & canonical signature (deterministically, before provider extraction)
        fast_features = extract_fast_features(norm_query)
        temp_atom = fast_features.to_symptom_atom()
        signature = self.sig_generator.generate_signature(temp_atom)

        # 3. Generate Runtime Fingerprint
        runtime_fp = self._generate_runtime_fingerprint()

        val_ctx = ValidationContext(
            request_id=req_id,
            original_query_hash=query_hash,
            case_signature=signature,
            catalog_fingerprint=runtime_fp.catalog_sha256,
            pipeline_fingerprint=runtime_fp.composite_sha256,
            prohibited_actions=temp_atom.constraints.prohibited_actions,
            completed_actions=temp_atom.constraints.completed_actions
        )

        def validate_and_fallback(goal: Goal, reason: str, fallback_reason: str) -> Goal:
            report = self.final_gate.validate(goal, val_ctx)
            if report.valid:
                return goal
            logger.warning(f"[req_id={req_id}] Validation failed for {reason}: {[e.message for e in report.errors]}")

            fallback = get_safe_fallback_goal(fallback_reason)
            # Final fallback validation
            fb_report = self.final_gate.validate(fallback, val_ctx)
            if fb_report.valid:
                return fallback
            logger.error(f"[req_id={req_id}] FALLBACK VALIDATION FAILED! {fb_report.errors}")
            return None

        # 4. Two-stage fast-path cache lookup (skipped if cache_enabled=False)
        cache_entry, sim_score, match_reason = None, 0.0, "cache_disabled"
        if settings.cache_enabled:
            cache_entry, sim_score, match_reason = self.cache_matcher.lookup(
                signature=signature,
                query=norm_query.clean_query,
                runtime_fingerprint=runtime_fp,
            )

        if cache_entry:
            # FAST PATH CACHE HIT (<300ms)
            metrics.cache_hit = True
            metrics.cache_similarity = sim_score
            metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
            cached_goal_dict = json.loads(cache_entry.validated_plan_json)
            cached_goal = Goal.model_validate(cached_goal_dict)

            logger.info(
                f"[req_id={req_id}] Cache HIT for query_hash '{query_hash}' (reason: {match_reason}, sim: {sim_score})"
            )
            # Must run through final validation gate even if cached
            final_cached_goal = validate_and_fallback(cached_goal, "cached_plan", "invalid_plan")

            if final_cached_goal:
                return TroubleshootOutcome(request_id=req_id, status="success", goal=final_cached_goal, source="semantic_cache", metrics=metrics)
            else:
                return TroubleshootOutcome(request_id=req_id, status="error", source="fallback", failure_reason="fallback_invalid", metrics=metrics)

        # COLD PATH GENERATION & COMPILATION
        logger.info(f"[req_id={req_id}] Cache MISS for query_hash '{query_hash}'. Executing full pipeline compiler.")

        # 5. Evidence collection
        siis_content = request.get_normalized_siis_content()
        evidence_spans = self.evidence_resolver.segment_evidence(siis_content)
        metrics.evidence_span_count = len(evidence_spans)

        fallback_reason = None
        compiled_goal = None

        if not evidence_spans:
            logger.warning(f"[req_id={req_id}] No SIIS evidence found and cache miss. Skipping model generation.")
            metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
            # Return a contract-safe fallback goal (no_evidence path)
            fb_goal = get_safe_fallback_goal("no_evidence")
            return TroubleshootOutcome(request_id=req_id, status="success", goal=fb_goal, source="no_evidence", metrics=metrics)

        try:
            metrics.llm_called = True
            llm_start = time.time()
            atom = self.symptom_parser.extract_atoms(norm_query, evidence_spans)
            signature = self.sig_generator.generate_signature(atom)

            val_ctx.prohibited_actions = atom.constraints.prohibited_actions
            val_ctx.completed_actions = atom.constraints.completed_actions

            # 7. Candidate action extraction
            supported_actions, unsupported_actions = self.action_extractor.extract_actions(
                norm_query.clean_query, atom, evidence_spans
            )
            metrics.llm_latency_ms = round((time.time() - llm_start) * 1000.0, 2)
            metrics.supported_action_count = len(supported_actions)
            metrics.unsupported_action_count = len(unsupported_actions)
            metrics.candidate_action_count = len(supported_actions) + len(unsupported_actions)

            metrics.provider_used = settings.llm_provider
            metrics.model_used = settings.llm_model_name

            if not supported_actions:
                logger.warning(f"[req_id={req_id}] No supported actions produced by provider.")
                fallback_reason = "no_supported_actions"

            if not fallback_reason:
                # 8. One-action-one-screen resolution & grouping
                resolved_actions = self.grouper.group_and_resolve(supported_actions)

                # 9. Risk classification & sequencing
                classified_actions = [self.risk_classifier.classify(ra) for ra in resolved_actions]
                sequenced_actions = self.sequencer.sequence_actions(classified_actions)

                # 10. Compile Goal
                compiled_goal = self.compiler.compile(
                    raw_query=request.query,
                    atom=atom,
                    resolved_actions=sequenced_actions,
                    catalog=self.catalog
                )

        except ProviderError as e:
            metrics.provider_error = e.__class__.__name__
            logger.error(f"[req_id={req_id}] Provider Error: {e.__class__.__name__}")
            fallback_reason = "provider_error"
        except Exception as e:
            logger.error(f"[req_id={req_id}] Unexpected pipeline error: {str(e)}")
            fallback_reason = "internal_error"

        if fallback_reason:
            metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
            fb_goal = get_safe_fallback_goal(fallback_reason)
            final_fb_goal = validate_and_fallback(fb_goal, "fallback_goal", "invalid_plan")
            if final_fb_goal:
                return TroubleshootOutcome(request_id=req_id, status="success", goal=final_fb_goal, source="fallback", metrics=metrics)
            return TroubleshootOutcome(request_id=req_id, status="error", source="fallback", failure_reason="fallback_invalid", metrics=metrics)


        # 11. Validation pipeline
        val_report = self.final_gate.validate(compiled_goal, val_ctx)
        final_goal = compiled_goal

        if not val_report.valid:
            # 12. Deterministic repair pass
            repaired_goal, was_repaired, repair_logs = self.repair_pass.repair_goal(compiled_goal)
            metrics.validation_repaired = was_repaired

            recheck_report = self.final_gate.validate(repaired_goal, val_ctx)
            if recheck_report.valid:
                final_goal = repaired_goal
            else:
                # 13. Safe fallback
                logger.warning(
                    f"[req_id={req_id}] Plan validation failed after repair. Serving contract-safe fallback."
                )
                metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
                fb_goal = get_safe_fallback_goal("invalid_plan")
                final_fb_goal = validate_and_fallback(fb_goal, "fallback_goal", "invalid_plan")
                if final_fb_goal:
                    return TroubleshootOutcome(request_id=req_id, status="success", goal=final_fb_goal, source="fallback", metrics=metrics)
                return TroubleshootOutcome(request_id=req_id, status="error", source="fallback", failure_reason="fallback_invalid", metrics=metrics)

        # 14. Write ONLY fully validated response JSON to cache (P0-17)
        decision = check_cacheability(final_goal)
        if decision.cacheable:
            plan_json = final_goal.model_dump_json()
            plan_hash = compute_sha256_string(plan_json)
            query_vec = self.cache_matcher.embedder.encode_single(norm_query.clean_query)

            store_query = norm_query.clean_query if settings.cache_store_raw_query else "REDACTED"

            entry = CacheEntry(
                cache_id=str(uuid.uuid4()),
                signature_hash=signature.signature_hash,
                canonical_signature_json=signature.model_dump_json(),
                canonical_query=store_query,
                original_query_hash=query_hash,
                validated_plan_json=plan_json,
                query_embedding=query_vec,
                embedding_model_id=runtime_fp.embedder_id,
                embedding_dimension=runtime_fp.embedding_dimension,
                pipeline_fingerprint=runtime_fp,
                catalog_fingerprint=runtime_fp.catalog_sha256,
                created_at=time.time(),
                updated_at=time.time(),
                validation_hash=compute_sha256_string("valid"),
                plan_hash=plan_hash,
            )
            self.cache_store.put_validated_plan(entry)
        else:
            logger.info(f"[req_id={req_id}] Plan not cached (reason: {decision.reason})")

        metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
        return TroubleshootOutcome(request_id=req_id, status="success", goal=final_goal, source="cold_pipeline", metrics=metrics)
