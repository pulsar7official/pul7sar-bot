# Phase 18 Implementation Log 392 — First Genuine Golden v6 Zero-Cost Contract Regression Guard

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

`main` is read-only and must not be modified, merged, rebased, reset, or force-updated as part of this changeset.

Starting Phase 18 HEAD: `a7d391a62432e33b1f33ae52766fbb3055ad8590`.

The preceding CS391 workflow hardening had already made the official First Genuine Golden v6 path local-cache-only by requiring `$0-local`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and replay-time rejection of model receipts that report a runtime download. Phase 18 Story Intelligence Verification run `34523042527` completed successfully on that exact starting SHA before CS392 began.

## Gap closed

CS391's zero-cost/offline constraints lived in `.github/workflows/phase18-first-genuine-golden-v6.yml`, but there was no dedicated regression test whose purpose was to fail if those critical execution-contract markers were later removed from the workflow.

That left a maintenance gap: a future YAML edit could silently weaken local-only model resolution, CUDA runner qualification, replay-time download rejection, or downstream fail-closed authority without a narrowly targeted contract test making the regression explicit.

CS392 closes that gap without changing generic model-prefetch semantics and without granting any new generation, review, Golden, or publication authority.

## Added

`tests/test_phase18_first_genuine_golden_v6_zero_cost_contract.py`

The regression test reads the canonical First Genuine Golden v6 workflow and asserts that the following safety/execution contract remains explicit:

- `PUL7SAR_PHASE18_COST_MODE: $0-local`.
- `HF_HUB_OFFLINE: "1"` and `TRANSFORMERS_OFFLINE: "1"`.
- Runtime refusal when those offline environment flags are absent.
- The dedicated self-hosted `gpu`, `cuda`, `bf16`, `pul7sar-phase18` runner contract remains present.
- CUDA-enabled PyTorch remains mandatory and automatic PyTorch replacement remains refused.
- Semantic preflight replay rejects `model_downloaded_now != false`.
- Qwen and FLUX cache replay each reject `downloaded_now != false`.
- Strict staging/final evidence keeps Human Review, Golden Quality, publication readiness, and Seeds 2–4 authorization fail-closed at this workflow boundary.

The initial test commit was `053861863a1f55297cca94865f0cb18ab1f104f3`. A first correction produced `4eb9eabc6ebf4fce47499cf9a815a56b798f8ade`, but repository verification later proved that the test still encoded two textual assumptions that did not match the canonical YAML representation.

## CI failure diagnosis and corrective change

`Phase 18 Story Intelligence Verification` run `34529528611` on documentation descendant `baad47a5502e6e6986a4f0c1a44a4b7ee8f801e6` failed at `Syntax and discover validation`; downstream Phase 18 steps were skipped.

Review of the exact CS392 test against `.github/workflows/phase18-first-genuine-golden-v6.yml` identified two contract-test defects rather than production/workflow defects:

1. The test searched for each runner label as a block-list line such as `- gpu`, while the canonical workflow intentionally declares the complete runner contract inline as `runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]`.
2. The test searched for a three-field authority tuple beginning with `golden_quality_approved`, while the canonical replay gate deliberately includes `human_visual_review_approved` in the same fail-closed tuple and checks those fields against the final resource-lock receipt.

The corrective commit `c2442cadc5d915646e62bf112140a856e675cec5` changes only the regression test so that it guards the exact canonical contract actually used by the workflow. It does not weaken or alter the workflow itself.

## Modified

`tests/test_phase18_first_genuine_golden_v6_zero_cost_contract.py` was corrected so runner qualification is asserted against the canonical inline `runs-on` declaration, and downstream authority is asserted against the full fail-closed final-evidence tuple including Human Review.

`docs/PHASE18_IMPLEMENTATION_LOG_392.md` was updated with the exact CI failure diagnosis and corrective commit.

No production Python files were modified.

No workflow file was modified in CS392; CS392 protects the CS391 workflow contract rather than changing it again.

## Deleted

Nothing.

## Dependencies

No dependency was added, removed, or changed. The test uses only Python standard-library `pathlib` and `unittest`.

## Safety / authority preservation

CS392 does not perform model loading, Qwen/FLUX inference, pixel generation, pixel mutation, identity approval, semantic approval, human visual approval, Golden approval, upload, or publication.

It does not weaken factual/freshness, Entity/Identity, sentiment neutrality and loser-respect, `$0-local`, semantic-publication, generated-layer, visual-quality, Human Review, Golden-quality, or publication gates.

It intentionally does not modify `tools/phase18_colab_first_genuine_resources_locked.py`: that utility has broader resource-orchestration/prefetch semantics, whereas the official First Genuine Golden v6 execution workflow is the boundary that must be strictly offline/local-only at inference time.

## Genuine Golden status

No Genuine Golden Visual PNG is claimed or fabricated by this changeset. Genuine inference still requires a compatible self-hosted NVIDIA CUDA/native-BF16 host with adequate RAM/VRAM/storage and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already available locally.

## Verification

The failed run `34529528611` is retained here as part of the implementation history and must not be described as green.

The corrective code-and-test-bearing SHA is `c2442cadc5d915646e62bf112140a856e675cec5`. CS392 is not terminal-green until Phase 18 verification completes successfully on this corrective SHA or a documentation-only descendant with the identical code/test tree.
