# Phase 18 Change Set 277 — Composed Candidate Human Visual Review Request

## Purpose

CS277 inserts a fail-closed, byte-bound request boundary between authentic Golden-quality adjudication (CS276) and any later Human Visual Review evidence. It does not itself perform or approve a human review.

## Preconditions

The stage re-verifies the exact CS276 receipt and requires:

- `golden_quality_selector_executed=true`;
- `golden_quality_approved=true`;
- `quality_tier` is `golden` or `elite`;
- composition, composed-byte admission, hybrid-surface semantic inspection, and visual-quality evidence gates remain proven;
- Human Review, final composed approval, final semantic approval, Genuine Golden PNG creation, and publication authority remain unopened.

A `below_golden` candidate cannot be routed to Human Review through CS277.

## Exact-byte binding

CS277 binds:

1. the exact CS276 receipt by repository-relative path, SHA-256, byte size, and internal receipt SHA; and
2. the exact `composed_candidate.png` referenced by CS276.

The composed PNG is reopened from the repository and its path/hash/size are revalidated. Later byte replacement invalidates the CS277 receipt.

## Human-review checklist

The request carries required review subjects rather than verdicts:

- story/editorial fidelity;
- factual/result integrity;
- entity identity continuity when applicable;
- sentiment neutrality and loser respect;
- composition and visual hierarchy;
- photorealism/cinematic realism;
- sport geometry/physical coherence;
- artifact and pseudo-text absence;
- exact brand/logo/typography surface;
- overall Golden visual acceptability.

These checklist entries are requirements for a later independent review stage; they are not machine-generated PASS decisions.

## Authority boundary

CS277 may set only:

- `human_visual_review_requested=true`.

It must keep all of the following false:

- `human_visual_review_executed`;
- `human_visual_review_approved`;
- `composed_visual_approved`;
- `semantic_approved`;
- `genuine_golden_png_created`;
- `publication_ready`.

The CLI deliberately accepts no reviewer identity, verdict, scores, approval override, Genuine Golden claim, or publication override.

## Failure behavior

The stage fails closed on CS276 schema/state drift, non-Golden quality, source-receipt byte drift, composed-PNG byte drift, path escape/symlink inputs, forged downstream authority, receipt digest drift, or pre-existing output directories.

## Scope

This change does not modify Fact Lock, identity/entity verification, sentiment/loser-respect policy, zero-cost execution policy, Qwen inference requirements, semantic publication, Golden thresholds, composition, or previous quality gates. It creates no production image and makes no claim that GPU inference or Human Review occurred.
