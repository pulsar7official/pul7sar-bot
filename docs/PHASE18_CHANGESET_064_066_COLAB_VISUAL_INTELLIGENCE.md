# PUL7SAR Phase 18 — Change Sets 064–066

## Purpose
Turn the first genuine Colab/Tesla T4 proof into durable engineering improvements instead of treating it as a one-off demo.

The first real FLUX.2 Klein PNG proved that the `$0-local` GPU execution path works end to end, but visual inspection exposed a composition failure: the model interpreted the general multi-league concept as a four-panel football collage. These change sets preserve the successful generation stack while correcting the Visual Intelligence contract and reducing future Colab interaction to a repeatable semi-automatic runner.

## Change Set 064 — First real T4 Golden Visual proof recorded

### Observed execution
- Host: Google Colab Tesla T4.
- Reported VRAM: approximately 14.56 GiB.
- Model: `black-forest-labs/FLUX.2-klein-4B`.
- Backend: Diffusers `Flux2KleinPipeline`.
- Dtype: locked BF16 path.
- Seed: `7007001`.
- Native canvas: `1088x1360`.
- Exact target canvas: `1080x1350`.
- Inference steps: 4.
- Cost mode: `$0-local`.
- Result status: `REAL_VISUAL_PROOF_GENERATED`.
- Approximate observed execution time: 252.7 seconds on the T4 after low-VRAM sequential offload was enabled.

### What the proof established
The first genuine PNG proved CUDA execution, FLUX.2 loading, real inference, canvas normalization, result persistence, and visual-proof registration. It also proved that the T4 can complete the locked Golden path when sequential CPU offload is used.

### What the proof did not establish
Generation success is not semantic approval, identity approval, Golden-quality approval, publication readiness, or production throughput proof.

## Change Set 065 — Unified-scene Visual Intelligence correction

### Root visual failure
The original Golden benchmark described five major European league atmospheres and five visual zones while also asking for a coherent scene. FLUX interpreted the multi-zone language as a literal four-panel photographic collage. The first proof therefore failed the intended PUL7SAR editorial-art direction even though the image was technically valid.

### `engine/intelligence/visual_router.py`
General-world stories now route toward one unified premium editorial scene with:
- one focal hierarchy,
- continuous perspective,
- integrated narrative variety inside one physical world,
- explicit rejection of collage-style representation.

The resulting `VisualIntent` also carries `composition_grammar=single_continuous_scene` metadata.

### `engine/intelligence/generation_package.py`
Adds a provider-neutral composition contract to every generated base scene:
- one full-bleed image,
- one physical world,
- one coherent camera perspective,
- one unified lighting system,
- no collage,
- no montage,
- no split screen,
- no grid,
- no diptych/triptych/contact sheet,
- no comic/tiled panels,
- no framed windows,
- no image-within-image structure,
- no seams or panel borders.

Metadata records:
- `composition_grammar=single_continuous_scene`,
- `multi_panel_layout_allowed=false`.

This is a base-scene grammar and does not interfere with later deterministic PUL7SAR overlays.

### `engine/intelligence/provider_prompting.py`
FLUX.2 Klein does not use the project’s constraints as a native negative prompt, so the new composition bans are not silently discarded. Three deterministic positive reframes were added for:
- `no collage or multi-panel layout`,
- `no split-screen, grid, diptych, triptych, or contact-sheet framing`,
- `no image-within-image composition`.

The compiler therefore remains fail-closed: an unknown negative constraint is still rejected rather than omitted.

### `tools/phase18_build_golden_handoff.py`
Golden benchmark advances to `golden-visual-general-season-opener-v2`.

The scene is rewritten as one continuous elite European stadium world. The previous phrase `five visual zones` is removed. League breadth is now expressed through harmonized atmosphere, crowd energy, lighting nuance and football culture inside one physical stadium environment.

