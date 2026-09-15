"""Fail-closed human decision gate for a SHA-bound Hybrid review bundle.

This stage records an explicit human visual judgment on the exact base/Hybrid
bytes prepared by ``HybridHumanReviewBundleBuilder``. It never invents a score,
never selects a pitch preset automatically, and never grants Golden or
publication authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
REVIEW_VERSION = "pul7sar-hybrid-human-review-decision-v1"
_CHECK_FIELDS = (
    "pitch_perspective_valid",
    "photographic_integration_valid",
    "surface_tint_natural",
    "line_weight_readable",
    "premium_editorial_composition",
)


class HybridHumanReviewDecisionGate:
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
            raise RuntimeError(f"HYBRID_HUMAN_DECISION_{label}_ESCAPES_REPOSITORY")
        return path

    @staticmethod
    def _load_json(path: Path, *, error: str) -> dict[str, object]:
        if not path.is_file():
            raise RuntimeError(error)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(error) from exc
        if not isinstance(payload, dict):
            raise RuntimeError(error)
        return payload

    @staticmethod
    def _require_png(path: Path, *, label: str) -> None:
        if not path.is_file() or path.read_bytes()[:8] != PNG_SIGNATURE:
            raise RuntimeError(f"HYBRID_HUMAN_DECISION_{label}_INVALID_PNG")

    def _validated_bundle(self, bundle_path: Path) -> tuple[dict[str, object], Path, Path, str, str, str]:
        bundle_path = self._inside_root(bundle_path, label="BUNDLE")
        bundle = self._load_json(bundle_path, error="HYBRID_HUMAN_DECISION_BUNDLE_INVALID")
        expected = {
            "schema": "pul7sar-hybrid-human-review-bundle-v1",
            "status": "HYBRID_HUMAN_REVIEW_BUNDLE_READY",
            "candidate": 1,
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failures = [f"{key}={bundle.get(key)!r}" for key, value in expected.items() if bundle.get(key) != value]
        if failures:
            raise RuntimeError("HYBRID_HUMAN_DECISION_BUNDLE_STATE_DRIFT: " + "; ".join(failures))

        base = self._inside_root(str(bundle.get("review_base_png", "")), label="BASE")
        hybrid = self._inside_root(str(bundle.get("review_hybrid_png", "")), label="HYBRID")
        self._require_png(base, label="BASE")
        self._require_png(hybrid, label="HYBRID")
        base_sha = self._sha256(base)
        hybrid_sha = self._sha256(hybrid)
        if bundle.get("base_png_sha256") != base_sha:
            raise RuntimeError("HYBRID_HUMAN_DECISION_BASE_SHA256_MISMATCH")
        if bundle.get("hybrid_png_sha256") != hybrid_sha:
            raise RuntimeError("HYBRID_HUMAN_DECISION_HYBRID_SHA256_MISMATCH")
        return bundle, base, hybrid, base_sha, hybrid_sha, self._sha256(bundle_path)

    def build_template(self, *, bundle_path: str | Path) -> dict[str, object]:
        bundle_path = self._inside_root(bundle_path, label="BUNDLE")
        _, base, hybrid, base_sha, hybrid_sha, bundle_sha = self._validated_bundle(bundle_path)
        return {
            "review_version": REVIEW_VERSION,
            "status": "HYBRID_HUMAN_REVIEW_DECISION_TEMPLATE",
            "candidate": 1,
            "review_bundle": str(bundle_path),
            "review_bundle_sha256": bundle_sha,
            "review_base_png": str(base),
            "review_hybrid_png": str(hybrid),
            "base_png_sha256": base_sha,
            "hybrid_png_sha256": hybrid_sha,
            "checks": {field: None for field in _CHECK_FIELDS},
            "decision": None,
            "review_note": "",
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "instructions": (
                "Inspect the exact SHA-bound base and Hybrid PNGs. Set every check to true/false and decision to "
                "'accept' or 'reject'. Accept is valid only when every visual-integration check is true."
            ),
        }

    def evaluate(
        self,
        *,
        bundle_path: str | Path,
        review_path: str | Path,
        output_path: str | Path,
    ) -> dict[str, object]:
        bundle_path = self._inside_root(bundle_path, label="BUNDLE")
        _, base, hybrid, base_sha, hybrid_sha, bundle_sha = self._validated_bundle(bundle_path)
        review_path = self._inside_root(review_path, label="REVIEW")
        review = self._load_json(review_path, error="HYBRID_HUMAN_DECISION_REVIEW_INVALID")

        if review.get("review_version") != REVIEW_VERSION:
            raise RuntimeError("HYBRID_HUMAN_DECISION_VERSION_INVALID")
        if review.get("status") != "HYBRID_HUMAN_REVIEW_DECISION_TEMPLATE":
            raise RuntimeError("HYBRID_HUMAN_DECISION_STATUS_INVALID")
        if review.get("candidate") != 1:
            raise RuntimeError("HYBRID_HUMAN_DECISION_CANDIDATE_DRIFT")
        if review.get("publication_ready") is not False or review.get("golden_quality_approved") is not False:
            raise RuntimeError("HYBRID_HUMAN_DECISION_DOWNSTREAM_AUTHORITY_DRIFT")
        if review.get("automatic_selection_performed") is not False:
            raise RuntimeError("HYBRID_HUMAN_DECISION_AUTOMATIC_SELECTION_FORBIDDEN")
        if review.get("review_bundle") != str(bundle_path) or review.get("review_bundle_sha256") != bundle_sha:
            raise RuntimeError("HYBRID_HUMAN_DECISION_BUNDLE_BINDING_MISMATCH")
        if review.get("review_base_png") != str(base) or review.get("review_hybrid_png") != str(hybrid):
            raise RuntimeError("HYBRID_HUMAN_DECISION_PNG_PATH_MISMATCH")
        if review.get("base_png_sha256") != base_sha or review.get("hybrid_png_sha256") != hybrid_sha:
            raise RuntimeError("HYBRID_HUMAN_DECISION_PNG_SHA256_MISMATCH")

        checks = review.get("checks")
        if not isinstance(checks, dict) or set(checks) != set(_CHECK_FIELDS):
            raise RuntimeError("HYBRID_HUMAN_DECISION_CHECK_SCHEMA_MISMATCH")
        for field in _CHECK_FIELDS:
            if not isinstance(checks[field], bool):
                raise RuntimeError(f"HYBRID_HUMAN_DECISION_CHECK_INCOMPLETE:{field}")

        decision = review.get("decision")
        if decision not in {"accept", "reject"}:
            raise RuntimeError("HYBRID_HUMAN_DECISION_VALUE_INVALID")
        all_checks_pass = all(bool(checks[field]) for field in _CHECK_FIELDS)
        if decision == "accept" and not all_checks_pass:
            raise RuntimeError("HYBRID_HUMAN_DECISION_ACCEPT_REQUIRES_ALL_CHECKS")

        approved = decision == "accept" and all_checks_pass
        payload: dict[str, object] = {
            "schema": REVIEW_VERSION,
            "status": "HYBRID_HUMAN_REVIEW_ACCEPTED" if approved else "HYBRID_HUMAN_REVIEW_REJECTED",
            "candidate": 1,
            "review_bundle": str(bundle_path),
            "review_bundle_sha256": bundle_sha,
            "review_file": str(review_path),
            "review_file_sha256": self._sha256(review_path),
            "review_base_png": str(base),
            "review_hybrid_png": str(hybrid),
            "base_png_sha256": base_sha,
            "hybrid_png_sha256": hybrid_sha,
            "checks": {field: bool(checks[field]) for field in _CHECK_FIELDS},
            "decision": decision,
            "review_note": str(review.get("review_note", "")),
            "human_visual_review_approved": approved,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "next_gate": (
                "SHA-bound Golden 8.5/9.0 review may proceed only when human_visual_review_approved=true; "
                "exact brand/typography and SemanticPublicationGate remain mandatory."
            ),
        }
        output_path = self._inside_root(output_path, label="OUTPUT")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return payload
