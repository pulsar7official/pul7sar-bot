# Phase 18 Change Set 303 — Sealed Handoff Candidate Admission

## Purpose

Change Set 303 closes the remaining production admission bypass between the new CS301/302 sealed-candidate execution path and the older CS263 post-generation QA admission edge.

Before CS303, `tools/phase18_admit_canonical_candidate_bytes.py` accepted a bare CS262 canonical inference receipt. That receipt could still be valid, but using it directly meant downstream post-generation QA did not have to prove that the candidate passed the newer CS290/CS293/CS300 lineage replay and CS301/CS302 handoff sealing path.

CS303 makes the sealed canonical-candidate handoff the required production admission source.

## Required production flow

The canonical downstream edge is now:

1. verified GPU launch manifest;
2. mandatory preload/offline/runtime gates;
3. genuine one-shot local Qwen inference;
4. CS290 provenance;
5. CS293/CS300 launch-to-output replay;
6. CS301/CS302 `canonical_candidate_handoff.json` build and replay;
7. CS303 sealed-handoff byte admission;
8. factual, identity, sentiment, semantic, composition, generated-layer and visual-quality gates;
9. Human Review;
10. exact brand/typography;
11. `SemanticPublicationGate`;
12. Genuine Golden materialization and publication readiness.

A bare canonical inference receipt is no longer a valid input to the production admission CLI.

## Security and authority rules

CS303 replays `verify_canonical_candidate_handoff(...)` and derives the canonical inference receipt and candidate PNG only from the verified handoff bindings. It independently reopens and hashes those files and replays the canonical inference receipt.

The admission requires:

- `cost_mode == "$0-local"`;
- `network_allowed == false`;
- `local_files_only == true`;
- `genuine_canonical_inference_executed == true`;
- `handoff_sealed == true`;
- exact story SHA agreement;
- exact candidate path/hash/byte-size/dimensions agreement across handoff, canonical receipt and local file bytes.

It requires all downstream authority to remain closed:

- `semantic_approved == false`;
- `human_visual_review_approved == false`;
- `golden_quality_approved == false`;
- `genuine_golden_png_created == false`;
- `publication_ready == false`.

CS303 is an admission gate only. It does not perform semantic approval, identity approval, visual-quality adjudication, Human Review, Golden materialization or publication.

## Production CLI change

`tools/phase18_admit_canonical_candidate_bytes.py` now requires:

`--candidate-handoff <canonical_candidate_handoff.json>`

The previous `--cs262-receipt` production input has been removed.

No model, prompt, seed, dimension, inference-setting, network, paid-mode, quality, Golden or publication override is introduced.

## Verification intent

Regression coverage proves that:

- a valid sealed handoff can be admitted without gaining downstream authority;
- a bare canonical inference receipt is rejected as an admission source;
- candidate byte drift after admission is rejected;
- premature semantic authority in the handoff is rejected;
- symlinked candidate inputs are rejected;
- an existing output directory is rejected fail-closed.

## Genuine Golden status

CS303 creates no pixels and does not claim a Golden Visual. Genuine generation remains dependent on a compatible zero-cost NVIDIA CUDA/BF16 host and successful real local Qwen model load/inference, followed by every downstream quality and publication gate.
