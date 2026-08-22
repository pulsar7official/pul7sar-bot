"""Optional zero-cost Diffusers backend adapter shell.

This module intentionally avoids importing diffusers/torch at import time.
Heavy local dependencies are optional and execution is fail-closed until the
runtime explicitly proves they are available.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Callable

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendSnapshot
from engine.intelligence.local_backend_execution import (
    LocalBackendGenerationRequest,
    LocalBackendGenerationResult,
)


@dataclass(frozen=True)
class DiffusersExecutionConfig:
    output_dir: str
    dtype: str = "bfloat16"

    def __post_init__(self) -> None:
        if not isinstance(self.output_dir, str) or not self.output_dir.strip():
            raise ValueError("output_dir must be non-empty")
        if self.dtype not in {"float16", "bfloat16", "float32"}:
            raise ValueError("unsupported dtype")


class DiffusersBackendProbe:
    def probe(self) -> LocalBackendSnapshot:
        available = find_spec("diffusers") is not None and find_spec("torch") is not None
        version = None
        if available:
            try:
                from importlib.metadata import version as pkg_version
                version = pkg_version("diffusers")
            except Exception:
                version = None
        return LocalBackendSnapshot(
            LocalBackendKind.DIFFUSERS,
            available,
            version=version,
            details=("optional-local-backend",),
        )


class DiffusersLocalBackend:
    """Execution wrapper with dependency injection for testability.

    A concrete pipeline factory is injected at runtime so Phase 18 does not
    hard-code model classes or force heavyweight packages into CI.
    """

    backend_id = LocalBackendKind.DIFFUSERS.value

    def __init__(self, config: DiffusersExecutionConfig, pipeline_factory: Callable[[str, str], Any]) -> None:
        self.config = config
        self._pipeline_factory = pipeline_factory

    def generate(self, request: LocalBackendGenerationRequest) -> LocalBackendGenerationResult:
        if request.backend != self.backend_id:
            raise ValueError("Diffusers backend received a request for another backend")
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pipeline = self._pipeline_factory(request.model_id, self.config.dtype)
        result = pipeline(
            prompt=request.prompt,
            negative_prompt="\n".join(request.native_negative_constraints) or None,
            width=request.width,
            height=request.height,
            seed=request.seed,
            reference_asset_ids=request.reference_asset_ids,
        )
        image = getattr(result, "image", None)
        if image is None and isinstance(result, dict):
            image = result.get("image")
        if image is None or not hasattr(image, "save"):
            raise ValueError("Diffusers pipeline did not return a saveable image")

        output_path = output_dir / f"{request.request_id}.png"
        image.save(output_path)
        return LocalBackendGenerationResult(
            provider_id=request.provider_id,
            model_id=request.model_id,
            backend=request.backend,
            request_id=request.request_id,
            seed=request.seed,
            width=request.width,
            height=request.height,
            output_ref=str(output_path),
            metadata={"adapter": "diffusers", "dtype": self.config.dtype},
        )
