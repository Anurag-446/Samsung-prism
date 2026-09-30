"""One-action-one-screen grouper logic (P0-11 & M4-01)."""

from typing import Dict, List

from fixgraph.contracts.internal import CandidateAction, ResolvedAction, RiskTier, ScreenCandidate
from fixgraph.navigation.resolver import NavigationAwareScreenResolver as ScreenResolver


class ScreenGrouper:
    def __init__(self, resolver: ScreenResolver):
        self.resolver = resolver

    def group_and_resolve(self, candidate_actions: List[CandidateAction]) -> List[ResolvedAction]:
        resolved_by_screen: Dict[str, ResolvedAction] = {}
        unresolved_count = 0

        for cand in candidate_actions:
            # Resolve to exact target screen via catalog hybrid search
            screen_cand: ScreenCandidate = self.resolver.resolve_action_intent(
                cand.candidate_screen_text or cand.intent
            )

            if screen_cand:
                rec = self.resolver.get_catalog_record(screen_cand.catalog_record_id)
                rec_id = screen_cand.catalog_record_id
                category = rec.category if rec else "auto"

                if rec_id in resolved_by_screen:
                    # Merge steps for candidate actions targeting the SAME physical screen
                    existing = resolved_by_screen[rec_id]
                    combined_steps = list(dict.fromkeys(existing.steps + cand.steps))
                    resolved_by_screen[rec_id] = ResolvedAction(
                        action_id=existing.action_id,
                        name=existing.name,
                        description=existing.description,
                        steps=combined_steps,
                        category=category,
                        risk_tier=existing.risk_tier,
                        catalog_record_id=rec_id,
                        exact_uri=screen_cand.exact_uri,
                        evidence_ids=list(set(existing.evidence_ids + cand.evidence_ids)),
                        screen_confidence=screen_cand.confidence,
                    )
                else:
                    resolved_by_screen[rec_id] = ResolvedAction(
                        action_id=cand.action_id,
                        name=rec.name if rec else cand.intent,
                        description=f"It will optimize {rec.name.lower() if rec else 'settings'} performance",
                        steps=cand.steps,
                        category=category,
                        risk_tier=cand.risk_hint,
                        catalog_record_id=rec_id,
                        exact_uri=screen_cand.exact_uri,
                        evidence_ids=cand.evidence_ids,
                        screen_confidence=screen_cand.confidence,
                    )
            else:
                # Unresolved screen mapping becomes a manual action with deeplink = None
                unresolved_count += 1
                rec_id = f"manual_{unresolved_count}"
                resolved_by_screen[rec_id] = ResolvedAction(
                    action_id=cand.action_id,
                    name=f"Manual {cand.intent}",
                    description=f"It will inspect manual {cand.intent.lower()} state",
                    steps=cand.steps,
                    category="manual",
                    risk_tier=RiskTier.MANUAL_REPAIR,
                    catalog_record_id=None,
                    exact_uri=None,
                    evidence_ids=cand.evidence_ids,
                    screen_confidence=0.0,
                )

        return list(resolved_by_screen.values())
