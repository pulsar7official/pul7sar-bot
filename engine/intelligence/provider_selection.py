"""Deterministic provider selection/fallback policy for PUL7SAR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from engine.intelligence.cost_policy import DevelopmentCostPolicy, ProviderEconomics
from engine.intelligence.provider_capabilities import (
    ProviderCapabilities,
    ProviderEligibilityDecision,
    ProviderEligibilityGate,
    ProviderRequirements,
)


@dataclass(frozen=True)
class ProviderSelection:
    selected_provider_id: str | None
    decisions: tuple[ProviderEligibilityDecision, ...]
    cost_rejections: tuple[str, ...] = ()

    @property
    def found(self) -> bool:
        return self.selected_provider_id is not None


class ProviderSelector:
    """Choose the first eligible provider in an explicit preference order.

    Current development can enforce zero-cost selection. Paid providers may be
    described/configured for future evaluation but are skipped while the cost
    policy rejects them.
    """

    def __init__(
        self,
        gate: ProviderEligibilityGate | None = None,
        *,
        cost_policy: DevelopmentCostPolicy | None = None,
    ) -> None:
        self._gate = gate or ProviderEligibilityGate()
        self._cost_policy = cost_policy or DevelopmentCostPolicy(zero_cost_only=True)

    def select(
        self,
        providers: tuple[ProviderCapabilities, ...],
        requirements: ProviderRequirements,
        *,
        economics: Mapping[str, ProviderEconomics] | None = None,
    ) -> ProviderSelection:
        providers = tuple(providers)
        if not providers:
            raise ValueError("providers must not be empty")
        ids = [provider.provider_id for provider in providers]
        if len(ids) != len(set(ids)):
            raise ValueError("provider_id values must be unique")

        decisions: list[ProviderEligibilityDecision] = []
        cost_rejections: list[str] = []
        selected = None
        economics = economics or {}

        for provider in providers:
            decision = self._gate.evaluate(provider, requirements)
            decisions.append(decision)
            if not decision.eligible or selected is not None:
                continue

            provider_economics = economics.get(provider.provider_id)
            if provider_economics is None:
                cost_rejections.append(
                    f"{provider.provider_id}: economics not declared; zero-cost status unproven"
                )
                continue
            cost_decision = self._cost_policy.evaluate(provider_economics)
            if not cost_decision.allowed:
                cost_rejections.append(f"{provider.provider_id}: {cost_decision.reason}")
                continue
            selected = provider.provider_id

        return ProviderSelection(selected, tuple(decisions), tuple(cost_rejections))
