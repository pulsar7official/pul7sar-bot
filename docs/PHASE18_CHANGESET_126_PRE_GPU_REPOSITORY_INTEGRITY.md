# PUL7SAR Phase 18 — Change Set 126

## Pre-GPU Repository Integrity Gate

This change is limited to `phase18/story-intelligence`. `main` is not modified.

## Why this change exists

The first genuine Golden Hybrid v5 GPU window is expensive in time even under the `$0-local` policy. Phase 18 already proves the Golden batch, CUDA/BF16 host, Qwen runtime/model, FLUX snapshot, provenance, semantic ownership and downstream visual-quality gates. The remaining repository-side risk was that an exact-reference study asset could drift and only be discovered after GPU preparation.

The active Phase 18 reference-brand study transport is now the compact member-pinned Base85+zlib master under `assets/brand/compact_v1`. The older `assets/brand/pul7sar_reference_master_v1.zip.b64` remains a historical truncated transport and is explicitly non-authoritative. It must never be promoted by convenience into the active brand source, and neither reference study asset is a publication master.

## Added

### `engine/intelligence/pre_gpu_repository_integrity.py`

Adds a CPU-only, zero-network, zero-GPU integrity gate. It verifies:

- execution is on `phase18/story-intelligence`;
- `EmbeddedBrandMasterLoader` still targets `assets/brand/compact_v1`;
- all compact transport/member SHA locks successfully replay;
- the compact master still points to the approved source-reference SHA;
- the compact master is self-contained and member-pinned;
- no font recreation, generator or network is required;
- the compact master remains `study_only=true` and `publication_ready=false`;
- the historical truncated ZIP transport remains `legacy_transport_authoritative=false`.

Its receipt also hard-codes that it grants no generation, queue, PNG or publication authority.

### `tools/phase18_preflight_repository_integrity.py`

Adds a JSON CLI receipt suitable for Colab/self-hosted GPU orchestration. It performs no inference and no model download.

### `tests/test_phase18_pre_gpu_repository_integrity.py`

Adds regression coverage for the current compact master, wrong-branch rejection, legacy-transport non-authority, publication-authority drift, and missing/corrupt compact transport.

## Modified

### `tools/phase18_first_png.py`

The one-command Candidate 1 flow now proves CPU repository/reference integrity immediately after Golden batch integrity and before:

- GPU host qualification;
- Qwen model preparation;
- FLUX model preparation;
- durable queue mutation.

The new repository receipt is carried into the first-PNG evidence payload. Any drift toward publication authority, network/GPU dependency, non-zero-cost mode, or legacy truncated transport authority fails closed.

### `tests/test_phase18_first_png_preflight.py`

The preflight-order regression now proves:

`Golden batch integrity → repository integrity → GPU qualification → Qwen semantic preflight → FLUX cache → BF16 readiness → queue mutation`

It also verifies that a repository preflight which attempts to re-authorize the legacy truncated transport is rejected.

## Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main`, `main.py`, Telegram and production publishing;
- Fact Lock and source/state integrity;
- identity verification;
- sentiment and winner/loser neutrality;
- `$0-local` execution;
- FLUX.2 Klein 4B and native BF16;
- seed/canvas locks;
- generated text/brand/score/crest/exact-geometry exclusions;
- Qwen semantic inspection and layer ownership;
- deterministic football geometry and integrity receipts;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum, `9.0+` elite target);
- exact final brand/typography integrity requirements.

The compact reference-derived master remains study-only. This change does not treat it as the user-approved publication logo master.

## Effect on the first genuine Golden PNG

The change does not fabricate or simulate a GPU result. It reduces the remaining gap by ensuring the next compatible CUDA/BF16 host cannot spend time on Qwen/FLUX preparation or enqueue Candidate 1 while repository-side reference integrity is already broken.
