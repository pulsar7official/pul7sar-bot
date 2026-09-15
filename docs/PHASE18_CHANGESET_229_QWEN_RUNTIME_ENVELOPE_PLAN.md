# Phase 18 Change Set 229 — Qwen Runtime Envelope Measurement Plan

## Purpose
Lock the future Qwen Image 2512 runtime-envelope experiment before a compatible local GPU host is available. This avoids ad-hoc probe escalation and preserves evidence comparability.

## Added
- `engine/intelligence/qwen_image_runtime_envelope_plan.py`
- `tools/phase18_build_qwen_runtime_envelope_plan.py`
- `tests/test_phase18_qwen_image_runtime_envelope_plan.py`

## Locked probe sequence
1. 512×512 at 4 steps.
2. 768×768 at 6 steps.
3. 1024×1024 at 8 steps.

All probes require BF16 and sequential CPU offload. Execution must stop on the first CUDA out-of-memory event, non-zero child exit, invalid PNG evidence, BF16 loss, offload-contract drift, or missing/inconsistent telemetry.

These are engineering measurement points only. They are not Golden rendering settings and do not establish a production runtime floor.

## Authority boundaries
The plan remains measurement-only and engineering-only. It cannot establish runtime qualification, authorize canonical generation, reuse engineering pixels as canonical evidence, approve semantics, approve Golden quality, or approve publication.

## Golden Visual status
No canonical PNG was generated in this change set. Repository execution does not currently expose a compatible self-hosted NVIDIA CUDA path with the pinned Qwen Image 2512 snapshot and required measured runtime evidence.
