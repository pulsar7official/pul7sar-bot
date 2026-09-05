"""Traceable evidence for the user-approved PUL7SAR visual identity guide.

The guide is approval evidence, not a publication asset. Exact render geometry is
still separately gated by BrandMasterGeometryGate.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandGuideEvidence:
    evidence_id: str
    source_name: str
    sha256: str
    decisions: tuple[str, ...]

    def __post_init__(self) -> None:
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("brand guide evidence sha256 must be hexadecimal")
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(self, "decisions", tuple(self.decisions))


APPROVED_BRAND_GUIDE_EVIDENCE = BrandGuideEvidence(
    evidence_id="pul7sar-brand-guide-approved-phase18-v1",
    source_name="دليل هوية بولسار الرياضية futuristикалык.png",
    sha256="0817d597efad133a9f599c1f9c8c1d0e31126a7528311791ab1ca3d68a1b47e6",
    decisions=(
        "metallic wordmark body remains fixed",
        "only pulse and number 7 change with verified club/story color",
        "number 7 remains larger than surrounding letters",
        "pulse remains below wordmark",
        "small football remains near R as football signature",
        "lower logo placement is preferred when it does not collide with content",
        "stadium light, tactical drawing, club flags and football are optional approved football motifs, not mandatory for every story",
    ),
)
