# PUL7SAR Phase 18 — Change Set 099

## Colab non-destructive pitch review flow

### Purpose
Change Set 098 made it possible to render all approved deterministic football camera presets over one existing FLUX base PNG. Change Set 099 closes the remaining operational gap for Colab: the reviewer can now consume the existing `output/phase18_colab/latest.json`, display the genuine base image first, display every approved pitch diagnostic variant, and optionally record an explicit human-selected preset without invoking FLUX again.

This is a review-only path. It never marks any image publication-ready and never weakens semantic, factual, identity, sentiment, Golden-quality, branding, typography, or publication-readiness gates.

### Added
- `tools/phase18_colab_pitch_review.py`
  - Requires the active branch and stored summary to both identify `phase18/story-intelligence`.
  - Requires `pul7sar-golden-batch-v5`, `hybrid_surface_replacement_required=true`, `publication_ready=false`, the requested candidate number, and a real existing `.png` path.
  - Reuses `FootballPitchDiagnosticBuilder`; it does not invoke FLUX or Qwen.
  - Displays the genuine base PNG first, then every approved `FootballCameraPreset` variant.
  - Does not auto-select a preset.
  - Optional `--selected-preset` records an explicit human review choice only; it remains `publication_ready=false`.
  - Writes `colab-pitch-review.json` beside the diagnostic matrix for auditability.
- `tests/test_phase18_colab_pitch_review.py`
  - Proves there is no automatic preset selection.
  - Proves all approved presets are surfaced for review.
  - Proves an explicit selection stays review-only and non-publication.
  - Rejects stale Golden contracts, publication-ready source summaries, candidate mismatch, and execution from the wrong branch.

### Modified
- `docs/PHASE18_IMPLEMENTATION_LOG_098.md` is extended to record Change Set 099 and the current branch state.

### Deleted
- Nothing.

### Why this materially reduces the gap to the next genuine Golden PNG
The next CUDA/BF16 run should generate Candidate 1 only. Once that base exists, pitch-placement evaluation no longer requires another seed or another FLUX inference. One CPU-only Colab command can expose the exact base and every deterministic camera preset side by side, preserving the same base pixels. This isolates placement/integration from generative quality and avoids wasting GPU time while the correct camera mapping is still under review.

### Review command after Candidate 1 exists
```bash
PYTHONPATH=. python tools/phase18_colab_pitch_review.py --candidate 1
```

After reviewing the displayed variants, an explicit review choice can be recorded without changing publication status:

```bash
PYTHONPATH=. python tools/phase18_colab_pitch_review.py \
  --candidate 1 \
  --selected-preset sideline_oblique
```

No preset selection in this tool is publication approval.

### Invariants preserved
- `main` and `main.py` untouched.
- Fact Lock unchanged.
- Identity verification unchanged.
- Sentiment and neutrality unchanged.
- `$0-local` unchanged.
- FLUX.2 Klein 4B, BF16, seeds and canvases unchanged.
- Base semantic layer-ownership gate unchanged.
- SemanticPublicationGate unchanged.
- Golden thresholds unchanged at 8.5 minimum / 9.0+ elite with hard blockers overriding score.
- Generated PUL7SAR branding remains forbidden.
- Exact official PUL7SAR logo SHA remains unresolved; final publication composition remains blocked.
- No paid provider, secret, model weights, font files, fake PNG, or fabricated benchmark added.
