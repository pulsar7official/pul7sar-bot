"""End-to-end durable queue -> generation -> critic binding for Dynamic Visual Brain.

The selected concept is already SHA-locked before rendering, renderer-safe before
admission, and the admitted request is already sealed into the durable queue.
This module closes the remaining durable-worker boundary: the exact succeeded
queue job and its current handoff must be the same execution that produced the
PNG later evaluated by the existing byte-bound Visual Critic chain.

This gate is CPU-only and grants no Human, Golden, or publication authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from engine.intelligence.dynamic_visual_brain_critic_binding import DynamicVisualBrainCriticBindingGate
from engine.intelligence.dynamic_visual_brain_queue_binding import DynamicVisualBrainQueueBindingGate
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState


@dataclass(frozen=True)
class DynamicVisualBrainQueueCriticBindingReceipt:
    contract: str
    status: str
    branch: str
    job_id: str
    job_state: str
    job_attempt: int
    request_id: str
    seed: int
    provider_id: str
    model_id: str
    cost_mode: str
    story_fingerprint: str
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    renderer_prompt_sha256: str
    original_scene_request_sha256: str
    handoff_payload_sha256: str
    queue_binding_sha256: str
    durable_job_sha256: str
    handoff_file_sha256: str
    generation_result_sha256: str
    critic_binding_sha256: str
    png_sha256: str
    critic_approved: bool
    critic_rejections: tuple[str, ...]
    semantic_inspection_required: bool
    human_visual_review_required: bool
    golden_quality_approved: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainQueueCriticBindingGate:
    """Fail closed unless the durable queued job is the critic-reviewed PNG."""

    CONTRACT = "pul7sar-dynamic-visual-brain-queue-critic-binding-v1"
    STATUS = "DYNAMIC_VISUAL_BRAIN_DURABLE_EXECUTION_CRITIC_BOUND"
    BRANCH = "phase18/story-intelligence"

    @classmethod
    def verify(
        cls,
        *,
        queue_binding_path: str,
        concept_lock_path: str,
        local_admission_path: str,
        batch_manifest_path: str,
        generation_result_path: str,
        critic_evidence_path: str,
        repository_root: str = ".",
    ) -> DynamicVisualBrainQueueCriticBindingReceipt:
        root = Path(repository_root).resolve()
        binding_path = cls._inside_file(root, queue_binding_path, "queue_binding")
        result_path = cls._inside_file(root, generation_result_path, "generation_result")
        binding = cls._load(binding_path)
        result = cls._load(result_path)
        cls._verify_queue_binding(binding)

        queue_root = cls._inside_dir(root, binding["queue_root"], "queue_root")
        handoff_path = cls._inside_file(root, binding["handoff_path"], "handoff")
        if cls._sha(handoff_path) != binding["handoff_file_sha256"]:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_HANDOFF_FILE_DRIFT")
        handoff_raw = cls._load(handoff_path)
        if handoff_raw.get("payload_sha256") != binding["handoff_payload_sha256"]:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_HANDOFF_PAYLOAD_DRIFT")

        store = FilesystemGenerationJobStore(queue_root)
        job = store.get(binding["job_id"])
        if job is None:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_MISSING")
        if job.state is not GenerationJobState.SUCCEEDED:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_NOT_SUCCEEDED")
        if job.attempt <= 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_ATTEMPT_INVALID")
        cls._verify_job(binding, job)

        job_path = queue_root / "succeeded" / f"{job.job_id}.json"
        if not job_path.is_file():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_RECORD_MISSING")
        durable_job_sha = cls._sha(job_path)

        cls._verify_generation(binding, job, result)
        png_path = cls._inside_file(root, str(result["png"]), "png")
        if cls._normalized_repo_path(root, png_path) != cls._normalized_repo_path(root, cls._resolve(root, str(job.result_path))):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_RESULT_PATH_DRIFT")
        png_sha = cls._sha(png_path)

        critic = DynamicVisualBrainCriticBindingGate.verify(
            concept_lock_path=concept_lock_path,
            local_admission_path=local_admission_path,
            batch_manifest_path=batch_manifest_path,
            generation_result_path=generation_result_path,
            critic_evidence_path=critic_evidence_path,
            repository_root=repository_root,
        )
        cls._verify_critic(binding, result, critic, png_sha)

        critic_payload = critic.to_dict()
        critic_binding_sha = sha256(
            json.dumps(critic_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        return DynamicVisualBrainQueueCriticBindingReceipt(
            contract=cls.CONTRACT,
            status=cls.STATUS,
            branch=cls.BRANCH,
            job_id=job.job_id,
            job_state=job.state.value,
            job_attempt=job.attempt,
            request_id=job.request_id,
            seed=int(binding["seed"]),
            provider_id=job.provider_id,
            model_id=job.model_id,
            cost_mode="$0-local",
            story_fingerprint=binding["story_fingerprint"],
            competition_sha256=binding["competition_sha256"],
            selected_concept_id=binding["selected_concept_id"],
            selected_concept_sha256=binding["selected_concept_sha256"],
            renderer_prompt_sha256=binding["renderer_prompt_sha256"],
            original_scene_request_sha256=binding["original_scene_request_sha256"],
            handoff_payload_sha256=binding["handoff_payload_sha256"],
            queue_binding_sha256=cls._sha(binding_path),
            durable_job_sha256=durable_job_sha,
            handoff_file_sha256=cls._sha(handoff_path),
            generation_result_sha256=cls._sha(result_path),
            critic_binding_sha256=critic_binding_sha,
            png_sha256=png_sha,
            critic_approved=bool(critic.critic_approved),
            critic_rejections=tuple(critic.critic_rejections),
            semantic_inspection_required=True,
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )

    @classmethod
    def _verify_queue_binding(cls, binding: dict[str, Any]) -> None:
        if binding.get("contract") != DynamicVisualBrainQueueBindingGate.CONTRACT:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_CONTRACT_DRIFT")
        if binding.get("status") != DynamicVisualBrainQueueBindingGate.STATUS:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_STATUS_INVALID")
        if binding.get("branch") != cls.BRANCH:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_BRANCH_DRIFT")
        for key in (
            "story_fingerprint",
            "competition_sha256",
            "selected_concept_sha256",
            "scene_prompt_sha256",
            "renderer_prompt_sha256",
            "original_scene_request_sha256",
            "handoff_payload_sha256",
            "handoff_file_sha256",
        ):
            cls._digest(binding.get(key), key)
        for key in ("request_id", "provider_id", "model_id", "backend", "selected_concept_id", "job_id"):
            if not isinstance(binding.get(key), str) or not binding[key].strip():
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_FIELD_INVALID:{key}")
        if not isinstance(binding.get("seed"), int) or isinstance(binding.get("seed"), bool) or binding["seed"] < 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_SEED_INVALID")
        expectations = {
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key, expected in expectations.items():
            if binding.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_QUEUE_BINDING_AUTHORITY_DRIFT:{key}")

    @classmethod
    def _verify_job(cls, binding: dict[str, Any], job) -> None:
        locked = {
            "request_id": binding["request_id"],
            "payload_sha256": binding["handoff_payload_sha256"],
            "provider_id": binding["provider_id"],
            "model_id": binding["model_id"],
            "handoff_path": binding["handoff_path"],
        }
        for key, expected in locked.items():
            if getattr(job, key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_IDENTITY_DRIFT:{key}")
        metadata_expectations = {
            "queue_binding_contract": DynamicVisualBrainQueueBindingGate.CONTRACT,
            "branch": cls.BRANCH,
            "cost_mode": "$0-local",
            "dynamic_visual_brain_story_fingerprint": binding["story_fingerprint"],
            "dynamic_visual_brain_competition_sha256": binding["competition_sha256"],
            "dynamic_visual_brain_selected_concept_id": binding["selected_concept_id"],
            "dynamic_visual_brain_selected_concept_sha256": binding["selected_concept_sha256"],
            "dynamic_visual_brain_scene_prompt_sha256": binding["scene_prompt_sha256"],
            "dynamic_renderer_prompt_sha256": binding["renderer_prompt_sha256"],
            "dynamic_visual_brain_original_scene_request_sha256": binding["original_scene_request_sha256"],
            "renderer_identity_neutral": True,
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
        }
        for key, expected in metadata_expectations.items():
            if job.metadata.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_METADATA_DRIFT:{key}")

    @classmethod
    def _verify_generation(cls, binding: dict[str, Any], job, result: dict[str, Any]) -> None:
        expectations = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "request_id": binding["request_id"],
            "seed": binding["seed"],
            "provider_id": binding["provider_id"],
            "model_id": binding["model_id"],
            "payload_sha256": binding["handoff_payload_sha256"],
            "cost_mode": "$0-local",
            "publication_ready": False,
            "dynamic_visual_brain_story_fingerprint": binding["story_fingerprint"],
            "dynamic_visual_brain_competition_sha256": binding["competition_sha256"],
            "dynamic_visual_brain_selected_concept_id": binding["selected_concept_id"],
            "dynamic_visual_brain_selected_concept_sha256": binding["selected_concept_sha256"],
            "dynamic_visual_brain_scene_prompt_sha256": binding["scene_prompt_sha256"],
            "dynamic_renderer_prompt_sha256": binding["renderer_prompt_sha256"],
            "dynamic_visual_brain_original_scene_request_sha256": binding["original_scene_request_sha256"],
        }
        for key, expected in expectations.items():
            if result.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_GENERATION_DRIFT:{key}")
        if result.get("dynamic_visual_brain_selection_locked_before_rendering") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_GENERATION_SELECTION_LOCK_DRIFT")
        if not isinstance(result.get("png"), str) or not result["png"].strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_GENERATION_PNG_MISSING")
        if not job.result_path:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_JOB_RESULT_PATH_MISSING")

    @classmethod
    def _verify_critic(cls, binding: dict[str, Any], result: dict[str, Any], critic, png_sha: str) -> None:
        expected = {
            "story_fingerprint": binding["story_fingerprint"],
            "competition_sha256": binding["competition_sha256"],
            "selected_concept_id": binding["selected_concept_id"],
            "selected_concept_sha256": binding["selected_concept_sha256"],
            "renderer_prompt_sha256": binding["renderer_prompt_sha256"],
            "original_scene_request_sha256": binding["original_scene_request_sha256"],
            "request_id": binding["request_id"],
            "seed": binding["seed"],
            "payload_sha256": binding["handoff_payload_sha256"],
            "png_sha256": png_sha,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key, value in expected.items():
            if getattr(critic, key) != value:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_CRITIC_DRIFT:{key}")
        if result.get("concept_id") != critic.selected_concept_id:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_CRITIC_CONCEPT_RESULT_DRIFT")

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_EVIDENCE_NOT_OBJECT")
        return data

    @staticmethod
    def _resolve(root: Path, value: str) -> Path:
        candidate = Path(value)
        return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()

    @classmethod
    def _inside_file(cls, root: Path, value: str, name: str) -> Path:
        resolved = cls._resolve(root, value)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_{name.upper()}_OUTSIDE_REPOSITORY") from exc
        if not resolved.is_file():
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_{name.upper()}_MISSING")
        return resolved

    @classmethod
    def _inside_dir(cls, root: Path, value: str, name: str) -> Path:
        resolved = cls._resolve(root, value)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_{name.upper()}_OUTSIDE_REPOSITORY") from exc
        if not resolved.is_dir():
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_{name.upper()}_MISSING")
        return resolved

    @staticmethod
    def _normalized_repo_path(root: Path, path: Path) -> str:
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_DURABLE_RESULT_PATH_OUTSIDE_REPOSITORY") from exc

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _digest(value: Any, name: str) -> None:
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.casefold()):
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DURABLE_SHA_INVALID:{name}")
