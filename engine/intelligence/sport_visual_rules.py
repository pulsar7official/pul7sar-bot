"""Sport-aware production rules for PUL7SAR Story-to-Visual v1.

Event semantics and sport geometry are orthogonal. A transfer, injury, record or
controversy can happen in many sports, while each sport has different physical
surfaces, equipment and geometry risks. This registry keeps those concerns
separate so the visual system can scale beyond football without inventing a new
pipeline for every sport.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SportSurface(str, Enum):
    FIELD = "field"
    COURT = "court"
    TRACK = "track"
    ROAD = "road"
    RING = "ring"
    CAGE = "cage"
    COURSE = "course"
    POOL = "pool"
    WATER = "water"
    ICE = "ice"
    SNOW = "snow"
    PRECISION = "precision"
    OPEN_ENVIRONMENT = "open_environment"
    ABSTRACT = "abstract"


@dataclass(frozen=True)
class SportVisualRule:
    sport: str
    surface: SportSurface
    exact_geometry_preferred: bool
    deterministic_overlay_preferred: bool
    safe_generated_context: tuple[str, ...]
    geometry_requirements: tuple[str, ...]
    high_risk_generated_elements: tuple[str, ...]


_RULES = {
    "football": SportVisualRule(
        "football", SportSurface.FIELD, True, True,
        ("crowd atmosphere", "stadium lighting", "tunnel", "touchline ambience", "abstract grass texture"),
        ("regulation rectangular pitch proportions", "single halfway line and centre circle", "correct penalty and goal areas", "perspective-consistent touchlines and goal lines"),
        ("full generated pitch geometry", "generated scoreboards", "generated kit text", "generated club crests"),
    ),
    "basketball": SportVisualRule(
        "basketball", SportSurface.COURT, True, True,
        ("arena crowd", "tunnel", "bench atmosphere", "basketball texture", "dramatic rim light"),
        ("regulation court proportions", "correct centre circle", "correct three-point arcs", "aligned baskets and paint areas"),
        ("full generated court linework", "generated jersey text", "generated scoreboard"),
    ),
    "tennis": SportVisualRule(
        "tennis", SportSurface.COURT, True, True,
        ("stadium atmosphere", "player tunnel", "surface texture", "net-side ambience"),
        ("rectangular court proportions", "correct singles and doubles sidelines", "service boxes", "net centred across court"),
        ("invented court markings", "generated sponsor text", "generated score display"),
    ),
    "golf": SportVisualRule(
        "golf", SportSurface.COURSE, False, False,
        ("fairway", "green", "gallery", "clubhouse atmosphere", "weather and landscape"),
        ("plausible hole and green relationship",),
        ("invented tournament text", "wrong equipment anatomy", "fake scorecard"),
    ),
    "boxing": SportVisualRule(
        "boxing", SportSurface.RING, True, True,
        ("arena haze", "ring lights", "crowd", "walkout tunnel"),
        ("four-sided ring", "parallel ropes", "credible corner posts"),
        ("broken rope geometry", "generated belt text", "fake sponsor marks"),
    ),
    "mma": SportVisualRule(
        "mma", SportSurface.CAGE, True, True,
        ("arena atmosphere", "walkout lighting", "crowd", "mat texture"),
        ("coherent polygonal cage", "continuous fence geometry"),
        ("broken cage geometry", "generated promotion logos", "fake text"),
    ),
    "athletics": SportVisualRule(
        "athletics", SportSurface.TRACK, True, True,
        ("stadium ambience", "track texture", "crowd", "finish-line atmosphere"),
        ("parallel lanes", "continuous lane numbering geometry", "credible curve perspective"),
        ("invented lane topology", "generated timing board", "fake result text"),
    ),
    "formula_1": SportVisualRule(
        "formula_1", SportSurface.ROAD, False, True,
        ("pit-lane atmosphere", "grandstands", "trackside lighting", "garage ambience"),
        ("physically continuous drivable circuit segment",),
        ("generated sponsor typography", "fake car numbers when exact identity matters", "impossible track intersections"),
    ),
    "motorsport": SportVisualRule(
        "motorsport", SportSurface.ROAD, False, True,
        ("pit lane", "garage", "trackside", "crowd"),
        ("continuous road surface",),
        ("generated sponsor typography", "fake numbers", "impossible track topology"),
    ),
    "swimming": SportVisualRule(
        "swimming", SportSurface.POOL, True, True,
        ("aquatic arena", "water caustics", "crowd", "starting-block ambience"),
        ("parallel lanes", "consistent lane ropes", "aligned starting blocks"),
        ("warped lane geometry", "generated timing board", "fake result text"),
    ),
    "cycling": SportVisualRule(
        "cycling", SportSurface.ROAD, False, False,
        ("road", "mountain stage", "peloton atmosphere", "finish-zone ambience"),
        ("continuous plausible road perspective",),
        ("generated jersey sponsor text", "impossible bicycle geometry", "fake timing text"),
    ),
    "volleyball": SportVisualRule(
        "volleyball", SportSurface.COURT, True, True,
        ("arena crowd", "court texture", "net-side atmosphere"),
        ("rectangular court", "centred net", "parallel boundary and attack lines"),
        ("invented court markings", "generated scoreboard", "fake jersey text"),
    ),
    "handball": SportVisualRule(
        "handball", SportSurface.COURT, True, True,
        ("arena crowd", "goal-area atmosphere", "court texture"),
        ("rectangular court", "correct goal-area arcs", "aligned goals"),
        ("invented court markings", "generated scoreboard", "fake jersey text"),
    ),
    "ice_hockey": SportVisualRule(
        "ice_hockey", SportSurface.ICE, True, True,
        ("arena crowd", "ice texture", "bench/tunnel atmosphere"),
        ("coherent rink", "centre line", "blue lines", "faceoff circles", "aligned goals"),
        ("invented rink markings", "generated scoreboard", "fake jersey text"),
    ),
    "winter_sport": SportVisualRule(
        "winter_sport", SportSurface.SNOW, False, False,
        ("snow environment", "mountain atmosphere", "crowd", "weather"),
        (),
        ("fake timing text", "impossible equipment geometry"),
    ),
}


class SportVisualRuleRegistry:
    _ALIASES = {
        "soccer": "football", "association_football": "football", "كرة القدم": "football",
        "كرة السلة": "basketball", "كرة المضرب": "tennis", "التنس": "tennis",
        "الملاكمة": "boxing", "فورمولا 1": "formula_1", "f1": "formula_1",
        "العاب القوى": "athletics", "ألعاب القوى": "athletics",
        "السباحة": "swimming", "ركوب الدراجات": "cycling", "كرة الطائرة": "volleyball",
        "كرة اليد": "handball", "الهوكي": "ice_hockey",
    }

    def get(self, sport: str) -> SportVisualRule:
        if not isinstance(sport, str) or not sport.strip():
            raise ValueError("sport must be non-empty")
        key = sport.strip().casefold().replace("-", "_").replace(" ", "_")
        key = self._ALIASES.get(sport.strip().casefold(), self._ALIASES.get(key, key))
        if key in _RULES:
            return _RULES[key]
        return SportVisualRule(
            sport=key,
            surface=SportSurface.OPEN_ENVIRONMENT,
            exact_geometry_preferred=False,
            deterministic_overlay_preferred=True,
            safe_generated_context=("environmental atmosphere", "lighting", "depth", "texture"),
            geometry_requirements=(),
            high_risk_generated_elements=("generated text", "generated logos", "exact scores", "exact diagrams"),
        )
