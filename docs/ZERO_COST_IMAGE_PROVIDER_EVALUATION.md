# PUL7SAR — Zero-Cost Image Provider Evaluation

## Current development rule

Phase 18 development must not incur per-image or subscription cost.
Paid providers may be modeled for future extensibility but remain disabled by the active zero-cost policy.

Quality thresholds do not change because a provider is free.
If no zero-cost provider can satisfy PUL7SAR quality requirements, the system must return `NO_ACCEPTABLE_SCENE` rather than publish degraded output.

## First local evaluation candidate

### FLUX.2 [klein] 4B

Model ID:
`black-forest-labs/FLUX.2-klein-4B`

Declared evaluation properties from official Black Forest Labs material reviewed on 2026-08-22:
- Apache-2.0 license for the 4B model.
- Text-to-image generation.
- Image editing and multi-reference support.
- Designed to run locally on consumer GPU hardware.
- Approximately 13 GB VRAM stated by the model card for consumer-hardware use.
- FLUX prompting does not use native negative prompts; unwanted concepts should be expressed as positive desired constraints.

This makes the 4B model suitable for a first zero-cost local evaluation, not an automatic production approval.

## PUL7SAR integration rule

The local model is responsible only for the original base scene.
It is not trusted to render:
- PUL7SAR wordmark
- PUL7SAR 7/pulse
- club/team crests
- competition marks
- social icons
- score typography
- final headline/footer

Those remain deterministic post-composition responsibilities.

## Negative/forbidden constraints

Because the selected FLUX candidate does not natively support negative prompts, PUL7SAR uses `PromptConstraintCompiler`.

Known editorial constraints are deterministically converted into positive desired scene instructions.
If a constraint cannot be translated exactly, the provider is not allowed to execute that package. Constraints are never silently dropped.

Examples:
- `no humiliation` -> respectful treatment of every losing/secondary side while emphasis stays on the winner.
- `no unverified signing` -> unresolved negotiation/interest context only.
- `no invented result` -> pre-event anticipation with no implied outcome.

## Runtime status

This document does not claim the model is installed on the user's current machine.
The codebase currently contains the evaluation profile and prompting policy only.

Before real local generation we still need:
1. runtime hardware capability detection,
2. optional Diffusers/ComfyUI local backend,
3. local file/output management,
4. visual-evidence probe for identity/framing/defects/protected regions,
5. end-to-end generation session through the existing quality gates.

## Official references reviewed

- Black Forest Labs FLUX.2 official GitHub repository.
- Black Forest Labs FLUX.2 [klein] 4B Hugging Face model card.
- Black Forest Labs official FLUX prompting/best-practices material.

No paid API endpoint is selected by this decision.
