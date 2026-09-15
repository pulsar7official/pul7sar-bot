# Phase 18 Implementation Log — CS484

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline: CS483 at `658f9eac1a28dc232c8982b7535126aa52f8597a`. The baseline had 12 Phase 18 workflow runs and no failed runs returned for that exact SHA before this change set.

## Gap closed

CS483 activated canonical RGB8 evidence in the real Golden workflow, but the canonical evidence copied semantic identity fields from the upstream PNG-structure report without cryptographically identifying the exact structure-report bytes from which it was derived. The review bundle independently contained both files, but their relationship was therefore semantic rather than byte-bound.

CS484 makes that relationship explicit and fail-closed. Canonical verification now records the SHA-256 of the exact upstream structure evidence bytes. Review-bundle binding requires that hash to equal the manifest SHA-256 of `evidence/png_structure.json`, verifies the structure entry bytes before canonical binding, records the upstream structure hash in the bundle manifest, and replays the chain before upload.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_484.md`

## Modified

- `tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py`
  - canonical evidence schema promoted to v2;
  - hashes exact upstream PNG-structure evidence bytes;
  - emits `upstream_structure_schema` and `upstream_structure_evidence_sha256`;
  - preserves RGB8/non-interlaced, identity, zero-cost/offline, and closed-authority checks.
- `tools/phase18_bind_png_canonical_encoding_to_review_bundle.py`
  - canonical schema pinned to v2;
  - requires the already-bound `evidence_png_structure` manifest entry;
  - verifies its path, SHA-256, byte count, file bytes, and structure schema;
  - requires canonical evidence's upstream hash to equal that exact structure evidence SHA-256;
  - records `png_canonical_upstream_structure_evidence_sha256` in the review manifest;
  - independently replays the cross-evidence hash chain before upload.
- `tests/test_phase18_first_golden_png_canonical_encoding.py`
  - verifies exact upstream structure byte hashing;
  - verifies a structure-byte change changes the canonical upstream hash;
  - preserves stale-schema, RGB8, interlace, structural-proof, authority and platform-normalizer coverage.
- `tests/test_phase18_png_canonical_encoding_review_binding.py`
  - fixture now contains real structure evidence and manifest metadata;
  - covers successful cross-evidence binding;
  - rejects canonical upstream-hash drift;
  - rejects structure-evidence byte drift during replay;
  - preserves encoding, authority and canonical-evidence byte-drift coverage.

## Deleted

None.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/network isolation, SemanticPublicationGate, exact model/runtime provenance, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds 2–4 gate was weakened. No paid API, network model download, CPU generation fallback, FP16 fallback, or FP32 fallback was introduced.

## Testing state

The CS483 baseline was green at review time. CS484 uses stdlib-only CPU-safe code/tests and is committed for normal Phase 18 CI. Do not call CS484 terminal-green until GitHub Actions completes on its final SHA.

## Golden PNG state / blocker

No First Genuine Golden Visual PNG was generated or claimed. Actual generation still requires the compatible self-hosted NVIDIA runner: CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only execution.

## Remaining gap

After CS484 CI is green, the next safe work is to inspect the final review-bundle evidence graph for any remaining semantic-only edge and, if none remains, keep preparatory changes minimal until a compatible GPU runner can execute Candidate 1. The Human Visual Review and Golden-quality decisions remain deliberately manual and closed.
