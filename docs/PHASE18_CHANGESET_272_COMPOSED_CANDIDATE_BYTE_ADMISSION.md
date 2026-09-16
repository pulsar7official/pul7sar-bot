# Phase 18 Change Set 272 — Composed Candidate Byte Admission

## Purpose

CS272 creates the byte-bound handoff between successful one-shot deterministic composition (CS271) and all post-composition visual QA.

It does **not** approve the composed visual and does **not** create Golden or publication authority.

## Required upstream state

CS272 accepts only an exact CS271 receipt that re-verifies successfully and proves:

- `composition_executed = true`
- the original candidate PNG remains byte-bound
- the composition runner and attempt-consumption evidence remain byte-bound
- the composed PNG remains byte-bound
- all downstream quality/publication authorities remain false

## Admission checks

CS272 reopens the exact composed PNG and validates:

- repository-contained, non-symlink path
- SHA-256
- byte size
- PNG signature and IHDR
- positive width and height
- dimensions equal the CS271 composed binding
- canvas dimensions equal the source candidate dimensions
- story identity remains the same
- source CS271 receipt bytes and receipt digest remain unchanged

## New authority

Only this authority may become true:

`composed_candidate_bytes_admitted_for_post_composition_qa = true`

The following remain false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

## Why this is necessary

Without CS272, a downstream semantic inspector, Visual Critic, or human-review receipt could accidentally or maliciously inspect a different PNG from the exact pixels produced by CS271. CS272 converts the composed image itself into the immutable provenance anchor for all remaining quality gates.

## Fail-closed rules

CS272 rejects CS271 drift, composed-PNG drift, canvas-size drift, premature Golden/publication authority, symlinks, paths outside the repository, malformed PNG headers, cross-story bindings, and output-directory reuse.

## GPU status

CS272 is CPU/control-plane work and does not claim that a genuine Qwen candidate exists. Genuine production execution remains blocked until the already-defined zero-cost compatible CUDA/BF16 Qwen runtime is actually available and CS262 can execute truthfully.
