"""Concrete optional FLUX.2 [klein] 4B Diffusers runtime wrapper.

The module imports torch/diffusers only when a real runtime factory is invoked.
It follows the official Flux2KleinPipeline inference shape while preserving the
provider-neutral DiffusersLocalBackend contract used by PUL7SAR.

No dependency installation, weight download, or network call happens at import.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Flux2KleinInferenceConfig:
    guidance_scale: float = 1.0
    num_inference_steps: int = 4
    cpu_offload: bool = True

    def __post_init__(self) -> None:
        if self.guidance_scale <= 0:
            raise ValueError("guidance_scale must be positive")
        if self.num_inference_steps <= 0:
            raise ValueError("num_inference_steps must be positive")


class Flux2KleinPipelineWrapper:
    """Translate PUL7SAR's local backend call into Flux2KleinPipeline arguments."""

    def __init__(self, pipe: Any, torch_module: Any, config: Flux2KleinInferenceConfig) -> None:
        self._pipe = pipe
        self._torch = torch_module
        self._config = config

    def __call__(
        self,
        *,
        prompt: str,
        negative_prompt: str | None,
        width: int,
        height: int,
        seed: int,
        reference_asset_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        if negative_prompt:
            raise ValueError("FLUX.2 klein wrapper does not accept native negative prompts")
        if reference_asset_ids:
            raise ValueError(
                "identity/reference image execution requires a verified asset-path resolver and is not enabled in the text-to-image wrapper"
            )
        generator = self._torch.Generator(device="cuda").manual_seed(seed)
        result = self._pipe(
            prompt=prompt,
            height=height,
            width=width,
            guidance_scale=self._config.guidance_scale,
            num_inference_steps=self._config.num_inference_steps,
            generator=generator,
        )
        images = getattr(result, "images", None)
        if not images:
            raise ValueError("Flux2KleinPipeline returned no images")
        return {"image": images[0]}


def build_flux2_klein_pipeline_factory(
    *,
    inference: Flux2KleinInferenceConfig = Flux2KleinInferenceConfig(),
    pipeline_loader: Callable[..., Any] | None = None,
    torch_module: Any | None = None,
) -> Callable[[str, str], Flux2KleinPipelineWrapper]:
    """Return the concrete factory expected by DiffusersLocalBackend.

    Tests may inject `pipeline_loader` and `torch_module`; production/local use
    imports the optional dependencies lazily.
    """

    def factory(model_id: str, dtype: str) -> Flux2KleinPipelineWrapper:
        nonlocal pipeline_loader, torch_module
        if torch_module is None:
            try:
                import torch as runtime_torch
            except ImportError as exc:
                raise RuntimeError("PyTorch is required for real FLUX.2 local execution") from exc
            torch_module = runtime_torch
        if pipeline_loader is None:
            try:
                from diffusers import Flux2KleinPipeline
            except ImportError as exc:
                raise RuntimeError("Diffusers with Flux2KleinPipeline support is required") from exc
            pipeline_loader = Flux2KleinPipeline.from_pretrained

        dtype_map = {
            "float16": torch_module.float16,
            "bfloat16": torch_module.bfloat16,
            "float32": torch_module.float32,
        }
        if dtype not in dtype_map:
            raise ValueError("unsupported dtype")
        pipe = pipeline_loader(model_id, torch_dtype=dtype_map[dtype])
        if inference.cpu_offload:
            enable = getattr(pipe, "enable_model_cpu_offload", None)
            if enable is None:
                raise RuntimeError("Flux2Klein pipeline does not expose enable_model_cpu_offload")
            enable()
        return Flux2KleinPipelineWrapper(pipe, torch_module, inference)

    return factory
