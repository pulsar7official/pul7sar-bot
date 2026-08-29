from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_semantic_layer_ownership_gate_verifier import (
    VERIFIER_ID,
    VERIFIER_VERSION,
    replay_semantic_layer_ownership_gate,
    verify_semantic_layer_ownership_evidence,
)
from engine.intelligence.semantic_layer_ownership import (
    SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA,
    evaluate_semantic_layer_ownership,
)


class SemanticLayerOwnershipGateVerifierTests(unittest.TestCase):
    STORY_SHA = "e" * 64

    def _receipt(self) -> dict:
        return {"verifier_id": VERIFIER_ID, "verifier_version": VERIFIER_VERSION}

    def _layers(self, *, identity: bool = True, exact_geometry: bool = True) -> list[dict]:
        layers = [
            {"name": "atmosphere_base", "source": "generative", "required": True},
            {
                "name": "sport_surface_geometry",
                "source": "deterministic" if exact_geometry else "optional",
                "required": exact_geometry,
            },
        ]
        if identity:
            layers.append(
                {"name": "hero_identity", "source": "verified_asset", "required": True}
            )
        layers.extend(
            [
                {"name": "exact_entity_marks", "source": "verified_asset", "required": False},
                {"name": "data_and_score", "source": "deterministic", "required": False},
                {"name": "editorial_typography", "source": "deterministic", "required": True},
                {"name": "pul7sar_brand", "source": "verified_asset", "required": True},
            ]
        )
        return layers

    def _leakage(self, **overrides) -> dict:
        payload = {
            "generated_text_detected": False,
            "generated_platform_brand_detected": False,
            "generated_exact_numbers_detected": False,
            "generated_entity_mark_detected": False,
            "generated_unverified_identity_detected": False,
            "generated_sport_geometry_detected": False,
            "notes": [],
        }
        payload.update(overrides)
        return payload

    def _evidence(self, **overrides) -> dict:
        payload = {
            "schema": SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA,
            "gate_id": "semantic_layer_ownership",
            "story_snapshot_sha256": self.STORY_SHA,
            "identity_sensitive_subject_present": True,
            "exact_sport_geometry_required": True,
            "layer_plan": self._layers(),
            "leakage_evidence": self._leakage(),
        }
        payload.update(overrides)
        return payload

    def _write(self, root: Path, payload: dict) -> Path:
        path = root / "semantic_layer_ownership.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_canonical_layer_ownership_replays_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            result = replay_semantic_layer_ownership_gate(
                path, self.STORY_SHA, self._receipt()
            )
            self.assertTrue(result["gate_passed"])
            self.assertEqual(result["gate_id"], "semantic_layer_ownership")
            self.assertEqual(result["verification_details"]["layer_count"], 7)
            self.assertEqual(result["verification_details"]["generated_layer_count"], 1)
            self.assertTrue(
                result["verification_details"][
                    "generated_content_limited_to_non_factual_atmosphere"
                ]
            )
            raw = path.read_bytes()
            self.assertEqual(result["source_evidence_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["source_evidence_byte_size"], len(raw))

    def test_story_without_identity_or_exact_geometry_can_use_optional_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                identity_sensitive_subject_present=False,
                exact_sport_geometry_required=False,
                layer_plan=self._layers(identity=False, exact_geometry=False),
            )
            path = self._write(Path(tmp), evidence)
            result = verify_semantic_layer_ownership_evidence(
                path, self.STORY_SHA, self._receipt()
            )
            self.assertTrue(result["gate_passed"])
            self.assertEqual(result["verification_details"]["layer_count"], 6)
            self.assertEqual(result["verification_details"]["optional_layer_count"], 1)

    def test_generated_typography_leakage_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(generated_text_detected=True)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(
                ValueError, "generated_text_leaked_into_deterministic_typography"
            ):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_generated_brand_leakage_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(generated_platform_brand_detected=True)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(
                ValueError, "generated_platform_brand_leaked_into_verified_brand_layer"
            ):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_generated_exact_data_leakage_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(generated_exact_numbers_detected=True)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "generated_exact_data_leaked"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_generated_entity_mark_leakage_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(generated_entity_mark_detected=True)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "generated_entity_mark_leaked"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_generated_identity_leakage_fails_closed_when_identity_is_reserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(
                    generated_unverified_identity_detected=True
                )
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "generated_identity_leaked"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_generated_exact_sport_geometry_leakage_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                leakage_evidence=self._leakage(generated_sport_geometry_detected=True)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "generated_sport_geometry_leaked"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_exact_data_layer_cannot_be_model_owned(self) -> None:
        layers = self._layers()
        layers[4] = {"name": "data_and_score", "source": "generative", "required": False}
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(layer_plan=layers))
            with self.assertRaisesRegex(
                ValueError, "PUL7SAR_LAYER_OWNERSHIP_SOURCE_INVALID:data_and_score"
            ):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_identity_sensitive_story_requires_verified_hero_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(layer_plan=self._layers(identity=False)),
            )
            with self.assertRaisesRegex(ValueError, "LAYER_SET_INVALID"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_cross_story_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), self._evidence(story_snapshot_sha256="f" * 64)
            )
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                verify_semantic_layer_ownership_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_receipt_cannot_select_another_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            receipt = self._receipt()
            receipt["verifier_id"] = "wrong"
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                verify_semantic_layer_ownership_evidence(path, self.STORY_SHA, receipt)

    def test_policy_rejects_non_boolean_control_flags(self) -> None:
        with self.assertRaisesRegex(ValueError, "IDENTITY_FLAG_INVALID"):
            evaluate_semantic_layer_ownership(
                layer_plan=self._layers(),
                leakage_evidence=self._leakage(),
                identity_sensitive_subject_present=1,
                exact_sport_geometry_required=True,
            )

    def test_adapter_exposes_production_source_object_provenance(self) -> None:
        self.assertIs(
            replay_semantic_layer_ownership_gate.PUL7SAR_PRODUCTION_BACKED,
            True,
        )
        self.assertEqual(
            replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_GATE_ID,
            "semantic_layer_ownership",
        )
        self.assertEqual(
            replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_ID,
            VERIFIER_ID,
        )
        self.assertEqual(
            replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_VERSION,
            VERIFIER_VERSION,
        )
        self.assertIs(
            replay_semantic_layer_ownership_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_semantic_layer_ownership_evidence,
        )


if __name__ == "__main__":
    unittest.main()
