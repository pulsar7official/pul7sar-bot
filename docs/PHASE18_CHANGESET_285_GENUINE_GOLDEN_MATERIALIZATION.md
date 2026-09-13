# Phase 18 Change Set 285 — Genuine Golden Materialization

## Purpose

CS285 is the first stage allowed to create a `genuine_golden_visual.png` artifact, but only as an exact byte-for-byte materialization of the already-approved composed PNG after the repository's real CS284 `SemanticPublicationGate` execution returns `semantic_publication_allowed=true`.

CS285 does **not** run Qwen inference, does not compose pixels, does not retouch, resize, recolor, crop, sharpen, compress, or otherwise mutate the image. It is an authority/materialization layer, not an image-generation layer.

## Required upstream authority

The CS284 receipt must re-verify successfully and must prove all of the following:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `semantic_publication_execution_requested=true`
- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true`
- `semantic_publication_failures=[]`
- `genuine_golden_png_created=false`
- `publication_ready=false`

Because CS284 is itself downstream of the Phase 18 factual, identity, sentiment/loser-respect, zero-cost, semantic, visual-quality, Human Review, and exact Brand/Typography chain, CS285 cannot bypass those gates without invalidating the upstream receipt chain.

## Exact-byte artifact rule

CS285 re-opens the repository-relative composed PNG binding from CS284 and verifies SHA-256 and byte size. It then validates the PNG container itself:

- canonical PNG signature;
- first chunk is a valid IHDR;
- positive image dimensions;
- valid chunk framing;
- CRC verification for every parsed chunk;
- exactly terminal IEND with no trailing bytes.

The output `genuine_golden_visual.png` is written from the source bytes without pixel decoding or re-encoding. The materialized SHA-256 and byte size must exactly match the CS284 composed candidate binding.

## Authority boundary

A valid CS285 receipt may assert:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true`
- `byte_identity_preserved=true`
- `genuine_golden_png_created=true`

It must continue to assert:

- `publication_ready=false`

Publication readiness therefore remains a separate downstream authority. Genuine-Golden creation is evidence that the approved bytes were materialized, not permission to publish them.

## Fail-closed behavior

CS285 rejects:

- any CS284 receipt that did not receive real repository-gate publication allowance;
- any CS284 receipt carrying semantic-publication failures;
- premature Golden or publication-ready state in CS284;
- source receipt drift;
- source PNG path/hash/size drift;
- malformed PNG signature, chunks, CRC, IHDR, or IEND;
- any mismatch between source and materialized bytes;
- output-directory reuse.

The CLI intentionally exposes no `--approve`, `--allowed`, `--golden`, `--publication-ready`, pixel-edit, or image-substitution argument.

## Runtime reality

This change set creates the authority capable of materializing the first genuine Golden artifact once a real production CS284 receipt exists. It does not claim that such a receipt or PNG exists in the current CPU-only automation runtime. Genuine upstream CS262 Qwen-Image inference still requires a compatible zero-cost CUDA/BF16 environment.
