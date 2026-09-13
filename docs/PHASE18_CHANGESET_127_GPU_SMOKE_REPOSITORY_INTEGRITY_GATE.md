# PUL7SAR Phase 18 — Change Set 127

## GPU Smoke Repository Integrity Gate

This change set applies to `phase18/story-intelligence` only. `main` is not modified.

## Problem

Change Set 126 moved the CPU repository/reference-integrity gate into `tools/phase18_first_png.py`, but the self-hosted GPU smoke workflow still began by probing CUDA and installing GPU-side dependencies before independently proving repository-side integrity. Because the workflow is an expensive/rare execution path, it should fail before any GPU probe, model preparation or queue work when the repository/reference contract is already invalid.

## Implementation

`.github/workflows/phase18-gpu-smoke.yml` now runs `tools/phase18_preflight_repository_integrity.py` immediately after branch isolation and before the CUDA PyTorch probe, dependency installation, Qwen preparation, FLUX cache/readiness or Candidate 1 generation.

The workflow fail-closes unless the receipt proves all of the following:

- schema `pul7sar-phase18-pre-gpu-repository-integrity-v1`;
- branch `phase18/story-intelligence`;
- `ready=true` with no blockers;
- `$0-local` cost mode;
- compact reference-member integrity pinned;
- compact reference master self-contained and study-only;
- legacy truncated transport remains non-authoritative;
- no network, GPU, generation, queue, PNG or publication authority was granted by this preflight.

The resulting `repository-integrity.json` is also added to the tamper-evident GPU evidence manifest, so the eventual real PNG can be cryptographically replayed together with the repository/reference state that authorized entry into the GPU path.

## Regression protection

`tests/test_phase18_gpu_smoke_workflow.py` now proves:

- repository integrity executes before CUDA probing, dependency installation, semantic preflight and Candidate 1 generation;
- the fail-closed repository/reference fields remain explicit;
- `repository-integrity.json` is included in the GPU evidence manifest before replay verification and artifact upload;
- all existing manual/self-hosted/CUDA/BF16/$0-local/provider-secret constraints remain intact.

## Safety/invariants

No Fact Lock, identity, sentiment/neutrality, semantic-publication, Golden-quality, brand-integrity, typography-integrity, FLUX.2 Klein 4B, BF16, seed/canvas, or generated-layer exclusion policy is relaxed.

No hosted/paid GPU provider, secret, Fake PNG, benchmark fabrication or publication shortcut is introduced.

## Remaining blocker

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA/BF16 host. This change set only makes that scarce execution window safer by rejecting repository/reference drift before any GPU-side work begins.
