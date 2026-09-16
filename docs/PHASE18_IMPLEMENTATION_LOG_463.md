# Phase 18 Implementation Log — CS463

## Scope

Branch-only change on `phase18/story-intelligence`. `main` was not modified.

## Goal

Bind the concrete self-hosted runner and CUDA device identity into the First Genuine Golden v6 evidence chain before Candidate 1 generation and into the final content-addressed manifest afterward. This closes the remaining provenance gap between an execution-readiness result and the actual GitHub Actions runner/device that executed the attempt.

This change does not generate pixels and does not weaken factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality/Human Review gates.

## Added

### `tools/phase18_capture_first_golden_runner_identity.py`

Added a local-only fail-closed runner identity capture. It records only non-secret execution facts:

- repository and exact Phase 18 branch;
- source commit SHA;
- GitHub workflow run ID and run attempt;
- runner OS and architecture;
- a SHA-256 digest of the runner name rather than the raw runner name;
- PyTorch version and CUDA runtime;
- CUDA device count and native BF16 support;
- per-device compute capability, total memory, multiprocessor count, and a SHA-256 digest of the GPU model name;
- `$0-local` and offline-only policy state.

The capture fails closed if repository/branch/source identity is invalid, the runner is not Linux/X64, run identity is missing, `$0-local` or offline-only policy drifts, CUDA is unavailable, or native BF16 is unavailable. All generation/publication authorities remain false.

### `docs/PHASE18_IMPLEMENTATION_LOG_463.md`

This implementation log.

## Modified

### `tools/phase18_verify_first_genuine_golden_v6_fresh_source_bound.py`

Upgraded the final manifest to `pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3` and made runner identity mandatory evidence.

The verifier now requires the runner evidence to match:

- repository `pulsar7official/pul7sar-bot`;
- branch `phase18/story-intelligence`;
- the exact expected source commit SHA;
- the same workflow run ID and run attempt;
- Linux/X64 runner platform;
- CUDA availability, CUDA runtime, at least one device, and native BF16;
- at least one structurally valid device identity with compute capability and positive device memory;
- `$0-local` and offline-only policy;
- all authority fields still closed.

On success the final manifest records `runner_identity_verified=true` and includes the SHA-256 of the exact runner identity evidence file alongside the execution probe, freshness, source, resource-lock, and PNG digests.

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

Added runner identity capture after the execution blocker probe and before Candidate 1 generation. The final binding step now passes the exact runner identity file through `--runner-identity` before evidence upload.

### `tests/test_phase18_first_golden_fresh_source_bound_manifest.py`

Updated fixture construction for runner identity evidence and added regression coverage for:

- valid runner identity becoming content-addressed final evidence;
- source commit/run identity drift rejection;
- CUDA/native-BF16 runner drift rejection;
- workflow ordering proving runner identity is captured before Candidate 1 and bound before artifact upload;
- preservation of execution-blocker, stale-evidence, PNG-byte-drift, publication, and Seeds 2–4 protections.

## Deleted

None.

## Gate preservation

Unchanged:

- factual verification;
- entity/identity verification;
- neutral and respectful sentiment treatment;
- `$0-local` execution requirement;
- offline-only model resolution;
- native CUDA/BF16 requirement with no FP16/FP32 substitution;
- exact approved Qwen2.5-VL and FLUX.2 model identities/revisions;
- SemanticPublicationGate and semantic preflight semantics;
- Candidate 1 prompt, seed, dimensions, steps, and guidance;
- Human Visual Review requirement;
- Golden quality approval remains false before Human Review;
- publication remains false;
- Seeds 2–4 remain unauthorized.

## Execution status

No Genuine Golden PNG was fabricated or claimed. Actual Candidate 1 generation remains blocked until an available compatible self-hosted NVIDIA runner exists with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible semantic/generation runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under offline-only `$0-local` execution.
