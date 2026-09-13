"""Golden Visual review bound to the exact locked-pitch semantic artifact.

This stage bridges the locked HYBRID_SURFACE semantic receipt to the human
Golden-quality scorecard without falling back to the original FLUX batch PNG.
It never invents scores and never grants publication readiness.
"""
from __future__ import annotations

from dataclasses import fields
import hashlib
import json
from pathlib import Path

from engine.intelligence.golden_visual_quality import (
    GoldenVisualBlockers,
    GoldenVisualEvaluation,
    GoldenVisualScores,
)


LOCKED_GOLDEN_REVIEW_VERSION = "pul7sar-locked-golden-visual-review-v1"
_SCORE_FIELDS = tuple(item.name for item in fields(GoldenVisualScores))
_BLOCKER_FIELDS = tuple(item.name for item in fields(GoldenVisualBlockers))
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


class LockedGoldenVisualReviewGate:
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

    def _validated_semantic_receipt(self, semantic_review_path: str) -> tuple[dict[str, object], Path, str]:
        receipt_path = Path(semantic_review_path).resolve()
        receipt = self._load_json(receipt_path, error="LOCKED_GOLDEN_SEMANTIC_RECEIPT_INVALID_JSON")
        if receipt.get("status") != "FOOTBALL_PITCH_SEMANTIC_REVIEW_COMPLETE":
            raise RuntimeError("LOCKED_GOLDEN_SEMANTIC_RECEIPT_STATUS_INVALID")
        if receipt.get("semantic_approved") is not True:
            raise RuntimeError("LOCKED_GOLDEN_SEMANTIC_REVIEW_NOT_APPROVED")
        if receipt.get("publication_ready") is not False or receipt.get("golden_quality_approved") is not False:
            raise RuntimeError("LOCKED_GOLDEN_UPSTREAM_RECEIPT_STATE_INVALID")
        gates = receipt.get("gates_not_waived")
        if not isinstance(gates, list) or not _REQUIRED_UNWAIVED_GATES.issubset(set(gates)):
            raise RuntimeError("LOCKED_GOLDEN_DOWNSTREAM_GATES_NOT_PRESERVED")

        request_id = receipt.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise RuntimeError("LOCKED_GOLDEN_REQUEST_ID_INVALID")
        seed = receipt.get("seed")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise RuntimeError("LOCKED_GOLDEN_SEED_INVALID")
        candidate = receipt.get("candidate")
        if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate <= 0:
            raise RuntimeError("LOCKED_GOLDEN_CANDIDATE_INVALID")

        locked_png = self._resolve(
            receipt.get("locked_png"),
            relative_to=receipt_path.parent,
            error="LOCKED_GOLDEN_PNG_MISSING",
        )
        if not locked_png.is_file():
            raise RuntimeError("LOCKED_GOLDEN_PNG_MISSING")
        actual_sha = self._sha256(locked_png)
        if receipt.get("locked_png_sha256") != actual_sha:
            raise RuntimeError("LOCKED_GOLDEN_PNG_SHA256_MISMATCH")
        return receipt, locked_png, actual_sha

    def build_template(self, *, semantic_review_path: str) -> dict[str, object]:
        receipt, locked_png, actual_sha = self._validated_semantic_receipt(semantic_review_path)
        return {
            "review_version": LOCKED_GOLDEN_REVIEW_VERSION,
            "status": "LOCKED_GOLDEN_VISUAL_REVIEW_TEMPLATE",
            "candidate": receipt["candidate"],
            "request_id": receipt["request_id"],
            "seed": receipt["seed"],
            "semantic_review": str(Path(semantic_review_path).resolve()),
            "locked_png": str(locked_png),
            "locked_png_sha256": actual_sha,
            "scores": {field: None for field in _SCORE_FIELDS},
            "blockers": {field: False for field in _BLOCKER_FIELDS},
            "review_note": "",
            "publication_ready": False,
            "instructions": (
                "Inspect the exact locked PNG before entering 0-10 scores. Every hard blocker field must remain present; "
                "mark each observed blocker true. Do not alter candidate/request_id/seed/locked_png_sha256."
            ),
        }

    @staticmethod
    def _score(value: object, *, field: str) -> float:
        if value is None:
            raise RuntimeError(f"LOCKED_GOLDEN_SCORE_STILL_NULL:{field}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RuntimeError(f"LOCKED_GOLDEN_SCORE_INVALID:{field}")
        numeric = float(value)
        if not 0.0 <= numeric <= 10.0:
            raise RuntimeError(f"LOCKED_GOLDEN_SCORE_OUT_OF_RANGE:{field}")
        return numeric

    def evaluate(
        self,
        *,
        semantic_review_path: str,
        review_path: str,
        output_dir: str,
    ) -> dict[str, object]:
        semantic, locked_png, actual_sha = self._validated_semantic_receipt(semantic_review_path)
        review_file = Path(review_path).resolve()
        review = self._load_json(review_file, error="LOCKED_GOLDEN_REVIEW_INVALID_JSON")
        if review.get("review_version") != LOCKED_GOLDEN_REVIEW_VERSION:
            raise RuntimeError("LOCKED_GOLDEN_REVIEW_VERSION_INVALID")
        if review.get("status") != "LOCKED_GOLDEN_VISUAL_REVIEW_TEMPLATE":
            raise RuntimeError("LOCKED_GOLDEN_REVIEW_STATUS_INVALID")
        if review.get("publication_ready") is not False:
            raise RuntimeError("LOCKED_GOLDEN_REVIEW_MUST_BE_NON_PUBLICATION")
        for key in ("candidate", "request_id", "seed"):
            if review.get(key) != semantic.get(key):
                raise RuntimeError(f"LOCKED_GOLDEN_REVIEW_IDENTITY_MISMATCH:{key}")
        if review.get("locked_png_sha256") != actual_sha:
            raise RuntimeError("LOCKED_GOLDEN_REVIEW_SHA256_MISMATCH")
        review_png = self._resolve(
            review.get("locked_png"), relative_to=review_file.parent, error="LOCKED_GOLDEN_REVIEW_PNG_MISSING"
        )
        if review_png != locked_png:
            raise RuntimeError("LOCKED_GOLDEN_REVIEW_PNG_PATH_MISMATCH")

        scores_data = review.get("scores")
        blockers_data = review.get("blockers")
        if not isinstance(scores_data, dict) or set(scores_data) != set(_SCORE_FIELDS):
            raise RuntimeError("LOCKED_GOLDEN_SCORE_SCHEMA_MISMATCH")
        if not isinstance(blockers_data, dict) or set(blockers_data) != set(_BLOCKER_FIELDS):
            raise RuntimeError("LOCKED_GOLDEN_BLOCKER_SCHEMA_MISMATCH")
        for field in _BLOCKER_FIELDS:
            if not isinstance(blockers_data[field], bool):
                raise RuntimeError(f"LOCKED_GOLDEN_BLOCKER_INVALID:{field}")

        scores = GoldenVisualScores(**{field: self._score(scores_data[field], field=field) for field in _SCORE_FIELDS})
        blockers = GoldenVisualBlockers(**{field: blockers_data[field] for field in _BLOCKER_FIELDS})
        evaluation = GoldenVisualEvaluation(str(semantic["request_id"]), int(semantic["seed"]), scores, blockers)

        target = Path(output_dir).resolve()
        target.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "status": "LOCKED_GOLDEN_VISUAL_APPROVED" if evaluation.approved else "LOCKED_GOLDEN_VISUAL_REJECTED",
            "candidate": semantic["candidate"],
            "request_id": evaluation.request_id,
            "seed": evaluation.seed,
            "semantic_review": str(Path(semantic_review_path).resolve()),
            "review_file": str(review_file),
            "locked_png": str(locked_png),
            "locked_png_sha256": actual_sha,
            "weighted_score": evaluation.scores.weighted_score,
            "quality_tier": evaluation.quality_tier,
            "scores": {field: float(getattr(evaluation.scores, field)) for field in _SCORE_FIELDS},
            "blockers": list(evaluation.blockers.active),
            "golden_quality_approved": evaluation.approved,
            "publication_ready": False,
            "gates_not_waived": sorted(_REQUIRED_UNWAIVED_GATES),
            "next_gate": (
                "Exact approved brand/typography composition may proceed only if golden_quality_approved=true; "
                "SemanticPublicationGate and final publication readiness remain mandatory."
            ),
        }
        receipt_path = target / f"candidate-{int(semantic['candidate']):02d}-locked-golden-review.json"
        receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        payload["receipt"] = str(receipt_path)
        return payload
