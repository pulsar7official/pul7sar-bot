# Phase 18 Implementation Log — CS464

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

CS464 adds a deterministic, zero-cost, offline-only approved-model snapshot inventory gate immediately before the first genuine Golden v6 Candidate 1 GPU attempt. The purpose is to reduce the chance of consuming a rare compatible GPU run on an incomplete or structurally drifted local Hugging Face cache even when the approved revision directory name is present.

## Added

### `tools/phase18_capture_approved_snapshot_inventory.py`

Adds a non-authoritative local-only inventory probe for the exact approved Qwen2.5-VL and FLUX.2 snapshot directories. It:

- performs no network access, downloads, model loading, generation, publication, or queue mutation;
- requires `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`;
- resolves only the exact approved model IDs and revisions already defined by Phase 18 policy;
- requires each approved snapshot directory to exist and contain readable files;
- records deterministic relative file paths, sizes, symlink state, and local cache targets;
- rejects any resolved snapshot file that escapes the Hugging Face cache root;
- produces per-model and combined SHA-256 inventory fingerprints;
- leaves authoritative, generation, network-download, publication, and Seeds 2–4 authorities closed.

This is an inventory fingerprint rather than a full multi-gigabyte byte hash. It is deliberately fast enough to run before a rare GPU attempt while still detecting missing files, path drift, size drift, and cache-target drift.

### `tests/test_phase18_approved_snapshot_inventory.py`

Adds regression coverage for:

- deterministic inventory fingerprints for unchanged approved local snapshots;
- fail-closed behavior when the FLUX approved snapshot is absent;
- fingerprint drift when a local model file size changes;
- mandatory zero-cost and offline-only contracts.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

The freshness-bound GPU workflow now:

1. confirms that the snapshot-inventory tool exists on the immutable Phase 18 commit;
2. runs the existing execution-blocker probe;
3. captures `first-genuine-golden-v6-approved-snapshot-inventory.json`;
4. proceeds to runner/CUDA identity capture and native-BF16 proof only if the inventory gate succeeds;
5. starts Candidate 1 only after the approved local snapshots have passed this structural inventory gate.

The inventory JSON is under `output/phase18_gpu_smoke/**`, so the existing `if: always()` evidence upload includes it on completed runner executions.

### `tests/test_phase18_first_golden_fresh_workflow.py`

Adds a workflow-ordering regression assertion proving that the approved snapshot inventory runs after the execution-blocker probe and before Candidate 1 generation.

## Deleted

Nothing.

## Preserved contracts

CS464 does not change:

- factual verification gates;
- entity/identity verification;
- result sentiment and losing-side respect rules;
- `SemanticPublicationGate`;
- Human Visual Review or Golden quality approval authority;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or visual direction;
- approved Qwen2.5-VL or FLUX.2 model IDs/revisions;
- CUDA/native-BF16 requirement;
- `$0-local` and offline-only requirements;
- publication authority;
- Seeds 2–4 authority.

The new inventory tool explicitly keeps `authoritative_gate=false`, `network_download_authorized=false`, `generation_authorized=false`, `publication_ready=false`, and `seeds_2_to_4_authorized=false`.

## Tests

Added unit tests for the new inventory probe and expanded the existing fresh-workflow static contract tests. Central GitHub Actions status must be evaluated on the final CS464 HEAD before calling the change terminal-green.

## Remaining blocker to first genuine Golden PNG

No Golden PNG is fabricated by CS464. A genuine Candidate 1 still requires an available self-hosted NVIDIA runner satisfying all existing labels and runtime contracts simultaneously: real CUDA-enabled PyTorch, native BF16, approved GPU/VRAM headroom, sufficient host RAM and cache/filesystem working space, compatible generation and semantic runtimes, and both exact approved Qwen2.5-VL and FLUX.2 snapshots already available locally under zero-cost offline-only execution.
