#!/usr/bin/env python3
"""Measure one real Qwen-Image-2512 Elite GPU qualification run.

This is an explicit engineering bootstrap command, not CI and not publication.
It may load/download the official local weights when invoked by an operator on a
CUDA host. Success proves only the observed GPU class and canvas envelope; it does
not invent a universal VRAM minimum.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from engine.intelligence.cuda_memory import CudaPeakMemoryTracker
from engine.intelligence.elite_runtime_qualification import EliteRuntimeQualificationReceipt
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest, LocalBackendResultGate
from engine.intelligence.local_diffusers_adapter import DiffusersExecutionConfig, DiffusersLocalBackend
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_runtime import LocalRuntimeProbe, RuntimeKind
from engine.intelligence.qwen_image_2512_diffusers import QwenImage2512DiffusersProbe, build_qwen_image_2512_pipeline_factory
from engine.intelligence.zero_cost_models import QWEN_IMAGE_2512_LOCAL


QUALIFICATION_WIDTH = 1088
QUALIFICATION_HEIGHT = 1920
QUALIFICATION_SEED = 2512


def qualify(*, output_dir: str, receipt_path: str) -> EliteRuntimeQualificationReceipt:
    model = QWEN_IMAGE_2512_LOCAL
    runtime = LocalRuntimeProbe().detect()
    if runtime.kind is not RuntimeKind.LOCAL_CUDA or not runtime.cuda_available:
        raise RuntimeError("Qwen Elite qualification requires a real CUDA GPU")
    if runtime.metadata.get("bf16_supported") is not True:
        raise RuntimeError("Qwen Elite qualification requires proven BF16 support")
    if not runtime.gpu_name or runtime.gpu_vram_gb is None or not runtime.metadata.get("compute_capability"):
        raise RuntimeError("Qwen Elite qualification requires complete GPU identity telemetry")

    backend_snapshot = QwenImage2512DiffusersProbe().probe()
    if not backend_snapshot.available:
        raise RuntimeError("Qwen Diffusers backend is unavailable: " + "; ".join(backend_snapshot.details))
    dtype = LocalDTypeSelector().select(runtime, "bfloat16")
    request = LocalBackendGenerationRequest(
        provider_id=model.provider_id,
        model_id=model.model_id,
        backend="diffusers",
        prompt=(
            "A premium cinematic global sports editorial atmosphere with realistic architectural depth, "
            "dramatic controlled lighting, subtle crowd-scale energy and clean negative space. "
            "One continuous physical scene, no readable text, no numbers, no logos, no crests, no watermark, "
            "no recognizable real person, no exact playing-field markings."
        ),
        native_negative_constraints=(),
        width=QUALIFICATION_WIDTH,
        height=QUALIFICATION_HEIGHT,
        seed=QUALIFICATION_SEED,
        request_id="qwen-image-2512-runtime-qualification",
        metadata={
            "cost_mode": "$0-local",
            "qualification_only": True,
            "publication_ready": False,
            "image_quality_tier": "elite",
        },
    )
    tracker = CudaPeakMemoryTracker()
    tracker.reset()
    backend = DiffusersLocalBackend(
        DiffusersExecutionConfig(output_dir=output_dir, dtype=dtype.resolved),
        build_qwen_image_2512_pipeline_factory(),
    )
    result = backend.generate(request)
    LocalBackendResultGate().validate(request, result)
    output = Path(result.output_ref)
    if not output.is_file():
        raise RuntimeError("Qwen qualification returned no real PNG")
    digest = sha256(output.read_bytes()).hexdigest()
    memory = tracker.capture()
    receipt = EliteRuntimeQualificationReceipt(
        provider_id=model.provider_id,
        model_id=model.model_id,
        backend="diffusers",
        dtype=dtype.resolved,
        gpu_name=runtime.gpu_name,
        gpu_vram_gb=runtime.gpu_vram_gb,
        compute_capability=str(runtime.metadata["compute_capability"]),
        bf16_supported=True,
        qualified_width=QUALIFICATION_WIDTH,
        qualified_height=QUALIFICATION_HEIGHT,
        backend_version=str(backend_snapshot.version or "unknown"),
        png_sha256=digest,
        cuda_peak_allocated_gb=memory.peak_allocated_gb,
        cuda_peak_reserved_gb=memory.peak_reserved_gb,
        qualified_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    receipt.write(receipt_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure Qwen-Image-2512 Elite runtime qualification")
    parser.add_argument("--output-dir", default="output/phase18_qwen_qualification")
    parser.add_argument("--receipt", default="output/phase18_qwen_qualification/qualification.json")
    args = parser.parse_args()
    receipt = qualify(output_dir=args.output_dir, receipt_path=args.receipt)
    print(f"QWEN_IMAGE_2512_QUALIFIED gpu={receipt.gpu_name} canvas={receipt.qualified_width}x{receipt.qualified_height} peak_reserved_gb={receipt.cuda_peak_reserved_gb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
