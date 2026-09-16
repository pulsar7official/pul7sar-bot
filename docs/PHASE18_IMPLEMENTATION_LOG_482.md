# Phase 18 Implementation Log — CS482

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline reviewed before change: CS481 at `61885647f195ef2da9450b6c84483e29309b0286`.

## Baseline verification

The CS481 branch state was reviewed before writes. Its Phase 18 Story Intelligence Verification and Phase 18 CPU Verification Diagnostics workflow runs completed successfully. The critical Golden workflow still requires the self-hosted `linux/x64/gpu/cuda/bf16/pul7sar-phase18` runner and keeps `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` fail-closed constraints.

## Gap found

CS481 promoted `tools/phase18_verify_first_genuine_golden_png_structure.py` output from structural schema v2 to v3 while moving canonical RGB8 enforcement into that critical gate. The separate canonical encoding verifier prepared in CS479 was still pinned to structural schema v2. Activating it unchanged would therefore reject every legitimate CS481 structural report before Human Review packaging.

This was a real integration blocker for the planned canonical-evidence review-bundle activation and had to be repaired before putting that verifier/binder into the GPU workflow.

## Changes

### Modified `tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py`

- Pinned upstream structural evidence to `pul7sar-phase18-first-genuine-golden-png-structure-v3`.
- Added fail-closed requirement for CS481 `canonical_encoding_verified=true`.
- Added fail-closed requirement for exact contract label `RGB8_TRUECOLOUR_NON_INTERLACED`.
- Preserved exact RGB8 requirements: bit depth 8, truecolour type 2, 3 channels, 24 bits/pixel, non-interlaced.
- Preserved source SHA, PNG SHA, branch, Candidate 1, `$0-local`, offline-only and all closed authority checks.

### Modified `tests/test_phase18_first_golden_png_canonical_encoding.py`

- Updated the canonical fixture to structural schema v3.
- Added the CS481 canonical proof fields.
- Added explicit rejection of stale structural schema v2.
- Added explicit rejection when `canonical_encoding_verified` is absent/false.
- Added explicit rejection when the canonical contract label drifts.
- Preserved RGBA, RGB16, interlace, incomplete structural proof, authority drift and platform normalizer contract coverage.
- Remains stdlib `unittest` only and CPU-safe.

### Added this implementation log

`docs/PHASE18_IMPLEMENTATION_LOG_482.md`

## Deleted

None.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, SemanticPublicationGate, zero-cost/network isolation, source provenance, exact-model/runtime, CUDA/native-BF16, Human Visual Review, Golden-quality, publication or Seeds 2–4 authority was weakened or opened.

No paid API, model download, network generation path, CPU generation fallback, FP16 fallback or FP32 fallback was introduced.

## Testing status

CS481 baseline CI was green before this change. CS482 changes are intentionally CPU-safe and covered by `unittest`. GitHub Actions on the new CS482 HEAD must complete before CS482 can be called terminal-green.

## First Genuine Golden PNG status

No Golden PNG was fabricated or claimed. The remaining execution blocker is still the absence, in the available execution environment, of a compatible self-hosted NVIDIA runner satisfying all of: CUDA-enabled PyTorch, a real CUDA device, native BF16, required VRAM/RAM/cache/filesystem headroom, approved runtime, and the exact approved Qwen2.5-VL and FLUX.2 local snapshots under `$0-local`/offline-only execution.

## Next safe step

After CS482 is green, activate the now-v3-compatible canonical verifier in the Golden workflow immediately after structural verification, then bind `evidence/png_canonical_encoding.json` into the exact Human Review bundle and replay that binding before tracked-source replay/upload. This closes the prepared CS479/CS480 canonical-evidence chain without weakening any existing gate.
