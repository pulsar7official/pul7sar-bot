"""Runtime readiness probe for the optional local Qwen semantic inspector.

The probe never downloads a model. It verifies that the installed Python stack
can represent Qwen2.5-VL before Colab spends time downloading/loading weights.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticInspectorReadiness:
    ready: bool
    model_id: str
    failures: tuple[str, ...]
    transformers_version: str | None = None
    torch_version: str | None = None
    cuda_available: bool = False


class Qwen25VLReadinessProbe:
    MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"

    def inspect(self) -> SemanticInspectorReadiness:
        failures: list[str] = []
        transformers_version = None
        torch_version = None
        cuda = False

        try:
            import transformers
            transformers_version = getattr(transformers, "__version__", None)
            # The architecture must be registered; an old Transformers build can
            # otherwise fail only after a multi-GB model download.
            from transformers.models.qwen2_5_vl import Qwen2_5_VLConfig  # noqa: F401
            from transformers import pipeline  # noqa: F401
        except Exception as exc:
            failures.append("transformers_qwen2_5_vl_unavailable:" + exc.__class__.__name__)

        try:
            import torch
            torch_version = getattr(torch, "__version__", None)
            cuda = bool(torch.cuda.is_available())
            if not cuda:
                failures.append("cuda_unavailable_for_local_semantic_inspection")
        except Exception as exc:
            failures.append("torch_unavailable:" + exc.__class__.__name__)

        try:
            from PIL import Image  # noqa: F401
        except Exception as exc:
            failures.append("pillow_unavailable:" + exc.__class__.__name__)

        return SemanticInspectorReadiness(
            ready=not failures,
            model_id=self.MODEL_ID,
            failures=tuple(failures),
            transformers_version=transformers_version,
            torch_version=torch_version,
            cuda_available=cuda,
        )
