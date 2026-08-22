"""Cost policy for Phase 18 provider evaluation.

Current development mode is intentionally zero-cost. Paid providers may be
modeled for future production evaluation, but they are not selectable while the
zero-cost policy is active.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BillingClass(str, Enum):
    LOCAL_FREE = "local_free"
    FREE_TIER = "free_tier"
    PAID_USAGE = "paid_usage"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProviderEconomics:
    provider_id: str
    billing_class: BillingClass
    requires_payment_method: bool = False
    notes: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id must be non-empty")
        if not isinstance(self.billing_class, BillingClass):
            raise TypeError("billing_class must be BillingClass")
        if self.notes is not None and (not isinstance(self.notes, str) or not self.notes.strip()):
            raise ValueError("notes must be non-empty or None")


@dataclass(frozen=True)
class CostPolicyDecision:
    allowed: bool
    reason: str


class DevelopmentCostPolicy:
    """Default-zero-cost gate for current PUL7SAR development."""

    def __init__(self, *, zero_cost_only: bool = True) -> None:
        self.zero_cost_only = bool(zero_cost_only)

    def evaluate(self, economics: ProviderEconomics) -> CostPolicyDecision:
        if not isinstance(economics, ProviderEconomics):
            raise TypeError("economics must be ProviderEconomics")
        if not self.zero_cost_only:
            return CostPolicyDecision(True, "paid provider evaluation is explicitly enabled")
        if economics.billing_class is BillingClass.LOCAL_FREE:
            return CostPolicyDecision(True, "local/free provider is allowed in zero-cost mode")
        if economics.billing_class is BillingClass.FREE_TIER and not economics.requires_payment_method:
            return CostPolicyDecision(True, "free-tier provider is allowed without payment method")
        if economics.billing_class is BillingClass.PAID_USAGE:
            return CostPolicyDecision(False, "paid-usage provider is disabled during zero-cost development")
        if economics.requires_payment_method:
            return CostPolicyDecision(False, "provider requires a payment method and is disabled during zero-cost development")
        return CostPolicyDecision(False, "provider economics are not proven zero-cost")

    def assert_allowed(self, economics: ProviderEconomics) -> None:
        decision = self.evaluate(economics)
        if not decision.allowed:
            raise ValueError("cost policy rejected provider: " + decision.reason)
