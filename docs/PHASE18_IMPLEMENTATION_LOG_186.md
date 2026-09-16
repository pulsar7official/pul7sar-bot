# PUL7SAR Phase 18 — Implementation Log 186

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence`

Production branch policy: **never modify `main`**.

## Branch state reviewed first

At the beginning of this run:

- `phase18/story-intelligence` HEAD: `e7b63ddd0375abfed722d374c8ed22b53c53c562`
- `main` HEAD: `098e54517185e410a21a47b878c3dbd12490b2f1`
- compare state: `diverged`
- the branch remained isolated from `main`; no write, merge, force-update, ref move, or direct change was performed against `main` or `main.py`.

The starting Phase 18 HEAD was green in GitHub Actions: Story Intelligence Verification Run `33028267869` completed with `success`, and the returned companion Phase 18 workflows on the same HEAD also completed successfully.

After the code/test changes in this run, the branch comparison remained `diverged`; the latest comparison reported Phase 18 ahead of `main` by 1635 commits and behind by 193 commits.

## Gap found

The canonical Golden Editorial v6 Candidate 1 path already SHA-bound the pinned Qwen semantic preflight/cache, runtime fingerprints, strict staging and resulting PNG. FLUX model-cache preparation was not yet part of the same pre-generation evidence seal.

The combined first-Golden cache-budget preflight also checked whether a model ID had any local snapshot, rather than requiring the exact approved immutable revision. A stale cached revision could therefore be counted as present and reduce the disk budget even though Candidate 1 would still need to download the approved revision later.

This was a real pre-GPU/pre-generation reliability gap, not a visual-quality shortcut.

## Change Set 186 implemented

### Modified

1. `tools/phase18_preflight_first_golden_cache_budget.py`
   - now imports the approved Qwen and FLUX model IDs and immutable upstream revisions from `approved_model_revisions`;
   - probes local cache with both `repo_id` and exact `revision`;
   - validates the returned snapshot path against the approved revision before counting it as cached;
   - treats stale/unrelated snapshots as missing rather than as valid cache evidence;
   - records Qwen and FLUX revisions in the receipt;
   - records `revisions_pinned=true`;
   - preserves `downloads_performed=false`, `$0-local`, and all authority-closure fields.

2. `tools/phase18_colab_first_genuine_resources_locked.py`
   - runs GPU and live host-memory qualification first;
   - runs the combined pinned cache-budget preflight before either model is allowed to download;
   - keeps the pinned Qwen semantic/model preflight inside the same resource lock;
   - explicitly prefetches and validates the exact pinned FLUX snapshot before Candidate 1;
   - validates FLUX cache schema, model ID, immutable revision, resolved snapshot revision, canonical snapshot path and `$0-local`;
   - captures the runtime fingerprint only after both approved model snapshots are ready;
   - adds `cache_budget` and `flux_model_cache` to the SHA-256/byte-size evidence map;
   - upgrades the final schema to `pul7sar-first-genuine-golden-v6-resource-lock-v4`;
   - uses status `FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED`;
   - records `cache_budget_bound=true`, `qwen_model_cache_bound=true`, `flux_model_cache_bound=true`, and the exact FLUX model/revision identity;
   - verifies that strict staging still reports the same pinned FLUX identity.

3. `.github/workflows/phase18-first-genuine-golden-v6.yml`
   - uses the v4 model-cache/resource/runtime/semantic lock contract;
   - requires cache-budget and FLUX-cache evidence in the exact evidence set;
   - replays SHA/size for both new receipts;
   - revalidates the combined cache-budget model IDs/revisions and authority closure;
   - revalidates the exact FLUX cache snapshot/revision and `$0-local`;
   - verifies strict staging still names the same pinned FLUX revision;
   - keeps evidence replay before artifact upload.

4. `tests/test_phase18_first_genuine_golden_v6_workflow.py`
   - regression-locks the order `GPU → RAM → combined cache budget → Qwen → FLUX prefetch → runtime PRE → Candidate 1`;
   - requires the exact approved revisions in the cache-budget tool;
   - rejects the old unversioned `snapshot_download(repo_id=model_id, local_files_only=True)` cache check;
   - requires cache-budget and FLUX-cache receipts in the final evidence set;
   - requires v4 schema/status and replay of both pinned model caches.

### Added

1. `docs/PHASE18_CHANGESET_186_PINNED_MODEL_CACHE_EVIDENCE.md`
2. `docs/PHASE18_IMPLEMENTATION_LOG_186.md`

### Deleted

None.

## Safety / quality gates preserved

No gate was weakened. The following remain fail-closed:

- Fact Lock;
- Entity / Identity Verification;
- Sentiment / Neutrality and losing-side respect;
- `$0-local` execution policy;
- pinned FLUX.2 Klein 4B upstream revision;
- pinned Qwen2.5-VL upstream revision and semantic verifier identity;
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
- Golden visual-quality floor of 8.5 and 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- publication remains false until every downstream gate passes;
- Seeds 2-4 remain unauthorized until Candidate 1 exists genuinely and passes review.

## Testing state

Baseline HEAD `e7b63ddd0375abfed722d374c8ed22b53c53c562` was green before modification, including Story Intelligence Verification Run `33028267869` and returned companion Phase 18 workflows.

Change Set 186 code, workflow, regression tests and documentation have been pushed to `phase18/story-intelligence`. A fresh GitHub Actions result tied to the final Change Set 186 HEAD must be inspected before this change set is called CI-green. No success is claimed prematurely.

## Genuine Golden PNG status

No Golden Editorial v6 PNG was fabricated or claimed.

The exact remaining external execution blocker is the absence, in the environment available to this automation, of a usable self-hosted host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM;
- safe local Diffusers execution/offload;
- pinned FLUX revision and exact local snapshot;
- pinned Qwen revision and exact local semantic snapshot;
- stable approved runtime fingerprint;
- `$0-local` execution.

Change Set 186 materially reduces the remaining gap because a stale cached model revision can no longer reduce the shared disk budget, and the exact approved FLUX snapshot is now proven and SHA-bound before Candidate 1 enters generation rather than being resolved implicitly inside the executor.
