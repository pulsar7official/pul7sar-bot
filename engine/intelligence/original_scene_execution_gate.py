"""Fail-closed admission gate for original PUL7SAR scene synthesis."""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.original_scene_runtime_contract import (
    OriginalSceneRequest,
    OriginalSceneRuntimeKind,
    OriginalSceneRuntimeQualification,
)


@dataclass(frozen=True)
class OriginalSceneExecutionDecision:
    admitted: bool
    reason: str
    runtime_id: str | None
    requires_semantic_inspection: bool
    requires_identity_fidelity_gate: bool
    publication_ready: bool = False
    contract: str = "pul7sar-original-scene-execution-gate-v1"


class OriginalSceneExecutionGate:
    """Admit synthesis only when a measured local/self-hosted runtime is qualified."""

    def evaluate(
        self,
        request: OriginalSceneRequest,
        runtime: OriginalSceneRuntimeQualification | None,
    ) -> OriginalSceneExecutionDecision:
        if not isinstance(request, OriginalSceneRequest):
            raise TypeError("request must be OriginalSceneRequest")
        if runtime is None:
            return self._deny("ORIGINAL_SCENE_RUNTIME_MISSING")
        if not isinstance(runtime, OriginalSceneRuntimeQualification):
            raise TypeError("runtime must be OriginalSceneRuntimeQualification")
        if not runtime.qualified:
            return self._deny("ORIGINAL_SCENE_RUNTIME_NOT_QUALIFIED", runtime.runtime_id)
        if runtime.runtime_kind is not request.runtime_kind:
            return self._deny("ORIGINAL_SCENE_RUNTIME_KIND_MISMATCH", runtime.runtime_id)
        if runtime.network_dependency_required or runtime.paid_provider_required:
            return self._deny("ORIGINAL_SCENE_RUNTIME_EXTERNAL_DEPENDENCY_FORBIDDEN", runtime.runtime_id)
        if not runtime.local_or_self_hosted or not runtime.provider_agnostic_adapter:
            return self._deny("ORIGINAL_SCENE_RUNTIME_PORTABILITY_CONTRACT_FAILED", runtime.runtime_id)
        if not runtime.original_pixels or not runtime.accepts_seed:
            return self._deny("ORIGINAL_SCENE_RUNTIME_ORIGINALITY_CONTRACT_FAILED", runtime.runtime_id)
        if not runtime.semantic_inspection_required:
            return self._deny("ORIGINAL_SCENE_SEMANTIC_INSPECTION_REQUIRED", runtime.runtime_id)
        if request.runtime_kind is OriginalSceneRuntimeKind.IDENTITY_CONDITIONED:
            if not request.identity_reference_ids:
                return self._deny("ORIGINAL_SCENE_IDENTITY_REFERENCE_MISSING", runtime.runtime_id)
            if not runtime.identity_fidelity_gate_required:
                return self._deny("ORIGINAL_SCENE_IDENTITY_GATE_REQUIRED", runtime.runtime_id)
        return OriginalSceneExecutionDecision(
            admitted=True,
            reason="ORIGINAL_SCENE_RUNTIME_ADMITTED",
            runtime_id=runtime.runtime_id,
            requires_semantic_inspection=True,
            requires_identity_fidelity_gate=runtime.identity_fidelity_gate_required,
            publication_ready=False,
        )

    @staticmethod
    def _deny(reason: str, runtime_id: str | None = None) -> OriginalSceneExecutionDecision:
        return OriginalSceneExecutionDecision(
            admitted=False,
            reason=reason,
            runtime_id=runtime_id,
            requires_semantic_inspection=False,
            requires_identity_fidelity_gate=False,
            publication_ready=False,
        )
