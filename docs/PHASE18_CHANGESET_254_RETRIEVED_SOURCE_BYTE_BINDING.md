# Phase 18 Change Set 254 — Retrieved Source Byte Binding

## Purpose

Change Set 253 introduced a deterministic source-backed story manifest and six-gate evidence compiler, but its `content_sha256` field was still a declared value. Change Set 254 closes that provenance gap before the first genuine fresh-story replay.

The new CPU-only binding layer requires the already retrieved source document bytes to exist under an explicit source root. It hashes those bytes itself and emits the exact Change Set 253 manifest schema. A separate receipt records each relative capture path, byte size, and SHA-256.

## Safety boundary

This change does not retrieve from the network and does not claim a source is true merely because bytes were captured. It proves only that the story manifest's source digest was derived from concrete local bytes rather than hand-authored metadata.

The receipt remains fail-closed for semantic replay, fresh-story passage, canonical generation, inference, Golden PNG creation, and publication.

## Files

Added:

- `engine/intelligence/qwen_image_retrieved_source_byte_binding.py`
- `tests/test_phase18_qwen_image_retrieved_source_byte_binding.py`
- `tools/phase18_bind_retrieved_source_bytes.py`
- `docs/PHASE18_CHANGESET_254_RETRIEVED_SOURCE_BYTE_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_254.md`

Deleted: none.

## New invariants

- capture paths must be relative to the supplied source root;
- `..` and absolute path escapes are rejected;
- captures must exist and be non-empty;
- duplicate source IDs are rejected;
- duplicate capture paths are rejected;
- SHA-256 and byte size are computed from the exact captured bytes;
- the emitted manifest uses `pul7sar-phase18-source-backed-story-manifest-v1` and is therefore directly consumable by Change Set 253;
- no downstream authority is granted by byte binding.

## Remaining path

`genuine retrieved bytes -> Change Set 254 binding -> Change Set 253 six evidence files -> Change Set 252 six production receipts -> Change Set 237 freshness admission -> Change Set 238 semantic replay -> explicit generation authorization -> qualified zero-cost CUDA runtime -> genuine Qwen PNG -> semantic/layer QA -> Visual Critic -> human review -> Golden threshold -> exact brand/typography -> SemanticPublicationGate`
