# Phase 18 — Change Set 301: Canonical Candidate Handoff Seal

## Objective

Create a fail-closed handoff artifact for the first genuine Qwen canonical candidate so downstream semantic, composition, visual-quality, human-review, brand/typography, Golden-materialization, and publication gates can consume one replay-verifiable lineage instead of relying on directory convention or operator-selected files.

## Preconditions

CS301 does not execute Qwen and cannot create pixels. Its build path requires the existing canonical output directory to contain the CS300 successful child bundle:

- `canonical_candidate.png`
- `canonical_inference_receipt.json`
- `local_inference_provenance.json`
- `launch_to_output_attestation.json`

The CS293 launch-to-output attestation is replayed before a handoff can be written.

## Handoff contract

The new `canonical_candidate_handoff.json` binds by repository-relative path, SHA-256, and byte size all four source files above. It additionally carries the attested story snapshot digest, Qwen model identity/revision, exact inference settings, candidate dimensions, `$0-local`, `network_allowed=false`, and `local_files_only=true`.

The candidate PNG binding must exactly match the candidate binding already present in the replayed launch-to-output attestation.

The handoff has its own canonical JSON digest (`handoff_sha256`). Verification recomputes that digest, re-hashes all bound files, and replays the upstream launch-to-output attestation.

## Authority boundary

A sealed handoff means only that a genuine canonical inference candidate and its evidence lineage are internally consistent and byte-bound for the next gates.

It must keep all of the following false:

- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

It explicitly lists the next required gates rather than claiming them.

## Zero-cost and network policy

CS301 requires the replayed lineage to remain `$0-local`, `network_allowed=false`, and `local_files_only=true`. It does not add a model download, API call, paid service, or network-enabled inference path.

## Files

Added:

- `engine/intelligence/qwen_image_canonical_candidate_handoff.py`
- `tools/phase18_qwen_image_canonical_candidate_handoff.py`
- `tests/test_phase18_qwen_image_canonical_candidate_handoff.py`
- `docs/PHASE18_CHANGESET_301_CANONICAL_CANDIDATE_HANDOFF_SEAL.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_301.md`

No files are deleted. CS301 intentionally does not alter the production inference launcher; the handoff is a downstream post-success sealing step and therefore cannot weaken CS295–CS300 execution controls.

## Remaining hard blocker

No Genuine Golden PNG is claimed by CS301. Real progress still requires a zero-cost compatible host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized runtime identity, compatible QwenImagePipeline/Diffusers, sequential CPU offload, the exact approved local Qwen snapshot, and sufficient RAM/VRAM proven by real model load and inference.
