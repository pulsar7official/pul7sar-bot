# Phase 18 — Change Set 213

## Renderer-Safe Dynamic Execution Binding

### Goal

Move the newest Dynamic Visual Brain work materially closer to a genuine Golden Visual by ensuring that the concept selected editorially is **translated into an identity-neutral renderer prompt before measured local admission**, and that the exact renderer-safe prompt identity remains bound through the durable FLUX result and Visual Critic provenance.

### Problem found

Recent renderer-safe work introduced `DynamicRendererPromptCompiler`, but the canonical measured Dynamic Visual Brain path still built `OriginalSceneRequest.scene_intent` from the raw editorial concept prompt. This left two serious gaps:

1. raw story/concept language could carry entity names or platform naming toward a text-to-image renderer;
2. the renderer-safe translation was not end-to-end provenance-bound from Original Scene admission through FLUX execution and Visual Critic evidence.

The first transfer handoff helper also marked itself as Dynamic Visual Brain without carrying the full SHA-locked metadata required by the durable executor.

### Changes

#### `engine/intelligence/dynamic_renderer_prompt.py`

- Upgraded renderer prompt contract to `pul7sar-dynamic-renderer-prompt-v2-identity-neutral`.
- Removed raw story headline/summary injection from generation prompts.
- Added event-safe factual semantics for transfer, contract, injury, result and preview stories.
- Removed the literal platform name from the prompt; later compositor-owned headline/brand layers are described generically.
- Added entity-name stripping for generic camera/focal/negative-space language.
- Added a final fail-closed platform/entity leak guard.
- Preserved single-scene, no-text, no-branding, no-exact-sport-geometry and physical-coherence rules.

#### `engine/intelligence/dynamic_visual_brain_original_scene.py`

- The canonical Original Scene bridge now compiles the locked concept through `DynamicRendererPromptCompiler` before it can become `scene_intent`.
- Added renderer-prompt contract/SHA and explicit identity-neutrality to the Original Scene receipt.
- Original concept SHA remains preserved separately, so editorial selection remains auditable while renderer translation is independently auditable.

#### `engine/intelligence/dynamic_visual_brain_local_admission.py`

- Upgraded measured local admission to renderer-safe v2.
- Bound renderer-prompt contract/SHA and identity-neutrality into the SHA-protected local generation request metadata and admission receipt.
- Kept `$0-local`, semantic inspection, Human review, and generator ownership restrictions fail-closed.

#### `tools/phase18_flux2_execute.py`

- Durable FLUX results now carry renderer-prompt contract/SHA and identity-neutrality for Dynamic Visual Brain requests.
- Executor rejects missing/invalid renderer prompt hashes, contract drift, or identity-neutrality drift before generation.
- Non-Dynamic requests remain backward-compatible.

#### `engine/intelligence/dynamic_visual_brain_critic_binding.py`

- Upgraded critic binding to renderer-safe v2.
- Critic replay now proves that the renderer-safe prompt admitted before generation is the same renderer-safe prompt identity exposed by the FLUX result that produced the exact PNG.
- Human review remains mandatory; Golden and publication authority remain false.

#### `tools/phase18_build_dynamic_transfer_handoff.py`

- The renderer-safe transfer engineering handoff now freezes a concept lock and Original Scene receipt before writing a handoff.
- It carries the full Dynamic Visual Brain metadata expected by the executor, rather than partial/unbound metadata.
- The generated prompt is checked for entity/platform leakage.
- The helper remains explicitly engineering-only and non-publication-ready; measured runtime admission remains the canonical genuine path.

### Tests added/updated

- `tests/test_dynamic_renderer_prompt.py`
- `tests/test_phase18_dynamic_visual_brain_original_scene.py`
- `tests/test_phase18_dynamic_visual_brain_local_admission.py`
- `tests/test_phase18_dynamic_visual_brain_executor_provenance.py`
- `tests/test_phase18_dynamic_visual_brain_critic_binding.py`
- `tests/test_phase18_dynamic_transfer_handoff.py`

Regression coverage now includes:

- named headlines/summaries never reaching unverified renderer prompts;
- platform-name leakage rejection;
- identity-neutral Original Scene admission;
- renderer prompt SHA propagation into executor evidence;
- renderer prompt substitution rejection at Critic replay;
- renderer identity-neutrality drift rejection;
- transfer handoff completeness against executor Dynamic Visual Brain requirements.

### Safety / quality gates preserved

No gate was relaxed:

- Fact Lock unchanged;
- Entity/Identity Verification unchanged;
- Sentiment/Neutrality and loser-respect unchanged;
- `$0-local` mandatory;
- generated branding/text/exact facts/entity marks/exact sport geometry forbidden;
- semantic/layer ownership inspection mandatory;
- Visual Critic hard failures fail closed;
- Human review mandatory;
- Golden quality remains `8.5` minimum / `9.0+` elite target;
- Exact Brand/Typography Integrity downstream;
- SemanticPublicationGate downstream;
- `publication_ready=false` throughout this change.

### Golden Visual status

No PNG was fabricated. A new accepted Golden candidate still requires a compatible approved `$0-local` CUDA execution host. This change reduces the remaining gap by making the **actual canonical measured Dynamic Visual Brain path renderer-safe before pixels exist**, then preserving that renderer-safe identity through FLUX and critic provenance.
