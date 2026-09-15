# Phase 18 Implementation Log — CS452

## Scope

CS452 integrates the CS451 immutable first-Golden GPU handoff into the existing self-hosted attested host-readiness workflow. The goal is to reduce the remaining operational gap between a successful zero-cost GPU host attestation and the canonical Golden v6 preflight without granting generation, publication, network-download, or seed-expansion authority.

## Branch safety

- Target branch: `phase18/story-intelligence` only.
- `main` was read for isolation verification only and was not modified.
- The existing `main.py` diff guard remains in the host-readiness workflow.

## Prior state reviewed

CS451 HEAD was `68362e85812c0a8bc5db53605a9c71b6dd41de25`.
The GitHub check run `verify-story-intelligence` completed successfully on that exact SHA before CS452 work began. The existing CS451 handoff builder already validated exact commit binding, the attested pre-GPU schema, readiness, receipt attestation, empty blockers, closed authorities, canonical workflow presence, readiness workflow presence, required runner labels, `$0-local`, and offline-only requirements.

## Modified

### `.github/workflows/phase18-first-golden-attested-host-readiness.yml`

Added a required check that `tools/phase18_build_first_golden_gpu_handoff.py` exists after immutable checkout and branch reattachment.

Added `Build immutable first-Golden GPU handoff` after the existing attested summary replay. It invokes the CS451 builder with the exact `DISPATCH_SHA`, consumes the attested pre-GPU summary from the same run, and writes:

`output/phase18_gpu_smoke/first-golden-gpu-handoff.json`

Added `Replay GPU handoff and keep generation authority closed`. This step fails closed unless all of the following remain true:

- schema is `pul7sar-phase18-first-golden-gpu-handoff-v1`;
- handoff `expected_commit` equals the immutable dispatch SHA;
- branch requirement remains `phase18/story-intelligence`;
- `eligible_for_authoritative_golden_preflight` is true;
- blocker list is empty;
- cost mode remains `$0-local`;
- offline requirement remains true;
- `authoritative_gate` remains false;
- `network_download_authorized` remains false;
- `generation_authorized` remains false;
- `publication_ready` remains false;
- `seeds_2_to_4_authorized` remains false.

The handoff JSON is now uploaded in the same seven-day evidence artifact as the receipt, attestation, and attested summary.

## Added

### `tests/test_phase18_first_golden_host_readiness_handoff_integration.py`

Added standard-library `unittest` coverage that locks:

- ordering: readiness replay → handoff build → handoff replay → evidence upload;
- exact dispatch-SHA binding;
- use of the attested summary as the handoff source;
- handoff artifact upload;
- self-hosted GPU labels;
- `$0-local` plus Hugging Face/Transformers offline flags;
- closed authority fields;
- preservation of the `main.py` isolation guard.

## Deleted

None.

## Unchanged production contracts

CS452 does not modify:

- factual verification or fact locks;
- identity/entity verification;
- sentiment and loser-respect policy;
- SemanticPublicationGate;
- visual-quality or Human Review gates;
- Candidate 1 prompt, seed, dimensions, inference steps, or guidance;
- Qwen2.5-VL or FLUX.2 model identities/revisions;
- CUDA/native-BF16 qualification rules;
- canonical/JIT/offload generation implementations;
- network-download authority;
- generation authority;
- publication authority;
- Seeds 2–4 authority.

## Test/CI status at commit time

CS452 writes trigger normal branch/PR verification. Final terminal status must be checked on the final CS452 HEAD before calling the change green.

## Remaining blocker to the first genuine Golden PNG

No PNG is fabricated by CS452. A genuine Candidate 1 still requires an actual compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/compute capability, adequate live VRAM/RAM/cache headroom, compatible semantic and generation runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally. The run must remain `$0-local`, offline-only, and must not substitute FP16/FP32 for the required quality path.

CS452 materially reduces the gap by ensuring that a successful host-readiness run now emits a commit-bound, machine-readable handoff that can be carried into the canonical Golden preflight without manual reconstruction of readiness state.
