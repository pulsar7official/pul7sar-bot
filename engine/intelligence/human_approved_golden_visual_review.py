"""Golden Visual review bound to the accepted human Hybrid decision.

This gate closes the gap between the SHA-bound human integration review and the
Golden 8.5/9.0 scorecard. It consumes three independent evidence artifacts:

- the provenance-bound first-PNG Hybrid handoff (request/seed/base identity),
- the successful Hybrid semantic continuation (exact Hybrid artifact), and
- the accepted SHA-bound human review decision.

No score is invented, no publication authority is granted, and every image path
is re-hashed before Golden quality can be evaluated.
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


REVIEW_VERSION = "pul7sar-human-approved-golden-review-v1"
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST = "pul7sar-golden-batch-v5"
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
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class HumanApprovedGoldenVisualReviewGate:
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
            raise RuntimeError(f"HUMAN_GOLDEN_{label}_ESCAPES_REPOSITORY")
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
            raise RuntimeError(f"HUMAN_GOLDEN_{label}_INVALID_PNG")

    def _validate_chain(
        self,
        *,
        handoff_path: str | Path,
        continuation_path: str | Path,
        human_decision_path: str | Path,
    ) -> dict[str, object]:
        handoff_file = self._inside_root(handoff_path, label="HANDOFF")
        continuation_file = self._inside_root(continuation_path, label="CONTINUATION")
        decision_file = self._inside_root(human_decision_path, label="DECISION")
        handoff = self._load_json(handoff_file, error="HUMAN_GOLDEN_HANDOFF_INVALID")
        continuation = self._load_json(continuation_file, error="HUMAN_GOLDEN_CONTINUATION_INVALID")
        decision = self._load_json(decision_file, error="HUMAN_GOLDEN_DECISION_INVALID")

        expected_handoff = {
            "status": "FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY",
            "branch": EXPECTED_BRANCH,
            "manifest_version": EXPECTED_MANIFEST,
            "candidate": 1,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failures = [f"{k}={handoff.get(k)!r}" for k, v in expected_handoff.items() if handoff.get(k) != v]
        if failures:
            raise RuntimeError("HUMAN_GOLDEN_HANDOFF_STATE_DRIFT: " + "; ".join(failures))
        request_id = handoff.get("request_id")
        seed = handoff.get("seed")
        if not isinstance(request_id, str) or not request_id.strip():
            raise RuntimeError("HUMAN_GOLDEN_REQUEST_ID_INVALID")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise RuntimeError("HUMAN_GOLDEN_SEED_INVALID")

        base = self._inside_root(str(handoff.get("png", "")), label="BASE")
        self._require_png(base, label="BASE")
        base_sha = self._sha256(base)
        if handoff.get("base_png_sha256") != base_sha:
            raise RuntimeError("HUMAN_GOLDEN_BASE_SHA256_MISMATCH")

        expected_continuation = {
            "status": "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY",
            "branch": EXPECTED_BRANCH,
            "manifest_version": EXPECTED_MANIFEST,
            "candidate": 1,
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failures = [
            f"{k}={continuation.get(k)!r}" for k, v in expected_continuation.items()
            if continuation.get(k) != v
        ]
        if failures:
            raise RuntimeError("HUMAN_GOLDEN_CONTINUATION_STATE_DRIFT: " + "; ".join(failures))
        artifact = continuation.get("artifact_integrity")
        if not isinstance(artifact, dict) or artifact.get("valid") is not True:
            raise RuntimeError("HUMAN_GOLDEN_ARTIFACT_INTEGRITY_NOT_PROVEN")
        continuation_base = self._inside_root(str(continuation.get("base_png", "")), label="CONTINUATION_BASE")
        if continuation_base != base or artifact.get("input_sha256") != base_sha:
            raise RuntimeError("HUMAN_GOLDEN_BASE_CHAIN_MISMATCH")

        hybrid = self._inside_root(str(continuation.get("hybrid_png", "")), label="HYBRID")
        self._require_png(hybrid, label="HYBRID")
        hybrid_sha = self._sha256(hybrid)
        if continuation.get("hybrid_png_sha256") != hybrid_sha or artifact.get("output_sha256") != hybrid_sha:
            raise RuntimeError("HUMAN_GOLDEN_HYBRID_SHA256_MISMATCH")

        expected_decision = {
            "schema": "pul7sar-hybrid-human-review-decision-v1",
            "status": "HYBRID_HUMAN_REVIEW_ACCEPTED",
            "candidate": 1,
            "human_visual_review_approved": True,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failures = [f"{k}={decision.get(k)!r}" for k, v in expected_decision.items() if decision.get(k) != v]
        if failures:
            raise RuntimeError("HUMAN_GOLDEN_HUMAN_DECISION_NOT_ACCEPTED: " + "; ".join(failures))
        if decision.get("base_png_sha256") != base_sha or decision.get("hybrid_png_sha256") != hybrid_sha:
            raise RuntimeError("HUMAN_GOLDEN_HUMAN_DECISION_SHA_MISMATCH")
        review_hybrid = self._inside_root(str(decision.get("review_hybrid_png", "")), label="REVIEW_HYBRID")
        self._require_png(review_hybrid, label="REVIEW_HYBRID")
        if self._sha256(review_hybrid) != hybrid_sha:
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_HYBRID_SHA256_MISMATCH")

        return {
            "request_id": request_id,
            "seed": seed,
            "candidate": 1,
            "base_png": str(base),
            "base_png_sha256": base_sha,
            "hybrid_png": str(hybrid),
            "hybrid_png_sha256": hybrid_sha,
            "review_hybrid_png": str(review_hybrid),
            "handoff": str(handoff_file),
            "handoff_sha256": self._sha256(handoff_file),
            "continuation": str(continuation_file),
            "continuation_sha256": self._sha256(continuation_file),
            "human_decision": str(decision_file),
            "human_decision_sha256": self._sha256(decision_file),
        }

    def build_template(
        self,
        *,
        handoff_path: str | Path,
        continuation_path: str | Path,
        human_decision_path: str | Path,
    ) -> dict[str, object]:
        chain = self._validate_chain(
            handoff_path=handoff_path,
            continuation_path=continuation_path,
            human_decision_path=human_decision_path,
        )
        return {
            "review_version": REVIEW_VERSION,
            "status": "HUMAN_APPROVED_GOLDEN_VISUAL_REVIEW_TEMPLATE",
            **chain,
            "scores": {field: None for field in _SCORE_FIELDS},
            "blockers": {field: False for field in _BLOCKER_FIELDS},
            "review_note": "",
            "human_visual_review_approved": True,
            "golden_quality_approved": False,
            "publication_ready": False,
            "gates_not_waived": sorted(_REQUIRED_UNWAIVED_GATES),
            "instructions": (
                "Score only the exact SHA-bound Hybrid PNG that already passed semantic and explicit human integration review. "
                "Fill every 0-10 score and every hard-blocker field. Do not alter evidence paths, hashes, request_id or seed."
            ),
        }

    @staticmethod
    def _score(value: object, *, field: str) -> float:
        if value is None:
            raise RuntimeError(f"HUMAN_GOLDEN_SCORE_STILL_NULL:{field}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RuntimeError(f"HUMAN_GOLDEN_SCORE_INVALID:{field}")
        numeric = float(value)
        if not 0.0 <= numeric <= 10.0:
            raise RuntimeError(f"HUMAN_GOLDEN_SCORE_OUT_OF_RANGE:{field}")
        return numeric

    def evaluate(
        self,
        *,
        handoff_path: str | Path,
        continuation_path: str | Path,
        human_decision_path: str | Path,
        review_path: str | Path,
        output_dir: str | Path,
    ) -> dict[str, object]:
        chain = self._validate_chain(
            handoff_path=handoff_path,
            continuation_path=continuation_path,
            human_decision_path=human_decision_path,
        )
        review_file = self._inside_root(review_path, label="REVIEW")
        review = self._load_json(review_file, error="HUMAN_GOLDEN_REVIEW_INVALID")
        if review.get("review_version") != REVIEW_VERSION or review.get("status") != "HUMAN_APPROVED_GOLDEN_VISUAL_REVIEW_TEMPLATE":
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_CONTRACT_INVALID")
        if review.get("publication_ready") is not False or review.get("golden_quality_approved") is not False:
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_DOWNSTREAM_AUTHORITY_DRIFT")
        if review.get("human_visual_review_approved") is not True:
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_HUMAN_APPROVAL_MISSING")
        for field in (
            "request_id", "seed", "candidate", "base_png_sha256", "hybrid_png_sha256",
            "handoff_sha256", "continuation_sha256", "human_decision_sha256",
        ):
            if review.get(field) != chain.get(field):
                raise RuntimeError(f"HUMAN_GOLDEN_REVIEW_BINDING_MISMATCH:{field}")
        if review.get("review_hybrid_png") != chain["review_hybrid_png"]:
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_HYBRID_PATH_MISMATCH")
        gates = review.get("gates_not_waived")
        if not isinstance(gates, list) or not _REQUIRED_UNWAIVED_GATES.issubset(set(gates)):
            raise RuntimeError("HUMAN_GOLDEN_REVIEW_GATES_NOT_PRESERVED")

        scores_data = review.get("scores")
        blockers_data = review.get("blockers")
        if not isinstance(scores_data, dict) or set(scores_data) != set(_SCORE_FIELDS):
            raise RuntimeError("HUMAN_GOLDEN_SCORE_SCHEMA_MISMATCH")
        if not isinstance(blockers_data, dict) or set(blockers_data) != set(_BLOCKER_FIELDS):
            raise RuntimeError("HUMAN_GOLDEN_BLOCKER_SCHEMA_MISMATCH")
        for field in _BLOCKER_FIELDS:
            if not isinstance(blockers_data[field], bool):
                raise RuntimeError(f"HUMAN_GOLDEN_BLOCKER_INVALID:{field}")

        scores = GoldenVisualScores(**{field: self._score(scores_data[field], field=field) for field in _SCORE_FIELDS})
        blockers = GoldenVisualBlockers(**{field: blockers_data[field] for field in _BLOCKER_FIELDS})
        evaluation = GoldenVisualEvaluation(str(chain["request_id"]), int(chain["seed"]), scores, blockers)

        target = self._inside_root(output_dir, label="OUTPUT_DIR")
        target.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": REVIEW_VERSION,
            "status": "HUMAN_APPROVED_GOLDEN_VISUAL_APPROVED" if evaluation.approved else "HUMAN_APPROVED_GOLDEN_VISUAL_REJECTED",
            **chain,
            "review_file": str(review_file),
            "review_file_sha256": self._sha256(review_file),
            "weighted_score": evaluation.scores.weighted_score,
            "quality_tier": evaluation.quality_tier,
            "scores": {field: float(getattr(evaluation.scores, field)) for field in _SCORE_FIELDS},
            "blockers": list(evaluation.blockers.active),
            "human_visual_review_approved": True,
            "golden_quality_approved": evaluation.approved,
            "publication_ready": False,
            "gates_not_waived": sorted(_REQUIRED_UNWAIVED_GATES),
            "next_gate": (
                "Exact approved brand and typography composition may proceed only after Golden approval; "
                "SemanticPublicationGate and final publication readiness remain mandatory."
            ),
        }
        receipt = target / "candidate-01-human-approved-golden-review.json"
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        payload["receipt"] = str(receipt)
        return payload
