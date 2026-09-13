# Phase 18 Change Set 288 — Qwen-Image Model-Load Attestation

## Purpose

CS288 reduces the remaining gap to the first genuine Golden Visual by introducing a fail-closed, auditable model-load step for the exact approved `Qwen/Qwen-Image-2512` snapshot. It is intentionally not an inference or visual-approval change set.

## Preconditions

Before any `from_pretrained` call, CS288 requires CS287 static readiness to pass, including:

- CUDA-visible NVIDIA runtime,
- CUDA-enabled PyTorch,
- native BF16 support,
- importable `QwenImagePipeline`,
- sequential CPU offload support,
- `nvidia-smi`,
- exact immutable approved local Hugging Face snapshot revision.

The execution cost mode must also be exactly `$0-local`.

## Model-load behavior

When all preconditions pass, CS288 performs one real local-only load:

- `QwenImagePipeline.from_pretrained(<approved local snapshot>, torch_dtype=torch.bfloat16, local_files_only=True)`
- `enable_sequential_cpu_offload()`

No mutable model ID is supplied to `from_pretrained`; the resolved immutable local snapshot path is used directly. `local_files_only=True` forbids download fallback.

## Fail-closed evidence

The attestation records whether:

- static preflight passed,
- model loading was actually attempted,
- loading actually succeeded,
- sequential CPU offload was actually enabled,
- the operation remained local-only / network-forbidden,
- a concrete exception type occurred on load failure.

A real resource or compatibility failure is recorded as failure. It must not be converted into a successful model-load claim from static metadata.

## Authority limits

Even a successful CS288 result always keeps:

- `genuine_inference_executed=false`
- `png_created=false`
- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

Model-load success proves only that this host loaded the approved model under the required local BF16/offload policy. It does not prove inference, image quality, factual correctness, identity correctness, sentiment compliance, SemanticPublication approval, Golden materialization, or publication readiness.

## Zero-cost and network policy

CS288 is permitted only when `PUL7SAR_PHASE18_COST_MODE=$0-local`. The loader uses only an already-present immutable snapshot and passes `local_files_only=True`. No download or paid endpoint is authorized by this contract.

## CLI

`tools/phase18_qwen_image_model_load_attestation.py` writes machine-readable evidence inside the repository. `--require-loaded` returns a non-zero exit code unless both real loading and sequential CPU offload enabling succeed.

The CLI exposes no inference, image, approval, Golden, publication, network, model-revision, or cost-mode override.

## Relationship to the Genuine Golden path

The intended sequence is now:

`CS287 static GPU preflight -> CS288 genuine model-load attestation -> genuine Qwen inference -> existing factual / identity / sentiment / semantic / composition / quality / human / brand / publication chain -> CS285 Golden materialization -> CS286 publication readiness`.

CS288 therefore materially reduces the execution uncertainty while preserving every downstream gate.
