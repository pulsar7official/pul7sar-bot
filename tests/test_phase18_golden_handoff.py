import unittest

from tools.phase18_build_golden_handoff import build_request


class GoldenVisualHandoffTests(unittest.TestCase):
    def test_golden_request_uses_real_phase18_layout_and_zero_cost_model(self):
        request = build_request(seed=7007001, request_id="golden-test")
        self.assertEqual(request.provider_id, "local-flux2-klein-4b")
        self.assertEqual(request.model_id, "black-forest-labs/FLUX.2-klein-4B")
        self.assertEqual(request.backend, "diffusers")
        self.assertEqual(request.metadata["cost_mode"], "$0-local")
        self.assertTrue(request.metadata["portable_handoff"])
        self.assertEqual(request.seed, 7007001)
        self.assertIn("European football season opener", request.prompt)
        self.assertIn("Do not render PUL7SAR branding", request.prompt)
        self.assertIn("outcome completely unresolved", request.prompt)

    def test_golden_request_is_deterministic_for_same_seed(self):
        first = build_request(seed=42, request_id="same")
        second = build_request(seed=42, request_id="same")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
