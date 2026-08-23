# Phase 18 Change Set 091 — Qwen / Colab Runtime Compatibility Lock

## Problem observed
A genuine Colab run reached the semantic-inspector readiness gate and failed before Qwen inference with an import error involving `PIL._typing._Ink`. The install transcript showed that the notebook had upgraded its preinstalled Pillow 11.x package to Pillow 12.x in-place. The same environment also upgraded Transformers onto a 5.x major line even though the Phase 18 semantic inspector was implemented and regression-tested against the documented Transformers 4.x Qwen2.5-VL public API.

This is a runtime-coherence failure, not a factual, identity, sentiment, visual-quality or GPU-generation success. Phase 18 must fail closed rather than bypass semantic inspection.

## Changes

### GPU dependency compatibility lock
`requirements-phase18-gpu.txt` now keeps the Golden runtime on:

- `transformers>=4.52.1,<5.0.0`
- `Pillow>=11.3.0,<12.0.0`

The FLUX model, Diffusers floor, CUDA/BF16 policy and `$0-local` policy are unchanged.

The Pillow upper bound is intentional for the current Colab path. It prevents the setup cell from replacing the notebook's coherent Pillow 11.x installation with a different major version in the same live Python process before Qwen imports are evaluated.

### Stronger semantic-inspector readiness
`engine/intelligence/semantic_inspector_readiness.py` now:

- rejects an unverified Transformers major version `>=5`;
- imports the public `Qwen2_5_VLConfig` and `pipeline` API exactly as before;
- imports `PIL.Image`, `ImageDraw`, `ImageFont` and `ImageText` together to prove the Pillow runtime is internally coherent;
- rejects an unverified Pillow major version `>=12`;
- reports an explicit `pillow_runtime_incoherent` blocker when Pillow modules cannot import consistently.

The readiness probe still downloads no model weights and remains fail-closed.

### Regression coverage
`tests/test_phase18_qwen_runtime_contract.py` now asserts both compatibility bounds and the Pillow-coherence checks, in addition to preserving the public Transformers API and documented `image-text-to-text` pipeline contract.

## Safety invariants preserved

- `main` and production publishing are untouched.
- No paid provider or paid image API is introduced.
- No semantic-inspection bypass is added.
- Fact Lock, identity verification, sentiment/neutrality, `SemanticPublicationGate` and Golden visual-quality thresholds are unchanged.
- FLUX.2 Klein 4B, native BF16 and the locked Golden seeds/canvases are unchanged.
- No fake PNG, fake semantic result or fake performance evidence is produced.

## Remaining execution blocker
A fresh compatible Colab/CUDA runtime must install the locked dependency range and pass `Qwen25VLReadinessProbe` before the latest Golden Hybrid v5 Candidate 1 can be semantically inspected and deterministically composed. A previous live notebook already contaminated by an in-place Pillow major upgrade may require a runtime restart; Phase 18 must report that incompatibility rather than attempt to work around it by disabling Qwen.
