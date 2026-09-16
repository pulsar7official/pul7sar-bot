# PUL7SAR Phase 18 — Implementation Log 122

This log records work on `phase18/story-intelligence` only. `main` is not modified.

## Branch state reviewed before work

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Comparison against `main` before this pass: `diverged`, 946 commits ahead / 99 behind.
- PR #1 remained open, Draft, unmerged, with `main` as its base.
- Change Set 121 code/test head `ed5d8bc9304af916095d91dc6cee109ca23c054f` was verified by GitHub Actions run `32731206053` / run 1733 with conclusion `success`.
- A genuine Golden Hybrid v5 FLUX.2 Klein Candidate 1 remains unavailable in the current tool environment because no compatible CUDA/BF16 execution host is attached.

## Gap found

Change Set 121 provided a fail-closed semantic GPU preflight command, but the manual self-hosted GPU smoke workflow did not invoke it. Therefore a future compatible host could still begin FLUX preparation/generation before proving that the exact Qwen runtime and approved Qwen snapshot were ready on that same host.

This would preserve publication safety but could waste the scarce GPU window and leave the first genuine Candidate without semantic-side readiness evidence in the final GPU evidence bundle.

## Change Set 122 — GPU Smoke Semantic Preflight Integration

### Modified

#### `.github/workflows/phase18-gpu-smoke.yml`

The self-hosted GPU smoke now invokes `tools/phase18_preflight_semantic_gpu.py` immediately after GPU-side dependencies are installed and before FLUX model prefetch/readiness/generation.

The workflow validates the semantic receipt for:

- schema `pul7sar-phase18-semantic-gpu-preflight-v1`;
- branch `phase18/story-intelligence`;
- exact Qwen model `Qwen/Qwen2.5-VL-3B-Instruct`;
- `$0-local`;
- semantic runtime readiness;
- semantic model readiness;
- CUDA availability;
- `generation_authorized=false`;
- `queue_mutated=false`;
- `png_created=false`;
- `publication_ready=false`.

The branch-isolation step now also requires the semantic-preflight and Qwen-prefetch tools to exist.

The tamper-evident GPU evidence manifest now includes both `semantic-preflight.json` and `qwen-model-cache.json`, in addition to the existing FLUX model-cache, readiness, host qualification, execution, and PNG evidence.

#### `tests/test_phase18_gpu_smoke_workflow.py`

Added regression assertions proving:

- semantic preflight is present;
- semantic preflight executes before FLUX prefetch, local readiness, and generation;
- fail-closed semantic receipt fields are checked;
- the exact Qwen model is locked;
- semantic/Qwen cache evidence is included before evidence replay/upload;
- self-hosted CUDA/BF16, `$0-local`, and no-provider-secret invariants remain present.

### Added

- `docs/PHASE18_CHANGESET_122_GPU_SMOKE_SEMANTIC_PREFLIGHT_INTEGRATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_122.md`

### Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main`, `main.py`, production publishing and Telegram behavior;
- Fact Lock, source/state integrity and source consensus;
- identity verification and verified-asset ownership;
- sentiment and winner/loser neutrality safeguards;
- `$0-local` execution policy;
- FLUX.2 Klein 4B model selection;
- BF16 requirement;
- seed/canvas locks;
- generated PUL7SAR brand/text/score/crest/exact-sport-geometry exclusions;
- Qwen semantic inspection requirements;
- SemanticPublicationGate and direct publication gates;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact brand and typography integrity requirements.

No Fake PNG, provider substitution, paid API, hosted-GPU fallback, hidden precision downgrade, queue mutation in semantic preflight, or publication shortcut was introduced.

## Test / CI status

- Change Set 121 was independently verified: GitHub Actions `32731206053` / run 1733 concluded `success`.
- Change Set 122 code/test changes are committed on `phase18/story-intelligence`.
- A new Phase 18 verification run should be triggered by the workflow/test/documentation changes. Do not claim Change Set 122 CI success until a completed successful run is observed.

## Current genuine visual state

### Golden Hybrid v5 FLUX Candidate 1

Still blocked by the absence of a compatible CUDA/BF16 execution host in the current tool environment. No new FLUX PNG is fabricated or claimed.

### What this pass reduces

On the next real GPU host, the manual smoke workflow cannot reach FLUX Candidate 1 until semantic runtime + Qwen model readiness are proven first. The same semantic evidence is then carried into the replayable GPU evidence bundle.

The intended order is now:

`explicit confirmation → Phase 18 branch isolation → CUDA PyTorch → dependencies → semantic/Qwen preflight → FLUX model cache → BF16 readiness → locked Candidate 1 → real PNG → evidence build/replay → artifact upload`

## Remaining work

1. Observe the new Phase 18 CI result for Change Set 122 and fix any regression without weakening gates.
2. Execute the manual self-hosted GPU smoke on a compatible CUDA/BF16 host.
3. Generate Golden Hybrid v5 Candidate 1 only; do not spend GPU on Seeds 2–4 before review.
4. Preserve provenance acceptance, Base semantic/layer ownership, deterministic football geometry, Hybrid QA, Qwen HYBRID_SURFACE inspection, and SHA-bound Golden quality review on the genuine PNG.
5. Approve and SHA-lock the exact PUL7SAR logo/brand geometry/font assets before final publication composition.

## Change summary

- Modified: `.github/workflows/phase18-gpu-smoke.yml`
- Modified: `tests/test_phase18_gpu_smoke_workflow.py`
- Added: `docs/PHASE18_CHANGESET_122_GPU_SMOKE_SEMANTIC_PREFLIGHT_INTEGRATION.md`
- Added: `docs/PHASE18_IMPLEMENTATION_LOG_122.md`
- Deleted: none
- `main`: untouched
