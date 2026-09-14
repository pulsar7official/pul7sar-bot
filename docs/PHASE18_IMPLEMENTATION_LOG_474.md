# Phase 18 Implementation Log — CS474

## Scope

CS474 advances the first genuine Golden Visual PNG path without changing `main` and without weakening any factual, identity, sentiment, zero-cost, semantic-publication, Human Review, Golden-quality, or publication authority gate.

The exact Phase 18 working branch is `phase18/story-intelligence`.

## Problem closed

CS473 proved that the Python-level zero-cost network guard was active before model/CUDA preflight and emitted a dedicated JSON evidence file. That evidence was useful diagnostically, but it was not yet cryptographically carried into the exact Human Review bundle that would be uploaded after a successful Candidate 1 generation.

That left a provenance gap: the final review artifact could prove source/runtime/model/PNG integrity while the zero-cost network isolation proof remained outside the bundle.

CS474 closes that gap.

## Added

### `tools/phase18_bind_zero_cost_network_guard_to_review_bundle.py`

A CPU-safe, offline, fail-closed binder/replayer that:

- validates the CS473 network-evidence schema;
- requires `phase18/story-intelligence` and the exact source commit recorded by the review bundle;
- requires `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` evidence;
- requires the `sitecustomize` guard to have been active;
- requires `network_download_authorized=false`;
- requires all four synthetic external-network paths to have been blocked with the exact guard marker;
- validates the evidence's internal canonical SHA-256;
- optionally binds the evidence to the exact GitHub run ID and run attempt;
- copies the exact evidence bytes into `evidence/zero_cost_network_guard.json` inside the run-scoped Human Review bundle;
- adds the copied file to the bundle manifest with SHA-256 and byte count;
- records both the copied-file SHA-256 and the internal canonical evidence SHA-256;
- provides an independent `verify` replay that fails on removal, byte drift, source/run drift, policy drift, authority drift, or evidence tampering.

### `tests/test_phase18_zero_cost_network_review_binding.py`

Regression coverage includes:

- successful bind + replay of exact network evidence;
- rejection of source-commit drift;
- rejection if any synthetic external-network path was not blocked;
- rejection of post-binding evidence-byte drift;
- rejection of review-bundle authority drift;
- workflow ordering that requires network binding after packaging, before closed-set replay, then network replay before tracked-source replay and success upload.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

The immutable checkout proof now requires the new binder tool.

The success path is now:

1. package the exact Candidate 1 Human Review bundle;
2. bind the CS473 zero-cost network guard evidence into that bundle;
3. replay the entire bundle as an exact closed file set;
4. independently replay the zero-cost network binding;
5. replay immutable tracked-source integrity;
6. upload the exact review bundle only if every previous step succeeds.

The original CS473 evidence file remains captured before model preflight. CS474 therefore connects that pre-generation proof to the final post-generation Human Review artifact.

## Deleted

None.

## Gate preservation

CS474 does not authorize generation, Human Review approval, Golden approval, publication, model downloads, paid services, or seeds 2–4.

The following remain closed:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

Existing factual/source-consensus, identity/entity, sentiment/loser-respect, SemanticPublicationGate, exact Qwen2.5-VL/FLUX.2 snapshot, CUDA, native-BF16, freshness, source provenance, runtime replay, snapshot replay, review-bundle replay, tracked-source, and immutable GitHub Action requirements remain unchanged.

## Testing

The new unit tests are committed on the Phase 18 branch and GitHub Actions is the authoritative CI environment for this repository. The local execution environment available to this run cannot resolve `github.com` from the container, so no local clone-based test result is claimed.

## Remaining blocker to the first genuine Golden Visual PNG

No genuine PNG is claimed by CS474.

A real Candidate 1 generation still requires an available self-hosted NVIDIA runner satisfying all existing requirements simultaneously, including CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local` / offline-only contract.

CS474 materially reduces the remaining provenance gap: when a compatible GPU attempt succeeds, the final Human Review artifact cannot pass the upload path unless the same run's pre-model zero-cost network-isolation evidence is cryptographically embedded and replayed inside the exact review bundle.
