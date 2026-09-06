# Phase 18 Change Set 286 — Genuine Golden Publication Readiness

## Purpose

CS286 is the final fail-closed authority that may set `publication_ready=true` for a Genuine Golden Visual. It does not generate, edit, re-encode, upload, or publish an image. It consumes only a successfully re-verified CS285 materialization receipt and the exact byte-bound `genuine_golden_visual.png` produced by that stage.

## Required upstream authority

CS286 re-verifies CS285 and requires all of the following to remain true:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true`
- `byte_identity_preserved=true`
- `genuine_golden_png_created=true`

The CS285 receipt must still carry `publication_ready=false`; otherwise CS286 rejects it as premature state.

CS286 also requires the CS285 non-mutation policy to remain intact:

- `pixel_mutation_forbidden=true`
- `source_must_be_cs284_allowed_exact_png=true`
- `genuine_golden_creation_does_not_set_publication_ready=true`

## Exact-byte requirement

The stage re-opens both the approved composed source PNG and the materialized Genuine Golden PNG through repository-relative SHA-256/byte-size bindings. Their bytes must be identical. The Golden PNG is structurally re-validated and its dimensions must still match CS285.

No pixel or metadata transformation occurs in CS286.

## Final authority

Only after all checks succeed does CS286 emit a receipt with:

- `genuine_golden_png_created=true`
- `publication_ready=true`

This is readiness evidence only. CS286 performs no network publication, social posting, upload, or external side effect.

## Fail-closed properties

CS286 rejects:

- a CS285 receipt that no longer verifies;
- missing semantic-publication allowance;
- missing Genuine Golden creation authority;
- lost byte-identity authority;
- weakened CS285 pixel-mutation policy;
- source or Golden PNG byte drift;
- PNG dimension drift;
- a forged or mutated CS286 receipt;
- an output directory outside the repository root;
- output-directory reuse.

The CLI exposes build/verify operations only. It has no `--approve`, `--allowed`, `--golden`, `--publication-ready`, image-substitution, or pixel-edit override.

## Production blocker

This contract closes the downstream publication-readiness gap, but it does not fabricate the upstream production artifact. A real run still requires genuine CS262 Qwen-Image inference on a compatible zero-cost NVIDIA CUDA/BF16 environment, followed by every existing factual, identity, sentiment, semantic, composition, visual-quality, human-review, brand/typography, SemanticPublicationGate, and CS285 materialization stage.
