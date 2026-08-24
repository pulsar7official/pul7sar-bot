# PUL7SAR Phase 18 — Implementation Log Continuation 110

This file is the authoritative continuation record for Change Set 110 on `phase18/story-intelligence`. No production branch is modified.

## Branch review before change
- Repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence` only.
- PR #1 was observed open, Draft and unmerged before the change.
- Observed pre-change head: `4dc38472ad5f30c81649f4b67de3846a4c05f1c7`.
- Observed PR base branch: `main`; observed base SHA: `bfa90a54429ea0610bb07ecac072cbaa0461dda1`.
- `main` / `main.py` were not used as write targets.
- No genuine new Golden Hybrid v5 GPU PNG is claimed in this run.

## Prior state reviewed
- Change Set 109 propagated provider-agnostic `VisualGrammar` through `StoryToVisualOrchestrator` and `GenerationPackageCompiler`.
- Review of `tools/phase18_build_golden_handoff.py` showed that the active Golden Hybrid v5 benchmark still built its scene from a hand-authored full-stadium/reserved-pitch concept without passing `VisualGrammar` into the generation package.
- `SceneComplexityPolicy` classifies `EditorialEvent.PREVIEW` as `partial_deterministic`, so the benchmark and the general story path could diverge exactly at the point we need the Golden proof to validate the current architecture.

## Change Set 110 — Golden Hybrid v5 VisualGrammar Alignment

### Added
- `docs/PHASE18_CHANGESET_110_GOLDEN_VISUAL_GRAMMAR_ALIGNMENT.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_110.md`.
- Golden benchmark propagation of `VisualGrammarDecision`.
- Golden request metadata for `pul7sar-visual-grammar-v1`, provider-agnostic state, `partial_deterministic` surface visibility and restrained fantasy.
- Golden batch manifest fields for VisualGrammar contract/surface visibility.
- Cross-seed drift detection for Golden VisualGrammar metadata.
- Regression assertions that the actual Golden prompt uses restrained partial surface context and explicitly avoids making a full pitch the visual subject.
- A local-backend regression assertion proving the provider-neutral VisualGrammar metadata survives into the locked local generation request.

### Modified
- `tools/phase18_build_golden_handoff.py`
  - imports `VisualGrammar`;
  - derives grammar from the approved season-opener editorial plan;
  - passes the grammar into `GenerationPackageCompiler`;
  - changes hand-authored scene direction from broad/full pitch dependency to restrained partial turf context;
  - records the grammar contract/surface visibility in scene metadata and CLI output.
- `tools/phase18_build_golden_batch.py`
  - records the VisualGrammar contract and surface visibility in the manifest;
  - records surface visibility per candidate;
  - fails if candidate grammar metadata drifts across seeds.
- `engine/intelligence/provider_prompting.py`
  - adds deterministic positive translation for the new `reserved surface context` wording;
  - preserves fail-closed behavior for unknown constraints instead of dropping them.
- `engine/intelligence/local_backend_execution.py`
  - preserves provider-agnostic VisualGrammar contract, surface visibility, camera/fantasy metadata and generated/deterministic/forbidden element ownership in the local request metadata.
- `tests/test_phase18_golden_handoff.py`
  - verifies provider-agnostic VisualGrammar metadata and `partial_deterministic` preview behavior;
  - verifies prompt restraint against a full-pitch visual dependency.
- `tests/test_phase18_golden_batch.py`
  - verifies manifest/candidate grammar stability and the restrained partial-surface prompt.
- `tests/test_phase18_local_backend_execution.py`
  - explicitly verifies VisualGrammar metadata survives `GenerationPackage -> LocalBackendGenerationRequest` without provider-specific reinterpretation.

### Deleted
- Nothing.

## CI / regression history during Change Set 110
- Change Set 109 code/test head `675e05da546111b61733416ffa23a43b6ab24142` previously completed GitHub Actions Run `32708563566` with `success`.
- First Change Set 110 attempt triggered Run `32713972400` / run 1518 and failed. The failure was correct fail-closed behavior: the new constraint wording `no football pitch markings in the reserved surface context` had no deterministic positive reframe for FLUX-like providers. The constraint was not removed; `PromptConstraintCompiler` was extended with the equivalent safe translation.
- The next attempt on `5989199291fb0c67473bd81dc6a4e98d9c88c565` triggered Run `32714080186` / run 1520 and failed with 23 errors. The root cause was not the VisualGrammar decision itself: `GenerationPackage.metadata` contained the grammar fields, but `LocalBackendRequestCompiler` did not preserve them in the locked request. Golden batch/smoke/verifier tests correctly failed rather than infer missing metadata.
- Commit `d06807140a463943ea44cfc4581abe9e7dddda32` fixed the backend boundary by preserving the VisualGrammar metadata in the local handoff.
- GitHub Actions Run `32714229033` / run 1526 completed with `success` for commit `d06807140a463943ea44cfc4581abe9e7dddda32`.
- A further explicit local-backend regression test was added after that success so this exact metadata boundary cannot regress silently. Any CI run produced by the later test/documentation commits must be observed independently before attributing success to the final documentation head.
- CPU CI did not fabricate or claim a GPU visual proof.

## Why this advances the first genuine Golden Visual
The active Candidate 1 handoff now exercises the same story-specific provider-agnostic visual grammar as the normal Phase 18 pipeline. The next GPU proof therefore tests the current architecture rather than an older benchmark-only scene assumption. For the preview benchmark, FLUX can still create premium stadium atmosphere, but the generated surface is explicitly limited to restrained context while exact geometry remains deterministic and downstream.

Current intended path:
`Verified story -> editorial plan -> VisualGrammar -> provider-neutral GenerationPackage -> zero-cost FLUX.2 Klein -> provenance acceptance -> semantic/layer QA -> deterministic exact layers only when required -> receipt-backed hybrid QA -> pitch review/SHA lock -> Qwen HYBRID_SURFACE -> SHA-bound Golden 8.5/9.0 review -> exact approved brand/typography -> SemanticPublicationGate -> publication readiness`.

## Gates and invariants unchanged
- `main` / `main.py`: untouched.
- Telegram and legacy production publishing: untouched.
- Fact Lock: unchanged and fail-closed.
- Identity verification: unchanged and fail-closed.
- Sentiment / result neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B, BF16, seeds/canvases and generation controls: unchanged.
- Generated football geometry remains forbidden.
- Base semantic layer ownership remains mandatory.
- Qwen semantic inspection remains mandatory for publication-grade flow.
- SemanticPublicationGate remains mandatory.
- Golden thresholds remain 8.5 minimum / 9.0+ elite; hard blockers override score.
- Generated PUL7SAR branding remains forbidden.
- Exact PUL7SAR logo/brand/typography integrity remains a separate downstream requirement.
- No paid provider, secret, model weights, font files, fake PNG, fabricated benchmark or fabricated review score was added.

## Remaining work
1. Observe CI for the final Change Set 110 regression/documentation head and repair any failure without weakening gates.
2. Obtain a compatible CUDA/BF16 host and generate genuine Golden Hybrid v5 Candidate 1 using the now-aligned VisualGrammar handoff.
3. Require generation-provenance acceptance and semantic/layer ownership on the exact produced bytes.
4. For the preview benchmark, verify that surface context remains visually restrained and does not become the generated hero.
5. Apply deterministic football geometry only after base-scene approval and inspect integration on the exact bytes.
6. Require receipt-backed HybridVisualEvidence / HybridVisualQualityGate on the exact composed bytes.
7. Complete pitch review/SHA lock, Qwen HYBRID_SURFACE inspection and SHA-bound Golden visual review.
8. Resolve and SHA-lock the approved PUL7SAR logo/brand geometry/font assets before publication composition.
9. Run exact brand/typography composition, SemanticPublicationGate and final publication-readiness checks; no earlier stage can waive them.
