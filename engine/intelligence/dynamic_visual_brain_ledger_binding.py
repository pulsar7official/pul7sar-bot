"""Bind a durable Dynamic Visual Brain execution into the Phase 18 visual ledger.

This module bridges the end-to-end durable queue -> generation -> byte-bound
Visual Critic receipt into the canonical real-visual validation ledger.  It is
CPU-only and deliberately grants neither Golden nor publication authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.dynamic_visual_brain_queue_critic_binding import (
    DynamicVisualBrainQueueCriticBindingGate,
)
from engine.intelligence.visual_benchmark_suite import PHASE18_VISUAL_BENCHMARKS
from engine.intelligence.visual_validation_ledger import (
    record_visual_review,
    validate_visual_validation_ledger,
)


@dataclass(frozen=True)
class DynamicVisualBrainLedgerBindingReceipt:
    contract: str
    status: str
    branch: str
    benchmark_id: str
    queue_critic_binding_sha256: str
    job_id: str
    job_attempt: int
    request_id: str
    seed: int
    cost_mode: str
    story_fingerprint: str
    selected_concept_id: str
    selected_concept_sha256: str
    renderer_prompt_sha256: str
    original_scene_request_sha256: str
    png_path: str
    png_sha256: str
    png_bytes: int
    critic_approved: bool
    critic_rejections: tuple[str, ...]
    provenance_passed: bool
    human_visual_review_required: bool
    golden_quality_approved: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainLedgerBindingGate:
    """Fail closed unless the ledger candidate is the durable critic-reviewed PNG."""

    CONTRACT = "pul7sar-dynamic-visual-brain-ledger-binding-v1"
    STATUS = "DYNAMIC_VISUAL_BRAIN_LEDGER_CANDIDATE_BOUND"
    BRANCH = "phase18/story-intelligence"
    PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

    @classmethod
    def verify(
        cls,
        *,
        benchmark_id: str,
        queue_critic_binding_path: str,
        candidate_png_path: str,
        repository_root: str = ".",
    ) -> DynamicVisualBrainLedgerBindingReceipt:
        root = Path(repository_root).resolve()
        cls._verify_benchmark(benchmark_id)
        binding_path = cls._inside_file(root, queue_critic_binding_path, "queue_critic_binding")
        png_path = cls._inside_file(root, candidate_png_path, "candidate_png")
        payload = cls._load(binding_path)
        cls._verify_queue_critic_payload(payload)

        png_bytes = png_path.read_bytes()
        if len(png_bytes) <= len(cls.PNG_SIGNATURE) or not png_bytes.startswith(cls.PNG_SIGNATURE):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_CANDIDATE_NOT_PNG")
        png_sha = sha256(png_bytes).hexdigest()
        if payload.get("png_sha256") != png_sha:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_PNG_SHA_DRIFT")

        return DynamicVisualBrainLedgerBindingReceipt(
            contract=cls.CONTRACT,
            status=cls.STATUS,
            branch=cls.BRANCH,
            benchmark_id=benchmark_id,
            queue_critic_binding_sha256=cls._sha(binding_path),
            job_id=payload["job_id"],
            job_attempt=int(payload["job_attempt"]),
            request_id=payload["request_id"],
            seed=int(payload["seed"]),
            cost_mode="$0-local",
            story_fingerprint=payload["story_fingerprint"],
            selected_concept_id=payload["selected_concept_id"],
            selected_concept_sha256=payload["selected_concept_sha256"],
            renderer_prompt_sha256=payload["renderer_prompt_sha256"],
            original_scene_request_sha256=payload["original_scene_request_sha256"],
            png_path=cls._repo_path(root, png_path),
            png_sha256=png_sha,
            png_bytes=len(png_bytes),
            critic_approved=bool(payload["critic_approved"]),
            critic_rejections=tuple(payload.get("critic_rejections", ())),
            provenance_passed=True,
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )

    @classmethod
    def record_review(
        cls,
        ledger: Mapping[str, Any],
        *,
        binding: Mapping[str, Any],
        status: str,
        checks: Mapping[str, bool | None],
        owner_visual_accepted: bool,
        golden_quality_score: float | None,
        hard_blockers: tuple[str, ...] = (),
        rejection_reasons: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Record a ledger review using already-bound Dynamic Visual Brain evidence.

        Provenance is injected only from a valid binding receipt.  Visual Critic
        rejection can be recorded as a rejected ledger case, but can never be
        promoted to an accepted case.
        """

        cls._verify_binding_receipt(binding)
        if status == "accepted" and binding.get("critic_approved") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_CRITIC_APPROVAL_REQUIRED")

        merged_checks = dict(checks)
        merged_checks["provenance_passed"] = True
        candidate = {
            "path": binding["png_path"],
            "sha256": binding["png_sha256"],
            "bytes": binding["png_bytes"],
        }
        updated = record_visual_review(
            ledger,
            benchmark_id=binding["benchmark_id"],
            candidate=candidate,
            status=status,
            checks=merged_checks,
            owner_visual_accepted=owner_visual_accepted,
            golden_quality_score=golden_quality_score,
            hard_blockers=hard_blockers,
            rejection_reasons=rejection_reasons,
        )
        validate_visual_validation_ledger(updated)
        return updated

    @classmethod
    def _verify_queue_critic_payload(cls, payload: Mapping[str, Any]) -> None:
        expectations = {
            "contract": DynamicVisualBrainQueueCriticBindingGate.CONTRACT,
            "status": DynamicVisualBrainQueueCriticBindingGate.STATUS,
            "branch": cls.BRANCH,
            "job_state": "succeeded",
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key, expected in expectations.items():
            if payload.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_QUEUE_CRITIC_DRIFT:{key}")
        if not isinstance(payload.get("job_attempt"), int) or isinstance(payload.get("job_attempt"), bool) or payload["job_attempt"] <= 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_JOB_ATTEMPT_INVALID")
        if not isinstance(payload.get("seed"), int) or isinstance(payload.get("seed"), bool) or payload["seed"] < 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_SEED_INVALID")
        for key in (
            "job_id",
            "request_id",
            "story_fingerprint",
            "selected_concept_id",
        ):
            if not isinstance(payload.get(key), str) or not payload[key].strip():
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_FIELD_INVALID:{key}")
        for key in (
            "selected_concept_sha256",
            "renderer_prompt_sha256",
            "original_scene_request_sha256",
            "png_sha256",
        ):
            cls._digest(payload.get(key), key)
        rejections = payload.get("critic_rejections")
        if not isinstance(rejections, list) or not all(isinstance(item, str) and item for item in rejections):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_CRITIC_REJECTIONS_INVALID")
        if payload.get("critic_approved") is True and rejections:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_CRITIC_APPROVAL_CONTRADICTION")

    @classmethod
    def _verify_binding_receipt(cls, payload: Mapping[str, Any]) -> None:
        expectations = {
            "contract": cls.CONTRACT,
            "status": cls.STATUS,
            "branch": cls.BRANCH,
            "cost_mode": "$0-local",
            "provenance_passed": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key, expected in expectations.items():
            if payload.get(key) != expected:
                raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_BINDING_DRIFT:{key}")
        cls._verify_benchmark(str(payload.get("benchmark_id", "")))
        for key in (
            "queue_critic_binding_sha256",
            "selected_concept_sha256",
            "renderer_prompt_sha256",
            "original_scene_request_sha256",
            "png_sha256",
        ):
            cls._digest(payload.get(key), key)
        if not isinstance(payload.get("png_path"), str) or not payload["png_path"].strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_BINDING_PNG_PATH_INVALID")
        if not isinstance(payload.get("png_bytes"), int) or isinstance(payload.get("png_bytes"), bool) or payload["png_bytes"] <= len(cls.PNG_SIGNATURE):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_BINDING_PNG_SIZE_INVALID")

    @staticmethod
    def _verify_benchmark(benchmark_id: str) -> None:
        canonical = {case.benchmark_id for case in PHASE18_VISUAL_BENCHMARKS}
        if benchmark_id not in canonical:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_BENCHMARK_INVALID")

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_EVIDENCE_NOT_OBJECT")
        return payload

    @classmethod
    def _inside_file(cls, root: Path, value: str, name: str) -> Path:
        candidate = Path(value)
        resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_{name.upper()}_OUTSIDE_REPOSITORY") from exc
        if not resolved.is_file():
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_{name.upper()}_MISSING")
        return resolved

    @staticmethod
    def _repo_path(root: Path, path: Path) -> str:
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LEDGER_CANDIDATE_OUTSIDE_REPOSITORY") from exc

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _digest(value: Any, name: str) -> None:
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.casefold()):
            raise ValueError(f"DYNAMIC_VISUAL_BRAIN_LEDGER_SHA_INVALID:{name}")
