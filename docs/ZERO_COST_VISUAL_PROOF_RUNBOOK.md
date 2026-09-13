# PUL7SAR Phase 18 — Zero-Cost Visual Proof Runbook

## Purpose
Produce the first real Phase 18 PNG without a paid image API and without weakening any PUL7SAR quality gate.

The PUL7SAR core stays environment-neutral. A compatible CUDA GPU may be a user-owned/self-hosted machine or a temporary free notebook runtime. The execution environment is replaceable; the generation handoff, seed, prompt, provenance, platform normalization and later quality gates remain PUL7SAR-owned.

## Current approved model
- Provider profile: `local-flux2-klein-4b`
- Model: `black-forest-labs/FLUX.2-klein-4B`
- License: Apache-2.0
- Conservative PUL7SAR VRAM floor: 13 GB
- Backend: Diffusers
- Native canvas alignment: 16 pixels
- Golden Visual precision: documented `bfloat16` path
- Current development cost mode: `$0-local`

No BFL paid API is used by this runbook.

## Tamper-proof portable handoff
Every current GPU handoff uses `pul7sar-local-generation-v2` and contains a canonical SHA-256 over the provider, model, backend, prompt, constraints, canvas, seed, request ID, reference IDs and metadata. The executor validates this digest before any model execution. Changing the prompt, seed, dimensions, provider or `$0-local` metadata invalidates the handoff.

This is intentionally separate from GitHub artifact transport integrity: PUL7SAR verifies the semantic generation payload itself.

## Why the model canvas differs from the platform canvas
FLUX.2/Diffusers uses packed VAE latents and requires aligned image dimensions. PUL7SAR therefore keeps two canvases:

1. **Target platform canvas** — e.g. Instagram feed `1080x1350`.
2. **Native generation canvas** — e.g. `1088x1360`, aligned to 16 pixels.

The generated PNG is deterministically center-cropped/resized back to the exact platform canvas before visual proof registration and semantic acceptance. The final platform output remains exact.

## CPU/CI stage — automated
The normal Phase 18 GitHub workflow builds both a single canonical handoff and a deterministic four-candidate quality batch.

Single canonical request:

```bash
python tools/phase18_build_golden_handoff.py \
  --output output/phase18_handoffs/golden-general-season-opener.json \
  --seed 7007001 \
  --request-id golden-general-season-opener-001
```

Quality-first batch:

```bash
python tools/phase18_build_golden_batch.py \
  --output-dir output/phase18_handoffs/golden-batch \
  --seeds 7007001 7007002 7007003 7007004
```

The batch deliberately varies only the deterministic seed. Prompt, model, platform geometry, constraints and cost policy stay identical. `manifest.json` records each candidate's request ID, exact native/target canvas and SHA-256 so candidates can be compared fairly after generation.

## Pre-GPU transport verification
Before model loading, verify the whole batch without CUDA or network access:

```bash
PYTHONPATH=. python tools/phase18_verify_golden_batch.py \
  --manifest output/phase18_handoffs/golden-batch/manifest.json
```

The verifier checks every v2 handoff hash, manifest-to-handoff SHA, request ID, seed, approved provider/model/backend, `$0-local` lock, native/target canvas and exact one-to-one candidate file coverage. Unknown or unmanifested candidate files fail closed.

## GPU runtime preparation
Use Python 3 with an existing CUDA-enabled PyTorch installation. Install only the optional Phase 18 packages:

```bash
pip install -r requirements-phase18-gpu.txt
```

Do not replace a working CUDA PyTorch build with a CPU-only wheel.

Then verify the environment:

```bash
PYTHONPATH=. python tools/phase18_local_readiness.py
```

Readiness proves the installed Diffusers build exposes `Flux2KleinPipeline`; generic package import is not sufficient. Execution stops if CUDA, VRAM, backend or model-specific pipeline readiness is not proven.

The readiness report also exposes `recommended_dtype` and `golden_generation_ready`. The current Golden Visual benchmark follows the model's documented Diffusers `bfloat16` configuration. `--dtype auto` therefore means **prove native BF16 support and use BF16**. If BF16 support is false or cannot be proven, Golden generation stops; it does not silently switch to FP16 or another unverified precision. This keeps the first benchmark comparable to the documented reference path rather than trading quality certainty for broader hardware compatibility.

## First real GPU smoke proof — candidate 1 only
Use the same sequential batch executor that will later produce the complete four-candidate set, but limit it to the first locked candidate:

```bash
PYTHONPATH=. python tools/phase18_flux2_batch_execute.py \
  --manifest output/phase18_handoffs/golden-batch/manifest.json \
  --limit 1 \
  --generation-dir output/phase18_generated \
  --proof-dir output/phase18_visual_proof \
  --dtype auto \
  --result output/phase18_visual_proof/first-candidate-execution.json
```

`--limit 1` does not alter the four-candidate manifest. It only reduces the execution scope so the CUDA runtime, model loading, native canvas, normalization and proof registration can be proven before spending runtime on seeds 2–4.

