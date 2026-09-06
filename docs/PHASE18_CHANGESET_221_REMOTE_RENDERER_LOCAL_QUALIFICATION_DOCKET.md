# Phase 18 Change Set 221 — Remote Renderer Local Qualification Docket

## Goal

Convert a strong, byte-bound remote renderer research result into a strictly non-authoritative recommendation for *local qualification work only*.

This does **not** promote ZeroGPU output into canonical Golden evidence. Remote pixels, scores, and renderer identity remain research signals. Canonical generation still requires an explicit local model candidate, measured `$0-local` runtime readiness, pinned model/runtime evidence, semantic/layer ownership review, Visual Critic, human review, Golden quality, exact brand/typography integrity, and SemanticPublicationGate.

## Gap closed

Change Set 220 introduced a reproducible research ledger for remote renderer studies. It can identify a blocker-free research leader, but it did not define a safe boundary between:

1. a renderer that looks promising in a remote engineering study; and
2. a renderer that is permitted to enter canonical local qualification.

Without that boundary, a future implementation could accidentally treat `research_leader` as an admission decision.

## Implementation

Added `engine/intelligence/remote_renderer_local_qualification.py`.

The builder:
- accepts only `pul7sar-phase18-remote-renderer-research-ledger-v1`;
- replays the ledger canonical SHA-256 and the leader PNG SHA-256;
- independently replays all five hard blockers instead of trusting `blocker_free=true` alone;
- verifies PNG signature and byte size again before creating a docket;
- requires `$0-remote-zerogpu-study`, `research_only=true`, and `canonical_admission_required=true`;
- rejects any remote Semantic, Golden, canonical, or Publication authority;
- requires a unique research leader;
- requires all hard blockers to remain clear;
- raises the threshold for scarce local qualification time to an average research score of at least `8.5`;
- independently requires geometry integrity `>=8.5`, entity neutrality `>=9.0`, and text/brand cleanliness `>=9.0`;
- produces only a local-measurement docket;
- deliberately leaves `local_model_candidate_id=null`, `local_runtime_qualified=false`, and `canonical_generation_authorized=false`;
- explicitly forbids reuse of remote pixels as canonical evidence; and
- enumerates the canonical local gates that still must be passed.

Added `tools/phase18_build_remote_renderer_local_qualification.py` as a CPU-only CLI.

Added `tests/test_phase18_remote_renderer_local_qualification.py` covering:
- successful non-authoritative qualification docket creation;
- average score below the qualification floor;
- critical geometry score below its floor;
- a hard blocker remaining fatal even if `blocker_free` is maliciously left `true`;
- remote authority drift;
- research-ledger digest tampering;
- research PNG tampering;
- non-PNG bytes even when ledger hashes are recomputed;
- missing research leader; and
- repository path escape.

## Safety and authority

The docket always preserves:
- `research_signal_only=true`;
- `recommended_for_local_measurement=true`;
- `requires_explicit_local_model_candidate=true`;
- `local_runtime_qualified=false`;
- `canonical_generation_authorized=false`;
- `remote_pixels_reusable_as_canonical_evidence=false`;
- `canonical_golden_eligible=false`;
- `semantic_approved=false`;
- `golden_quality_approved=false`;
- `publication_ready=false`;
- canonical cost mode requirement `$0-local`.

## Files

Added:
- `engine/intelligence/remote_renderer_local_qualification.py`
- `tools/phase18_build_remote_renderer_local_qualification.py`
- `tests/test_phase18_remote_renderer_local_qualification.py`
- `docs/PHASE18_CHANGESET_221_REMOTE_RENDERER_LOCAL_QUALIFICATION_DOCKET.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_221.md`

Modified during hardening:
- `engine/intelligence/remote_renderer_local_qualification.py`
- `tests/test_phase18_remote_renderer_local_qualification.py`

Modified existing production/runtime files outside this new isolated research-qualification component:
- none.

Deleted:
- none.
