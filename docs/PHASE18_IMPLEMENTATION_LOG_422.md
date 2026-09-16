# Phase 18 Implementation Log 422 — Golden v6 Offline Transport Provenance

## Scope

Branch: `phase18/story-intelligence` only. `main` was inspected read-only and was not modified.

CS422 closes an auditability gap between the fully replayed ten-evidence Golden v6 bundle and the final readiness/upload transport boundary. Before this change, the upstream artifact replay validated the `local_only_model_receipts` evidence semantically, but the run-bound readiness manifest and transport attestation carried only the generic `evidence_semantics_verified=true` summary. CS422 propagates and re-verifies the explicit no-network/local-only model provenance through the final handoff while keeping every downstream authority closed.

## Modified

- `tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`
  - binds explicit `local_only_model_receipts_verified=true`, `network_download_authorized=false`, and `local_files_only=true` into the source-bound replay and readiness manifest;
  - binds the exact approved Qwen2.5-VL and FLUX.2 model IDs and immutable revisions into readiness;
  - fails closed if the local-only proof or either model identity/revision drifts.
- `tools/phase18_verify_first_genuine_golden_v6_uploaded_artifact_metadata.py`
  - independently requires the explicit local-only/no-network readiness fields;
  - independently requires the exact approved Qwen2.5-VL and FLUX.2 IDs/revisions;
  - propagates those facts into the verified transport result.
- `tools/phase18_attest_first_genuine_golden_v6_uploaded_artifact.py`
  - refuses attestation unless transport verification preserves local-only/no-network provenance;
  - records local-only/no-network status and exact model IDs/revisions in the immutable transport attestation;
  - continues to leave Human Visual Review, Golden Quality, publication, and Seeds 2–4 authority closed.
- `tests/test_phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`
  - covers readiness propagation and rejection of local-only/network/model-revision drift.
- `tests/test_phase18_first_genuine_golden_v6_artifact_ready_manifest.py`
  - aligns the readiness fixture with the explicit offline/model provenance contract and tests tamper rejection.
- `tests/test_phase18_verify_first_genuine_golden_v6_uploaded_artifact_metadata.py`
  - covers transport rejection of network authority, non-local resolution, and Qwen/FLUX identity/revision drift.
- `tests/test_phase18_attest_first_genuine_golden_v6_uploaded_artifact.py`
  - covers preservation of offline provenance in the final transport attestation and rejects network-enabled readiness.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_422.md`

## Deleted

None.

## Gate preservation

CS422 does not change prompts, seeds, generation parameters, model selections, approved model revisions, semantic publication policy, factual/identity/sentiment checks, visual-quality criteria, or GPU resource floors. It performs no model download and introduces no network fallback. `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` remain unchanged in the Golden workflow.

The following authorities remain false throughout readiness and transport:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Testing

The repository CI is expected to exercise syntax/discovery and the affected regression suites on the exact CS422 branch HEAD. CS421 baseline run `34694905968` was terminal-green before CS422 began. CS422 must not be described as terminal-green until the new HEAD receives a successful terminal verification run.

## Remaining blocker to the first genuine Golden PNG

No PNG is fabricated by this change. Candidate 1 still requires a compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the canonical local Hugging Face cache. Model downloads remain unauthorized for the `$0-local` Golden path.
