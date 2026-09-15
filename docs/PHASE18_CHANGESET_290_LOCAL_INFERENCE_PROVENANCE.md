# Phase 18 Change Set 290 — Local Inference Provenance

## Purpose

CS290 closes a narrow auditability gap between the CS289 local-only Qwen execution edge and the first successful canonical candidate PNG.

CS289 already forces the actual inference path to use the exact approved local `Qwen/Qwen-Image-2512` snapshot with `$0-local`, native BF16, `local_files_only=True`, and sequential CPU offload. CS262 already byte-binds a successful canonical candidate PNG to the story authorization, prompt, runtime fingerprint, inference settings, and one-shot authorization consumption.

CS290 adds a post-success provenance receipt that binds those two facts together. It does **not** execute inference, approve a visual, create a Golden PNG, or authorize publication.

## Build prerequisites

`build_local_inference_provenance(...)` requires all of the following:

1. `verify_one_shot_canonical_inference(...)` must succeed on the existing CS262 receipt.
2. The receipt must prove `genuine_canonical_inference_executed=true`.
3. All downstream authority fields must still be false:
   - `semantic_approved`;
   - `human_visual_review_approved`;
   - `golden_quality_approved`;
   - `genuine_golden_png_created`;
   - `publication_ready`.
4. Cost mode must remain exactly `$0-local`.
5. The supplied snapshot path must resolve as canonical `snapshots/<full-commit-sha>` and match the approved Qwen revision:
   `2ce1c28560fbc62c9f5531e076b237d3575330a9`.
6. The snapshot directory must exist when the receipt is built.

## Evidence bound by CS290

The receipt records and verifies:

- story snapshot SHA-256;
- approved Qwen model ID and immutable revision;
- `$0-local` cost mode;
- `network_allowed=false`;
- `local_files_only=true`;
- sequential CPU offload requirement;
- resolved local snapshot path and verified revision;
- the exact CS262 canonical inference receipt bytes;
- the exact `canonical_candidate.png` bytes and dimensions;
- the exact repository bytes of:
  - `engine/intelligence/qwen_image_local_inference_runtime.py`;
  - `tools/phase18_run_one_shot_canonical_inference.py`.

The complete receipt is protected by `provenance_sha256`.

## Verification behavior

`verify_local_inference_provenance(...)` fails closed on:

- provenance digest drift;
- model/revision drift;
- zero-cost/network-policy drift;
- downstream authority drift;
- snapshot revision drift;
- canonical receipt byte drift;
- candidate PNG byte or dimension drift;
- cross-story mismatch;
- execution-contract source byte drift.

The verifier does not require the external model cache directory to remain populated after the original host disappears; it revalidates the immutable revision encoded in the canonical snapshot path. The snapshot directory itself is required at build time, when the genuine execution host is still present.

## Canonical CLI integration

`tools/phase18_run_one_shot_canonical_inference.py` now creates `local_inference_provenance.json` automatically after a successful canonical inference and immediately verifies it before returning success.

Therefore a successful CS290-capable CLI run produces:

- `canonical_candidate.png`;
- `canonical_inference_receipt.json`;
- `local_inference_provenance.json`;
- the pre-existing one-shot authorization consumption evidence.

There is still no retry loop and no free-form prompt input.

## Authority boundary

CS290 can attest only:

- `genuine_canonical_inference_executed=true`;
- `local_only_execution_attested=true`.

It always keeps these false:

- `semantic_approved`;
- `human_visual_review_approved`;
- `golden_quality_approved`;
- `genuine_golden_png_created`;
- `publication_ready`.

All factual, identity, sentiment, semantic, visual-quality, Human Review, Brand/Typography, SemanticPublicationGate, Genuine Golden materialization, and publication-readiness gates remain downstream and unchanged.

## Genuine execution status

No production inference result is claimed by this change set. The currently available execution environment still lacks a compatible NVIDIA CUDA/BF16 host, so CS290 is preparatory control/evidence work only until a genuine zero-cost GPU host is available.
