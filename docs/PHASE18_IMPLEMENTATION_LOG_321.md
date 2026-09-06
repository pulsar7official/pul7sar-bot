# Phase 18 Implementation Log 321 — Bound Composition Execution and Admission

## Baseline and branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Required write branch: `phase18/story-intelligence`
- Starting Phase 18 HEAD reviewed before writes: `bc176bbbbda1ea1f143ef979d732fb4e4f1cfae4`
- Starting `main` observed read-only: `89b69e0972047af615162518dcc32dc1a16cd2dd`
- No write, merge, rebase, reset, force-update, or branch movement was performed on `main`.

The reviewed baseline was CS320. CS320 already proves that the actual CS271 `compose_fn` originates from the exact repository-byte-bound runner source and records the top-level runner entrypoint.

## Gap identified

CS270, CS271, and CS272 were individually strong, but execution still required a manual junction:

1. choose/load the explicit project-native renderer;
2. call CS271;
3. locate the resulting CS271 receipt;
4. call CS272 with the correct receipt.

That did not weaken the existing verifiers, but it left avoidable operator-selection risk immediately before post-composition QA. A genuine expensive/rare upstream inference should not depend on a manual receipt handoff once the exact renderer and CS270 inputs are explicitly known.

The safe fix is orchestration only. It must not invent a renderer or layer payloads.

## Added

### `tools/phase18_execute_bound_composition_and_admit.py`

Adds a fail-closed execution/admission checkpoint that requires:

- an exact repository-local CS270 receipt;
- an exact repository-local Python runner source;
- an explicit top-level entrypoint;
- an explicit runner ID;
- a fresh repository-local output directory.

Behavior:

1. rejects runner/receipt/output paths outside the repository and runner symlinks;
2. loads only the explicit named entrypoint from the explicit runner source;
3. sets Hugging Face, Transformers, and Datasets offline flags before runner import/execution;
4. calls existing CS271 one-shot composition execution;
5. independently replays CS271;
6. requires CS271 `composition_executed=true` while downstream visual/semantic/human/Golden/publication authorities remain false;
7. passes that exact CS271 receipt path directly into CS272;
8. independently replays CS272;
9. requires CS272 exact-byte admission authority only;
10. checks story SHA, source-candidate binding, and composed-candidate binding across CS271 → CS272;
11. writes a non-authoritative checkpoint recording only execution + byte-admission readiness for post-composition QA.

The checkpoint does not create composition manifests, deterministic payloads, editorial text, logos, geometry, score data, or any other visual layer.

### `tests/test_phase18_bound_composition_execution_and_admission.py`

Coverage added for:

- exact repository-local runner entrypoint loading;
- missing entrypoint rejection;
- outside-repository runner rejection;
- exact CS271 output feeding CS272 directly;
- preservation of all downstream false authorities;
- story/source/composed lineage drift fail-closed assertions;
- no QwenImagePipeline invocation or publication-authority code in the new orchestration path.

Synthetic/mocked bindings in the unit test are control-plane fixtures only and are not represented as Qwen output or Golden Visual evidence.

### Documentation

Added:

- `docs/PHASE18_CHANGESET_321_BOUND_COMPOSITION_EXECUTION_AND_ADMISSION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_321.md`

## Modified

No pre-existing production gate, renderer, factual policy, identity policy, sentiment policy, zero-cost policy, semantic QA, composition verifier, visual-quality threshold, Golden gate, brand/typography policy, or publication authority was modified.

## Deleted

None.

## Commits

- `a0e8ee657ca2289a7ade9daa8332acae7a1a7230` — add bound CS270 → CS271 → CS272 execution/admission checkpoint.
- `fe7e1eec0eae65563aaaa3112d4c1604cc5da3f5` — add CS321 regression coverage.
- `dead92d6558957ab6679f7bece2a442cf825c439` — document CS321 contract.
- implementation-log commit — this file.

## Preserved gates

CS321 does not weaken or replace:

- Fact/Freshness verification;
- Entity/Identity verification;
- manual source comparison when pixel identity requires it;
- sentiment neutrality and loser-respect;
- `$0-local` generation policy;
- Semantic Base QA;
- Generated-Layer QA;
- deterministic composition layer ownership;
- CS270 deterministic-payload binding;
- CS271 one-shot/callable provenance;
- CS272 exact-byte admission;
- post-composition semantic/layer QA;
- Golden Visual Quality;
- Human Visual Review;
- exact brand/typography approval;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- CS285 Genuine Golden materialization;
- CS286 publication readiness.

After successful CS321 orchestration, these remain false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

## Test status

The new source and test files were syntax-compiled locally before repository writes. GitHub Actions for the final CS321 HEAD must reach terminal `completed/success` before CS321 is recorded as terminal-green.

## GPU/runtime blocker

No genuine Qwen inference or production PNG is claimed by CS321. The current execution environment still lacks the compatible upstream zero-cost GPU runtime required for Qwen-Image generation: NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM, the exact approved already-local pinned `Qwen/Qwen-Image-2512` snapshot/runtime, and the pinned local semantic-verifier assets.

CS321 is CPU/control-plane preparation only. It materially reduces the post-CS270 operator gap but does not fabricate a renderer, candidate PNG, composed production PNG, quality score, or Golden Visual.

## Remaining path

`genuine Qwen inference → exact candidate admission/semantic/identity/generated-layer gates → CS269/CS270 → explicit project-native deterministic renderer → CS321 (CS271 execution + CS272 exact-byte admission) → post-composition QA → Golden quality → Human Visual Review → exact Brand/Typography → Final Composed Approval → Final Semantic Approval → SemanticPublicationGate → CS285 Genuine Golden PNG → CS286 readiness`.
