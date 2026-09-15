# Phase 18 Implementation Log — CS460

## Scope
CS460 advances the first genuine Golden Visual path by wiring the CS459 freshness-bound canonical wrapper into a dedicated self-hosted GPU workflow. The change is restricted to `phase18/story-intelligence`; `main` is not modified.

## State reviewed before change
The branch started at `a178d1d332f5cfb1e7e94c3f4ecfc37b0f8a705f` (CS459). GitHub Actions runs retrieved for that exact head were completed successfully. CS459 already provided `tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py`, but the existing canonical GPU workflow still directly invoked the older attested launcher, leaving freshness enforcement outside the dispatch path.

## Added
- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - Manual dispatch only.
  - Exact `phase18/story-intelligence` branch and immutable SHA enforcement.
  - `main.py` isolation check.
  - Self-hosted CUDA/BF16 runner labels only.
  - `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` retained.
  - Refuses FP16/FP32 substitution.
  - Calls the CS459 freshness-bound canonical wrapper with explicit receipt, attestation, summary, handoff, attempt-contract, freshness-baseline, and freshness-verification paths.
  - Replays the freshness result before source binding.
  - Keeps authoritative/generation/network/publication/Seeds 2–4 authority closed.
  - Replays exact source-commit provenance and uploads evidence, including freshness artifacts.
- `tests/test_phase18_first_golden_fresh_workflow.py`
  - Locks runner labels, branch, zero-cost/offline policy, main isolation, wrapper entrypoint, argument coverage, step ordering, native BF16, and closed authorities.
- `docs/PHASE18_IMPLEMENTATION_LOG_460.md`
  - This record.

## Modified
None.

## Deleted
None.

## Tests performed before repository write
A local isolated copy of the new workflow and regression test was executed with Python `unittest`; all four workflow-contract tests passed. The repository CI remains the authority for integration verification after the commit lands.

## Preserved gates
No factual, identity, sentiment, semantic-publication, visual-quality/Human Review, approved model identity/revision, Candidate 1 prompt/seed/steps/dimensions/guidance, native-BF16, zero-cost, offline-only, publication, or Seeds 2–4 gate is relaxed by CS460.

## Remaining blocker
CS460 does not create or claim a Golden PNG. A genuine Candidate 1 attempt still requires an available self-hosted NVIDIA runner satisfying the existing CUDA-enabled PyTorch, real CUDA device, native BF16, approved GPU/compute capability, VRAM/RAM/cache headroom, compatible generation/semantic runtimes, and exact locally cached approved Qwen2.5-VL and FLUX.2 snapshots. Network model download and FP16/FP32 quality substitution remain forbidden.
