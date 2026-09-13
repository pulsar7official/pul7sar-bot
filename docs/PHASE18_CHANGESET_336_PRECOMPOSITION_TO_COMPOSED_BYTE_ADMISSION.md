# Phase 18 Change Set 336 — Precomposition to Composed-Byte Admission

## Purpose

Change Set 336 closes the final manual handoff between the independently verified CS335 precomposition-readiness checkpoint and CS272 exact composed-byte admission.

The continuation is deliberately narrow:

1. independently reverify the exact CS335 receipt;
2. reopen the exact CS270 receipt selected by CS335;
3. execute exactly one CS271 composition attempt using only the repository-bound CS330 production overlay runner;
4. independently reverify CS271 and its one-shot consumption evidence;
5. pass only that exact CS271 receipt to CS272;
6. independently reverify CS272 and the exact composed PNG byte binding;
7. stop before post-composition semantic, visual-review, Golden-quality, brand-publication, semantic-publication, or publication-readiness authority.

## One-shot invariant

CS271 owns attempt consumption. It writes consumption evidence before rendering. CS336 contains no retry loop. If CS271 raises, CS272 is not invoked and CS336 does not manufacture a success receipt. The surviving CS271 consumption evidence is forensic evidence that the attempt was spent.

## Runner invariant

Only the existing project-native CS330 runner is supplied to CS271:

- runner ID: `pul7sar-phase18-production-overlay-composer-v1`
- entrypoint: `compose_visual(preflight, output_path, repo_root)`
- runner source is repository-byte-bound again by CS271 itself.

CS336 performs no generation, placement inference, resizing, typography selection, identity synthesis, brand drawing, or network access.

## Lineage invariant

Successful execution requires the same:

- story snapshot SHA-256;
- canonical candidate binding;
- exact CS335-selected CS270 receipt;
- exact CS271 receipt and composed PNG;
- exact CS272 source-CS271 receipt binding.

The composed PNG admitted by CS272 must be the exact byte-bound image emitted by CS271.

## Authority boundary

A successful CS336 checkpoint may assert only that the deterministic composition attempt was consumed/executed and that the resulting bytes were admitted for post-composition QA:

```text
precomposition_execution_ready = true
cs271_attempt_consumed = true
composition_executed = true
composed_candidate_bytes_admitted_for_post_composition_qa = true
```

It must keep all later authorities closed:

```text
composed_visual_approved = false
semantic_approved = false
human_visual_review_approved = false
golden_quality_approved = false
genuine_golden_png_created = false
publication_ready = false
authoritative = false
```

CS336 is therefore not a Golden Visual approval and not a publication approval.

## Files

- `engine/intelligence/qwen_image_precomposition_to_composed_byte_admission.py`
- `tests/test_phase18_qwen_precomposition_to_composed_byte_admission.py`
- `tools/phase18_continue_precomposition_to_composed_byte_admission.py`
- `docs/PHASE18_CHANGESET_336_PRECOMPOSITION_TO_COMPOSED_BYTE_ADMISSION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_336.md`

## Preserved gates

No existing Phase 18 gate is modified or bypassed, including factual/freshness verification, entity/identity verification, sentiment neutrality and loser-respect, zero-cost/offline enforcement, generated-layer QA, deterministic composition contracts, post-composition semantic QA, visual-quality/Golden-quality review, Human Visual Review, exact Brand/Typography review, Final Composed Approval, Final Semantic Approval, SemanticPublicationGate, CS285 Genuine Golden materialization, and CS286 publication readiness.
