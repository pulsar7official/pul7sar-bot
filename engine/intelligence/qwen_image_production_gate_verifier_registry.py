"""Canonical production registry for Change Set 238 gate replay verifiers.

This registry is intentionally empty until real, production-backed replay adapters are
implemented for every required fresh-story gate. Test fixtures, lambdas, pass-through
stubs, and receipt-echo functions must never be registered here.

Keeping the missing wiring explicit is safer than silently substituting synthetic
verifiers: Change Set 239 audits this registry and fails closed until all six gates are
bound to callable production adapters with stable verifier identity/version metadata.
"""
from __future__ import annotations

from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import GateReplayVerifier

# Do not populate this mapping with test fixtures or receipt-echo placeholders.
# Required gates are defined by REQUIRED_FRESH_GATE_EVIDENCE in the controlled
# Golden-trial preflight contract.
GATE_REPLAY_VERIFIERS: dict[str, GateReplayVerifier] = {}
