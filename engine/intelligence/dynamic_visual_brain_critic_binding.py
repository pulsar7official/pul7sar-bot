"""End-to-end concept binding for Dynamic Visual Brain critic evidence.

A visually strong PNG must not be allowed to inherit a critic decision from a
nearby concept, seed, or generation request.  This gate binds the pre-render
concept lock and measured local-runtime admission to the durable generation
result, exact PNG bytes, and the existing byte-bound Visual Critic provenance.
It never grants Golden or publication authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmission
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock
from engine.intelligence.visual_brain_critic_provenance import VisualCriticProvenanceGate


@dataclass(frozen=True)
class DynamicVisualBrainCriticBindingReceipt:
    contract: str
    status: str
    story_fingerprint: str
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    scene_prompt_sha256: str
    original_scene_request_sha256: str
    request_id: str
    seed: int
    payload_sha256: str
    concept_lock_sha256: str
    local_admission_sha256: str
    generation_result_sha256: str
    critic_evidence_sha256: str
    png_sha256: str
    critic_approved: bool
    critic_rejections: tuple[str, ...]
    human_visual_review_required: bool
    golden_quality_approved: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainCriticBindingGate:
    CONTRACT = "pul7sar-dynamic-visual-brain-critic-binding-v1"

    @classmethod
    def verify(
        cls,
        *,
        concept_lock_path: str,
        local_admission_path: str,
        batch_manifest_path: str,
        generation_result_path: str,
        critic_evidence_path: str,
        repository_root: str = ".",
    ) -> DynamicVisualBrainCriticBindingReceipt:
        root = Path(repository_root).resolve()
        lock_path = cls._inside(root, concept_lock_path)
        admission_path = cls._inside(root, local_admission_path)
        result_path = cls._inside(root, generation_result_path)
        critic_path = cls._inside(root, critic_evidence_path)

        lock = cls._load(lock_path)
        admission = cls._load(admission_path)
        result = cls._load(result_path)

        cls._verify_lock(lock)
        cls._verify_admission(lock, admission)
        cls._verify_generation(lock, admission, result)

        critic = VisualCriticProvenanceGate.evaluate(
            batch_manifest_path=batch_manifest_path,
            generation_result_path=generation_result_path,
            critic_evidence_path=critic_evidence_path,
            repository_root=repository_root,
        )

        if critic.concept_id != lock["selected_concept_id"]:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CRITIC_CONCEPT_DRIFT")
        if critic.request_id != admission["request_id"] or critic.seed != admission["seed"]:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CRITIC_EXECUTION_IDENTITY_DRIFT")
        if critic.png_sha256 != cls._sha(cls._inside(root, result["png"])):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CRITIC_PNG_DRIFT")

        return DynamicVisualBrainCriticBindingReceipt(
            contract=cls.CONTRACT,
            status="DYNAMIC_VISUAL_BRAIN_CRITIC_PROVENANCE_BOUND",
            story_fingerprint=lock["story_fingerprint"],
            competition_sha256=lock["competition_sha256"],
            selected_concept_id=lock["selected_concept_id"],
            selected_concept_sha256=lock["selected_concept_sha256"],
            scene_prompt_sha256=lock["scene_prompt_sha256"],
            original_scene_request_sha256=admission["original_scene_request_sha256"],
            request_id=admission["request_id"],
            seed=int(admission["seed"]),
            payload_sha256=result["payload_sha256"],
            concept_lock_sha256=cls._sha(lock_path),
            local_admission_sha256=cls._sha(admission_path),
            generation_result_sha256=critic.generation_result_sha256,
            critic_evidence_sha256=critic.critic_evidence_sha256,
            png_sha256=critic.png_sha256,
            critic_approved=critic.critic_approved,
            critic_rejections=tuple(critic.critic_rejections),
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )

    @staticmethod
    def _verify_lock(lock: dict[str, Any]) -> None:
        if lock.get("contract") != DynamicVisualBrainConceptLock.CONTRACT:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCK_CONTRACT_MISMATCH")
        if lock.get("status") != "DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCKED":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCK_STATUS_INVALID")
        for key in ("story_fingerprint", "competition_sha256", "selected_concept_sha256", "scene_prompt_sha256"):
            DynamicVisualBrainCriticBindingGate._digest(lock.get(key), key)
        if not isinstance(lock.get("selected_concept_id"), str) or not lock["selected_concept_id"].strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SELECTED_CONCEPT_ID_INVALID")
        expected_false = (
            "generation_authorized",
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        )
        if any(lock.get(key) is not False for key in expected_false):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCK_AUTHORITY_DRIFT")
        if lock.get("selection_locked_before_rendering") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SELECTION_NOT_LOCKED_BEFORE_RENDERING")

    @staticmethod
    def _verify_admission(lock: dict[str, Any], admission: dict[str, Any]) -> None:
        if admission.get("contract") != DynamicVisualBrainLocalAdmission.CONTRACT:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_CONTRACT_MISMATCH")
        if admission.get("status") != "DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_ADMITTED":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_STATUS_INVALID")
        matches = {
            "story_fingerprint": lock["story_fingerprint"],
            "competition_sha256": lock["competition_sha256"],
            "selected_concept_id": lock["selected_concept_id"],
            "selected_concept_sha256": lock["selected_concept_sha256"],
            "scene_prompt_sha256": lock["scene_prompt_sha256"],
        }
        for key, expected in matches.items():
            if admission.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_{key.upper()}_DRIFT")
        DynamicVisualBrainCriticBindingGate._digest(admission.get("original_scene_request_sha256"), "original_scene_request_sha256")
        DynamicVisualBrainCriticBindingGate._digest(admission.get("request_id") if False else "0" * 64, "internal")
        if not isinstance(admission.get("request_id"), str) or not admission["request_id"].strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_REQUEST_ID_INVALID")
        if not isinstance(admission.get("seed"), int) or isinstance(admission.get("seed"), bool) or admission["seed"] < 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_SEED_INVALID")
        expectations = {
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "runtime_qualified": True,
            "generation_request_compiled": True,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key, expected in expectations.items():
            if admission.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LOCAL_ADMISSION_AUTHORITY_DRIFT:{key}")

    @staticmethod
    def _verify_generation(lock: dict[str, Any], admission: dict[str, Any], result: dict[str, Any]) -> None:
        if result.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_GENERATION_NOT_REAL_VISUAL_PROOF")
        pairs = {
            "dynamic_visual_brain_story_fingerprint": lock["story_fingerprint"],
            "dynamic_visual_brain_competition_sha256": lock["competition_sha256"],
            "dynamic_visual_brain_selected_concept_id": lock["selected_concept_id"],
            "dynamic_visual_brain_selected_concept_sha256": lock["selected_concept_sha256"],
            "dynamic_visual_brain_scene_prompt_sha256": lock["scene_prompt_sha256"],
            "dynamic_visual_brain_original_scene_request_sha256": admission["original_scene_request_sha256"],
            "request_id": admission["request_id"],
            "seed": admission["seed"],
            "provider_id": admission["provider_id"],
            "model_id": admission["model_id"],
            "cost_mode": "$0-local",
            "publication_ready": False,
        }
        for key, expected in pairs.items():
            if result.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_GENERATION_BINDING_DRIFT:{key}")
        if result.get("dynamic_visual_brain_selection_locked_before_rendering") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_GENERATION_SELECTION_LOCK_DRIFT")
        DynamicVisualBrainCriticBindingGate._digest(result.get("payload_sha256"), "payload_sha256")

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_EVIDENCE_MUST_BE_JSON_OBJECT")
        return data

    @staticmethod
    def _inside(root: Path, path: str) -> Path:
        candidate = Path(path)
        resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_EVIDENCE_PATH_ESCAPES_REPOSITORY") from exc
        if not resolved.is_file():
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_EVIDENCE_MISSING:{resolved}")
        return resolved

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _digest(value: Any, field: str) -> None:
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_DIGEST_INVALID:{field}")
