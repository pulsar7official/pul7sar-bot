"""Convert completed semantic visual checks into Hybrid layer-leakage evidence.

The adapter is deliberately fail-closed. A PASS is usable only when the check was
actually inspected at or above the configured confidence. Missing checks never
become an implicit clean result.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict
from engine.intelligence.visual_layer_qa import LayerLeakageEvidence


@dataclass(frozen=True)
class SemanticLayerInspection:
    evidence: LayerLeakageEvidence
    complete: bool
    blockers: tuple[str, ...]


class SemanticLayerEvidenceAdapter:
    def __init__(self, *, minimum_confidence: float = 0.85) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        self.minimum_confidence = minimum_confidence

    def _usable(self, name: str, check: SemanticCheck | None, blockers: list[str]) -> bool:
        if check is None or check.state is InspectionState.NOT_INSPECTED:
            blockers.append(name + ":not_inspected")
            return False
        if check.confidence < self.minimum_confidence:
            blockers.append(name + ":confidence_below_threshold")
            return False
        return True

    def adapt(
        self,
        verdict: SemanticVisualVerdict,
        *,
        require_exact_number_check: bool,
        require_sport_geometry_check: bool,
    ) -> SemanticLayerInspection:
        if not isinstance(verdict, SemanticVisualVerdict):
            raise TypeError("verdict must be SemanticVisualVerdict")

        blockers: list[str] = []
        notes: list[str] = ["semantic_verifier:" + verdict.verifier_id]

        core = {
            "readable_text_absent": verdict.readable_text_absent,
            "platform_brand_absent": verdict.platform_brand_absent,
            "fake_entity_marks_absent": verdict.fake_entity_marks_absent,
        }
        usable: dict[str, bool] = {}
        for name, check in core.items():
            usable[name] = self._usable(name, check, blockers)

        exact_usable = True
        if require_exact_number_check:
            exact_usable = self._usable("exact_numbers_absent", verdict.exact_numbers_absent, blockers)

        geometry_usable = True
        if require_sport_geometry_check:
            geometry_usable = self._usable("generated_sport_geometry_absent", verdict.generated_sport_geometry_absent, blockers)

        evidence = LayerLeakageEvidence(
            generated_text_detected=usable["readable_text_absent"] and verdict.readable_text_absent.state is InspectionState.FAIL,
            generated_platform_brand_detected=usable["platform_brand_absent"] and verdict.platform_brand_absent.state is InspectionState.FAIL,
            generated_exact_numbers_detected=bool(
                require_exact_number_check and exact_usable and verdict.exact_numbers_absent is not None
                and verdict.exact_numbers_absent.state is InspectionState.FAIL
            ),
            generated_entity_mark_detected=usable["fake_entity_marks_absent"] and verdict.fake_entity_marks_absent.state is InspectionState.FAIL,
            generated_sport_geometry_detected=bool(
                require_sport_geometry_check and geometry_usable and verdict.generated_sport_geometry_absent is not None
                and verdict.generated_sport_geometry_absent.state is InspectionState.FAIL
            ),
            notes=tuple(notes),
        )
        return SemanticLayerInspection(evidence=evidence, complete=not blockers, blockers=tuple(blockers))

    @staticmethod
    def assert_complete(result: SemanticLayerInspection) -> None:
        if not isinstance(result, SemanticLayerInspection):
            raise TypeError("result must be SemanticLayerInspection")
        if not result.complete:
            raise ValueError("SEMANTIC_LAYER_EVIDENCE_INCOMPLETE: " + "; ".join(result.blockers))
