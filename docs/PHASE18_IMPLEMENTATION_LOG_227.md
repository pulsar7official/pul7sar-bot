# Phase 18 Implementation Log 227 — Qwen Inference Replay and CI Discovery Repair

## Branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch only: `phase18/story-intelligence`
- Starting Phase 18 HEAD: `9facfdb3c2fa5319cf445031973f7a61806d806c`
- Read-only `main` HEAD observed before work: `2a6dee5bb64895a1658be84d7ce018cd71a08dff`
- No merge, rebase, force-update, or write to `main` or `main.py` was performed.

## Baseline CI finding

The previously reported Change Set 226 verification did not remain pending: Phase 18 Story Intelligence Verification Run `33140161304 / 3628` completed with `failure` in step `Syntax and discover validation`. Checkout, Python setup, and CPU dependency installation succeeded; later workflow stages were skipped after the validation failure.

A separate coverage defect was confirmed while reviewing the canonical validator: `tools/phase18_cpu_validate.py` uses `python -m unittest discover`, whereas `tests/test_phase18_qwen_image_inference_measurement.py` used free pytest-style test functions. Those functions were not canonical `unittest` discoveries. Change Set 227 converts the module to the project-native `unittest.TestCase` pattern so the new inference-measurement regressions are executed by canonical CPU validation.

The available GitHub connector did not expose the raw zipped Actions log body, so this log does not invent a specific assertion for Run 3628 beyond the verified failing workflow step.

## Code changes

### Modified: `engine/intelligence/qwen_image_inference_measurement.py`

Strengthened receipt replay without changing the measurement authority boundary:

- validates load-receipt SHA fields;
- validates the pinned snapshot revision structurally;
- locks probe guidance as well as dimensions/steps/seed/offload policy;
- enforces consistency among status, child exit code, `inference_succeeded`, and `single_inference_proven`;
- successful measurements must report `QwenImagePipeline`;
- actual offload must equal `sequential_cpu`;
- native BF16 must be proven;
- successful PNG evidence must have a `.png` path, SHA-256-shaped digest, and positive byte size;
- successful receipts cannot contain failure fields;
- canonical/semantic/human/Golden/publication authority remains closed.

Commit: `99fc35b563a9bb6742eb91153f33188e084d7c12`

### Modified: `tests/test_phase18_qwen_image_inference_measurement.py`

Converted the full suite to `unittest.TestCase` so `phase18_cpu_validate.py` executes it. Added regression coverage for:

- forged success status with recomputed SHA;
- actual offload-mode drift;
- native-BF16 drift;
- missing/invalid PNG path, SHA, and size evidence;
- all original prompt isolation and authority-boundary checks.

Commit: `8cd3d6cc36cbfb942e6d54454e05c1fd37c1bb2f`

### Added documentation

- `docs/PHASE18_CHANGESET_227_QWEN_INFERENCE_REPLAY_AND_CI_DISCOVERY_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_227.md`

Deleted files: none.

## Gates preserved

No gate was weakened or bypassed. The following remain fail-closed:

- Fact Lock / factual integrity;
- Entity and Identity Verification;
- Sentiment/Neutrality and respectful result treatment;
- canonical `$0-local` policy;
- pinned model identity/revision evidence;
- generated text/branding/exact-fact/entity-mark/exact-sport-geometry prohibitions;
- Semantic and Layer Ownership gates;
- byte-bound Visual Critic;
- Human review;
- Golden minimum `8.5` and elite target `9.0+`;
- Exact Brand and Typography integrity;
- SemanticPublicationGate.

The Qwen Image probe remains engineering-only and cannot become canonical Golden evidence.

## Testing status

A new Story Intelligence Verification is expected to run from the Change Set 227 branch head after these commits. Do not record Change Set 227 as CI-green until GitHub reports a completed successful Story Intelligence run for a head containing both the code hardening and the converted unittest suite.

## Remaining blocker toward the first accepted genuine Golden Visual

No compatible self-hosted CUDA execution host is available in this environment. A real next measurement still requires the exact pinned Qwen Image 2512 snapshot on a `$0-local` host with:

- NVIDIA CUDA;
- native BF16;
- sufficient live VRAM;
- sufficient system RAM;
- supported local Diffusers/QwenImagePipeline runtime;
- safe offload behavior;
- preserved model/runtime provenance.

No GPU result, inference success, Golden PNG, or visual score is fabricated in this change set.

## Next permissible step

1. Obtain a green canonical CPU verification for Change Set 227.
2. On a compatible `$0-local` CUDA host, execute the isolated 512x512 single-inference measurement.
3. Only after a real successful measured probe, design the controlled runtime-envelope measurement required to establish a genuine runtime floor.
4. Runtime-floor evidence must remain separate from Golden quality and publication authority.
