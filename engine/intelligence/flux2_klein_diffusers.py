"""Concrete optional FLUX.2 [klein] 4B Diffusers runtime wrapper.

The module imports torch/diffusers only when runtime probing or a real pipeline
factory is invoked. It follows the official Flux2KleinPipeline inference shape
while preserving the provider-neutral DiffusersLocalBackend contract used by
PUL7SAR.

No dependency installation, weight download, or network call happens at import.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Any, Callable

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from engine.intelligence.local_backend import LocalBackendKind, LocalBackendSnapshot


@dataclass(frozen=True)
class Flux2KleinInferenceConfig:
    guidance_scale: float = 1.0
    num_inference_steps: int = 4
    cpu_offload: bool = True
    prefer_sequential_cpu_offload: bool = True
    model_offload_minimum_total_vram_gb: float = 16.0

    def __post_init__(self) -> None:
        if self.guidance_scale <= 0:
            raise ValueError("guidance_scale must be positive")
        if self.num_inference_steps <= 0:
            raise ValueError("num_inference_steps must be positive")
        if self.model_offload_minimum_total_vram_gb <= 0:
            raise ValueError("model_offload_minimum_total_vram_gb must be positive")


class Flux2KleinDiffusersProbe:
    """Prove that the installed Diffusers build exposes Flux2KleinPipeline.

    Generic `diffusers` presence is insufficient: an older build can import
    successfully yet still be unable to execute the approved FLUX.2 klein model.
    This probe performs no model download and no network call.
    """

    def probe(self) -> LocalBackendSnapshot:
        details: list[str] = ["flux2-klein-preflight"]
        try:
            import_module("torch")
        except (ImportError, ModuleNotFoundError):
            return LocalBackendSnapshot(
                LocalBackendKind.DIFFUSERS,
                False,
                version=None,
                details=tuple(details + ["torch-missing"]),
            )
        try:
            diffusers = import_module("diffusers")
        except (ImportError, ModuleNotFoundError):
            return LocalBackendSnapshot(
                LocalBackendKind.DIFFUSERS,
                False,
                version=None,
                details=tuple(details + ["diffusers-missing"]),
            )

        supported = getattr(diffusers, "Flux2KleinPipeline", None) is not None
        try:
            diffusers_version = package_version("diffusers")
        except PackageNotFoundError:
            diffusers_version = getattr(diffusers, "__version__", None)
        details.append("Flux2KleinPipeline-present" if supported else "Flux2KleinPipeline-missing")
        return LocalBackendSnapshot(
            LocalBackendKind.DIFFUSERS,
            supported,
            version=diffusers_version,
            details=tuple(details),
        )


class Flux2KleinPipelineWrapper:
    """Translate PUL7SAR's local backend call into Flux2KleinPipeline arguments."""

    def __init__(
        self,
        pipe: Any,
        torch_module: Any,
        config: Flux2KleinInferenceConfig,
        *,
        offload_mode: str = "none",
        model_revision: str = FLUX2_KLEIN_4B_REVISION,
    ) -> None:
        self._pipe = pipe
        self._torch = torch_module
        self._config = config
        self._offload_mode = offload_mode
        self._model_revision = model_revision

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
        if width % 16 != 0 or height % 16 != 0:
            raise ValueError("FLUX.2 klein native generation canvas must be divisible by 16")
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
        return {
            "image": images[0],
            "metadata": {
                "pipeline": "Flux2KleinPipeline",
                "model_revision": self._model_revision,
                "guidance_scale": self._config.guidance_scale,
                "num_inference_steps": self._config.num_inference_steps,
                "cpu_offload": self._config.cpu_offload,
                "offload_mode": self._offload_mode,
                "native_canvas_alignment": 16,
            },
        }


