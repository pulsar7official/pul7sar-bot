"""Canonical production registry for Change Set 238 gate replay verifiers.

Only genuine production-backed replay adapters may be registered here. Test fixtures,
lambdas, pass-through stubs, and receipt-echo functions are forbidden.

Change Set 244 registers the first genuine adapter: ``zero_cost_policy``. The other
five required gates intentionally remain absent until equivalent production-backed
semantic verifiers exist. Change Set 239/241 therefore continues to report the
registry as NOT READY and generation authority remains closed.
"""
from __future__ import annotations

from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import GateReplayVerifier
from engine.intelligence.qwen_image_zero_cost_policy_gate_verifier import (
    replay_zero_cost_policy_gate,
)

# Partial by design. Readiness must remain false until every required gate is bound.
GATE_REPLAY_VERIFIERS: dict[str, GateReplayVerifier] = {
    "zero_cost_policy": replay_zero_cost_policy_gate,
}
