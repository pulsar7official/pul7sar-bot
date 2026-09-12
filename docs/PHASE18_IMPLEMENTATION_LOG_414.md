# Phase 18 Implementation Log 414 — Local-Only Model Receipt Verification Seam

## Scope

This checkpoint advances the first genuine Golden Editorial v6 path without generating or fabricating a PNG. It adds a reusable CPU-safe, network-free verification seam for the already-emitted Qwen2.5-VL and FLUX.2 local-cache receipts so the remaining Golden replay hardening can fail closed on explicit zero-network evidence.

Branch scope remains `phase18/story-intelligence` only. `main` was inspected read-only and was not modified, merged, rebased, reset, or otherwise mutated.

## Starting state

- Starting Phase 18 HEAD: `63b4fed273c29dc0b3b021465c7085e3319f1e6c`.
- CS413 Story Intelligence Verification run `34668879788` completed successfully on that source.
- Read-only `main` observation during this checkpoint: `b14f9f2e75e8ab3c0d1c8466e646d6e6e955fc3d`.
- First Genuine Golden v6 still requires a compatible self-hosted NVIDIA/CUDA/BF16 host and the exact approved Qwen2.5-VL and FLUX.2 snapshots to exist beforehand in canonical Hugging Face cache locations.

## Gap addressed

The Qwen and FLUX cache-proof tools already emit all of the following:

- exact immutable approved model identity and revision;
- `cost_mode = "$0-local"`;
- `downloaded_now = false`;
- `network_download_authorized = false`;
- `local_files_only = true`;
- canonical Hugging Face snapshot revision evidence.

The Golden v6 replay currently validates model identity, pinned revision, `$0-local`, `downloaded_now = false`, and snapshot revision binding, but it does not yet have a reusable verifier whose contract explicitly rejects drift in both `network_download_authorized` and `local_files_only` for both model receipts.

CS414 creates that fail-closed verification seam and its regression contract. It deliberately does not yet widen authority or alter generation behavior.

## Added

### `tools/phase18_verify_local_only_model_receipts.py`

A CPU-safe, network-free receipt verifier that:

- accepts the Qwen and FLUX cache receipts only as local JSON evidence;
- requires the expected receipt schemas;
- requires `ready = true` and `revision_pinned = true`;
- requires `cost_mode = "$0-local"`;
- requires `downloaded_now = false`;
- requires `network_download_authorized = false`;
- requires `local_files_only = true`;
- requires the exact approved Qwen2.5-VL and FLUX.2 model IDs and immutable revisions;
- requires `resolved_snapshot_revision` to match the approved revision;
- reuses `assert_snapshot_revision(...)` so canonical Hugging Face cache-path provenance remains enforced;
- emits a combined verification result with generation, publication, and Seeds 2–4 authority explicitly closed.

Success status:

`PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED`

Success schema:

`pul7sar-phase18-local-only-model-receipt-verification-v1`

The verifier performs no model loading, inference, image generation, queue mutation, network access, or publication action.

Commit: `e351821cd82f3c8a679bc1a5988497a174a5992d`

### `tests/test_phase18_verify_local_only_model_receipts.py`

Regression coverage verifies that:

- Qwen rejects `network_download_authorized = true`;
- Qwen rejects `local_files_only = false`;
- FLUX rejects a missing `network_download_authorized` field;
- FLUX rejects a missing `local_files_only` field;
- FLUX continues to reject resolved-revision drift;
- a valid pair of canonical local-only receipts produces the expected verification status while keeping `generation_authorized`, `publication_ready`, and `seeds_2_to_4_authorized` false.

Commit: `29a10624f916c4d7b9cde3074d3d0459b59b06b6`

## Modified

No pre-existing production, workflow, test, model-profile, prompt, generation, factual, identity, sentiment, semantic-publication, or visual-quality files were modified in the functional part of this checkpoint.

## Deleted

Nothing.

## Gate preservation

This checkpoint does not change:

- factual verification requirements;
- entity/identity verification;
- neutral/respectful result sentiment policy;
- semantic approval requirements;
- layer-ownership requirements;
- visual-quality thresholds;
- approved model IDs or revisions;
- BF16/GPU requirements;
- `$0-local` policy;
- human visual review authority;
- Golden-quality authority;
- publication authority;
- Seeds 2–4 authority.

The new combined verifier explicitly returns:

- `generation_authorized = false`;
- `publication_ready = false`;
- `seeds_2_to_4_authorized = false`.

## Testing status

The new verifier and its regression tests have been committed to `phase18/story-intelligence`. Repository CI is the authoritative full-suite validation for this checkpoint. CS414 must not be called terminal-green until the Story Intelligence Verification for the final CS414 HEAD completes successfully.

## Remaining integration gap

The next safe integration step, after CS414 CI is confirmed green, is to bind this verifier into the First Genuine Golden v6 evidence/replay path so the workflow/resource lock cannot accept either model receipt unless both explicit local-only fields are proven. That integration must remain fail-closed and must not create publication or Golden acceptance authority.

## Genuine PNG status and exact blocker

No First Genuine Golden Visual PNG was created or claimed in this checkpoint.

The non-substitutable execution blocker remains the absence, for this run, of a compatible self-hosted NVIDIA execution host satisfying the Golden v6 contract: CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the exact approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in canonical Hugging Face cache paths. Network model download is not an authorized workaround because the path must remain `$0-local` and local-cache-only.
