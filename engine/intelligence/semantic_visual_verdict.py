"""Strict semantic visual-verification result contract for PUL7SAR Phase 18.

A concrete local vision model may implement the verifier, but all providers must
return this normalized evidence shape. The contract deliberately separates
"not detected" from "not inspected" so unavailable capabilities cannot be
mistaken for a clean image.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.hybrid_evidence_builder import VisualInspectionFlags


class InspectionState(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_INSPECTED = "not_inspected"


@dataclass(frozen=True)
class SemanticCheck:
    state: InspectionState
    confidence: float
    detail: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.state, InspectionState):
            raise TypeError("state must be InspectionState")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.state is InspectionState.NOT_INSPECTED and self.confidence != 0.0:
            raise ValueError("not-inspected check must have zero confidence")


@dataclass(frozen=True)
class SemanticVisualVerdict:
    verifier_id: str
    readable_text_absent: SemanticCheck
    platform_brand_absent: SemanticCheck
    fake_entity_marks_absent: SemanticCheck
    single_scene: SemanticCheck
    severe_defects_absent: SemanticCheck
    subject_framing_valid: SemanticCheck
    sport_geometry_alignment_valid: SemanticCheck | None = None
    identity_valid: SemanticCheck | None = None
    exact_numbers_absent: SemanticCheck | None = None
    generated_sport_geometry_absent: SemanticCheck | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.verifier_id, str) or not self.verifier_id.strip():
            raise ValueError("verifier_id is required")

    def _non_identity_checks(self) -> tuple[SemanticCheck, ...]:
        checks = [
            self.readable_text_absent,
            self.platform_brand_absent,
            self.fake_entity_marks_absent,
            self.single_scene,
            self.severe_defects_absent,
            self.subject_framing_valid,
        ]
        for optional in (
            self.sport_geometry_alignment_valid,
            self.exact_numbers_absent,
            self.generated_sport_geometry_absent,
        ):
            if optional is not None:
                checks.append(optional)
        return tuple(checks)

    @property
    def complete_non_identity(self) -> bool:
        return all(item.state is not InspectionState.NOT_INSPECTED for item in self._non_identity_checks())

    @property
    def approved_non_identity(self) -> bool:
        checks = self._non_identity_checks()
        return self.complete_non_identity and all(item.state is InspectionState.PASS for item in checks)

    def to_flags(self) -> VisualInspectionFlags:
        """Convert only inspected FAIL states to negative Hybrid evidence."""
        severe = self.severe_defects_absent.state is InspectionState.FAIL
        if self.sport_geometry_alignment_valid is not None:
            severe = severe or self.sport_geometry_alignment_valid.state is InspectionState.FAIL
        generated_text = self.readable_text_absent.state is InspectionState.FAIL
        if self.exact_numbers_absent is not None:
            generated_text = generated_text or self.exact_numbers_absent.state is InspectionState.FAIL
        if self.generated_sport_geometry_absent is not None:
            severe = severe or self.generated_sport_geometry_absent.state is InspectionState.FAIL
        return VisualInspectionFlags(
            generated_text_detected=generated_text,
            generated_brand_detected=self.platform_brand_absent.state is InspectionState.FAIL,
            generated_fake_logo_detected=self.fake_entity_marks_absent.state is InspectionState.FAIL,
            severe_anatomy_or_object_defect=severe,
            collage_or_split_scene_detected=self.single_scene.state is InspectionState.FAIL,
        )


class SemanticVisualVerdictGate:
    def evaluate(
        self,
        verdict: SemanticVisualVerdict,
        *,
        identity_required: bool,
        geometry_alignment_required: bool = False,
        exact_numbers_absence_required: bool = False,
        generated_sport_geometry_absence_required: bool = False,
        minimum_confidence: float = 0.85,
    ) -> tuple[bool, tuple[str, ...]]:
        if not isinstance(verdict, SemanticVisualVerdict):
            raise TypeError("verdict must be SemanticVisualVerdict")
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")

        checks = {
            "readable_text_absent": verdict.readable_text_absent,
            "platform_brand_absent": verdict.platform_brand_absent,
            "fake_entity_marks_absent": verdict.fake_entity_marks_absent,
            "single_scene": verdict.single_scene,
            "severe_defects_absent": verdict.severe_defects_absent,
            "subject_framing_valid": verdict.subject_framing_valid,
        }
        if geometry_alignment_required:
            if verdict.sport_geometry_alignment_valid is None:
                return False, ("sport_geometry_alignment_not_inspected",)
            checks["sport_geometry_alignment_valid"] = verdict.sport_geometry_alignment_valid
        if exact_numbers_absence_required:
            if verdict.exact_numbers_absent is None:
                return False, ("exact_numbers_absence_not_inspected",)
            checks["exact_numbers_absent"] = verdict.exact_numbers_absent
        if generated_sport_geometry_absence_required:
            if verdict.generated_sport_geometry_absent is None:
                return False, ("generated_sport_geometry_absence_not_inspected",)
            checks["generated_sport_geometry_absent"] = verdict.generated_sport_geometry_absent
        if identity_required:
            if verdict.identity_valid is None:
                return False, ("identity_not_inspected",)
            checks["identity_valid"] = verdict.identity_valid

        failures: list[str] = []
        for name, check in checks.items():
            if check.state is InspectionState.NOT_INSPECTED:
                failures.append(name + ":not_inspected")
            elif check.state is InspectionState.FAIL:
                failures.append(name + ":failed")
            elif check.confidence < minimum_confidence:
                failures.append(name + ":confidence_below_threshold")
        return not failures, tuple(failures)
