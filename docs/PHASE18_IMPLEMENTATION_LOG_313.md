# Phase 18 Implementation Log 313 — Canonical Qwen GPU Workflow

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Starting branch HEAD: `04fd70fa62b1d9dc0777e4ec98403fc4a7fd58c7`.

`main` was treated as read-only throughout this change set. No merge, rebase, reset, force-update, or content write to `main` was performed.

## Pre-change review

CS312 was rechecked before any write. Its `Phase 18 Story Intelligence Verification` run on `04fd70fa62b1d9dc0777e4ec98403fc4a7fd58c7` completed successfully, establishing a green starting point.

The first-PNG execution surface was then audited rather than assuming another lineage defect. A suspected postflight PNG-path mismatch in `tools/phase18_first_png.py` was rejected after replaying the implementation: `GenerationProvenanceLock.verify()` resolves the base PNG beneath the repository and the postflight returns that resolved path. No change was made for that disproven hypothesis.

The audit then compared the currently available GPU workflows with the hardened Qwen-Image execution tools. The branch already contained:

- `tools/phase18_qwen_image_gpu_readiness.py`;
- `tools/phase18_qwen_image_gpu_host_launch_manifest.py`;
- `tools/phase18_run_manifest_bound_canonical_inference.py`;
- `engine/intelligence/qwen_image_manifest_bound_execution.py`;
- `tools/phase18_qwen_image_launch_to_output_attestation.py`.

However, no dedicated `.github/workflows` entry point existed for that current canonical Qwen path. Existing first-image/Golden-v6 GPU workflows remain tied to the older FLUX generation route. This left a real orchestration gap: a compatible self-hosted GPU could not invoke the hardened manifest-bound Qwen path through a dedicated branch-safe Actions workflow without manual command assembly.

## Added

### `.github/workflows/phase18-qwen-image-canonical-inference.yml`

A manual, immutable-SHA, branch-bound, self-hosted CUDA/BF16 workflow was added for exactly one canonical Qwen inference.

Controls added:

- explicit dispatch token;
- exact `refs/heads/phase18/story-intelligence` requirement;
- immutable dispatch SHA checkout and branch reattachment;
- read-only repository permission;
- `$0-local` cost-mode lock;
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`;
- no automatic PyTorch replacement;
- CUDA and native BF16 proof;
- repository-local authorization and CS257 evidence containment;
- already-local Qwen snapshot requirement;
- current static Qwen readiness with `--require-static-ready`;
- build + replay of the current GPU-host launch manifest;
- execution only through `phase18_run_manifest_bound_canonical_inference.py`;
- independent replay of `launch_to_output_attestation.json`;
- PNG signature proof for `canonical_candidate.png`;
- explicit requirement for `genuine_canonical_inference_executed=true`;
- explicit fail-closed checks keeping semantic, human-review, Golden-quality, Genuine-Golden, and publication authorities false;
- artifact upload of the candidate/evidence bundle for downstream admission.

The workflow does not execute downstream semantic approval, human review, Golden adjudication, materialization, or publication readiness.

### `tests/test_phase18_qwen_image_canonical_inference_workflow.py`

Static regression coverage was added to lock the workflow contract. It checks:

- manual branch-bound dispatch;
- self-hosted GPU/CUDA/BF16 labels;
- `$0-local` and offline flags;
- use of the current Qwen readiness, launch-manifest, manifest-bound inference, and launch-to-output attestation tools;
- explicit closure of all downstream authorities;
- absence of legacy FLUX generation commands in the canonical Qwen workflow.

### `docs/PHASE18_CHANGESET_313_CANONICAL_QWEN_GPU_WORKFLOW.md`

Added the formal CS313 contract and authority boundary.

### `docs/PHASE18_IMPLEMENTATION_LOG_313.md`

This file records the complete implementation/audit history for CS313.

## Modified

No executable or test file was modified after its initial CS313 addition. This implementation log was updated after CI completed to record the terminal verification result. The older FLUX/Golden-v6 paths remain intact for historical/review use cases while the current Qwen canonical route has its own isolated entry point.

## Deleted

None.

## Preserved gates and authorities

CS313 does not change or weaken:

- fact/freshness requirements;
- entity/identity verification;
- sentiment neutrality and loser-respect constraints;
- zero-cost policy;
- semantic Base QA;
- generated-layer QA;
- composition QA;
- Golden visual-quality adjudication;
- human visual review;
- exact brand/typography review;
- final composed approval;
- final semantic approval;
- `SemanticPublicationGate`;
- exact-byte Genuine Golden materialization;
- final publication readiness.

A canonical Qwen candidate produced by this workflow remains non-semantic-approved, non-human-approved, non-Golden-approved, non-materialized, and non-publication-ready until the existing downstream chain grants those authorities independently.

## Testing

### Starting point

CS312 verification was confirmed completed/success on starting HEAD `04fd70fa62b1d9dc0777e4ec98403fc4a7fd58c7` before CS313 writes.

### CS313 terminal verification

The code-bearing/documented CS313 HEAD `8d4551512ab0b14f9adec0f04e283121b27c7ca9` ran `Phase 18 Story Intelligence Verification` run `33606002222` to completion with conclusion `success`.

The following major verification steps all completed successfully:

- Syntax and discover validation;
- Completion and production isolation;
- visual-study handoff build and verification;
- result composition matrix build;
- publication-block verification;
- project-native editorial visual study;
- adaptive reference brand verification;
- self-contained brand ownership verification;
- Golden editorial v6 build/verification;
- legacy-logo non-canonical assertion;
- all configured artifact uploads.

This establishes CS313 as terminal-green for the repository CPU verification suite. The later documentation-only commit recording this outcome does not change executable code or tests.

### GPU execution

No genuine Qwen inference was claimed during implementation. The available execution environment was directly probed and reported `torch=2.10.0+cpu`, `cuda_available=false`, `torch.version.cuda=null`, `device_count=0`, native BF16 unavailable, and no `nvidia-smi`. It was therefore not used as a substitute for a compatible self-hosted GPU.

A real canonical candidate requires the workflow runner to prove CUDA-enabled PyTorch, at least one CUDA device, native BF16 support, the current compatible Qwen runtime, and the exact already-local pinned Qwen snapshot.

## Remaining gap after CS313

The repository now has a safe Actions entry point to reach an attested Qwen canonical candidate once a compatible zero-cost GPU host exists. The remaining path is intentionally still gated:

1. execute CS313 workflow on a compatible self-hosted CUDA/BF16 host;
2. obtain a real `canonical_candidate.png` plus exact launch/provenance attestation;
3. pass exact-byte candidate admission;
4. pass semantic Base, identity, generated-layer, composition/post-composition, Golden-quality, human-review, brand/typography, final-composed and final-semantic gates;
5. execute the lineage-bound `SemanticPublicationGate`;
6. materialize the Genuine Golden PNG byte-for-byte;
7. grant publication readiness separately.

No placeholder or fabricated PNG may be used to satisfy any of those steps.
