# Phase 18 Change Set 351 — Local Qwen Snapshot Structure Preflight

## Purpose
CS351 reduces the remaining gap to the first genuine Golden Visual PNG at the actual zero-cost GPU execution edge. It does not add a new quality/publication authority and does not fabricate inference. Instead, it closes a false-positive in the existing Qwen static readiness probe: before CS351, a correctly named but empty `snapshots/<approved-revision>` directory could satisfy snapshot revision verification and therefore appear statically ready when the CUDA/software checks also passed.

## Scope
Production file modified:
- `engine/intelligence/qwen_image_gpu_readiness.py`

Regression file modified:
- `tests/test_phase18_qwen_image_gpu_readiness.py`

No workflow, publication gate, semantic gate, identity gate, sentiment gate, quality gate, Human Review contract, Golden materializer, or `main` code is modified.

## New fail-closed snapshot checks
For an already-local Qwen/Qwen-Image-2512 snapshot, static readiness now requires all of the following before `ready_for_model_load_attempt=true`:

1. The path still resolves to the exact approved immutable revision.
2. The snapshot directory exists locally.
3. `model_index.json` exists and parses as JSON.
4. `_class_name` is exactly `QwenImagePipeline`.
5. At least one Diffusers component is declared by the model index.
6. Every declared two-item Diffusers component has a non-empty local component directory.

Hugging Face cache symlinks are allowed when they resolve to real local files. No network lookup or download is performed.

## Deliberate authority boundary
Snapshot structure verification is only a pre-model-load check. It does **not** prove:
- that all model weight shards are complete;
- that the model can fit host RAM/VRAM;
- that `from_pretrained` succeeds;
- that inference executes;
- that a canonical candidate exists;
- that factual, identity, sentiment, semantic, visual-quality, Golden-quality, Human Review, presentation, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden, or publication readiness approvals have passed.

Resource sufficiency remains provable only by the genuine local model-load/inference attempt already protected by the existing manifest-bound execution chain.

## Schema
The readiness report schema advances from `pul7sar.phase18.qwen_image_gpu_readiness.v1` to `pul7sar.phase18.qwen_image_gpu_readiness.v2` and adds:
- `snapshot_structure_verified`
- `snapshot_component_count`

New blocker codes are specific and fail-closed, including missing/invalid model index, pipeline-class mismatch, undeclared components, and missing declared component data.

## Zero-cost and network policy
CS351 performs filesystem and JSON inspection only. It does not import or load model weights, does not call Hugging Face Hub, and does not introduce any paid or network fallback.

## Regression coverage
The tests now prove:
- CPU-only hosts still fail closed;
- a structurally valid local snapshot may pass static preflight on a compatible mocked CUDA/BF16 host without claiming inference;
- observed VRAM is not turned into an invented threshold;
- wrong immutable revision fails closed;
- a correctly named but empty snapshot fails closed;
- a missing/empty declared component fails closed;
- a non-Qwen pipeline class fails closed.

## Relation to the Genuine Golden path
The downstream CS284 → CS285 → CS286 chain remains unchanged. CS351 only makes the upstream genuine-Qwen launch preflight more truthful, preventing an avoidable launch attempt against an obviously incomplete local model snapshot.
