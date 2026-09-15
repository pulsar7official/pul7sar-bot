# Phase 18 Implementation Log — CS425

## Scope

CS425 advances the first genuine Golden Editorial v6 Candidate 1 toward a safe GPU execution by closing a provenance gap in the JIT replay path. All work is restricted to `phase18/story-intelligence`; `main` remains read-only.

## Reviewed baseline

- Starting Phase 18 HEAD: `8e2723d803f86d587d00988945d0e156490ebc0e` (CS424).
- `Phase 18 Story Intelligence Verification` run `34703303048` completed successfully on that exact SHA.
- CS424 therefore entered CS425 terminal-green.
- The JIT workflow already enforced `$0-local`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, CUDA-enabled PyTorch, at least one CUDA device, and native BF16 before Candidate 1 execution.

## Gap found

The JIT final lock cryptographically replayed its offload/resource/staging/JIT evidence and PNG binding, but did not independently carry and re-verify the explicit Qwen/FLUX local-only provenance already present in the inner Golden resource lock. This meant the JIT handoff was weaker than the main Golden v6 provenance chain: a future change could theoretically preserve file hashes while dropping the explicit outer contract that network model resolution is unauthorized and only the approved immutable model revisions are acceptable.

No evidence was found that a network download actually occurred. This change is preventative and fail-closed.

## Modified

### `tools/phase18_colab_first_genuine_jit_replay_locked.py`

- Imports the approved immutable Qwen2.5-VL and FLUX.2 model IDs/revisions from the canonical revision module.
- Adds `_validate_local_only_provenance()`.
- Requires the inner resource lock to prove:
  - `local_only_model_receipts_bound=true`
  - `network_download_authorized=false`
  - `local_files_only=true`
  - exact approved Qwen model ID/revision
  - exact approved FLUX model ID/revision
- Replays the `local_only_model_receipts` evidence record by path, SHA-256, and byte size.
- Re-validates the receipt schema/status, `$0-local`, no-network/local-only policy, exact approved model provenance, and closed generation/publication/Seeds authorities.
- Adds the local-only receipt as a fifth SHA-256-bound evidence record in the JIT lock.
- Carries explicit local-only provenance into the final JIT lock:
  - `local_only_model_receipts_verified=true`
  - `network_download_authorized=false`
  - `local_files_only=true`
  - exact Qwen/FLUX IDs and immutable revisions
- Leaves human visual review, Golden quality approval, publication, and Seeds 2–4 authorization false.

### `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`

- Extends the final pre-upload replay to require the new explicit local-only provenance fields.
- Expands the expected JIT evidence set from four records to five by requiring `local_only_model_receipts`.
- Re-opens and semantically validates that receipt after SHA-256 replay rather than trusting a Boolean summary alone.
- Re-validates exact Qwen/FLUX IDs/revisions and rejects any network-authority or downstream-authority drift.
- Keeps the existing runner, branch isolation, offline environment, CUDA runtime, and native BF16 gates unchanged.

## Added

### `tests/test_phase18_first_genuine_golden_v6_jit_local_only_provenance.py`

Regression coverage now proves:

- the exact approved local-only contract is accepted;
- network-download authority drift is rejected;
- `local_files_only=false` is rejected;
- missing/unbound local-only provenance is rejected;
- Qwen and FLUX revision/identity drift is rejected;
- generation, publication, or Seeds authority drift in the receipt is rejected;
- the workflow replays local-only evidence before artifact upload;
- offline flags, branch isolation, and downstream-authority closure remain present.

## Deleted

None.

## Intentionally unchanged

- No prompt changes.
- No seed changes.
- No image-generation parameter changes.
- No approved model selection or immutable revision changes.
- No dependency changes.
- No factual, entity/identity, sentiment, semantic-publication, or visual-quality gate weakening.
- No write, merge, rebase, reset, or ref update to `main`.

## Validation state

The functional changes and regression suite were committed to `phase18/story-intelligence`. Repository CI must complete on the final CS425 HEAD before CS425 can be called terminal-green.

## Remaining blocker to the first genuine Golden PNG

CS425 does not fabricate or substitute a PNG. A genuine Candidate 1 still requires execution on a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the canonical local Hugging Face cache. Network model download remains forbidden by the `$0-local` contract.

The downstream authorities remain closed until genuine generation, evidence replay, and human visual review succeed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`
