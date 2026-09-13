# Phase 18 Implementation Log — CS441

## Change set

CS441 adds an isolated, non-generating, self-hosted **Attested Host Readiness** workflow for the first genuine Golden Visual. The purpose is to prove the immutable Phase 18 source identity and all currently encoded zero-cost execution prerequisites on the actual NVIDIA host before consuming a Candidate 1 generation attempt.

## Added

- `.github/workflows/phase18-first-golden-attested-host-readiness.yml`
  - Manual dispatch only.
  - Requires the exact `phase18/story-intelligence` branch and immutable `${{ github.sha }}`.
  - Checks out the exact dispatch SHA with complete ancestry and reattaches only `phase18/story-intelligence`.
  - Re-checks `main.py` isolation against `origin/main`.
  - Requires the self-hosted GPU labels already used by the genuine-Golden execution lanes.
  - Forces `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`.
  - Runs `tools/phase18_run_first_golden_pre_gpu_attested.py` using the exact dispatch SHA.
  - Emits the unified pre-GPU receipt, byte-level attestation, and summary under `output/phase18_gpu_smoke/`.
  - Replays the summary and fails closed unless readiness is true, the receipt is attested, blockers are empty, and all network/generation/publication/Seeds authorities remain false.
  - Uploads only diagnostic evidence and does not invoke generation.

- `tests/test_phase18_first_golden_attested_host_readiness_workflow.py`
  - Standard-library `unittest` regression coverage.
  - Locks self-hosted GPU labels, `$0-local`, offline-only environment, immutable source SHA, Phase 18 branch isolation, attested runner invocation, authority closure, and the explicit absence of Golden generation entry points.

- `docs/PHASE18_IMPLEMENTATION_LOG_441.md`
  - This implementation record.

## Modified

None.

## Deleted

None.

## Gates preserved

CS441 does not change prompts, seeds, generation parameters, model IDs, immutable model revisions, dependencies, factual gates, entity/identity gates, sentiment-neutrality rules, semantic-publication gates, visual-quality gates, human-review gates, or publication authority.

The new workflow is diagnostic only. It cannot download models, authorize generation, create a Golden PNG, authorize Seeds 2–4, or publish anything. It reuses the existing CS437/CS438/CS439 source + environment + attestation chain instead of introducing a parallel readiness policy.

## Test intent

The normal Phase 18 CPU verification suite should discover the new test through `unittest discover`. The workflow itself can only prove live GPU readiness when a compatible self-hosted NVIDIA runner is online with the exact approved local model snapshots and compatible runtime.

## Remaining blocker

A first genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA execution host satisfying the existing execution probe: CUDA-enabled PyTorch, at least one CUDA device, native BF16, qualified GPU identity/compute capability, sufficient total and live-free VRAM, sufficient available system RAM, sufficient filesystem headroom, compatible generation and Qwen semantic runtimes, and exact approved Qwen2.5-VL and FLUX.2 snapshots resolvable locally with network downloads disabled.

CS441 materially reduces the remaining gap by providing a single low-risk way to prove all of those prerequisites and bind the proof to the exact source commit before launching any genuine-Golden generation lane.
