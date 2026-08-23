"""Optional zero-cost local semantic inspector using Qwen2.5-VL-3B-Instruct.

This adapter is intentionally lazy: importing Phase 18 never downloads or loads
model weights. A caller must explicitly invoke `inspect_file`. FLUX generation
and semantic inspection are expected to run sequentially so the T4 can release
one model before loading the other.

The model is not used for factual extraction. It answers a fixed visual-QA
schema about the already-generated image. Identity similarity remains a separate
specialized gate.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict

MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
VERIFIER_ID = "qwen2.5-vl-3b-local-v2"


class Qwen25VLInspectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Qwen25VLConfig:
    model_id: str = MODEL_ID
    max_new_tokens: int = 640
    minimum_self_confidence: float = 0.85


class Qwen25VLSemanticInspector:
    """Ask a local VLM for constrained, machine-readable visual QA evidence."""

    def __init__(self, config: Qwen25VLConfig | None = None) -> None:
        self.config = config or Qwen25VLConfig()
        self._pipeline = None

    @staticmethod
    def dependencies_available() -> bool:
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401
            from PIL import Image  # noqa: F401
            return True
        except (ImportError, ModuleNotFoundError):
            return False

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline
        if not self.dependencies_available():
            raise Qwen25VLInspectionError("Qwen semantic inspection dependencies are unavailable")
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "image-text-to-text",
                model=self.config.model_id,
                device_map="auto",
                torch_dtype="auto",
            )
        except Exception as exc:
            raise Qwen25VLInspectionError(f"unable to load local semantic inspector: {exc}") from exc
        return self._pipeline

    @staticmethod
    def _instruction(expected_subject: str | None) -> str:
        subject = expected_subject.strip() if isinstance(expected_subject, str) and expected_subject.strip() else "none"
        return f"""You are a strict sports-editorial visual QA inspector. Inspect only the supplied image. Do not infer facts outside the pixels.
Expected hero subject: {subject}.
Return ONE JSON object only, with exactly these keys:
readable_text_absent, platform_brand_absent, fake_entity_marks_absent, exact_numbers_absent, generated_sport_geometry_absent, single_scene, severe_defects_absent, subject_framing_valid, sport_geometry_alignment_valid.
Each value must be an object with keys: pass (boolean), confidence (number 0..1), detail (short string).
Rules:
- readable_text_absent=false if obvious generated readable or pseudo-readable lettering appears in the clean base scene.
- platform_brand_absent=false if any PUL7SAR-like/platform wordmark, seven/pulse imitation, or logo-like platform branding appears.
- fake_entity_marks_absent=false if obviously invented team, federation, league or competition crests/marks appear.
- exact_numbers_absent=false if score-like numerals, dates, fees, standings values, record values or other editorial exact-number graphics appear in the generative base scene. Incidental jersey numbers inside a natural athlete depiction are not editorial exact-number graphics.
- generated_sport_geometry_absent=false if the generative base scene visibly owns exact field/court/rink markings or diagram geometry that should instead be supplied by a deterministic layer. Natural vague turf/floor/arena texture without exact markings may pass.
- single_scene=false for collage, split-screen, tiled, multi-panel or image-within-image composition.
- severe_defects_absent=false for major malformed anatomy, impossible objects, gross perspective failures, duplicated structural objects or visually broken sport elements.
- subject_framing_valid=true when expected subject is none and the scene has a usable editorial focal hierarchy; when supplied, require the subject to be usable and not badly cropped/occluded.
- sport_geometry_alignment_valid=true only when any visible final playing-surface geometry is physically plausible and coherent with the surrounding arena perspective. If no exact playing-surface geometry is visible, pass with detail saying not materially present.
Be conservative. If uncertain, lower confidence rather than pretending certainty."""

    @staticmethod
    def _extract_text(output: Any) -> str:
        if isinstance(output, str):
            return output
        if isinstance(output, dict):
            if isinstance(output.get("generated_text"), str):
                return output["generated_text"]
            generated = output.get("generated_text")
            if isinstance(generated, list):
                for item in reversed(generated):
                    if isinstance(item, dict) and isinstance(item.get("content"), str):
                        return item["content"]
            for key in ("text", "content"):
                if isinstance(output.get(key), str):
                    return output[key]
        if isinstance(output, list):
            for item in reversed(output):
                text = Qwen25VLSemanticInspector._extract_text(item)
                if text:
                    return text
        return ""

    @staticmethod
    def _json_object(text: str) -> dict[str, Any]:
        value = text.strip()
        if value.startswith("```"):
            value = value.strip("`")
            if value.lower().startswith("json"):
                value = value[4:].lstrip()
        start, end = value.find("{"), value.rfind("}")
        if start < 0 or end <= start:
            raise Qwen25VLInspectionError("semantic inspector did not return a JSON object")
        try:
            data = json.loads(value[start:end + 1])
        except json.JSONDecodeError as exc:
            raise Qwen25VLInspectionError("semantic inspector returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise Qwen25VLInspectionError("semantic inspector JSON root must be an object")
        return data

    @staticmethod
    def _check(data: dict[str, Any], key: str) -> SemanticCheck:
        item = data.get(key)
        if not isinstance(item, dict):
            return SemanticCheck(InspectionState.NOT_INSPECTED, 0.0, "missing verifier field")
        passed = item.get("pass")
        confidence = item.get("confidence")
        detail = str(item.get("detail") or "")[:500]
        if not isinstance(passed, bool) or not isinstance(confidence, (int, float)):
            return SemanticCheck(InspectionState.NOT_INSPECTED, 0.0, "malformed verifier field")
        confidence = max(0.0, min(1.0, float(confidence)))
        return SemanticCheck(InspectionState.PASS if passed else InspectionState.FAIL, confidence, detail)

    def inspect_file(self, image_path: str, *, expected_subject: str | None = None) -> SemanticVisualVerdict:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(image_path)
        try:
            from PIL import Image
            image = Image.open(path).convert("RGB")
        except Exception as exc:
            raise Qwen25VLInspectionError(f"cannot decode inspection image: {exc}") from exc

        pipe = self._load()
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": self._instruction(expected_subject)}]}]
        try:
            output = pipe(text=messages, images=[image], max_new_tokens=self.config.max_new_tokens, return_full_text=False)
        except Exception as exc:
            raise Qwen25VLInspectionError(f"semantic inspection inference failed: {exc}") from exc

        data = self._json_object(self._extract_text(output))
        return SemanticVisualVerdict(
            verifier_id=VERIFIER_ID,
            readable_text_absent=self._check(data, "readable_text_absent"),
            platform_brand_absent=self._check(data, "platform_brand_absent"),
            fake_entity_marks_absent=self._check(data, "fake_entity_marks_absent"),
            single_scene=self._check(data, "single_scene"),
            severe_defects_absent=self._check(data, "severe_defects_absent"),
            subject_framing_valid=self._check(data, "subject_framing_valid"),
            sport_geometry_alignment_valid=self._check(data, "sport_geometry_alignment_valid"),
            exact_numbers_absent=self._check(data, "exact_numbers_absent"),
            generated_sport_geometry_absent=self._check(data, "generated_sport_geometry_absent"),
            identity_valid=None,
        )
