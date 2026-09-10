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
- The dedicated self-hosted `gpu`, `cuda`, `bf16`, `pul7sar-phase18` runner labels remain present.
- CUDA-enabled PyTorch remains mandatory and automatic PyTorch replacement remains refused.
- Semantic preflight replay rejects `model_downloaded_now != false`.
- Qwen and FLUX cache replay each reject `downloaded_now != false`.
- Strict staging keeps `golden_quality_approved`, `publication_ready`, and `seeds_2_to_4_authorized` fail-closed at this workflow boundary.

The initial test commit was `053861863a1f55297cca94865f0cb18ab1f104f3`. Before relying on CI, the authority assertion was reviewed against the exact workflow text and corrected so it checks the actual strict-staging authority tuple rather than assuming a Human Review field is serialized directly in this YAML. No workflow or production behavior was changed by that correction.

Exact corrected code-and-test-bearing commit: `4eb9eabc6ebf4fce47499cf9a815a56b798f8ade`.

## Modified

`tests/test_phase18_first_genuine_golden_v6_zero_cost_contract.py` was corrected once after creation so the downstream-authority regression matches the real workflow contract exactly.

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

CI for the exact corrected CS392 test-bearing commit must be checked separately. CS392 is not terminal-green until the repository's Phase 18 verification completes successfully on the exact corrected code-and-test-bearing SHA (or a documentation-only descendant whose code tree is unchanged and whose corresponding verification is also successful).
