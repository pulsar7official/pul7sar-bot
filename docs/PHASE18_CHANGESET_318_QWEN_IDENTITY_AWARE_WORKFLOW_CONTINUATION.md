# Phase 18 Change Set 318 — Qwen Identity-Aware Workflow Continuation

## Purpose

Close the remaining orchestration gap between the canonical Qwen GPU workflow's CS304/CS305 semantic checkpoint and the existing CS317 identity-aware router.

A real canonical candidate that survives CS304 and CS305 must no longer depend on an operator to choose manually whether to create a CS266 human pixel-identity review request or continue to CS268 Generated-Layer QA.

## Contract

The canonical Qwen workflow now consumes the exact `cs304_receipt` and `cs305_receipt` emitted by the same run's semantic checkpoint and invokes `tools/phase18_route_semantic_checkpoint_after_identity_requirement.py` exactly once.

### Identity review required

When `pixel_identity_review_required=true`:

- the CS317 router must select `CS266_PIXEL_IDENTITY_REVIEW_REQUIRED`;
- the byte-bound CS266 request must be created;
- `generated_layer_qa_executed` must remain `false`;
- the workflow stops after evidence upload and does not manufacture CS267 or identity approval.

### Identity review not required

When `pixel_identity_review_required=false`:

- the CS317 router must select `CS268_GENERATED_LAYER_QA_NO_PIXEL_IDENTITY_REVIEW_REQUIRED`;
- CS268 Generated-Layer QA must execute;
- the candidate must pass CS268 for the workflow to remain successful;
- no identity approval is manufactured.

## Authority boundary

CS318 does not grant or relax any of the following:

- Fact/Freshness approval;
- Entity/Identity approval;
- sentiment or loser-respect requirements;
- semantic final approval;
- Human Visual Review approval;
- Golden-quality approval;
- Genuine Golden PNG materialization;
- publication readiness.

The workflow explicitly requires `identity_approved`, `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, and `publication_ready` to remain `false` after routing.

## Zero-cost and offline preservation

The existing Qwen workflow remains branch-bound to `phase18/story-intelligence`, self-hosted, CUDA/BF16 gated, `$0-local`, and Hugging Face/Transformers offline. CS318 adds no network fetch, paid service, model substitution, or alternate generation path.

## Result

When a compatible zero-cost GPU host becomes available, one canonical workflow run can now advance a genuine candidate through:

`Qwen inference → attestation → CS301 → CS303 → CS304 → CS305 → CS317`

and then either stop safely at CS266 for independent human identity review or continue to CS268 when human pixel-identity review is not required.