The single-request executor writes a dedicated JSON result file for every delegated candidate. Batch control reads that file rather than parsing stdout, so normal Diffusers/Transformers progress output cannot corrupt machine-readable execution state.

## Execute the full quality batch with one command
After candidate 1 proves the GPU runtime is stable, run all four sequentially:

```bash
PYTHONPATH=. python tools/phase18_flux2_batch_execute.py \
  --manifest output/phase18_handoffs/golden-batch/manifest.json \
  --generation-dir output/phase18_generated \
  --proof-dir output/phase18_visual_proof \
  --dtype auto \
  --result output/phase18_visual_proof/batch-execution.json
```

The batch executor never runs candidates in parallel. It delegates every candidate to the exact same single-request execution path, validates returned deterministic seed/request identity and confirms the result stayed on BF16, then stops immediately on the first failed candidate. This avoids VRAM contention and prevents one candidate from bypassing the normal integrity/readiness/provenance/normalization/precision gates.

The single-request executor performs, in order:

1. Validate handoff version, SHA-256 and `$0-local` lock.
2. Confirm approved FLUX.2 model/provider/backend IDs.
3. Confirm CUDA, VRAM and model-specific Diffusers readiness.
4. Prove native BF16 support and resolve the Golden dtype to `bfloat16`.
5. Load `Flux2KleinPipeline` locally through Diffusers.
6. Generate using the locked prompt and deterministic seed.
7. Validate native result provider/model/backend/request ID/seed/dimensions.
8. Normalize native aligned canvas to the exact platform canvas.
9. Write the real PNG and JSON provenance to `output/phase18_visual_proof/`.
10. Persist a dedicated machine-readable executor result for robust batch orchestration.

## Build the human review template
After the full real batch exists, build a review file from the execution report:

```bash
PYTHONPATH=. python tools/phase18_build_golden_review_template.py \
  --execution-report output/phase18_visual_proof/batch-execution.json \
  --output output/phase18_visual_proof/golden-review.json
```

PUL7SAR copies the exact request IDs, seeds, PNG paths and metadata paths into the review template. Every visual score is deliberately `null` until the real PNG is inspected; no visual judgment is fabricated. Hard blockers default to `false` only as an editable checklist and must be changed to `true` wherever observed.

After all six 0–10 score fields are completed for every candidate and blockers are reviewed, select through the quality gate:

```bash
PYTHONPATH=. python tools/phase18_review_golden_batch.py \
  --execution-report output/phase18_visual_proof/batch-execution.json \
  --review output/phase18_visual_proof/golden-review.json \
  --output output/phase18_visual_proof/golden-selection.json
```

A candidate cannot win through score alone if it has fantasy/monument staging, fake logos/crests, pseudo-text, an invented result, cluttered collage treatment, or broken geometry/anatomy.

### Strict visual approval bar
The Golden Visual bar is intentionally higher than a merely attractive or technically successful image:

- Weighted score must be **at least 8.5/10**.
- Editorial realism, composition hierarchy and protected-zone cleanliness must each be **at least 8.0/10**.
- A weighted score of **9.0/10 or higher** is classified as `elite` and is the target for flagship PUL7SAR visuals.
- Any hard blocker forces `below_golden`, regardless of numeric score.

This prevents a 7/10 or low-8/10 image from being promoted simply because the generation pipeline worked.

## What is recorded
The proof/execution metadata preserves:
- provider ID
- model ID
- backend and backend version
- seed
- request ID
- native and target dimensions
- normalization crop
- requested and resolved dtype
- GPU name and VRAM when available
- BF16 support and CUDA compute capability when available
- Diffusers version when available
- PyTorch version when available
- FLUX inference steps
- guidance scale
- CPU-offload state
- `$0-local` mode

## Publication status
A generated proof is **not automatically publication-ready**.

The first PNG must still pass PUL7SAR's independent subject/framing, semantic-defect, forbidden-visual, protected-region and — when applicable — identity-similarity checks. The Semantic Publication Gate remains fail-closed. Golden Visual approval is an additional aesthetic gate, not a substitute for semantic safety.

## Colab execution path
`notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb` provides the current lowest-friction free-GPU path. It checks for a GPU, installs only the Phase 18 GPU requirements, proves FLUX-specific and BF16 Golden readiness, builds and verifies the deterministic batch, executes candidate 1 through `--limit 1 --dtype auto`, reads the structured execution report, confirms the result resolved to BF16, and displays the real proof. Full-batch generation remains intentionally opt-in after candidate 1 proves the runtime stable.

## Golden Visual benchmark
For the first general-season proof, evaluate at minimum:
- premium editorial realism, not fantasy
- convincing stadium depth and controlled lighting
- coherent visual hierarchy
- natural PUL7SAR red environmental accent
- clean protected logo/headline/footer zones
- no fake logos or pseudo-text
- no invented winner/result
- no cluttered collage feeling
- strong platform crop/composition

A technically successful generation that looks mediocre is a failed visual proof and must be regenerated or the prompt/model/composition improved.
