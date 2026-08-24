import unittest
from pathlib import Path


class Phase18GpuSmokeHybridHandoffTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(".github/workflows/phase18-gpu-smoke.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_provenance_handoff_precedes_evidence_sealing(self):
        self.assertIn("tools/phase18_build_first_png_hybrid_handoff.py", self.text)
        self.assertIn("FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY", self.text)
        self.assertIn("output/phase18_colab/latest.json", self.text)
        generation = self.text.index("python tools/phase18_first_png.py")
        postflight = self.text.index("python tools/phase18_verify_first_png_provenance.py")
        handoff = self.text.index("python tools/phase18_build_first_png_hybrid_handoff.py")
        evidence = self.text.index("python tools/phase18_build_gpu_evidence_manifest.py")
        self.assertLess(generation, postflight)
        self.assertLess(postflight, handoff)
        self.assertLess(handoff, evidence)

    def test_handoff_keeps_semantic_golden_and_publication_gates_closed(self):
        self.assertIn('handoff.get("manifest_version") != "pul7sar-golden-batch-v5"', self.text)
        self.assertIn('handoff.get("resolved_dtype") != "bfloat16"', self.text)
        self.assertIn('handoff.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('handoff.get("hybrid_surface_replacement_required") is not True', self.text)
        self.assertIn('for field in ("semantic_layer_gate_approved", "hybrid_semantic_review_approved", "golden_quality_approved", "publication_ready")', self.text)

    def test_handoff_is_sealed_into_gpu_evidence(self):
        self.assertIn("--include output/phase18_gpu_smoke/first-png-hybrid-handoff.json", self.text)
        self.assertIn("output/phase18_colab/**", self.text)


if __name__ == "__main__":
    unittest.main()
