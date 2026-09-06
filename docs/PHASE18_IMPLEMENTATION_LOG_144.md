# PUL7SAR Phase 18 — Implementation Log 144

## Scope and branch state

Branch: `phase18/story-intelligence` only.

Starting Phase 18 head reviewed for this automation turn: `a649c0ce88f0dfe1572d69b29f00ede17a145eab`.
Observed `main` head: `65344bd7cbcea9b162df2847a89672850ff5ab85`.

`main` was not modified, merged, force-updated, or used as a write target. The branch remained `diverged`; after the Change Set 144 code/test/documentation work the comparison was 1327 commits ahead and 127 commits behind `main`.

The starting branch already contained Change Set 143 and its provider-agnostic Original Scene request/runtime bridge. The documented next safe step was to bind that seam to the real Candidate 1 GPU path after measured local readiness and before queue mutation.

## Change Set 144 — Golden Original Scene Runtime Admission

### Problem addressed

The provider-neutral `OriginalSceneRequest` and measured `$0-local` runtime bridge existed, but the canonical Golden Candidate 1 generation path could still proceed directly through the older first-PNG orchestration without first proving that the selected local runtime was admitted for the same original-first visual concept.

That left the architectural seam correct in isolation but not yet enforced in the path that will create the first genuine Golden PNG.

### Added

- `engine/intelligence/golden_original_scene_admission.py`
  - reloads the integrity-hashed Candidate 1 handoff;
  - locks Candidate 1, request ID, payload SHA, provider, model, backend, seed and canvas;
  - requires the current `pul7sar-visual-concept-director-v2-original-first` contract and `generative_event_atmosphere` archetype;
  - preserves single-scene composition and deterministic ownership of platform identity, readable text, exact score, club crest and sport geometry;
  - invokes `OriginalSceneLocalBridge` against measured local readiness;
  - rejects compiled provider/model/backend/request/seed/canvas drift;
  - records a SHA-256 of the admitted provider-neutral prompt without exposing it as publication authority.

- `tools/phase18_admit_golden_original_scene.py`
  - probes the exact Diffusers FLUX backend and local hardware;
  - builds the existing `LocalGenerationReadinessReport` used by Phase 18;
  - requires native BF16 resolution before admission;
  - writes `output/phase18_gpu_smoke/original-scene-runtime-admission.json`;
  - explicitly records that no queue mutation, PNG creation, semantic approval, Golden approval or publication approval occurred.

- `tools/phase18_first_png_original_scene.py`
  - new preferred Candidate 1 entrypoint;
  - executes Original Scene runtime admission first;
  - only after successful admission delegates to the already hardened `phase18_first_png.py` path;
  - therefore preserves repository integrity, CUDA/BF16 qualification, Qwen preflight, FLUX cache/readiness, durable job execution and provenance postflight rather than duplicating them;
  - contains no direct durable-queue mutation.

- `tests/test_phase18_golden_original_scene_admission.py`
  - verifies successful Candidate 1 admission on matching CUDA readiness;
  - rejects Candidate-number drift;
  - rejects CPU/unready runtime evidence;
  - rejects provider drift;
  - verifies admission is ordered before canonical first-PNG delegation;
  - verifies the wrapper cannot grant semantic, Golden or publication authority.

- `docs/PHASE18_CHANGESET_144_GOLDEN_ORIGINAL_SCENE_ADMISSION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_144.md`

### Modified

No existing production or generation runtime file was modified. Change Set 144 is additive: the established first-PNG path remains intact, while the new preferred wrapper gates entry through provider-neutral Original Scene admission.

### Deleted

Nothing.

## Gate preservation

The following remain unchanged and fail-closed:

- Fact Lock;
- entity/identity verification;
- sentiment/neutrality and respectful losing-side treatment;
- `$0-local` economics;
- FLUX.2 Klein 4B lock for the current Golden path;
- native BF16 requirement;
- Candidate/seed/canvas and handoff SHA locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE semantic/layer-ownership inspection;
- deterministic football geometry and artifact-integrity replay;
- Qwen HYBRID_SURFACE semantic/alignment inspection;
- provenance/evidence replay;
- SHA-bound human review;
- Golden 8.5 minimum / 9.0+ elite quality thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

No paid provider, hosted GPU fallback, secret, precision downgrade, fake PNG, fake benchmark or publication bypass was introduced.

## Testing status

The Change Set 144 code/test head `f36dfb54f4c9f42b3a971bb1ff6b288baf237774` completed GitHub Actions successfully in **Phase 18 Story Intelligence Verification run `32829227736 / 2506`**. Syntax/discover validation, completion/production isolation, visual-study handoffs, self-contained brand integrity and Golden Hybrid v5 build/verification all completed successfully. All companion Phase 18 CPU workflows visible for the same head also completed with `success`.

The final implementation-log-only commit does not change tested runtime behavior.

## Remaining blocker to the first genuine Golden Visual PNG

The exact external blocker remains execution capability: a genuine Candidate 1 needs a compatible NVIDIA CUDA + native BF16 host that can run the locked FLUX.2 Klein 4B path and the local Qwen semantic stages.

The current automation environment has no such GPU execution capability. No PNG, benchmark or visual-quality result was fabricated.

The preferred next GPU entrypoint is now:

```bash
PYTHONPATH=. python tools/phase18_first_png_original_scene.py
```

The intended chain is now:

`Repository/Golden integrity → measured Original Scene runtime admission → CUDA/BF16 + Qwen + FLUX readiness → Candidate 1 → provenance postflight → BASE_SCENE ownership QA → deterministic football geometry → HYBRID_SURFACE QA → SHA-bound human review → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`.

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted. The authoritative final PUL7SAR logo/typography asset SHA lock also remains a separate blocker before Final Publication Composition.
