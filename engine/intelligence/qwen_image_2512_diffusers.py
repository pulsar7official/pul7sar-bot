"""Optional Qwen-Image-2512 Diffusers runtime for PUL7SAR Elite base scenes.

Imports are lazy: repository import and CPU CI never install packages, download
weights or contact the network. The factory follows the official Hugging Face
Diffusers loading shape while the wrapper enforces PUL7SAR's locked dimensions
and seed before invoking a real pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as package_version
import inspect
from typing import Any, Callable

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendSnapshot


@dataclass(frozen=True)
class QwenImage2512InferenceConfig:
    cpu_offload: bool = True
    prefer_model_cpu_offload: bool = True


class QwenImage2512DiffusersProbe:
    """Prove installed torch/diffusers expose a compatible Qwen image pipeline."""

    def probe(self) -> LocalBackendSnapshot:
        details = ["qwen-image-2512-preflight"]
        try:
            import_module("torch")
        except (ImportError, ModuleNotFoundError):
            return LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, False, version=None, details=tuple(details + ["torch-missing"]))
        try:
            diffusers = import_module("diffusers")
        except (ImportError, ModuleNotFoundError):
            return LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, False, version=None, details=tuple(details + ["diffusers-missing"]))
        # Current official model metadata names QwenImagePipeline. Some Diffusers
        # installations also route it through DiffusionPipeline.from_pretrained.
        direct = getattr(diffusers, "QwenImagePipeline", None)
        generic = getattr(diffusers, "DiffusionPipeline", None)
        supported = direct is not None or generic is not None
        details.append("QwenImagePipeline-present" if direct is not None else "QwenImagePipeline-via-DiffusionPipeline" if generic is not None else "QwenImagePipeline-missing")
        try:
            version = package_version("diffusers")
        except PackageNotFoundError:
            version = getattr(diffusers, "__version__", None)
        return LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, supported, version=version, details=tuple(details))


class QwenImage2512PipelineWrapper:
    def __init__(self, pipe: Any, torch_module: Any, config: QwenImage2512InferenceConfig, *, offload_mode: str) -> None:
        self._pipe = pipe
        self._torch = torch_module
        self._config = config
        self._offload_mode = offload_mode

    @staticmethod
    def _supports(callable_obj: Any, name: str) -> bool:
        try:
            parameters = inspect.signature(callable_obj).parameters.values()
        except (TypeError, ValueError):
            return False
        return any(p.kind is inspect.Parameter.VAR_KEYWORD for p in parameters) or any(p.name == name for p in parameters)

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
        if reference_asset_ids:
            raise ValueError("Qwen-Image-2512 text-to-image base-scene wrapper does not consume reference asset IDs")
        call = self._pipe.__call__
        for required in ("width", "height", "generator"):
            if not self._supports(call, required):
                raise RuntimeError(f"installed Qwen image pipeline cannot preserve locked {required}")
        if negative_prompt and not self._supports(call, "negative_prompt"):
            raise RuntimeError("installed Qwen image pipeline cannot preserve native negative constraints")
        generator_device = "cuda" if getattr(getattr(self._torch, "cuda", None), "is_available", lambda: False)() else "cpu"
        generator = self._torch.Generator(device=generator_device).manual_seed(seed)
        kwargs: dict[str, Any] = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "generator": generator,
        }
        if negative_prompt:
            kwargs["negative_prompt"] = negative_prompt
        result = self._pipe(**kwargs)
        images = getattr(result, "images", None)
        if not images:
            raise ValueError("Qwen image pipeline returned no images")
        return {
            "image": images[0],
            "metadata": {
                "pipeline": "QwenImagePipeline",
                "model_family": "Qwen-Image-2512",
                "offload_mode": self._offload_mode,
                "seed_locked": True,
                "canvas_locked": True,
            },
        }


def build_qwen_image_2512_pipeline_factory(
    *,
    inference: QwenImage2512InferenceConfig = QwenImage2512InferenceConfig(),
    pipeline_loader: Callable[..., Any] | None = None,
    torch_module: Any | None = None,
) -> Callable[[str, str], QwenImage2512PipelineWrapper]:
    """Return the factory consumed by :class:`DiffusersLocalBackend`.

    Default loading follows the official model-card example: DiffusionPipeline
    from pretrained weights in BF16/CUDA. Optional CPU offload is enabled only
    after construction when the installed pipeline exposes an official Diffusers
    offload method.
    """
    def factory(model_id: str, dtype: str) -> QwenImage2512PipelineWrapper:
        nonlocal pipeline_loader, torch_module
        if torch_module is None:
            try:
                import torch as runtime_torch
            except ImportError as exc:
                raise RuntimeError("PyTorch is required for Qwen-Image-2512 local execution") from exc
            torch_module = runtime_torch
        if pipeline_loader is None:
            try:
                from diffusers import DiffusionPipeline
            except ImportError as exc:
                raise RuntimeError("Diffusers with Qwen image support is required") from exc
            pipeline_loader = DiffusionPipeline.from_pretrained
        dtype_map = {
            "float16": torch_module.float16,
            "bfloat16": torch_module.bfloat16,
            "float32": torch_module.float32,
        }
        if dtype not in dtype_map:
            raise ValueError("unsupported dtype")
        # `dtype` and `device_map='cuda'` match the official model-card loader.
        pipe = pipeline_loader(model_id, dtype=dtype_map[dtype], device_map="cuda")
        offload_mode = "none"
        if inference.cpu_offload:
            model_offload = getattr(pipe, "enable_model_cpu_offload", None)
            sequential = getattr(pipe, "enable_sequential_cpu_offload", None)
            if inference.prefer_model_cpu_offload and callable(model_offload):
                model_offload()
                offload_mode = "model_cpu"
            elif callable(sequential):
                sequential()
                offload_mode = "sequential_cpu"
            elif callable(model_offload):
                model_offload()
                offload_mode = "model_cpu"
            else:
                # Device-map loading is still a valid official path. Do not fail
                # solely because an optional offload helper is absent.
                offload_mode = "device_map_cuda"
        return QwenImage2512PipelineWrapper(pipe, torch_module, inference, offload_mode=offload_mode)
    return factory
