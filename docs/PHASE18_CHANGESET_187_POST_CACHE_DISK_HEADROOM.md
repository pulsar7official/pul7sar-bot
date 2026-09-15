# PUL7SAR Phase 18 — Change Set 187

## Post-Cache Disk Headroom Guard

### Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence`

Production policy: **never modify `main`**.

### Problem

The first-Golden cache-budget preflight already proves enough disk capacity exists before missing pinned Qwen and FLUX snapshots are downloaded. That budget is a preflight, not a reservation. Concurrent disk usage, cache expansion, or a larger-than-expected snapshot can reduce free disk after the exact approved FLUX snapshot is present.

Without a second measurement, Candidate 1 could pass the pre-download budget but enter runtime preparation with almost no local working space left for scratch data, receipts and output artifacts.

### Change

1. Added `engine/intelligence/model_cache_headroom.py`.
   - introduces `ModelCacheHeadroomPolicy` and `ModelCacheHeadroomDecision`;
   - uses an 8 GiB conservative post-cache working-space floor by default;
   - rejects invalid or unproven measurements;
   - fails closed with `PHASE18_MODEL_CACHE_POST_HEADROOM_INSUFFICIENT` when the live free-space floor is not met;
   - performs no I/O and grants no generation/publication authority.

2. Updated `tools/phase18_prefetch_flux2.py`.
   - preserves the existing pinned FLUX model ID/revision and pre-download 30 GiB policy;
   - after the exact approved snapshot is present, validated by immutable revision, and confirmed to contain `model_index.json`, re-measures free space on the actual Hugging Face cache filesystem;
   - requires `--minimum-working-free-gib` (default 8.0 GiB) before returning a ready cache receipt;
   - records `working_headroom_after_cache` and `working_headroom_ready=true` in the existing v2 receipt;
   - keeps the change additive and backward-compatible with the current resource-lock/workflow replay contract.

3. Added `tests/test_phase18_model_cache_post_headroom.py`.
   - verifies success at the 8 GiB floor;
   - verifies fail-closed behavior below the floor;
   - rejects invalid policy/measurement values;
   - regression-locks the ordering `pinned snapshot validation → post-cache disk measurement → headroom assertion → receipt`;
   - confirms FLUX prefetch remains before runtime fingerprint capture and Candidate 1.

### Safety / quality invariants

No gate was weakened. The change preserves:

- Fact Lock;
- Entity / Identity Verification;
- Sentiment / Neutrality and losing-side respect;
- `$0-local` execution;
- pinned FLUX and Qwen revisions;
- native BF16;
- GPU VRAM and live system-RAM qualification;
- safe local Diffusers/offload rules;
- runtime fingerprint stability;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/exact-sport-geometry prohibitions;
- Qwen BASE_SCENE and layer-ownership gates;
- Golden visual floor 8.5 and 9.0+ elite target;
- Exact Brand Integrity, Typography Integrity and SemanticPublicationGate;
- `publication_ready=false` until all downstream gates pass;
- Seeds 2–4 remain unauthorized until genuine Candidate 1 exists and passes review.

### Why this reduces the remaining gap

The first compatible GPU session should not be lost because model caching consumed the storage that later runtime stages need. Candidate 1 can now proceed only if the exact pinned FLUX snapshot is ready **and** a live post-cache working-space floor still exists immediately before the runtime fingerprint and strict generation path.

The 8 GiB value is a conservative admission floor, not a claim that it guarantees every possible runtime allocation.

### Genuine Golden PNG status

No Golden Editorial v6 PNG is fabricated or claimed by this change. GPU execution remains externally blocked until a compatible self-hosted host is available with CUDA, native BF16, sufficient live VRAM/RAM, safe local Diffusers execution, exact pinned FLUX/Qwen snapshots, stable runtime fingerprint and `$0-local` execution.
