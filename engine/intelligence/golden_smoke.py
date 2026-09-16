"""Fail-closed coordinator for genuine Golden Visual GPU smoke runs.

Legacy v1-v5 manifests remain readable. The current v6 smoke candidate is a
story-first editorial PREVIEW: the generated scene may contain contextual turf,
but no deterministic football pitch replacement is required. Exact branding and
typography remain later deterministic layers, and publication authority remains
closed throughout smoke execution.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff

SUPPORTED_GOLDEN_MANIFEST_VERSIONS = {
    "pul7sar-golden-batch-v1", "pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3",
    "pul7sar-golden-batch-v4", "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6",
}
GOLDEN_COST_MODE = "$0-local"
DEFAULT_SMOKE_JOB_ID = "golden-smoke-candidate-01"
V6_SPORT_GEOMETRY = "contextual_optional_not_required"


@dataclass(frozen=True)
class GoldenSmokeCandidate:
    manifest_path: Path
    handoff_path: Path
    candidate: int
    seed: int
    request_id: str
    payload_sha256: str
    provider_id: str
    model_id: str


@dataclass(frozen=True)
class GoldenSmokePreparation:
    job: GenerationJob
    created: bool
    reusable_existing: bool


def _assert_manifest_policy(data: dict[str, Any], manifest_version: str) -> None:
    if manifest_version in {
        "pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4",
        "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6",
    } and data.get("composition_grammar") != "single_continuous_scene":
        raise ValueError("Golden smoke v2+ requires single_continuous_scene composition grammar")
    if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"} and data.get("sport_geometry") != "association_football_regulation_pitch":
        raise ValueError("Golden smoke v3/v4 requires regulation association-football pitch geometry")
    if manifest_version == "pul7sar-golden-batch-v4":
        if data.get("generated_branding_allowed") is not False:
            raise ValueError("Golden smoke v4 requires generated platform branding to remain forbidden")
        if data.get("brand_composition_policy") != "exact_assets_only_after_generation":
            raise ValueError("Golden smoke v4 requires exact-assets-only post-generation branding")
    if manifest_version == "pul7sar-golden-batch-v5":
        expected = {
            "sport_geometry": "deterministic_football_pitch_projective_v1",
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": "high_wide_central",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
        }
        failures = [f"{key}={data.get(key)!r}" for key, value in expected.items() if data.get(key) != value]
        if failures:
            raise ValueError("Golden smoke v5 hybrid policy mismatch: " + "; ".join(failures))
    if manifest_version == "pul7sar-golden-batch-v6":
        expected = {
            "visual_grammar_surface_visibility": "context_only",
            "sport_geometry": V6_SPORT_GEOMETRY,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": False,
            "football_camera_preset": "editorial_environmental_oblique",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
        }
        failures = [f"{key}={data.get(key)!r}" for key, value in expected.items() if data.get(key) != value]
        if failures:
            raise ValueError("Golden smoke v6 editorial policy mismatch: " + "; ".join(failures))


def _assert_handoff_prompt_policy(request: Any, manifest_version: str) -> None:
    prompt = request.prompt.casefold()
    if manifest_version in {
        "pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4",
        "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6",
    }:
        unified_markers = (
            "one single continuous full-bleed editorial image",
            "never use collage, montage, split-screen, grid, diptych, triptych",
        )
        if any(marker not in prompt for marker in unified_markers):
            raise ValueError("candidate 1 v2+ handoff is missing unified-scene prompt lock")

    if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"}:
        geometry_markers = (
            "regulation association-football pitch geometry", "exactly one halfway line",
            "exactly one circular centre circle", "do not duplicate the halfway line or centre circle",
        )
        if any(marker not in prompt for marker in geometry_markers):
            raise ValueError("candidate 1 v3/v4 handoff is missing regulation-pitch prompt lock")

    if manifest_version == "pul7sar-golden-batch-v4":
        branding_markers = (
            "zero pul7sar lettering", "never spell pul7sar, pulsar, or any approximation",
            "no legible words, letters, numerals, pseudo-text, fake logos",
            "exact branding and typography are added only by deterministic post-composition",
        )
        if any(marker not in prompt for marker in branding_markers):
            raise ValueError("candidate 1 v4 handoff is missing generated-brand exclusion prompt lock")

    if manifest_version == "pul7sar-golden-batch-v5":
        semantic_markers = (
            "reserved surface region plain and unmarked",
            "no field/court/rink lines",
            "the exact surface will be replaced by deterministic code after generation",
            "fully unbranded",
            "platform names",
        )
        if any(marker not in prompt for marker in semantic_markers):
            raise ValueError("candidate 1 v5 handoff is missing semantic hybrid prompt safeguards")
        if "pul7sar" in prompt or "pulsar" in prompt:
            raise ValueError("candidate 1 v5 handoff leaked protected platform name")
        expected_metadata = {
            "brand_name_redacted_from_generation_prompt": True,
            "generated_branding_allowed": False,
            "composition_grammar": "single_continuous_scene",
            "hybrid_base_scene_contract": True,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
        }
        failures = [f"{key}={request.metadata.get(key)!r}" for key, value in expected_metadata.items() if request.metadata.get(key) != value]
        if failures:
            raise ValueError("candidate 1 v5 structured ownership contract mismatch: " + "; ".join(failures))

    if manifest_version == "pul7sar-golden-batch-v6":
        semantic_markers = (
            "asymmetric editorial hierarchy",
            "oblique three-quarter environmental camera",
            "no high-wide-central broadcast framing",
            "no full-pitch master shot",
            "turf is optional context only and visually subordinate",
            "fully unbranded",
            "platform names",
        )
        if any(marker not in prompt for marker in semantic_markers):
            raise ValueError("candidate 1 v6 handoff is missing story-first editorial safeguards")
        if "the exact surface will be replaced by deterministic code after generation" in prompt:
            raise ValueError("candidate 1 v6 handoff regressed to pitch-replacement wording")
        if "pul7sar" in prompt or "pulsar" in prompt:
            raise ValueError("candidate 1 v6 handoff leaked protected platform name")
        expected_metadata = {
            "brand_name_redacted_from_generation_prompt": True,
            "generated_branding_allowed": False,
            "composition_grammar": "single_continuous_scene",
            "hybrid_base_scene_contract": True,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": False,
            "visual_grammar_surface_visibility": "context_only",
            "sport_geometry": V6_SPORT_GEOMETRY,
            "football_camera_preset": "editorial_environmental_oblique",
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
        }
        failures = [f"{key}={request.metadata.get(key)!r}" for key, value in expected_metadata.items() if request.metadata.get(key) != value]
        if failures:
            raise ValueError("candidate 1 v6 structured ownership contract mismatch: " + "; ".join(failures))


def load_first_candidate(manifest_path: str | Path) -> GoldenSmokeCandidate:
    path = Path(manifest_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    manifest_version = data.get("manifest_version")
    if manifest_version not in SUPPORTED_GOLDEN_MANIFEST_VERSIONS:
        raise ValueError("unsupported Golden batch manifest version")
    if data.get("cost_mode") != GOLDEN_COST_MODE:
        raise ValueError("Golden smoke path requires $0-local cost mode")
    _assert_manifest_policy(data, manifest_version)
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden batch has no candidates")
    first = next((item for item in candidates if isinstance(item, dict) and item.get("candidate") == 1), None)
    if first is None:
        raise ValueError("Golden batch is missing candidate 1")
    handoff_name = first.get("handoff")
    if not isinstance(handoff_name, str) or not handoff_name.strip():
        raise ValueError("candidate 1 is missing handoff path")
    handoff_path = path.parent / handoff_name
    if not handoff_path.is_file():
        raise FileNotFoundError(f"candidate 1 handoff does not exist: {handoff_path}")
    request = LocalGenerationHandoff.read(str(handoff_path))
    raw_handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    actual_sha = raw_handoff.get("payload_sha256")
    manifest_sha = first.get("payload_sha256")
    if not isinstance(actual_sha, str) or actual_sha != manifest_sha:
        raise ValueError("candidate 1 handoff SHA does not match Golden manifest")
    if request.request_id != first.get("request_id"):
        raise ValueError("candidate 1 request ID does not match Golden manifest")
    if request.seed != first.get("seed"):
        raise ValueError("candidate 1 seed does not match Golden manifest")
    if request.model_id != first.get("model_id"):
        raise ValueError("candidate 1 model ID does not match Golden manifest")
    if request.metadata.get("cost_mode") != GOLDEN_COST_MODE:
        raise ValueError("candidate 1 handoff escaped $0-local cost mode")
    _assert_handoff_prompt_policy(request, manifest_version)
    return GoldenSmokeCandidate(path, handoff_path, 1, request.seed, request.request_id, actual_sha, request.provider_id, request.model_id)


def _same_locked_identity(job: GenerationJob, candidate: GoldenSmokeCandidate) -> bool:
    return job.request_id == candidate.request_id and Path(job.handoff_path) == candidate.handoff_path and job.payload_sha256 == candidate.payload_sha256 and job.provider_id == candidate.provider_id and job.model_id == candidate.model_id


def prepare_smoke_job(*, store: FilesystemGenerationJobStore, candidate: GoldenSmokeCandidate, job_id: str = DEFAULT_SMOKE_JOB_ID, max_attempts: int = 3) -> GoldenSmokePreparation:
    existing = store.get(job_id)
    if existing is not None:
        if not _same_locked_identity(existing, candidate):
            raise ValueError("existing smoke job identity does not match locked candidate 1")
        if existing.state is GenerationJobState.TERMINAL_FAILED:
            raise RuntimeError("candidate 1 smoke job is terminal_failed; investigate before creating a new job")
        return GoldenSmokePreparation(job=existing, created=False, reusable_existing=True)
    job = GenerationJob(
        job_id=job_id, request_id=candidate.request_id, handoff_path=str(candidate.handoff_path), payload_sha256=candidate.payload_sha256,
        provider_id=candidate.provider_id, model_id=candidate.model_id, max_attempts=max_attempts,
        metadata={"candidate": candidate.candidate, "seed": candidate.seed, "cost_mode": GOLDEN_COST_MODE, "smoke_role": "golden-editorial-base", "manifest_path": str(candidate.manifest_path)},
    )
    store.enqueue(job)
    return GoldenSmokePreparation(job=job, created=True, reusable_existing=False)


def smoke_status_payload(preparation: GoldenSmokePreparation) -> dict[str, Any]:
    job = preparation.job
    return {
        "status": "SMOKE_JOB_PREPARED", "job_id": job.job_id, "job_state": job.state.value, "request_id": job.request_id,
        "payload_sha256": job.payload_sha256, "provider_id": job.provider_id, "model_id": job.model_id,
        "created": preparation.created, "reusable_existing": preparation.reusable_existing, "attempt": job.attempt,
        "max_attempts": job.max_attempts, "cost_mode": job.metadata.get("cost_mode"),
    }
