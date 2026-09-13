# PUL7SAR Phase 18 — Implementation Log 154

## Scope

Branch only: `phase18/story-intelligence`

`main` and `main.py` were not modified, merged, force-updated, or used as write targets.

## Starting state reviewed

- Phase 18 branch HEAD at review start: `0dd694a4746c7d8bba22470443d08ba1c91df33a`
- `main` HEAD observed during this run: `93d1db2562a7337df3b89243e08333e3ffa0d330`
- Branch remains `diverged` from `main`; latest compare observed Phase 18 ahead by 1379 commits and behind by 138.
- Previous Phase 18 verification was confirmed green: Story Intelligence Verification Run `32880756783 / 2675` completed with `success`, and all visible companion Phase 18 workflows returned success on the same starting commit.
- No genuine new Golden Hybrid v5 Candidate 1 PNG existed under the latest architecture because no compatible NVIDIA CUDA/native-BF16 execution host was available to this automation run.

## Change Set 154 — Live Free-VRAM Qualification

### Why

Change Set 153 moved GPU host qualification earlier, but the host policy still qualified against physical/total VRAM only. A shared or partially occupied GPU can satisfy a 13 GB total-VRAM floor while having much less than 13 GB available at the moment Candidate 1 starts. That creates a preventable late failure during model load or execution.

### What changed

`LocalRuntimeProbe` now attempts `torch.cuda.mem_get_info(device)` and records live free/used GPU memory. If CUDA memory telemetry is unavailable, it records no evidence instead of estimating.

`GpuHostQualificationPolicy` now requires live free VRAM to be proven and at least the selected model's existing proven minimum VRAM floor. For the current FLUX.2 Klein 4B Golden execution candidate, that remains 13 GB; this Change Set does not alter the model profile or lower any existing threshold.

The strict first-Golden bootstrap and canonical self-hosted workflow now replay this free-VRAM fact before allowing shared cache/model preparation or accepting the sealed Candidate 1 review artifact.

### Bootstrap contract update

Strict bootstrap receipt moved from:

`pul7sar-first-golden-colab-bootstrap-v3`

to:

`pul7sar-first-golden-colab-bootstrap-v4`

New explicit evidence:

- `gpu_free_vram_gb`
- `required_vram_gb`
- `live_free_vram_proven=true`
- host policy `requires_live_free_vram=true`

## Files modified

- `engine/intelligence/local_runtime.py`
- `engine/intelligence/gpu_host_qualification.py`
- `tools/phase18_qualify_gpu_host.py`
- `tools/phase18_colab_first_golden_bootstrap.py`
- `.github/workflows/phase18-first-golden-review.yml`
- `tests/test_phase18_local_runtime.py`
- `tests/test_phase18_gpu_host_qualification.py`
- `tests/test_phase18_colab_first_golden_bootstrap.py`
- `tests/test_phase18_first_golden_review_workflow.py`

## Files added

- `docs/PHASE18_CHANGESET_154_LIVE_FREE_VRAM_QUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_154.md`

## Files deleted

None.

## Regression coverage added/expanded

- CUDA runtime probe records free and used VRAM using driver/PyTorch telemetry.
- Telemetry failure leaves live free VRAM unproven rather than fabricated.
- A 24 GB GPU with only 8 GB currently free is rejected despite sufficient total capacity.
- Missing live free-VRAM evidence fails closed.
- Strict bootstrap stops before cache/model work when live free VRAM is insufficient.
- Host policy must explicitly state that live free VRAM is required.
- Canonical workflow replays both bootstrap-level and host-receipt free-VRAM evidence.
- Human, Golden, publication and Seeds 2–4 authority remain closed.

## Test status

All code, tests, workflow changes, and documentation have been pushed to the Phase 18 branch. GitHub Actions are expected to start automatically for the new HEAD; CI success is not claimed until an actual run completes successfully.

The immediately preceding branch HEAD `0dd694a4746c7d8bba22470443d08ba1c91df33a` is confirmed green via Story Intelligence Verification Run `32880756783 / 2675` and the visible companion workflows on that commit.

## Gates preserved without weakening

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- `$0-local`
- FLUX.2 Klein 4B identity
- native BF16 requirement
- Candidate/request/seed/canvas/SHA locks
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions
- Original Scene runtime admission
- Qwen `BASE_SCENE` and `HYBRID_SURFACE`
- deterministic football geometry
- provenance/evidence replay
- Golden 8.5 minimum / 9.0+ elite
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

## Remaining blocker

The first genuine Golden Hybrid v5 Candidate 1 still requires a real NVIDIA CUDA host that satisfies the existing total-VRAM and native-BF16 policy **and now also proves sufficient live free VRAM at execution time**, while supporting the locked Qwen semantic path.

No PNG, benchmark, or visual success is fabricated when compatible execution hardware is unavailable.

## Remaining path to first genuine Golden Visual

`immutable Phase 18 source → repository integrity → runtime repair → GPU/native-BF16 qualification + live free-VRAM proof → shared cache budget → Qwen readiness → Original Scene admission → FLUX Candidate 1 → provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed human review → explicit human acceptance → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted visually.
