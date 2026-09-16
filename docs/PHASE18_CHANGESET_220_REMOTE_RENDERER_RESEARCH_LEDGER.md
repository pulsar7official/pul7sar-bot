# Phase 18 Change Set 220 — Remote Renderer Research Ledger

## Goal

Make the isolated ZeroGPU renderer study useful for evidence-driven renderer research without allowing any remote result to enter the canonical `$0-local` Golden path.

The study lane already produced entity-neutral, platform-name-free, PNG/SHA-bound engineering outputs. The remaining research gap was comparative provenance: a human could score remote images, but there was no canonical research-only ledger proving that the scores referred to the same PNG bytes emitted by the benchmark report.

## Implemented

Added `engine/intelligence/remote_renderer_research_ledger.py`.

The ledger:
- accepts only `pul7sar-phase18-remote-renderer-benchmark-v3` reports;
- requires `$0-remote-zerogpu-study`;
- requires engineering-only, entity-neutral, non-canonical authority closure;
- reopens each output PNG, verifies the PNG signature, SHA-256, byte size, seed, and prompt SHA continuity;
- requires a human-review document bound to the exact output SHA;
- records six 0–10 research dimensions: editorial composition, photorealism, geometry integrity, scene continuity, entity neutrality, and text/brand cleanliness;
- applies hard blockers for broken geometry, pseudo-text, identifiable entity cues, multi-scene/collage output, or generated brand/crest;
- allows a `research_leader` only when the result is blocker-free and meets the research score floor;
- still forces `canonical_golden_eligible=false`, `semantic_approved=false`, `golden_quality_approved=false`, and `publication_ready=false`.

Added `tools/phase18_build_remote_renderer_research_ledger.py` as a CPU-only replay/build utility.

Added `tests/test_phase18_remote_renderer_research_ledger.py` covering:
- byte-bound ledger creation;
- PNG tampering after benchmark generation;
- hard blockers defeating a 9.9 research score;
- human-review/output SHA mismatch;
- forbidden canonical authority drift; and
- repository path escape.

## Why this materially reduces the Golden gap

A remote ZeroGPU result is still not Golden evidence and can never be promoted directly. However, while compatible canonical CUDA execution is unavailable, this ledger lets PUL7SAR compare renderer behavior using exact image bytes rather than memory or subjective notes. A renderer can be identified as a research leader for future local qualification only after geometry, pseudo-text, entity neutrality, composition, and photorealism are reviewed against the same SHA-bound PNG.

This reduces the chance of spending a future canonical GPU session qualifying a renderer that already exhibits obvious geometry, pseudo-text, collage, or identity-cue failures in the isolated research lane.

## Preserved gates

Unchanged and fail-closed:
- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- canonical `$0-local` execution policy;
- generated text/branding/exact facts/entity marks/exact sport geometry exclusions;
- Semantic/Layer Ownership gates;
- byte-bound Visual Critic hard failures;
- explicit Human Review;
- Golden quality floor 8.5 and 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity; and
- SemanticPublicationGate.

The remote research ledger itself has no canonical admission, Golden, semantic, or publication authority.

## Files

Added:
- `engine/intelligence/remote_renderer_research_ledger.py`
- `tools/phase18_build_remote_renderer_research_ledger.py`
- `tests/test_phase18_remote_renderer_research_ledger.py`
- `docs/PHASE18_CHANGESET_220_REMOTE_RENDERER_RESEARCH_LEDGER.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_220.md`

Modified:
- none in production/runtime paths.

Deleted:
- none.
