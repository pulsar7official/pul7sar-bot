"""Optional zero-cost ComfyUI backend adapter shell.

The adapter is intentionally transport-neutral. It prepares/validates the
PUL7SAR request contract and delegates HTTP/workflow specifics to an injected
executor so no external service is required by CI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendSnapshot
from engine.intelligence.local_backend_execution import (
    LocalBackendGenerationRequest,
    LocalBackendGenerationResult,
)


@dataclass(frozen=True)
class ComfyUIExecutionConfig:
    endpoint: str
    workflow_id: str

    def __post_init__(self) -> None:
        for name in ("endpoint", "workflow_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not self.endpoint.startswith(("http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost")):
            raise ValueError("ComfyUI endpoint must be explicitly local")


class ComfyUIBackendProbe:
    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    def probe(self) -> LocalBackendSnapshot:
        return LocalBackendSnapshot(
            LocalBackendKind.COMFYUI,
            bool(self.endpoint),
            endpoint=self.endpoint,
            details=("explicit-local-endpoint-required",),
        )


class ComfyUILocalBackend:
    backend_id = LocalBackendKind.COMFYUI.value

    def __init__(self, config: ComfyUIExecutionConfig, executor: Callable[[str, str, Mapping[str, Any]], Mapping[str, Any]]) -> None:
        self.config = config
        self._executor = executor

    def generate(self, request: LocalBackendGenerationRequest) -> LocalBackendGenerationResult:
        if request.backend != self.backend_id:
            raise ValueError("ComfyUI backend received a request for another backend")
        payload = {
            "provider_id": request.provider_id,
            "model_id": request.model_id,
            "prompt": request.prompt,
            "negative_constraints": list(request.native_negative_constraints),
            "width": request.width,
            "height": request.height,
            "seed": request.seed,
            "request_id": request.request_id,
            "reference_asset_ids": list(request.reference_asset_ids),
            "metadata": dict(request.metadata),
        }
        result = self._executor(self.config.endpoint, self.config.workflow_id, payload)
        output_ref = result.get("output_ref") if isinstance(result, Mapping) else None
        if not isinstance(output_ref, str) or not output_ref.strip():
            raise ValueError("ComfyUI executor did not return output_ref")
        return LocalBackendGenerationResult(
            provider_id=request.provider_id,
            model_id=request.model_id,
            backend=request.backend,
            request_id=request.request_id,
            seed=request.seed,
            width=request.width,
            height=request.height,
            output_ref=output_ref,
            metadata={"adapter": "comfyui", "workflow_id": self.config.workflow_id},
        )
