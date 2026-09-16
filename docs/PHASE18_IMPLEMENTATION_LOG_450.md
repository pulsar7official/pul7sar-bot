# Phase 18 Implementation Log — CS450

## Scope

CS450 resolves the exact CPU verification regression exposed by the CS449 deterministic diagnostic artifact. The repair is test-contract-only: no production generation workflow, model runtime, publication path, or visual-quality authority was weakened or changed.

## Branch isolation

- Target branch: `phase18/story-intelligence` only.
- `main` was reviewed read-only and was not modified.
- Starting Phase 18 HEAD reviewed before this change: `edb49c4fbd5ee54a4853bf92826feca7526d0f41`.
- `Phase 18 Story Intelligence Verification` push run `34772923530` and PR run `34772926168` were both terminal-red on that SHA.
- The CS449 CPU diagnostic run `34772926183` successfully executed the validator, uploaded its report artifact, and then re-failed intentionally to preserve validator failure semantics.

## Diagnostic result

The retained CS449 report is conclusive:

- Python compilation passed.
- Phase 18 unittest discovery executed 2,428 tests.
- Exactly one test errored.
- Failing test: `test_workflow_replays_bound_model_cache_runtime_staging_and_keeps_authority_closed` in `tests/test_phase18_first_genuine_golden_v6_workflow.py`.
- Error: the regression test searched for the pre-CS445 workflow step name `Run model-cache resource runtime semantic locked strict Golden Editorial v6 Candidate 1`.
- The canonical workflow correctly uses the stronger current step name `Run attested canonical model-cache resource runtime semantic locked strict Golden Editorial v6 Candidate 1` and delegates through `tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`.

This was therefore a stale regression-test expectation, not a factual, identity, sentiment, semantic-publication, GPU, or generation-gate failure.

## Modified

### `tests/test_phase18_first_genuine_golden_v6_workflow.py`

- Replaced the stale pre-attestation workflow step-name expectation with the current canonical attested step name.
- Preserved ordering assertions requiring canonical execution before evidence replay and evidence replay before upload.
- Added an explicit assertion that the workflow invokes `phase18_run_first_genuine_golden_v6_canonical_attested.py`.
- Added an explicit assertion that the canonical launcher remains bound to the immutable dispatch SHA through `--expected-commit "$DISPATCH_SHA"`.
- Did not remove any model-cache, semantic-runtime, resource-lock, evidence-replay, quality, publication, or Seeds 2–4 closure assertions.

## Added

### `docs/PHASE18_IMPLEMENTATION_LOG_450.md`

This implementation log records the retained diagnostic evidence, exact regression cause, repair scope, preserved gates, and remaining path to the first genuine Golden PNG.

## Deleted

None.

## Production code/workflow changes

None.

CS450 intentionally does not modify `.github/workflows/phase18-first-genuine-golden-v6.yml`; the current attested canonical workflow is the desired stronger production contract and the stale test was repaired around it.

## Safety and quality gates preserved

CS450 does not modify or relax:

- factual verification and fact locks;
- real-person/entity identity verification;
- sentiment and loser-respect constraints;
- `$0-local` execution policy;
- `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` requirements;
- no-network model-download policy;
- native BF16 requirement and FP16/FP32 substitution refusal;
- exact approved Qwen2.5-VL and FLUX.2 model identities/revisions;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or composition parameters;
- semantic-publication gates;
- visual-quality and Human Review gates;
- canonical/JIT/offload attested pre-GPU contracts;
- publication authority;
- Seeds 2–4 authority;
- `main`.

## Why this materially reduces the Golden PNG gap

The branch no longer needs speculative CPU repairs: CS449 identified one exact stale assertion among 2,428 tests, and CS450 aligns that assertion with the already-hardened canonical attested workflow. Once central verification confirms this repair, the remaining blocker is no longer CPU orchestration; it is compatible authoritative CUDA execution under the existing zero-cost and offline-only constraints.

## Remaining blockers

1. Obtain terminal-green central Phase 18 verification on the CS450 HEAD.
2. Execute the already-attested canonical/JIT/offload path on a compatible self-hosted NVIDIA host with CUDA-enabled PyTorch, at least one real CUDA device, native BF16, approved GPU/compute capability, sufficient live VRAM, RAM and filesystem/cache headroom, coherent Qwen2.5-VL semantic runtime, compatible generation runtime, and exact approved local Qwen2.5-VL and FLUX.2 snapshots.
3. Preserve `$0-local`, offline-only resolution, no network model downloads, and no FP16/FP32 quality substitution.
4. Accept a Candidate 1 PNG only if all factual, identity, sentiment, semantic, provenance, resource, visual-quality, and Human Review gates pass. Publication remains separately gated.

## Golden Visual status

No genuine Golden Visual PNG was created or claimed in CS450.
