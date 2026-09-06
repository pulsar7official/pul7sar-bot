# PUL7SAR Phase 18 — Change Set 191
## Actual FLUX Offload Postflight Binding

### Purpose

Close the remaining offload provenance gap before the first genuine Golden Editorial v6 Candidate 1 can be treated as human-review evidence.

Change Set 189 proved which Diffusers CPU-offload mode was safe before model work. Change Set 190 made the real FLUX executor persist the mode that the constructed pipeline actually used. Change Set 191 binds those two facts together and fails closed unless they are identical.

### Added

- `engine/intelligence/golden_offload_provenance.py`
  - Replays the pre-model offload receipt and the strict Golden staging receipt.
  - Replays the staging-bound executor-result SHA-256.
  - Requires the executor to prove the pinned FLUX revision, `$0-local`, native BF16 Golden precision, and `offload_mode_proven=true`.
  - Requires `actual_offload_mode` to equal the preflight `selected_safe_mode` exactly.
  - Keeps semantic, Golden-quality and publication authority closed.

- `tests/test_phase18_golden_offload_provenance.py`
  - Accepts a correctly bound sequential CPU execution.
  - Rejects selected/actual mode mismatch.
  - Rejects executor byte tampering after staging SHA binding.
  - Rejects an executor that does not prove its actual mode.
  - Rejects authority drift in the pre-model receipt.

### Modified

- `tools/phase18_colab_first_genuine_offload_locked.py`
  - Runs actual-execution offload provenance verification after the inner Golden v6 resource/runtime/semantic lock.
  - Persists `first-genuine-golden-v6-actual-offload-provenance.json`.
  - Adds that receipt to the SHA-256 evidence set.
  - Upgrades the final receipt to `pul7sar-first-genuine-golden-v6-offload-lock-v2`.
  - Requires and records `actual_offload_mode_bound=true` and exact equality between selected and actual offload mode.

- `.github/workflows/phase18-first-genuine-golden-v6-offload.yml`
  - Replays the new actual-offload provenance receipt before artifact upload.
  - Re-hashes the executor result referenced by that receipt.
  - Requires the executor's `actual_offload_mode` and `offload_mode_proven` fields to match the pre-model selection.
  - Replays the immutable FLUX revision again at workflow level.

- `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py`
  - Locks the new v2 receipt schema/status.
  - Requires actual-offload evidence in the workflow evidence set.
  - Requires selected/preflight mode equality with actual executor mode.

### Deleted

Nothing.

### Gates preserved

No factual, entity/identity, sentiment/neutrality, zero-cost, semantic-publication, visual-quality, model-revision, precision, resource, or Golden-quality gate was weakened. Seeds 2–4 remain unauthorized until Candidate 1 exists and is visually accepted.

### Genuine PNG status

No genuine Golden Editorial v6 Candidate 1 PNG is claimed by this change. Real generation remains dependent on an actually available self-hosted host that satisfies all current CUDA/BF16/VRAM/RAM/cache/runtime/offload and `$0-local` requirements.
