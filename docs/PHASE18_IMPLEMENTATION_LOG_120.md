# PUL7SAR Phase 18 — Implementation Log 120

This log records the current maintenance/progression pass on `phase18/story-intelligence` only. `main` is not modified.

## Branch state reviewed before work

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Comparison against `main`: `diverged`, 904 commits ahead / 90 behind after the regression-lock commit.
- PR #1 remains open, Draft, unmerged, with `main` as its base.
- Current Golden Hybrid contract remains `pul7sar-golden-batch-v5`.
- The genuine FLUX.2 Klein 4B Golden Hybrid Candidate 1 is still not available from this tool environment because no compatible CUDA/BF16 host is attached.

## Problem discovered

The branch had just advanced the CPU editorial visual study from the old generic study contract to a story-specific fictional transfer benchmark:

- `pul7sar-editorial-scene-study-v2`
- benchmark id `transfer-signature-v1`
- no generator/provider/GPU
- no verified player asset
- approximate study-only brand geometry
- publication remains blocked

The first CI run after that change (`32723963613`, run 1679) failed at `Assert editorial visual study safety contract` because the workflow was still asserting the obsolete `pul7sar-editorial-scene-study-v1` manifest.

This was a CI contract drift, not a visual-generation failure and not a reason to weaken any factual, identity, sentiment, semantic-publication or Golden-quality gate.

## Change Set 120 — Transfer benchmark CI contract lock

### Existing fix confirmed

The workflow was updated on the Phase 18 branch to assert the current transfer-study v2 contract:

- `manifest_version == pul7sar-editorial-scene-study-v2`
- `benchmark_id == transfer-signature-v1`
- `generator_used == false`
- `legacy_logo_used == false`
- `verified_player_asset_used == false`
- `study_only == true`
- `publication_ready == false`
- `brand_geometry_mode == approximate-study-only-v2`
- `exact_brand_master_still_required_for_publication == true`
- output must be a genuine PNG

This keeps the transfer study explicitly fictional/non-publication and prevents it from being confused with a real player-news visual or with the still-missing FLUX Golden Hybrid proof.

### Added regression lock

Modified `tests/test_phase18_intelligence_workflow.py` with a dedicated regression test that now requires the workflow itself to contain the transfer-study v2 contract and rejects the stale v1 assertion.

The regression specifically locks:

- `pul7sar-editorial-scene-study-v2`
- `transfer-signature-v1`
- `verified_player_asset_used`
- `approximate-study-only-v2`
- absence of the stale `manifest_version == pul7sar-editorial-scene-study-v1` assertion

This prevents a future builder/workflow mismatch from silently stopping the Phase 18 validation pipeline before the Golden Hybrid handoff and batch checks.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_120.md`
- new transfer-study v2 workflow regression coverage inside `tests/test_phase18_intelligence_workflow.py`

## Modified

- `tests/test_phase18_intelligence_workflow.py`

The workflow alignment itself is already present on the same Phase 18 branch in commit `6bcd1448ea9357f7ae11f3c9339da6284333c581`.

## Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main` / `main.py` / production publishing behavior;
- Fact Lock, source/state integrity and consensus requirements;
- identity verification and verified-asset requirements;
- sentiment and winner/loser neutrality safeguards;
- `$0-local` policy;
- FLUX.2 Klein 4B and BF16 requirement for the Golden generative path;
- generated PUL7SAR brand/text/score/crest/exact sport geometry exclusions;
- Qwen semantic inspection requirements;
- SemanticPublicationGate / direct publication gates;
- Golden visual thresholds (`8.5` minimum, `9.0+` elite target);
- exact brand and typography integrity requirements.

No Fake PNG, provider substitution, paid API, hidden GPU downgrade or publication-ready shortcut was introduced.

## Test / CI status

Historical failing evidence:

- Run `32723963613` / 1679: CPU tests, completion audit, production isolation, and visual-study build all passed; the run failed only because CI still asserted the old editorial-study v1 manifest.

Current regression-lock commit:

- `0d25d09aae09ea363648838c7286445632fec548`
- GitHub Actions run `32724293906` / 1683 is in progress at the time this log is written.

Do not claim CI success for Change Set 120 until that run completes successfully.

## Current genuine visual state

### Transfer editorial study v2

A CPU-only, fictional transfer benchmark intended for visual grammar/design study. It uses no verified real-player asset and cannot be publication-ready.

### Golden Hybrid v5 FLUX Candidate 1

Still blocked by the absence of a compatible CUDA/BF16 execution host in the current tool environment. No FLUX Hybrid v5 PNG is fabricated or claimed here.

## Remaining work

1. Wait for/verify run 1683; if it fails, fix the exact regression without weakening any gate.
2. Execute Golden Hybrid v5 Candidate 1 on a compatible CUDA/BF16 host when available.
3. Preserve generation provenance, Base semantic/layer ownership, deterministic football geometry, Hybrid QA, Qwen HYBRID_SURFACE review, and SHA-bound Golden quality review on that real PNG.
4. Review Candidate 1 before spending GPU on Seeds 2–4.
5. Approve and SHA-lock the exact PUL7SAR brand geometry/logo/font assets before final publication composition.

## Change summary

- Added: `docs/PHASE18_IMPLEMENTATION_LOG_120.md`
- Modified: `tests/test_phase18_intelligence_workflow.py`
- Deleted: none
- `main`: untouched
