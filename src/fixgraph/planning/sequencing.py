"""Action sequencer sorting actions from least disruptive to critical (P0-13 & M4-03)."""

from typing import List
from fixgraph.contracts.internal import ResolvedAction, RiskTier


def _get_risk_order_weight(action: ResolvedAction) -> int:
    if action.category == "critical" or action.risk_tier in (
        RiskTier.FACTORY_RESET,
        RiskTier.RESET_NETWORK,
        RiskTier.SYSTEM_REBOOT,
    ):
        return 100
    if action.category == "manual":
        return 50
    return 10  # auto / inspection / reversible toggle


class ActionSequencer:
    def sequence_actions(self, actions: List[ResolvedAction]) -> List[ResolvedAction]:
        if not actions:
            return []

        # Stable sort based on risk order weight
        sorted_actions = sorted(actions, key=_get_risk_order_weight)
        return sorted_actions
