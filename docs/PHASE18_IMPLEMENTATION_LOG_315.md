# Phase 18 Implementation Log 315 — Admitted Candidate Semantic Checkpoint

## Branch safety

Target branch: `phase18/story-intelligence` only.

Starting branch HEAD reviewed before changes: `7010fe0f176e27775b3f74aecbcffc93e60382da`.

`main` was read-only and observed at `f8c7c703a2528838425193979a40b0abca8493af`. No merge, rebase, reset, force update, content write, or workflow dispatch was performed against `main`.

The starting CS314 verification run `33611157832` / Phase 18 Story Intelligence Verification #4594 completed successfully on `7010fe0f176e27775b3f74aecbcffc93e60382da` before CS315 changes were introduced.

## Review performed

CS314 already guarantees that a genuine manifest-bound Qwen-Image inference, when a compatible GPU host exists, is independently attested, sealed through CS301, replay-verified, and exact-byte admitted by CS303. Its workflow intentionally stops before semantic approval.

The next existing production authority, CS304, was reviewed. It:

- verifies the exact CS303 admission;
- reopens and hashes the exact admitted PNG;
- runs the pinned Qwen2.5-VL semantic inspector in `BASE_SCENE` mode;
- evaluates the existing semantic verdict and layer-evidence gates;
- cannot grant identity, Human Review, Golden, final semantic, materialization, or publication authority.

CS305 was also reviewed. It:

- requires a passing CS304 receipt;
- walks CS304 -> CS303 -> sealed handoff -> launch attestation -> launch manifest -> exact CS257 evidence;
- derives human identity targets from the lineage-bound entity evidence;
- classifies only whether separate pixel-identity review is mandatory;
- keeps `identity_approved=false`.

The operational gap was therefore not a missing policy gate. It was the absence of a single fail-closed command that advances an already admitted candidate through these two existing non-Golden authorities without manual receipt/path selection between them.

A second safety issue was found during CS315 self-review before finalization: the pinned Qwen2.5-VL inspector itself selects an immutable revision, but a standalone caller could still allow the underlying Hugging Face/Transformers runtime to attempt a network cache fill if the pinned model bytes were absent. CS315 therefore explicitly forces Hugging Face, Transformers, and datasets offline before invoking CS304. Missing local semantic-model bytes now fail closed rather than converting the checkpoint into a network-fetch path.

## Added

### `tools/phase18_run_admitted_candidate_semantic_checkpoint.py`

New orchestration command for:

`CS303 exact-byte admission -> CS304 semantic Base QA -> conditional CS305 identity-requirement classification`.

Properties:

- output must be a new directory inside the repository;
- `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`, and `HF_HUB_DISABLE_TELEMETRY=1` are forced before semantic inference;
- CS304 receipt is independently replay-verified;
- CS305 is never executed if CS304 rejects;
- CS305 receipt is independently replay-verified when produced;
- story SHA and candidate binding must remain identical between verified CS304 and CS305 receipts;
- downstream authorities are explicitly checked to remain false;
- a compact checkpoint receipt records either semantic rejection or successful identity-requirement classification;
- no generation, pixel mutation, publication, or network call is implemented by the checkpoint itself.

### `tests/test_phase18_admitted_candidate_semantic_checkpoint.py`

Static regression coverage asserts:

- use of the existing CS304 builder/verifier and CS305 builder/verifier;
- CS304 occurs before CS305;
- semantic rejection stops before identity-requirement classification;
- downstream authority fields remain closed;
- story/candidate lineage drift checks remain present;
- all four local/offline environment controls are forced before CS304;
- Qwen-Image/FLUX generation and publication calls are absent from the checkpoint.

### `docs/PHASE18_CHANGESET_315_ADMITTED_CANDIDATE_SEMANTIC_CHECKPOINT.md`

Defines the CS315 purpose, execution contract, authority boundaries, lineage guarantees, explicit offline semantics, files, and remaining gap.

### `docs/PHASE18_IMPLEMENTATION_LOG_315.md`

This implementation record.

## Modified relative to CS314

None. All CS315 executable/test/documentation paths are new relative to the CS314 baseline; the offline hardening was applied while finalizing those newly added files.

## Deleted

None.

## CS315 commit progression

- `4a6c22e9a7c80058cce1ffd6c5c6edfe13393bb4` — add admitted-candidate semantic checkpoint.
- `d78196da8b84acd2d5091f1cd28b5a9a1647dc91` — add checkpoint regression coverage.
- `9c08b6d45cdb4cd9d5eb0160a1c500e5ae75e364` — add CS315 contract.
- `0ebc31809c231462490f7ceda464efcaf3f29894` — add initial CS315 implementation log.
- `3984495cf095504d60ae54590611cf096dfb54c0` — force offline semantic runtime before CS304.
- `668591d4f22304cde1912868d7f8711656158fe8` — regress the offline controls and ordering.
- `314718ab02b376d4b7efc9335c969c482e2b11f6` — synchronize the CS315 contract with offline fail-closed semantics.

## Tests and validation

Pre-change baseline: Phase 18 Story Intelligence Verification run `33611157832` completed with `success` for CS314 HEAD `7010fe0f176e27775b3f74aecbcffc93e60382da`.

An initial CS315 verification run was started on the pre-offline-hardening implementation, but that revision was superseded before being treated as final because the semantic runtime network-fallback risk was found during self-review. The final hardened CS315 revision must be judged only by CI on the post-hardening HEAD; no success is inferred from a superseded run.

CS315 adds a dedicated regression module and relies on the repository's normal Phase 18 Story Intelligence Verification workflow to perform syntax/discovery and the complete existing regression matrix. The final CI outcome must be reported from GitHub; it must not be inferred or fabricated.

## Preserved gates

No threshold, verdict policy, or authority was weakened or bypassed. The following remain independent gates downstream of CS315 where applicable:

- factual/freshness locks;
- entity/identity verification and required pixel-identity review;
- sentiment neutrality and loser-respect policy;
- `$0-local` / forced offline execution constraints;
- Generated-Layer QA;
- deterministic composition and post-composition semantic QA;
- Golden visual-quality adjudication;
- Human Visual Review;
- exact brand/typography verification;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- exact-byte Genuine Golden materialization;
- final publication readiness.

## Exact execution blocker

No genuine PNG was generated during CS315. The available execution environment still lacks a compatible CUDA/GPU runtime for the canonical Qwen-Image inference path. A real first candidate requires, on one zero-cost self-hosted host:

- NVIDIA CUDA device;
- CUDA-enabled PyTorch;
- native BF16 support;
- compatible Qwen-Image runtime;
- exact approved already-local `Qwen/Qwen-Image-2512` snapshot at revision `2ce1c28560fbc62c9f5531e076b237d3575330a9`;
- sufficient RAM/VRAM for real model load and inference.

To execute CS304 locally/offline after admission, the pinned `Qwen/Qwen2.5-VL-3B-Instruct` revision `66285546d2b821cf421d4f5eb2576359d3770cd3` must also already be available in the local Hugging Face cache/runtime. CS315 now forces offline mode before semantic inference, so missing local semantic-model bytes fail closed rather than trigger a network download.

## What remains

Once a compatible host produces and CS303 admits a real candidate, CS315 can advance that exact candidate through semantic Base QA and identify whether human pixel-identity review is mandatory without any manual evidence re-selection. A passing candidate then continues through the still-independent downstream QA, human, brand, semantic-publication, materialization, and publication-readiness gates before it may ever be called a Genuine Golden Visual PNG.
