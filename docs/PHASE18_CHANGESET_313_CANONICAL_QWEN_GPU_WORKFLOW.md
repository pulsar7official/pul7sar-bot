# Phase 18 Change Set 313 — Canonical Qwen GPU Workflow

## Purpose

CS313 closes an execution-orchestration gap between the hardened Qwen-Image canonical inference path and GitHub Actions. Before this change, the branch contained the current Qwen GPU-readiness, launch-manifest, manifest-bound execution, and launch-to-output attestation tools, but the available GPU workflows were still oriented around the older FLUX/Golden-v6 execution paths.

CS313 adds a dedicated manual self-hosted workflow for exactly one canonical Qwen candidate. It does not create semantic, human-review, Golden-quality, Genuine-Golden, or publication authority.

## Added workflow

`.github/workflows/phase18-qwen-image-canonical-inference.yml`

The workflow:

1. requires explicit `workflow_dispatch` confirmation;
2. refuses any dispatch outside `phase18/story-intelligence`;
3. checks out the immutable dispatch SHA and reattaches only that branch;
4. proves a CUDA device and native BF16 without installing/replacing PyTorch;
5. keeps `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` locked;
6. accepts only repository-local authorization/CS257 evidence plus an already-local Qwen/Qwen-Image-2512 snapshot;
7. runs the current static Qwen readiness check without downloads;
8. builds and replays the exact GPU-host launch manifest;
9. invokes only `phase18_run_manifest_bound_canonical_inference.py`, so prompt/model/evidence/settings are recovered from the verified launch manifest rather than duplicated at the execution edge;
10. independently replays `launch_to_output_attestation.json` after the subprocess succeeds;
11. requires a genuine `canonical_candidate.png` and `genuine_canonical_inference_executed=true`;
12. fail-closes `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, and `publication_ready` to `false`;
13. uploads the candidate and exact evidence for downstream gated admission/review.

## Added regression

`tests/test_phase18_qwen_image_canonical_inference_workflow.py`

The regression locks:

- manual branch-bound dispatch;
- self-hosted CUDA/BF16 runner labels;
- zero-cost/offline environment;
- current Qwen readiness + manifest + canonical execution + attestation toolchain;
- downstream authority closure;
- absence of legacy FLUX generation commands from this new canonical workflow.

## Authority boundary

CS313 does **not** bypass or replace any Phase 18 gate. A successful workflow run proves only that the approved manifest-bound Qwen inference executed and produced an attested canonical candidate. It does not imply factual approval, identity approval, semantic approval, sentiment/loser-respect approval, composition approval, human visual approval, Golden-quality approval, Genuine Golden materialization, or publication readiness.

The candidate must still enter the existing exact-byte admission and downstream QA/adjudication chain.

## Zero-cost / network boundary

The workflow requires `$0-local` and an already-local pinned Qwen snapshot. It sets Hugging Face Hub and Transformers offline flags before the current manifest-bound launcher runs. It performs no model download and does not add a paid service/API dependency.

## Why this reduces the remaining gap

Once a compatible zero-cost self-hosted CUDA/BF16 machine is available, the canonical Qwen execution path now has a branch-bound GitHub Actions entry point that reaches the exact provenance-attested candidate boundary without operator duplication of prompt/model/settings and without granting downstream authority prematurely.
