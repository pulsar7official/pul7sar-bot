"""Canonical production registry for Change Set 238 gate replay verifiers.

Only genuine production-backed replay adapters may be registered here. Test fixtures,
lambdas, pass-through stubs, and receipt-echo functions are forbidden.

Change Sets 244-249 implement and CI-validate genuine production adapters for all six
required fresh-story gates. Change Set 250 performs the atomic registry cutover in the
exact `REQUIRED_FRESH_GATE_EVIDENCE` order. Registry readiness still grants no semantic
replay result, generation authority, Golden approval, human approval, or publication
authority; those remain independent downstream gates.
"""
from __future__ import annotations

from engine.intelligence.qwen_image_entity_identity_gate_verifier import (
    replay_entity_identity_gate,
)
from engine.intelligence.qwen_image_fact_lock_gate_verifier import replay_fact_lock_gate
from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import GateReplayVerifier
from engine.intelligence.qwen_image_semantic_layer_ownership_gate_verifier import (
    replay_semantic_layer_ownership_gate,
)
from engine.intelligence.qwen_image_sentiment_neutrality_gate_verifier import (
    replay_sentiment_neutrality_gate,
)
from engine.intelligence.qwen_image_story_semantic_preflight_gate_verifier import (
    replay_story_semantic_preflight_gate,
)
from engine.intelligence.qwen_image_zero_cost_policy_gate_verifier import (
    replay_zero_cost_policy_gate,
)


# Atomic six-gate cutover. Keep this order identical to REQUIRED_FRESH_GATE_EVIDENCE.
GATE_REPLAY_VERIFIERS: dict[str, GateReplayVerifier] = {
    "fact_lock": replay_fact_lock_gate,
    "entity_identity_verification": replay_entity_identity_gate,
    "sentiment_neutrality": replay_sentiment_neutrality_gate,
    "story_semantic_preflight": replay_story_semantic_preflight_gate,
    "zero_cost_policy": replay_zero_cost_policy_gate,
    "semantic_layer_ownership": replay_semantic_layer_ownership_gate,
}
