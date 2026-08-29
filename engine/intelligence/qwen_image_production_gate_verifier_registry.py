"""Canonical production registry for Change Set 238 gate replay verifiers.

Only genuine production-backed replay adapters may be registered here. Test fixtures,
lambdas, pass-through stubs, and receipt-echo functions are forbidden.

Change Sets 244-246 implement genuine production adapters for ``zero_cost_policy``,
``fact_lock``, and ``sentiment_neutrality``. The canonical registry remains empty until
all six required gates have genuine adapters so the cutover is atomic and Change Set
239/241 continues to report the pre-cutover state as explicitly NOT READY. This avoids
a partial registry being mistaken for an executable production replay set.
"""
from __future__ import annotations

from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import GateReplayVerifier

# Atomic cutover policy: populate only when every REQUIRED_FRESH_GATE_EVIDENCE gate has
# a genuine production-backed adapter. Three required gates remain after Change Set 246:
# entity_identity_verification, story_semantic_preflight, semantic_layer_ownership.
GATE_REPLAY_VERIFIERS: dict[str, GateReplayVerifier] = {}
