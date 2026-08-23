"""Runtime readiness probe for the optional local Qwen semantic inspector.

The probe never downloads model weights. It verifies that the installed Python
stack exposes the *public* Transformers Qwen2.5-VL API before Colab spends GPU
time on FLUX or downloads/loads semantic-inspector weights.

Important compatibility rule: do not import Qwen2.5-VL classes from the private
``transformers.models.qwen2_5_vl`` package. Transformers may reorganize that
internal package while keeping its documented top-level public API stable.
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
            # Use only the documented public API. Hugging Face documents both
            # Qwen2_5_VLConfig and pipeline at transformers package top level.
            from transformers import Qwen2_5_VLConfig, pipeline  # noqa: F401

            # The inspector itself uses image-text-to-text Pipeline. Merely
            # importing the callable proves registration without downloading
            # model weights in this readiness phase.
            if Qwen2_5_VLConfig is None or pipeline is None:  # defensive only
                failures.append("transformers_qwen2_5_vl_public_api_unavailable")
        except Exception as exc:
            failures.append(
                "transformers_qwen2_5_vl_unavailable:"
                + exc.__class__.__name__
                + ":"
                + str(exc)[:240]
            )

        try:
            import torch

            torch_version = getattr(torch, "__version__", None)
            cuda = bool(torch.cuda.is_available())
            if not cuda:
                failures.append("cuda_unavailable_for_local_semantic_inspection")
        except Exception as exc:
            failures.append("torch_unavailable:" + exc.__class__.__name__ + ":" + str(exc)[:240])

        try:
            from PIL import Image  # noqa: F401
        except Exception as exc:
            failures.append("pillow_unavailable:" + exc.__class__.__name__ + ":" + str(exc)[:240])

        return SemanticInspectorReadiness(
            ready=not failures,
            model_id=self.MODEL_ID,
            failures=tuple(failures),
            transformers_version=transformers_version,
            torch_version=torch_version,
            cuda_available=cuda,
        )
