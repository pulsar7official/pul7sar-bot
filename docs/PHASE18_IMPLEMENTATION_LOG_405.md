# Phase 18 Implementation Log 405 — Upload Action / REST Transport Attestation

## State reviewed before this change

- Working branch: `phase18/story-intelligence` only.
- Starting branch HEAD: `cad893f2cc990ac3c08dce95ad8ef96ca9fbdfe8`.
- CS404 verification was terminal-green: Phase 18 Story Intelligence Verification run `34586484810` completed successfully on the starting SHA.
- `main` was inspected read-only at `ac74bbae24389f30dec51fca37ad4e09f2eba397`; no write, merge, rebase, reset, or ref update was performed on `main`.

## Gap closed

CS404 can verify a supplied GitHub artifact metadata object against the run-bound readiness manifest, exact source commit, artifact digest, branch, and fail-closed authority contract. The remaining transport gap was that the immutable outputs emitted by `actions/upload-artifact` (`artifact-id` and `artifact-digest`) were not yet bound to the separately fetched GitHub REST artifact metadata in a persisted attestation.

Without this binding, a caller could verify a valid metadata object without producing a durable receipt proving that the metadata describes the same artifact instance emitted by the upload action.

## Added

### `tools/phase18_attest_first_genuine_golden_v6_uploaded_artifact.py`

A CPU-safe, network-free transport attestation helper that:

- consumes already-fetched GitHub artifact metadata;
- consumes the run-bound readiness manifest;
- consumes immutable `actions/upload-artifact` outputs;
- delegates the underlying REST metadata/readiness verification to the CS404 verifier;
- requires exact artifact-ID equality between the upload action output and REST metadata;
- requires exact SHA-256 digest equality between the upload action output and REST metadata;
- binds workflow run ID, run attempt, source commit SHA, branch, Candidate 1, artifact identity, artifact size, and `$0-local` policy into one attestation;
- writes the attestation atomically;
- grants only eligibility for Human Visual Review while keeping Human Review approval, Golden Quality approval, publication, and Seeds 2–4 authorization closed.

Attestation schema:

`pul7sar-first-genuine-golden-v6-upload-transport-attestation-v1`

Verified status:

`FIRST_GENUINE_GOLDEN_V6_UPLOAD_TRANSPORT_ATTESTED`

### `tests/test_phase18_attest_first_genuine_golden_v6_uploaded_artifact.py`

Regression coverage includes:

- valid upload-action/REST metadata binding;
- artifact-ID mismatch rejection;
- artifact-digest mismatch rejection;
- rejection of noncanonical artifact IDs;
- atomic-write behavior with no leftover temporary file;
- continued fail-closed downstream authority.

## Modified

None of the pre-existing generation, prompt, model, identity, factual, sentiment, semantic-publication, or visual-quality implementation was modified in CS405.

## Deleted

Nothing.

## Test status

The new helper/test contract received an isolated local unit smoke run before repository commit and all five focused tests passed. Repository CI is authoritative and must still become green on the committed CS405 HEAD before this change is described as terminal-green.

## Gate preservation

CS405 does not alter or weaken:

- factual verification/freshness gates;
- entity/identity verification;
- sentiment and loser-respect policy;
- `$0-local` / offline model-resolution policy;
- semantic-publication gating;
- generated-layer checks;
- visual-quality gating;
- Human Visual Review approval;
- Golden Quality approval;
- publication authority;
- Seeds 2–4 authorization.

The attestation explicitly keeps the last four authorities `false`.

## Remaining integration gap

The Golden v6 workflow still needs a post-upload integration step that:

1. captures `actions/upload-artifact` output `artifact-id` and `artifact-digest`;
2. fetches the artifact metadata for that exact artifact ID using read-only GitHub Actions metadata access;
3. invokes this CS405 helper against the run-bound readiness manifest;
4. persists the resulting transport attestation as a separate audit artifact or otherwise preserves it without mutating the already-uploaded Golden evidence archive.

That integration must remain fail-closed and must not turn transport verification into Human Review approval or publication authority.

## Genuine Golden PNG blocker

No Genuine Golden PNG was created in CS405. The non-substitutable execution blocker remains an eligible self-hosted NVIDIA runner with CUDA-enabled PyTorch and native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally so the run remains `$0-local` and offline. No PNG result should be fabricated in the absence of that execution environment.
