# PUL7SAR Phase 18 — Change Set 123

## First-PNG Semantic Preflight Lock

Change Set 123 closes a remaining safety/efficiency gap in the one-command genuine Golden PNG path.

The self-hosted GPU workflow was already upgraded in Change Set 122 to prove Qwen runtime/model readiness before FLUX. However, `tools/phase18_first_png.py` could still be run directly on a GPU host without that same semantic-side preflight. That meant the manual one-command path could consume FLUX GPU time and only discover a broken Qwen runtime/model later.

## What changed

### `tools/phase18_first_png.py`

The one-command path now runs, in fail-closed order:

1. Golden batch build/integrity verification;
2. CUDA/BF16 host qualification;
3. exact Qwen semantic GPU preflight;
4. approved FLUX.2 model cache preflight;
5. FLUX/BF16 readiness;
6. durable Candidate 1 queue mutation;
7. one GPU worker cycle;
8. genuine PNG verification.

The semantic preflight is executed through the existing `tools/phase18_preflight_semantic_gpu.py` boundary and must prove:

- schema `pul7sar-phase18-semantic-gpu-preflight-v1`;
- exact Qwen model `Qwen/Qwen2.5-VL-3B-Instruct`;
- `$0-local` cost mode;
- semantic runtime ready;
- semantic model ready;
- CUDA available;
- `generation_authorized=false`;
- `queue_mutated=false`;
- `png_created=false`;
- `publication_ready=false`.

Any drift fails before FLUX model prefetch and before the durable queue is mutated.

The command now also accepts explicit paths for the semantic-preflight receipt and Qwen model-cache receipt, plus a separate Qwen disk-headroom threshold. The final first-PNG JSON evidence records semantic runtime/model readiness and the exact Qwen receipt paths alongside host, FLUX cache, and GPU-readiness evidence.

### `tests/test_phase18_first_png_preflight.py`

Regression coverage now proves:

- host qualification precedes semantic preflight;
- semantic preflight precedes FLUX cache/readiness and queue mutation;
- the complete fail-closed semantic contract is required;
- any accidental generation/publication authority in semantic preflight is rejected;
- the exact Qwen model, zero-cost policy, Qwen cache receipt, semantic receipt, and Qwen disk-headroom arguments are locked;
- existing host, FLUX cache, and repository-scoping tests remain intact.

## Safety and product invariants preserved

Unchanged:

- `main`, `main.py`, Telegram and production publishing;
- factual/source/state integrity;
- identity verification;
- sentiment and winner/loser neutrality;
- `$0-local` execution;
- FLUX.2 Klein 4B;
- BF16 requirement;
- seed/canvas locks;
- generated brand/text/score/crest/exact-sport-geometry exclusions;
- Base semantic/layer ownership gates;
- Qwen HYBRID_SURFACE inspection;
- SemanticPublicationGate;
- Golden visual thresholds (8.5 minimum, 9.0+ elite target);
- exact brand and typography integrity.

No Fake PNG, paid provider, hosted-GPU fallback, precision downgrade, publication shortcut, or semantic bypass was introduced.

## Why this materially reduces the gap to the first genuine Golden Visual

There are now two independent GPU entrypoints — the manual self-hosted workflow and the one-command first-PNG tool — and both refuse to spend FLUX GPU time until the semantic runtime and approved Qwen snapshot are proven ready on the same CUDA host.

This turns Qwen readiness from a workflow-specific protection into a genuine first-PNG execution invariant.
