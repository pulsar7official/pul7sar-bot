# PUL7SAR Phase 18 — Change Set 104
## Final Composer Football Integrity Alignment

### Purpose
Close a stale contract in `FinalHybridComposer` before the first new Golden Visual reaches deterministic brand/typography composition.

The final compositor still carried the legacy engineering-proof assumption that a valid football surface had `surface_opacity == 255`. Change Sets 095–097 intentionally replaced that opaque tactical-board surface with texture-preserving, feathered football composition. Leaving the old assertion in the final compositor would make a correct modern Golden artifact fail later, after visual review.

A second problem was more serious: when football geometry was not composed inside `FinalHybridComposer`, the returned receipt reported `deterministic_geometry_applied=true` anyway. That could overstate evidence and weaken publication-readiness reasoning.

### Modified
- `engine/intelligence/final_hybrid_composer.py`
  - removed the hard-coded `surface_opacity == 255` legacy assertion;
  - validates every football receipt through `HybridArtifactIntegrityGate`, which enforces the current texture-preserving composition mode, safe opacity, inward feather, SHA replay and deterministic-marking authority;
  - adds optional `precomposed_football_receipt` support for a previously composed football artifact;
  - requires the precomposed receipt output SHA to match the exact base bytes supplied to the final compositor;
  - makes new composition and precomposed evidence mutually exclusive;
  - reports `deterministic_geometry_applied=false` when no verified football receipt exists instead of silently claiming success.
- `tests/test_phase18_final_hybrid_composer.py`
  - proves the current low-opacity texture-preserving football receipt is accepted;
  - proves missing football evidence is never reported as deterministic geometry;
  - proves a precomposed football receipt must match the exact final-composer base bytes;
  - proves precomposed and newly rendered football geometry cannot be combined in one call;
  - preserves existing missing-base and approved-brand recipe protections.

### Added
- This Change Set document.
- `docs/PHASE18_IMPLEMENTATION_LOG_104.md` as the authoritative continuation record.

### Deleted
- Nothing.

### Safety / quality invariants preserved
- `main` and `main.py` are not modified.
- Fact Lock, identity verification, sentiment/neutrality and story integrity are unchanged.
- `$0-local`, FLUX.2 Klein 4B, BF16, seeds and canvas locks are unchanged.
- Semantic layer ownership and SemanticPublicationGate remain mandatory.
- Golden quality remains 8.5 minimum / 9.0+ elite with hard blockers overriding score.
- Generated PUL7SAR branding remains forbidden.
- Exact approved brand and typography integrity remain downstream requirements.
- This Change Set does not generate or fabricate a GPU PNG.

### Why this materially reduces the remaining gap
A future Candidate 1 that successfully survives pitch selection, semantic review and Golden review must later enter exact brand/typography composition. Before Change Set 104 that path would reject the modern texture-preserving pitch because it expected the obsolete opaque surface, while also being capable of falsely claiming geometry when none was proven. The final composition boundary now consumes the same football integrity contract used by the current Hybrid v5 pipeline.
