# PUL7SAR Phase 18 — Change Set 090: Base-Scene Execution Gate

## Purpose
Close the remaining runtime gap between semantic layer inspection and deterministic hybrid composition. Before this change, the one-command Colab path could record an unavailable/failed base-scene semantic inspection and still continue into `FootballHybridComposer`. Change Set 090 makes that transition fail closed.

## Added
- `engine/intelligence/base_scene_execution_gate.py`
  - Combines `SemanticLayerEvidenceAdapter` inspection completeness with `HybridLayerQualityGate` ownership enforcement.
  - Missing or low-confidence required checks block execution.
  - Detected generated text, platform branding, exact editorial numbers, entity marks, unverified identity, or model-owned sport geometry block according to the active `HybridLayerPlan`.
- `tests/test_phase18_base_scene_execution_gate.py`
  - Clean complete evidence allows composition.
  - Missing required sport-geometry inspection blocks.
  - Generated sport geometry blocks deterministic-geometry ownership.
  - Generated platform branding blocks verified-brand ownership.

## Modified
- `tools/phase18_colab_one_command.py`
  - Qwen semantic inspection is now mandatory for the non-prepare Golden Hybrid v5 composition path.
  - Qwen runtime readiness failure blocks before composition.
  - Base-scene semantic inspection failure blocks before composition.
  - The new execution gate runs after the semantic verdict and before `FootballHybridComposer`.
  - A base scene that fails semantic safety or layer ownership does not receive the deterministic football surface.
  - Receipt output now carries `base_scene_layer_gate` evidence and blockers.
  - Hybrid-surface verification no longer requires `generated_sport_geometry_absent`, because the deterministic renderer owns that geometry at the hybrid stage; perspective/alignment verification remains required there.

## Deleted
None.

## Safety invariants preserved
- Branch scope remains `phase18/story-intelligence` only; `main` and `main.py` are not modified.
- No paid provider or paid API is introduced.
- FLUX.2 Klein model, BF16 lock, seed/canvas locks, and `$0-local` policy are unchanged.
- Fact, identity, sentiment, neutrality, semantic-publication, exact-brand integrity, and Golden quality gates are unchanged.
- Identity remains a separate verification concern; this gate does not claim identity similarity.
- `publication_ready` remains false after generation/hybrid composition.

## Remaining blocker
A genuine Candidate 1 under this stricter path still needs a compatible CUDA/BF16 execution host with the local Qwen semantic inspector ready. No new PNG or visual-quality claim is made by this change set.
