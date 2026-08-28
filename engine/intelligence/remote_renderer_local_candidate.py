"""Fail-closed explicit local-model declaration for remote renderer research leaders.

Remote ZeroGPU evidence may justify measuring a renderer locally, but it may not
select or authorize a canonical model by itself. This module requires an
explicit caller-supplied PUL7SAR ``LocalModelCandidate`` identifier and only
accepts an exact curated model match for the research renderer. The result is a
non-authoritative declaration: pinned model revision, measured runtime
readiness, genuine local generation, semantic review, human review and Golden
quality all remain downstream requirements.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.intelligence.cost_policy import BillingClass
from engine.intelligence.zero_cost_models import LocalModelCandidate, ZERO_COST_LOCAL_CANDIDATES


DOCKET_SCHEMA = "pul7sar-phase18-remote-renderer-local-qualification-v1"
DECLARATION_SCHEMA = "pul7sar-phase18-remote-renderer-explicit-local-candidate-v1"
CANONICAL_COST_MODE = "$0-local"

# Deliberately strict. A research renderer may only nominate the exact curated
# local model profile for the same upstream model family. Similar-looking or
# smaller variants are not silently treated as equivalent Golden candidates.
REMOTE_RENDERER_EXACT_LOCAL_MODEL = {
    "qwen-image-2512": "Qwen/Qwen-Image-2512",
}


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
        raise ValueError(f"REMOTE_LOCAL_CANDIDATE_PATH_ESCAPE: {resolved}")
    return resolved


def _verify_docket_digest(docket: dict[str, Any]) -> str:
    claimed = docket.get("docket_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_SHA_INVALID")
    unsigned = dict(docket)
    unsigned.pop("docket_sha256", None)
    actual = _sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_SHA_MISMATCH")
    return actual


def _validate_docket(docket: dict[str, Any]) -> None:
    if docket.get("schema") != DOCKET_SCHEMA:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_SCHEMA_MISMATCH")
    if docket.get("status") != "REMOTE_RENDERER_LOCAL_QUALIFICATION_DOCKET_READY":
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_NOT_READY")
    if docket.get("research_signal_only") is not True:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_RESEARCH_BOUNDARY_MISSING")
    if docket.get("recommended_for_local_measurement") is not True:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_LOCAL_MEASUREMENT_NOT_RECOMMENDED")
    if docket.get("requires_explicit_local_model_candidate") is not True:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_EXPLICIT_SELECTION_NOT_REQUIRED")
    if docket.get("local_model_candidate_id") is not None:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_ALREADY_ASSIGNED")
    if docket.get("canonical_cost_mode_required") != CANONICAL_COST_MODE:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_CANONICAL_COST_MODE_MISMATCH")

    forbidden_true = (
        "local_runtime_qualified",
        "canonical_generation_authorized",
        "remote_pixels_reusable_as_canonical_evidence",
        "canonical_golden_eligible",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    )
    if any(docket.get(field) is not False for field in forbidden_true):
        raise ValueError("REMOTE_LOCAL_CANDIDATE_DOCKET_AUTHORITY_FORBIDDEN")


def _candidate_by_provider_id(candidate_id: str) -> LocalModelCandidate:
    matches = [candidate for candidate in ZERO_COST_LOCAL_CANDIDATES if candidate.provider_id == candidate_id]
    if len(matches) != 1:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_NOT_CURATED")
    return matches[0]


def _assert_exact_remote_match(renderer: str, candidate: LocalModelCandidate) -> None:
    expected_model = REMOTE_RENDERER_EXACT_LOCAL_MODEL.get(renderer)
    if expected_model is None:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_NO_EXACT_CURATED_LOCAL_MATCH")
    if candidate.model_id != expected_model:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_EXACT_MODEL_MISMATCH")


def _assert_zero_cost_candidate(candidate: LocalModelCandidate) -> None:
    economics = candidate.economics
    if economics.billing_class is not BillingClass.LOCAL_FREE:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_NOT_LOCAL_FREE")
    if economics.requires_payment_method:
        raise ValueError("REMOTE_LOCAL_CANDIDATE_PAYMENT_METHOD_FORBIDDEN")


@dataclass(frozen=True)
class RemoteRendererExplicitLocalCandidateBuilder:
    repo_root: Path

    def build(self, *, qualification_docket_path: Path, local_model_candidate_id: str) -> dict[str, Any]:
        docket_path = _require_repo_path(qualification_docket_path, self.repo_root)
        docket = json.loads(docket_path.read_text(encoding="utf-8"))
        _validate_docket(docket)
        docket_digest = _verify_docket_digest(docket)

        candidate_id = local_model_candidate_id.strip() if isinstance(local_model_candidate_id, str) else ""
        if not candidate_id:
            raise ValueError("REMOTE_LOCAL_CANDIDATE_EXPLICIT_ID_REQUIRED")
        candidate = _candidate_by_provider_id(candidate_id)
        _assert_zero_cost_candidate(candidate)

        renderer = docket.get("renderer")
        if not isinstance(renderer, str) or not renderer:
            raise ValueError("REMOTE_LOCAL_CANDIDATE_RENDERER_INVALID")
        _assert_exact_remote_match(renderer, candidate)

        payload = {
            "schema": DECLARATION_SCHEMA,
            "status": "REMOTE_RENDERER_EXPLICIT_LOCAL_MODEL_CANDIDATE_DECLARED",
            "qualification_docket": str(docket_path),
            "qualification_docket_file_sha256": _sha256_file(docket_path),
            "qualification_docket_sha256": docket_digest,
            "remote_renderer": renderer,
            "remote_space": docket.get("remote_space"),
            "research_output_sha256": docket.get("research_output_sha256"),
            "research_average_score": docket.get("research_average_score"),
            "local_model_candidate_id": candidate.provider_id,
            "local_model_id": candidate.model_id,
            "local_model_license": candidate.license_id,
            "local_runtime_adapter": candidate.runtime_adapter,
            "local_quality_tier": candidate.quality_tier.value,
            "local_intended_role": candidate.intended_role.value,
            "local_repository_size_gb": candidate.repository_size_gb,
            "local_minimum_vram_gb": candidate.minimum_vram_gb,
            "runtime_floor_proven": candidate.runtime_floor_proven,
            "exact_remote_model_match": True,
            "explicit_candidate_selection": True,
            "research_signal_only": True,
            "research_pixels_reusable_as_canonical_evidence": False,
            "pinned_model_revision_required": True,
            "pinned_model_revision": None,
            "measured_runtime_readiness_required": True,
            "local_runtime_qualified": False,
            "local_generation_authorized": False,
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "canonical_cost_mode_required": CANONICAL_COST_MODE,
        }
        payload["declaration_sha256"] = _sha256_json(payload)
        return payload
