# Phase 18 Implementation Log — CS465

## Scope

Branch only: `phase18/story-intelligence`.

`main` was not modified.

CS465 closes the remaining provenance gap introduced after CS464: the approved Qwen2.5-VL and FLUX.2 snapshot inventory was captured before Candidate 1 generation, but it was not replayed and cryptographically bound to the final Golden evidence after generation.

## Added

### `tools/phase18_verify_first_genuine_golden_v6_snapshot_bound.py`

Adds a CPU-safe, fail-closed post-generation verifier that:

- accepts the existing fresh/source/runner/execution-bound Golden manifest;
- validates the recorded approved snapshot inventory schema and policy;
- validates exact approved Qwen2.5-VL and FLUX.2 model IDs and revisions;
- recomputes each inventory fingerprint from model ID, revision, relative file paths, sizes, symlink state and local cache targets;
- recomputes the combined inventory fingerprint;
- re-captures the local approved-model inventory after generation using the same zero-cost/offline inventory implementation;
- rejects any preflight-to-post-generation cache drift;
- binds the recorded inventory file SHA-256 and upstream Golden manifest SHA-256 into a final snapshot-bound manifest;
- preserves Human Review, Golden approval, publication and Seeds 2–4 as closed authorities.

The new final schema is:

`pul7sar-phase18-first-genuine-golden-v6-snapshot-bound-manifest-v1`

The verifier performs no network access, model loading, image generation, approval, publication or queue mutation.

### `tests/test_phase18_first_golden_snapshot_bound_manifest.py`

Adds regression coverage for:

1. identical approved snapshot inventory before and after generation;
2. rejection when the model cache inventory changes after preflight;
3. rejection of publication/authority drift.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

Adds the new verifier to the immutable checkout proof and adds a post-generation step after the existing execution/runner/fresh/source/PNG binding and before artifact upload:

`Replay and bind approved model snapshots after generation`

The step consumes:

- `first-genuine-golden-v6-fresh-source-bound-manifest.json`
- `first-genuine-golden-v6-approved-snapshot-inventory.json`

and emits:

- `first-genuine-golden-v6-snapshot-bound-manifest.json`
- `first-genuine-golden-v6-snapshot-bound-replay.json`

This makes an unchanged approved local model snapshot inventory a requirement for Candidate 1 evidence to remain eligible for Human Visual Review.

### `tests/test_phase18_first_golden_fresh_workflow.py`

Extends the workflow contract tests to require:

- the post-generation snapshot replay tool;
- the recorded preflight inventory as input;
- the snapshot-bound manifest as output;
- ordering after final PNG/source binding and before artifact upload.

## Deleted

None.

## Preserved gates

CS465 does not change or weaken:

- factual correctness gates;
- entity/identity verification;
- sentiment and loser-respect rules;
- SemanticPublicationGate;
- Human Visual Review authority;
- Golden quality approval authority;
- Candidate 1 prompt, seed, steps, dimensions or guidance;
- Qwen2.5-VL or FLUX.2 approved identities/revisions;
- `$0-local` execution;
- offline-only model resolution;
- native BF16 requirement;
- publication authority;
- Seeds 2–4 authority.

The final snapshot-bound manifest explicitly keeps:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Testing

The new unit tests are designed to run CPU-only and without network/model loading. GitHub Actions on the exact CS465 head is the authoritative repository test result for this change set.

A genuine Golden PNG is still not fabricated or claimed by CS465. Actual Candidate 1 generation remains blocked until a compatible self-hosted NVIDIA runner is available with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the zero-cost/offline-only contract.
