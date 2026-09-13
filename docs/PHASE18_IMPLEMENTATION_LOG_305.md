# Phase 18 Implementation Log 305 — Candidate-Lineage-Bound Identity Requirement

## Scope and branch safety

Work was performed only on `phase18/story-intelligence`.

Starting Phase 18 branch SHA:

`1c0dad9b5bc5024156f70ab1acf27f8ea5c81fd9`

CS304 was reviewed before CS305 work and its Phase 18 Story Intelligence Verification run #4492 had reached `completed / success` on that starting SHA.

No commit, merge, rebase, force-update, or file modification was performed on `main` during CS305. `main` continued to move independently through the repository's existing bot history updates.

## Problem found

CS304 correctly bound Semantic Base QA to the CS303 sealed-handoff byte admission. The next identity-requirement edge, however, still accepted an independently supplied `cs257_run_dir`.

That directory was validated for the same story snapshot and valid entity-identity evidence, but it did not have to be the exact CS257 evidence directory already fixed in the candidate's GPU Host Launch Manifest. Therefore two independently valid CS257 evidence runs for the same story could theoretically be substituted at CS265 without changing the candidate bytes.

This was a lineage-integrity gap, not an identity-approval bypass: downstream identity/semantic/Golden/publication authorities were already false. CS305 removes the substitution surface so the identity evidence used after generation is the evidence that was already bound into the candidate's generation launch history.

## Implemented production lineage

CS265 now derives identity evidence exclusively through the candidate's verified lineage:

1. CS304 Semantic Base QA receipt.
2. Its CS303 candidate byte-admission binding and verifier.
3. The CS301/302 sealed canonical-candidate handoff referenced by that admission.
4. The CS293 launch-to-output attestation referenced by the handoff.
5. The exact GPU Host Launch Manifest referenced by the attestation.
6. The `cs257_evidence.repository_relative_directory` and file set recorded in that launch manifest.
7. The entity-identity evidence binding inside that exact CS257 evidence manifest.

Each transition is repository-relative, symlink-safe, byte-bound, and replayed with its canonical verifier. Story SHA, receipt digests, candidate handoff SHA, launch manifest binding, `$0-local`, `network_allowed=false`, and `local_files_only=true` are checked fail-closed where applicable.

## Added

- `docs/PHASE18_CHANGESET_305_CANDIDATE_LINEAGE_BOUND_IDENTITY_REQUIREMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_305.md`

## Modified

- `engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py`
  - upgraded CS265 schema from v1 to v2;
  - removed the independent `cs257_run_dir` production argument;
  - added candidate-lineage traversal/replay through CS303, CS301/302, CS293, the GPU launch manifest, and its exact CS257 evidence binding;
  - added `lineage_bound_identity_source` to the sealed receipt;
  - re-derives and compares the lineage during receipt verification;
  - retains fail-closed candidate/source-byte checks and identity semantic replay.

- `tools/phase18_classify_canonical_candidate_identity_requirement.py`
  - removed `--cs257-run-dir`;
  - now accepts only the CS304 receipt, output directory, and repository root;
  - the identity evidence selector is no longer operator-controlled.

- `tests/test_phase18_qwen_image_canonical_candidate_identity_requirement.py`
  - tracks the CS304 schema source of truth;
  - asserts the production API contains no `cs257_run_dir` selector;
  - covers human/non-human classification without manufacturing identity approval;
  - covers candidate-byte and CS304-source-byte drift;
  - covers lineage-source tampering;
  - directly tests launch-bound identity-evidence hashing and rejects post-binding evidence byte drift.

- `tests/test_phase18_qwen_image_canonical_candidate_pixel_identity_review_request.py`
  - preserves the existing CS266 regression set;
  - replaces the hard-coded CS265 v1 schema fixture with the CS265 schema constant so the downstream test follows the production source of truth without weakening review behavior.

## Deleted

No files were deleted.

The obsolete production CLI/API selector `--cs257-run-dir` / `cs257_run_dir` was removed rather than retained as a compatibility bypass.

## Commit sequence

- `0769a803a0dbcd075a54effbc67397798e5bb967` — bind CS265 identity requirement to candidate launch lineage.
- `35c91863566e758546c7a422bb96b4ac07b36481` — remove independent CS257 selector from production CLI.
- `a6c4588a9febe62490d3b22108ca8f6435d10ebe` — add lineage-bound CS265 regressions.
- `d02660c81469cf8ec87ea2a47f3664c3fc6c664b` — preserve CS266 regressions while tracking CS265 schema dynamically.
- `f7876961dfc605b6475b20ee1a3bc8be6a499618` — document the CS305 contract.
- `0d9e8773b87128820f9e5a93fbffcbb16ca7ce9f` — strengthen direct launch-bound identity-evidence byte-drift coverage.
- this implementation-log commit records the complete change set.

## Testing and verification

Control-plane regression coverage was expanded as described above. These tests use synthetic fixtures and mocks where appropriate and are not represented as Qwen model-load or image-generation evidence.

GitHub Actions was triggered for the CS305 commits. At the time this log was finalized, the newest workflow set for `0d9e8773b87128820f9e5a93fbffcbb16ca7ce9f` had started and Phase 18 workflows were still `in_progress`; therefore this log does not claim terminal-green status for CS305. Final status must be read against the final branch SHA.

## Authority and gate preservation

CS305 does not perform pixel face recognition and does not grant identity approval. It classifies whether a separate pixel-identity review is mandatory and binds the targets/evidence to the candidate's own generation lineage.

The receipt continues to require the following authorities to remain false:

- `identity_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

No Fact/Freshness, Entity/Identity, sentiment-neutrality, loser-respect, zero-cost/local-only, semantic-publication, generated-layer/composition, visual-quality, Human Review, exact brand/typography, Genuine Golden, or publication-readiness gate was weakened or bypassed.

## Execution-host probe and Genuine Golden status

The execution environment available during this change set was probed and remained CPU-only:

- PyTorch: `2.10.0+cpu`
- `torch.cuda.is_available()`: `False`
- `torch.version.cuda`: `None`
- CUDA device count: `0`
- native BF16 support: unavailable
- `nvidia-smi`: unavailable

Accordingly CS305 did **not** fabricate or claim:

- a genuine Qwen-Image model load;
- CUDA/BF16 inference;
- a genuine `canonical_candidate.png`;
- a production composed PNG;
- a Genuine Golden Visual PNG.

The remaining execution blocker is a zero-cost host that simultaneously provides NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized compatible QwenImagePipeline/Diffusers runtime, sequential CPU offload, the exact approved already-local Qwen snapshot, and sufficient RAM/VRAM demonstrated by genuine model load and inference.

## Remaining route to the first Genuine Golden Visual

`verified launch manifest`
→ preload/offline/runtime gates
→ genuine local Qwen inference
→ provenance/postflight replay
→ sealed candidate handoff
→ CS303 exact byte admission
→ CS304 admission-bound Semantic Base QA
→ **CS305 candidate-lineage-bound identity requirement**
→ pixel-identity review when required
→ generated-layer/composition QA
→ visual-quality adjudication
→ Human Review
→ Exact Brand/Typography
→ `SemanticPublicationGate`
→ Genuine Golden materialization
→ publication readiness.

CS305 materially reduces the remaining gap by ensuring that post-generation identity classification can no longer substitute a different same-story CS257 evidence run for the evidence that actually authorized the candidate's generation lineage.
