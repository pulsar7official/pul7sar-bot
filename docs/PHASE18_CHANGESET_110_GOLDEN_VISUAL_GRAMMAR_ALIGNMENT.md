# PUL7SAR Phase 18 — Change Set 110

## Golden Hybrid v5 VisualGrammar Alignment

### Purpose
The provider-agnostic `VisualGrammar` introduced into the normal story-to-generation path in Change Set 109 was not yet exercised by the Golden Hybrid v5 benchmark builder. The benchmark still used a hand-authored stadium/pitch prompt that could over-emphasize a full pitch dependency even though `SceneComplexityPolicy` classifies a football preview as `partial_deterministic` surface context.

Change Set 110 makes the Golden v5 handoff use the same story-level VisualGrammar contract as the general Phase 18 generation path before FLUX.2 Klein is selected.

### Added behavior
- The Golden season-opener editorial plan is now passed through `VisualGrammar().direct(...)`.
- `GenerationPackageCompiler` receives the resulting `VisualGrammarDecision`.
- Golden v5 now records `pul7sar-visual-grammar-v1`, provider-agnostic status, `partial_deterministic` surface visibility and restrained fantasy in the request metadata.
- The generated prompt now explicitly limits the model to restrained partial sport-surface context and tells it not to make a full pitch the visual subject.
- The Golden batch manifest records the VisualGrammar contract and surface visibility and fails if candidates drift across seeds.
- Candidate entries carry their surface-visibility contract for later audit.

### Modified files
- `tools/phase18_build_golden_handoff.py`
- `tools/phase18_build_golden_batch.py`
- `tests/test_phase18_golden_handoff.py`
- `tests/test_phase18_golden_batch.py`

### Deleted
Nothing.

### Safety and quality invariants preserved
- `main` and `main.py` are not modified.
- Fact Lock, identity verification and sentiment/result neutrality are unchanged.
- `$0-local`, FLUX.2 Klein 4B, BF16, seeds and canvas contracts are unchanged.
- Generated football geometry remains forbidden.
- Generated PUL7SAR branding, readable editorial text and exact entity marks remain forbidden.
- Deterministic football geometry remains downstream and receipt-backed.
- Qwen semantic/layer inspection remains required for publication-grade flow.
- Golden quality thresholds remain 8.5 minimum and 9.0+ elite, with hard blockers overriding score.
- SemanticPublicationGate and exact brand/typography integrity remain mandatory.

### Why this reduces the remaining gap
The next genuine Candidate 1 will no longer benchmark an older hand-authored visual assumption while the rest of Phase 18 uses story-specific VisualGrammar. The benchmark now exercises the same provider-agnostic complexity decision that future news stories will use. For this preview story that means stadium atmosphere can remain strong, but the generated image is explicitly prevented from turning a full football pitch into the dominant dependency.

No GPU PNG is claimed by this change set. A compatible CUDA/BF16 host is still required for the genuine visual proof.
