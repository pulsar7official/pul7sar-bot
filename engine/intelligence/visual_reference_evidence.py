"""Traceable visual-reference evidence for Phase 18 PUL7SAR art direction.

The reference is not a universal template. It records which qualities were worth
preserving and which weaknesses must be improved in future story-specific scenes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisualReferenceEvidence:
    reference_id: str
    source_name: str
    sha256: str
    score_out_of_10: float
    preserve: tuple[str, ...]
    improve_or_avoid: tuple[str, ...]

    def __post_init__(self) -> None:
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("visual reference sha256 must be hexadecimal")
        if not 0.0 <= float(self.score_out_of_10) <= 10.0:
            raise ValueError("score_out_of_10 must be between 0 and 10")
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(self, "preserve", tuple(self.preserve))
        object.__setattr__(self, "improve_or_avoid", tuple(self.improve_or_avoid))


CHELSEA_REFERENCE_7_OF_10 = VisualReferenceEvidence(
    reference_id="pul7sar-chelsea-reference-7of10-v1",
    source_name="تشيلسي يبدأ تحضيراته للموسم الجديد.png",
    sha256="ab5f2e7b58d29153427837b08080c39a2912952ca251ef0c3cb29f437c489e60",
    score_out_of_10=7.0,
    preserve=(
        "premium dark sports-editorial depth",
        "fixed metallic PUL7SAR wordmark body",
        "enlarged dynamic number 7",
        "pulse signature tied to number 7",
        "small football signature near R",
        "verified club-linked accent color",
        "dramatic stadium-style light when story benefits from it",
        "subtle tactical drawing as contextual texture when relevant",
        "club flags or exact identity cues when relevant and verified",
        "strong single visual hierarchy",
    ),
    improve_or_avoid=(
        "headline copy that is too long or visually crowded",
        "Arabic rendering that sacrifices clarity for heavy effects",
        "forcing stadium or pitch motifs into unrelated stories",
        "using this composition as a fixed template for all news",
        "invented club marks or generated readable brand text",
        "club names rendered inconsistently when the editorial rule calls for English names",
    ),
)
