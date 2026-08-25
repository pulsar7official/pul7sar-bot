# PUL7SAR Phase 18 — Implementation Log 157

## Scope and branch state

Repository: `pulsar7official/pul7sar-bot`

Write target: `phase18/story-intelligence` only.

Starting Phase 18 HEAD reviewed before changes: `cef9988ccc0a60fc71636c44da3420edc2c77089`.

`main` was independently at `5c95eff1aaf404491304835898b719911e0647a1` when reviewed. `main` / `main.py` were not modified, merged, force-updated, or used as a write target.

Change Set 156 verification is now confirmed: GitHub Actions Phase 18 Story Intelligence Verification run `32897769836` completed with `success` on `cef9988ccc0a60fc71636c44da3420edc2c77089`.

## Change Set 157 — Immutable FLUX Model Revision Lock

### Why this materially reduces the remaining gap

The first genuine Golden Candidate was already locked to the FLUX.2 Klein 4B
repository name, BF16, request/seed/canvas, prompt handoff, queue/provenance, and
semantic/visual gates. However, Hugging Face repository `main` is mutable. Cache
prefetch and Diffusers loading could therefore resolve different upstream bytes
at different times while still reporting the same model ID.

Change Set 157 locks the actual upstream FLUX repository commit and carries that
revision into generated proof metadata and provenance replay. This removes model
revision drift as a source of irreproducible Candidate 1 output.

Approved FLUX revision:

`e7b7dc27f91deacad38e78976d1f2b499d76a294`

The public Hugging Face model API and commit history identify this as the current
upstream `black-forest-labs/FLUX.2-klein-4B` revision used for this lock.

### Added

- `engine/intelligence/approved_model_revisions.py`
  - exact FLUX model ID and immutable revision;
  - full-SHA validation;
  - canonical Hugging Face snapshot revision extraction;
  - fail-closed snapshot revision comparison.
- `tests/test_phase18_flux_model_revision_lock.py`
  - full revision syntax and model identity;
  - exact cache revision enforcement;
  - noncanonical/short revision rejection;
  - Diffusers revision propagation;
  - prefetch revision-lock regression coverage.
- `docs/PHASE18_CHANGESET_157_IMMUTABLE_FLUX_MODEL_REVISION.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_157.md`.

### Modified

- `tools/phase18_prefetch_flux2.py`
  - local cache lookup and network acquisition now pass the same immutable revision;
  - cache snapshot must resolve to the approved full SHA;
  - cache receipt upgraded to `pul7sar-phase18-model-cache-v2` and records both approved and resolved revisions.
- `engine/intelligence/flux2_klein_diffusers.py`
  - `from_pretrained` now receives the immutable revision;
  - model/revision identity drift is rejected;
  - runtime result metadata records `model_revision`.
- `engine/intelligence/generation_provenance_lock.py`
  - registered visual-proof metadata must carry the exact approved model revision;
  - provenance result exposes the locked model revision.
- `tests/test_phase18_generation_provenance_lock.py`
  - fixtures include immutable model revision evidence;
  - model-revision tampering is rejected explicitly.

### Deleted

None.

## Preserved contracts and gates

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model identity;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text / platform branding / exact facts / entity marks / sport geometry prohibitions;
- Qwen BASE_SCENE and HYBRID_SURFACE semantic inspection;
- deterministic football geometry ownership;
- generation provenance/evidence replay requirements;
- Golden visual-quality thresholds (8.5 minimum, 9.0+ elite);
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate / final publication readiness.

The revision lock adds no paid provider, no secret, no precision downgrade, no
fake image, and no publication authority.

## Tests

Regression coverage added/updated for:

- exact 40-character approved FLUX revision;
- canonical Hugging Face snapshot path requirement;
- snapshot revision mismatch rejection;
- Diffusers loader receiving the approved revision;
- prefetch local lookup and download using the same revision;
- provenance rejection if proof metadata reports another model revision.

GitHub Actions status for the final Change Set 157 head must only be recorded after
an actual run result is available. No CI success is inferred from local reasoning.

## Remaining exact blocker to first genuine Golden Visual PNG

No compatible physical execution host is available in the current tool/runtime
environment. Candidate 1 still requires an NVIDIA CUDA host that proves native
BF16 and sufficient live free VRAM for FLUX.2 Klein 4B, followed by the required
Qwen semantic inspection. No PNG, visual score, benchmark, or GPU success is
fabricated.

Current intended path:

`immutable Phase 18 source → repository/runtime/cache checks → immutable FLUX revision → Qwen readiness → Original Scene admission → Candidate 1 lease → lease-bound live GPU requalification → genuine FLUX PNG → revision-bound provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed human review → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`

Seeds 2–4 remain unauthorized until Candidate 1 exists genuinely and passes the
required semantic and visual review gates.
