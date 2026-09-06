# Phase 18 Change Set 345 — Final Presentation Evidence → Final Composed Visual Approval

## Scope

CS345 closes the current-chain handoff between exact CS344/CS280 Final Presentation evidence and the repository's existing CS281 Final Composed Visual Approval contract. It does not perform another visual review, alter pixels, grant final semantic authority, materialize a Genuine Golden PNG, or publish.

The branch baseline reviewed before writing was `phase18/story-intelligence` at `cac292b33dd349007ffbdd1edc2d830ced5d04f5`. `main` was inspected read-only at `a3176a6d4e224c3b4437d37d76700b395605ece6` and is not modified by this change set.

## Contract

```text
exact CS344 checkpoint
→ independent CS344 replay
→ exact CS280 selected by CS344
→ independent CS280 replay
→ require approved presentation + exact brand + typography integrity
→ replay CS280 review lineage back to exact CS273 semantic QA
→ existing CS281 deterministic Final Composed Visual Approval
→ independent CS281 replay
→ STOP before CS282 Final Semantic Approval
```

Presentation rejection is fail-closed and never reaches CS281. CS345 requires the same Story and the same composed PNG byte lineage throughout.

## Why the historical CS326 tool is not reused directly

The repository already contains an older CS326 orchestration path that begins from CS325 and creates a fresh CS280 receipt from external presentation evidence before invoking CS281. CS345 starts later in the current chain: CS344 has already admitted and replayed the exact CS280 evidence. Re-running external review admission would duplicate authority and enlarge the attack surface. CS345 therefore reuses only the secure lineage principle: it replays the already-admitted CS280 chain back to CS273 and then invokes the existing CS281 contract.

## Gate preservation

CS345 preserves all upstream factual/freshness, entity/identity, sentiment neutrality and loser-respect, zero-cost/local-only, semantic QA, visual-quality, Golden-quality, Human Visual Review, exact brand, typography, and presentation gates transitively.

On success it may set only Final Composed authority:

- `composed_visual_approved = true`

It must keep downstream authority closed:

- `semantic_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`
- `authoritative = false`

The repository's existing CS281 contract remains the authority that actually grants deterministic Final Composed approval. CS345 does not duplicate that decision logic.

## Exact lineage

CS345 independently replays CS344 and its exact CS280 receipt. It then follows CS280's signed/repository-bound review chain through CS279, CS278, CS277, CS276, CS275, and CS274 to the exact CS273 hybrid-surface semantic QA receipt. Each child binding must match repository-relative path, SHA-256, byte size, and receipt SHA where applicable.

The derived CS273 and admitted CS280 must match the CS344 Story and composed PNG. CS281 is then built from those exact two receipts and independently verified.

## Prohibited shortcuts

CS345 contains no Qwen inference, model loading, pixel generation, pixel mutation, generated manual review, paid fallback, network fallback, upload/publish shortcut, Final Semantic approval builder, Genuine Golden materialization builder, or publication authority.

## Regression coverage

`tests/test_phase18_qwen_final_presentation_evidence_to_final_composed_visual_approval.py` covers the approved current-chain continuation, rejection fail-closed behavior, premature semantic authority rejection, exact CS280 receipt binding, and static guards against generation/network/publication/final-semantic shortcuts.

## Genuine Golden execution blocker

The execution environment measured during CS345 remains CPU-only:

```text
torch=2.10.0+cpu
cuda_available=False
torch_version_cuda=None
cuda_device_count=0
native_cuda_bf16=False
nvidia_smi=unavailable
```

No genuine Qwen inference, genuine canonical candidate, or Genuine Golden Visual PNG is claimed. Genuine generation still requires a zero-cost compatible host containing together an NVIDIA CUDA GPU, CUDA-enabled PyTorch, native BF16 support, sufficient RAM/VRAM, the approved Qwen-Image/Diffusers runtime, and the exact approved already-local pinned model/verifier assets, without paid or network fallback.

## Next boundary

The exact next repository contract is CS282 `qwen_image_composed_candidate_final_semantic_approval.py`. It re-verifies CS281 and the transitively bound CS273 and may set only `semantic_approved = true`; SemanticPublicationGate and Genuine Golden/publication authority remain independent downstream stages. CS345 deliberately stops before CS282.
