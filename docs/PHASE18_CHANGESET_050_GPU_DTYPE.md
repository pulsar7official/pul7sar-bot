# PUL7SAR Phase 18 — Change Set 050: CUDA-Aware Golden Dtype Verification

## Purpose
Make the first real `$0-local` FLUX.2 GPU proof truthful across heterogeneous free/self-hosted CUDA runtimes without assuming that every GPU with enough VRAM supports the documented `bfloat16` reference path.

This change does not alter the approved model, generation prompt, four Golden Visual seeds, platform dimensions, or `$0-local` cost policy.

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
- `tests/test_phase18_flux2_batch_execute.py`
- `tests/test_phase18_colab_notebook.py`

## Runtime probe changes
`LocalRuntimeProbe` still proves CUDA availability, GPU identity and VRAM. It now additionally records, when PyTorch exposes the information:

- `bf16_supported`
- `compute_capability`

Failure to retrieve those optional fields does not invent a capability. The value remains unknown.

## Final dtype policy
During implementation an FP16 fallback was considered for broader notebook compatibility. Before the first real benchmark, the official FLUX.2 Klein 4B Diffusers reference path was rechecked and its documented configuration uses `torch.bfloat16`. Because PUL7SAR's requirement is quality first, the Golden Visual path was tightened before any PNG was generated.

The final `LocalDTypeSelector` supports only:
- `auto`
- `bfloat16`

For the Golden Visual benchmark:

1. `auto` means native BF16 support must be explicitly proven.
2. If BF16 support is true, resolve to `bfloat16`.
3. If BF16 support is false or unknown, fail closed.
4. Explicit `bfloat16` also fails unless support is proven.
5. `float16` and `float32` are not accepted by the Golden executor merely to widen hardware compatibility.

This avoids creating the first quality baseline under a precision mode that has not been accepted as the PUL7SAR reference configuration.

## Executor changes
`phase18_flux2_execute.py` defaults to `--dtype auto`, but `auto` is a proof policy rather than a fallback policy. The resulting machine-readable report records:

- requested dtype
- resolved dtype
- resolution reason
- GPU name
- GPU VRAM
- BF16 support
- compute capability

The batch executor additionally rejects any candidate result whose resolved dtype is not `bfloat16`.

## Readiness changes
`phase18_local_readiness.py` distinguishes:

- generic model/backend generation readiness; and
- `golden_generation_ready` for the documented BF16 benchmark path.

A machine may therefore have CUDA, enough VRAM and `Flux2KleinPipeline`, yet still be rejected for the Golden proof when native BF16 support is not proven.

The readiness command still:
- installs nothing;
- downloads no model weights;
- uses no paid API;
- requires `Flux2KleinPipeline` to exist in the installed Diffusers build.

## Colab changes
The Golden Visual Colab notebook uses `--dtype auto` for candidate 1 and the optional full batch. It explicitly states that `auto` does not authorize a precision downgrade. After candidate 1, it asserts that the resolved dtype is `bfloat16` before displaying the PNG.

This means some free notebook GPU assignments may be rejected. That is intentional: the project does not lower the benchmark simply because a free runtime happens to expose weaker hardware.

## Quality impact
This is a quality-preservation change. It does not lower:

- the strict Golden Visual weighted floor of `8.5/10`;
- the core visual floor of `8.0/10`;
- the `9.0+` elite target;
- semantic publication gates;
- identity or neutrality constraints.

## Production isolation
- `main.py`: untouched.
- Existing publishing: untouched.
- No paid provider/API added.
- No credential added.
- No model weights committed.
- GitHub CPU CI still does not claim a PNG was generated.

## Next execution milestone
Run candidate 1 on a compatible CUDA runtime with `--limit 1 --dtype auto`. The readiness stage must report `golden_generation_ready: true`, and the generated candidate must report `resolved_dtype: bfloat16`. Only then should the first PNG be treated as a valid Golden benchmark candidate and visually reviewed.
