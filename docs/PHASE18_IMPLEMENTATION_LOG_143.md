# PUL7SAR Phase 18 — Implementation Log 143

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed before implementation and was not modified, merged, force-updated, or used as a write target.

Observed starting Phase 18 head for this automation turn: `3698fa5f3734da42708505036d88befad05b45a1`.
Observed `main` head during the turn: `65344bd7cbcea9b162df2847a89672850ff5ab85`.
The branch comparison remained `diverged`; after the code/test work it was ahead by 1305 commits and behind by 127 commits.

The starting head already contained the first provider-agnostic original-scene request builder tests. This change set consolidates that work into a measured local-runtime bridge rather than creating another image-provider-specific architecture.

## Change Set 143 — Original Scene Runtime Bridge

### Problem addressed

Change Set 142 successfully carried the story-specific Visual Concept into the provider-neutral Generation Package and FLUX portable handoff. A newer provider-agnostic seam then introduced `OriginalSceneRequest`, runtime qualification and fail-closed admission contracts, but those contracts were not yet connected to the existing measured `$0-local` runtime/readiness stack.

Without that connection, a future image model could be described abstractly but not admitted using the same runtime evidence already used by Phase 18, while the current FLUX path would remain a separate special case.

### Added

- `engine/intelligence/original_scene_runtime_contract.py`
- `engine/intelligence/original_scene_execution_gate.py`
- `engine/intelligence/original_scene_request_builder.py`
- `engine/intelligence/original_scene_local_bridge.py`
- `tests/test_phase18_original_scene_runtime_contract.py`
- `tests/test_phase18_original_scene_execution_gate.py`
- `tests/test_phase18_original_scene_request_builder.py`
- `tests/test_phase18_original_scene_local_bridge.py`
- `docs/PHASE18_CHANGESET_143_ORIGINAL_SCENE_RUNTIME_BRIDGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_143.md`

Some of the original-scene contract/builder files were already present on the branch at the beginning of this turn; they are listed here because Change Set 143 is the first implementation log that formally records that seam and its local-runtime integration.

### Modified

No existing production runtime, publication runtime, Golden quality gate, semantic gate, Fact Lock, identity gate or `main` file was modified by the new local bridge work in this turn.

### Deleted

Nothing.

## Runtime bridge behavior

`OriginalSceneLocalRuntimeQualifier` derives a qualification from a concrete `LocalModelCandidate` and `LocalGenerationReadinessReport`.

Qualification requires:

- readiness is actually `ready`;
- provider and model identities match the selected model;
- `$0-local` cost mode;
- a proven local runtime floor;
- a `local_cuda` runtime;
- a runtime role compatible with the requested original-scene kind.

Current FLUX.2 Klein 4B may qualify for atmosphere synthesis when the measured CUDA readiness report is valid. It is not silently elevated into an identity-conditioned runtime under the present `ENGINEERING_FALLBACK` model-role contract.

`OriginalSceneLocalBridge` then reuses the existing `PromptConstraintCompiler` and `DevelopmentCostPolicy` rather than inventing a parallel prompting/economics layer. Unknown forbidden visual claims fail closed instead of being dropped. The compiled request keeps branding, exact facts and sport geometry outside generation and requires downstream semantic inspection.

Neither admission nor compilation can set publication readiness true.

## Tests added

Regression coverage now verifies:

- missing and unqualified runtime rejection;
- measured CUDA atmosphere qualification;
- CPU/unready rejection;
- runtime-kind mismatch;
- no automatic identity-conditioned promotion of FLUX.2 Klein;
- `$0-local` local request compilation;
- no protected platform name in the generation prompt;
- generated brand/exact-fact/sport-geometry authority remains false;
- readiness provider/model drift rejection;
- unknown forbidden claims cannot be silently dropped.

## Safety and publication gates preserved

No weakening or bypass was introduced for:

- Fact Lock;
- entity/identity verification;
- sentiment/neutrality and respectful losing-side treatment;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock for the current Golden path;
- native BF16 lock;
- Candidate/seed/canvas locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE semantic/layer ownership gate;
- deterministic football geometry and artifact-integrity replay;
- Qwen HYBRID_SURFACE semantic/alignment gate;
- human-review SHA locks;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

No paid provider, hosted GPU fallback, secret, fake PNG, fake benchmark or publication bypass was added.

## Testing status

The code and regression tests were pushed to `phase18/story-intelligence` and GitHub Actions was triggered automatically.

This log intentionally does not claim the final Change Set 143 head is CI-green until the Story Intelligence verification run for that head completes successfully.

## Remaining blocker to the first genuine Golden Visual PNG

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA + BF16 host capable of running the locked FLUX.2 Klein 4B path and the Qwen semantic stages.

The current automation environment does not provide that execution capability. No PNG, benchmark or visual-quality result was fabricated.

The next safe integration step is to invoke the new original-scene runtime admission seam inside the real Candidate 1 GPU path immediately after local readiness evidence is available. That will make the Golden path consume the same provider-agnostic scene contract that future qualified local runtimes can use, while preserving the existing provenance, semantic, deterministic-geometry, human-review and Golden-quality chain.
