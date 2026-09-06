# Phase 18 Change Set 279 — Composed Candidate Final Presentation Review Request

## Purpose

CS279 creates the fail-closed request boundary between an approved CS278 Human Visual Review and the final exact Brand/Typography presentation evidence required before semantic/publication authority can be considered.

It does **not** approve the final presentation and does **not** create a Genuine Golden PNG.

## Required upstream state

CS279 re-verifies CS278 and requires all of the following to be true:

- Golden-quality selector executed;
- Golden-quality candidate approved;
- Human Visual Review requested;
- Human Visual Review executed;
- Human Visual Review evidence admitted;
- Human Visual Review approved.

It requires final composed approval, final semantic approval, Genuine Golden creation, and publication readiness to still be false.

## Exact-byte provenance

The request binds and later re-opens:

1. the exact CS278 receipt bytes;
2. the exact `composed_candidate.png` bytes carried by CS278;
3. the existing repository policy sources used for the final presentation decision:
   - `engine/intelligence/brand_approval_evidence.py`;
   - `engine/intelligence/brand_asset_approval.py`;
   - `engine/intelligence/brand_master_geometry.py`;
   - `engine/fonts/resolver.py`.

Every binding contains repository-relative path, SHA-256, and byte size. Policy-source or PNG byte drift invalidates the request.

## Required presentation checks

The downstream independent review must explicitly evaluate:

- approved brand-asset checksum;
- exact brand-master geometry;
- metallic wordmark preservation;
- verified-story color policy for pulse and number 7;
- number-7 scale and pulse/wordmark relationship;
- football signature presence/position;
- typography font-policy resolution;
- exact, legible copy with no pseudo-text;
- safe-area/content-collision integrity;
- absence of post-review pixel drift or new artifacts.

These checks reuse existing PUL7SAR brand and font contracts rather than duplicating their policy logic.

## Authority boundary

CS279 may set only:

- `final_presentation_review_requested=true`.

It must keep all of these false:

- `final_presentation_review_executed`;
- `final_presentation_review_approved`;
- `exact_brand_integrity_approved`;
- `typography_integrity_approved`;
- `composed_visual_approved`;
- `semantic_approved`;
- `genuine_golden_png_created`;
- `publication_ready`.

The CLI intentionally accepts no presentation verdict, approval override, Golden override, Genuine-Golden claim, or publication override.

## Next safe stage

The next stage should admit independent final-presentation evidence tied to this exact request and exact PNG. Only that later evidence may establish exact Brand/Typography integrity. Final semantic/publication authority must remain separate after that.
