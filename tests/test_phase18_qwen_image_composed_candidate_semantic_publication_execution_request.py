from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    _POLICY_SOURCES,
    _assert_cs282,
)
from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import SCHEMA as CS282_SCHEMA


class TestPhase18QwenImageComposedCandidateSemanticPublicationExecutionRequest(unittest.TestCase):
    def _cs282(self):
        return {
            "schema": CS282_SCHEMA,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_cs282_approved_state_can_request_publication_gate_execution(self):
        _assert_cs282(self._cs282())

    def test_composed_visual_failure_blocks_request(self):
        value = self._cs282(); value["composed_visual_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS282_GATE_MISSING:composed_visual_approved"):
            _assert_cs282(value)

    def test_semantic_failure_blocks_request(self):
        value = self._cs282(); value["semantic_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS282_GATE_MISSING:semantic_approved"):
            _assert_cs282(value)

    def test_premature_genuine_golden_authority_is_rejected(self):
        value = self._cs282(); value["genuine_golden_png_created"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:genuine_golden_png_created"):
            _assert_cs282(value)

    def test_premature_publication_authority_is_rejected(self):
        value = self._cs282(); value["publication_ready"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:publication_ready"):
            _assert_cs282(value)

    def test_request_binds_all_semantic_publication_policy_sources(self):
        self.assertEqual(
            set(_POLICY_SOURCES),
            {
                "engine/intelligence/semantic_publication_gate.py",
                "engine/intelligence/base_scene_quality.py",
                "engine/intelligence/vision_verification_policy.py",
                "engine/intelligence/generation_package.py",
            },
        )


if __name__ == "__main__":
    unittest.main()
