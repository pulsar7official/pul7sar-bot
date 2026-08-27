# PUL7SAR Phase 18 Implementation Log — Change Set 195

## Branch isolation

All writes in this change set target `phase18/story-intelligence` only.

Starting Phase 18 HEAD reviewed for this run: `29117803a3d685e243155609d16d68b964ca1864`.

Starting `main` HEAD observed for comparison: `813ef31d2647e4353ca604e60e48975c79d7d95e`.

GitHub compare reported the branches as `diverged`, with Phase 18 ahead by 1686 commits and behind by 208 commits at the review point. `main` and `main.py` were not modified, merged, rebased, force-updated, or used as write targets.

## Baseline verification state

The reviewed Phase 18 HEAD `29117803a3d685e243155609d16d68b964ca1864` is CI-green.

Phase 18 Story Intelligence Verification run `33063341072` / run number `3261` completed with `success`.

The companion Phase 18 workflows returned for the same HEAD also completed successfully, including Composition Matrix, Data Monument, Result Statement, Tactical Intelligence, Adaptive Brand, Event Editorial, Event Hybrid Context, Premium Hybrid Result, and Verified Match Result visual studies.

## Gap identified

Recent Phase 18 work deliberately split generation and semantic QA in the Colab path so Candidate 1 pixels are generated, durably saved, provenance-verified, and displayed before Qwen is loaded.

However, the notebook semantic cell still called `phase18_colab_one_command.py` using its general execution contract. The general contract normally enters `phase18_colab_runner.py`. If the saved generation disappeared, drifted, or was otherwise unavailable, semantic QA could therefore enter generation again instead of failing closed.

That contradicted the new non-destructive generation-before-semantic contract.

## Implemented

### 1. Semantic-only existing-generation execution mode

Modified `tools/phase18_colab_one_command.py` with a new `--semantic-only-existing` mode.

This mode:

- requires Qwen semantic inspection;
- rejects `--force`;
- rejects `--prepare-only`;
- reads the already saved Golden v6 `latest.json`;
- requires the requested Candidate number to match the saved Candidate;
- requires `publication_ready=false`;
- replays `GenerationProvenanceLock` against the exact saved PNG;
- requires verified generation provenance;
- requires the provenance PNG identity to match the current PNG exactly;
- skips `phase18_colab_runner.py` completely;
- continues only to semantic/layer QA of the existing pixels.

This makes semantic QA unable to create, replace, or regenerate Candidate 1.

### 2. Colab notebook now uses the non-destructive semantic contract

Modified `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`.

Step 2 remains generation-only and displays Candidate 1 before Qwen.

Step 3 now calls:

`phase18_colab_one_command.py --candidate 1 --semantic-inspection qwen --semantic-only-existing --skip-update`

The notebook text now states explicitly that semantic QA must reuse the already-saved provenance-verified Candidate and is forbidden from invoking generation.

### 3. Regression tests

Modified `tests/test_phase18_colab_notebook_contract.py` to require the new semantic-only mode in the notebook.

Added `tests/test_phase18_semantic_only_existing_generation.py` covering:

- the new CLI option;
- rejection of force/prepare/non-Qwen combinations;
- durable provenance replay;
- candidate identity binding;
- exact PNG identity binding;
- absence of a runner call from the semantic-only branch;
- continued publication-authority closure.

## Files changed

Modified:

- `tools/phase18_colab_one_command.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`
- `tests/test_phase18_colab_notebook_contract.py`

Added:

- `tests/test_phase18_semantic_only_existing_generation.py`
- `docs/PHASE18_CHANGESET_195_SEMANTIC_ONLY_EXISTING_GENERATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_195.md`

Deleted: none.

## Safety and quality gates preserved

No gate was weakened. The following remain fail-closed:

- factual integrity / Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful result treatment;
- `$0-local` execution;
- pinned FLUX and Qwen revisions;
- native BF16 requirement for Golden-reference proof;
- VRAM/RAM/offload/cache/runtime-fingerprint gates;
- Candidate/request/seed/canvas/SHA identity locks;
- generation and execution provenance;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Qwen BASE_SCENE and layer-ownership QA;
- Golden minimum `8.5` / elite target `9.0+`;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate and final publication readiness;
- Seeds 2-4 remain unauthorized before genuine Candidate 1 succeeds and is visually accepted.

## Test status for Change Set 195

The pre-change baseline is confirmed CI-green.

Change Set 195 code, notebook, tests, and documentation have been committed to `phase18/story-intelligence`. A new Story Intelligence Verification run must complete successfully on a HEAD containing these changes before this change set is described as CI-green.

## First genuine Golden PNG status

No new Golden Editorial v6 PNG was generated or claimed in this change set.

The exact external blocker remains the absence, in the currently available execution environment, of a compatible self-hosted host simultaneously proving:

- NVIDIA CUDA;
- native BF16 for Golden-reference execution;
- sufficient total and live-free VRAM;
- sufficient live system RAM through execution;
- verified safe local Diffusers/offload runtime;
- exact pinned FLUX and Qwen snapshots;
- stable runtime fingerprint;
- sufficient post-cache disk headroom;
- `$0-local` execution.

Safe preparatory progress materially reduced the remaining gap: once Candidate 1 pixels are generated, semantic QA can no longer accidentally regenerate or replace them. It must evaluate the exact saved provenance-verified PNG or fail closed.
