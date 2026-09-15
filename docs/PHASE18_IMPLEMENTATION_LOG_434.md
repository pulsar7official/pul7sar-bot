# Phase 18 Implementation Log — CS434

## Change set

**CS434 — First-Golden software/runtime compatibility blocker alignment**

Branch: `phase18/story-intelligence` only. `main` remains read-only and is not modified, merged, rebased, reset, or updated by this change set.

## Why this change was necessary

CS433 made the early first-Golden execution blocker probe agree with the authoritative GPU, live-VRAM, host-RAM, local-model-resolution, and working-filesystem-headroom policies. One material late-failure gap remained: a self-hosted NVIDIA host could satisfy those resource/cache checks and still fail only after entering the heavier resource-lock path because its installed generation software stack was outside the already-approved first-Golden runtime contract.

The project already owns the strict runtime contract in `engine/intelligence/generation_runtime_fingerprint.py`; CS434 reuses that contract rather than inventing a second version policy.

The approved runtime fingerprint currently requires exact `transformers==4.56.2` and `Pillow==11.3.0`, range-qualified `diffusers`, `accelerate`, `safetensors`, and `huggingface_hub`, records `tokenizers`, and requires a valid CUDA-enabled PyTorch/GPU runtime. Missing or incompatible packages fail closed.

## Modified

### `tools/phase18_probe_first_golden_execution_blocker.py`

- Imports and reuses `capture_generation_runtime_fingerprint()`.
- Adds a non-mutating `_generation_runtime_qualification()` stage before the heavier Golden execution path.
- Adds fail-closed blocker codes:
  - `GENERATION_RUNTIME_NOT_READY`
  - `GENERATION_RUNTIME_ZERO_COST_DRIFT`
  - `GENERATION_RUNTIME_AUTHORITY_DRIFT`
- Records a `generation_runtime` diagnostic section containing the validated fingerprint identity, Python/machine data, package versions, and CUDA/PyTorch contract when ready.
- Preserves `$0-local` and refuses any runtime evidence that grants generation/publication authority.
- Advances the diagnostic schema from `pul7sar-phase18-first-golden-execution-blocker-probe-v4` to `...-v5`.
- Does not load Qwen or FLUX and does not generate an image.

### `tests/test_phase18_first_golden_execution_blocker_probe.py`

- Extends the deterministic ready fixture with approved generation-runtime evidence.
- Verifies readiness now requires a compatible software/runtime contract in addition to CUDA/BF16/resources/headroom/exact local snapshots.
- Adds regression coverage proving an incompatible generation software runtime blocks before authoritative preflight.
- Adds regression coverage proving runtime cost-mode drift or authority drift blocks readiness.
- Keeps existing CUDA, native-BF16, live-VRAM, RAM, cache-headroom, immutable-snapshot, local-resolution, and zero-cost regressions.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_434.md`

## Deleted

None.

## Intentionally unchanged

- Golden prompt text
- Candidate 1 seed
- Canvas or generation parameters
- Qwen2.5-VL approved model ID/revision
- FLUX.2 approved model ID/revision
- Factual/entity/identity gates
- Losing-side/result sentiment-neutrality rules
- SemanticPublicationGate and downstream publication authority
- Human visual review requirement
- Golden quality threshold
- Seeds 2–4 authorization
- `$0-local` policy
- Offline-only model resolution and no-network-download policy
- Native BF16 requirement and no FP16/FP32 substitution

## Test intent

The standard Phase 18 Story Intelligence Verification workflow must discover the updated `unittest` suite and prove syntax/import/discovery plus the existing Phase 18 regression matrix on the exact CS434 branch SHA.

CS434 specifically protects against wasting the first compatible GPU opportunity on a late software-stack mismatch after resource/cache qualification has already succeeded.

## First genuine Golden PNG status

No PNG is fabricated or claimed by CS434. The first genuine Candidate 1 remains blocked until an actual self-hosted NVIDIA execution host is available with all of the following simultaneously:

- CUDA-enabled PyTorch and at least one real CUDA device
- native BF16
- approved GPU identity/compute capability and sufficient total/live-free VRAM
- sufficient currently available system RAM
- at least the approved post-cache working filesystem headroom
- software/runtime packages satisfying the existing `generation_runtime_fingerprint` contract
- exact approved immutable Qwen2.5-VL snapshot locally resolvable
- exact approved immutable FLUX.2 snapshot locally resolvable
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `PUL7SAR_PHASE18_COST_MODE=$0-local`
- no network model download

Human review, Golden acceptance, publication, and Seeds 2–4 remain closed until the real PNG exists and all downstream gates pass.