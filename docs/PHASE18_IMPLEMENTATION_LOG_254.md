# Phase 18 Implementation Log 254 — Retrieved Source Byte Binding

## Baseline reviewed

- Target branch: `phase18/story-intelligence`
- Baseline HEAD: `acb7dee62902ec1d4a6fc62437dae1f2ba40998b`
- `main` observed read-only at: `8cb07a4f4e331f5956a8c1c8d930699c7b755991`
- No merge, rebase, force-update, or write to `main` was performed.
- Change Set 253 baseline CI: Phase 18 Story Intelligence Verification run `33234854194`, run number `3941`, completed successfully.

## Gap identified

Change Set 253 structurally requires `content_sha256` for every source, but accepts that digest from the manifest. Before a genuine story can be trusted for six-gate replay, the digest should be recomputed from concrete retrieved source bytes rather than accepted as hand-authored provenance.

## Added

1. `engine/intelligence/qwen_image_retrieved_source_byte_binding.py`
   - CPU-only byte-binding layer.
   - Reads a draft story manifest whose source records point to local capture files.
   - Restricts capture paths to an explicit source root.
   - Rejects missing, empty, duplicate, absolute, or escaping capture paths.
   - Computes SHA-256 and byte size from exact source bytes.
   - Emits a Change Set 253-compatible source-backed story manifest.
   - Emits a fail-closed source binding receipt.

2. `tests/test_phase18_qwen_image_retrieved_source_byte_binding.py`
   - exact byte digest binding;
   - digest changes when captured bytes change;
   - path traversal rejection;
   - empty capture rejection;
   - duplicate capture path rejection;
   - downstream authority remains false.

3. `tools/phase18_bind_retrieved_source_bytes.py`
   - CPU-only CLI for converting retrieved captures plus a draft manifest into a byte-bound Change Set 253 manifest.

4. `docs/PHASE18_CHANGESET_254_RETRIEVED_SOURCE_BYTE_BINDING.md`

5. `docs/PHASE18_IMPLEMENTATION_LOG_254.md`

## Modified

- No pre-existing production, gate, generation, publication, or registry implementation was modified.

## Deleted

- None.

## Authority state

The new binding receipt explicitly leaves these false:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `inference_executed`
- `genuine_golden_png_created`
- `publication_ready`

The change does not weaken Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, Zero-cost, Story Semantic Preflight, Semantic/Layer Ownership, Visual Critic, Human Review, Golden-quality thresholds, Exact Brand/Typography, or SemanticPublicationGate.

## Testing status

The regression suite is included in the repository and will be evaluated by the normal Phase 18 Story Intelligence Verification workflow after this change lands. No CI-green claim is made until GitHub reports completion.

## Exact blocker to genuine Golden PNG

No compatible zero-cost local runtime is available in this execution environment proving, in one runtime, NVIDIA CUDA, native BF16, sufficient live VRAM, sufficient system RAM, the exact pinned `Qwen/Qwen-Image-2512` snapshot/revision, a compatible Diffusers/QwenImagePipeline, successful sequential CPU offload, and canonical `$0-local` execution.

## Remaining non-GPU gap

Use genuinely retrieved source bytes with Change Set 254, compile the resulting manifest through Change Set 253, execute all six production gates through Change Set 252, admit freshness through Change Set 237, and independently replay semantics through Change Set 238. Only then may an explicit generation-authorization step be considered.
