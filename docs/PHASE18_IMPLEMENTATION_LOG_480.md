# Phase 18 Implementation Log — CS480

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

## Baseline reviewed
CS479 HEAD: `031cbd81e1a98b50b8d5bfe282ad3831abd1de9a`.

## Goal
Reduce the remaining gap between the CPU-verified canonical RGB8 PNG contract and the eventual exact Human Review artifact without weakening factual, identity, sentiment, zero-cost, semantic-publication, CUDA/BF16, provenance, or visual-quality gates.

## Added
- `tools/phase18_bind_png_canonical_encoding_to_review_bundle.py`
  - stdlib-only, CPU-safe, offline and fail-closed;
  - accepts only the CS479 canonical encoding evidence schema;
  - requires Candidate 1, `phase18/story-intelligence`, `$0-local`, offline-only, exact source SHA and PNG SHA identity;
  - requires RGB8 truecolour (`bit_depth=8`, `color_type=2`, `channels=3`, `bits_per_pixel=24`, `interlace_method=0`);
  - requires canonical encoding verification and Human Review eligibility while all authority fields remain false;
  - copies the exact evidence bytes to `evidence/png_canonical_encoding.json` in a review bundle;
  - records SHA-256 and byte size in the bundle manifest;
  - provides an independent replay path that rejects byte drift, identity drift, policy drift, encoding drift, or authority drift.
- `tests/test_phase18_png_canonical_encoding_review_binding.py`
  - successful bind/replay;
  - RGBA/non-RGB8 rejection;
  - publication-authority drift rejection;
  - post-bind byte-drift rejection.
- this implementation log.

## Modified
None.

## Deleted
None.

## Tests / validation
The new tests are stdlib `unittest` and require no GPU or network. GitHub CI is the authoritative execution path for this branch. The current runtime available to this work does not provide a compatible NVIDIA/CUDA generation environment, so no Golden PNG was generated or claimed.

## Gate preservation
No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline-only, `SemanticPublicationGate`, Human Visual Review, Golden-quality, source-provenance, exact model snapshot, CUDA/native-BF16, publication, or Seeds 2–4 authority gate was weakened. No paid API, network download path, or CPU/FP16/FP32 generation fallback was added.

## Deliberate non-activation
The binder is preparatory in CS480 and is not yet inserted into the critical GPU workflow. This follows the same fail-closed rollout discipline used for earlier evidence binders: first land and validate the binder independently in CPU CI, then activate the canonical verifier + binder + replay as an ordered workflow chain after green validation.

## Remaining path
After CS480 is green, activate:
1. canonical RGB8 verifier immediately after full PNG structural verification;
2. canonical evidence binding after review-bundle packaging (and after existing evidence bindings as appropriate);
3. independent canonical evidence replay before tracked-source replay/upload;
4. immutable checkout proof for both canonical verifier and binder.

The first genuine Golden Visual PNG remains blocked on an eligible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real compatible CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only execution.
