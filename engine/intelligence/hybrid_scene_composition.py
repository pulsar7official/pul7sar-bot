"""Hybrid composition contract for PUL7SAR publication candidates.

Generated pixels may own atmosphere and non-identifying environment only. Exact
facts, club identity, verified people and PUL7SAR branding are deterministic
layers. The contract fails closed when a generated base tries to own those facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class LayerOwner(str, Enum):
    SYNTHESIS = "synthesis"
    DETERMINISTIC = "deterministic"
    VERIFIED_ASSET = "verified_asset"


@dataclass(frozen=True)
class HybridLayer:
    name: str
    owner: LayerOwner
    required: bool = True


@dataclass(frozen=True)
class HybridCompositionPlan:
    family: EditorialSceneFamily
    base_scene: HybridLayer
    layers: tuple[HybridLayer, ...]
    generated_base_must_be_unbranded: bool = True
    generated_base_must_have_no_readable_facts: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-hybrid-scene-composition-v1"

    def validate(self) -> None:
        if self.base_scene.owner is not LayerOwner.SYNTHESIS:
            raise ValueError("base scene must be synthesis-owned")
        exact_names = {
            "pul7sar_brand", "headline", "score", "statistics", "club_crest",
            "verified_subject", "club_name", "competition_mark", "date_time",
        }
        for layer in self.layers:
            if layer.name in exact_names and layer.owner is LayerOwner.SYNTHESIS:
                raise ValueError(f"exact layer cannot be synthesis-owned: {layer.name}")


class HybridCompositionRegistry:
    _COMMON = (
        HybridLayer("pul7sar_brand", LayerOwner.DETERMINISTIC),
        HybridLayer("headline", LayerOwner.DETERMINISTIC),
    )
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: _COMMON + (
            HybridLayer("score", LayerOwner.DETERMINISTIC),
            HybridLayer("club_name", LayerOwner.DETERMINISTIC),
            HybridLayer("club_crest", LayerOwner.VERIFIED_ASSET, required=False),
            HybridLayer("competition_mark", LayerOwner.VERIFIED_ASSET, required=False),
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: _COMMON + (
            HybridLayer("verified_subject", LayerOwner.VERIFIED_ASSET, required=False),
            HybridLayer("club_name", LayerOwner.DETERMINISTIC),
            HybridLayer("club_crest", LayerOwner.VERIFIED_ASSET, required=False),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: _COMMON + (
            HybridLayer("verified_subject", LayerOwner.VERIFIED_ASSET),
            HybridLayer("club_crest", LayerOwner.VERIFIED_ASSET, required=False),
        ),
        EditorialSceneFamily.DATA_MONUMENT: _COMMON + (
            HybridLayer("statistics", LayerOwner.DETERMINISTIC),
            HybridLayer("club_crest", LayerOwner.VERIFIED_ASSET, required=False),
            HybridLayer("competition_mark", LayerOwner.VERIFIED_ASSET, required=False),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: _COMMON + (
            HybridLayer("date_time", LayerOwner.DETERMINISTIC, required=False),
            HybridLayer("competition_mark", LayerOwner.VERIFIED_ASSET, required=False),
        ),
        EditorialSceneFamily.TACTICAL_BOARD: (
            HybridLayer("pul7sar_brand", LayerOwner.DETERMINISTIC),
            HybridLayer("headline", LayerOwner.DETERMINISTIC),
            HybridLayer("statistics", LayerOwner.DETERMINISTIC, required=False),
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> HybridCompositionPlan:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            # Tactical is deterministic-first; a synthesis base is deliberately
            # not part of its production plan.
            raise ValueError("TACTICAL_BOARD_HAS_NO_SYNTHESIS_BASE")
        plan = HybridCompositionPlan(
            family=family,
            base_scene=HybridLayer("original_unbranded_environment", LayerOwner.SYNTHESIS),
            layers=cls._MAP[family],
        )
        plan.validate()
        return plan
