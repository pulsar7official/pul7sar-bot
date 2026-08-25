"""Verified provenance contract for hybrid generated base scenes.

A hybrid compositor must not trust caller booleans about whether a generated image
is safe to receive exact layers. This module validates the synthesis manifest and
binds one scene file to its family, sport lock, semantic lock, and prompt-budget
contracts before composition is allowed. Multiple candidates for one family are
supported only when the requested filename uniquely identifies a manifest scene.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class GeneratedBaseProvenance:
    family: EditorialSceneFamily
    image_path: str
    manifest_path: str
    synthesis_contract: str
    sport_lock: str
    prompt_policy: str
    prompt_token_count: int
    prompt_usable_limit: int
    publication_ready: bool
    generated_subject_policy: str
    exact_layers_reserved: tuple[str, ...]
    seed: int | None = None
    contract: str = "pul7sar-generated-base-provenance-v2-multi-candidate"

    EXPECTED_SYNTHESIS_CONTRACTS = (
        "pul7sar-cpu-cross-family-synthesis-v4",
        "pul7sar-result-seed-sweep-v2-provenance",
    )

    @classmethod
    def from_manifest(
        cls,
        *,
        manifest_path: str,
        family: EditorialSceneFamily,
        image_path: str,
    ) -> "GeneratedBaseProvenance":
        manifest_file = Path(manifest_path)
        image_file = Path(image_path)
        if not manifest_file.is_file():
            raise FileNotFoundError(manifest_path)
        if not image_file.is_file():
            raise FileNotFoundError(image_path)
        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
        synthesis_contract = str(payload.get("contract", ""))
        if synthesis_contract not in cls.EXPECTED_SYNTHESIS_CONTRACTS:
            raise ValueError(f"UNTRUSTED_SYNTHESIS_CONTRACT:{synthesis_contract}")
        if payload.get("publication_ready") is not False:
            raise ValueError("SYNTHESIS_BASE_MUST_BE_STUDY_ONLY")

        scenes = payload.get("scenes")
        if not isinstance(scenes, list):
            raise ValueError("SYNTHESIS_MANIFEST_SCENES_MISSING")
        matches = [
            s for s in scenes
            if s.get("family") == family.value
            and Path(str(s.get("file", ""))).name == image_file.name
        ]
        if not matches:
            family_exists = any(s.get("family") == family.value for s in scenes)
            if family_exists:
                raise ValueError("SYNTHESIS_IMAGE_MANIFEST_MISMATCH")
            raise ValueError(f"SYNTHESIS_FAMILY_MISSING:{family.value}")
        if len(matches) != 1:
            raise ValueError("SYNTHESIS_IMAGE_MANIFEST_AMBIGUOUS")
        scene = matches[0]
        if scene.get("sport_lock") != "association_football":
            raise ValueError(f"SPORT_LOCK_MISMATCH:{scene.get('sport_lock')}")
        token_count = int(scene.get("prompt_token_count", -1))
        usable_limit = int(scene.get("prompt_usable_limit", -1))
        if token_count < 1 or usable_limit < 1 or token_count > usable_limit:
            raise ValueError("PROMPT_BUDGET_PROVENANCE_INVALID")
        prompt_policy = str(scene.get("prompt_policy", ""))
        if prompt_policy != "compact_positive_scene_ownership_fail_closed_token_budget":
            raise ValueError(f"UNTRUSTED_PROMPT_POLICY:{prompt_policy}")
        exact_layers_reserved = tuple(str(x) for x in scene.get("exact_layers_reserved", ()))
        required_reservations = {
            "PUL7SAR brand",
            "readable editorial copy",
            "club crests and branded garments",
            "exact score",
            "exact statistics",
            "verified real-person identity",
            "exact sport geometry",
        }
        if not required_reservations.issubset(set(exact_layers_reserved)):
            raise ValueError("EXACT_LAYER_RESERVATIONS_INCOMPLETE")

        raw_seed = scene.get("seed")
        provenance = cls(
            family=family,
            image_path=str(image_file),
            manifest_path=str(manifest_file),
            synthesis_contract=synthesis_contract,
            sport_lock=str(scene.get("sport_lock")),
            prompt_policy=prompt_policy,
            prompt_token_count=token_count,
            prompt_usable_limit=usable_limit,
            publication_ready=False,
            generated_subject_policy=str(scene.get("generated_subject_policy", "")),
            exact_layers_reserved=exact_layers_reserved,
            seed=int(raw_seed) if raw_seed is not None else None,
        )
        provenance.validate_for(family=family, image_path=str(image_file))
        return provenance

    def validate_for(self, *, family: EditorialSceneFamily, image_path: str) -> None:
        if self.family is not family:
            raise ValueError("GENERATED_BASE_FAMILY_MISMATCH")
        if Path(self.image_path).resolve() != Path(image_path).resolve():
            raise ValueError("GENERATED_BASE_PATH_MISMATCH")
        if self.sport_lock != "association_football":
            raise ValueError("GENERATED_BASE_SPORT_NOT_LOCKED")
        if self.publication_ready:
            raise ValueError("GENERATED_BASE_CANNOT_BE_PUBLICATION_READY")
        if self.prompt_token_count > self.prompt_usable_limit:
            raise ValueError("GENERATED_BASE_PROMPT_TRUNCATED")