The benchmark explicitly requires:
- one uninterrupted camera view,
- one vanishing point,
- one main visual axis,
- foreground-to-background depth,
- negative space for deterministic PUL7SAR overlays.

### `tools/phase18_build_golden_batch.py`
Golden batch advances to `pul7sar-golden-batch-v2` and uses v2 request IDs so new proofs cannot be confused with the original collage proof.

The manifest explicitly records `composition_grammar=single_continuous_scene`.

### `tools/phase18_verify_golden_batch.py`
The verifier supports legacy v1 plus the new v2 manifest, but v2 fails closed unless:
- the manifest locks `single_continuous_scene`, and
- every candidate’s SHA-protected prompt contains the mandatory unified-scene instructions.

This prevents a stale or tampered multi-panel prompt from reaching expensive GPU inference under a v2 manifest.

### Regression coverage
`tests/test_phase18_unified_scene_policy.py` covers:
- deterministic FLUX-friendly reframing of all new composition constraints,
- absence of the old `five visual zones` phrase,
- presence of the single-scene lock in the generated request,
- v2 batch round-trip integrity,
- fail-closed rejection of a v2 manifest whose composition grammar is altered.

## Change Set 066 — Semi-automatic Colab runner

### `tools/phase18_colab_runner.py`
Adds one repeatable Colab-facing command that keeps GitHub as the source of truth.

Capabilities:
1. Refuses to run outside `phase18/story-intelligence`.
2. Optional `--update` performs only `git pull --ff-only`; no merge/rebase fallback is allowed.
3. Always rebuilds the Golden batch so stale prompts/hashes from a previous Colab session cannot be reused silently.
4. Verifies the complete Golden batch before GPU work.
5. Re-runs the project’s Golden readiness check.
6. Selects one manifest candidate by number.
7. Runs the locked FLUX executor with the approved dtype path.
8. Persists a durable candidate result JSON.
9. Verifies request ID and seed against the manifest result.
10. Verifies a real PNG exists.
11. Writes `output/phase18_colab/latest.json` with branch, commit, benchmark, seed, SHA-256 identity, model, canvases, runtime and memory evidence where available.
12. When invoked with IPython `%run`, attempts to display the resulting PNG inline automatically.
13. Reuses an already-successful matching result unless `--force` is explicitly supplied.
14. Keeps `publication_ready=false`; generation success cannot bypass semantic or Golden review.

### Intended Colab interaction
After the active notebook has the runner, the normal loop becomes approximately:

```python
%run tools/phase18_colab_runner.py --update --candidate 1
```

Instead of manually copying readiness, batch-build, verify, executor and display commands one by one.

### Regression coverage
`tests/test_phase18_colab_runner.py` covers:
- deterministic manifest candidate selection,
- invalid candidate rejection,
- real existing PNG result resolution,
- rejection of non-success result states.

## Files added
- `tools/phase18_colab_runner.py`
- `tests/test_phase18_unified_scene_policy.py`
- `tests/test_phase18_colab_runner.py`
- `docs/PHASE18_CHANGESET_064_066_COLAB_VISUAL_INTELLIGENCE.md`

## Files modified
- `engine/intelligence/provider_prompting.py`
- `engine/intelligence/generation_package.py`
- `engine/intelligence/visual_router.py`
- `tools/phase18_build_golden_handoff.py`
- `tools/phase18_build_golden_batch.py`
- `tools/phase18_verify_golden_batch.py`
- `docs/PHASE18_IMPLEMENTATION_LOG.md`

## Files deleted
None.

## Production isolation
- `main`: untouched.
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image path: untouched.
- No paid image API added.
- No secret or model weight committed.

## Next validation
Pull the branch into the active Colab checkout, run the new CPU-safe targeted regression tests, then run the v2 candidate 1 through `phase18_colab_runner.py`. The next real PNG should be judged specifically for whether the first-proof collage failure has disappeared. Do not spend GPU time on candidates 2–4 until candidate 1 proves the corrected composition grammar is directionally sound.
