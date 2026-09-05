"""Lock an explicitly reviewed football pitch diagnostic without regenerating FLUX.

The lock is deliberately non-publication. It binds a human-selected camera preset
to the exact genuine base PNG and exact diagnostic variant bytes that were shown
in the Phase 18 pitch-review flow. It never chooses a preset automatically and
never waives semantic, factual, identity, Golden-quality, branding, typography,
or publication-readiness gates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from engine.intelligence.football_pitch_placement import FootballCameraPreset


class FootballPitchSelectionLock:
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
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(error) from exc
        if not isinstance(payload, dict):
            raise RuntimeError(error)
        return payload

    @staticmethod
    def _resolve(value: object, *, relative_to: Path, error: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(error)
        path = Path(value)
        if not path.is_absolute():
            path = relative_to / path
        return path.resolve()

    def lock(
        self,
        *,
        review_path: str,
        output_dir: str,
    ) -> dict[str, object]:
        review_file = Path(review_path).resolve()
        review = self._load_json(review_file, error="PITCH_SELECTION_REVIEW_INVALID_JSON")

        if review.get("status") != "COLAB_PITCH_REVIEW_READY":
            raise RuntimeError("PITCH_SELECTION_REVIEW_STATUS_INVALID")
        if review.get("review_only") is not True or review.get("publication_ready") is not False:
            raise RuntimeError("PITCH_SELECTION_REVIEW_MUST_BE_NON_PUBLICATION")
        if review.get("selection_is_manual") is not True:
            raise RuntimeError("PITCH_SELECTION_REQUIRES_EXPLICIT_MANUAL_SELECTION")

        selected = review.get("selected_preset")
        allowed = {preset.value for preset in FootballCameraPreset}
        if selected not in allowed:
            raise RuntimeError("PITCH_SELECTION_PRESET_INVALID")

        review_root = review_file.parent
        manifest_path = self._resolve(
            review.get("diagnostic_manifest"),
            relative_to=review_root,
            error="PITCH_SELECTION_DIAGNOSTIC_MANIFEST_MISSING",
        )
        diagnostics = self._load_json(
            manifest_path,
            error="PITCH_SELECTION_DIAGNOSTIC_MANIFEST_INVALID_JSON",
        )
        if diagnostics.get("status") != "FOOTBALL_PITCH_DIAGNOSTICS_READY":
            raise RuntimeError("PITCH_SELECTION_DIAGNOSTIC_STATUS_INVALID")
        if diagnostics.get("diagnostic_only") is not True or diagnostics.get("publication_ready") is not False:
            raise RuntimeError("PITCH_SELECTION_DIAGNOSTIC_MUST_BE_NON_PUBLICATION")
        if diagnostics.get("candidate_pixels_untouched") is not True:
            raise RuntimeError("PITCH_SELECTION_BASE_IMMUTABILITY_NOT_PROVEN")

        manifest_root = manifest_path.parent
        base_from_review = self._resolve(
            review.get("base_png"), relative_to=review_root, error="PITCH_SELECTION_REVIEW_BASE_MISSING"
        )
        base_from_manifest = self._resolve(
            diagnostics.get("base_png"), relative_to=manifest_root, error="PITCH_SELECTION_MANIFEST_BASE_MISSING"
        )
        if base_from_review != base_from_manifest or not base_from_review.is_file():
            raise RuntimeError("PITCH_SELECTION_BASE_PATH_MISMATCH")
        base_sha = self._sha256(base_from_review)
        if diagnostics.get("base_sha256") != base_sha:
            raise RuntimeError("PITCH_SELECTION_BASE_SHA256_MISMATCH")

        selected_review_png = self._resolve(
            review.get("selected_review_png"),
            relative_to=review_root,
            error="PITCH_SELECTION_REVIEW_VARIANT_MISSING",
        )
        variants = diagnostics.get("variants")
        if not isinstance(variants, list):
            raise RuntimeError("PITCH_SELECTION_DIAGNOSTIC_VARIANTS_INVALID")

        matched: dict[str, object] | None = None
        for item in variants:
            if isinstance(item, dict) and item.get("camera_preset") == selected:
                if matched is not None:
                    raise RuntimeError("PITCH_SELECTION_DUPLICATE_PRESET_VARIANTS")
                matched = item
        if matched is None:
            raise RuntimeError("PITCH_SELECTION_PRESET_VARIANT_NOT_FOUND")

        variant_path = self._resolve(
            matched.get("png"), relative_to=manifest_root, error="PITCH_SELECTION_VARIANT_PATH_MISSING"
        )
        if variant_path != selected_review_png or not variant_path.is_file():
            raise RuntimeError("PITCH_SELECTION_REVIEW_VARIANT_PATH_MISMATCH")
        variant_sha = self._sha256(variant_path)
        if matched.get("output_sha256") != variant_sha:
            raise RuntimeError("PITCH_SELECTION_VARIANT_SHA256_MISMATCH")
        integrity = matched.get("artifact_integrity")
        if not isinstance(integrity, dict) or integrity.get("valid") is not True or integrity.get("failures") not in ([], ()):
            raise RuntimeError("PITCH_SELECTION_VARIANT_INTEGRITY_NOT_PROVEN")

        target_dir = Path(output_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        candidate = review.get("candidate")
        try:
            candidate_number = int(candidate)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("PITCH_SELECTION_CANDIDATE_INVALID") from exc
        if candidate_number <= 0:
            raise RuntimeError("PITCH_SELECTION_CANDIDATE_INVALID")

        locked_png = target_dir / f"candidate-{candidate_number:02d}-pitch-{selected}-locked.png"
        shutil.copyfile(variant_path, locked_png)
        locked_sha = self._sha256(locked_png)
        if locked_sha != variant_sha:
            raise RuntimeError("PITCH_SELECTION_LOCK_COPY_SHA256_MISMATCH")

        payload: dict[str, object] = {
            "status": "FOOTBALL_PITCH_SELECTION_LOCKED",
            "selection_only": True,
            "publication_ready": False,
            "candidate": candidate_number,
            "request_id": review.get("request_id"),
            "seed": review.get("seed"),
            "model_id": review.get("model_id"),
            "selection_is_manual": True,
            "selected_preset": selected,
            "base_png": str(base_from_review),
            "base_sha256": base_sha,
            "diagnostic_manifest": str(manifest_path),
            "review_receipt": str(review_file),
            "source_variant_png": str(variant_path),
            "source_variant_sha256": variant_sha,
            "locked_png": str(locked_png),
            "locked_png_sha256": locked_sha,
            "artifact_integrity_proven": True,
            "candidate_pixels_untouched": True,
            "gates_not_waived": [
                "fact_lock",
                "identity_verification",
                "sentiment_neutrality",
                "semantic_layer_ownership",
                "semantic_publication",
                "golden_visual_quality",
                "exact_brand_integrity",
                "typography_integrity",
                "publication_readiness",
            ],
            "next_gate": (
                "Run hybrid semantic/alignment inspection on the locked artifact before any Golden-quality or publication claim."
            ),
        }
        receipt = target_dir / f"candidate-{candidate_number:02d}-pitch-selection-lock.json"
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        payload["receipt"] = str(receipt)
        return payload
