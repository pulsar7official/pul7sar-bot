# Phase 18 Change Set 308 — Exact Final Composed Approval Lineage

## Purpose

CS308 strengthens the historical CS281 Final Composed Visual Approval boundary. CS281 combines two independently supplied inputs: CS273 post-composition semantic QA and CS280 final Brand/Typography presentation evidence. Before this change, CS281 re-verified both inputs and required the same Story and exact composed PNG bytes, but did not prove that the supplied CS273 was the exact CS273 embedded in the transitive review lineage that produced CS280.

That left a narrow cross-run substitution surface: two valid CS273 receipts for the same Story and the same PNG could be exchanged at the CS281 aggregation boundary even though CS280 had been produced from only one of those review runs.

## Contract change

The CS281 schema is upgraded to:

`pul7sar-phase18-qwen-image-composed-candidate-final-composed-visual-approval-v2`

Before opening `composed_visual_approved`, CS281 now replays:

`CS280 -> CS279 -> CS278 -> CS277 -> CS276 -> CS275 -> CS274 -> CS273`

Every transition is repository-relative, byte-bound, symlink/path-escape resistant, and receipt-digest checked through the original verifier for that stage.

The independently supplied CS273 must be identical to the CS273 derived from the CS280 lineage across:

- repository-relative path
- file SHA-256
- byte size
- receipt SHA-256

Same Story SHA and same composed PNG are still mandatory, but are no longer sufficient by themselves.

## Preserved authority boundaries

CS308 does not alter any score, visual-quality threshold, human-review checklist, factual rule, identity rule, sentiment/loser-respect rule, brand/Typography rule, or zero-cost generation rule.

Successful CS281 still sets only `composed_visual_approved=true`. It keeps:

- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

Final semantic approval and `SemanticPublicationGate` remain independent downstream authorities. Genuine Golden materialization remains a later, separately verified operation.

## Regression coverage

The CS281 regression suite now covers:

- acceptance when the supplied CS273 binding exactly matches the CS273 transitively derived from CS280;
- rejection when a different CS273 run has the same Story and composed PNG;
- rejection when only the receipt digest differs despite the same file binding;
- existing Story/PNG drift and premature-authority rejection behavior.

## Genuine Golden boundary

This change is control-plane/provenance work only. It does not claim a Qwen-Image model load, CUDA/BF16 inference, a genuine canonical candidate PNG, a production composed PNG, or a Genuine Golden Visual PNG.
