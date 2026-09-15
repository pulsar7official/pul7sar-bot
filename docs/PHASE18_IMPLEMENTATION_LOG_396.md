# Phase 18 Implementation Log — CS396

## Scope

Golden v6 artifact replay semantic hardening on `phase18/story-intelligence` only. `main` was inspected read-only and was not modified.

## Starting state

- Starting branch HEAD: `32eb5576ecfea6b0a2f3e23966f17dddf8654097`
- CS395 `verify-story-intelligence` was confirmed `completed/success` on that HEAD.
- `main` observed read-only at `064fd78cefdf033722e1ca81353a617a3753c43d`.

## Gap identified

CS395 replayed byte integrity for all nine evidence files and the Candidate 1 PNG, but the downloaded-artifact verifier did not independently re-interpret the semantic claims inside those evidence JSON files. A locally rewritten evidence file plus a correspondingly rewritten final receipt could therefore remain hash-consistent while weakening a CUDA/BF16, zero-cost, pinned-model, runtime, or staging claim.

The producer workflow already performs semantic replay before upload. CS396 extends that fail-closed meaning check to the independent post-download verifier so the artifact remains self-checking after it leaves the runner.

## Code changes

### Modified `tools/phase18_verify_first_genuine_golden_v6_artifact.py`

Added CPU-safe semantic replay for the nine hash-bound evidence receipts. The verifier now additionally proves:

- GPU evidence is eligible, CUDA-backed, native-BF16 capable, `$0-local`, and has live free VRAM at or above its required floor.
- Host-memory preflight is ready and `$0-local`.
- Cache-budget receipt has the expected schema, branch, pinned Qwen/FLUX identities and revisions, and no download/generation/publication authority.
- Semantic preflight has the expected pinned Qwen identity/revision, CUDA readiness, local-only cost mode, `model_downloaded_now=false`, and no generation/publication authority.
- Qwen and FLUX cache receipts match the approved pinned model identities/revisions and require `downloaded_now=false`.
- FLUX cache evidence still proves post-cache working headroom.
- Pre/post generation runtime fingerprints are independently replayed with `verify_matching_runtime_fingerprints`, and their digest must match the final resource-lock receipt.
- Strict Golden staging has the expected schema/status, Candidate 1 identity, `$0-local`, native `bfloat16`, `golden_reference` precision tier, approved semantic/layer gates, pinned Qwen/FLUX identities, closed downstream authority, and the same PNG SHA-256 as the final lock.
- Successful replay reports `evidence_semantics_verified=true` but still returns Human Review, Golden Quality, publication, and Seeds 2–4 authority as false.

No generation logic, factual/identity policy, sentiment policy, semantic-publication policy, visual-quality thresholds, model revisions, or dependency versions were changed.

### Modified `tests/test_phase18_verify_first_genuine_golden_v6_artifact.py`

Rebuilt the synthetic artifact fixture so all nine evidence receipts carry contract-valid semantics instead of placeholder JSON. Added regression cases proving that the verifier rejects a rewritten evidence file even when the attacker also updates the matching SHA/byte record in the final receipt, including:

- semantic preflight changed to `model_downloaded_now=true`;
- GPU evidence changed to `bf16_supported=false`;
- strict staging changed to `publication_ready=true`.

Existing PNG byte/SHA, evidence hash, evidence inventory, staging-path binding, path-root, LCA-layout, and fail-closed authority tests remain.

## Commits

- `55494b8158571b45462ceca17e53f2662e4c2a06` — semantic evidence replay implementation.
- `e8ae44159655ab1262727a00e9a29fe1dc8bff3e` — regression tests and contract-valid artifact fixture.

## Added / modified / deleted

- Added: this implementation log only.
- Modified: artifact replay verifier; artifact replay regression tests.
- Deleted: none.
- Dependencies: unchanged.
- `main`: unchanged.

## Genuine Golden execution status

No Genuine Golden PNG was created or claimed in CS396. The remaining non-substitutable execution blocker is still the absence of an available compatible self-hosted NVIDIA CUDA host with native BF16 support, CUDA-enabled PyTorch, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local` contract.

CS396 only reduces the post-generation trust gap. It does not authorize generation, Human Review acceptance, Golden Quality acceptance, publication, or Seeds 2–4.
