# PUL7SAR Phase 18 — Change Set 147

## Original Scene Admission Postflight Binding

### Purpose

Close a remaining evidence gap in the preferred Candidate 1 entrypoint. The Original Scene runtime admission was already required before the canonical first-PNG path, but the wrapper did not prove that the persisted admission receipt remained byte-identical while the delegated GPU generation path executed.

### Changes

#### Modified

- `tools/phase18_first_png_original_scene.py`
  - constrains the admission receipt path to the repository;
  - loads and validates the persisted admission receipt before generation;
  - records its SHA-256 and byte size before delegating to `phase18_first_png.py`;
  - reloads and revalidates the same receipt after the delegated first-PNG path returns;
  - rejects payload drift, SHA drift, byte-size drift, missing evidence, invalid JSON or path escape;
  - emits `original_scene_admission_sha256`, `original_scene_admission_bytes` and `original_scene_admission_replayed=true` in the wrapper result.

- `tests/test_phase18_golden_original_scene_admission.py`
  - adds regression coverage for pre-generation SHA binding;
  - proves replay happens after `phase18_first_png.py`;
  - proves tampering during generation is fail-closed;
  - proves the admission receipt cannot escape the repository.

#### Added

- `docs/PHASE18_CHANGESET_147_ORIGINAL_SCENE_ADMISSION_POSTFLIGHT_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_147.md`

#### Deleted

Nothing.

### Gates preserved

No change was made to Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, FLUX.2 Klein 4B, native BF16, Candidate/request/seed/canvas/SHA locks, generated text/branding/exact-fact/entity-mark/sport-geometry exclusions, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, generation provenance replay, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, SemanticPublicationGate or final Publication Readiness.

### Why this materially reduces the remaining gap

The next genuine Candidate 1 GPU run now has a stronger chain of custody around the provider-neutral Original Scene admission itself. The measured runtime admission cannot silently change between admission and the first-PNG result while still being reported as valid by the wrapper.

This does not create a PNG on CPU and does not fabricate GPU success. A compatible NVIDIA CUDA + native BF16 host is still required for the genuine Golden Hybrid v5 Candidate 1 generation path.
