# Phase 18 Change Set 321 — Bound Composition Execution and Admission

## Purpose

CS321 closes the remaining operator-wiring gap between a READY CS270 deterministic composition preflight, CS271 one-shot composition execution, and CS272 exact composed-byte admission.

It does **not** create a renderer, invent layer inputs, approve the composed visual, grant semantic or human authority, create a Golden Visual, or publish anything.

## New execution checkpoint

Added:

`tools/phase18_execute_bound_composition_and_admit.py`

The checkpoint requires explicit repository-local inputs:

- exact CS270 receipt;
- exact Python runner source;
- exact top-level runner entrypoint;
- explicit runner ID;
- fresh repository-local output directory.

It then:

1. resolves all inputs inside the repository and rejects symlinks/outside-repository runner inputs;
2. loads the exact requested top-level runner entrypoint from the explicit source file;
3. keeps Hugging Face/Transformers/Datasets hubs offline during runner import/execution;
4. delegates the actual render to CS271, which independently re-verifies CS270 and binds the callable to the exact runner-source bytes;
5. independently replays CS271;
6. passes the exact CS271 receipt path directly to CS272;
7. independently replays CS272;
8. verifies story, source-candidate, and composed-candidate lineage across CS271 → CS272;
9. emits a non-authoritative checkpoint for the admitted composed bytes.

## Authority boundary

CS321 may truthfully report only that:

- composition executed through CS271; and
- the exact composed bytes were admitted through CS272 for post-composition QA.

It must keep all of these false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

The checkpoint itself is explicitly `authoritative=false`.

## Why this materially reduces the remaining gap

Before CS321, a real CS270-ready candidate still required an operator to load a renderer, call CS271, find the resulting receipt, then separately feed that receipt to CS272. That manual junction could select the wrong receipt or wrong candidate even though CS271 and CS272 individually had strong verification.

CS321 removes that handoff ambiguity while preserving the existing authority boundaries: the exact receipt produced by CS271 in the run is the receipt passed to CS272.

## Explicit non-goals

CS321 does not:

- synthesize editorial text, branding, sport geometry, score/data payloads, or visual assets;
- select or generate a renderer automatically;
- run Qwen-Image generation;
- bypass identity review;
- bypass post-composition semantic/layer QA;
- score Golden quality;
- replace Human Visual Review;
- authorize semantic publication.

## Runtime status

The Genuine Golden path still requires a compatible zero-cost CUDA/BF16 host for the upstream genuine Qwen inference. CS321 is CPU/control-plane preparation and does not fabricate a candidate or composed production PNG when that upstream evidence is absent.
