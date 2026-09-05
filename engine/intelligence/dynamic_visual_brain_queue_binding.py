"""Durable queue binding for measured Dynamic Visual Brain admissions.

The Dynamic Visual Brain already locks the selected story concept, translates it
into an identity-neutral renderer prompt, and admits that prompt only through a
measured $0-local runtime.  This module closes the next execution boundary: the
exact admitted request is SHA-sealed into a LocalGenerationHandoff and then
persisted as the exact durable GenerationJob a GPU worker may lease.

No semantic, Golden, or publication authority is granted here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from engine.intelligence.dynamic_visual_brain_local_admission import (
    DynamicVisualBrainLocalAdmission,
    DynamicVisualBrainLocalAdmissionReceipt,
)
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


@dataclass(frozen=True)
class DynamicVisualBrainQueueBindingReceipt:
    contract: str
    status: str
    branch: str
    request_id: str
    seed: int
    provider_id: str
    model_id: str
    backend: str
    cost_mode: str
    story_fingerprint: str
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    scene_prompt_sha256: str
    renderer_prompt_sha256: str
    original_scene_request_sha256: str
    handoff_path: str
    handoff_payload_sha256: str
    handoff_file_sha256: str
    queue_root: str
    job_id: str
    job_state: str
    already_enqueued: bool
    semantic_inspection_required: bool
    human_visual_review_required: bool
    golden_quality_approved: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainQueueBindingGate:
    """Fail-closed bridge from measured admission to a durable worker job."""

    CONTRACT = "pul7sar-dynamic-visual-brain-queue-binding-v1"
    STATUS = "DYNAMIC_VISUAL_BRAIN_DURABLE_QUEUE_BOUND"
    BRANCH = "phase18/story-intelligence"

    @classmethod
    def bind_and_enqueue(
        cls,
        *,
        branch: str,
        request: LocalBackendGenerationRequest,
        admission: DynamicVisualBrainLocalAdmissionReceipt,
        handoff_path: str | Path,
        queue_root: str | Path,
        repository_root: str | Path = ".",
        job_id: str | None = None,
        max_attempts: int = 3,
    ) -> tuple[GenerationJob, DynamicVisualBrainQueueBindingReceipt]:
        if branch != cls.BRANCH:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_BRANCH_ISOLATION_FAILED")
        if not isinstance(request, LocalBackendGenerationRequest):
            raise TypeError("request must be LocalBackendGenerationRequest")
        if not isinstance(admission, DynamicVisualBrainLocalAdmissionReceipt):
            raise TypeError("admission must be DynamicVisualBrainLocalAdmissionReceipt")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        cls._assert_admission_and_request(request, admission)

        root = Path(repository_root).resolve()
        sealed_handoff = cls._inside(root, handoff_path, "handoff_path")
        durable_queue = cls._inside(root, queue_root, "queue_root")
        sealed_handoff.parent.mkdir(parents=True, exist_ok=True)

        expected_payload = LocalGenerationHandoff.to_dict(request)
        expected_payload_sha = str(expected_payload["payload_sha256"])
        if sealed_handoff.exists():
            replayed = LocalGenerationHandoff.read(str(sealed_handoff))
            cls._assert_request_identity(replayed, request)
            existing_payload = cls._read_payload_sha(sealed_handoff)
            if existing_payload != expected_payload_sha:
                raise ValueError("DYNAMIC_VISUAL_BRAIN_EXISTING_HANDOFF_PAYLOAD_DRIFT")
        else:
            LocalGenerationHandoff.write(request, str(sealed_handoff))

        replayed = LocalGenerationHandoff.read(str(sealed_handoff))
        cls._assert_request_identity(replayed, request)
        payload_sha = cls._read_payload_sha(sealed_handoff)
        if payload_sha != expected_payload_sha:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_HANDOFF_PAYLOAD_DRIFT")
        handoff_file_sha = sha256(sealed_handoff.read_bytes()).hexdigest()

        resolved_job_id = job_id or f"dvb-{payload_sha[:24]}"
        handoff_repo_path = sealed_handoff.relative_to(root).as_posix()
        queue_repo_path = durable_queue.relative_to(root).as_posix()
        metadata = {
            "queue_binding_contract": cls.CONTRACT,
            "branch": cls.BRANCH,
            "cost_mode": "$0-local",
            "backend": request.backend,
            "seed": request.seed,
            "native_width": request.width,
            "native_height": request.height,
            "dynamic_visual_brain_story_fingerprint": admission.story_fingerprint,
            "dynamic_visual_brain_competition_sha256": admission.competition_sha256,
            "dynamic_visual_brain_selected_concept_id": admission.selected_concept_id,
            "dynamic_visual_brain_selected_concept_sha256": admission.selected_concept_sha256,
            "dynamic_visual_brain_scene_prompt_sha256": admission.scene_prompt_sha256,
            "dynamic_renderer_prompt_sha256": admission.renderer_prompt_sha256,
            "dynamic_visual_brain_original_scene_request_sha256": admission.original_scene_request_sha256,
            "renderer_identity_neutral": True,
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
        }
        candidate = GenerationJob(
            job_id=resolved_job_id,
            request_id=request.request_id,
            handoff_path=handoff_repo_path,
            payload_sha256=payload_sha,
            provider_id=request.provider_id,
            model_id=request.model_id,
            max_attempts=max_attempts,
            metadata=metadata,
        )

        store = FilesystemGenerationJobStore(durable_queue)
        existing = store.get(resolved_job_id)
        already_enqueued = existing is not None
        if existing is None:
            store.enqueue(candidate)
            stored = store.get(resolved_job_id)
            if stored is None:
                raise RuntimeError("DYNAMIC_VISUAL_BRAIN_QUEUE_WRITE_NOT_DURABLE")
        else:
            stored = existing
            cls._assert_job_identity(stored, candidate)

        receipt = DynamicVisualBrainQueueBindingReceipt(
            contract=cls.CONTRACT,
            status=cls.STATUS,
            branch=cls.BRANCH,
            request_id=request.request_id,
            seed=request.seed,
            provider_id=request.provider_id,
            model_id=request.model_id,
            backend=request.backend,
            cost_mode="$0-local",
            story_fingerprint=admission.story_fingerprint,
            competition_sha256=admission.competition_sha256,
            selected_concept_id=admission.selected_concept_id,
            selected_concept_sha256=admission.selected_concept_sha256,
            scene_prompt_sha256=admission.scene_prompt_sha256,
            renderer_prompt_sha256=admission.renderer_prompt_sha256,
            original_scene_request_sha256=admission.original_scene_request_sha256,
            handoff_path=handoff_repo_path,
            handoff_payload_sha256=payload_sha,
            handoff_file_sha256=handoff_file_sha,
            queue_root=queue_repo_path,
            job_id=stored.job_id,
            job_state=stored.state.value,
            already_enqueued=already_enqueued,
            semantic_inspection_required=True,
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )
        return stored, receipt

    @classmethod
    def _assert_admission_and_request(
        cls,
        request: LocalBackendGenerationRequest,
        admission: DynamicVisualBrainLocalAdmissionReceipt,
    ) -> None:
        if admission.contract != DynamicVisualBrainLocalAdmission.CONTRACT:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_ADMISSION_CONTRACT_DRIFT")
        if admission.status != "DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_LOCAL_RUNTIME_ADMITTED":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_ADMISSION_STATUS_INVALID")
        if not admission.runtime_qualified or not admission.generation_request_compiled:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_RUNTIME_NOT_QUALIFIED")
        if not admission.semantic_inspection_required or not admission.human_visual_review_required:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_DOWNSTREAM_REVIEW_GATE_MISSING")
        if admission.golden_quality_approved or admission.publication_ready:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_PUBLICATION_AUTHORITY_DRIFT")
        if any((
            admission.generated_branding_allowed,
            admission.generated_exact_facts_allowed,
            admission.generated_sport_geometry_allowed,
        )):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_GENERATOR_AUTHORITY_DRIFT")
        if not admission.renderer_identity_neutral:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_RENDERER_IDENTITY_NEUTRALITY_MISSING")
        if admission.cost_mode != "$0-local":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_COST_MODE_DRIFT")

        locked = (
            ("provider_id", admission.provider_id, request.provider_id),
            ("model_id", admission.model_id, request.model_id),
            ("backend", admission.backend, request.backend),
            ("request_id", admission.request_id, request.request_id),
            ("seed", admission.seed, request.seed),
        )
        drift = [name for name, expected, actual in locked if expected != actual]
        if drift:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_REQUEST_IDENTITY_DRIFT:" + ",".join(drift))

        metadata = dict(request.metadata)
        expected_metadata = {
            "cost_mode": "$0-local",
            "dynamic_visual_brain_story_fingerprint": admission.story_fingerprint,
            "dynamic_visual_brain_competition_sha256": admission.competition_sha256,
            "dynamic_visual_brain_selected_concept_id": admission.selected_concept_id,
            "dynamic_visual_brain_selected_concept_sha256": admission.selected_concept_sha256,
            "dynamic_visual_brain_scene_prompt_sha256": admission.scene_prompt_sha256,
            "dynamic_renderer_prompt_contract": admission.renderer_prompt_contract,
            "dynamic_renderer_prompt_sha256": admission.renderer_prompt_sha256,
            "dynamic_renderer_identity_neutral": True,
            "dynamic_visual_brain_original_scene_request_sha256": admission.original_scene_request_sha256,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "semantic_inspection_required": True,
        }
        drift_keys = [key for key, expected in expected_metadata.items() if metadata.get(key) != expected]
        if drift_keys:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_METADATA_DRIFT:" + ",".join(drift_keys))
        lowered = request.prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_PROMPT_PLATFORM_NAME_LEAK")

        for value in (
            admission.story_fingerprint,
            admission.competition_sha256,
            admission.selected_concept_sha256,
            admission.scene_prompt_sha256,
            admission.renderer_prompt_sha256,
            admission.original_scene_request_sha256,
        ):
            cls._require_sha(value)

    @staticmethod
    def _assert_request_identity(actual: LocalBackendGenerationRequest, expected: LocalBackendGenerationRequest) -> None:
        locked = (
            "provider_id", "model_id", "backend", "prompt", "native_negative_constraints",
            "width", "height", "seed", "request_id", "reference_asset_ids",
        )
        drift = [name for name in locked if getattr(actual, name) != getattr(expected, name)]
        if drift or dict(actual.metadata) != dict(expected.metadata):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_HANDOFF_REQUEST_DRIFT:" + ",".join(drift or ["metadata"]))

    @staticmethod
    def _assert_job_identity(actual: GenerationJob, expected: GenerationJob) -> None:
        locked = ("request_id", "handoff_path", "payload_sha256", "provider_id", "model_id", "max_attempts")
        drift = [name for name in locked if getattr(actual, name) != getattr(expected, name)]
        if drift or dict(actual.metadata) != dict(expected.metadata):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_EXISTING_QUEUE_JOB_DRIFT:" + ",".join(drift or ["metadata"]))

    @staticmethod
    def _inside(root: Path, value: str | Path, name: str) -> Path:
        candidate = Path(value)
        resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_QUEUE_{name.upper()}_OUTSIDE_REPOSITORY") from exc
        return resolved

    @staticmethod
    def _read_payload_sha(path: Path) -> str:
        import json
        value = json.loads(path.read_text(encoding="utf-8")).get("payload_sha256")
        DynamicVisualBrainQueueBindingGate._require_sha(value)
        return str(value)

    @staticmethod
    def _require_sha(value: Any) -> None:
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.casefold()):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_SHA256_INVALID")
