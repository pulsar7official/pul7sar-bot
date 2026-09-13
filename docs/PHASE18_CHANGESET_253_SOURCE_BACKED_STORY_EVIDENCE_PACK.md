# Phase 18 Change Set 253 — Source-Backed Story Evidence Pack

## Purpose

Change Set 253 removes the remaining hand-authored-evidence gap between the six production-backed semantic verifiers and Change Set 252's production receipt executor.

The canonical input is one UTF-8 JSON story manifest. Its exact bytes are the story snapshot. The compiler SHA-256 binds those bytes and injects the same story digest into all six gate evidence files in canonical order.

## Source provenance contract

A manifest must contain at least one source document and an explicit `story_source_ids` set. Every source record requires:

- stable `source_id`;
- HTTPS source URL;
- publisher;
- UTC publication timestamp;
- UTC retrieval timestamp not earlier than publication;
- SHA-256 of the retrieved source content.

Fact claims may reference only declared source IDs. Every `fact` claim requires one declared source. Every canonical identity record requires one or more declared identity source IDs. Any emotional attribution allowed through sentiment evidence must be paired with a declared source ID in the manifest before the compiler emits the existing sentiment verifier's attribution list.

This compiler validates provenance structure; it does not claim that a URL or source content is truthful merely because metadata exists. Independent production gate semantics remain authoritative.

## Six evidence outputs

The compiler emits exactly, and in canonical order:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

Each emitted file receives the appropriate existing production evidence schema, gate ID, and the same byte-bound story snapshot SHA-256.

A separate pack receipt records each evidence file path, SHA-256 and byte size while explicitly keeping semantic replay, fresh-story admission, generation, inference, Golden creation and publication authority false.

## Fail-closed properties

The compiler rejects missing/empty/malformed manifests, duplicate/unknown source IDs, non-HTTPS source URLs, invalid source-content hashes, impossible publication/retrieval ordering, unknown factual source references, unknown identity source references, unknown emotional-attribution source references, non-canonical gate order and non-empty output directories.

It does not execute CUDA, load Qwen weights, generate pixels, mark semantic replay complete, mark fresh story gates passed, approve human review, score Golden quality, apply final branding or publish.

## Test boundary

The regression suite contains a deliberately synthetic `example.org` fixture only to prove that the compiled six-file pack can feed all six real production verifiers through Change Set 252. That fixture is never represented as a genuine news story and grants no runtime or publication authority.
