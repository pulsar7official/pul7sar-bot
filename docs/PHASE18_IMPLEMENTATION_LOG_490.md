# Phase 18 Implementation Log — CS490

## Scope
Strengthen Candidate 1 PNG chunk-semantics evidence before workflow activation by cryptographically chaining the semantic proof to the exact structure-v3 evidence bytes from which it was derived.

## Baseline reviewed
- Branch: `phase18/story-intelligence` only.
- Baseline HEAD: `b43ccc849c0a7433f1da8ca57f3bfce44ba16447` (CS489).
- CS489 had 12 Phase 18 workflow runs; returned completed runs were successful.
- `main` was not modified.
- The Golden workflow already executes chunk-semantics verification before canonical/review packaging, but the CS489 review-bundle binder is not yet activated in that workflow.

## Added
- `docs/PHASE18_IMPLEMENTATION_LOG_490.md`

## Modified
- `tools/phase18_verify_first_genuine_golden_png_chunk_semantics.py`
  - output schema advanced from chunk-semantics v1 to v2;
  - records `upstream_structure_schema`;
  - records SHA-256 of the exact structure evidence bytes as `upstream_structure_evidence_sha256`;
  - preserves all fail-closed identity, policy, semantic and authority checks.
- `tools/phase18_bind_png_chunk_semantics_to_review_bundle.py`
  - accepts chunk-semantics v2 only;
  - requires the semantic evidence's upstream structure schema/hash to match the exact `evidence/png_structure.json` bytes already bound in the same review bundle;
  - replay independently rechecks that chain;
  - binding replay schema advanced to v2.
- `tests/test_phase18_first_golden_png_chunk_semantics.py`
  - asserts v2 schema and exact upstream structure SHA-256;
  - proves byte-level structure representation changes change the upstream hash;
  - preserves semantic and authority rejection coverage.
- `tests/test_phase18_png_chunk_semantics_review_binding.py`
  - fixtures advanced to v2;
  - adds rejection of forged upstream structure hash;
  - adds rejection of legacy v1 semantics;
  - preserves missing/drift/authority tests.

## Deleted
None.

## Security / publication invariants preserved
No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline-only, semantic-publication, exact model/runtime, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds 2–4 authority was weakened. No paid API, network model download, CPU generation, FP16 substitution, or FP32 substitution was introduced.

## Why this materially reduces the remaining gap
Before CS490, the bundle binder could cryptographically associate semantic evidence with structure evidence in the bundle manifest, but the semantic evidence itself did not identify the exact structure evidence bytes it was derived from. CS490 makes that dependency intrinsic to the semantic proof and independently replayable, matching the stronger evidence-chain pattern already used by canonical encoding evidence.

## Testing status
The changes are stdlib-only and CPU-safe. Repository CI must run on the new HEAD before this checkpoint is considered terminal-green. The chunk-semantics binder remains intentionally unactivated in the GPU Golden workflow until this v2 chain passes CI.

## Remaining path
1. Obtain terminal-green CI for CS490.
2. Activate `phase18_bind_png_chunk_semantics_to_review_bundle.py` in immutable source checks and in the exact review-bundle path after structure binding.
3. Add independent chunk-semantics binding replay before tracked-source replay and success upload.
4. Run the first real Candidate 1 only on a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real native-BF16 CUDA device, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` / offline-only policy.
5. Human Visual Review and Golden-quality approval remain manual and closed until a genuine PNG exists.

## Golden PNG status
No genuine Golden Visual PNG was fabricated or claimed. Compatible CUDA/GPU execution remains the material execution blocker.
