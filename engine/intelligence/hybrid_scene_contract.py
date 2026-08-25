"""Contract joining generated atmosphere with exact editorial composition.

Generated pixels may own atmosphere and material world only. Exact facts,
verified identity and PUL7SAR branding remain deterministic overlays. This
module defines the hand-off without making any benchmark publication-ready.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class HybridSceneContract:
    family: EditorialSceneFamily
    generated_owns: tuple[str, ...]
    deterministic_owns: tuple[str, ...]
    required_clear_zones: tuple[str, ...]
    reject_if: tuple[str, ...]
    contract: str = "pul7sar-hybrid-scene-contract-v1"


class HybridSceneContractRegistry:
    _COMMON_EXACT = (
        "PUL7SAR approved brand master",
        "readable headline/caption",
        "verified club crests",
        "verified real-person identity",
    )
    _COMMON_REJECT = (
        "generated readable text competes with exact copy",
        "generated fake logo or crest",
        "unexplained badge/dot/placeholder",
        "wrong sport semantics",
        "generic template composition",
    )

    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: HybridSceneContract(
            EditorialSceneFamily.RESULT_STATEMENT,
            ("post-match football atmosphere", "lighting", "material depth", "generic crowd depth", "football surface/environment"),
            _COMMON_EXACT + ("exact score", "team names", "competition/result metadata"),
            ("score hero zone", "left club identity zone", "right club identity zone", "brand safe zone"),
            _COMMON_REJECT + ("invented score visible in generated base", "losing side visually humiliated"),
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: HybridSceneContract(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            ("arrival environment", "club-color atmosphere", "tunnel/destination depth", "material light"),
            _COMMON_EXACT + ("verified transfer fact", "destination club name", "shirt number only if verified"),
            ("verified subject hero zone", "destination identity zone", "headline safe zone", "brand safe zone"),
            _COMMON_REJECT + ("invented player identity", "invented signing ceremony"),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: HybridSceneContract(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            ("football editorial environment", "lighting", "depth", "story-specific symbolic atmosphere"),
            _COMMON_EXACT + ("verified subject cutout/asset", "verified role/team context"),
            ("large subject hero zone", "story signal zone", "headline safe zone", "brand safe zone"),
            _COMMON_REJECT + ("generated human presented as the named real person",),
        ),
        EditorialSceneFamily.DATA_MONUMENT: HybridSceneContract(
            EditorialSceneFamily.DATA_MONUMENT,
            ("premium information monument", "gallery/arena atmosphere", "blank physical data surfaces", "lighting"),
            _COMMON_EXACT + ("exact statistic/rank/table/draw data", "exact numeric typography"),
            ("primary number/data zone", "secondary context zone", "brand safe zone"),
            _COMMON_REJECT + ("generated fake statistic", "natural rock mistaken for data monument"),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: HybridSceneContract(
            EditorialSceneFamily.EVENT_EDITORIAL,
            ("pre-event football anticipation", "venue depth", "sport object atmosphere", "lighting"),
            _COMMON_EXACT + ("verified event name", "verified date/time", "verified participants when known"),
            ("event identity zone", "date/time zone", "brand safe zone"),
            _COMMON_REJECT + ("generated outcome implication", "invented result"),
        ),
        EditorialSceneFamily.TACTICAL_BOARD: HybridSceneContract(
            EditorialSceneFamily.TACTICAL_BOARD,
            ("restrained atmosphere only",),
            _COMMON_EXACT + ("pitch geometry", "positions", "movement arrows", "zones", "role labels"),
            ("tactical geometry field", "analysis label zone", "brand safe zone"),
            _COMMON_REJECT + ("generated tactical geometry", "invented player position"),
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> HybridSceneContract:
        return cls._MAP[family]
