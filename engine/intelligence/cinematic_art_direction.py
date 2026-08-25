"""Story-first cinematic art direction profiles for PUL7SAR visual families.

The profiles describe a visual world, not a fixed template. They intentionally
control camera, lens, material mood, environment density and hero placement so
cross-family scenes cannot collapse into the same centered procedural poster.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class CinematicArtDirection:
    family: EditorialSceneFamily
    camera_xyz: tuple[float, float, float]
    look_at_xyz: tuple[float, float, float]
    lens_mm: float
    aperture_fstop: float
    environment_density: float
    hero_bias_x: float
    horizon_height: float
    surface_reflectivity: float
    atmosphere: str
    material_language: str
    composition_language: str
    must_avoid: tuple[str, ...]
    contract: str = "pul7sar-cinematic-art-direction-v1"


class CinematicArtDirectionRegistry:
    _COMMON_AVOID = (
        "generic centered poster",
        "symmetrical demo scene unless story requires symmetry",
        "floating placeholder badge",
        "empty crest slot",
        "decorative pulse outside approved brand",
        "full pitch by default",
        "uniform neon on every object",
    )

    _MAP = {
        EditorialSceneFamily.TRANSFER_SIGNATURE: CinematicArtDirection(
            family=EditorialSceneFamily.TRANSFER_SIGNATURE,
            camera_xyz=(-1.20, -15.8, 5.25), look_at_xyz=(0.45, 0.55, 2.35), lens_mm=67,
            aperture_fstop=3.8, environment_density=.66, hero_bias_x=.18, horizon_height=.47,
            surface_reflectivity=.34, atmosphere="arrival tension, premium architectural depth, controlled destination light",
            material_language="tailored fabric, brushed alloy, dark stone, narrow luminous accents",
            composition_language="asymmetric threshold or object-led signing scene; destination pulls the eye through depth",
            must_avoid=_COMMON_AVOID + ("fake player likeness", "fake contract ceremony when unverified"),
        ),
        EditorialSceneFamily.RESULT_STATEMENT: CinematicArtDirection(
            family=EditorialSceneFamily.RESULT_STATEMENT,
            camera_xyz=(-.60, -16.2, 4.90), look_at_xyz=(0.10, .45, 2.15), lens_mm=72,
            aperture_fstop=4.6, environment_density=.74, hero_bias_x=.04, horizon_height=.43,
            surface_reflectivity=.48, atmosphere="post-match stadium-scale tension without requiring a literal stadium",
            material_language="heavy machined score metal, club-color light fields, dark reflective sporting surface",
            composition_language="score exists as a physical editorial object inside space; identities oppose through depth not panels",
            must_avoid=_COMMON_AVOID + ("scoreboard card", "winner humiliating loser", "oversized score filling the frame"),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: CinematicArtDirection(
            family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            camera_xyz=(-1.45, -15.0, 5.10), look_at_xyz=(.45, .50, 2.45), lens_mm=78,
            aperture_fstop=3.2, environment_density=.48, hero_bias_x=.26, horizon_height=.51,
            surface_reflectivity=.22, atmosphere="editorial restraint, quiet emotional negative space, subject-first staging",
            material_language="soft matte architecture, fabric detail, restrained metal, practical light",
            composition_language="off-center subject or absence metaphor with a deliberately quiet secondary field",
            must_avoid=_COMMON_AVOID + ("fabricated face", "generic mannequin as if it were the real person"),
        ),
        EditorialSceneFamily.TACTICAL_BOARD: CinematicArtDirection(
            family=EditorialSceneFamily.TACTICAL_BOARD,
            camera_xyz=(-1.10, -14.0, 9.60), look_at_xyz=(.15, 1.10, .25), lens_mm=58,
            aperture_fstop=6.3, environment_density=.38, hero_bias_x=.00, horizon_height=.31,
            surface_reflectivity=.16, atmosphere="analytical clarity with premium spatial depth rather than sci-fi spectacle",
            material_language="matte playing surface, precise luminous tactical traces, neutral metal markers",
            composition_language="cropped mechanism or phase corridor; exact geometry owns the image and decoration stays secondary",
            must_avoid=_COMMON_AVOID + ("fake tactical data", "full decorative stadium", "random arrows"),
        ),
        EditorialSceneFamily.DATA_MONUMENT: CinematicArtDirection(
            family=EditorialSceneFamily.DATA_MONUMENT,
            camera_xyz=(-.85, -15.6, 5.15), look_at_xyz=(.10, .70, 2.25), lens_mm=70,
            aperture_fstop=4.8, environment_density=.44, hero_bias_x=-.12, horizon_height=.46,
            surface_reflectivity=.42, atmosphere="luxury information object, precise and sparse, strong negative space",
            material_language="engraved metal, frosted glass, exact data light, subtle dark stone",
            composition_language="one factual number/ranking/draw system behaves as the hero object, not a dashboard",
            must_avoid=_COMMON_AVOID + ("dashboard cards", "invented statistics", "decorative chart junk"),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: CinematicArtDirection(
            family=EditorialSceneFamily.EVENT_EDITORIAL,
            camera_xyz=(-1.25, -16.4, 5.05), look_at_xyz=(.35, .75, 2.35), lens_mm=64,
            aperture_fstop=4.0, environment_density=.70, hero_bias_x=.21, horizon_height=.48,
            surface_reflectivity=.28, atmosphere="anticipation, event scale, forward depth and one memorable symbolic object",
            material_language="sport object realism, architectural darkness, practical event light, restrained haze",
            composition_language="object story or anticipation passage; event world is immersive and not a generic arena wallpaper",
            must_avoid=_COMMON_AVOID + ("invented venue identity", "invented result", "generic event card"),
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> CinematicArtDirection:
        if not isinstance(family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        return cls._MAP[family]
