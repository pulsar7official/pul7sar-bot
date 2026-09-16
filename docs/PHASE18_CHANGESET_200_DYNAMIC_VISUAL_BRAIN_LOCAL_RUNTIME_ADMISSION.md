# Phase 18 Change Set 200 — Dynamic Visual Brain Local Runtime Admission

## Purpose

Change Set 199 connected a locked story-specific Dynamic Visual Brain concept to the provider-neutral Original Scene contract.  Change Set 200 connects that request to the existing measured `$0-local` runtime qualifier and local-backend bridge.

This is an execution-facing bridge, not a publication shortcut.  A local generation request is compiled only when the measured readiness report admits the selected model/runtime.  Semantic inspection, Visual Critic, human Golden review, exact branding/typography, and SemanticPublicationGate remain downstream and mandatory.

## Added

- `engine/intelligence/dynamic_visual_brain_local_admission.py`
  - replays the Dynamic Visual Brain concept lock through Change Set 199;
  - delegates runtime qualification to the existing `OriginalSceneLocalBridge`;
  - requires measured `local_cuda` readiness and `$0-local` economics;
  - verifies the exact selected scene intent is present in the compiled local prompt;
  - rejects platform-name leakage;
  - carries story fingerprint, competition SHA, selected-concept SHA, prompt SHA, and Original Scene request SHA into `LocalBackendGenerationRequest.metadata`;
  - keeps generated branding, exact facts, and exact sport geometry forbidden;
  - keeps semantic inspection and human review mandatory;
  - never grants Golden or publication authority.
- `tests/test_phase18_dynamic_visual_brain_local_admission.py`
  - successful measured local-CUDA admission;
  - unready runtime rejection;
  - CPU runtime rejection;
  - model/backend readiness drift rejection;
  - concept-lock tampering rejection;
  - protected platform-name exclusion.

## Why this materially reduces the gap

The new Dynamic Visual Brain is no longer isolated from the qualified execution architecture.  A story-specific concept can now travel through one fail-closed chain from editorial competition to an exact local backend request while retaining its SHA-bound identity.

The chain is now:

`verified story -> concept competition -> explicit pre-render lock -> provider-neutral OriginalSceneRequest -> measured $0-local runtime admission -> concept-bound LocalBackendGenerationRequest`

A future compatible GPU host can execute that request without changing the editorial concept or inventing a second policy layer.

## Preserved gates

Fact, identity, sentiment/neutrality, zero-cost, model/runtime qualification, exact-layer ownership, semantic inspection, Visual Critic, Golden quality, exact brand/typography, and SemanticPublication gates remain fail-closed.

## Deleted

Nothing.

## Production isolation

`main` and `main.py` are not modified by this change set.
