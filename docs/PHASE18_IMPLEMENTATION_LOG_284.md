# Phase 18 Implementation Log — CS284

## Baseline

- Working branch: `phase18/story-intelligence`
- Baseline SHA: `39ccc918ae993082a6297a96dd4bd902dfe66a80`
- Baseline CS283 `verify-story-intelligence`: completed / success.
- `main` was read only and was not modified, merged, rebased, or force-updated by this change set.

## Goal

Materially reduce the remaining gap to the first genuine Golden Visual by replacing the post-CS283 theoretical publication step with an executable, fail-closed adapter around the repository's existing `SemanticPublicationGate`.

## Added

1. `engine/intelligence/qwen_image_composed_candidate_semantic_publication_execution.py`
   - Re-verifies CS283.
   - Byte-binds the external execution-evidence JSON.
   - Reconstructs `GenerationPackage`, `BaseSceneEvidence`, and `VisionVerifierProfile`.
   - Executes `SemanticPublicationGate().evaluate(...)` directly.
   - Records the gate's actual `allowed`, base-scene, verifier, failure, and warning results.
   - Keeps Genuine-Golden and publication-ready authority closed.

2. `tests/test_phase18_qwen_image_composed_candidate_semantic_publication_execution.py`
   - Complete local zero-cost non-identity verifier can pass the gate.
   - Identity-required publication is blocked without identity-similarity capability.
   - Non-zero-cost verifier is blocked.
   - Identity mismatch is blocked even with complete verifier capability.
   - Unknown verifier capability is rejected.

3. `tools/phase18_execute_semantic_publication_gate.py`
   - Build/verify CLI only.
   - No `allowed`, approval, Golden, or publication override argument exists.

4. `docs/PHASE18_CHANGESET_284_SEMANTIC_PUBLICATION_EXECUTION.md`
   - Contract and authority-boundary documentation.

5. `docs/PHASE18_IMPLEMENTATION_LOG_284.md`
   - This implementation record.

## Modified

- No pre-existing production, policy, gate, workflow, or test file was modified.

## Deleted

- Nothing.

## Commits before this log

- `4c50b98ed79fafff9fcb1eb4e54e26ee6ce0360e` — CS284 execution engine.
- `6b78134d603c7fe86ec9144f90805e0cd347585c` — CS284 regressions.
- `5a0692f6dc410d8775cbabde1bde6ce7d024da05` — CS284 CLI.
- `8dc90fc4213dee640ce1cf5e7319b201763d97da` — CS284 contract documentation.

## Preserved gates

CS284 does not modify or bypass factual locks, entity/identity verification, sentiment neutrality and loser-respect rules, zero-cost constraints, Golden-quality adjudication, human visual review, exact brand/typography review, final composed approval, final semantic approval, or `SemanticPublicationGate` itself.

`semantic_publication_allowed` is not read from the external evidence. It is computed only by the repository gate after dataclass reconstruction.

Even a gate result of `allowed=true` is recorded with:

- `genuine_golden_png_created=false`
- `publication_ready=false`

## Testing state

Focused regression coverage was added in this change set. GitHub Actions is expected to execute automatically on the branch after commits. A terminal success is not claimed in this log until observed on the final CS284 SHA.

## Genuine Golden execution blocker

No genuine model inference or production PNG is claimed here. The current execution environment available to this automation does not expose a compatible NVIDIA CUDA/BF16 GPU runtime for genuine CS262 Qwen-Image inference. The remaining runtime blocker is a zero-cost host that simultaneously provides compatible CUDA, native BF16 support, sufficient live VRAM/system RAM, the pinned Qwen-Image revision, a compatible `QwenImagePipeline`, and the required sequential CPU offload behavior.

## Remaining path

1. Obtain genuine CS262 model inference on a compatible zero-cost GPU host.
2. Carry the real candidate through the existing byte/identity/semantic/composition/quality/human/brand/typography chain.
3. Produce real CS283 inputs for the exact production composed PNG.
4. Run CS284 with real generation-package/base-scene/verifier evidence.
5. Only if the repository gate returns `semantic_publication_allowed=true`, create a separate downstream authority that can bind and declare the already-existing exact PNG as the first Genuine Golden Visual.
6. Publication readiness remains a separate final authority after Genuine-Golden creation evidence.
