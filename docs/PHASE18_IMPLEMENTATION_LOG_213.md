# Phase 18 Implementation Log — Change Set 213

## Scope

**Change Set 213: Renderer-Safe Dynamic Execution Binding**

All work was performed on `phase18/story-intelligence` only. `main` was inspected independently and was never modified, merged, force-updated, or used as a write target.

## State reviewed before changes

- Phase 18 HEAD at the start of this change: `fe43894e53c15635a7c95ff5611977a71aeb7e77` (`Phase 18: add renderer-safe dynamic transfer handoff builder`).
- `main` HEAD reviewed independently: `813ef31d2647e4353ca604e60e48975c79d7d95e`.
- Recent branch work had introduced `DynamicRendererPromptCompiler`, renderer-safe prompt tests, and a transfer handoff helper after successful Change Set 212.
- No compatible Golden-reference CUDA execution host is available in the current automation environment; no new PNG was generated or fabricated.

## Problems found

### 1. Raw editorial text still reached the canonical measured generation path

`DynamicVisualBrainOriginalSceneBridge` still used the selected concept's raw `scene_prompt` as `OriginalSceneRequest.scene_intent`. The new renderer-safe compiler therefore existed beside, rather than inside, the genuine measured local-admission path.

### 2. Renderer prompt leaked platform language by construction

The first compiler version wrote `PUL7SAR` into a sentence about later headline/branding layers. That conflicts with the long-standing rule that generated base pixels must never be prompted with platform branding.

### 3. Raw story summary was injected into the renderer prompt

The compiler comment said entity names should be omitted when no verified identity asset exists, but the implementation appended `story.summary` directly. A named headline/summary could therefore bias the T2I model toward fabricated people, clubs, kit or branding.

### 4. Renderer-safe translation was not provenance-bound end-to-end

Concept lock/admission/FLUX/Visual Critic provenance bound the editorial concept and exact PNG, but not the renderer-safe translation itself. A renderer prompt could theoretically drift between admission and generation without a dedicated SHA check.

### 5. The new transfer helper declared Dynamic Visual Brain metadata incompletely

The helper set `dynamic_visual_brain_contract` without all of the SHA-locked identity fields required by `_dynamic_visual_brain_result_metadata()`. The durable executor would therefore fail closed rather than execute the helper as written.

## Code changes

### Modified — `engine/intelligence/dynamic_renderer_prompt.py`

- Upgraded contract to `pul7sar-dynamic-renderer-prompt-v2-identity-neutral`.
- Removed raw headline/summary injection.
- Added event-safe, non-identifying factual semantics for transfer, contract, injury, result and preview stories.
- Replaced literal platform naming with generic downstream `headline and brand layers` language.
- Added entity stripping for generic camera/focal/negative-space strings.
- Added final fail-closed platform/entity leak detection.
- Preserved single-scene, no-readable-text, no-logo/crest, no-exact-sport-geometry and physical-coherence constraints.

### Modified — `engine/intelligence/dynamic_visual_brain_original_scene.py`

- Upgraded Original Scene bridge to renderer-safe v2.
- The exact concept remains locked by its original SHA.
- Before entering `OriginalSceneRequest.scene_intent`, the concept is now translated through `DynamicRendererPromptCompiler` with `verified_person_asset=False`.
- Added renderer prompt contract/SHA and identity-neutrality fields to the Original Scene receipt.
- Exact facts, identity references, platform branding, typography and exact sport geometry remain reserved outside generation.

### Modified — `engine/intelligence/dynamic_visual_brain_local_admission.py`

- Upgraded measured local admission to `pul7sar-dynamic-visual-brain-local-admission-v2-renderer-safe`.
- Added renderer prompt contract/SHA/identity-neutrality to the SHA-protected local request metadata and admission receipt.
- Added fail-closed validation that the renderer-safe scene intent is actually present in the local prompt.
- Preserved `$0-local`, semantic inspection, Human review and publication closure.

### Modified — `tools/phase18_flux2_execute.py`

- Dynamic Visual Brain executor evidence now requires and persists:
  - `dynamic_renderer_prompt_contract`;
  - `dynamic_renderer_prompt_sha256`;
  - `dynamic_renderer_identity_neutral`.
- Rejects renderer prompt hash/contract/identity-neutrality drift before generation.
- Non-Dynamic requests remain backward compatible.

### Modified — `engine/intelligence/dynamic_visual_brain_critic_binding.py`

- Upgraded binding contract to renderer-safe v2.
- Admission replay now validates renderer prompt contract/SHA/identity-neutrality.
- Generation replay requires the same renderer prompt identity in the durable executor result.
- Critic approval still cannot grant Human, Golden or Publication authority.

### Modified — `tools/phase18_build_dynamic_transfer_handoff.py`

- Added an explicit concept lock and renderer-safe Original Scene binding before handoff creation.
- Added the complete Dynamic Visual Brain metadata expected by the durable executor.
- Added prompt leak checks for test entity names and platform naming.
- Marked the helper `engineering_handoff_only=true`; measured local runtime admission remains the canonical genuine path.

## Tests added / updated

### Updated

