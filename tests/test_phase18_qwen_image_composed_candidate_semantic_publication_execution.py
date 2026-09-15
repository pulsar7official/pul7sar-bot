from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import _evidence, _package, _verifier
from engine.intelligence.semantic_publication_gate import SemanticPublicationGate


class TestPhase18QwenImageComposedCandidateSemanticPublicationExecution(unittest.TestCase):
    def _package_raw(self, *, identity_required=False):
        return {
            "platform": "instagram", "canvas": "1080x1350", "scene_prompt": "clean editorial base scene",
            "negative_constraints": [], "asset_ids": [], "factual_constraints": ["score must remain exact"],
            "layout_boxes": {"headline": {"x": 10, "y": 10, "width": 400, "height": 100}}, "accent_hex": "#FF0000",
            "metadata": {"identity_required": identity_required, "identity_reference_ids": ["ref-1"] if identity_required else []},
        }

    def _evidence_raw(self, *, identity_required=False, identity_matched=True):
        return {
            "provider_id": "qwen-image-2512", "output_ref": "candidate.png", "width": 1080, "height": 1350, "aspect_ratio": "4:5",
            "framing": {"subject_present": True, "fully_visible_as_required": True, "hero_region_clear": True, "confidence": 0.99},
            "identity": {"required": identity_required, "matched": identity_matched, "confidence": 0.99, "reference_ids": ["ref-1"] if identity_required else []},
            "protected_regions": [{"role": "headline", "sufficiently_clear": True, "occupancy_ratio": 0.05}],
            "defects": {"defect_free": True, "defects": []}, "forbidden_visuals_detected": [], "safe_crop_possible": True,
            "provenance": {"request_id": "qwen-cs262-test"},
        }

    def _verifier_raw(self, *, include_identity=False, zero_cost=True):
        capabilities = ["subject_detection", "subject_framing", "semantic_defects", "forbidden_visuals", "protected_region_clutter"]
        if include_identity: capabilities.append("identity_similarity")
        return {"verifier_id": "local-test-verifier", "local_zero_cost": zero_cost, "requires_network": False, "capabilities": capabilities, "notes": []}

    def test_repository_gate_can_allow_complete_zero_cost_non_identity_evidence(self):
        decision = SemanticPublicationGate().evaluate(_package(self._package_raw()), _evidence(self._evidence_raw()), _verifier(self._verifier_raw()))
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.base_scene_accepted)
        self.assertTrue(decision.semantic_verifier_eligible)

    def test_identity_required_needs_identity_capability_and_matching_reference(self):
        decision = SemanticPublicationGate().evaluate(
            _package(self._package_raw(identity_required=True)),
            _evidence(self._evidence_raw(identity_required=True)),
            _verifier(self._verifier_raw(include_identity=False)),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("semantic vision capabilities are incomplete", decision.failures)

    def test_paid_or_nonlocal_verifier_cannot_authorize_publication(self):
        decision = SemanticPublicationGate().evaluate(_package(self._package_raw()), _evidence(self._evidence_raw()), _verifier(self._verifier_raw(zero_cost=False)))
        self.assertFalse(decision.allowed)
        self.assertIn("vision verifier is not proven zero-cost local", decision.failures)

    def test_identity_mismatch_blocks_even_with_complete_identity_capability(self):
        decision = SemanticPublicationGate().evaluate(
            _package(self._package_raw(identity_required=True)),
            _evidence(self._evidence_raw(identity_required=True, identity_matched=False)),
            _verifier(self._verifier_raw(include_identity=True)),
        )
        self.assertFalse(decision.allowed)
        self.assertTrue(any("identity" in item for item in decision.failures))

    def test_unknown_verifier_capability_is_rejected(self):
        raw = self._verifier_raw(); raw["capabilities"].append("invented_capability")
        with self.assertRaisesRegex(ValueError, "VERIFIER_CAPABILITY_INVALID"):
            _verifier(raw)


if __name__ == "__main__":
    unittest.main()
