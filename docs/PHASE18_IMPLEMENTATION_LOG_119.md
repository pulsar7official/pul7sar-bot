# PUL7SAR Phase 18 — Implementation Log 119

This log records Change Set 119 on `phase18/story-intelligence` only. `main` is not modified.

## Branch state reviewed before work

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Comparison against `main` before Change Set 119: `diverged`, 849 commits ahead / 90 behind.
- PR #1 remained open, Draft, unmerged, with `main` as its base.
- Pre-change head: `ea9e6c5cc82c3d49693bbe76642180db40a69865` (`Phase 18 Change Set 118: lock clean Golden Direct Visual candidate`).
- Pre-change Phase 18 CI: GitHub Actions run `32718051076` completed with `success`.

## Carry-forward evidence from Change Set 118

The successful CPU CI run produced a genuine deterministic PNG artifact at:

`output/phase18_visual_proof/golden-direct-v1/candidate-01-golden-direct.png`

Its manifest records:
- route: `deterministic_only`
- base source: `programmatic_canvas`
- generator used: `false`
- provider used: `false`
- GPU used: `false`
- cost mode: `$0-local`
- publication ready: `false`
- exact PNG SHA-256 receipt present

This is a genuine CPU-rendered engineering visual proof, not the still-missing Golden Hybrid FLUX GPU proof and not a publication-ready news visual.

## Change Set 119 — Direct semantic/publication evidence bridge

### Goal

Close the remaining generator-bypass publication architecture gap without fabricating a `GenerationPackage`, provider provenance, or GPU evidence for routes that correctly bypass image generation.

Direct deterministic and verified-asset visuals must preserve the same safety philosophy as hybrid/generative visuals: no image becomes publication-ready merely because exact PNG bytes exist.

### Added

#### `engine/intelligence/direct_publication.py`

Adds two independent fail-closed gates:

1. `DirectSemanticPublicationGate`
   - requires a successful `DirectRenderQualityDecision`;
   - rechecks direct-execution locks proving no generation package, provider selection, or GPU job was used;
   - requires a zero-cost local semantic-verifier capability profile;
   - requires an explicit semantic visual-inspection approval plus a concrete evidence reference;
   - requires identity approval when the direct base is a verified identity asset;
   - never invents provider/model provenance for a generator-bypass route.

2. `DirectPublicationReadinessGate`
   - requires the direct semantic-publication gate;
   - requires fact integrity;
   - requires result/editorial neutrality;
   - requires Golden visual-quality approval;
   - requires exact brand integrity;
   - requires typography integrity;
   - requires final export authorization;
   - returns `DIRECT_PUBLICATION_BLOCKED` unless every independent gate passes.

#### `tests/test_phase18_direct_publication.py`

Regression coverage proves:
- deterministic direct renders still require a concrete semantic evidence reference;
- verified-asset routes require identity verification;
- remote/paid/incomplete semantic verifier profiles cannot authorize the route;
- direct execution-lock drift (for example a GPU job suddenly becoming required) blocks publication;
- final direct publication readiness requires semantic, fact, neutrality, Golden, brand, typography and export gates together.

### Modified

No existing production/runtime file was modified in this change set. The new direct publication path is additive and isolated.

### Deleted

Nothing.

## Invariants preserved

Unchanged:
- `main` / `main.py` / production publishing behavior;
- Fact Lock and source/state integrity;
- identity verification;
- winner/loser neutrality and sentiment safeguards;
- `$0-local` development cost policy;
- FLUX.2 Klein 4B and BF16 requirements for the generative Golden path;
- generated PUL7SAR brand/text/score/crest/exact sport geometry exclusions;
- SemanticPublicationGate for generated/hybrid routes;
- Golden visual thresholds (`8.5` minimum, `9.0+` elite target);
- exact brand and typography integrity requirements.

The new direct gate does not weaken or replace the existing hybrid publication gate. It prevents direct routes from being forced through fake generator contracts while preserving independent publication checks.

## Current genuine visual state

### Genuine CPU Direct Visual

Available and SHA-receipted from successful CI. It proves the generator-bypass renderer can create exact PNG bytes and artifacts. It remains `publication_ready=false` and is an engineering benchmark, not a final sports-news Golden Visual.

### Genuine Golden Hybrid FLUX Visual

Still blocked by unavailable compatible CUDA/BF16 execution in the current tool environment. No FLUX Hybrid v5 PNG is fabricated or claimed in this change set.

The exact external blocker remains: a CUDA/BF16 host capable of running the locked FLUX.2 Klein 4B Candidate 1 path (plus the required local semantic inspection runtime for publication-grade review).

## CI evidence

Change Set 119 head before this log-only follow-up: `2c8aa478e9a5dd792d06b82b8d50c3cddf4fb5a7`.

GitHub Actions run `32719278191` / run number `1579` completed with `success`.

Successful stages included:
- Phase 18 syntax checks;
- complete discover-based Phase 18 CPU validation, including `tests/test_phase18_direct_publication.py`;
- completion audit;
- production-isolation verification;
- Golden Hybrid v5 portable handoff build;
- four-candidate Golden Hybrid v5 batch build and integrity verification;
- current Golden Hybrid v5 contract assertions;
- genuine Golden Direct Visual CPU proof build;
- upload of the direct visual proof artifact.

No CUDA/FLUX Hybrid PNG was fabricated by CPU CI and no publication-ready claim is made from this run.

## Remaining work

1. Run the current Golden Hybrid v5 Candidate 1 on a compatible CUDA/BF16 host and preserve all existing provenance/semantic/layer gates.
2. Review the real FLUX base and texture-preserving deterministic football integration before running Seeds 2–4.
3. Bind a concrete direct semantic-inspection receipt into `DirectSemanticPublicationGate` for direct-route automated execution; do not substitute a naked success flag.
4. Approve and SHA-lock the exact PUL7SAR brand geometry/logo/font assets before any final publication composition.
5. Keep the Golden Direct Visual as a separate non-generative benchmark; do not treat it as evidence that the FLUX Hybrid path is visually accepted.

## Change summary

- Added: `engine/intelligence/direct_publication.py`
- Added: `tests/test_phase18_direct_publication.py`
- Added: `docs/PHASE18_IMPLEMENTATION_LOG_119.md`
- Modified: `docs/PHASE18_IMPLEMENTATION_LOG_119.md` only to record the successful CI result
- Deleted: none
- `main`: untouched
