# PUL7SAR Phase 18 — Change Set 189

## Canonical Pre-Model FLUX.2 Offload Lock

### Goal

Close a remaining first-Golden execution gap in the current Golden Editorial v6 path: prove that the installed Diffusers `Flux2KleinPipeline` exposes a safe CPU-offload mode **before** the model-cache/resource/runtime/semantic path is allowed to begin Candidate 1 model work.

### Why this matters

Phase 18 already had a standalone offload capability probe. It proves whether the installed Diffusers runtime exposes `enable_sequential_cpu_offload` and/or `enable_model_cpu_offload`, and it intentionally requires sequential CPU offload on low-VRAM hosts. The current v6 resource lock, however, did not bind that pre-model capability proof into its preferred first-Golden entrypoint.

A compatible CUDA/BF16 host could therefore satisfy GPU/RAM/cache checks and only discover an unsafe or missing offload API later during FLUX pipeline construction. On constrained hosts this risks wasting the rare GPU window before any genuine PNG is produced.

### Implemented

#### Added `tools/phase18_colab_first_genuine_offload_locked.py`

- Runs Phase 18 GPU host qualification first.
- Runs `phase18_preflight_flux2_offload.py` before entering the existing Golden v6 resource/model-cache/runtime/semantic lock.
- Requires `$0-local`, CUDA, native BF16 and the approved FLUX.2 Klein 4B identity.
- Requires a valid live-VRAM-qualified host receipt.
- Requires low-VRAM hosts to prove `sequential_cpu` offload.
- Allows `model_cpu` only on higher-VRAM hosts when that API is actually available.
- Rejects any preflight authority drift: no model load, download, queue mutation, PNG creation, semantic approval, Golden approval or publication approval may be claimed by this preflight.
- Replays host identity against the inner Golden v6 resource-lock host evidence after Candidate 1 staging.
- Seals the host qualification, offload preflight and inner resource lock by SHA-256.
- Keeps human approval, Golden approval, publication readiness and Seeds 2–4 closed.

#### Added `.github/workflows/phase18-first-genuine-golden-v6-offload.yml`

- Manual `workflow_dispatch` only.
- Self-hosted CUDA/BF16 Phase 18 runner only.
- Immutable dispatch SHA with complete ancestry.
- Reattaches `phase18/story-intelligence` at the exact dispatch SHA.
- Reads `main` only to prove merge-base and reject any `main.py` modification in the Phase 18 diff.
- Never installs or replaces PyTorch automatically.
- Executes the new pre-model offload-locked wrapper.
- Replays SHA-256 for the offload host receipt, offload preflight receipt and inner resource-lock receipt before artifact upload.
- Rechecks low-VRAM sequential-offload policy and all downstream authority closures.

### Tests

Added CPU-safe regression coverage for:

- low-VRAM sequential-offload enforcement;
- high-VRAM verified model-CPU fallback;
- authority-drift rejection;
- total-VRAM binding between host qualification and offload preflight;
- ordering `GPU qualification -> offload preflight -> inner Golden v6 resource path`;
- immutable/manual/self-hosted workflow behavior;
- offload/resource evidence replay before artifact upload;
- continued closure of Human/Golden/Publication/Seeds authority.

### Files added

- `tools/phase18_colab_first_genuine_offload_locked.py`
- `.github/workflows/phase18-first-genuine-golden-v6-offload.yml`
- `tests/test_phase18_first_genuine_golden_v6_offload_lock.py`
- `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py`
- `docs/PHASE18_CHANGESET_189_CANONICAL_PREMODEL_OFFLOAD_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_189.md`

### Files modified

- None. This change set is additive so the already-qualified v6 resource path remains intact.

### Files deleted

- None.

### Gates preserved

No factual, identity, sentiment/neutrality, zero-cost, semantic-publication or visual-quality gate was weakened. FLUX/Qwen revisions, native BF16, GPU/RAM/cache/runtime locks, semantic/layer ownership, Golden 8.5 minimum / 9.0+ elite target, exact brand/typography integrity and SemanticPublicationGate remain fail-closed.

### Genuine Golden PNG status

No genuine Candidate 1 PNG is claimed by this change set. The remaining blocker is still an actually available self-hosted host satisfying the full CUDA/BF16/live-VRAM/live-RAM/local-runtime/pinned-model/runtime-stability/zero-cost requirements.
