# Phase 18 — Change Set 352: Local Qwen Snapshot Byte-Inventory Binding

## Objective
Prevent a genuine local Qwen model-load attempt from consuming snapshot bytes that changed after static readiness but before `QwenImagePipeline.from_pretrained(..., local_files_only=True)`.

CS351 established structural readiness. CS352 adds deterministic byte identity at the inference edge; it does not create pixels and grants no semantic, quality, Golden, publication, or external authority.

## New inventory contract
`engine/intelligence/qwen_image_snapshot_inventory.py` inventories the exact approved `snapshots/<revision>` directory using local filesystem reads only.

The inventory:
- re-validates the exact approved revision;
- requires canonical Hugging Face model-cache layout;
- requires a readable `model_index.json` declaring `QwenImagePipeline`;
- requires at least one file under every declared two-item Diffusers component;
- hashes every locally resolved snapshot file with SHA-256;
- records deterministic relative paths, byte sizes, file count, and total bytes;
- permits Hugging Face cache symlinks only when their resolved target remains inside the same model cache root;
- rejects broken/external file targets and directory symlinks;
- produces one canonical `snapshot_inventory_sha256` independent of absolute host paths.

No Hub lookup, HTTP request, model download, or model load is performed.

## Inference-edge binding
`engine/intelligence/qwen_image_local_inference_runtime.py` now:
1. preserves `$0-local` and CS351 static readiness requirements;
2. requires `snapshot_structure_verified=true`;
3. records a local snapshot byte inventory after static preflight;
4. imports and re-validates the exact live runtime identity;
5. records a second byte inventory immediately before `from_pretrained`;
6. fails closed on any inventory drift;
7. only then permits `QwenImagePipeline.from_pretrained(..., local_files_only=True)`.

This closes an avoidable pre-load TOCTOU window. It does not claim resource sufficiency; real RAM/VRAM sufficiency remains provable only by a genuine load/inference attempt.

## Regression coverage
CS352 adds coverage for:
- deterministic inventory identity on unchanged local bytes;
- inventory hash change when a component byte changes;
- fail-closed inference-edge behavior when the two inventories differ;
- allowed Hugging Face blob symlink targets inside the same model cache root;
- rejected symlink targets outside that root;
- missing declared component files;
- wrong pipeline class;
- continued exact `local_files_only=True` and native-BF16 model-load call behavior;
- continued zero-cost, static-preflight, runtime-identity, and offload gates.

## Authority boundary
CS352 cannot set or infer any of the following:
- factual/freshness approval;
- entity/identity approval;
- sentiment neutrality / loser-respect approval;
- semantic QA approval;
- visual-quality or Golden-quality approval;
- Human Visual Review approval;
- Brand/Typography/Presentation approval;
- Final Composed or Final Semantic approval;
- SemanticPublicationGate allowance;
- Genuine Golden PNG creation;
- publication readiness;
- external publication authority.

The established downstream path through CS284 → CS285 → CS286 remains unchanged.

## Zero-cost / offline boundary
All new checks are local filesystem operations. CS352 introduces no paid execution path, no network fallback, no model fetch, and no upload/publish side effect.
