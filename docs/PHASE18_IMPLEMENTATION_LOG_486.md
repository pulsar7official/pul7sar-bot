# Phase 18 Implementation Log — CS486

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline: CS485 `1029835a1002d1debd44ab1b284f4a1f4bdeb330`.

## Review finding
CS485 is CI-green on the reviewed Phase 18 workflow runs. The existing structural PNG verifier proves framing, CRC, IHDR, exact zlib termination, scanline geometry/filter bytes, terminal IEND, no trailing bytes, and canonical RGB8 encoding. A remaining PNG semantic gap was identified: it does not yet fail closed on unknown critical chunks, the PNG reserved-bit rule, non-consecutive IDAT chunks, or PLTE ordering/duplication.

These are decoder-semantics constraints rather than cosmetic metadata. Leaving them unchecked would allow a byte-valid/canonical-RGB8 file whose chunk semantics are outside the intended deterministic Golden contract.

## Added
- `tools/phase18_verify_first_genuine_golden_png_chunk_semantics.py`
  - stdlib-only, CPU-safe, offline-only verifier;
  - rebinds exact Candidate 1 bytes to structure-v3 SHA/size evidence;
  - rejects unknown critical chunks;
  - rejects reserved-bit violations;
  - rejects non-consecutive IDAT chunks;
  - rejects PLTE after IDAT or duplicate PLTE;
  - preserves all Human Review, Golden, publication and Seeds 2–4 authorities closed.
- `tests/test_phase18_first_golden_png_chunk_semantics.py`
  - valid consecutive-IDAT case;
  - unknown-critical rejection;
  - reserved-bit rejection;
  - split-IDAT rejection when an ancillary chunk intervenes;
  - PLTE-after-IDAT rejection;
  - publication-authority drift rejection.
- this implementation log.

## Modified
None.

## Deleted
None.

## Rollout decision
The new verifier is deliberately not inserted into the GPU Golden workflow in CS486. It must first pass the repository's CPU/Story Intelligence CI as an isolated fail-closed gate. Once green, the next safe step is to place it after structure-v3 verification and before canonical/review packaging, then bind/replay its evidence in the exact Human Review bundle.

## Preserved gates
No factual/source-consensus, identity/entity, sentiment/loser-respect, `$0-local`, offline/network, SemanticPublicationGate, approved-model provenance, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds authority was weakened. No paid API, model download, CPU generation, FP16, or FP32 fallback was added.

## Golden PNG status / blocker
No Genuine Golden PNG was generated or claimed. Actual generation remains blocked outside a compatible self-hosted NVIDIA execution environment providing CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient live VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` / offline-only execution.
