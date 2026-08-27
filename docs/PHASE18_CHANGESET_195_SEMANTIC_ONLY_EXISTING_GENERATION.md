# PUL7SAR Phase 18 — Change Set 195

## Non-destructive semantic QA against an already generated Candidate 1

### Purpose

Golden Editorial v6 now separates pixel generation from semantic QA in the Colab workflow. The remaining risk was that the semantic step still invoked `phase18_colab_one_command.py`, whose normal path can enter `phase18_colab_runner.py`. If the saved Candidate were missing, stale, or mismatched, a semantic-review command could therefore fall back into generation instead of failing closed.

Change Set 195 makes the semantic phase explicitly non-generative.

### Implemented

#### 1. Explicit semantic-only existing-generation mode

`tools/phase18_colab_one_command.py` now exposes:

`--semantic-only-existing`

When enabled, the command:

- requires `--semantic-inspection qwen`;
- rejects `--force`;
- rejects `--prepare-only`;
- requires an existing Golden v6 `latest.json`;
- requires the requested candidate number to match the saved candidate;
- requires `publication_ready=false`;
- replays `GenerationProvenanceLock` against the existing PNG;
- accepts only verified Golden-reference or engineering-preview generation provenance;
- requires the provenance PNG path to match the exact current saved PNG;
- skips `phase18_colab_runner.py` entirely;
- runs semantic/layer QA only against the already generated pixels.

No semantic-only call may create or replace Candidate 1.

#### 2. Notebook semantic cell uses the new mode

`notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb` now calls:

`phase18_colab_one_command.py --candidate 1 --semantic-inspection qwen --semantic-only-existing --skip-update`

The notebook explicitly states that semantic QA is non-destructive and is forbidden from invoking generation.

#### 3. Regression coverage

Updated `tests/test_phase18_colab_notebook_contract.py` and added `tests/test_phase18_semantic_only_existing_generation.py`.

Coverage locks:

- the explicit semantic-only CLI mode;
- incompatibility with force/prepare/non-Qwen execution;
- durable generation provenance replay before semantic QA;
- candidate identity matching;
- exact PNG identity matching;
- no `phase18_colab_runner.py` call inside the semantic-only branch;
- continued `publication_ready=false` authority.

### Safety and quality gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate was weakened.

The split flow is now:

`Candidate 1 generation -> durable PNG/provenance -> visual display -> semantic-only provenance replay -> Qwen BASE_SCENE/layer QA -> human Golden review`

Semantic failure can block publication but can no longer regenerate, overwrite, or hide an already saved Candidate 1.

### Files

Modified:

- `tools/phase18_colab_one_command.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`
- `tests/test_phase18_colab_notebook_contract.py`

Added:

- `tests/test_phase18_semantic_only_existing_generation.py`
- `docs/PHASE18_CHANGESET_195_SEMANTIC_ONLY_EXISTING_GENERATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_195.md`

Deleted: none.

`main` and `main.py` are not modified by this change set.
