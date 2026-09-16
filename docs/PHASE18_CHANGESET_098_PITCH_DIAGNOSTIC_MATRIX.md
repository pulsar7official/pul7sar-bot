# PUL7SAR Phase 18 — Change Set 098: Pitch Diagnostic Matrix

## Scope
Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Pre-change comparison with `main`: `diverged`, 731 commits ahead and 72 behind. `main` was not modified, merged, or force-updated.

## Why this change exists
The latest Hybrid v5 compositor already preserves photographic turf, disables synthetic mowing stripes by default, feathers the low-opacity turf normalization inward, and keeps exact football markings deterministic. The remaining visual uncertainty is placement: a fixed camera preset may not match the real pitch footprint in a generated base image.

Generating another FLUX seed just to compare pitch placement wastes GPU time and can hide whether the failure came from generation or composition. Change Set 098 therefore reuses one genuine FLUX base PNG and renders every approved deterministic camera preset as a separate non-publication diagnostic artifact.

## Added
- `engine/intelligence/football_pitch_diagnostics.py`
  - Builds one diagnostic PNG per `FootballCameraPreset`.
  - Reuses the current `FootballHybridComposer`; no alternate or weaker geometry path exists.
  - Replays `HybridArtifactIntegrityGate` for every variant.
  - SHA-256 checks the source before and after and fails if the base image changes.
  - Emits a JSON manifest with `diagnostic_only=true`, `publication_ready=false`, and `candidate_pixels_untouched=true`.
- `tools/phase18_build_pitch_diagnostics.py`
  - CLI for building the diagnostic matrix from an existing PNG without any GPU inference.
  - Default output directory: `output/phase18_visual_proof/pitch-diagnostics`.
- `tests/test_phase18_football_pitch_diagnostics.py`
  - Proves one variant is produced for every approved camera preset.
  - Proves the base file bytes are unchanged.
  - Proves every diagnostic variant passes the current football artifact-integrity gate.
  - Proves diagnostics can never claim publication readiness.

## Modified
- No production runtime module was modified in this change set.
- A new implementation-log continuation records Change Set 098.

## Deleted
Nothing.

## Gates and invariants unchanged
- `main` / `main.py`: untouched.
- Fact Lock: unchanged and fail-closed.
- Identity verification: unchanged and fail-closed.
- Sentiment / neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B, BF16, seeds/canvases and generation controls: unchanged.
- Base semantic layer-ownership gate remains mandatory for the quality path.
- SemanticPublicationGate remains mandatory for publication.
- Golden quality thresholds remain 8.5 minimum / 9.0+ elite; hard blockers override score.
- Generated PUL7SAR branding remains forbidden.
- Exact PUL7SAR logo bytes/checksum remain unresolved; final publication composition stays blocked.
- No paid provider, secret, model weights, font files, fake PNG, or fabricated benchmark was added.

## Intended use
After Candidate 1 produces a genuine FLUX base PNG on CUDA/BF16, run the diagnostic tool against that exact base before generating seeds 2–4. Visually compare `high_wide_central`, `elevated_endline`, and `sideline_oblique` using identical base pixels. This isolates camera-placement quality from generative quality and lets the next adjustment be evidence-based.

Example:

```bash
PYTHONPATH=. python tools/phase18_build_pitch_diagnostics.py \
  --base output/phase18_colab/<real-base>.png
```

These artifacts are engineering diagnostics only. They do not satisfy semantic, identity, Golden-quality, branding, typography, or publication gates.

## Remaining work
1. Confirm CPU CI on the Change Set 098 head.
2. On a compatible CUDA/BF16 host, generate Candidate 1 only under the current Hybrid v5 path.
3. If the base passes semantic layer ownership, build the pitch diagnostic matrix from the genuine base PNG before spending GPU on any additional seed.
4. Select or refine placement only from visual evidence; do not weaken factual, identity, semantic-publication, or Golden-quality gates.
5. Resolve and SHA-lock the approved PUL7SAR logo asset before final publication composition.
