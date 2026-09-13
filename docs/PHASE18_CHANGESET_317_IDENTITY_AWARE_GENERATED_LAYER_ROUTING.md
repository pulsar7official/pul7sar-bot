# Phase 18 Change Set 317 — Identity-Aware Generated-Layer Routing

## Purpose

Change Set 317 removes the manual control-plane gap immediately after the CS304/CS305 admitted-candidate semantic checkpoint without manufacturing an identity verdict.

The router consumes the exact existing CS304 Semantic Base QA receipt and CS305 Identity Requirement receipt and replays both verifiers before choosing one of two mutually exclusive routes:

1. **Human pixel identity review required** — build and independently verify the existing byte-bound CS266 Pixel Identity Review Request, then stop. CS268 is not executed and identity remains unapproved.
2. **No human pixel identity review required** — execute and independently replay the existing CS268 Generated-Layer QA without supplying CS267 evidence. Identity remains unapproved because no human identity claim was required or manufactured.

## New executable surface

`tools/phase18_route_semantic_checkpoint_after_identity_requirement.py`

The command accepts:

- `--cs304-receipt`
- `--cs305-receipt`
- `--output-root`
- `--repo-root`

It produces `post_semantic_identity_route_receipt.json` and returns non-zero if the no-review CS268 route rejects Generated-Layer QA.

## Fail-closed routing contract

The router requires:

- CS304 to replay successfully with `semantic_base_scene_approved=true`;
- CS305 to replay successfully with `identity_requirement_classified=true`;
- exact story SHA and candidate binding agreement between CS304 and CS305;
- `pixel_identity_review_required` to be an explicit boolean;
- semantic, Human Review, Golden, materialization, and publication authorities to remain false upstream and downstream.

When `pixel_identity_review_required=true`, CS266 must prove:

- the same story and candidate;
- `pixel_identity_review_request_created=true`;
- `pixel_identity_review_executed=false`;
- `identity_approved=false`.

The router then stops. It does not admit external CS267 evidence and cannot approve identity.

When `pixel_identity_review_required=false`, CS268 must prove:

- the same story and candidate;
- no identity review requirement;
- `identity_approved=false`;
- no composition execution or composed-visual approval;
- all downstream authorities remain false.

## Authority boundary

CS317 may only establish a deterministic route state and, on the no-review route, preserve the existing CS268 `generated_layer_qa_approved` result.

It does not grant or fabricate:

- person identity approval;
- final semantic approval;
- Human Visual Review approval;
- Golden quality approval;
- Genuine Golden materialization;
- publication readiness;
- network or paid-generation permission.

Fact/Freshness, Entity/Identity, sentiment neutrality, loser-respect, `$0-local`, semantic-publication, brand/typography, and visual-quality policies are unchanged.

## Why this advances the first Genuine Golden Visual

Before CS317, a genuine candidate that passed CS304/CS305 still required an operator to decide manually whether to create CS266 or invoke CS268. CS317 makes that branch deterministic and replay-bound while preserving the human-review boundary.

The resulting safe path is:

`CS304 → CS305 → CS317`

- if human identity review is required: `→ CS266 → stop for independent manual source comparison → CS267 later`;
- otherwise: `→ CS268 Generated-Layer QA`.

No PNG or Golden verdict is claimed by this control-plane change set.
