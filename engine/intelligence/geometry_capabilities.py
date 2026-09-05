"""Capabilities for deterministic sport-surface renderers.

A sport rule may *require* exact geometry before a renderer exists. PUL7SAR must
not interpret the policy requirement as implementation readiness. This registry
fails closed and lets editorial planning choose a safer no-surface fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.sport_visual_rules import SportVisualRule


class GeometryCapabilityStatus(str, Enum):
    READY = "ready"
    NOT_REQUIRED = "not_required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class GeometryCapability:
    sport: str
    status: GeometryCapabilityStatus
    renderer_id: str | None = None
    reason: str | None = None

    @property
    def ready(self) -> bool:
        return self.status in {GeometryCapabilityStatus.READY, GeometryCapabilityStatus.NOT_REQUIRED}


class DeterministicGeometryCapabilityRegistry:
    """Only declare renderers that actually exist in Phase 18 code."""

    _READY = {
        "football": "football_pitch_projective_v1",
    }

    def evaluate(self, rule: SportVisualRule) -> GeometryCapability:
        if not isinstance(rule, SportVisualRule):
            raise TypeError("rule must be SportVisualRule")
        if not rule.exact_geometry_preferred:
            return GeometryCapability(rule.sport, GeometryCapabilityStatus.NOT_REQUIRED, reason="sport rule does not require exact surface geometry")
        renderer = self._READY.get(rule.sport)
        if renderer is not None:
            return GeometryCapability(rule.sport, GeometryCapabilityStatus.READY, renderer_id=renderer)
        return GeometryCapability(
            rule.sport,
            GeometryCapabilityStatus.UNAVAILABLE,
            reason="exact sport geometry is required by policy but no deterministic renderer is implemented yet",
        )
