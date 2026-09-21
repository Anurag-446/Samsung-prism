"""Risk classifier assigning risk tier and category (M4-02)."""

from fixgraph.contracts.internal import ResolvedAction, RiskTier


class RiskClassifier:
    def classify(self, action: ResolvedAction) -> ResolvedAction:
        name_lower = action.name.lower()
        desc_lower = action.description.lower()
        steps_text = " ".join(action.steps).lower()

        if "factory reset" in name_lower or "factory reset" in steps_text:
            category = "critical"
            tier = RiskTier.FACTORY_RESET
        elif "reset" in name_lower or "reset network" in steps_text:
            category = "critical"
            tier = RiskTier.RESET_NETWORK
        elif "reboot" in name_lower or "restart" in steps_text:
            category = "critical"
            tier = RiskTier.SYSTEM_REBOOT
        elif action.category == "manual" or action.exact_uri is None:
            category = "manual"
            tier = RiskTier.MANUAL_REPAIR
        else:
            category = "auto"
            tier = RiskTier.REVERSIBLE_TOGGLE

        return ResolvedAction(
            action_id=action.action_id,
            name=action.name,
            description=action.description,
            steps=action.steps,
            category=category,
            risk_tier=tier,
            catalog_record_id=action.catalog_record_id,
            exact_uri=action.exact_uri,
            evidence_ids=action.evidence_ids,
            screen_confidence=action.screen_confidence,
        )
