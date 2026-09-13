# Phase 18 Change Set 331 — Production Overlay Execution Readiness

## Purpose

CS330 supplied a project-native production composition runner that consumes only exact repository-byte-bound full-canvas overlays. CS271, however, consumes its one-shot composition attempt before runner invocation. CS270 proves deterministic payload byte provenance but deliberately does not decode those payloads as CS330-compatible visual overlays.

CS331 closes that pre-execution gap. It is a fail-closed CPU/control-plane readiness boundary between CS270 and the CS271 one-shot call. It discovers malformed or non-materialized overlays before an attempt can be consumed.

## Inputs and replay

CS331 consumes one READY CS270 receipt and independently re-verifies it. It reopens the exact candidate PNG, follows CS270 back to the exact CS269 receipt, independently re-verifies CS269, and requires Story/candidate/receipt continuity.

For every non-generative layer that CS330 would consume, CS331 reopens the exact repository binding and checks the actual image bytes.

## CS330 compatibility contract

Deterministic layers must use:

`pul7sar-phase18-full-canvas-rgba-overlay-v1`

Verified assets are checked under their CS269 repository binding. Every consumed overlay must already be:

- a PNG;
- natively `RGBA` (conversion is not accepted as evidence);
- exactly the same width and height as the canonical candidate;
- non-empty in alpha;
- not a fully opaque full-canvas replacement.

CS331 never resizes, positions, wraps text, selects a font, chooses typography, moves a logo, creates a brand mark, renders sport geometry, or generates image content. A layer that is not already materialized correctly remains blocked.

## Why this boundary matters

CS271 writes/fsyncs its attempt-consumption evidence before invoking the composition runner. Without CS331, a wrong canvas size, RGB brand asset, malformed PNG, or unsupported deterministic renderer contract could consume the one-shot attempt and then fail inside CS330. CS331 moves those deterministic compatibility checks before that irreversible boundary.

## Authority

A successful receipt may set only:

`overlay_execution_ready = true`

It must keep false:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

CS331 is therefore not visual approval, semantic approval, Golden status, or publication authority. It does not itself consume a CS271 attempt.

## Preserved gates

CS331 does not weaken Fact/Freshness Lock, Entity/Identity Verification, sentiment neutrality and loser-respect, `$0-local`, generated-layer QA, semantic ownership, post-composition semantic QA, Visual Critic, Human Visual Review, exact Brand/Typography review, Final Semantic Approval, or `SemanticPublicationGate`.

## Scope limitation

CS331 validates already-materialized overlays; it intentionally does not invent the missing typography/brand layout specification needed to create them. If the approved production path has not yet produced a full-canvas typography or brand overlay, readiness stays false and names the exact blocker.

## Remaining genuine Golden path

`genuine Qwen candidate -> CS268 -> CS269 -> CS270 -> CS331 overlay readiness -> CS271 with CS330 runner -> composed byte admission -> post-composition semantic/layer QA -> Golden Quality -> Human Review -> exact Brand/Typography -> Final Composed Approval -> Final Semantic Approval -> SemanticPublicationGate -> CS285 Genuine Golden PNG -> CS286 readiness`
