# PUL7SAR Phase 18 — Implementation Log 187

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence`

Production branch policy: **never modify `main`**.

## Branch state reviewed first

At the beginning of this run:

- `phase18/story-intelligence` HEAD: `1a076a2896d258429b75b13485df7e10950775f4`
- `main` HEAD: `098e54517185e410a21a47b878c3dbd12490b2f1`
- the Phase 18 branch remained isolated from `main`; no write, merge, force-update, ref move, or direct change was performed against `main` or `main.py`.

The starting Phase 18 HEAD was green in GitHub Actions. `Phase 18 Story Intelligence Verification` Run `33031551696` completed with `success`; the push verification Run `33031549322` also completed with `success`, and the returned companion Phase 18 workflows on the same HEAD completed successfully.

## Gap found

Change Set 186 correctly made the combined Qwen + FLUX cache budget revision-aware before any model download. It also bound the exact pinned FLUX snapshot into Candidate 1 evidence.

The remaining reliability gap was that the pre-download disk budget is not a storage reservation. The exact pinned snapshot can consume more space than expected, or another process can consume cache-disk capacity while the model is being prepared. The path could therefore pass the early cache budget and reach Candidate 1 with dangerously low local working space.

This is a pre-generation reliability gap, not a visual-quality shortcut.

## Change Set 187 implemented

### Added

1. `engine/intelligence/model_cache_headroom.py`
   - adds a provider-neutral `ModelCacheHeadroomPolicy`;
   - uses an 8 GiB conservative post-cache free-space floor by default;
   - validates policy inputs and live byte measurements;
   - returns a structured `ModelCacheHeadroomDecision`;
   - fails closed below the floor using `PHASE18_MODEL_CACHE_POST_HEADROOM_INSUFFICIENT`;
   - performs no download, generation, queue mutation, or publication action.

2. `tests/test_phase18_model_cache_post_headroom.py`
   - verifies eligibility at the 8 GiB floor;
   - verifies fail-closed behavior below the floor;
   - verifies invalid policy/measurement inputs are rejected;
   - regression-locks the FLUX prefetch ordering so post-cache disk measurement occurs only after exact pinned snapshot validation;
   - confirms FLUX prefetch still happens before runtime fingerprint capture and Candidate 1.

3. `docs/PHASE18_CHANGESET_187_POST_CACHE_DISK_HEADROOM.md`
4. `docs/PHASE18_IMPLEMENTATION_LOG_187.md`

### Modified

1. `tools/phase18_prefetch_flux2.py`
   - retains the exact approved immutable FLUX model revision;
   - retains the existing 30 GiB pre-download cache qualification;
   - adds `--minimum-working-free-gib` with a default of 8.0 GiB;
   - after the exact pinned FLUX snapshot exists, its revision is validated, and `model_index.json` is confirmed, re-measures the live free space on the Hugging Face cache filesystem;
   - blocks before Candidate 1 if the remaining live working headroom is below the configured floor;
   - adds `working_headroom_after_cache` and `working_headroom_ready=true` to the existing `pul7sar-phase18-model-cache-v2` receipt;
   - intentionally keeps the receipt schema at v2 because the fields are additive, the current resource-lock already SHA-binds the receipt, and the canonical workflow already replay-verifies the exact FLUX cache receipt.

### Deleted

None.

## Safety / quality gates preserved

No gate was weakened. The following remain fail-closed:

- Fact Lock;
- Entity / Identity Verification;
- Sentiment / Neutrality and losing-side respect;
- `$0-local` execution policy;
- pinned FLUX.2 Klein 4B upstream revision;
- pinned Qwen2.5-VL upstream revision and verifier identity;
- native BF16 requirement;
- total/live-free GPU VRAM qualification;
- live host-memory qualification;
- safe local Diffusers/offload policy;
- runtime fingerprint stability;
- Candidate/request/seed/canvas/SHA locks;
- generated text prohibition;
- generated PUL7SAR branding prohibition;
- generated exact facts/numbers prohibition;
- generated entity-mark prohibition;
- generated exact sport-geometry prohibition;
- Qwen BASE_SCENE semantic QA;
- layer-ownership QA;
- Golden visual-quality floor 8.5 and 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- publication remains false until every downstream gate passes;
- Seeds 2–4 remain unauthorized until genuine Candidate 1 exists and passes review.

## Testing state

Baseline HEAD `1a076a2896d258429b75b13485df7e10950775f4` was green before this change set: Story Intelligence Verification Run `33031551696` and push verification Run `33031549322` both completed successfully, together with the returned companion Phase 18 workflows.

Change Set 187 code and regression tests have been pushed to `phase18/story-intelligence`. A fresh GitHub Actions result tied to the new Change Set 187 HEAD must be inspected before this change set is called CI-green. No success is claimed prematurely.

## Genuine Golden PNG status

No Golden Editorial v6 Candidate 1 PNG was fabricated or claimed.

The exact remaining external execution blocker is the absence, in the environment available to this automation, of a usable self-hosted host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM through execution;
- safe local Diffusers execution/offload;
- exact pinned FLUX revision/snapshot;
- exact pinned Qwen revision/snapshot;
- stable approved runtime fingerprint;
- `$0-local` execution.

Change Set 187 materially reduces the remaining gap because the first compatible GPU session can no longer proceed merely on a pre-download disk estimate: the path now proves that usable cache-filesystem headroom still exists after the exact approved FLUX snapshot is actually ready and before Candidate 1 reaches runtime fingerprinting/generation.
