# Phase 18 Implementation Log 336

## Scope

Change Set 336 — Precomposition to Composed-Byte Admission.

Branch-only work: `phase18/story-intelligence`.

Starting branch HEAD reviewed before implementation:

`8b3235a187446d5b98fe453229b38eb4a5c30af2`

`main` was inspected read-only and was not modified, merged, rebased, reset, force-updated, or used as a write target during this Change Set.

## Why this change was needed

CS335 already proved the exact CS334 -> CS269 -> CS270 -> CS331 chain and stopped immediately before CS271. The remaining manual control-plane handoff was therefore the sensitive transition from precomposition readiness into the one-shot composition boundary and then into CS272 exact composed-byte admission.

CS336 removes that handoff without adding new authority. It invokes only the existing CS271 one-shot boundary with the existing CS330 production overlay runner, independently reverifies CS271, invokes existing CS272 on the exact CS271 receipt, independently reverifies CS272, then stops.

## Added

- `engine/intelligence/qwen_image_precomposition_to_composed_byte_admission.py`
- `tests/test_phase18_qwen_precomposition_to_composed_byte_admission.py`
- `tools/phase18_continue_precomposition_to_composed_byte_admission.py`
- `docs/PHASE18_CHANGESET_336_PRECOMPOSITION_TO_COMPOSED_BYTE_ADMISSION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_336.md`

## Modified

No pre-existing production gate or renderer was modified.

## Deleted

Nothing.

## Commits

- `3556e5cb2c45421dc8403a18b0585190b1b2a659` — production continuation
- `b99da4cc18f3edd30673eed3825987ba52856254` — regression coverage
- `2019cbbfaff5f352fd675349d5c8f239be13faf8` — operator CLI
- `dbc321d96e51e18d6ce5dcbd4f02397b763c33d5` — Change Set contract

The commit that adds this implementation log follows the commits above.

## Execution contract

The continuation performs:

```text
exact CS335 checkpoint
    -> independent CS335 replay
    -> exact CS335-selected CS270 receipt
    -> CS271 one-shot execution
       using exact CS330 repository-bound runner
    -> independent CS271 replay
    -> exact CS272 byte admission
    -> independent CS272 replay
    -> STOP
```

No retry loop exists around CS271. If rendering fails, CS272 is not called and no CS336 success receipt is created. CS271's pre-render consumption evidence remains the authoritative forensic record that the attempt was consumed.

## Lineage protections

CS336 requires:

- exact Story SHA continuity from CS335 through CS271 and CS272;
- exact canonical-candidate binding continuity;
- CS271 to consume the exact CS270 receipt selected by CS335;
- CS271 runner ID to equal `pul7sar-phase18-production-overlay-composer-v1`;
- CS272 to consume the exact CS271 receipt and receipt digest;
- CS272 composed-candidate binding to equal the exact CS271 composed-candidate binding;
- final composed PNG bytes to reopen from their repository binding.

## Authority boundary

Success may establish:

```text
precomposition_execution_ready = true
cs271_attempt_consumed = true
composition_executed = true
composed_candidate_bytes_admitted_for_post_composition_qa = true
```

Success must still keep:

```text
composed_visual_approved = false
semantic_approved = false
human_visual_review_approved = false
golden_quality_approved = false
genuine_golden_png_created = false
publication_ready = false
authoritative = false
```

Therefore CS336 does not claim that a composed image is visually correct, semantically correct, Golden, or publishable.

## Regression coverage added

The new regression module covers:

- exactly one CS271 call followed by exactly one CS272 call on the success path;
- CS271 failure propagating without retry and without invoking CS272;
- same-story/same-candidate lineage enforcement;
- rejection of premature semantic authority;
- static isolation from Qwen model loading and network access;
- static absence of retry loops, publishing/uploading, and downstream approval shortcuts.

Existing CS271 and CS272 verifiers continue to own their own byte-level and one-shot invariants.

## Preserved gates

No bypass or weakening was introduced for:

- Fact/Freshness verification;
- Entity/Identity verification and manual identity evidence;
- sentiment neutrality and loser-respect;
- zero-cost/offline enforcement;
- Generated-Layer QA;
- CS269/CS270 composition contracts;
- CS331 overlay execution readiness;
- CS271 one-shot consumption semantics;
- CS272 exact composed-byte admission;
- post-composition semantic/layer QA;
- visual critic and visual-quality gates;
- Golden Quality;
- Human Visual Review;
- exact Brand/Typography review;
- Final Composed Approval;
- Final Semantic Approval;
- SemanticPublicationGate;
- CS285 Genuine Golden materialization;
- CS286 publication readiness.

## CUDA/GPU execution blocker measured during this Change Set

Current execution environment:

```text
PyTorch = 2.10.0+cpu
CUDA available = false
torch.version.cuda = null
CUDA device count = 0
native CUDA BF16 = false
nvidia-smi = unavailable
```

Accordingly, this Change Set did **not** fabricate or claim genuine Qwen inference, a genuine `canonical_candidate.png`, a genuine production-composed visual derived from Qwen inference, or a Genuine Golden Visual PNG.

The remaining generation blocker is a zero-cost execution host that provides, in one compatible environment, NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM, the approved Qwen-Image/Diffusers runtime, the exact approved already-local pinned model snapshot, and local verifier assets, with no paid/network fallback.

## CI state at initial documentation

GitHub Actions were triggered on the CS336 commits. At the time this log was first written, the newest workflows for `dbc321d96e51e18d6ce5dcbd4f02397b763c33d5` were queued/in progress. No terminal-green claim is made until the relevant verification workflow reports `completed/success`.

## Remaining path to the first genuine Golden PNG

For the selected low-risk first target (no required Human Identity layer), the intended path is now:

```text
genuine Qwen candidate
    -> CS268 Generated-Layer QA
    -> CS332 typography materialization
    -> CS333 verified PUL7SAR brand materialization
    -> CS334 exact manifests
    -> CS335 CS269/CS270/CS331 precomposition readiness
    -> CS336 CS271/CS330 one-shot composition + CS272 byte admission
    -> post-composition semantic/layer QA
    -> visual-quality and Golden-quality gates
    -> Human Visual Review
    -> exact Brand/Typography review
    -> Final Composed Approval
    -> Final Semantic Approval
    -> SemanticPublicationGate
    -> CS285 Genuine Golden PNG
    -> CS286 publication readiness
```

The dominant external execution blocker remains genuine Qwen CUDA/BF16 generation; CS336 materially reduces the downstream manual gap without pretending that such generation has occurred.
