"""Troubleshoot service orchestrator assembling end-to-end pipeline execution (M6-01)."""

import json
import time
from typing import Optional, Tuple
from fixgraph.cache.matcher import TwoStageCacheMatcher
from fixgraph.cache.store import CaseCacheStore
from fixgraph.contracts.internal import RunMetrics
from fixgraph.contracts.public import Goal, TroubleshootRequest
from fixgraph.data.deeplink_catalog import DeeplinkCatalog
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.evidence.resolver import EvidenceResolver
from fixgraph.observability.logging import logger
from fixgraph.planning.action_extractor import ActionExtractor
from fixgraph.planning.compiler import PlanCompiler
from fixgraph.planning.grouping import ScreenGrouper
from fixgraph.planning.risk import RiskClassifier
from fixgraph.planning.sequencing import ActionSequencer
from fixgraph.query.case_signature import CaseSignatureGenerator
from fixgraph.query.normalizer import QueryNormalizer
from fixgraph.query.symptom_parser import SymptomParser
from fixgraph.retrieval.screen_resolver import ScreenResolver
from fixgraph.validation.fallback import get_safe_fallback_goal
from fixgraph.validation.pipeline import ValidationPipeline
from fixgraph.validation.repair import DeterministicRepairPass


class TroubleshootService:
    def __init__(
        self,
        catalog: Optional[DeeplinkCatalog] = None,
        cache_db_path: str = "data/cache.db",
    ):
        self.catalog = catalog or load_deeplink_catalog(None)
        self.normalizer = QueryNormalizer()
        self.symptom_parser = SymptomParser()
        self.sig_generator = CaseSignatureGenerator()
        self.evidence_resolver = EvidenceResolver()
        self.screen_resolver = ScreenResolver(self.catalog)
        self.action_extractor = ActionExtractor()
        self.grouper = ScreenGrouper(self.screen_resolver)
        self.risk_classifier = RiskClassifier()
        self.sequencer = ActionSequencer()
        self.compiler = PlanCompiler()
        self.pipeline = ValidationPipeline(self.catalog)
        self.repair_pass = DeterministicRepairPass(self.pipeline)
        self.cache_store = CaseCacheStore(db_path=cache_db_path)
        self.cache_matcher = TwoStageCacheMatcher(store=self.cache_store)

    def troubleshoot(self, request: TroubleshootRequest) -> Tuple[Goal, RunMetrics]:
        start_ts = time.time()
        metrics = RunMetrics()

        # 1. Normalize query
        norm_query = self.normalizer.normalize(request.query)

        # 2. Extract symptom atom & canonical signature
        atom = self.symptom_parser.extract_atoms(norm_query)
        signature = self.sig_generator.generate_signature(atom)

        # 3. Two-stage fast-path cache lookup
        cache_entry, sim_score, match_reason = self.cache_matcher.lookup(
            signature=signature,
            query=norm_query.clean_query,
            catalog_fingerprint=self.catalog.fingerprint,
        )

        if cache_entry:
            # FAST PATH CACHE HIT (<300ms)
            metrics.cache_hit = True
            metrics.cache_similarity = sim_score
            metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
            cached_goal_dict = json.loads(cache_entry.validated_plan_json)
            logger.info(f"Cache HIT for query '{request.query}' (reason: {match_reason}, sim: {sim_score})")
            return Goal.model_validate(cached_goal_dict), metrics

        # COLD PATH GENERATION & COMPILATION
        logger.info(f"Cache MISS for query '{request.query}'. Executing full pipeline compiler.")

        # 4. Evidence segmentation
        evidence_spans = self.evidence_resolver.segment_evidence(request.siis_response)

        # 5. Candidate action extraction
        candidate_actions = self.action_extractor.extract_actions(
            norm_query.clean_query, atom, evidence_spans
        )

        # 6. One-action-one-screen resolution & grouping
        resolved_actions = self.grouper.group_and_resolve(candidate_actions)

        # 7. Risk classification & sequencing
        classified_actions = [self.risk_classifier.classify(ra) for ra in resolved_actions]
        sequenced_actions = self.sequencer.sequence_actions(classified_actions)

        # 8. Compile Goal
        compiled_goal = self.compiler.compile(
            raw_query=request.query,
            atom=atom,
            resolved_actions=sequenced_actions,
        )

        # 9. Validation pipeline
        val_report = self.pipeline.validate(compiled_goal)
        final_goal = compiled_goal

        if not val_report.is_valid:
            # 10. Deterministic repair pass
            repaired_goal, was_repaired, repair_logs = self.repair_pass.repair_goal(compiled_goal)
            metrics.validation_repaired = was_repaired

            recheck_report = self.pipeline.validate(repaired_goal)
            if recheck_report.is_valid:
                final_goal = repaired_goal
            else:
                # 11. Safe fallback
                logger.warning(f"Plan validation failed after repair. Serving contract-safe fallback.")
                final_goal = get_safe_fallback_goal("invalid_plan")

        # 12. Write ONLY fully validated response JSON to cache (P0-17)
        self.cache_store.put_validated_plan(
            signature_hash=signature.signature_hash,
            canonical_query=signature.canonical_query,
            query_embedding=self.cache_matcher.embedder.encode_single(norm_query.clean_query),
            validated_plan_json=final_goal.model_dump_json(),
            catalog_fingerprint=self.catalog.fingerprint,
        )

        metrics.total_latency_ms = round((time.time() - start_ts) * 1000.0, 2)
        return final_goal, metrics
