# PUL7SAR Phase 18 — Implementation Log 121

This log records the current progression pass on `phase18/story-intelligence` only. `main` is not modified.

## Branch state reviewed before work

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Comparison against `main` at the start of this pass: `diverged`, 927 commits ahead / 93 behind.
- PR #1 remained open, Draft, unmerged, with `main` as its base.
- The current Golden Hybrid contract remains `pul7sar-golden-batch-v5`.
- The previous branch HEAD `05664db2b5baa2954d91811828d59fd111d8df6d` had a successful Phase 18 verification run: GitHub Actions `32729840707`, run 1729, conclusion `success`.
- A genuine FLUX.2 Klein 4B Golden Hybrid Candidate 1 is still unavailable in this tool environment because no compatible CUDA/BF16 execution host is attached.

## Gap found

The Colab bootstrap already contains a Qwen model-cache preflight before the Golden Hybrid run, but the generic/self-hosted GPU execution surface did not have a standalone, reusable semantic-side preflight command that could prove all of the following *before* FLUX generation:

1. the exact qualified Qwen/Pillow/Transformers runtime is healthy on CUDA;
2. the approved `Qwen/Qwen2.5-VL-3B-Instruct` snapshot is locally available or can be prefetched under the existing disk policy;
3. the semantic model remains `$0-local`;
4. no generation queue mutation, PNG creation, or publication authorization happens during this preparation.

Without this check a GPU host could spend time generating a valid FLUX base scene and only then discover that semantic inspection cannot run, which would not violate publication gating but would waste the scarce compatible GPU window.

## Change Set 121 — Fail-closed semantic GPU preflight

### Added

#### `tools/phase18_preflight_semantic_gpu.py`

A new pre-generation semantic readiness command.

It performs the following sequence:

- proves the active branch is exactly `phase18/story-intelligence`;
- runs `Qwen25VLReadinessProbe` first;
- fails closed if CUDA or the exact verified semantic runtime is unavailable;
- only after runtime readiness succeeds, invokes the existing `tools/phase18_prefetch_qwen.py` cache/prefetch boundary;
- requires the exact approved Qwen model id;
- requires `cost_mode == $0-local`;
- requires a real snapshot path;
- writes a machine-readable receipt at `output/phase18_gpu_smoke/semantic-preflight.json` by default.

The receipt explicitly records:

- `semantic_runtime_ready`;
- `semantic_model_ready`;
- CUDA availability;
- Transformers/Torch versions;
- runtime failures, if any;
- Qwen snapshot path and prefetch receipt path;
- `generation_authorized=false`;
- `queue_mutated=false`;
- `png_created=false`;
- `publication_ready=false`.

The tool does not import or invoke FLUX, does not enqueue a GenerationJob, and cannot grant publication approval.

#### `tests/test_phase18_semantic_gpu_preflight.py`

Regression coverage verifies:

- semantic runtime failure blocks before Qwen model prefetch;
- the prefetch receipt must identify the exact approved model;
- any escape from `$0-local` is rejected;
- the semantic-preflight receipt can never authorize generation or publication;
- a successful preflight writes only its receipt and does not create a generation queue.

## Modified

Nothing in existing Phase 18 runtime behavior was modified in this pass. The change is additive so it cannot silently alter a previously qualified generation or publication route.

## Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main`, `main.py`, production publishing and Telegram behavior;
- Fact Lock, source/state integrity and consensus requirements;
- identity verification and verified-asset requirements;
- sentiment and winner/loser neutrality safeguards;
- `$0-local` policy;
- FLUX.2 Klein 4B and BF16 requirement for the Golden generative path;
- seed/canvas locks;
- generated PUL7SAR brand/text/score/crest/exact sport geometry exclusions;
- Qwen semantic inspection requirements;
- SemanticPublicationGate / direct publication gates;
- Golden visual thresholds (`8.5` minimum, `9.0+` elite target);
- exact brand and typography integrity requirements.

No Fake PNG, provider substitution, paid API, hidden GPU downgrade, queue mutation, or publication-ready shortcut was introduced.

## Test / CI status

- Pre-work verified CI: run `32729840707` / 1729 on HEAD `05664db2b5baa2954d91811828d59fd111d8df6d` completed successfully.
- Change Set 121 code/test HEAD after this pass: `ed5d8bc9304af916095d91dc6cee109ca23c054f` before this log commit.
- A new GitHub Actions run is expected from the added Phase 18 test/tool files; do not claim Change Set 121 CI success until that run completes successfully.

## Current genuine visual state

### Golden Hybrid v5 FLUX Candidate 1

Still blocked by the absence of a compatible CUDA/BF16 execution host in the current tool environment. No FLUX Hybrid v5 PNG is fabricated or claimed here.

### What this pass reduces

When a compatible host becomes available, the semantic side can now be qualified before FLUX generation with one explicit command:

```bash
PYTHONPATH=. python tools/phase18_preflight_semantic_gpu.py
```

Only after it succeeds should the locked Candidate 1 generation path run. This removes a preventable late Qwen-runtime/model-cache failure from the scarce GPU window while preserving all semantic-publication and quality gates.

## Remaining work

1. Verify the new Phase 18 CI run for Change Set 121; fix any exact regression without weakening gates.
2. Integrate this semantic preflight into the self-hosted GPU smoke workflow after it has been independently validated.
3. Execute Golden Hybrid v5 Candidate 1 on a compatible CUDA/BF16 host.
4. Preserve generation provenance, Base semantic/layer ownership, deterministic football geometry, Hybrid QA, Qwen HYBRID_SURFACE review, and SHA-bound Golden quality review on that real PNG.
5. Review Candidate 1 before spending GPU on Seeds 2–4.
6. Approve and SHA-lock the exact PUL7SAR brand geometry/logo/font assets before final publication composition.

## Change summary

- Added: `tools/phase18_preflight_semantic_gpu.py`
- Added: `tests/test_phase18_semantic_gpu_preflight.py`
- Added: `docs/PHASE18_IMPLEMENTATION_LOG_121.md`
- Modified: none
- Deleted: none
- `main`: untouched
