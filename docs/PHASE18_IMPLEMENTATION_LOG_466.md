# Phase 18 Implementation Log — CS466

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

CS466 adds an exact, cryptographically replayed Human Visual Review bundle boundary after CS465 snapshot replay. It does not generate images, load models, access the network, approve Human Review, approve Golden quality, publish content, or authorize Seeds 2–4.

## Problem closed

The freshness-bound GPU workflow previously uploaded broad `output/**` areas after the Candidate 1 evidence chain. On a self-hosted runner, broad artifact collection is a weaker review handoff boundary than the cryptographically verified evidence chain itself because unrelated or stale files could be included in the uploaded artifact even though they were not part of the accepted Candidate 1 manifest.

CS466 makes the success artifact an exact review-only bundle assembled from the already verified PNG and evidence references. Failure diagnostics remain separate and cannot be mistaken for a review-eligible Golden bundle.

## Added

### `tools/phase18_package_first_genuine_golden_v6_review_bundle.py`

CPU-safe, zero-cost, offline-only packager that:

- requires the CS463 fresh/source-bound manifest v3 and the CS465 snapshot-bound manifest v1;
- requires `phase18/story-intelligence`, Candidate 1, `$0-local`, and offline-only policy;
- requires Human Visual Review eligibility while keeping Human Review approval, Golden approval, publication, generation authority, network download authority, and Seeds 2–4 authority closed;
- proves the snapshot-bound manifest points to the exact fresh/source-bound manifest by SHA-256;
- proves source commit SHA and PNG SHA-256 agree across both manifests;
- replays every evidence reference in the fresh/source-bound manifest against current bytes inside the repository;
- replays the approved snapshot inventory reference;
- validates PNG signature, SHA-256, and byte count again at packaging time;
- refuses any evidence path or target outside the repository;
- refuses an existing run-scoped bundle directory, preventing stale evidence mixing;
- copies only the exact verified PNG and exact referenced evidence to a temporary run-scoped directory;
- writes stable bundle-relative paths in `review-bundle-manifest.json`;
- atomically renames the temporary directory into the final review bundle.

### `tests/test_phase18_first_golden_review_bundle.py`

Adds regression coverage for:

- successful exact-evidence packaging;
- PNG byte drift after upstream manifests;
- stale/existing bundle target rejection;
- authority drift rejection.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

The authoritative manual GPU path now:

1. verifies the exact CS466 packager exists in the immutable checkout;
2. runs the existing execution, snapshot, runner, BF16, freshness, source, PNG, and post-generation snapshot gates unchanged;
3. packages a run/attempt-scoped exact review bundle only after snapshot replay succeeds;
4. uploads only `output/phase18_golden_review/<run-id>-<attempt>/**` on success with `if-no-files-found: error`;
5. uploads only `output/phase18_gpu_smoke/**` as short-lived diagnostics on failure;
6. no longer uploads broad generated/handoff/output directories as the success artifact.

### `tests/test_phase18_first_golden_fresh_workflow.py`

Extends workflow contract tests to require:

- snapshot replay before review-bundle packaging;
- review-bundle packaging before success upload;
- run/attempt-scoped bundle destination;
- `if: success()` and `if-no-files-found: error` on the Golden review artifact;
- separate `if: failure()` diagnostics;
- absence of the former broad `output/phase18_generated/**` and `output/phase18_handoffs/golden-batch/**` success upload paths.

## Deleted

No files deleted.

## Test / verification status

A direct local clone/test attempt was not possible in the execution environment because DNS resolution for `github.com` failed before repository checkout; this is an environment/network limitation, not a code-test result. GitHub Actions therefore remains the authoritative executable verification for CS466.

The changes are designed to be covered by the existing Phase 18 PR CI plus the two targeted test modules above. CS466 must not be described as terminal-green until those runs complete successfully on the exact final HEAD.

## Preserved gates

CS466 does not alter factual verification, entity/identity verification, sentiment/loser-respect rules, `SemanticPublicationGate`, Human Visual Review authority, Golden-quality approval, Candidate 1 prompt/seed/dimensions/steps/guidance, approved Qwen2.5-VL or FLUX.2 identities/revisions, native-BF16 requirements, `$0-local`, offline-only execution, or publication/Seeds 2–4 authority.

## Remaining blocker

No First Genuine Golden Visual PNG is fabricated or claimed by CS466. A real Candidate 1 still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient GPU/host/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the zero-cost/offline-only contract.

When that environment is available, the successful artifact will now be an exact, cryptographically bound Human Visual Review bundle rather than a broad runner output collection.
