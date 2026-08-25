"""Tamper-evident integrity seal for the first Golden human-review packet.

This layer does not generate, score, approve, or publish anything. It binds the
Candidate 1 review packet to the exact receipts and PNG bytes that produced the
human-review staging result, then supports replay verification before a human
opens or acts on the packet.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PACKET_SCHEMA = "pul7sar-first-golden-human-review-packet-v1"
PACKET_STATUS = "FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW"
MANIFEST_SCHEMA = "pul7sar-first-golden-review-integrity-manifest-v1"
VERIFY_SCHEMA = "pul7sar-first-golden-review-integrity-verification-v1"


@dataclass(frozen=True)
class FirstGoldenReviewIntegrityDecision:
    verified: bool
    failures: tuple[str, ...]
    manifest_sha256: str


class FirstGoldenReviewPacketIntegrity:
    _REQUIRED_FILE_FIELDS = (
        "first_png_result",
        "hybrid_handoff",
        "hybrid_semantic_continuation",
        "human_review_bundle",
        "human_review_template",
        "review_base_png",
        "review_hybrid_png",
    )

    def __init__(self, *, root: Path) -> None:
        self.root = root.resolve()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _canonical_sha(payload: dict[str, Any]) -> str:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    def _inside_root(self, value: str | Path, *, label: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        path = path.resolve()
        if path != self.root and self.root not in path.parents:
            raise RuntimeError(f"FIRST_GOLDEN_REVIEW_INTEGRITY_{label}_ESCAPES_REPOSITORY")
        return path

    @staticmethod
    def _require_png(path: Path, *, label: str) -> None:
        if not path.is_file() or path.read_bytes()[:8] != PNG_SIGNATURE:
            raise RuntimeError(f"FIRST_GOLDEN_REVIEW_INTEGRITY_{label}_INVALID_PNG")

    @staticmethod
    def _require_packet_authority_closed(packet: dict[str, Any]) -> None:
        if packet.get("schema") != PACKET_SCHEMA or packet.get("status") != PACKET_STATUS:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_PACKET_CONTRACT_MISMATCH")
        if packet.get("candidate") != 1:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_REQUIRES_CANDIDATE_1")
        if packet.get("branch") != "phase18/story-intelligence":
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_BRANCH_DRIFT")
        if packet.get("cost_mode") != "$0-local":
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_COST_MODE_DRIFT")
        if packet.get("human_visual_review_required") is not True:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_HUMAN_REVIEW_NOT_REQUIRED")
        if packet.get("automatic_selection_performed") is not False:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_AUTOMATIC_SELECTION_DRIFT")
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            if packet.get(field) is not False:
                raise RuntimeError(f"FIRST_GOLDEN_REVIEW_INTEGRITY_{field.upper()}_AUTHORITY_DRIFT")

    def build_manifest(self, *, packet_path: str | Path) -> dict[str, Any]:
        packet_file = self._inside_root(packet_path, label="PACKET")
        if not packet_file.is_file():
            raise FileNotFoundError(packet_file)
        packet = json.loads(packet_file.read_text(encoding="utf-8"))
        if not isinstance(packet, dict):
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_PACKET_NOT_OBJECT")
        self._require_packet_authority_closed(packet)

        records: list[dict[str, Any]] = []
        seen: set[Path] = set()
        for field in self._REQUIRED_FILE_FIELDS:
            raw = packet.get(field)
            if not isinstance(raw, str) or not raw.strip():
                raise RuntimeError(f"FIRST_GOLDEN_REVIEW_INTEGRITY_{field.upper()}_MISSING")
            path = self._inside_root(raw, label=field.upper())
            if path in seen:
                raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_DUPLICATE_EVIDENCE_PATH")
            seen.add(path)
            if not path.is_file():
                raise FileNotFoundError(path)
            if field in {"review_base_png", "review_hybrid_png"}:
                self._require_png(path, label=field.upper())
            records.append(
                {
                    "field": field,
                    "path": str(path),
                    "sha256": self._sha256(path),
                    "bytes": path.stat().st_size,
                }
            )

        record_by_field = {item["field"]: item for item in records}
        if packet.get("review_base_png_sha256") != record_by_field["review_base_png"]["sha256"]:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_BASE_SHA256_MISMATCH")
        if packet.get("review_hybrid_png_sha256") != record_by_field["review_hybrid_png"]["sha256"]:
            raise RuntimeError("FIRST_GOLDEN_REVIEW_INTEGRITY_HYBRID_SHA256_MISMATCH")

        body: dict[str, Any] = {
            "schema": MANIFEST_SCHEMA,
            "status": "FIRST_GOLDEN_REVIEW_PACKET_SEALED",
            "candidate": 1,
            "branch": "phase18/story-intelligence",
            "cost_mode": "$0-local",
            "packet_path": str(packet_file),
            "packet_sha256": self._sha256(packet_file),
            "files": records,
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        return {**body, "manifest_sha256": self._canonical_sha(body)}

    def verify_manifest(self, *, manifest: dict[str, Any]) -> FirstGoldenReviewIntegrityDecision:
        failures: list[str] = []
        if manifest.get("schema") != MANIFEST_SCHEMA:
            failures.append("manifest_schema_mismatch")
        if manifest.get("status") != "FIRST_GOLDEN_REVIEW_PACKET_SEALED":
            failures.append("manifest_status_mismatch")
        if manifest.get("candidate") != 1:
            failures.append("candidate_mismatch")
        if manifest.get("branch") != "phase18/story-intelligence":
            failures.append("branch_mismatch")
        if manifest.get("cost_mode") != "$0-local":
            failures.append("cost_mode_mismatch")
        if manifest.get("human_visual_review_required") is not True:
            failures.append("human_review_requirement_missing")
        if manifest.get("automatic_selection_performed") is not False:
            failures.append("automatic_selection_drift")
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            if manifest.get(field) is not False:
                failures.append(f"{field}_authority_drift")

        claimed_manifest_sha = manifest.get("manifest_sha256")
        body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        actual_manifest_sha = self._canonical_sha(body)
        if not isinstance(claimed_manifest_sha, str) or claimed_manifest_sha != actual_manifest_sha:
            failures.append("manifest_sha256_mismatch")

        packet_raw = manifest.get("packet_path")
        if not isinstance(packet_raw, str) or not packet_raw:
            failures.append("packet_path_missing")
        else:
            try:
                packet = self._inside_root(packet_raw, label="PACKET")
            except RuntimeError:
                failures.append("packet_path_escape")
            else:
                if not packet.is_file():
                    failures.append("packet_missing")
                elif self._sha256(packet) != manifest.get("packet_sha256"):
                    failures.append("packet_sha256_mismatch")

        files = manifest.get("files")
        if not isinstance(files, list) or len(files) != len(self._REQUIRED_FILE_FIELDS):
            failures.append("evidence_file_set_invalid")
        else:
            observed_fields: set[str] = set()
            observed_paths: set[Path] = set()
            for item in files:
                if not isinstance(item, dict):
                    failures.append("evidence_record_invalid")
                    continue
                field = item.get("field")
                raw_path = item.get("path")
                if field not in self._REQUIRED_FILE_FIELDS or field in observed_fields:
                    failures.append("evidence_field_invalid_or_duplicate")
                    continue
                observed_fields.add(field)
                if not isinstance(raw_path, str):
                    failures.append(f"{field}_path_missing")
                    continue
                try:
                    path = self._inside_root(raw_path, label=str(field).upper())
                except RuntimeError:
                    failures.append(f"{field}_path_escape")
                    continue
                if path in observed_paths:
                    failures.append("duplicate_evidence_path")
                    continue
                observed_paths.add(path)
                if not path.is_file():
                    failures.append(f"{field}_missing")
                    continue
                if field in {"review_base_png", "review_hybrid_png"} and path.read_bytes()[:8] != PNG_SIGNATURE:
                    failures.append(f"{field}_invalid_png")
                if self._sha256(path) != item.get("sha256"):
                    failures.append(f"{field}_sha256_mismatch")
                if path.stat().st_size != item.get("bytes"):
                    failures.append(f"{field}_size_mismatch")
            if observed_fields != set(self._REQUIRED_FILE_FIELDS):
                failures.append("evidence_fields_incomplete")

        return FirstGoldenReviewIntegrityDecision(
            verified=not failures,
            failures=tuple(dict.fromkeys(failures)),
            manifest_sha256=actual_manifest_sha,
        )


def verification_payload(decision: FirstGoldenReviewIntegrityDecision) -> dict[str, Any]:
    return {
        "schema": VERIFY_SCHEMA,
        "status": "FIRST_GOLDEN_REVIEW_PACKET_INTEGRITY_VERIFIED" if decision.verified else "FIRST_GOLDEN_REVIEW_PACKET_INTEGRITY_FAILED",
        "verified": decision.verified,
        "failures": list(decision.failures),
        "manifest_sha256": decision.manifest_sha256,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
