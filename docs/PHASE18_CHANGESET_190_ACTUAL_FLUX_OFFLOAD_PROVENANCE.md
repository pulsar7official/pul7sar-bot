# PUL7SAR Phase 18 — Change Set 190
## Actual FLUX Offload Provenance

### Purpose

The pre-model offload gate introduced in Change Set 189 proves which Diffusers CPU-offload mode is safe and available before model work. This change closes the next gap: the real FLUX executor must also report which offload mode the constructed pipeline actually used.

A preflight capability is not sufficient evidence by itself. Candidate 1 must not later be treated as a genuine Golden result if the real pipeline silently used an unproven/no-offload path.

### Implemented

- `tools/phase18_flux2_execute.py`
  - Added a fail-closed `_verified_execution_metadata()` check immediately after the real Diffusers backend returns.
  - Requires the pipeline result to report the exact approved immutable FLUX revision.
  - Requires the actual runtime offload mode to be either `sequential_cpu` or `model_cpu`.
  - Rejects missing, `none`, unknown, or unsafe modes before PNG normalization/proof registration continues.
  - Adds `actual_offload_mode`, `offload_mode_proven=true`, and the verified `model_revision` to the durable executor result.

- `tests/test_phase18_flux2_actual_offload_provenance.py`
  - Accepts proven sequential CPU offload.
  - Accepts proven model CPU offload when that is what the runtime reports.
  - Rejects absent/unsafe offload modes.
  - Rejects immutable model-revision drift.
  - Rejects missing execution metadata.

### Safety / policy preservation

No quality or publication gate was relaxed. The change does not alter prompt, seed, canvas, inference steps, model identity, pinned revision, BF16 policy, `$0-local`, factual/identity/sentiment gates, Qwen semantic gates, Golden quality thresholds, exact brand/typography integrity, or SemanticPublicationGate.

### Next binding step

The newly durable `actual_offload_mode` is intended to be replayed against the pre-model offload receipt in the canonical first-Golden v6 postflight, so the future genuine Candidate 1 can prove both:

1. the safe mode was available before model work; and
2. the real pipeline actually used that same mode during generation.
