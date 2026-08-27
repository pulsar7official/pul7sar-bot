# Phase 18 Change Set 217 — Remote Renderer Benchmark Isolation

## Goal

Keep the newly introduced public Hugging Face ZeroGPU renderer comparison useful as a quality research tool without allowing it to bypass the canonical Phase 18 `$0-local` Golden path or leak protected platform identity into a renderer prompt.

## Problem found

The current branch added a development comparison tool for Qwen Image 2512 and FLUX.2 dev ZeroGPU Spaces plus a transfer benchmark prompt. The study was already marked `publication_ready=false`, but it still had several gaps relative to the stronger Phase 18 contracts:

1. the benchmark prompt contained the literal platform name `PUL7SAR`;
2. the remote tool did not hash the exact prompt that was sent;
3. returned image bytes were copied without PNG-signature verification or output SHA-256 evidence;
4. the result did not explicitly distinguish this remote study from the canonical `$0-local` Golden path;
5. the result did not explicitly close Semantic and Golden authority;
6. there were no Phase 18 regression tests preventing future platform-name leakage or accidental promotion of remote-study outputs.

## Implemented

### Hardened `tools/phase18_remote_renderer_compare.py`

The tool now uses contract `pul7sar-phase18-remote-renderer-benchmark-v2` and declares the study cost mode as `$0-remote-zerogpu-study`.

It is explicitly non-canonical:

- `engineering_benchmark_only=true`;
- `canonical_golden_eligible=false`;
- `semantic_approved=false`;
- `golden_quality_approved=false`;
- `publication_ready=false`;
- `human_visual_review_required=true`.

The canonical `$0-local` path is not modified.

Prompt validation now fails closed if `PUL7SAR` or `PULSAR` reaches the remote renderer. The benchmark also requires markers preserving anonymous identity, one continuous scene, no readable text, no club crest, and no sponsor mark.

The exact renderer prompt is SHA-256 bound before remote execution. Each returned artifact must have a real PNG signature and is recorded with output SHA-256 and byte size.

### Updated transfer benchmark prompt

`benchmarks/phase18/savinho_transfer_renderer_benchmark_prompt.txt` no longer contains the platform name. The reserved area is described generically as space for later deterministic brand and headline composition.

The anonymous-person, no-readable-text, no-crest, no-sponsor, single-scene, and geometry-safety instructions remain.

### Added regression coverage

`tests/test_phase18_remote_renderer_benchmark.py` verifies:

- the checked-in benchmark prompt is platform-name free and identity neutral;
- platform-name leakage fails closed;
- missing required safety markers fail closed;
- copied remote outputs must be PNG bytes;
- image evidence is SHA-256 bound;
- reports can never claim canonical Golden, Semantic, or Publication authority;
- the remote study remains distinct from the canonical `$0-local` path.

## Files

### Modified

- `tools/phase18_remote_renderer_compare.py`
- `benchmarks/phase18/savinho_transfer_renderer_benchmark_prompt.txt`

### Added

- `tests/test_phase18_remote_renderer_benchmark.py`
- `docs/PHASE18_CHANGESET_217_REMOTE_RENDERER_BENCHMARK_ISOLATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_217.md`

### Deleted

- None.

## Gate preservation

Unchanged and still fail-closed in the canonical Golden path:

- factual integrity / Fact Lock;
- Entity and Identity Verification;
- sentiment / neutrality and loser-respect policy;
- canonical `$0-local` execution policy;
- model/runtime qualification and provenance;
- generated branding/text/exact facts/entity marks/exact sport geometry prohibitions;
- Semantic and Layer Ownership gates;
- Visual Critic hard failures;
- explicit Human Review;
- Golden minimum `8.5`, elite target `9.0+`;
- Exact Brand and Typography Integrity;
- SemanticPublicationGate and final publication readiness.

Remote ZeroGPU outputs are research evidence only and cannot be substituted for an accepted Genuine Golden Visual.
