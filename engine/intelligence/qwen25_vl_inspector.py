"""Optional zero-cost local semantic inspector using Qwen2.5-VL-3B-Instruct.

The inspector has explicit stages. A generative base scene is inspected for
forbidden generated text/branding/numbers/sport geometry before deterministic
composition. The hybrid surface is inspected separately for physical alignment
and visual coherence after exact geometry has been applied.

The Colab/T4 profile is deliberately conservative: inspection images are resized
for semantic QA and generation is capped to a short JSON answer. The semantic
verifier is a QA component, not an image-detail preservation path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any

from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict

MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
VERIFIER_ID = "qwen2.5-vl-3b-local-v4-t4"


class Qwen25VLInspectionError(RuntimeError):
    pass


class SemanticInspectionStage(str, Enum):
    BASE_SCENE = "base_scene"
    HYBRID_SURFACE = "hybrid_surface"


@dataclass(frozen=True)
class Qwen25VLConfig:
    model_id: str = MODEL_ID
    max_new_tokens: int = 256
    minimum_self_confidence: float = 0.85
    max_image_edge: int = 768


class Qwen25VLSemanticInspector:
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
            import torch
            from transformers import pipeline
            self._pipeline = pipeline(
                "image-text-to-text",
                model=self.config.model_id,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else "auto",
            )
        except Exception as exc:
            raise Qwen25VLInspectionError(f"unable to load local semantic inspector: {exc}") from exc
        return self._pipeline

    @staticmethod
    def _instruction(expected_subject: str | None, stage: SemanticInspectionStage) -> str:
        subject = expected_subject.strip() if isinstance(expected_subject, str) and expected_subject.strip() else "none"
        common = f"""You are a strict sports-editorial visual QA inspector. Inspect only the supplied image. Do not infer facts outside the pixels.
Expected hero subject: {subject}.
Return ONE compact JSON object only, with exactly these keys:
readable_text_absent, platform_brand_absent, fake_entity_marks_absent, exact_numbers_absent, generated_sport_geometry_absent, single_scene, severe_defects_absent, subject_framing_valid, sport_geometry_alignment_valid.
Each value must be an object with keys: pass (boolean), confidence (number 0..1), detail (very short string).
General rules:
- single_scene=false for collage, split-screen, tiled, multi-panel or image-within-image composition.
- severe_defects_absent=false for major malformed anatomy, impossible objects, gross perspective failures, duplicated structural objects or visually broken sport elements.
- subject_framing_valid=true when expected subject is none and the scene has a usable editorial focal hierarchy; when supplied, require the subject to be usable and not badly cropped/occluded.
Be conservative. If uncertain, lower confidence rather than pretending certainty.
"""
        if stage is SemanticInspectionStage.BASE_SCENE:
            return common + """
Stage: GENERATIVE BASE SCENE BEFORE DETERMINISTIC COMPOSITION.
Fail readable_text_absent for generated readable/pseudo-readable lettering.
Fail platform_brand_absent for platform wordmark, 7/pulse imitation or platform-like branding.
Fail fake_entity_marks_absent for invented team/federation/league/competition crests.
Fail exact_numbers_absent for score/date/fee/standing/record graphics.
Fail generated_sport_geometry_absent when exact pitch/court/rink markings or tactical geometry are visibly model-generated; vague turf/floor may pass.
For sport_geometry_alignment_valid return pass=true with detail 'not applicable at base stage' unless illegal exact geometry exists.
"""
        return common + """
Stage: HYBRID SURFACE AFTER DETERMINISTIC SPORT GEOMETRY COMPOSITION.
Fail readable_text_absent only for generated/pseudo text surviving from the base.
Fail platform_brand_absent if generated platform branding survived.
Fail fake_entity_marks_absent if invented entity marks survived.
Fail exact_numbers_absent if generated exact editorial-number graphics survived.
Deterministic pitch markings are expected now: fail generated_sport_geometry_absent only for a second/conflicting generated set.
Pass sport_geometry_alignment_valid only when the final surface has plausible proportions, depth/vanishing perspective and physical integration with the stadium; fail pasted-on, floating, implausibly wide/short/long or conflicting perspective.
"""

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

    def inspect_file(
        self,
        image_path: str,
        *,
        expected_subject: str | None = None,
        stage: SemanticInspectionStage = SemanticInspectionStage.BASE_SCENE,
    ) -> SemanticVisualVerdict:
        if not isinstance(stage, SemanticInspectionStage):
            raise TypeError("stage must be SemanticInspectionStage")
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(image_path)
        try:
            from PIL import Image
            image = Image.open(path).convert("RGB")
            max_edge = max(256, int(self.config.max_image_edge))
            if max(image.size) > max_edge:
                image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        except Exception as exc:
            raise Qwen25VLInspectionError(f"cannot decode inspection image: {exc}") from exc

        pipe = self._load()
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": self._instruction(expected_subject, stage)}]}]
        try:
            output = pipe(
                text=messages,
                images=[image],
                max_new_tokens=self.config.max_new_tokens,
                do_sample=False,
                return_full_text=False,
            )
        except Exception as exc:
            raise Qwen25VLInspectionError(f"semantic inspection inference failed: {exc}") from exc

        data = self._json_object(self._extract_text(output))
        return SemanticVisualVerdict(
            verifier_id=f"{VERIFIER_ID}:{stage.value}",
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
