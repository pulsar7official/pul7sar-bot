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
- Current development cost mode: `$0-local`

No BFL paid API is used by this runbook.

## Why the model canvas differs from the platform canvas
FLUX.2/Diffusers uses packed VAE latents and requires aligned image dimensions. PUL7SAR therefore keeps two canvases:

1. **Target platform canvas** — e.g. Instagram feed `1080x1350`.
2. **Native generation canvas** — e.g. `1088x1360`, aligned to 16 pixels.

The generated PNG is deterministically center-cropped/resized back to the exact platform canvas before visual proof registration and semantic acceptance. The final platform output remains exact.

## CPU/CI stage — already automated
The normal Phase 18 GitHub workflow runs:

```bash
python tools/phase18_build_golden_handoff.py \
  --output output/phase18_handoffs/golden-general-season-opener.json \
  --seed 7007001 \
  --request-id golden-general-season-opener-001
```

The workflow uploads the handoff JSON as an artifact named:

`golden-general-season-opener.json`

This artifact is not an image. It is the locked request that a compatible free GPU runtime must execute.

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

Execution must stop if CUDA/VRAM/backend readiness is not proven.

## Execute the real Golden Visual handoff

```bash
PYTHONPATH=. python tools/phase18_flux2_execute.py \
  --request output/phase18_handoffs/golden-general-season-opener.json \
  --generation-dir output/phase18_generated \
  --proof-dir output/phase18_visual_proof \
  --dtype bfloat16
```

The executor performs, in order:

1. Validate handoff version and `$0-local` lock.
2. Confirm approved FLUX.2 model/provider/backend IDs.
3. Confirm CUDA, VRAM and Diffusers readiness.
4. Load `Flux2KleinPipeline` locally through Diffusers.
5. Generate using the locked prompt and deterministic seed.
6. Validate native result provider/model/backend/request ID/seed/dimensions.
7. Normalize native aligned canvas to the exact platform canvas.
8. Write the real PNG and JSON provenance to `output/phase18_visual_proof/`.

## What is recorded
The proof metadata preserves:
- provider ID
- model ID
- backend
- seed
- request ID
- native and target dimensions
- normalization crop
- dtype
- Diffusers version when available
- PyTorch version when available
- FLUX inference steps
- guidance scale
- CPU-offload state
- `$0-local` mode

## Publication status
A generated proof is **not automatically publication-ready**.

The first PNG must still pass PUL7SAR's independent subject/framing, semantic-defect, forbidden-visual, protected-region and — when applicable — identity-similarity checks. The Semantic Publication Gate remains fail-closed.

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
