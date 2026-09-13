"""Bridge real base-scene inspection evidence into HybridLayerQualityGate.

The visual probes remain responsible for observing the generated PNG. This
module only normalizes their explicit findings into layer-ownership evidence.
It never turns missing/unknown inspection output into a clean bill of health.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.base_scene_quality import BaseSceneEvidence
from engine.intelligence.visual_layer_qa import LayerLeakageEvidence


@dataclass(frozen=True)
class BaseSceneLayerInspection:
    evidence: LayerLeakageEvidence
    complete: bool
    blockers: tuple[str, ...] = ()


class BaseSceneLayerEvidenceAdapter:
    """Normalize explicit forbidden-visual observations into layer QA evidence."""

    _TOKENS = {
        "generated_text": "generated_text_detected",
        "generated_platform_brand": "generated_platform_brand_detected",
        "generated_exact_number": "generated_exact_numbers_detected",
        "generated_entity_mark": "generated_entity_mark_detected",
        "generated_unverified_identity": "generated_unverified_identity_detected",
        "generated_sport_geometry": "generated_sport_geometry_detected",
    }

    def adapt(self, base: BaseSceneEvidence) -> BaseSceneLayerInspection:
        if not isinstance(base, BaseSceneEvidence):
            raise TypeError("base must be BaseSceneEvidence")

        findings = {
            "generated_text_detected": False,
            "generated_platform_brand_detected": False,
            "generated_exact_numbers_detected": False,
            "generated_entity_mark_detected": False,
            "generated_unverified_identity_detected": False,
            "generated_sport_geometry_detected": False,
        }
        unknown: list[str] = []
        notes: list[str] = []

        for raw in base.forbidden_visuals_detected:
            token = raw.strip().casefold().replace(" ", "_")
            field = self._TOKENS.get(token)
            if field is None:
                unknown.append(raw)
                continue
            findings[field] = True
            notes.append(f"probe:{token}")

        provenance = dict(base.provenance)
        inspection_complete = provenance.get("forbidden_visual_inspection_complete") is True
        blockers: list[str] = []
        if not inspection_complete:
            blockers.append("forbidden_visual_inspection_not_proven_complete")
        if unknown:
            blockers.append("unclassified_forbidden_visual_observation")
            notes.extend(f"unclassified:{item}" for item in unknown)

        return BaseSceneLayerInspection(
            evidence=LayerLeakageEvidence(notes=tuple(notes), **findings),
            complete=not blockers,
            blockers=tuple(blockers),
        )

    def assert_complete(self, inspection: BaseSceneLayerInspection) -> None:
        if not isinstance(inspection, BaseSceneLayerInspection):
            raise TypeError("inspection must be BaseSceneLayerInspection")
        if not inspection.complete:
            raise ValueError("BASE_SCENE_LAYER_EVIDENCE_INCOMPLETE: " + "; ".join(inspection.blockers))
