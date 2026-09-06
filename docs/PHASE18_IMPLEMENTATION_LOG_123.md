# PUL7SAR Phase 18 — Implementation Log 123

This log records work on `phase18/story-intelligence` only. `main` is not modified.

## Branch state reviewed before work

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Comparison against `main` before this pass: `diverged`, 974 commits ahead / 101 behind.
- PR #1 remained open, Draft, unmerged, with `main` as its base.
- The prior Phase 18 verification run `32741694496` / run 1820 completed with conclusion `success` on head `9b7ff709c6e664a3928d34e8a3151abd75a71878`.
- A genuine Golden Hybrid v5 FLUX.2 Klein Candidate 1 remains unavailable in the current tool environment because no compatible CUDA/BF16 execution host is attached.

## Gap found

Change Set 122 integrated semantic/Qwen preflight into the manual self-hosted GPU workflow. The direct one-command path `tools/phase18_first_png.py`, however, still qualified the host and FLUX stack without requiring the same exact Qwen runtime/model preflight before FLUX preparation and queue mutation.

Therefore a user could correctly use the one-command tool on a compatible GPU host, spend FLUX GPU time, and only discover semantic-side incompatibility after the genuine Base PNG already existed. This did not weaken publication safety, but it left an avoidable reliability gap before the first genuine Golden Visual.

## Change Set 123 — First-PNG Semantic Preflight Lock

### Modified

#### `tools/phase18_first_png.py`

Added a mandatory semantic GPU preflight between physical host qualification and FLUX model prefetch.

The direct first-PNG execution order is now:

`Golden batch integrity → CUDA/BF16 host qualification → Qwen semantic/model preflight → FLUX model cache → FLUX/BF16 readiness → durable Candidate 1 queue → GPU worker → genuine PNG`

The semantic preflight must prove:

- schema `pul7sar-phase18-semantic-gpu-preflight-v1`;
- exact Qwen model `Qwen/Qwen2.5-VL-3B-Instruct`;
- `$0-local`;
- semantic runtime ready;
- semantic model ready;
- CUDA available;
- no generation authority;
- no queue mutation;
- no PNG creation;
- no publication authority.

Added explicit first-PNG arguments/evidence paths for:

- semantic preflight receipt;
- Qwen model-cache receipt;
- separate Qwen minimum free-disk headroom.

The final first-PNG result now carries semantic runtime/model readiness and exact semantic/Qwen evidence references alongside the existing host/FLUX/readiness evidence.

#### `tests/test_phase18_first_png_preflight.py`

Added regression tests proving:

- host qualification precedes semantic preflight;
- semantic preflight precedes FLUX prefetch/readiness and any durable queue mutation;
- the complete semantic fail-closed contract is required;
- generation/publication authority drift in semantic preflight is rejected;
- exact semantic/Qwen evidence paths and Qwen disk-headroom arguments are passed to the semantic tool;
- the existing host, FLUX-cache and repository-path protections remain.

### Added

- `docs/PHASE18_CHANGESET_123_FIRST_PNG_SEMANTIC_PREFLIGHT_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_123.md`

### Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main`, `main.py`, production publishing and Telegram behavior;
- Fact Lock, source consensus and story-state integrity;
- identity verification and verified-asset ownership;
- sentiment and winner/loser neutrality;
- `$0-local` execution policy;
- FLUX.2 Klein 4B model selection;
- native BF16 requirement;
- seed/canvas locks;
- generated PUL7SAR brand/text/score/crest/exact-sport-geometry exclusions;
- Base semantic/layer ownership gate;
- Qwen semantic inspection and HYBRID_SURFACE review;
- SemanticPublicationGate and direct publication gates;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact brand and typography integrity requirements.

No Fake PNG, paid provider, hosted-GPU fallback, hidden precision downgrade, semantic bypass or publication shortcut was introduced.

## Test / CI status

- Prior head `9b7ff709c6e664a3928d34e8a3151abd75a71878` is verified: GitHub Actions `32741694496` / run 1820 concluded `success`.
- Change Set 123 code/tests/documentation are committed on `phase18/story-intelligence`.
- A new Phase 18 verification run should be triggered by these changes. Do not claim Change Set 123 CI success until a completed successful run is observed.

## Current genuine visual state

### Golden Hybrid v5 FLUX Candidate 1

Still blocked by the absence of a compatible CUDA/BF16 execution host in the current tool environment. No new FLUX PNG is fabricated or claimed.

### What this pass reduces

The two practical GPU entrypoints now share the same semantic-before-generation invariant:

- `.github/workflows/phase18-gpu-smoke.yml`
- `tools/phase18_first_png.py`

Both must prove exact local Qwen runtime/model readiness on the target CUDA host before FLUX Candidate 1 execution is allowed.

## Remaining work

1. Observe the new Phase 18 CI result for Change Set 123 and repair any regression without weakening gates.
2. Execute Candidate 1 only on a compatible CUDA/BF16 host.
3. Preserve generation provenance acceptance, Base semantic/layer ownership, deterministic football geometry, receipt-backed Hybrid QA, Qwen HYBRID_SURFACE inspection and SHA-bound Golden review on the genuine PNG.
4. Do not spend GPU on Seeds 2–4 before Candidate 1 is visually reviewed.
5. Approve and SHA-lock the exact PUL7SAR logo/brand geometry/font assets before final publication composition.

## Change summary

- Modified: `tools/phase18_first_png.py`
- Modified: `tests/test_phase18_first_png_preflight.py`
- Added: `docs/PHASE18_CHANGESET_123_FIRST_PNG_SEMANTIC_PREFLIGHT_LOCK.md`
- Added: `docs/PHASE18_IMPLEMENTATION_LOG_123.md`
- Deleted: none
- `main`: untouched
