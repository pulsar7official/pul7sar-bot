"""Temporary PUL7SAR brand defaults.

IMPORTANT:
    The final PUL7SAR Signature Red is NOT finalized.
    These values are PROVISIONAL placeholders for architecture validation.
    OWNER VISUAL APPROVAL IS PENDING.

Do not label the temporary primary as official, signature, or final.
"""

from __future__ import annotations

from engine.branding.model import BrandPalette

# TEMPORARY — OWNER APPROVAL PENDING.
# One centralized replacement point for the future approved Signature Red.
TEMPORARY_BRAND_PRIMARY = (225, 6, 0)  # #E10600 — provisional only.


def get_default_brand_palette() -> BrandPalette:
    """Return the current provisional master palette."""
    return BrandPalette(
        primary=TEMPORARY_BRAND_PRIMARY,
        secondary=(20, 30, 50),
        accent=TEMPORARY_BRAND_PRIMARY,
        dark=(15, 23, 42),
        light=(240, 245, 250),
        text=(255, 255, 255),
        brand_id="pul7sar_temp",
    )
