"""Fail-closed semantic/alignment review for a locked football-pitch selection.

This gate is intentionally downstream of the human pitch-review lock and upstream
of any Golden-quality or publication claim. It replays the locked PNG hash and
requires a complete HYBRID_SURFACE semantic verdict with geometry alignment,
exact-number absence, and no conflicting generated sport geometry.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from engine.intelligence.semantic_visual_verdict import (
    SemanticVisualVerdict,
    SemanticVisualVerdictGate,
)


_REQUIRED_UNWAIVED_GATES = {
    "fact_lock",
    "identity_verification",
    "sentiment_neutrality",
    "semantic_layer_ownership",
    "semantic_publication",
    "golden_visual_quality",
    "exact_brand_integrity",
    "typography_integrity",
    "publication_readiness",
}


class FootballPitchSemanticReviewGate:
    def __init__(self, *, minimum_confidence: float = 0.85) -> None:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        self.minimum_confidence = minimum_confidence
        self._verdict_gate = SemanticVisualVerdictGate()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _load_json(path: Path, *, error: str) -> dict[str, object]:
        if not path.is_file():
            raise FileNotFoundError(path)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(error) from exc
        if not isinstance(value, dict):
            raise RuntimeError(error)
        return value

    @staticmethod
    def _resolve(value: object, *, relative_to: Path, error: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(error)
        path = Path(value)
        if not path.is_absolute():
            path = relative_to / path
        return path.resolve()

    @staticmethod
    def _check_payload(check) -> dict[str, object] | None:
        if check is None:
            return None
        return {
            "state": check.state.value,
            "confidence": float(check.confidence),
            "detail": check.detail,
        }

    def review(
        self,
        *,
        selection_lock_path: str,
        verdict: SemanticVisualVerdict,
        output_dir: str,
    ) -> dict[str, object]:
        if not isinstance(verdict, SemanticVisualVerdict):
            raise TypeError("verdict must be SemanticVisualVerdict")

        lock_file = Path(selection_lock_path).resolve()
        lock = self._load_json(lock_file, error="PITCH_SEMANTIC_SELECTION_LOCK_INVALID_JSON")
        if lock.get("status") != "FOOTBALL_PITCH_SELECTION_LOCKED":
            raise RuntimeError("PITCH_SEMANTIC_SELECTION_LOCK_STATUS_INVALID")
        if lock.get("selection_only") is not True or lock.get("publication_ready") is not False:
            raise RuntimeError("PITCH_SEMANTIC_SELECTION_LOCK_MUST_BE_NON_PUBLICATION")
        if lock.get("selection_is_manual") is not True or lock.get("artifact_integrity_proven") is not True:
            raise RuntimeError("PITCH_SEMANTIC_SELECTION_LOCK_INTEGRITY_NOT_PROVEN")

        unwaived = lock.get("gates_not_waived")
        if not isinstance(unwaived, list) or not _REQUIRED_UNWAIVED_GATES.issubset(set(unwaived)):
            raise RuntimeError("PITCH_SEMANTIC_DOWNSTREAM_GATES_NOT_PRESERVED")

        candidate_raw = lock.get("candidate")
        try:
            candidate = int(candidate_raw)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("PITCH_SEMANTIC_CANDIDATE_INVALID") from exc
        if candidate <= 0:
            raise RuntimeError("PITCH_SEMANTIC_CANDIDATE_INVALID")

        locked_png = self._resolve(
            lock.get("locked_png"),
            relative_to=lock_file.parent,
            error="PITCH_SEMANTIC_LOCKED_PNG_MISSING",
        )
        if not locked_png.is_file():
            raise RuntimeError("PITCH_SEMANTIC_LOCKED_PNG_MISSING")
        actual_sha = self._sha256(locked_png)
        if lock.get("locked_png_sha256") != actual_sha:
            raise RuntimeError("PITCH_SEMANTIC_LOCKED_PNG_SHA256_MISMATCH")
        if lock.get("source_variant_sha256") != actual_sha:
            raise RuntimeError("PITCH_SEMANTIC_SOURCE_VARIANT_SHA256_MISMATCH")

        approved, failures = self._verdict_gate.evaluate(
            verdict,
            identity_required=False,
            geometry_alignment_required=True,
            exact_numbers_absence_required=True,
            generated_sport_geometry_absence_required=True,
            minimum_confidence=self.minimum_confidence,
        )

        checks = {
            name: self._check_payload(getattr(verdict, name))
            for name in (
                "readable_text_absent",
                "platform_brand_absent",
                "fake_entity_marks_absent",
                "exact_numbers_absent",
                "generated_sport_geometry_absent",
                "single_scene",
                "severe_defects_absent",
                "subject_framing_valid",
                "sport_geometry_alignment_valid",
            )
        }

        target_dir = Path(output_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "status": "FOOTBALL_PITCH_SEMANTIC_REVIEW_COMPLETE",
            "candidate": candidate,
            "request_id": lock.get("request_id"),
            "seed": lock.get("seed"),
            "model_id": lock.get("model_id"),
            "selected_preset": lock.get("selected_preset"),
            "selection_lock": str(lock_file),
            "locked_png": str(locked_png),
            "locked_png_sha256": actual_sha,
            "semantic_stage": "hybrid_surface",
            "verifier_id": verdict.verifier_id,
            "minimum_confidence": self.minimum_confidence,
            "semantic_approved": approved,
            "semantic_failures": list(failures),
            "checks": checks,
            "publication_ready": False,
            "golden_quality_approved": False,
            "gates_not_waived": sorted(_REQUIRED_UNWAIVED_GATES),
            "next_gate": (
                "Golden visual quality review may run only when semantic_approved=true; "
                "publication still requires exact brand, typography, and final publication-readiness gates."
            ),
        }
        receipt = target_dir / f"candidate-{candidate:02d}-pitch-semantic-review.json"
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        payload["receipt"] = str(receipt)
        return payload
