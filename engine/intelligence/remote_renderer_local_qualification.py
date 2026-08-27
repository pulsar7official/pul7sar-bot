"""Fail-closed research-to-local qualification docket for Phase 18 renderers.

A remote ZeroGPU research leader may justify *measuring* the same renderer (or a
locally equivalent implementation) later, but remote evidence can never become
canonical Golden evidence. This module converts a byte-bound research ledger
into a non-authoritative local-qualification docket only when the research
leader is blocker-free and strong enough to justify scarce GPU time.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LEDGER_SCHEMA = "pul7sar-phase18-remote-renderer-research-ledger-v1"
DOCKET_SCHEMA = "pul7sar-phase18-remote-renderer-local-qualification-v1"
REMOTE_COST_MODE = "$0-remote-zerogpu-study"
QUALIFICATION_SCORE_FLOOR = 8.5
MIN_GEOMETRY_SCORE = 8.5
MIN_ENTITY_NEUTRALITY_SCORE = 9.0
MIN_TEXT_BRAND_CLEANLINESS_SCORE = 9.0
REQUIRED_LOCAL_GATES = (
    "explicit_local_model_candidate",
    "pinned_model_revision",
    "measured_$0-local_runtime_readiness",
    "cuda_and_required_precision",
    "live_vram_and_host_ram",
    "safe_local_offload_if_required",
    "renderer_safe_identity_neutral_prompt",
    "generation_and_execution_provenance",
    "semantic_and_layer_ownership_review",
    "byte_bound_visual_critic",
    "explicit_human_review",
    "golden_visual_quality_8.5_minimum",
    "exact_brand_and_typography_integrity",
    "semantic_publication_gate",
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(raw)


def _require_repo_path(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    root = repo_root.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"REMOTE_LOCAL_QUALIFICATION_PATH_ESCAPE: {resolved}")
    return resolved


def _verify_ledger_digest(ledger: dict[str, Any]) -> str:
    claimed = ledger.get("ledger_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEDGER_SHA_INVALID")
    unsigned = dict(ledger)
    unsigned.pop("ledger_sha256", None)
    actual = _sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEDGER_SHA_MISMATCH")
    return actual


def _validate_noncanonical_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEDGER_SCHEMA_MISMATCH")
    if ledger.get("cost_mode") != REMOTE_COST_MODE:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_REMOTE_COST_MODE_MISMATCH")
    if ledger.get("research_only") is not True or ledger.get("canonical_admission_required") is not True:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_RESEARCH_BOUNDARY_MISSING")
    forbidden_true = (
        "canonical_golden_eligible",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    )
    if any(ledger.get(field) is not False for field in forbidden_true):
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_REMOTE_AUTHORITY_FORBIDDEN")


def _leader_entry(ledger: dict[str, Any]) -> dict[str, Any]:
    leader = ledger.get("research_leader")
    leader_sha = ledger.get("research_leader_output_sha256")
    if not isinstance(leader, str) or not leader:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_NO_RESEARCH_LEADER")
    if not isinstance(leader_sha, str) or len(leader_sha) != 64:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEADER_OUTPUT_SHA_INVALID")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEDGER_ENTRIES_MISSING")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("renderer") == leader]
    if len(matches) != 1:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEADER_ENTRY_AMBIGUOUS")
    entry = matches[0]
    if entry.get("output_sha256") != leader_sha:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEADER_OUTPUT_MISMATCH")
    return entry


def _validate_research_strength(entry: dict[str, Any]) -> None:
    if entry.get("blocker_free") is not True or entry.get("research_score_floor_met") is not True:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_RESEARCH_BLOCKED")
    average = entry.get("average_score")
    if not isinstance(average, (int, float)) or isinstance(average, bool) or float(average) < QUALIFICATION_SCORE_FLOOR:
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_SCORE_BELOW_QUALIFICATION_FLOOR")
    scores = entry.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("REMOTE_LOCAL_QUALIFICATION_SCORES_MISSING")
    thresholds = {
        "geometry_integrity": MIN_GEOMETRY_SCORE,
        "entity_neutrality": MIN_ENTITY_NEUTRALITY_SCORE,
        "text_and_brand_cleanliness": MIN_TEXT_BRAND_CLEANLINESS_SCORE,
    }
    for field, minimum in thresholds.items():
        value = scores.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) < minimum:
            raise ValueError(f"REMOTE_LOCAL_QUALIFICATION_CRITICAL_SCORE_BELOW_FLOOR: {field}")


@dataclass(frozen=True)
class RemoteRendererLocalQualificationDocketBuilder:
    repo_root: Path

    def build(self, *, research_ledger_path: Path) -> dict[str, Any]:
        ledger_path = _require_repo_path(research_ledger_path, self.repo_root)
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        _validate_noncanonical_ledger(ledger)
        ledger_digest = _verify_ledger_digest(ledger)
        entry = _leader_entry(ledger)
        _validate_research_strength(entry)

        output = entry.get("output")
        if not isinstance(output, str) or not output:
            raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEADER_OUTPUT_PATH_INVALID")
        output_path = _require_repo_path(Path(output), self.repo_root)
        actual_output_sha = _sha256_file(output_path)
        if actual_output_sha != entry.get("output_sha256"):
            raise ValueError("REMOTE_LOCAL_QUALIFICATION_LEADER_PNG_SHA_MISMATCH")

        payload = {
            "schema": DOCKET_SCHEMA,
            "status": "REMOTE_RENDERER_LOCAL_QUALIFICATION_DOCKET_READY",
            "research_ledger": str(ledger_path),
            "research_ledger_file_sha256": _sha256_file(ledger_path),
            "research_ledger_sha256": ledger_digest,
            "renderer": entry.get("renderer"),
            "remote_space": entry.get("space"),
            "research_output": str(output_path),
            "research_output_sha256": actual_output_sha,
            "research_average_score": float(entry.get("average_score")),
            "research_scores": dict(entry.get("scores") or {}),
            "qualification_score_floor": QUALIFICATION_SCORE_FLOOR,
            "critical_score_floors": {
                "geometry_integrity": MIN_GEOMETRY_SCORE,
                "entity_neutrality": MIN_ENTITY_NEUTRALITY_SCORE,
                "text_and_brand_cleanliness": MIN_TEXT_BRAND_CLEANLINESS_SCORE,
            },
            "research_signal_only": True,
            "recommended_for_local_measurement": True,
            "requires_explicit_local_model_candidate": True,
            "local_model_candidate_id": None,
            "local_runtime_qualified": False,
            "canonical_generation_authorized": False,
            "remote_pixels_reusable_as_canonical_evidence": False,
            "required_local_gates": list(REQUIRED_LOCAL_GATES),
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "remote_cost_mode": REMOTE_COST_MODE,
            "canonical_cost_mode_required": "$0-local",
        }
        payload["docket_sha256"] = _sha256_json(payload)
        return payload
