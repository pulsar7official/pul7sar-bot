# Phase 18 Change Set 339 — Visual-Quality Review Request → Evidence Admission

CS339 removes the manual handoff between the exact CS338/CS274 visual-quality review request and the existing CS275 external visual-quality evidence gate.

## Contract

Input authority remains upstream only. CS339 requires one exact, independently reverified CS338 receipt and reopens the exact CS274 receipt selected by CS338. It then passes one repository-bound external manual visual-quality review to the existing CS275 builder and independently reverifies the resulting CS275 receipt.

The external review is evidence, not generated truth. CS339 does not create or alter scores, blockers, pixels, typography, brand assets, identity evidence, sentiment evidence, semantic evidence, or publication state. Scores/blockers are parsed and validated by CS275 from the external review evidence.

## Required lineage

`CS338 exact request -> exact CS274 replay -> external manual review -> CS275 evidence admission -> independent CS275 replay -> STOP`

Story SHA and composed-candidate PNG bindings must remain identical through CS338, CS274 and CS275. CS275 must bind the exact CS274 receipt byte-for-byte and by receipt SHA. The external review itself is repository-byte bound and is reopened during verification.

## Authority boundary

A successful CS339 receipt may state only that visual-quality review was requested, executed externally, and that the resulting evidence was admitted. It must keep `visual_quality_review_approved`, `composed_visual_approved`, `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, `publication_ready`, and `authoritative` false.

CS339 deliberately stops before CS276 Golden Quality Adjudication. No Qwen inference, network fallback, scoring generation, Human Review automation, SemanticPublicationGate shortcut, publication, or upload is permitted here.

## Safety preservation

All factual/freshness, identity, sentiment/loser-respect, zero-cost/local-only, exact byte lineage, semantic QA, visual-quality, Human Review, brand/presentation, Golden-quality, final semantic, and semantic-publication gates remain independent and unchanged.
