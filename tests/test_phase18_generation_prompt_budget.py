import pytest

from engine.intelligence.generation_prompt_budget import GenerationPromptBudget


class FakeTokenizer:
    model_max_length = 10

    def __call__(self, prompt, add_special_tokens=True, truncation=False):
        count = len(prompt.split()) + (2 if add_special_tokens else 0)
        return {"input_ids": list(range(count))}


def test_prompt_within_budget_passes():
    e = GenerationPromptBudget.require_fit(FakeTokenizer(), "one two three four", reserve_tokens=2)
    assert e.token_count == 6
    assert e.usable_limit == 8
    assert e.fits


def test_prompt_that_would_be_truncated_fails_closed():
    with pytest.raises(ValueError, match="GENERATION_PROMPT_EXCEEDS_TOKEN_BUDGET"):
        GenerationPromptBudget.require_fit(FakeTokenizer(), "one two three four five six seven", reserve_tokens=2)


def test_unusable_tokenizer_capacity_is_rejected():
    class BadTokenizer(FakeTokenizer):
        model_max_length = 10**30

    with pytest.raises(ValueError, match="TOKENIZER_MODEL_MAX_LENGTH_UNUSABLE"):
        GenerationPromptBudget.inspect(BadTokenizer(), "scene")
