"""Conservative pixel-health gate for Phase 18 visual candidates.

This is deliberately not an aesthetic judge. It removes only obviously broken
renders before human/editorial review: near-blank frames, severe clipping, or
very low visual information. Passing this gate never means publication-ready.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VisualCandidateQuality:
    path: str
    mean_luma: float
    dark_fraction: float
    bright_fraction: float
    entropy: float
    passed: bool
    reasons: tuple[str, ...]
    contract: str = "pul7sar-visual-candidate-quality-gate-v1"


class VisualCandidateQualityGate:
    MIN_MEAN_LUMA = 28.0
    MAX_MEAN_LUMA = 232.0
    MAX_DARK_FRACTION = 0.86
    MAX_BRIGHT_FRACTION = 0.72
    MIN_ENTROPY = 4.25

    @classmethod
    def inspect(cls, image_path: str) -> VisualCandidateQuality:
        from PIL import Image

        p = Path(image_path)
        if not p.is_file():
            raise FileNotFoundError(image_path)
        gray = Image.open(p).convert("L")
        hist = gray.histogram()
        total = max(1, sum(hist))
        mean = sum(i * count for i, count in enumerate(hist)) / total
        dark = sum(hist[:20]) / total
        bright = sum(hist[236:]) / total
        entropy = float(gray.entropy())

        reasons = []
        if mean < cls.MIN_MEAN_LUMA:
            reasons.append("FRAME_TOO_DARK")
        if mean > cls.MAX_MEAN_LUMA:
            reasons.append("FRAME_TOO_BRIGHT")
        if dark > cls.MAX_DARK_FRACTION:
            reasons.append("EXCESSIVE_BLACK_CLIPPING")
        if bright > cls.MAX_BRIGHT_FRACTION:
            reasons.append("EXCESSIVE_HIGHLIGHT_CLIPPING")
        if entropy < cls.MIN_ENTROPY:
            reasons.append("INSUFFICIENT_VISUAL_INFORMATION")

        return VisualCandidateQuality(
            path=str(p),
            mean_luma=round(mean, 3),
            dark_fraction=round(dark, 5),
            bright_fraction=round(bright, 5),
            entropy=round(entropy, 4),
            passed=not reasons,
            reasons=tuple(reasons),
        )
