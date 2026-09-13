# Phase 18 Implementation Log 317 — Identity-Aware Generated-Layer Routing

## Scope and branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence` only.
- Starting HEAD reviewed before writes: `b91d9129c260a18f825c900771a5a051150e5b3c` (CS316).
- `main` was reviewed read-only during this change set and was at `89b69e0972047af615162518dcc32dc1a16cd2dd` at the latest pre-log check.
- No write, merge, rebase, reset, force-update, or ref mutation was performed on `main`.

## Review finding

The downstream review started from the real CS316 stopping point rather than adding another abstract gate.

CS316 safely reaches CS304 Semantic Base QA and CS305 Identity Requirement Classification, but the next action was still manual. Existing repository contracts already define the correct mutually exclusive behavior:

- CS266 creates a byte-bound pixel-identity review request and cannot approve identity.
- CS267 admits independently produced manual source-comparison evidence when human identity review is required.
- CS268 Generated-Layer QA requires CS267 only when CS305 says human pixel-identity review is required; otherwise CS268 can run directly while keeping identity approval false.

Therefore a genuine candidate that passed CS304/CS305 still required an operator to decide manually whether to create CS266 or invoke CS268. That manual branch-selection gap can be removed safely without weakening identity policy.

## Added

### `tools/phase18_route_semantic_checkpoint_after_identity_requirement.py`

A CPU/control-plane router that independently replays the exact CS304 and CS305 receipts and then chooses exactly one route:

1. `pixel_identity_review_required=true`
   - builds CS266 from the exact CS305 receipt;
   - independently verifies CS266;
   - requires the same story SHA and candidate binding;
   - requires `pixel_identity_review_request_created=true`;
   - requires `pixel_identity_review_executed=false` and `identity_approved=false`;
   - does not execute CS268;
   - emits an explicit `AWAITING_PIXEL_IDENTITY_REVIEW` route receipt and stops.

2. `pixel_identity_review_required=false`
   - invokes existing CS268 against the exact CS304/CS305 receipts with no CS267 evidence;
   - independently verifies CS268;
   - requires the same story/candidate lineage;
   - requires `identity_approved=false`;
   - requires composition and composed-visual approval to remain false;
   - preserves CS268's Generated-Layer QA verdict;
   - returns non-zero if CS268 rejects the candidate.

The router rejects story/candidate drift, non-boolean identity requirements, premature downstream authority, invalid schemas, invalid CS266 state, and invalid CS268 state.

### `tests/test_phase18_post_semantic_identity_aware_routing.py`

Regression coverage includes:

- human-identity route creates CS266 and proves CS268 is never invoked;
- no-review route invokes CS268 and does not manufacture identity approval;
- story-lineage drift fails closed;
- premature publication authority fails closed;
- both routes preserve semantic, Human Review, Golden, materialization, and publication authorities as false.

### `docs/PHASE18_CHANGESET_317_IDENTITY_AWARE_GENERATED_LAYER_ROUTING.md`

Documents the routing contract and authority boundary.

### `docs/PHASE18_IMPLEMENTATION_LOG_317.md`

This implementation record.

## Modified

None. CS317 deliberately reuses existing CS266 and CS268 production authorities rather than changing their thresholds or semantics.

## Deleted

None.

## Commits

- `f58a9f3826d2dce905fe7dafe669a4ec8fb285dc` — identity-aware routing command.
- `f21bb36c9e991802b3ec0c8eb6bfe0108f758b14` — routing regressions.
- `0bdeb07edaa7fd32eb46143c974d692827506320` — CS317 contract documentation.
- The commit containing this file records the implementation log.

## Gate preservation

CS317 does not alter or bypass:

- Fact/Freshness locks;
- canonical Entity/Identity evidence;
- source-backed human identity requirements;
- sentiment neutrality and loser-respect constraints;
- `$0-local` / offline generation policy;
- Semantic Base QA;
- Generated-Layer ownership rules;
- Composition QA;
- Golden Visual Quality thresholds;
- Human Visual Review;
- Exact Brand/Typography ownership;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- final publication readiness.

The human route cannot accept or generate a CS267 identity approval. It stops at CS266 and therefore still requires independent manual source comparison against the bound source references.

The no-review route does not set `identity_approved=true`; it merely allows the already-existing CS268 contract to evaluate a candidate for which CS305 proved human pixel-identity review is not required.

## Test status

GitHub Actions began automatically on the CS317 commits. At the pre-log check, `Phase 18 Story Intelligence Verification` run `33627295230` for documentation HEAD `0bdeb07edaa7fd32eb46143c974d692827506320` was queued. Terminal success is not claimed until the final implementation-log HEAD completes the repository-wide verification.

## Genuine Golden PNG status and exact execution blocker

No genuine Qwen candidate PNG, composed production PNG, or Genuine Golden Visual PNG is claimed by CS317. This change set is deterministic control-plane work only.

A real candidate still requires a proven zero-cost execution host that simultaneously provides NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, a compatible approved QwenImagePipeline/Diffusers runtime, the exact already-local pinned `Qwen/Qwen-Image-2512` snapshot, required local semantic-verifier assets, sequential CPU offload support, and sufficient live RAM/VRAM demonstrated by an actual model load and inference.

No model load, inference, identity verdict, Golden score, or publication result is fabricated.

## Remaining path after CS317

`genuine Qwen inference`
→ CS301 sealed candidate handoff
→ CS303 exact-byte admission
→ CS304 Semantic Base QA
→ CS305 Identity Requirement
→ **CS317 deterministic routing**

If human identity review is required:
`→ CS266 request → independent manual source comparison → CS267 evidence admission → CS268 Generated-Layer QA`

If human identity review is not required:
`→ CS268 Generated-Layer QA directly`

Then:
`→ Composition/Post-composition → Golden Quality → Human Visual Review → Exact Brand/Typography → Final Composed Approval → Final Semantic Approval → SemanticPublicationGate → CS285 Genuine Golden materialization → CS286 publication readiness`.
