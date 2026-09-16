# Phase 18 Change Set 304 — Byte-Admission-Bound Semantic Base QA

## Purpose

CS304 repairs the production handoff between CS303 sealed candidate byte admission and the existing semantic base-scene QA stage.

CS303 upgraded `CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA` to v2 and made the admission verifier replay the CS301/302 sealed handoff. The semantic base QA module already called that verifier, but it still demanded legacy pre-CS303 authority fields (`production_semantic_replay_executed`, `fresh_story_gates_passed`, `controlled_trial_preflight_valid`, `canonical_generation_authorized`, and `inference_executed`). Those fields are intentionally not emitted by the CS303 v2 admission receipt. Existing unit fixtures masked the incompatibility by mocking the admission verifier with the obsolete authority shape.

Without this repair, a genuine CS303 receipt would be verified successfully and then rejected by semantic base QA before Qwen2.5-VL inspection.

## Production contract

The semantic base QA ingress is now explicitly the CS303 candidate admission receipt.

Required upstream authority is limited to the authority CS303 actually owns:

- `genuine_canonical_inference_executed=true`
- `handoff_sealed=true`
- `candidate_bytes_admitted_for_post_generation_qa=true`
- `cost_mode=$0-local`
- `network_allowed=false`
- `local_files_only=true`

The following remain forbidden at this stage:

- `genuine_golden_png_created=true`
- `semantic_approved=true`
- `human_visual_review_approved=true`
- `golden_quality_approved=true`
- `publication_ready=true`

The CS304 receipt schema is bumped to `pul7sar-phase18-qwen-image-canonical-candidate-semantic-base-qa-v2` and now records `source_candidate_admission` rather than the legacy `source_cs263_receipt` name.

`source_candidate_admission` binds:

- repository-relative admission receipt path;
- admission receipt file SHA-256 and byte size;
- admission `receipt_sha256`;
- the CS301/302 `candidate_handoff_sha256` carried by CS303.

Verification reopens and rehashes the admission and candidate, replays the CS303 verifier, checks the sealed handoff digest again, and compares candidate path/SHA-256/byte-size/dimensions field-by-field with the CS303 source.

## CLI contract

`tools/phase18_run_canonical_candidate_semantic_base_qa.py` now requires:

```text
--candidate-admission <canonical_candidate_byte_admission_receipt.json>
```

The obsolete `--cs263-receipt` production argument is removed. This is a naming and contract correction, not an authority expansion.

## Safety and publication boundaries

CS304 does not generate images and cannot create a Golden Visual. It does not grant identity approval, global semantic approval, Human Review, Golden quality, branding approval, or publication readiness.

All factual/freshness, entity/identity, sentiment/loser-respect, zero-cost/local-only, semantic-publication, composition, visual-quality, Human Review, Exact Brand/Typography, Genuine Golden materialization, and publication-readiness gates remain downstream or independently enforced.

## Regression coverage

Tests now use a CS303-v2-shaped admission fixture and cover:

- valid sealed admission -> semantic base QA;
- explicit handoff digest binding;
- generated-text semantic rejection;
- candidate byte tamper rejection;
- rejection of the obsolete legacy authority shape;
- rejection when the sealed handoff binding is missing;
- rejection of paid-mode drift;
- rejection of network-enabled/local-only drift;
- semantic verifier identity drift;
- fail-closed existing output directory behavior.

## Genuine Golden status

This change only repairs and strengthens the post-generation QA lineage. It is not evidence of Qwen-Image model loading, CUDA/BF16 inference, a genuine canonical candidate PNG, a composed production PNG, or a Genuine Golden PNG.
