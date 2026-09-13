import tempfile
import unittest

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_visual_brain_batch import build_batch


class VisualBrainBatchTests(unittest.TestCase):
    def test_batch_varies_concepts_not_only_seeds(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = build_batch(directory)
            self.assertEqual(manifest["candidate_strategy"], "concept_competition_not_seed_only")
            self.assertTrue(manifest["critic_required_before_acceptance"])
            self.assertFalse(manifest["publication_ready"])
            candidates = manifest["candidates"]
            self.assertEqual(len(candidates), 4)
            self.assertEqual(len({item["concept_id"] for item in candidates}), 4)
            self.assertEqual(len({item["focal_strategy"] for item in candidates}), 4)
            prompts = []
            for item in candidates:
                request = LocalGenerationHandoff.read(f"{directory}/{item['handoff']}")
                prompts.append(request.prompt)
                self.assertEqual(request.metadata["visual_brain_contract"], "pul7sar-visual-brain-v1")
                self.assertTrue(request.metadata["concept_competition"])
                self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
                self.assertFalse(request.metadata["publication_ready"])
                self.assertNotIn("pul7sar", request.prompt.casefold())
                self.assertNotIn("pulsar", request.prompt.casefold())
            self.assertEqual(len(set(prompts)), 4)


if __name__ == "__main__":
    unittest.main()
