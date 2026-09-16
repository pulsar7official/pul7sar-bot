# Phase 18 Change Set 278 — Composed Candidate Human Visual Review Evidence Admission

## Purpose

CS278 closes the gap immediately after CS277 by admitting an actual independent human visual-review verdict while keeping Genuine Golden creation, final semantic/composed approval, and publication authority separate.

It does not generate a verdict, does not infer a human decision from Golden scores, and does not allow a CLI approval override.

## Preconditions

CS278 re-verifies the CS277 request and requires:

- `golden_quality_selector_executed=true`;
- `golden_quality_approved=true`;
- `human_visual_review_requested=true`;
- Human Review has not already executed;
- no final composed, semantic, Genuine Golden, or publication authority has been opened.

The exact composed PNG is reopened from the CS277 binding. The CS277 request bytes and external evidence bytes are both repository-relative, SHA-256-bound, byte-size-bound, non-symlink files.

## External evidence contract

The review evidence schema is:

`pul7sar-phase18-composed-candidate-human-visual-review-v1`

It must contain:

- the exact Story Snapshot SHA-256;
- the exact composed candidate PNG SHA-256;
- the exact CS277 request receipt SHA-256;
- `review_method=independent_manual_human_visual_review`;
- a non-empty `reviewer_id`;
- non-empty `review_notes`;
- one explicit boolean result for every review check requested by CS277;
- `decision=approve|reject`.

An approval is valid only when every required check is `true`. A rejection is valid only when at least one required check is `false`. This prevents contradictory evidence such as `approve` with a failed factual/identity/brand check or `reject` while claiming every check passed.

## Authority boundary

CS278 may set:

- `human_visual_review_executed=true`;
- `human_visual_review_evidence_admitted=true`;
- `human_visual_review_approved=true|false`, derived only from the bound external evidence.

It always keeps:

- `composed_visual_approved=false`;
- `semantic_approved=false`;
- `genuine_golden_png_created=false`;
- `publication_ready=false`.

Thus even an approved independent human review cannot itself create a Genuine Golden PNG or authorize publication.

## Required review surface

CS278 inherits the exact checklist authored by CS277, including story/editorial fidelity, factual/result integrity, entity identity continuity when applicable, sentiment neutrality and loser respect, composition/hierarchy, photorealism/cinematic realism, sport geometry/physical coherence, artifact/pseudo-text absence, exact brand/logo/typography surface, and overall Golden Visual acceptability.

## Fail-closed behavior

Verification fails on request/evidence/PNG byte drift, receipt drift, missing or extra checks, non-boolean check values, invalid method, missing reviewer identity/notes, contradictory decision/check state, authority escalation, or reused output directories.

## What CS278 does not do

CS278 does not run Qwen-Image, does not create image pixels, does not bypass the zero-cost runtime gate, does not modify Golden thresholds, does not replace identity/factual/sentiment gates, does not grant final brand/typography authority, and does not call `SemanticPublicationGate`.

## Next safe stage

A later stage may consume only an approved CS278 receipt and the exact same composed PNG to perform final exact brand/typography plus composed-surface authority. Rejected Human Review evidence must remain terminal for that candidate unless a new candidate is generated and traverses the provenance chain again.
