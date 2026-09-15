# Phase 18 Change Set 266 — Canonical Candidate Pixel Identity Review Request

## Purpose

CS265 determines whether an exact canonical candidate contains a story-relevant human identity that still requires pixel-level verification. CS266 converts that requirement into a byte-bound, fail-closed review request. It does **not** perform face recognition, does **not** choose an identity threshold, and does **not** grant identity approval.

The objective is to prevent a candidate that is semantically plausible but depicts the wrong person from advancing simply because general scene QA passed.

## Inputs

CS266 accepts one CS265 receipt and replays `verify_identity_requirement` before building a request. Through CS265 it remains bound to:

- the exact story snapshot SHA-256;
- the exact CS264 semantic-base-QA receipt;
- the exact candidate PNG bytes;
- the exact source-backed entity/identity evidence;
- the canonical human identity targets derived from that evidence.

CS266 also re-opens the candidate and identity-evidence byte bindings itself.

## Human-target review contract

When `pixel_identity_review_required=true`, every canonical human target must retain non-empty `identity_source_refs`. The request records the exact target `entity_id`, display name, entity kind, and source-reference identifiers.

The immutable required checks are:

1. `candidate_subject_matches_canonical_entity`
2. `no_identity_substitution`
3. `no_ambiguous_or_conflicting_identity`
4. `source_backed_reference_evidence_used`

The contract additionally states:

- a general semantic scene verdict is not identity evidence;
- no automatic identity threshold is defined by CS266;
- the pipeline must fail closed if no compatible identity-review execution is available.

## Authority boundary

CS266 may state only whether a pixel-identity review request is required/created. It always keeps:

- `pixel_identity_review_executed=false`
- `identity_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `genuine_golden_png_created=false`
- `golden_quality_approved=false`
- `publication_ready=false`

A non-human candidate may legitimately have `pixel_identity_review_required=false`; that still does not manufacture `identity_approved=true`.

## Fail-closed provenance

The verifier re-opens and hashes the source CS265 receipt, replays the CS265 verifier, re-opens and hashes the exact candidate PNG and identity-evidence bytes, recomputes review targets from source evidence, and re-checks the immutable review contract.

Symlinks, path traversal, byte drift, target drift, requirement drift, contract drift, premature authority, and missing source-backed references are rejected.

## Relationship to Golden Visual production

CS266 is preparatory post-generation control-plane work. It does not run Qwen Image and does not create a candidate or Golden PNG. A genuine generated candidate must still pass the compatible pixel-identity review when required, Hybrid Layer QA, Visual Critic, Human Review, Golden scoring, exact brand/typography checks, and SemanticPublicationGate before publication authority can exist.
