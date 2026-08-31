# Phase 18 Implementation Log 302

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Baseline reviewed before changes: `babec0bff1959d06bc7683a9abf0d13f586b83be` (CS301).

`main` was read only and was not modified, merged, rebased, force-updated, or used as a write target.

## Problem found

CS301 provided a byte-bound `canonical_candidate_handoff.json` builder/verifier, but handoff creation remained a separate operator step after the CS300 manifest-bound launcher returned success. That left an avoidable operational gap: a genuine canonical run could be complete while the exact downstream handoff had not yet been materialized and replay-verified.

## Implementation

CS302 adds a composed execution edge that treats handoff sealing as part of successful candidate delivery.

### Added

1. `engine/intelligence/qwen_image_sealed_candidate_execution.py`
   - Adds `execute_and_seal_canonical_candidate(...)`.
   - Delegates inference to the existing CS295-CS300 manifest-bound launcher; it does not create an alternate inference path.
   - Propagates a non-zero canonical inference return code unchanged and does not attempt a handoff.
   - After zero, requires the repository-local output directory, rejects an existing/symlink handoff path, builds `canonical_candidate_handoff.json`, and independently replay-verifies it.
   - Requires `genuine_canonical_inference_executed=true` and `handoff_sealed=true`.
   - Requires semantic, human-review, Golden-quality, Genuine-Golden-PNG, and publication authority to remain false in both the built and verified handoff.

2. `tools/phase18_run_sealed_canonical_candidate.py`
   - Adds a narrow production CLI accepting only launch manifest, output directory, and repository root.
   - It exposes no prompt/model/seed/dimensions/steps/guidance/network/paid-mode/approval overrides.

3. `tests/test_phase18_qwen_image_sealed_candidate_execution.py`
   - Covers non-zero propagation with no handoff attempt.
   - Covers mandatory handoff build and replay verification after zero.
   - Covers rejection of premature downstream authority.
   - Covers fail-closed behavior when a handoff already exists.

4. `docs/PHASE18_CHANGESET_302_SEALED_CANDIDATE_EXECUTION.md`
   - Documents the contract, authority boundary, zero-cost/network boundary, and test intent.

5. `docs/PHASE18_IMPLEMENTATION_LOG_302.md`
   - This implementation record.

### Modified

None.

### Deleted

None.

## Commits in this change set

- `acc02ab74c655294b5362263ea89c9d288ccebb8` — `Phase 18 CS302 add sealed candidate execution`
- `8e66ad1afe6f7904894fdde7ec04560bc39045a8` — `Phase 18 CS302 add sealed candidate launcher`
- `77c38775eef5cf7f954c73d9cfe9e068b11ec164` — `Phase 18 CS302 add sealed candidate regressions`
- `554f8a564be50ffefddc1fff8df967e7c10fbe01` — `Phase 18 CS302 document sealed candidate execution`
- final implementation-log commit: this file's commit/branch HEAD after creation.

## Gate preservation

CS302 does not modify or bypass:

- Fact/Freshness Lock;
- Entity/Identity Verification;
- sentiment neutrality and loser-respect rules;
- story-bound semantic ownership;
- `$0-local` cost mode;
- local-only Qwen snapshot and no-network execution contracts;
- generated-layer/composition QA;
- visual-quality adjudication;
- Human Review;
- Exact Brand/Typography;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- publication readiness.

The handoff remains explicitly non-authoritative for downstream approval.

## Testing status

The added tests are deterministic CPU/control-plane regression tests. GitHub CI is expected to run the repository's existing Phase 18 verification workflows on the new HEAD. A passing control-plane CI result must not be interpreted as genuine CUDA/BF16 inference.

## Genuine Golden PNG status and blocker

No genuine Golden Visual PNG is claimed by CS302. No model load or CUDA/BF16 inference was fabricated.

The remaining execution blocker is a compatible zero-cost host that simultaneously provides:

- NVIDIA CUDA device;
- CUDA-enabled PyTorch;
- native BF16 support;
- the CS260-authorized runtime identity / compatible Diffusers `QwenImagePipeline`;
- sequential CPU offload;
- the exact already-local approved Qwen snapshot and pinned revision;
- sufficient RAM/VRAM demonstrated by an actual local model load and inference.

Once such a host exists, the intended production edge is now `manifest -> canonical inference -> independent output replay -> mandatory candidate handoff build -> mandatory candidate handoff replay`, before any semantic, visual-quality, Golden, or publication authority can advance.
