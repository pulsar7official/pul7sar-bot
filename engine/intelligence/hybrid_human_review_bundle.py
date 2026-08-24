"""Tamper-evident human review bundle for a semantically approved Hybrid proof.

The bundle is deliberately non-publication and does not score or auto-select any
visual. It copies the exact provenance-bound base and Hybrid PNG bytes into a
stable review directory and records SHA-256 evidence so the human reviewer sees
exactly the artifacts that passed BASE_SCENE and HYBRID_SURFACE semantic QA.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class HybridHumanReviewBundleReceipt:
    schema: str
    status: str
    candidate: int
    base_png: str
    hybrid_png: str
    base_png_sha256: str
    hybrid_png_sha256: str
    review_base_png: str
    review_hybrid_png: str
    review_manifest: str
    semantic_layer_gate_approved: bool
    hybrid_semantic_review_approved: bool
    human_visual_review_required: bool
    automatic_selection_performed: bool
    golden_quality_approved: bool
    publication_ready: bool


class HybridHumanReviewBundleBuilder:
    def __init__(self, *, root: Path) -> None:
        self.root = root.resolve()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _inside_root(self, value: str | Path, *, label: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        path = path.resolve()
        if path != self.root and self.root not in path.parents:
            raise RuntimeError(f"HYBRID_HUMAN_REVIEW_{label}_ESCAPES_REPOSITORY")
        return path

    @staticmethod
    def _require_png(path: Path, *, label: str) -> None:
        if not path.is_file() or path.read_bytes()[:8] != PNG_SIGNATURE:
            raise RuntimeError(f"HYBRID_HUMAN_REVIEW_{label}_INVALID_PNG")

    def build(
        self,
        *,
        continuation: dict[str, object],
        output_dir: str | Path,
    ) -> HybridHumanReviewBundleReceipt:
        if continuation.get("status") != "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY":
            raise RuntimeError("HYBRID_HUMAN_REVIEW_CONTINUATION_NOT_APPROVED")
        if continuation.get("candidate") != 1:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_REQUIRES_CANDIDATE_1")
        if continuation.get("semantic_layer_gate_approved") is not True:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_BASE_SEMANTIC_GATE_NOT_APPROVED")
        if continuation.get("hybrid_semantic_review_approved") is not True:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_HYBRID_SEMANTIC_GATE_NOT_APPROVED")
        if continuation.get("golden_quality_approved") is not False:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_GOLDEN_AUTHORITY_DRIFT")
        if continuation.get("publication_ready") is not False:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_PUBLICATION_AUTHORITY_DRIFT")

        artifact = continuation.get("artifact_integrity")
        if not isinstance(artifact, dict) or artifact.get("valid") is not True:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_ARTIFACT_INTEGRITY_NOT_PROVEN")

        base_value = continuation.get("base_png")
        hybrid_value = continuation.get("hybrid_png")
        if not isinstance(base_value, str) or not base_value.strip():
            raise RuntimeError("HYBRID_HUMAN_REVIEW_BASE_PNG_MISSING")
        if not isinstance(hybrid_value, str) or not hybrid_value.strip():
            raise RuntimeError("HYBRID_HUMAN_REVIEW_HYBRID_PNG_MISSING")

        base = self._inside_root(base_value, label="BASE_PNG")
        hybrid = self._inside_root(hybrid_value, label="HYBRID_PNG")
        self._require_png(base, label="BASE")
        self._require_png(hybrid, label="HYBRID")

        base_sha = self._sha256(base)
        hybrid_sha = self._sha256(hybrid)
        if continuation.get("hybrid_png_sha256") != hybrid_sha:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_HYBRID_SHA256_MISMATCH")
        if artifact.get("input_sha256") != base_sha:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_BASE_ARTIFACT_SHA256_MISMATCH")
        if artifact.get("output_sha256") != hybrid_sha:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_HYBRID_ARTIFACT_SHA256_MISMATCH")

        target_dir = self._inside_root(output_dir, label="OUTPUT_DIR")
        target_dir.mkdir(parents=True, exist_ok=True)
        review_base = target_dir / "01-proven-base.png"
        review_hybrid = target_dir / "02-semantic-approved-hybrid.png"
        shutil.copyfile(base, review_base)
        shutil.copyfile(hybrid, review_hybrid)
        if self._sha256(review_base) != base_sha or self._sha256(review_hybrid) != hybrid_sha:
            raise RuntimeError("HYBRID_HUMAN_REVIEW_COPY_SHA256_MISMATCH")

        manifest = target_dir / "human-review-manifest.json"
        payload = {
            "schema": "pul7sar-hybrid-human-review-bundle-v1",
            "status": "HYBRID_HUMAN_REVIEW_BUNDLE_READY",
            "candidate": 1,
            "base_png": str(base),
            "hybrid_png": str(hybrid),
            "base_png_sha256": base_sha,
            "hybrid_png_sha256": hybrid_sha,
            "review_base_png": str(review_base),
            "review_hybrid_png": str(review_hybrid),
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "review_focus": [
                "pitch perspective and photographic integration",
                "surface tint and edge blending",
                "line weight and regulation geometry readability",
                "overall editorial composition and premium sports-news quality",
            ],
            "next_gate": "explicit human visual review; no automatic approval or preset selection",
        }
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        return HybridHumanReviewBundleReceipt(
            schema=payload["schema"],
            status=payload["status"],
            candidate=1,
            base_png=str(base),
            hybrid_png=str(hybrid),
            base_png_sha256=base_sha,
            hybrid_png_sha256=hybrid_sha,
            review_base_png=str(review_base),
            review_hybrid_png=str(review_hybrid),
            review_manifest=str(manifest),
            semantic_layer_gate_approved=True,
            hybrid_semantic_review_approved=True,
            human_visual_review_required=True,
            automatic_selection_performed=False,
            golden_quality_approved=False,
            publication_ready=False,
        )
