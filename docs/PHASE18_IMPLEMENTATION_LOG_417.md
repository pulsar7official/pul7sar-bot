# Phase 18 Implementation Log 417 — Golden v6 Local-Only Evidence Replay Alignment

## Scope

Branch: `phase18/story-intelligence` only. `main` was inspected read-only and was not modified, merged, rebased, reset, or used as a write target.

Baseline: CS416 at `84c7b9fdaa5761d74c5658fe044e5c338d44c16e` was confirmed terminal-green by Phase 18 Story Intelligence Verification run `34676677624` before CS417 work began.

## Defect found

CS416 correctly added `local_only_model_receipts` to the final First Genuine Golden v6 resource-lock evidence and bound its SHA-256/byte count. However, two downstream replay consumers still enforced the pre-CS416 nine-record evidence set:

1. `.github/workflows/phase18-first-genuine-golden-v6.yml`
2. `tools/phase18_verify_first_genuine_golden_v6_artifact.py`

On a compatible CUDA/BF16 host this would allow the resource lock to complete, then fail closed during replay because the legitimate tenth evidence record made `set(evidence) != expected`. That was a real execution blocker before Candidate 1 could complete its full provenance chain.

The fix preserves the new evidence. It does not remove or relax it.

## Modified

### `tools/phase18_verify_first_genuine_golden_v6_artifact.py`

- Added `local_only_model_receipts` to the exact expected evidence set.
- The generic evidence replay now verifies its bound path, SHA-256, and byte count alongside all other evidence.
- Added semantic replay requirements for:
  - schema `pul7sar-phase18-local-only-model-receipt-verification-v1`
  - status `PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED`
  - `cost_mode == "$0-local"`
  - `network_download_authorized == false`
  - `local_files_only == true`
  - exact approved Qwen2.5-VL model ID/revision
  - exact approved FLUX.2 model ID/revision
  - `generation_authorized == false`
  - `publication_ready == false`
  - `seeds_2_to_4_authorized == false`
- Artifact replay now verifies ten bound evidence files.

### `.github/workflows/phase18-first-genuine-golden-v6.yml`

- Added `local_only_model_receipts` to the exact replay evidence set.
- Added semantic replay of the bound local-only receipt after Qwen/FLUX cache replay.
- Enforces the same no-network/local-files-only/model-identity/downstream-authority contract from the evidence actually bound by the resource-lock receipt.
- Preserved the pre-existing independent local-only verifier step before replay.

## Added

### `tests/test_phase18_first_genuine_golden_v6_local_only_evidence_replay.py`

Regression coverage asserts that:

- Golden v6 workflow replay includes the tenth bound evidence record.
- Workflow replay checks its local-only/no-network semantics and exact model identities.
- Artifact verifier requires and semantically validates the same evidence.
- Human Visual Review, Golden Quality, publication, and Seeds 2–4 authorities remain fail-closed.

### This implementation log

`docs/PHASE18_IMPLEMENTATION_LOG_417.md`

## Deleted

None.

## Intentionally unchanged

- Qwen2.5-VL model ID and immutable revision.
- FLUX.2 model ID and immutable revision.
- Generation prompt and visual art direction.
- Candidate 1 generation parameters.
- Factual, entity/identity, sentiment, semantic-publication, layer-ownership, and visual-quality gates.
- Human Visual Review authority.
- Golden Quality authority.
- Publication authority.
- Seeds 2–4 authority.
- `$0-local` policy and prohibition on network model downloads.
- `main`.

## Validation

- CS416 baseline verification run `34676677624`: `completed / success` before this change set.
- CS417 adds targeted regression coverage for the exact mismatch discovered between the resource-lock producer and its two downstream replay consumers.
- Full branch CI status must be evaluated on the final CS417 HEAD; CS417 is not called terminal-green until that exact HEAD succeeds.

## First Genuine Golden PNG status

No Golden Visual PNG was fabricated or claimed in CS417.

The non-substitutable execution requirement remains a compatible self-hosted NVIDIA host carrying the workflow labels:

`self-hosted + linux + x64 + gpu + cuda + bf16 + pul7sar-phase18`

It must provide CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in canonical local Hugging Face cache. Network download is not an allowed workaround because the path remains `$0-local` and fail-closed.

Until a genuine Candidate 1 run reaches Human Visual Review, the following remain false:

- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`
- `seeds_2_to_4_authorized`
