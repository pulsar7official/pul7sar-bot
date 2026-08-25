"""Fail-closed token budget for image-generation prompts.

Short-context text encoders such as SD-Turbo CLIP silently truncate long prompts.
PUL7SAR must never treat a syntactically complete prompt as semantically complete
unless the active tokenizer proves every token fits.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptBudgetEvidence:
    token_count: int
    model_max_length: int
    reserve_tokens: int
    usable_limit: int
    fits: bool
    contract: str = "pul7sar-generation-prompt-budget-v1"


class GenerationPromptBudget:
    CONTRACT = "pul7sar-generation-prompt-budget-v1"

    @staticmethod
    def inspect(tokenizer, prompt: str, *, reserve_tokens: int = 2) -> PromptBudgetEvidence:
        if not prompt or not prompt.strip():
            raise ValueError("prompt is required")
        max_len = int(getattr(tokenizer, "model_max_length", 0) or 0)
        if max_len <= 0 or max_len > 100_000:
            raise ValueError("TOKENIZER_MODEL_MAX_LENGTH_UNUSABLE")
        if reserve_tokens < 0 or reserve_tokens >= max_len:
            raise ValueError("INVALID_PROMPT_TOKEN_RESERVE")
        encoded = tokenizer(prompt, add_special_tokens=True, truncation=False)
        ids = encoded["input_ids"] if isinstance(encoded, dict) else encoded.input_ids
        if ids and isinstance(ids[0], (list, tuple)):
            ids = ids[0]
        count = len(ids)
        usable = max_len - reserve_tokens
        return PromptBudgetEvidence(count, max_len, reserve_tokens, usable, count <= usable)

    @classmethod
    def require_fit(cls, tokenizer, prompt: str, *, reserve_tokens: int = 2) -> PromptBudgetEvidence:
        evidence = cls.inspect(tokenizer, prompt, reserve_tokens=reserve_tokens)
        if not evidence.fits:
            raise ValueError(
                f"GENERATION_PROMPT_EXCEEDS_TOKEN_BUDGET:{evidence.token_count}>{evidence.usable_limit}"
            )
        return evidence
