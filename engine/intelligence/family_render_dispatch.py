"""Fail-closed bridge from editorial events to implemented pixel renderers.

This module is intentionally small: it does not render by itself and it never
falls back to another story family. It resolves the canonical editorial family,
checks the explicit capability registry, then imports exactly the renderer class
owned by that family. A missing module/class/contract is an execution blocker.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import type

from engine.intelligence.family_renderer_registry import (
    FamilyRendererCapability,
    FamilyRendererRegistry,
)
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class FamilyRenderDispatchDecision:
    event: EditorialEvent
    family: EditorialSceneFamily
    capability: FamilyRendererCapability
    renderer_class: type
    fallback_used: bool = False
    contract: str = "pul7sar-family-render-dispatch-v1"

    def __post_init__(self) -> None:
        if self.fallback_used:
            raise ValueError("CROSS_FAMILY_RENDER_FALLBACK_FORBIDDEN")


class FamilyRenderDispatcher:
    """Resolve one event to one renderer owner with no cross-family fallback."""

    def __init__(self, registry: FamilyRendererRegistry | None = None) -> None:
        self._registry = registry or FamilyRendererRegistry()

    @staticmethod
    def family_for_event(event: EditorialEvent) -> EditorialSceneFamily:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        if event in {EditorialEvent.TRANSFER_CONFIRMED, EditorialEvent.TRANSFER_RUMOUR, EditorialEvent.CONTRACT}:
            return EditorialSceneFamily.TRANSFER_SIGNATURE
        if event in {EditorialEvent.RESULT, EditorialEvent.LIVE_MOMENT}:
            return EditorialSceneFamily.RESULT_STATEMENT
        if event in {
            EditorialEvent.INJURY,
            EditorialEvent.SUSPENSION,
            EditorialEvent.STATEMENT,
            EditorialEvent.CONTROVERSY,
            EditorialEvent.OFFICIATING,
            EditorialEvent.DISMISSAL,
            EditorialEvent.APPOINTMENT,
            EditorialEvent.RETIREMENT,
        }:
            return EditorialSceneFamily.VERIFIED_SUBJECT_NEWS
        if event is EditorialEvent.TACTICS:
            return EditorialSceneFamily.TACTICAL_BOARD
        if event in {EditorialEvent.TABLE, EditorialEvent.DRAW, EditorialEvent.SCHEDULE, EditorialEvent.FINANCIAL}:
            return EditorialSceneFamily.DATA_MONUMENT
        return EditorialSceneFamily.EVENT_EDITORIAL

    def resolve(self, event: EditorialEvent) -> FamilyRenderDispatchDecision:
        family = self.family_for_event(event)
        capability = self._registry.require_implemented(family)
        module = import_module(capability.renderer_module)
        try:
            renderer_class = getattr(module, capability.renderer_class)
        except AttributeError as exc:
            raise RuntimeError(f"FAMILY_RENDERER_CLASS_MISSING: {family.value}") from exc
        declared = getattr(renderer_class, "__name__", None)
        if declared != capability.renderer_class:
            raise RuntimeError(f"FAMILY_RENDERER_CLASS_DRIFT: {family.value}")
        return FamilyRenderDispatchDecision(
            event=event,
            family=family,
            capability=capability,
            renderer_class=renderer_class,
        )
