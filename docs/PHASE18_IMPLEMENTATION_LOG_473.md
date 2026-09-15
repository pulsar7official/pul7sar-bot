# Phase 18 Implementation Log — CS473

## Scope

CS473 advances the first genuine Golden Visual PNG path by converting the CS472 process-local zero-cost network isolation from an implicit startup property into explicit, fail-closed execution evidence captured before any model/CUDA preflight.

Branch scope remains strictly `phase18/story-intelligence`. `main` is not modified.

## Why this change was necessary

CS472 installed a stdlib-only `sitecustomize` network guard whenever the existing `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` contract is active. That materially strengthened zero-cost execution, but the Golden workflow did not yet emit a run artifact proving that the guard was active in the exact process environment used by the attempt.

CS473 closes that gap without authorizing generation, publication, network access, or alternative model/runtime paths.

## Added

### `tools/phase18_capture_zero_cost_network_guard_evidence.py`

A stdlib-only evidence capture tool that fails closed unless all of the following are true:

- `PUL7SAR_PHASE18_COST_MODE=$0-local`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- the zero-cost guard contract is requested
- `sitecustomize` has actually activated the guard
- `PUL7SAR_PHASE18_NETWORK_GUARD_ACTIVE=1`
- the checked-out branch is exactly `phase18/story-intelligence`
- the checked-out source SHA is a valid 40-character Git commit SHA

It then performs four synthetic external-network attempts that must be rejected by the in-process guard before network I/O:

1. `socket.connect` to TEST-NET-2 (`198.51.100.1`)
2. `socket.connect_ex` to TEST-NET-2
3. `socket.create_connection` to TEST-NET-2
4. `socket.getaddrinfo` for the reserved `.invalid` name `example.invalid`

Every check must raise the existing `PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED` marker. Any other result is a hard failure.

The emitted JSON records source branch/SHA, zero-cost/offline contract state, guard activation, all synthetic checks, GitHub run identity when present, and a deterministic SHA-256 over the evidence payload.

No real external connection is needed or permitted by the probe.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

Added the new evidence tool to the immutable checkout proof and added a new step:

`Prove zero-cost network guard is active before any model preflight`

The step executes immediately after the tracked-source baseline and before the execution blocker/model snapshot/CUDA checks. It writes:

`output/phase18_gpu_smoke/first-genuine-golden-v6-zero-cost-network-guard.json`

Therefore an unavailable or bypassed process-local network guard now blocks the Golden attempt before model loading or Candidate 1 generation.

### `tests/test_phase18_zero_cost_network_guard.py`

Added workflow-order regression coverage requiring:

- the evidence tool to be part of immutable checkout proof;
- the evidence capture command to be present;
- the evidence JSON path to remain fixed;
- guard evidence capture to occur before the execution blocker probe;
- guard evidence capture to occur before canonical Candidate 1 generation.

The pre-existing subprocess test that proves `sitecustomize` rejects an external connection before network I/O remains intact.

## Deleted

Nothing.

## Gates preserved

CS473 does not weaken or bypass any existing Phase 18 gate. In particular it preserves:

- factual/source-consensus gates;
- entity/identity gates;
- sentiment and loser-respect gates;
- semantic-publication gate;
- Human Visual Review and Golden-quality gates;
- `$0-local` and offline-only execution;
- exact approved Qwen2.5-VL and FLUX.2 snapshots;
- CUDA and native-BF16 requirements;
- resource/headroom gates;
- freshness/source/runner/runtime/model/PNG provenance binding;
- immutable tracked-source replay;
- exact closed-set review bundle replay;
- publication and Seeds 2–4 authority remaining closed.

No Golden PNG is claimed by this changeset.

## Expected execution order after CS473

1. immutable dispatch/checkout/main isolation
2. tracked-source baseline
3. **zero-cost network-guard evidence**
4. execution blocker probe
5. approved model snapshot inventory
6. runner/CUDA identity evidence
7. native BF16/offline proof
8. freshness-bound Candidate 1 generation
9. freshness/source/PNG binding
10. post-generation model/runtime replay
11. exact Human Review bundle packaging
12. closed-set bundle replay
13. tracked-source replay
14. success upload

## Remaining blocker

The first genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA runner with all required conditions simultaneously satisfied: CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible approved runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local`/offline-only contract.

CS473 does not fabricate a GPU result and does not substitute CPU, FP16, FP32, downloads, paid APIs, or a different model stack.
