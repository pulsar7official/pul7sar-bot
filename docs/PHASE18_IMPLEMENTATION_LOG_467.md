# Phase 18 Implementation Log — CS467

## Scope

CS467 adds an exact, fail-closed replay of the First Genuine Golden v6 Candidate 1 Human Review bundle after packaging and immediately before artifact upload. It does not alter `main`, factual/identity/sentiment gates, SemanticPublicationGate behavior, Candidate 1 generation settings, model revisions, zero-cost/offline policy, Human Review authority, Golden approval authority, publication authority, or Seeds 2–4 authority.

## Why this change

CS466 cryptographically packaged only the exact Candidate 1 PNG and its bound evidence into a run-scoped review bundle. A remaining boundary existed between bundle creation and artifact upload: the workflow did not independently replay the completed directory as a closed set. A file added, removed, renamed, or modified after packaging could therefore bypass a second explicit validation step before upload.

CS467 closes that boundary without granting any new authority.

## Added

- `tools/phase18_verify_first_genuine_golden_v6_review_bundle.py`
  - CPU-safe, zero-cost, offline-only replay verifier.
  - Requires the CS466 review-bundle schema and Candidate 1 identity.
  - Requires `phase18/story-intelligence`, `$0-local`, and offline-only policy.
  - Requires Human Review eligibility while keeping Human Review approval, Golden approval, publication, network download, generation authority, authoritative gate, and Seeds 2–4 authority false.
  - Verifies every declared bundle entry by SHA-256 and byte count.
  - Rejects unsafe paths, duplicate paths, missing files, undeclared files, and manifest self-declaration.
  - Requires the exact `candidate-1.png`, verifies its SHA-256 against the bundle manifest, and verifies the PNG signature.
  - Emits a replay receipt containing the bundle-manifest SHA-256 and confirmation that the bundle is an exact closed file set.

- `tests/test_phase18_first_golden_review_bundle_replay.py`
  - Covers successful exact closed-set replay.
  - Covers rejection of undeclared files.
  - Covers rejection of declared-file byte drift.
  - Covers rejection of authority drift.

## Modified

- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - Adds the new verifier to immutable checkout proof.
  - Adds `Replay exact Golden v6 review bundle before upload` after packaging and before success upload.
  - Persists the replay receipt under failure-diagnostic evidence, not inside the immutable review bundle itself.
  - Success upload remains restricted to the run-scoped exact review bundle.

- `tests/test_phase18_first_golden_fresh_workflow.py`
  - Requires package -> bundle replay -> success upload ordering.
  - Requires the replay verifier and replay receipt path.

## Deleted

None.

## Tests

The new unit/regression coverage is committed. The connected execution environment used for this change could not clone `github.com` because DNS resolution failed, so no local test result is claimed. GitHub Actions on the exact CS467 branch HEAD is the authoritative CI result to inspect after the commits are accepted.

## Security and authority invariants preserved

- Branch: `phase18/story-intelligence` only.
- `main` is not modified.
- Cost mode remains `$0-local`.
- Hugging Face/model resolution remains offline-only.
- Native CUDA BF16 remains mandatory for genuine generation.
- Approved Qwen2.5-VL and FLUX.2 snapshot gates remain mandatory.
- Factual, entity/identity, sentiment/loser-respect, semantic-publication, and visual-quality gates remain unchanged.
- Human Visual Review is still required and not auto-approved.
- Golden quality is not auto-approved.
- Publication is not authorized.
- Seeds 2–4 remain unauthorized.

## Remaining blocker

CS467 does not create a Golden PNG and does not simulate GPU output. The First Genuine Golden Visual remains blocked until a compatible self-hosted NVIDIA runner is available with CUDA-enabled PyTorch, a real CUDA device, native BF16 support, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the zero-cost/offline-only contract.

When that environment is available, the authoritative path now reaches an exact review bundle and independently replays the completed bundle as a closed cryptographic file set before upload.
