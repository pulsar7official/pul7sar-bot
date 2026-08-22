# PUL7SAR Phase 18 — Change Set 050: CUDA-Aware Dtype Selection

## Purpose
Make the first real `$0-local` FLUX.2 GPU proof portable across heterogeneous free/self-hosted CUDA runtimes without assuming that every GPU with enough VRAM supports native `bfloat16`.

This change does not alter the approved model, the generation prompt, the four Golden Visual seeds, the platform dimensions, or the `$0-local` cost policy.

## Modified / added files
- `engine/intelligence/local_runtime.py`
- `engine/intelligence/local_dtype.py`
- `engine/intelligence/__init__.py`
- `tools/phase18_local_readiness.py`
- `tools/phase18_flux2_execute.py`
- `tools/phase18_flux2_batch_execute.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`
- `docs/ZERO_COST_VISUAL_PROOF_RUNBOOK.md`
- `tests/test_phase18_local_dtype.py`
- `tests/test_phase18_local_readiness_command.py`
- `tests/test_phase18_colab_notebook.py`

## Runtime probe changes
`LocalRuntimeProbe` still proves CUDA availability, GPU identity and VRAM. It now additionally records, when PyTorch exposes the information:

- `bf16_supported`
- `compute_capability`

Failure to retrieve those optional fields does not invent a capability. The value remains unknown.

## New dtype policy
`LocalDTypeSelector` resolves the requested execution dtype.

Supported requests:
- `auto`
- `float16`
- `bfloat16`
- `float32`

`auto` is now the default real-execution policy:

1. If native BF16 support is explicitly proven, resolve to `bfloat16`.
2. If BF16 is false or cannot be proven, resolve conservatively to `float16`.
3. If a caller explicitly requests `bfloat16` and support is not proven, fail closed.
4. Explicit `float32` remains possible but is never selected automatically because of its higher memory pressure.

The policy only resolves dtype after the normal CUDA/VRAM/model-specific readiness gate passes.

## Executor changes
`phase18_flux2_execute.py` now accepts `--dtype auto` and defaults to it. The resulting machine-readable report records:

- requested dtype
- resolved dtype
- resolution reason
- GPU name
- GPU VRAM
- BF16 support
- compute capability

The batch executor propagates the same fields into each candidate report so all four Golden candidates can be proven to have used the intended precision/runtime context.

## Readiness changes
`phase18_local_readiness.py` now emits a `recommended_dtype` section before model execution. When generation is ready, this predicts the same `auto` decision used by the real executor. When generation is not ready, it leaves the resolved dtype empty rather than pretending a usable GPU path exists.

The readiness command still:
- installs nothing;
- downloads no model weights;
- uses no paid API;
- requires `Flux2KleinPipeline` to exist in the installed Diffusers build.

## Colab changes
The Golden Visual Colab notebook now invokes both the first-candidate smoke proof and the optional full batch with `--dtype auto`. After candidate 1 is generated, it displays the actual GPU name, VRAM, BF16 capability and resolved dtype before displaying the PNG.

This is especially important for zero-cost notebook runtimes because GPU models are not assumed to be homogeneous.

## Quality impact
This is a runtime compatibility/reliability change, not a quality downgrade. It does not lower:

- the strict Golden Visual weighted floor of `8.5/10`;
- the core visual floor of `8.0/10`;
- the `9.0+` elite target;
- semantic publication gates;
- identity or neutrality constraints.

If a runtime cannot satisfy the approved model's CUDA/VRAM requirements, generation still stops. Dtype fallback does not bypass the model readiness gate.

## Production isolation
- `main.py`: untouched.
- Existing publishing: untouched.
- No paid provider/API added.
- No credential added.
- No model weights committed.
- GitHub CPU CI still does not claim a PNG was generated.

## Next execution milestone
The remaining external milestone is unchanged: run the verified Golden batch on a compatible CUDA runtime. Candidate 1 should be executed first with `--limit 1 --dtype auto`; only after it produces a genuine PNG should the remaining seeds be executed and visually compared.
