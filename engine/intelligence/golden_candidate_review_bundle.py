"""Prepare a fail-closed review bundle for a genuine Golden Hybrid v5 base PNG.

The bundle is deliberately non-publication. It binds the Colab generation summary
to the exact base-image bytes and expands that one GPU result into the approved
CPU-only football pitch diagnostic matrix. This lets visual review continue after
one genuine Candidate 1 generation without spending GPU time on additional seeds.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.football_pitch_diagnostics import FootballPitchDiagnosticBuilder

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST = "pul7sar-golden-batch-v5"
EXPECTED_MODEL = "black-forest-labs/FLUX.2-klein-4B"
_ALLOWED_GENERATED_STATUSES = {
    "COLAB_REAL_HYBRID_BASE_GENERATED",
    "COLAB_GOLDEN_BASE_ALREADY_EXISTS",
}
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(ch in "0123456789abcdefABCDEF" for ch in value)


def _repository_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    repository = root.resolve()
    if resolved != repository and repository not in resolved.parents:
        raise RuntimeError("GOLDEN_REVIEW_PATH_ESCAPES_REPOSITORY")
    return resolved


class GoldenCandidateReviewBundleBuilder:
    """Bind one genuine Colab base to deterministic CPU review artifacts."""

    def build(
        self,
        *,
        repository_root: str,
        summary_path: str,
        output_dir: str,
        expected_candidate: int = 1,
    ) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        if expected_candidate <= 0:
            raise ValueError("expected_candidate must be positive")

        summary_file = _repository_path(root, summary_path)
        if not summary_file.is_file():
            raise FileNotFoundError(summary_file)
        summary = json.loads(summary_file.read_text(encoding="utf-8"))

        if summary.get("branch") != EXPECTED_BRANCH:
            raise RuntimeError("GOLDEN_REVIEW_BRANCH_MISMATCH")
        if summary.get("manifest_version") != EXPECTED_MANIFEST:
            raise RuntimeError("GOLDEN_REVIEW_STALE_MANIFEST")
        if summary.get("status") not in _ALLOWED_GENERATED_STATUSES:
            raise RuntimeError("GOLDEN_REVIEW_REQUIRES_GENUINE_GENERATED_BASE")
        if summary.get("candidate") != expected_candidate:
            raise RuntimeError("GOLDEN_REVIEW_CANDIDATE_MISMATCH")
        if summary.get("publication_ready") is not False:
            raise RuntimeError("GOLDEN_REVIEW_CANNOT_CONSUME_PUBLICATION_READY_INPUT")
        if summary.get("model_id") != EXPECTED_MODEL:
            raise RuntimeError("GOLDEN_REVIEW_MODEL_MISMATCH")
        if summary.get("generated_branding_allowed") is not False:
            raise RuntimeError("GOLDEN_REVIEW_GENERATED_BRANDING_POLICY_DRIFT")
        if summary.get("generated_sport_geometry_allowed") is not False:
            raise RuntimeError("GOLDEN_REVIEW_GENERATED_GEOMETRY_POLICY_DRIFT")
        if summary.get("hybrid_surface_replacement_required") is not True:
            raise RuntimeError("GOLDEN_REVIEW_HYBRID_SURFACE_POLICY_DRIFT")
        if not _is_sha256(summary.get("payload_sha256")):
            raise RuntimeError("GOLDEN_REVIEW_PAYLOAD_SHA_MISSING")

        png_value = summary.get("png")
        if not isinstance(png_value, str) or not png_value.strip():
            raise RuntimeError("GOLDEN_REVIEW_BASE_PNG_MISSING")
        base_png = _repository_path(root, png_value)
        if not base_png.is_file():
            raise FileNotFoundError(base_png)
        with base_png.open("rb") as handle:
            if handle.read(len(_PNG_SIGNATURE)) != _PNG_SIGNATURE:
                raise RuntimeError("GOLDEN_REVIEW_BASE_IS_NOT_REAL_PNG")
        base_sha = _sha256(base_png)

        target_dir = _repository_path(root, output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        diagnostics = FootballPitchDiagnosticBuilder().build(
            base_path=str(base_png),
            output_dir=str(target_dir / "pitch-diagnostics"),
        )
        if diagnostics.get("base_sha256") != base_sha:
            raise RuntimeError("GOLDEN_REVIEW_DIAGNOSTIC_BASE_SHA_MISMATCH")
        if diagnostics.get("publication_ready") is not False:
            raise RuntimeError("GOLDEN_REVIEW_DIAGNOSTICS_CANNOT_BE_PUBLICATION_READY")

        payload: dict[str, Any] = {
            "status": "GOLDEN_CANDIDATE_REVIEW_BUNDLE_READY",
            "candidate": expected_candidate,
            "request_id": summary.get("request_id"),
            "seed": summary.get("seed"),
            "model_id": summary.get("model_id"),
            "payload_sha256": summary.get("payload_sha256"),
            "base_png": str(base_png),
            "base_png_sha256": base_sha,
            "source_summary": str(summary_file),
            "source_summary_sha256": _sha256(summary_file),
            "pitch_diagnostics_manifest": diagnostics.get("manifest"),
            "pitch_variant_count": diagnostics.get("variant_count"),
            "candidate_pixels_untouched": diagnostics.get("candidate_pixels_untouched"),
            "semantic_layer_gate_approved": False,
            "pitch_selection_locked": False,
            "hybrid_semantic_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "next_gate": (
                "semantic layer ownership on the genuine base; then human pitch preset review, "
                "SHA lock, HYBRID_SURFACE review and Golden visual-quality review"
            ),
        }
        manifest = target_dir / "candidate-review-bundle.json"
        manifest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        payload["manifest"] = str(manifest)
        return payload
