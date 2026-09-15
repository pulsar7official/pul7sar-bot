# Phase 18 Implementation Log 427 — First Golden Execution Blocker Probe

## Scope

Branch-only change on `phase18/story-intelligence`. `main` is not modified.

CS427 adds a deliberately non-authoritative, download-free probe that turns the remaining First Genuine Golden v6 execution dependency into explicit machine-readable blockers before an authoritative GPU attempt is made.

## Added

- `tools/phase18_probe_first_golden_execution_blocker.py`
  - reports whether both offline flags are asserted;
  - reports whether `$0-local` is asserted;
  - reports CUDA availability, CUDA runtime visibility, CUDA device count, and native BF16 support;
  - resolves the canonical Hugging Face Hub cache root without downloading anything;
  - checks only the exact approved immutable Qwen2.5-VL and FLUX.2 snapshot revision directories;
  - reports local cache filesystem free space for diagnosis;
  - emits explicit blocker codes;
  - never grants generation, publication, Human Visual Review, Golden quality, or Seeds 2–4 authority;
  - returns exit code `2` when prerequisites are incomplete and `0` only when the host is ready to enter the existing authoritative preflight chain.

- `tests/test_phase18_first_golden_execution_blocker_probe.py`
  - proves readiness requires offline mode, `$0-local`, CUDA, native BF16, and both exact approved snapshots;
  - proves a CPU/no-cache/no-offline host reports the concrete blockers instead of fabricating readiness;
  - proves mutable or wrong-revision cache directories do not satisfy the exact snapshot requirement;
  - uses `unittest` so Phase 18's standard discovery harness can execute it without adding dependencies.

## Modified

None.

## Deleted

None.

## Gates preserved

CS427 does not alter prompts, seeds, generation parameters, model IDs, approved immutable revisions, dependency versions, factual/entity/identity checks, sentiment policy, semantic-publication gates, visual-quality gates, or workflow publication authority.

The probe is explicitly advisory/non-authoritative:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Why this reduces the remaining Golden PNG gap

The remaining blocker is environmental rather than editorial: a compatible self-hosted NVIDIA runtime and the exact pinned local model snapshots must exist simultaneously. Previously that condition was distributed across several authoritative preflights. The new probe provides one safe zero-cost diagnostic seam that can be executed on any candidate host without loading models or creating a PNG, so the next real GPU attempt can immediately identify the exact missing prerequisite rather than consuming an expensive/rare execution opportunity and failing deeper in the pipeline.

## Validation status

The previous CS426 HEAD (`76ad04a4e5ecfa19d948d1c87c95bf3be679b89c`) is terminal-green in `Phase 18 Story Intelligence Verification` run `34709512368`.

CS427 must be considered pending until the standard Phase 18 CI completes successfully on the final CS427 HEAD.

## Remaining blocker

No genuine Golden Visual PNG is claimed by this change. Candidate 1 still requires a self-hosted NVIDIA host with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient VRAM/RAM/storage, both approved immutable Qwen2.5-VL and FLUX.2 snapshots already present in local Hugging Face cache, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `$0-local` execution. Network model download and FP16/FP32 substitution remain disallowed.
