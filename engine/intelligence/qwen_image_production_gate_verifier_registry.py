"""Canonical production registry for Change Set 238 gate replay verifiers.

Only genuine production-backed replay adapters may be registered here. Test fixtures,
lambdas, pass-through stubs, and receipt-echo functions are forbidden.

Change Set 244 implements the first genuine production adapter for ``zero_cost_policy``
in ``qwen_image_zero_cost_policy_gate_verifier.py``. The canonical registry remains
empty until all six required gates have genuine adapters so the cutover is atomic and
Change Set 239/241 continues to report the pre-cutover state as explicitly NOT READY.
This avoids a partial registry being mistaken for an executable production replay set.
"""
from __future__ import annotations

from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import GateReplayVerifier

# Atomic cutover policy: populate only when every REQUIRED_FRESH_GATE_EVIDENCE gate has
# a genuine production-backed adapter. Change Set 244 has qualified zero_cost_policy,
# but five required gates still remain.
GATE_REPLAY_VERIFIERS: dict[str, GateReplayVerifier] = {}
