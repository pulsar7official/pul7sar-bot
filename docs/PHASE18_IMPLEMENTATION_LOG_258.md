# Phase 18 Implementation Log 258 — Story-Bound Controlled Trial Request

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Baseline reviewed before writing:

- Phase 18 HEAD: `1cae6b7a60b492c180d30f6d2ef1948ecc877440`
- `main` HEAD observed read-only: `abbeebc5fc2cf88d7a58e2f308d9affb075624f7`

No merge, rebase, force update, branch reset, or write to `main` was performed.

## Change Set 258 objective

Close the remaining CPU-side handoff gap between CS257 fresh-story semantic replay and CS233 controlled Golden-trial preflight without granting live-host, generation, pixel, Golden-quality, human-review, or publication authority.

## Added

1. `engine/intelligence/qwen_image_story_bound_controlled_trial_request.py`
   - validates canonical CS257 run receipt;
   - replays byte bindings for the four CS257 artifacts;
   - requires the same story SHA in the semantic replay;
   - requires `production_semantic_replay_executed=true` and `fresh_story_gates_passed=true`;
   - verifies the locked CS233 preflight digest and policy boundaries;
   - binds CS257 receipt, semantic replay, and CS233 preflight bytes into a deterministic request;
   - publishes atomically through a staging directory;
   - rejects symlinked CS257 run directories and symlinked repository-bound file inputs before path resolution;
   - keeps live-host, generation, pixel, Golden, human-review, and publication authority false.

2. `tests/test_phase18_qwen_image_story_bound_controlled_trial_request.py`
   - success case with story binding and closed downstream authority;
   - CS257 artifact tamper rejection;
   - preflight authority-drift rejection;
   - symlinked CS257-run rejection before resolution;
   - symlinked preflight rejection before resolution;
   - existing-output overwrite rejection.

3. `tools/phase18_build_story_bound_controlled_trial_request.py`
   - CPU-only CLI for producing the CS258 request.

4. `docs/PHASE18_CHANGESET_258_STORY_BOUND_CONTROLLED_TRIAL_REQUEST.md`
   - contract, authority, and remaining-path documentation.

5. `docs/PHASE18_IMPLEMENTATION_LOG_258.md`
   - this implementation record.

## Modified

The newly added CS258 module and regression fixture were corrected and hardened during implementation:

- `0ae1762e81ce293124a27d6d7cfcef7d88909a47` corrected the request to source `production_semantic_replay_executed` from the CS257 run receipt rather than the CS238 replay artifact.
- `03491e4fc77c7c709877aca1cba2d4cef27efd97` aligned authority checks with the exact fields guaranteed by the CS257 and CS233 parent contracts.
- `d75becd8ecdc4c5ea55964d5554cd72f24889a7f` aligned the test preflight fixture with the exact CS233 authority fields.
- `14fd42a41c009f850536e4ff4d0fc47b3965340e` hardened path validation so symlink inputs are rejected before `Path.resolve()` can erase symlink identity.
- `06b1fcb2686c5bd71768509b8385f9b76a952032` added regression coverage for both symlinked CS257 run directories and symlinked preflight files.

No existing Fact Lock, identity, sentiment, story-semantic, zero-cost, semantic/layer-ownership, generation-runtime, Visual Critic, Human Review, Golden-quality, branding, typography, or SemanticPublicationGate implementation was relaxed or replaced.

## Deleted

Nothing.

## Commits created during implementation

- `a042219b1d5f5cf114d491632ad73b42e661adef` — initial story-bound controlled-trial request implementation
- `0ae1762e81ce293124a27d6d7cfcef7d88909a47` — correct CS257 authority source
- `fb473e0a1dc6bb774d45f5e7f843c08b6e7abc7f` — initial CS258 regression coverage
- `03491e4fc77c7c709877aca1cba2d4cef27efd97` — exact parent-contract authority alignment
- `d75becd8ecdc4c5ea55964d5554cd72f24889a7f` — exact CS233 test-fixture alignment
- `3bc0d206316a03749282148c56c846a739f2e6fc` — CPU-only CS258 CLI
- `1e5ccf38b34400497f26020099893baca94baf3e` — Change Set 258 documentation
- `fd7ff00696995afeea09dfd130d6dde1235ecf33` — initial CS258 implementation log
- `14fd42a41c009f850536e4ff4d0fc47b3965340e` — pre-resolve symlink hardening
- `06b1fcb2686c5bd71768509b8385f9b76a952032` — symlink fail-closed tests

## Authority state after CS258

Allowed to be true in a genuine successful request:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `live_same_host_recheck_required`

Must remain false:

- `live_host_recheck_passed`
- `controlled_trial_preflight_valid`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_canonical_inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Testing status

Regression coverage now includes the success path, byte-tamper failure, authority-drift failure, output-overwrite failure, and both symlink escape variants. GitHub Actions must still complete on the final CS258 hardening SHA before this Change Set is claimed CI-green. Earlier workflow runs on intermediate CS258 commits are not treated as final evidence.

## Exact remaining blocker

No genuine Qwen-Image-2512 PNG was created. Canonical inference remains blocked until one available execution host proves, in the same live runtime, all required zero-cost constraints including NVIDIA CUDA, native BF16, sufficient live VRAM and system RAM, exact pinned `Qwen/Qwen-Image-2512` revision, compatible Diffusers/QwenImagePipeline, successful required offload/runtime behavior, and `$0-local` execution.

## Remaining path

`genuine current story bytes → CS254/255/253/256 → CS257 independent semantic replay → CS258 story-bound controlled-trial request → live same-host runtime recheck → controlled-trial preflight validity → separate canonical generation authorization → genuine Qwen-Image-2512 inference → byte-bound semantic/layer QA → byte-bound Visual Critic → Human Review → Golden >= 8.5 / elite >= 9.0 → exact brand/typography → SemanticPublicationGate`.
