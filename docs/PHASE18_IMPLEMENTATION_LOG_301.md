# Phase 18 Implementation Log — Change Set 301

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence`

Starting branch HEAD: `8842fc7b88dc28e9435b16c6755679e5fc9e83fe` (CS300)

`main` was treated as read-only throughout this change set. No merge, rebase, force-update, commit, or file write to `main` was performed.

## Starting-state verification

Before modifying code, the branch was read directly from GitHub and confirmed at CS300 HEAD `8842fc7b88dc28e9435b16c6755679e5fc9e83fe`.

The Phase 18 workflow suite on that exact SHA was reviewed. `Phase 18 Story Intelligence Verification` was `completed / success`, and the visible Phase 18 visual checks on the same SHA were also `completed / success`. CS301 therefore began from a terminal-green branch.

`main` was separately read at `8ad5b8919387c5813359eda8434740949f5dcaf6` and was not modified.

## Gap identified

CS300 independently replays the successful canonical child output and verifies the exact candidate PNG, canonical inference receipt, local inference provenance, and launch-to-output attestation before the outer launcher may return success.

What was still missing was a single downstream handoff artifact that binds that same replay-verified candidate and evidence lineage for semantic/composition/visual-quality processing. Without such a seal, later stages would need to rediscover files by directory convention or accept operator-selected paths, creating avoidable risk of mixing files from different canonical runs.

## Added

### `engine/intelligence/qwen_image_canonical_candidate_handoff.py`

Adds a fail-closed CS301 handoff builder and verifier.

The builder:

- requires the exact CS300 successful canonical source bundle;
- replays `verify_launch_to_output_attestation(...)` before writing anything;
- requires `genuine_canonical_inference_executed=true`;
- requires semantic, human-review, Golden-quality, Genuine-Golden, and publication authorities to remain false;
- binds all four source files by repository-relative path, SHA-256, and byte size;
- verifies that the direct PNG binding equals the PNG binding already attested upstream;
- carries the story snapshot digest, Qwen model identity/revision, inference settings, dimensions, `$0-local`, network-disabled, and local-only state;
- records the remaining downstream gates explicitly;
- seals the handoff with `handoff_sha256`;
- uses exclusive creation and rejects output outside the repository or symlink inputs.

The verifier:

- validates schema/status and canonical digest;
- requires `$0-local`, `network_allowed=false`, and `local_files_only=true`;
- requires all downstream authorities to remain false;
- re-hashes every bound source file;
- replays the launch-to-output attestation again;
- rechecks story/model/settings joins;
- rechecks exact candidate path/hash/size/dimensions.

### `tools/phase18_qwen_image_canonical_candidate_handoff.py`

Adds explicit `build` and `verify` CLI operations. It has no model, prompt, approval, Golden, publication, network, or paid-mode override switches.

### `tests/test_phase18_qwen_image_canonical_candidate_handoff.py`

Adds CPU/control-plane regressions for:

- sealing exact sources while keeping downstream authorities false;
- rejection of premature upstream semantic authority;
- detection of source byte drift after sealing;
- detection of handoff authority tampering through digest mismatch.

### `docs/PHASE18_CHANGESET_301_CANONICAL_CANDIDATE_HANDOFF_SEAL.md`

Documents the handoff contract, authority boundary, zero-cost/network policy, and remaining GPU blocker.

### `docs/PHASE18_IMPLEMENTATION_LOG_301.md`

This implementation log.

## Modified

No pre-existing files were modified in CS301.

The production inference launcher is intentionally unchanged. CS301 is a downstream sealing step after CS300 successful-output replay; it therefore cannot weaken or bypass launch-manifest, preload-host, offline-child, model-load, inference, or launch-to-output controls.

## Deleted

No files were deleted.

## Commits

- `8ac2e80a502eab457e2f0ae96df92abf77cbb1d7` — canonical candidate handoff seal
- `45d521ecd63ce7229fce521d0c2c116247bea681` — candidate handoff CLI
- `313616bdcd374c658ec3b02380ddce5d7e9a3fc8` — candidate handoff regressions
- `dfe161b3327e5f28e80ddc6fc9e2d55709648c41` — CS301 contract documentation
- final implementation-log commit: recorded by GitHub when this file is created

## Gate preservation

CS301 does not alter or bypass:

- Fact/Freshness Lock
- Entity/Identity Verification
- sentiment neutrality
- loser-respect
- story-bound semantic ownership
- `$0-local`
- exact approved local snapshot policy
- local-only model loading
- generated-layer QA
- composition gates
- visual-quality adjudication
- human review
- exact brand/typography
- `SemanticPublicationGate`
- CS285 Genuine Golden materialization
- CS286 publication readiness

A valid CS301 handoff remains only a lineage seal for a genuine canonical inference candidate. It must keep:

- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

## Testing status

The new tests are CPU/control-plane regressions only. They do not constitute a Qwen model load, CUDA/BF16 inference, semantic approval, human visual review, or Genuine Golden Visual.

GitHub Actions must be checked on the final CS301 HEAD before this change set is described as terminal-green.

## Remaining blocker

No image was fabricated during CS301.

The remaining hard execution blocker is still an available zero-cost host that satisfies all of the following in one runtime:

- NVIDIA CUDA device;
- CUDA-enabled PyTorch;
- native BF16;
- CS260-authorized GPU/runtime identity;
- compatible `QwenImagePipeline`/Diffusers runtime;
- sequential CPU offload;
- exact approved `Qwen/Qwen-Image-2512` immutable snapshot already local;
- sufficient host RAM and GPU VRAM proven by actual model load and real inference.

Until that host exists, the project can continue reducing control-plane and downstream-handoff gaps but cannot truthfully produce `canonical_candidate.png`, a production-composed candidate, or the first Genuine Golden PNG.
