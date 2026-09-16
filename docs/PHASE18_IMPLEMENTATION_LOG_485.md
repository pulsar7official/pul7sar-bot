# Phase 18 Implementation Log — CS485

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline: CS484 at `edcd5ba136b3f6c6129e0f03a7a6617b412c5010`. Its 12 Phase 18 workflow runs were completed successfully before this change set.

## Integration blocker found and fixed
Final evidence-graph review found a real stale-schema edge in the live Golden path: `phase18_verify_first_genuine_golden_png_structure.py` emits structure schema v3, while `phase18_bind_png_structure_to_review_bundle.py` still accepted only structure schema v2. A genuine Candidate 1 could therefore pass structural/canonical verification and then fail when its structure evidence was bound into the Human Review bundle.

CS485 aligns the review-bundle binder with v3 and makes the binder independently require the canonical RGB8 proof already guaranteed by the critical-path structure verifier. This removes the stale v2 acceptance path rather than adding a compatibility downgrade.

## Modified
- `tools/phase18_bind_png_structure_to_review_bundle.py`
  - pins structure evidence to v3;
  - requires `canonical_encoding_verified=true`;
  - independently requires RGB8 truecolour: bit depth 8, color type 2, 3 channels, 24 bits/pixel, non-interlaced;
  - requires the exact canonical contract `RGB8_TRUECOLOUR_NON_INTERLACED`;
  - keeps branch/Candidate 1/source SHA/PNG SHA/$0-local/offline-only and closed-authority checks;
  - promotes binding result schema to v2 and reports canonical proof.
- `tests/test_phase18_png_structure_review_binding.py`
  - fixture now models structure-v3 evidence;
  - covers successful v3 bind/replay;
  - rejects stale v2 evidence;
  - rejects missing canonical proof;
  - rejects RGBA drift;
  - preserves authority and post-bind byte-drift rejection.

## Added
- `docs/PHASE18_IMPLEMENTATION_LOG_485.md`

## Deleted
None.

## Gates preserved
No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/network isolation, SemanticPublicationGate, exact model/runtime provenance, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds 2–4 gate was weakened. No paid API, model download, CPU generation fallback, FP16 fallback, or FP32 fallback was introduced.

## Testing state
CS484 was green before this work. CS485 changes are stdlib-only and CPU-safe and have been committed for the normal Phase 18 CI. CS485 must not be called terminal-green until Actions completes on the final SHA.

## Golden PNG state / blocker
No First Genuine Golden Visual PNG was generated or claimed. Actual generation remains blocked until a compatible self-hosted NVIDIA runner is available with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only execution.

## Remaining gap
After CS485 CI is green, the known stale structure-schema edge in the final review evidence graph is closed. Further preparatory changes should be limited to concrete defects found by CI/evidence-graph inspection; otherwise the material remaining step is compatible GPU execution of Candidate 1 followed by manual Human Visual Review and Golden-quality approval.
