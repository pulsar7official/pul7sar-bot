# Phase 18 Implementation Log — CS481

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline reviewed: CS480 `0990f322effc2910ea3046d183c6ea3475c0e198`.

## Baseline verification
CS480 completed both Phase 18 Story Intelligence Verification and Phase 18 CPU Verification Diagnostics successfully before this change set was started.

## Goal
Reduce the remaining gap to the first genuine Golden Visual PNG without requiring unavailable GPU execution by making the already-critical PNG structural gate enforce the canonical final image encoding directly.

CS479 introduced a standalone canonical-encoding verifier and CS480 prepared review-bundle binding. Those components remain intact. CS481 adds defense in depth at the earliest existing post-generation PNG gate, so a structurally valid but non-canonical PNG cannot advance to snapshot/runtime replay or review packaging.

## Added
- `docs/PHASE18_IMPLEMENTATION_LOG_481.md`

## Modified
- `tools/phase18_verify_first_genuine_golden_png_structure.py`
  - output schema advanced to v3;
  - requires canonical RGB8 truecolour encoding in the critical path;
  - requires bit depth 8, PNG color type 2, 3 channels, 24 bits/pixel, non-interlaced output;
  - emits `canonical_encoding_verified=true` and canonical encoding identity only after the contract is proven;
  - preserves complete CRC, zlib, scanline, filter-byte, IEND, no-trailing-bytes, source/PNG identity, `$0-local`, offline-only, and closed-authority checks.
- `tests/test_phase18_first_golden_png_structure.py`
  - keeps the prior structural and authority regressions;
  - verifies canonical RGB8 evidence on the valid fixture;
  - adds fail-closed rejection for RGBA8;
  - adds fail-closed rejection for RGB16;
  - remains stdlib/unittest-only and CPU-safe.

## Deleted
None.

## Gate preservation
No factual/source-consensus, identity/entity, sentiment/loser-respect, semantic-publication, zero-cost/network-isolation, model/runtime provenance, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds 2–4 gate was weakened.

No paid API, model download, network fallback, CPU generation fallback, FP16 fallback, or FP32 fallback was introduced.

Authority remains closed: `authoritative_gate=false`, `network_download_authorized=false`, `generation_authorized=false`, `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`, `seeds_2_to_4_authorized=false`.

## Testing
Before CS481, CS480 Story Intelligence Verification and CPU Verification Diagnostics were confirmed successful on GitHub Actions.

CS481 adds CPU-safe unittest coverage for canonical encoding directly in the existing critical PNG gate. GitHub Actions results for the final CS481 HEAD must be treated as authoritative once they complete; no GPU success is claimed by this log.

## GPU status / exact blocker
No genuine Golden Visual PNG was generated in CS481. The remaining execution blocker is unchanged: a compatible self-hosted NVIDIA runner must provide CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only execution.

No result is fabricated in the absence of that environment.

## Remaining gap
After CS481 passes CPU CI, the prepared standalone canonical evidence/binder path from CS479/CS480 can be activated or consolidated with the now-canonical structural evidence in the exact Human Review bundle. The actual Candidate 1 generation still requires the compatible offline NVIDIA/CUDA runner.
