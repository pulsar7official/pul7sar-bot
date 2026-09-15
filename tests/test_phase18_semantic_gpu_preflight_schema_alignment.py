import unittest
from pathlib import Path


EXPECTED_SCHEMA = "pul7sar-phase18-semantic-gpu-preflight-v2"
STALE_SCHEMA = "pul7sar-phase18-semantic-gpu-preflight-v1"


class Phase18SemanticGpuPreflightSchemaAlignmentTests(unittest.TestCase):
    def test_producer_orchestrator_and_gpu_workflow_share_v2_contract(self):
        producer = Path("tools/phase18_preflight_semantic_gpu.py").read_text(encoding="utf-8")
        orchestrator = Path("tools/phase18_first_png.py").read_text(encoding="utf-8")
        workflow = Path(".github/workflows/phase18-gpu-smoke.yml").read_text(encoding="utf-8")

        self.assertIn(EXPECTED_SCHEMA, producer)
        self.assertIn(EXPECTED_SCHEMA, orchestrator)
        self.assertIn(EXPECTED_SCHEMA, workflow)
        self.assertNotIn(STALE_SCHEMA, workflow)

    def test_alignment_does_not_relax_zero_cost_or_publication_gates(self):
        workflow = Path(".github/workflows/phase18-gpu-smoke.yml").read_text(encoding="utf-8")

        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", workflow)
        self.assertIn(
            'for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready"):',
            workflow,
        )
        self.assertIn("if payload.get(field) is not False:", workflow)
        self.assertIn(
            "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
