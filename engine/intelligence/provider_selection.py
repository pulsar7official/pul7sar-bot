"""Deterministic provider selection/fallback policy for PUL7SAR."""

from __future__ import annotations

from dataclasses import dataclass

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

    @property
    def found(self) -> bool:
        return self.selected_provider_id is not None


class ProviderSelector:
    """Choose the first eligible provider in an explicit preference order.

    Ordering is supplied by configuration; this class never silently ranks a
    provider by price, popularity, or vendor name.
    """

    def __init__(self, gate: ProviderEligibilityGate | None = None) -> None:
        self._gate = gate or ProviderEligibilityGate()

    def select(
        self,
        providers: tuple[ProviderCapabilities, ...],
        requirements: ProviderRequirements,
    ) -> ProviderSelection:
        providers = tuple(providers)
        if not providers:
            raise ValueError("providers must not be empty")
        ids = [provider.provider_id for provider in providers]
        if len(ids) != len(set(ids)):
            raise ValueError("provider_id values must be unique")

        decisions: list[ProviderEligibilityDecision] = []
        selected = None
        for provider in providers:
            decision = self._gate.evaluate(provider, requirements)
            decisions.append(decision)
            if selected is None and decision.eligible:
                selected = provider.provider_id
        return ProviderSelection(selected, tuple(decisions))
