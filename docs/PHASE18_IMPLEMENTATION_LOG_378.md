# Phase 18 Implementation Log 378 — CS348 Semantic Publication Gate Snapshot Lineage

## Branch safety

Target branch: `phase18/story-intelligence` only.
Starting branch HEAD: `318d5391c135474ba3172fc05720225b184914cd`.
`main` was not modified, merged, rebased, reset, force-updated, or otherwise written.

## What changed

### Modified

1. `engine/intelligence/qwen_image_semantic_publication_request_to_gate_execution.py`
   - Raised CS348 schema from v1 to v2.
   - Added strict five-field Qwen generator snapshot-lineage validation.
   - Requires verified snapshot lineage from freshly verified CS347 before CS284 execution.
   - Copies the exact five-field lineage into the CS348 receipt.
   - Replays CS347 during CS348 verification and compares snapshot lineage field-by-field.
   - Preserves CS284 SemanticPublicationGate allow/deny authority exactly and independently from generator identity.

2. `tests/test_phase18_qwen_semantic_publication_request_to_gate_execution.py`
   - Updated CS347 fixture with the five generator snapshot-lineage fields.
   - Added successful propagation assertions.
   - Added fail-before-CS284 regression for unverified snapshot inventory.
   - Added rehashed snapshot-inventory digest tamper regression.
   - Added rehashed model-revision tamper regression.
   - Preserved gate allow/deny behavior, request-only enforcement, CS283 binding protection, and forbidden shortcut checks.

3. `docs/PHASE18_IMPLEMENTATION_LOG_377.md`
   - Recorded the completed successful CS377 GitHub Actions result on exact code-and-test SHA `0bce98bcd0f3d0d34d2dd13ac5e2906bfaf78c22`.

### Added

- `docs/PHASE18_CHANGESET_378_CS348_SEMANTIC_PUBLICATION_GATE_SNAPSHOT_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_378.md`

### Deleted

None.

### Dependencies

None added or changed.

## Commits

Production hardening commit: `35a02d9f43671119e55708bfc97f868f531e0843`.
Exact code-and-test-bearing commit: `3ea81b0e673a6ee5813310988747de43cdc8bcf2`.
CS377 terminal-green documentation commit: `5d8b64f03b0fae2b150f78931c7a10346d75e5f0`.
CS378 changeset documentation commit: `397b0a2dfd0857b831f520e8c48e6b1df65e349a`.

## Gate preservation

CS348 executes the existing CS284 SemanticPublicationGate; it does not replace it or permit an external allowed override. All upstream factual/freshness, Entity/Identity, sentiment neutrality / loser-respect, zero-cost, semantic QA, visual-quality, Human Visual Review, Final Presentation / Brand / Typography, Final Composed, and Final Semantic gates remain upstream prerequisites through the verified chain.

CS348 still requires:

- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

Even `semantic_publication_allowed=true` is only a gate result and is not Genuine-Golden materialization or publication readiness.

## Tests / CI

The targeted regressions are committed at `3ea81b0e673a6ee5813310988747de43cdc8bcf2`.

`Phase 18 Story Intelligence Verification` run `34391189414` / #5274 completed successfully on that exact SHA. The visible companion Phase 18 workflows on the same SHA also completed successfully. CS378 is therefore terminal-green.

## Genuine Golden blocker

No Genuine Qwen-Image PNG was generated or fabricated in this changeset. Current execution capability remains CPU-only in the available runtime (`torch 2.10.0+cpu`, CUDA unavailable, no CUDA runtime, zero CUDA devices, no native CUDA BF16, and `nvidia-smi` unavailable). Genuine inference still requires a compatible zero-cost NVIDIA CUDA host, CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM under real inference load, and the approved already-local pinned assets/runtime.

## Next boundary

CS378 is terminal-green. The existing `qwen_image_semantic_publication_gate_to_genuine_golden_materialization.py` contract is the next real downstream boundary; CS379 hardens that exact contract rather than introducing a parallel materialization gate.