def _total_cuda_vram_gb(torch_module: Any) -> float | None:
    """Return physical CUDA VRAM when runtime evidence is available.

    This helper deliberately does not guess. If CUDA/device properties cannot be
    proven, callers that need the value must fail closed rather than assuming a
    high-memory host.
    """

    cuda = getattr(torch_module, "cuda", None)
    if cuda is None:
        return None
    is_available = getattr(cuda, "is_available", None)
    if callable(is_available):
        try:
            if not bool(is_available()):
                return None
        except Exception:
            return None
    get_device_properties = getattr(cuda, "get_device_properties", None)
    if not callable(get_device_properties):
        return None
    try:
        properties = get_device_properties(0)
        total_memory = int(getattr(properties, "total_memory"))
    except Exception:
        return None
    if total_memory <= 0:
        return None
    return total_memory / float(1024 ** 3)


def build_flux2_klein_pipeline_factory(
    *,
    inference: Flux2KleinInferenceConfig = Flux2KleinInferenceConfig(),
    pipeline_loader: Callable[..., Any] | None = None,
    torch_module: Any | None = None,
    model_revision: str = FLUX2_KLEIN_4B_REVISION,
) -> Callable[[str, str], Flux2KleinPipelineWrapper]:
    """Return the concrete factory expected by DiffusersLocalBackend.

    Tests may inject `pipeline_loader` and `torch_module`; production/local use
    imports the optional dependencies lazily. The upstream FLUX repository is
    always loaded at an immutable, project-approved Hugging Face commit revision
    so a mutable `main` update cannot silently change Golden Candidate bytes.

    Low-VRAM hosts prefer Diffusers' sequential CPU offload when the installed
    pipeline exposes it. Sequential offload is slower than model-level offload,
    but materially lowers the resident CUDA parameter footprint and is the safe
    first path after a real ~14.6-GiB T4 host proved model-level offload can OOM
    inside FLUX.2 attention at the locked Golden canvas.

    Critically, a low-VRAM host may no longer silently fall back from sequential
    offload to model-level offload. If sequential offload is unavailable, model
    offload is accepted only when physical CUDA VRAM is measurable and strictly
    above the configured low-VRAM safety floor. Unknown VRAM also fails closed.
    The exact model, BF16 dtype, prompt, seed, canvas and inference-step locks are
    unchanged.
    """

    if model_revision != FLUX2_KLEIN_4B_REVISION:
        raise ValueError("FLUX.2 model revision must match the approved immutable revision")

    def factory(model_id: str, dtype: str) -> Flux2KleinPipelineWrapper:
        nonlocal pipeline_loader, torch_module
        if model_id != FLUX2_KLEIN_4B_MODEL_ID:
            raise ValueError("FLUX.2 pipeline factory only accepts the approved model identity")
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
        pipe = pipeline_loader(
            model_id,
            revision=FLUX2_KLEIN_4B_REVISION,
            torch_dtype=dtype_map[dtype],
        )

        offload_mode = "none"
        if inference.cpu_offload:
            sequential = getattr(pipe, "enable_sequential_cpu_offload", None)
            model_offload = getattr(pipe, "enable_model_cpu_offload", None)
            if inference.prefer_sequential_cpu_offload and callable(sequential):
                sequential()
                offload_mode = "sequential_cpu"
            elif callable(model_offload):
                total_vram_gb = _total_cuda_vram_gb(torch_module)
                if inference.prefer_sequential_cpu_offload:
                    if total_vram_gb is None:
                        raise RuntimeError(
                            "sequential CPU offload is unavailable and CUDA VRAM could not be proven; unsafe model-offload fallback blocked"
                        )
                    if total_vram_gb <= inference.model_offload_minimum_total_vram_gb:
                        raise RuntimeError(
                            "sequential CPU offload is required on low-VRAM FLUX.2 hosts; unsafe model-offload fallback blocked"
                        )
                model_offload()
                offload_mode = "model_cpu"
            else:
                raise RuntimeError(
                    "Flux2Klein pipeline exposes neither sequential nor model CPU offload"
                )
        return Flux2KleinPipelineWrapper(
            pipe,
            torch_module,
            inference,
            offload_mode=offload_mode,
            model_revision=FLUX2_KLEIN_4B_REVISION,
        )

    return factory
