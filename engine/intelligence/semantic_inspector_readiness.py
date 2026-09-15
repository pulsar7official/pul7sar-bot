"""Runtime readiness probe for the optional local Qwen semantic inspector.

The probe never downloads model weights. It verifies that the installed Python
stack exposes the *public* Transformers Qwen2.5-VL API before Colab spends GPU
time on FLUX or downloads/loads semantic-inspector weights.

Important compatibility rules:
- do not import Qwen2.5-VL classes from the private
  ``transformers.models.qwen2_5_vl`` package;
- use only the exact semantic-runtime builds qualified for the Golden path;
- prove that Pillow public image/drawing/font modules import coherently;
- do not probe non-public/nonexistent symbols such as ``PIL.ImageText``.
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
    VERIFIED_TRANSFORMERS_VERSION = "4.56.2"
    VERIFIED_PILLOW_VERSION = "11.3.0"

    @staticmethod
    def _major(version: str | None) -> int | None:
        if not version:
            return None
        token = version.split(".", 1)[0]
        try:
            return int(token)
        except ValueError:
            return None

    def inspect(self) -> SemanticInspectorReadiness:
        failures: list[str] = []
        transformers_version = None
        torch_version = None
        cuda = False

        try:
            import transformers

            transformers_version = getattr(transformers, "__version__", None)
            major = self._major(transformers_version)
            if major is not None and major >= 5:
                failures.append(
                    "transformers_major_version_unverified:"
                    + str(transformers_version)
                    + ":expected_<5"
                )
            if transformers_version != self.VERIFIED_TRANSFORMERS_VERSION:
                failures.append(
                    "transformers_version_drift:"
                    + str(transformers_version)
                    + ":expected="
                    + self.VERIFIED_TRANSFORMERS_VERSION
                )

            # Use only the documented public API. Hugging Face documents both
            # Qwen2_5_VLConfig and pipeline at transformers package top level.
            from transformers import Qwen2_5_VLConfig, pipeline  # noqa: F401

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
            import PIL
            from PIL import Image, ImageDraw, ImageFont  # noqa: F401

            pillow_version = getattr(PIL, "__version__", None)
            pillow_major = self._major(pillow_version)
            if pillow_major is not None and pillow_major >= 12:
                failures.append(
                    "pillow_major_version_unverified:"
                    + str(pillow_version)
                    + ":expected_<12"
                )
            if pillow_version != self.VERIFIED_PILLOW_VERSION:
                failures.append(
                    "pillow_version_drift:"
                    + str(pillow_version)
                    + ":expected="
                    + self.VERIFIED_PILLOW_VERSION
                )
            if Image is None or ImageDraw is None or ImageFont is None:  # defensive only
                failures.append("pillow_public_modules_unavailable")
        except Exception as exc:
            failures.append(
                "pillow_runtime_incoherent:"
                + exc.__class__.__name__
                + ":"
                + str(exc)[:240]
            )

        return SemanticInspectorReadiness(
            ready=not failures,
            model_id=self.MODEL_ID,
            failures=tuple(failures),
            transformers_version=transformers_version,
            torch_version=torch_version,
            cuda_available=cuda,
        )