- `tests/test_dynamic_renderer_prompt.py`
- `tests/test_phase18_dynamic_visual_brain_original_scene.py`
- `tests/test_phase18_dynamic_visual_brain_local_admission.py`
- `tests/test_phase18_dynamic_visual_brain_executor_provenance.py`
- `tests/test_phase18_dynamic_visual_brain_critic_binding.py`

### Added

- `tests/test_phase18_dynamic_transfer_handoff.py`

Regression coverage now explicitly checks:

- named story summaries cannot leak entity names to an unverified renderer prompt;
- `PUL7SAR/PULSAR` cannot enter renderer prompts;
- renderer-safe translation is used by Original Scene and measured local admission;
- renderer prompt SHA/contract/identity-neutrality survive into durable FLUX evidence;
- renderer prompt substitution or identity-neutrality drift fails critic replay;
- dynamic transfer handoff is complete enough for the executor's Dynamic Visual Brain metadata gate;
- exact facts/branding/sport geometry remain generator-forbidden;
- Human review stays required and publication stays false.

## CI feedback and repair

The first documented-head Story Intelligence Verification run was **GitHub Actions run `33090584750`**, job `98582021673`.

- Checkout, Python setup and dependency installation succeeded.
- `Syntax and discover validation` executed **1,387 Phase 18 tests** and ended with **11 errors**.
- The newly added transfer handoff tests, renderer-prompt critic-binding tests and executor-provenance tests were already passing.
- All 11 errors happened before the new Original Scene / local-admission code was reached: the two new preview fixtures embedded the literal text `PUL7SAR reports ...`, and the existing `DynamicVisualBrainConceptLock` correctly rejected those fixtures with `DYNAMIC_VISUAL_BRAIN_PLATFORM_NAME_LEAK`.

This was a test-fixture regression, not a reason to relax the production lock. The platform-name lock remains unchanged and fail-closed.

### Fixture repair

The invalid preview summaries in:

- `tests/test_phase18_dynamic_visual_brain_original_scene.py`
- `tests/test_phase18_dynamic_visual_brain_local_admission.py`

were changed from a platform-authored phrase to a neutral verified-source phrase. The tests still assert that `PUL7SAR/PULSAR` cannot reach renderer/local prompts, while the canonical concept lock continues to reject platform naming before rendering.

Repair commits:

- `410109f6a68152e056782ad2311d39c449e39e06` — Original Scene fixture repair.
- `460873c19407f12e6a52c05f7215d270c8f1593d` — measured local-admission fixture repair.

## Final CI verification

The repaired documented-head commit `296f3e58fe3a06b51f3510a391a398e0020889ca` passed **Phase 18 Story Intelligence Verification run `33091023154 / run 3474` with conclusion `success`**.

The completed job confirms:

- `Syntax and discover validation` — success;
- Completion and production isolation — success;
- visual-study handoff build/verification — success;
- cross-platform result composition matrix — success;
- project-native editorial visual study — success;
- adaptive/self-contained reference-brand verification — success;
- Golden Editorial v6 build and verification — success;
- legacy-logo non-canonical assertion — success;
- required artifacts uploaded successfully.

Thus Change Set 213 is CI-green after the fixture repair, with the production platform-name safety lock left intact.

## Added documentation

- `docs/PHASE18_CHANGESET_213_RENDERER_SAFE_DYNAMIC_EXECUTION_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_213.md`

## Deleted

Nothing.

## Safety / quality invariants preserved

No safety or quality gate was relaxed:

- Fact Lock unchanged;
- Entity/Identity Verification unchanged;
- Sentiment/Neutrality and loser-respect unchanged;
- `$0-local` remains mandatory;
- pinned FLUX/Qwen and resource/runtime policies unchanged;
- generated platform branding/text forbidden;
- generated exact facts/numbers forbidden;
- generated entity marks forbidden;
- exact sport geometry outside generator ownership;
- Semantic/Layer Ownership inspection mandatory;
- Visual Critic hard failures fail closed;
- Human review mandatory;
- Golden quality remains `8.5` minimum / `9.0+` elite target;
- Exact Brand/Typography Integrity remains downstream;
- SemanticPublicationGate remains downstream;
- `publication_ready=false` throughout this Change Set.

## Current testing status

**CI-green.** The first run exposed invalid test fixtures and failed closed as intended; the fixtures were repaired without changing production safety behavior, and run `33091023154 / 3474` completed successfully on the repaired code/documentation head.

## Golden Visual status

No new Golden PNG was fabricated in this Change Set.

The project already has genuine rejected visual evidence; the target remains the first **accepted** genuine Golden Visual. The current environment does not expose a compatible approved `$0-local` CUDA host satisfying the required precision/VRAM/RAM/offload/model/runtime evidence gates, so a new real candidate cannot be generated here.

## Remaining blocker / next material step

The canonical Dynamic Visual Brain generation path is now:

`Verified Story → SHA-locked editorial concept → identity-neutral renderer translation → renderer-prompt SHA → provider-neutral Original Scene → measured $0-local local admission → exact local handoff → genuine FLUX result carrying concept + renderer hashes → exact PNG → byte-bound Visual Critic → Human Golden Review`

When an approved compatible GPU host is available, generate a new genuine Dynamic Visual Brain candidate through measured local admission, persist the concept lock/admission/generation/critic evidence together, and allow Human Golden Review only if the renderer-safe end-to-end replay and every existing semantic/visual gate pass.
