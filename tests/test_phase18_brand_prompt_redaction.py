import unittest

from engine.intelligence.provider_prompting import PromptConstraintCompiler
from tools.phase18_build_golden_handoff import build_request


class BrandPromptRedactionTests(unittest.TestCase):
    def test_current_golden_handoff_contains_no_protected_brand_token(self):
        request = build_request(seed=7007001, request_id="redaction-check")
        prompt = request.prompt.casefold()
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)
        self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])
        self.assertFalse(request.metadata["generated_branding_allowed"])

    def test_hybrid_positive_reframes_also_contain_no_protected_brand_token(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no football pitch markings in the reserved surface plane",
                "no centre circle, halfway line, penalty boxes, goal-area markings or painted touchlines",
                "no generated branding, wordmarks, readable text, numerals or pseudo-text",
            ),
            supports_native_negative=False,
        )
        self.assertTrue(compiled.complete)
        text = " ".join(compiled.positive_instructions).casefold()
        self.assertNotIn("pul7sar", text)
        self.assertNotIn("pulsar", text)
        self.assertIn("deterministic geometry", text)
        self.assertIn("clean unbranded photographic base scene", text)

    def test_redaction_is_not_a_branding_omission_in_final_architecture(self):
        request = build_request(seed=7007001, request_id="redaction-contract")
        # Brand is absent only from diffusion. The portable request attests that
        # generated branding is forbidden and final brand belongs downstream.
        self.assertFalse(request.metadata["generated_branding_allowed"])
        self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])


if __name__ == "__main__":
    unittest.main()
