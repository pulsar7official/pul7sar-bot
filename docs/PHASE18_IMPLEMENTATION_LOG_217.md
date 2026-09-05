# Phase 18 Implementation Log — Change Set 217

## Branch isolation

- Target branch: `phase18/story-intelligence` only.
- Branch state reviewed before writing.
- Phase 18 HEAD observed before this Change Set: `83019fdfe9fe19c67e384e247c65c6fd2eee59e7`.
- `main` observed at `813ef31d2647e4353ca604e60e48975c79d7d95e`.
- Compare state: `diverged`; Phase 18 was ahead by 1815 commits and behind by 208 at the review point.
- No merge, force-update, or write targeted `main` or `main.py`.
- Baseline HEAD `83019fd...` was green in Story Intelligence Verification Run `33106063414 / 3516`; companion Phase 18 workflows shown for the same HEAD were also successful.

## Current branch development found before Change Set 217

Two unlogged development additions were present after Change Set 216:

1. `tools/phase18_remote_renderer_compare.py` comparing the public ZeroGPU Spaces `Qwen/Qwen-Image-2512` and `black-forest-labs/FLUX.2-dev`;
2. `benchmarks/phase18/savinho_transfer_renderer_benchmark_prompt.txt` for a transfer-oriented renderer quality study.

These additions can materially reduce renderer-selection uncertainty while a compatible canonical local GPU host is unavailable, but the initial version was not sufficiently isolated from the stronger Phase 18 Golden contracts.

## Problem found

The transfer benchmark prompt contained the literal platform name `PUL7SAR`, despite the current Dynamic Visual Brain renderer-safe policy keeping platform identity outside generation.

The remote tool also lacked prompt SHA evidence, output PNG signature/SHA evidence, explicit Semantic/Golden authority closure, and an explicit contract preventing its remote outputs from being mistaken for canonical `$0-local` Golden evidence.

## Implemented

### Modified `tools/phase18_remote_renderer_compare.py`

- Added schema `pul7sar-phase18-remote-renderer-benchmark-v2`.
- Added explicit study cost mode `$0-remote-zerogpu-study`.
- Added fail-closed platform-name scan for `PUL7SAR` / `PULSAR`.
- Added required prompt markers for anonymous identity, one continuous scene, no readable text, no club crest, and no sponsor mark.
- Added SHA-256 binding for the exact prompt sent to the renderer.
- Added PNG signature verification for returned image bytes.
- Added output SHA-256 and byte-size evidence.
- Added explicit authority closure:
  - `engineering_benchmark_only=true`;
  - `canonical_golden_eligible=false`;
  - `semantic_approved=false`;
  - `golden_quality_approved=false`;
  - `publication_ready=false`.

No canonical generation/runtime gate was modified.

### Modified transfer benchmark prompt

Removed the literal platform name and replaced it with generic later deterministic brand/headline composition language. Identity-neutral and renderer-safety constraints remain.

### Added `tests/test_phase18_remote_renderer_benchmark.py`

Regression coverage now verifies:

- platform-name-free benchmark prompt;
- platform-name leakage rejection;
- safety marker rejection;
- PNG signature enforcement;
- SHA-bound output evidence;
- permanent closure of canonical Golden/Semantic/Publication authority;
- distinction between the remote study and canonical `$0-local` execution.

### Added documentation

- `docs/PHASE18_CHANGESET_217_REMOTE_RENDERER_BENCHMARK_ISOLATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_217.md`

## Files changed

### Modified

- `tools/phase18_remote_renderer_compare.py`
- `benchmarks/phase18/savinho_transfer_renderer_benchmark_prompt.txt`

### Added

- `tests/test_phase18_remote_renderer_benchmark.py`
- `docs/PHASE18_CHANGESET_217_REMOTE_RENDERER_BENCHMARK_ISOLATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_217.md`

### Deleted

- None.

## Safety and gate preservation

Unchanged and still fail-closed in the canonical path:

- Fact Lock / factual integrity;
- Entity and Identity Verification;
- sentiment / neutrality and loser-respect policy;
- canonical `$0-local` execution;
- pinned/qualified model and runtime policies;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Semantic and Layer Ownership gates;
- Visual Critic hard failures;
- explicit Human Review;
- Golden minimum `8.5`, elite target `9.0+`;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate and final publication readiness.

The new remote path is explicitly research-only. It cannot provide canonical Golden provenance or publication authority.

## Validation status

Change Set 217 code/tests/documentation have been committed to `phase18/story-intelligence`.

GitHub Actions must complete on the resulting HEAD before Change Set 217 is described as CI-green. No GPU or remote renderer result is inferred from CPU CI.

## Genuine Golden Visual status

No new Accepted Genuine Golden Visual PNG was fabricated or claimed in this Change Set.

The repository already contains genuine rejected visual evidence. The active target remains the first accepted Genuine Golden Visual.

The current execution environment still lacks an approved compatible canonical `$0-local` GPU host satisfying CUDA/precision/VRAM/RAM/offload/model/runtime evidence for a new canonical candidate.

The new remote ZeroGPU comparison may be used only to learn which renderer style/capability is promising. Its outputs remain non-canonical engineering studies and cannot replace the canonical Golden path.

## Remaining gap / next safe step

1. Let CI verify Change Set 217.
2. If a compatible canonical `$0-local` GPU host becomes available, execute the sealed Dynamic Visual Brain durable job and keep the existing queue-to-critic/ledger provenance chain.
3. If only public ZeroGPU research execution is available, run the hardened renderer comparison only as a non-canonical study, then use its qualitative findings to improve the canonical renderer-safe concept/prompt contract without promoting the remote image itself.
4. Continue to require exact Human Review and Golden `8.5/9.0+` before any candidate can become accepted evidence.
