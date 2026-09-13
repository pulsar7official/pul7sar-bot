import unittest

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendSnapshot
from engine.intelligence.local_readiness_service import LocalReadinessService
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalReadinessServiceTests(unittest.TestCase):
    def test_generation_can_be_ready_while_publication_remains_blocked(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CUDA, True, "GPU", 16.0, True)
        backend = LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, True, version="test")
        vision = LocalVisionCapabilityReport(True, True, False, False, False, False)
        bundle = LocalReadinessService().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            backend=backend,
            runtime=runtime,
            vision=vision,
        )
        self.assertTrue(bundle.generation_ready)
        self.assertFalse(bundle.publication_ready)
        self.assertEqual(bundle.as_dict()["cost_mode"], "$0-local")

    def test_publication_ready_requires_all_vision_capabilities(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CUDA, True, "GPU", 16.0, True)
        backend = LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, True, version="test")
        vision = LocalVisionCapabilityReport(True, True, True, True, True, True)
        bundle = LocalReadinessService().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            backend=backend,
            runtime=runtime,
            vision=vision,
        )
        self.assertTrue(bundle.generation_ready)
        self.assertTrue(bundle.publication_ready)

    def test_generation_blockers_remain_visible(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CPU, False, None, None, False)
        backend = LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, False)
        vision = LocalVisionCapabilityReport(True, False, False, False, False, False)
        bundle = LocalReadinessService().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            backend=backend,
            runtime=runtime,
            vision=vision,
        )
        self.assertFalse(bundle.generation_ready)
        self.assertFalse(bundle.publication_ready)
        self.assertGreaterEqual(len(bundle.generation.blockers), 2)


if __name__ == "__main__":
    unittest.main()
