"""Bind human-approved Golden scoring to the replay-verified first-Golden packet.

This layer closes the remaining evidence gap between the tamper-evident human
review packet and the existing HumanApprovedGoldenVisualReviewGate. It does not
invent scores, approve publication, or change any upstream authority. Golden
review may proceed only when the sealed packet replays cleanly and proves the
Original Scene runtime admission that produced Candidate 1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.first_golden_review_packet_integrity import (
    FirstGoldenReviewPacketIntegrity,
    VERIFY_SCHEMA,
)
from engine.intelligence.human_approved_golden_visual_review import HumanApprovedGoldenVisualReviewGate

SEALED_SCHEMA = "pul7sar-first-golden-human-review-sealed-v1"
SEALED_STATUS = "FIRST_GOLDEN_CANDIDATE_READY_FOR_VERIFIED_HUMAN_REVIEW"
ADMISSION_SCHEMA = "pul7sar-golden-original-scene-admission-v1"
ADMISSION_STATUS = "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED"


class SealedHumanApprovedGoldenReviewGate:
    def __init__(self, *, root: Path) -> None:
        self.root = root.resolve()
        self._packet_integrity = FirstGoldenReviewPacketIntegrity(root=self.root)
        self._golden = HumanApprovedGoldenVisualReviewGate(root=self.root)

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
            raise RuntimeError(f"SEALED_HUMAN_GOLDEN_{label}_ESCAPES_REPOSITORY")
        return path

    @staticmethod
    def _load_json(path: Path, *, error: str) -> dict[str, Any]:
        if not path.is_file():
            raise RuntimeError(error)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(error) from exc
        if not isinstance(payload, dict):
            raise RuntimeError(error)
        return payload

    def _verify_sealed_packet(self, sealed_path: str | Path) -> dict[str, Any]:
        sealed_file = self._inside_root(sealed_path, label="SEALED_PACKET")
        sealed = self._load_json(sealed_file, error="SEALED_HUMAN_GOLDEN_PACKET_INVALID")
        expected = {
            "schema": SEALED_SCHEMA,
            "status": SEALED_STATUS,
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        failures = [f"{key}={sealed.get(key)!r}" for key, value in expected.items() if sealed.get(key) != value]
        if failures:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_PACKET_STATE_DRIFT: " + "; ".join(failures))

        manifest_file = self._inside_root(str(sealed.get("integrity_manifest", "")), label="MANIFEST")
        verification_file = self._inside_root(str(sealed.get("integrity_verification", "")), label="VERIFICATION")
        manifest = self._load_json(manifest_file, error="SEALED_HUMAN_GOLDEN_MANIFEST_INVALID")
        verification = self._load_json(verification_file, error="SEALED_HUMAN_GOLDEN_VERIFICATION_INVALID")

        decision = self._packet_integrity.verify_manifest(manifest=manifest)
        if not decision.verified:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_MANIFEST_REPLAY_FAILED: " + "; ".join(decision.failures))
        if sealed.get("manifest_sha256") != decision.manifest_sha256:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_MANIFEST_SHA256_MISMATCH")
        if verification.get("schema") != VERIFY_SCHEMA:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_VERIFICATION_SCHEMA_MISMATCH")
        if verification.get("status") != "FIRST_GOLDEN_REVIEW_PACKET_INTEGRITY_VERIFIED" or verification.get("verified") is not True:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_VERIFICATION_NOT_PROVEN")
        if verification.get("manifest_sha256") != decision.manifest_sha256:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_VERIFICATION_SHA256_MISMATCH")
        if verification.get("original_scene_runtime_admission_bound") is not True:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_ORIGINAL_SCENE_NOT_BOUND")
        for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
            if verification.get(field) is not False:
                raise RuntimeError(f"SEALED_HUMAN_GOLDEN_VERIFICATION_{field.upper()}_AUTHORITY_DRIFT")

        records = manifest.get("files")
        if not isinstance(records, list):
            raise RuntimeError("SEALED_HUMAN_GOLDEN_MANIFEST_FILE_SET_INVALID")
        record_by_field = {item.get("field"): item for item in records if isinstance(item, dict)}
        admission_record = record_by_field.get("original_scene_runtime_admission")
        if not isinstance(admission_record, dict):
            raise RuntimeError("SEALED_HUMAN_GOLDEN_ORIGINAL_SCENE_EVIDENCE_MISSING")
        admission_file = self._inside_root(str(admission_record.get("path", "")), label="ORIGINAL_SCENE_ADMISSION")
        admission = self._load_json(admission_file, error="SEALED_HUMAN_GOLDEN_ORIGINAL_SCENE_ADMISSION_INVALID")
        if self._sha256(admission_file) != admission_record.get("sha256"):
            raise RuntimeError("SEALED_HUMAN_GOLDEN_ORIGINAL_SCENE_ADMISSION_SHA256_MISMATCH")
        admission_expected = {
            "schema": ADMISSION_SCHEMA,
            "status": ADMISSION_STATUS,
            "candidate": 1,
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failures = [f"{key}={admission.get(key)!r}" for key, value in admission_expected.items() if admission.get(key) != value]
        if failures:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_ORIGINAL_SCENE_STATE_DRIFT: " + "; ".join(failures))

        return {
            "sealed_packet": str(sealed_file),
            "sealed_packet_sha256": self._sha256(sealed_file),
            "manifest": str(manifest_file),
            "manifest_sha256": decision.manifest_sha256,
            "verification": str(verification_file),
            "verification_sha256": self._sha256(verification_file),
            "original_scene_runtime_admission": str(admission_file),
            "original_scene_runtime_admission_sha256": self._sha256(admission_file),
        }

    def build_template(
        self,
        *,
        sealed_packet_path: str | Path,
        handoff_path: str | Path,
        continuation_path: str | Path,
        human_decision_path: str | Path,
    ) -> dict[str, object]:
        seal = self._verify_sealed_packet(sealed_packet_path)
        payload = self._golden.build_template(
            handoff_path=handoff_path,
            continuation_path=continuation_path,
            human_decision_path=human_decision_path,
        )
        payload.update(seal)
        payload["sealed_packet_verified"] = True
        payload["original_scene_runtime_admission_bound"] = True
        payload["publication_ready"] = False
        return payload

    def evaluate(
        self,
        *,
        sealed_packet_path: str | Path,
        handoff_path: str | Path,
        continuation_path: str | Path,
        human_decision_path: str | Path,
        review_path: str | Path,
        output_dir: str | Path,
    ) -> dict[str, object]:
        seal = self._verify_sealed_packet(sealed_packet_path)
        review_file = self._inside_root(review_path, label="REVIEW")
        review = self._load_json(review_file, error="SEALED_HUMAN_GOLDEN_REVIEW_INVALID")
        for field in (
            "sealed_packet_sha256",
            "manifest_sha256",
            "verification_sha256",
            "original_scene_runtime_admission_sha256",
        ):
            if review.get(field) != seal.get(field):
                raise RuntimeError(f"SEALED_HUMAN_GOLDEN_REVIEW_BINDING_MISMATCH:{field}")
        if review.get("sealed_packet_verified") is not True or review.get("original_scene_runtime_admission_bound") is not True:
            raise RuntimeError("SEALED_HUMAN_GOLDEN_REVIEW_SEAL_BINDING_MISSING")

        payload = self._golden.evaluate(
            handoff_path=handoff_path,
            continuation_path=continuation_path,
            human_decision_path=human_decision_path,
            review_path=review_file,
            output_dir=output_dir,
        )
        payload.update(seal)
        payload["sealed_packet_verified"] = True
        payload["original_scene_runtime_admission_bound"] = True
        payload["publication_ready"] = False
        return payload
