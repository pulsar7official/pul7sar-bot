# Phase 18 Change Set 094 — Qwen Model Cache Preflight

## Purpose

Prevent a successful FLUX.2 base-scene generation from being followed by an avoidable late download of `Qwen/Qwen2.5-VL-3B-Instruct` inside the isolated semantic-inspection process. The latest architecture already proves the exact Transformers/Pillow runtime before FLUX, but it did not prove that the semantic model weights themselves were locally available before GPU generation began.

## Added

- `tools/phase18_prefetch_qwen.py`
  - Uses the exact `MODEL_ID` exported by `engine/intelligence/qwen25_vl_inspector.py`.
  - Checks the Hugging Face cache first with `local_files_only=True`.
  - Uses the existing fail-closed `ModelCachePolicy` with a conservative 12 GiB free-space floor when a download is required.
  - Downloads only the approved Qwen repository when it is not cached.
  - Requires `config.json` and at least one `.safetensors` model file before declaring the cache ready.
  - Writes a machine-readable `$0-local` receipt at `output/phase18_gpu_smoke/qwen-model-cache.json` by default.
  - Performs no inference and selects no paid provider.
- `tests/test_phase18_qwen_model_prefetch.py`
  - Locks the exact model ID and `$0-local` semantics.
  - Proves the prefetch path is cache/download preparation only, not inference.
  - Locks prefetch ordering before the Golden runner.
  - Covers observable prefetch success/failure behavior.

## Modified

- `tools/phase18_colab_bootstrap.py`
  - Bootstrap order is now: exact runtime repair -> fresh CUDA/Pillow/Transformers probe -> exact Qwen snapshot cache/prefetch -> protected Golden Hybrid v5 runner.
  - If runtime and model cache are both ready, semantic mode stays `qwen`.
  - If semantic runtime or Qwen model-cache preparation fails in normal development mode, the runner is explicitly switched to `--semantic-inspection none`, which permits only the existing engineering-proof path and keeps `publication_ready=false`.
  - `--strict-semantic` still fails closed if either semantic runtime or model-cache preparation is unavailable.
  - CUDA absence remains fatal; no CPU/fake generation fallback was introduced.

## Deleted

Nothing.

## Safety invariants preserved

No changes were made to `main`, `main.py`, Telegram production publishing, Fact Lock, identity verification, sentiment/neutrality, SemanticPublicationGate, Golden 8.5/9.0 thresholds, FLUX.2 Klein 4B, BF16, seeds, canvas locks, exact-logo integrity, or the `$0-local` policy. No model weights, font files, secrets, fake PNGs, or fabricated benchmark data were committed.

## Why this reduces the remaining gap

The next real Candidate 1 attempt should no longer spend FLUX GPU time and only then discover that Qwen weights must be downloaded within the isolated inspection timeout. Semantic weights are prepared before FLUX. If that preparation is unavailable, development can still produce a clearly labelled engineering visual proof without claiming semantic or publication approval.

## Remaining blocker

A genuine Candidate 1 under the latest Hybrid v5 / semantic-evidence / isolated-Qwen architecture still requires a compatible CUDA/BF16 host. CPU CI cannot produce this PNG and no result is fabricated here. The next GPU run must inspect the single Candidate 1 output before any seeds 2–4 are attempted.
