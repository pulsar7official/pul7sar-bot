# PUL7SAR Phase 18 — Change Set 144

## Golden Original Scene Runtime Admission

### Goal

Bind the provider-agnostic Original Scene runtime contract introduced in Change Set 143 to the real Golden Candidate 1 GPU path before any durable queue mutation.

The current Golden generator remains FLUX.2 Klein 4B under the existing `$0-local`, CUDA and native BF16 locks. This change does not replace the generator, weaken any gate, or claim a generated PNG. It proves that the measured local runtime is qualified to execute the same original-first visual concept before the canonical first-PNG command may proceed.

### Added

- `engine/intelligence/golden_original_scene_admission.py`
  - loads the integrity-hashed Candidate 1 handoff;
  - requires the v2 original-first Visual Concept contract and `generative_event_atmosphere` archetype;
  - requires the existing single-scene, no-generated-brand and no-generated-sport-geometry ownership metadata;
  - constructs the provider-neutral atmosphere request with exact text, score, crest, PUL7SAR identity and sport geometry reserved for deterministic composition;
  - invokes `OriginalSceneLocalBridge` using measured `LocalGenerationReadinessReport` evidence;
  - rejects provider/model/backend/request/seed/canvas drift between the admitted request and the locked Golden handoff;
  - records a SHA-256 of the compiled provider-neutral prompt without granting generation, semantic, Golden or publication authority.

- `tools/phase18_admit_golden_original_scene.py`
  - runs on the same local host intended for Candidate 1;
  - proves the exact FLUX backend/runtime readiness and native BF16 selection;
  - writes `output/phase18_gpu_smoke/original-scene-runtime-admission.json`;
  - performs no queue mutation and creates no PNG.

- `tools/phase18_first_png_original_scene.py`
  - new canonical wrapper for the next GPU session;
  - requires Original Scene admission first;
  - delegates only after admission to the existing `phase18_first_png.py`, preserving all repository, CUDA/BF16, Qwen, FLUX, provenance and publication gates;
  - does not import or mutate `FilesystemGenerationJobStore` itself.

- `tests/test_phase18_golden_original_scene_admission.py`
  - covers Candidate 1 admission, CPU/unready rejection, provider drift, Candidate drift, execution ordering and authority preservation.

### Modified

No existing runtime file was modified in this change set. The integration is additive so the established first-PNG/provenance path remains unchanged while the new provider-agnostic admission wrapper can be validated independently.

### Deleted

Nothing.

### Gates preserved

No change was made to Fact Lock, entity/identity verification, sentiment/neutrality, respectful losing-side treatment, `$0-local`, FLUX.2 Klein 4B, native BF16, seed/canvas locks, generated text/brand/exact-number/entity-mark/sport-geometry exclusions, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, artifact/provenance replay, human review, Golden 8.5 minimum / 9.0+ elite thresholds, exact brand/typography integrity, or SemanticPublicationGate.

The admission receipt is structurally unable to claim semantic approval, Golden approval or publication readiness.

### Remaining blocker

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA + BF16 host with the locked FLUX.2 Klein 4B and Qwen runtime. The current automation environment cannot execute that workload. No PNG, benchmark or visual-quality result is fabricated by this change set.

The preferred next GPU command is now:

```bash
PYTHONPATH=. python tools/phase18_first_png_original_scene.py
```

If runtime admission succeeds, the existing first-PNG pipeline continues with repository integrity, Qwen preflight, FLUX readiness, durable Candidate 1 execution and provenance postflight. Seeds 2–4 remain unauthorized until Candidate 1 is visually accepted.
