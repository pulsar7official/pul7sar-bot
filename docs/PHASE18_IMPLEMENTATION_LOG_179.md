# PUL7SAR Phase 18 — Implementation Log 179

## Branch safety

- Repository: `pulsar7official/pul7sar-bot`
- Development branch: `phase18/story-intelligence`
- Starting Phase 18 head reviewed: `6d26a911f22d2ddfde912bd92ea4e93eae86cf70`
- `main` head reviewed independently: `d44b7436fce129cd8453a93470404e53cf78d788`
- `main` / `main.py` were not modified, merged, force-updated, or used as write targets.

## Change Set 179 — Golden v6 handoff contract repair

### Current CI evidence reviewed

Story Intelligence Verification run `33001945155` completed with failure in `Syntax and discover validation` after 1,246 Phase 18 tests (`6` failures, `24` errors). All companion visual workflows reported for that branch head completed successfully.

The dominant failures were migration-contract issues rather than GPU execution failures:

- `tools/phase18_build_golden_batch.py` raised `KeyError: 'focal_anchor'` because the provider-neutral Golden v6 package carried the locked composition map but the local backend request dropped three fields.
- strict Golden prompt tests required `no specific identifiable real venue` and `approaching rather than already decided` markers.
- the newly locked provider-prompting v6 regression correctly rejected a contextual-turf reframe that still contained the phrase `full playing surface`.
- the Colab Golden v6 notebook lacked explicit `$0-local`, publication-blocked, and 8.5/9.0+ acceptance language.

### Implementation completed

1. `engine/intelligence/local_backend_execution.py`
   - propagates `focal_anchor`, `copy_negative_space`, and `brand_quiet_zone` from the provider-neutral GenerationPackage into LocalBackendGenerationRequest metadata;
   - preserves existing story-first `context_only` geometry ownership and no-pitch-replacement policy.

2. `engine/intelligence/provider_prompting.py`
   - strengthens the non-identifying venue reframe with the exact `no specific identifiable real venue` marker;
   - strengthens unresolved PREVIEW treatment with `approaching rather than already decided`;
   - keeps contextual turf incidental without using the rejected `full playing surface` wording;
   - restores the exact `no specific real-person depiction` marker inside the anonymous-person reframe after CI showed that this final identity marker remained the only failing Golden handoff assertion;
   - continues to fail closed for unknown constraint translations.

3. `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`
   - explicitly states `$0-local`;
   - states publication remains blocked;
   - states strict Golden floor `8.5` and elite target `9.0+`;
   - states exact branding/typography remain deterministic post-generation layers;
   - states semantic/runtime/integrity failures remain fail-closed for publication;
   - keeps T4 FP16 as engineering-preview-only, never Golden-reference proof.

### Existing code reviewed but not weakened

`engine/intelligence/original_scene_local_bridge.py` already recognizes the combined v6 claim `no full-pitch master shot or central broadcast pitch framing` and maps it into approved contextual-turf plus oblique-camera constraints. No bypass or permissive fallback was added.

## Added

- `docs/PHASE18_CHANGESET_179_GOLDEN_V6_HANDOFF_CONTRACT_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_179.md`

## Modified

- `engine/intelligence/local_backend_execution.py`
- `engine/intelligence/provider_prompting.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`

## Deleted

- None.

## Gates preserved

Unchanged and fail-closed:

- Fact Lock / source consensus / sports-state integrity.
- Entity and Identity Verification.
- Sentiment, neutrality, and loser-respect rules.
- `$0-local`; no paid provider or hosted-GPU fallback added.
- Pinned FLUX/Qwen revisions and stable runtime fingerprint requirements.
- Native BF16 Golden path; total/live-free VRAM; host RAM; safe offload; cycle- and lease-bound resource requalification.
- Candidate/request/seed/canvas/SHA and execution-resource provenance locks.
- No generated platform branding, readable typography, exact facts/numbers, entity marks, or exact sport geometry.
- Golden Editorial v6 composition map remains `story_focal_hierarchy_before_sport_surface`, `illuminated_tunnel_lower_left`, `right_center`, `upper_left`.
- PREVIEW remains `context_only`; deterministic pitch replacement remains false.
- Qwen semantic inspection and layer-ownership gates.
- Golden `8.5` minimum / `9.0+` elite thresholds.
- Exact Brand Integrity, Typography Integrity, and SemanticPublicationGate.
- Seeds 2–4 remain unauthorized before genuine Candidate 1 visual acceptance.

## Test state

- Baseline failing Story Intelligence run: `33001945155` — completed/failure, 1,246 Phase 18 tests, 6 failures and 24 errors.
- Companion Phase 18 visual workflows on that baseline head completed successfully.
- Corrective commits:
  - `880a2e6853830faa2ac1c28d69f20a778893c86c` — preserve Golden v6 composition metadata in the local handoff.
  - `4e46b501b40609097c147c01f3e071685e67e6b4` — align provider reframes with strict Golden v6 contracts.
  - `733483d59d3e02b73194be693577a4bd45005fbd` — align Colab notebook with current gated review contract.
  - `54d304348d2ad50505f4409e39d127b1a8d98a00` — restore the final strict real-person marker required by the Golden handoff contract.
- Story Intelligence Verification run `33002375737` on code head `733483d59d3e02b73194be693577a4bd45005fbd` improved the suite to 1,247 tests with only one remaining failure: `test_golden_request_does_not_claim_specific_real_venue_or_person`, specifically the missing exact `no specific real-person depiction` marker. All newly repaired Golden batch/smoke/metadata, notebook, provider-v6, and Original Scene translation tests passed in that run. The remaining marker was then restored in commit `54d304348d2ad50505f4409e39d127b1a8d98a00`.
- No CI-green claim is made for the final corrected head until an actual successful Story Intelligence run completes.

## Genuine Golden PNG status

No genuine Golden Editorial v6 Candidate 1 PNG has been fabricated or claimed.

Exact external execution blocker remains the absence, in the available execution environment, of a host that simultaneously proves NVIDIA CUDA, native BF16, sufficient total/live-free VRAM, sufficient live system RAM through lease/execution, safe local Diffusers offload/runtime, pinned FLUX/Qwen revisions, stable runtime fingerprint, and `$0-local` operation.

## Immediate next work

1. Inspect the first completed Story Intelligence run containing the final real-person marker repair.
2. Repair only any remaining v6 migration boundary revealed by real test evidence; do not weaken gates.
3. Once CPU contracts are green, use the first compatible zero-cost CUDA host for strict Candidate 1 only.
4. Require exact PNG/provenance replay plus Qwen BASE_SCENE/layer-ownership approval.
5. Keep Seeds 2–4 blocked until Candidate 1 passes human Golden visual review.
