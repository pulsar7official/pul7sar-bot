# PUL7SAR Phase 18 — Change Set 157

## Immutable FLUX Model Revision Lock

### Problem

Phase 18 already locked the FLUX.2 Klein 4B model repository name, local provider,
BF16 precision, seed, canvas, prompt handoff, and generation provenance. The
upstream Hugging Face repository itself was still addressed through the mutable
repository default revision. A future upstream `main` update could therefore
change model/tokenizer/config bytes without changing the PUL7SAR request identity.
That would weaken reproducibility of the first genuine Golden Visual and make a
later provenance replay unable to prove the exact upstream model revision.

### Approved upstream revision

Model: `black-forest-labs/FLUX.2-klein-4B`

Pinned full Hugging Face commit SHA:

`e7b7dc27f91deacad38e78976d1f2b499d76a294`

Public upstream evidence used for this lock:

- https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/commit/e7b7dc27f91deacad38e78976d1f2b499d76a294
- https://huggingface.co/api/models/black-forest-labs/FLUX.2-klein-4B

This is a reproducibility lock, not a quality claim and not a permission to bypass
Golden review.

### Added

- `engine/intelligence/approved_model_revisions.py`
  - stores the approved FLUX repository identity and immutable 40-character commit SHA;
  - validates full commit-SHA syntax;
  - extracts and verifies canonical Hugging Face `snapshots/<revision>` cache paths;
  - rejects cache revision drift rather than trusting a mutable ref.
- `tests/test_phase18_flux_model_revision_lock.py`
  - validates the full commit lock;
  - rejects noncanonical/short/drifted snapshot revisions;
  - proves Diffusers receives the pinned revision;
  - proves the prefetch command uses the same revision for local-only lookup and download.

### Modified

- `tools/phase18_prefetch_flux2.py`
  - cache lookup now uses `revision=<approved full SHA>`;
  - download now uses the same immutable revision;
  - the resolved Hugging Face cache snapshot must equal the approved revision;
  - receipt schema raised to `pul7sar-phase18-model-cache-v2`;
  - receipt now records `model_revision`, `resolved_snapshot_revision`, and `revision_pinned=true`.
- `engine/intelligence/flux2_klein_diffusers.py`
  - `Flux2KleinPipeline.from_pretrained` is now called with the approved immutable revision;
  - the factory rejects model-identity or revision drift;
  - generated backend metadata records the model revision.
- `engine/intelligence/generation_provenance_lock.py`
  - visual-proof metadata must contain the exact approved FLUX revision;
  - the verified provenance receipt now returns the model revision;
  - revision tampering fails closed before semantic/Golden continuation.
- `tests/test_phase18_generation_provenance_lock.py`
  - fixtures now include the approved model revision;
  - adds explicit revision-drift rejection coverage.

### Deleted

None.

### Preserved gates

This change does not alter or weaken Fact Lock, Entity/Identity Verification,
Sentiment/Neutrality, `$0-local`, native BF16, Candidate/request/seed/canvas/SHA
locks, generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions,
Qwen BASE_SCENE or HYBRID_SURFACE inspection, deterministic football geometry,
Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography
Integrity, SemanticPublicationGate, or final publication readiness.

The pinned FLUX model remains the existing zero-cost engineering/runtime choice;
no claim is made that this lightweight model alone satisfies Elite visual quality.

### Remaining gap

A genuine Candidate 1 still requires an available compatible NVIDIA CUDA host with
native BF16 and sufficient live free VRAM. No PNG or benchmark is fabricated by
this change. Once such a host is available, both cache acquisition and actual
Diffusers loading now target exactly the same upstream model commit, and the
resulting proof metadata must preserve that revision through provenance replay.
