from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_genuine_golden_publication_readiness import (
    PUBLICATION_POLICY,
    PUBLICATION_RECEIPT_FIELDS,
    _require_cs285_authority,
    _require_exact_publication_envelope,
    _require_output_inside_repo,
)


class TestPhase18QwenImageGenuineGoldenPublicationReadiness(unittest.TestCase):
    def _valid_cs285(self):
        return {
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": False,
            "policy": {
                "pixel_mutation_forbidden": True,
                "source_must_be_cs284_allowed_exact_png": True,
                "genuine_golden_creation_does_not_set_publication_ready": True,
            },
        }

    def _valid_final_envelope(self):
        values = {field: None for field in PUBLICATION_RECEIPT_FIELDS}
        values["policy"] = dict(PUBLICATION_POLICY)
        return values

    def test_verified_cs285_authority_is_eligible(self):
        _require_cs285_authority(self._valid_cs285())

    def test_missing_semantic_publication_allowance_is_rejected(self):
        state = self._valid_cs285()
        state["semantic_publication_allowed"] = False
        with self.assertRaisesRegex(ValueError, "semantic_publication_allowed"):
            _require_cs285_authority(state)

    def test_missing_genuine_golden_creation_is_rejected(self):
        state = self._valid_cs285()
        state["genuine_golden_png_created"] = False
        with self.assertRaisesRegex(ValueError, "genuine_golden_png_created"):
            _require_cs285_authority(state)

    def test_lost_byte_identity_is_rejected(self):
        state = self._valid_cs285()
        state["byte_identity_preserved"] = False
        with self.assertRaisesRegex(ValueError, "byte_identity_preserved"):
            _require_cs285_authority(state)

    def test_premature_publication_ready_is_rejected(self):
        state = self._valid_cs285()
        state["publication_ready"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_PUBLICATION_STATE"):
            _require_cs285_authority(state)

    def test_cs285_pixel_mutation_policy_cannot_be_weakened(self):
        state = self._valid_cs285()
        state["policy"]["pixel_mutation_forbidden"] = False
        with self.assertRaisesRegex(ValueError, "pixel_mutation_forbidden"):
            _require_cs285_authority(state)

    def test_final_publication_envelope_is_closed_world(self):
        envelope = self._valid_final_envelope()
        _require_exact_publication_envelope(envelope)

        envelope["publish_side_effect_authorized"] = True
        with self.assertRaisesRegex(ValueError, "ENVELOPE_FIELDS_INVALID"):
            _require_exact_publication_envelope(envelope)

    def test_final_publication_envelope_rejects_missing_canonical_field(self):
        envelope = self._valid_final_envelope()
        envelope.pop("generation_context")
        with self.assertRaisesRegex(ValueError, "ENVELOPE_FIELDS_INVALID"):
            _require_exact_publication_envelope(envelope)

    def test_final_publication_policy_rejects_unknown_authority_key(self):
        envelope = self._valid_final_envelope()
        envelope["policy"]["network_publish_allowed"] = True
        with self.assertRaisesRegex(ValueError, "POLICY_INVALID"):
            _require_exact_publication_envelope(envelope)

    def test_final_publication_policy_rejects_weakened_canonical_value(self):
        envelope = self._valid_final_envelope()
        envelope["policy"]["pixel_mutation_forbidden"] = False
        with self.assertRaisesRegex(ValueError, "POLICY_INVALID"):
            _require_exact_publication_envelope(envelope)

    def test_output_must_remain_inside_repository(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            repo = Path(repo_tmp)
            inside = repo / "artifacts" / "cs286"
            _require_output_inside_repo(repo, inside)
            with self.assertRaisesRegex(ValueError, "OUTPUT_OUTSIDE_REPOSITORY"):
                _require_output_inside_repo(repo, Path(outside_tmp) / "cs286")


if __name__ == "__main__":
    unittest.main()
