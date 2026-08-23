"""Sport-aware production rules for PUL7SAR Story-to-Visual v1.

Event semantics and sport physics are orthogonal. This registry records which
parts of each sport are safe as atmosphere and which exact geometry/equipment
must be deterministic or verified.
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
    MAT = "mat"
    TABLE = "table"
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


def _rule(sport, surface, exact, overlay, safe, geometry=(), risks=("generated text", "generated logos")):
    return SportVisualRule(sport, surface, exact, overlay, tuple(safe), tuple(geometry), tuple(risks))


_RULES = {
    "football": _rule("football", SportSurface.FIELD, True, True,
        ("crowd atmosphere", "stadium lighting", "tunnel", "touchline ambience", "abstract grass texture"),
        ("regulation rectangular pitch proportions", "single halfway line and centre circle", "correct penalty and goal areas", "perspective-consistent touchlines and goal lines"),
        ("full generated pitch geometry", "generated scoreboards", "generated kit text", "generated club crests")),
    "basketball": _rule("basketball", SportSurface.COURT, True, True,
        ("arena crowd", "tunnel", "bench atmosphere", "basketball texture", "dramatic rim light"),
        ("regulation court proportions", "correct centre circle", "correct three-point arcs", "aligned baskets and paint areas"),
        ("full generated court linework", "generated jersey text", "generated scoreboard")),
    "tennis": _rule("tennis", SportSurface.COURT, True, True,
        ("stadium atmosphere", "player tunnel", "surface texture", "net-side ambience"),
        ("rectangular court proportions", "correct singles and doubles sidelines", "service boxes", "net centred across court"),
        ("invented court markings", "generated sponsor text", "generated score display")),
    "padel": _rule("padel", SportSurface.COURT, True, True,
        ("arena atmosphere", "glass reflections", "court texture"),
        ("regulation rectangular court", "centred net", "continuous glass/wall enclosure geometry"),
        ("invented wall topology", "generated sponsor text", "fake score display")),
    "badminton": _rule("badminton", SportSurface.COURT, True, True,
        ("indoor arena", "court texture", "net-side lighting"),
        ("regulation court proportions", "singles/doubles lines", "centred net"),
        ("invented court markings", "fake score display")),
    "volleyball": _rule("volleyball", SportSurface.COURT, True, True,
        ("arena crowd", "court texture", "net-side atmosphere"),
        ("rectangular court", "centred net", "parallel boundary and attack lines"),
        ("invented court markings", "generated scoreboard", "fake jersey text")),
    "handball": _rule("handball", SportSurface.COURT, True, True,
        ("arena crowd", "goal-area atmosphere", "court texture"),
        ("rectangular court", "correct goal-area arcs", "aligned goals"),
        ("invented court markings", "generated scoreboard", "fake jersey text")),
    "baseball": _rule("baseball", SportSurface.FIELD, True, True,
        ("ballpark crowd", "dugout atmosphere", "stadium lights", "grass/dirt texture"),
        ("coherent diamond geometry", "aligned bases", "home plate and foul lines", "mound relationship"),
        ("invented base positions", "generated scoreboard", "fake jersey text")),
    "american_football": _rule("american_football", SportSurface.FIELD, True, True,
        ("stadium crowd", "tunnel", "sideline atmosphere", "field texture"),
        ("rectangular field", "parallel yard lines", "end zones", "aligned goalposts"),
        ("invented yard markings", "generated scoreboard", "fake jersey text")),
    "rugby": _rule("rugby", SportSurface.FIELD, True, True,
        ("stadium atmosphere", "grass texture", "crowd", "tunnel"),
        ("rectangular field", "try lines", "halfway line", "aligned H-posts"),
        ("invented field markings", "generated scoreboard")),
    "cricket": _rule("cricket", SportSurface.FIELD, True, True,
        ("ground atmosphere", "outfield", "stands", "sunlight"),
        ("central pitch strip", "aligned wickets", "credible crease geometry"),
        ("invented crease markings", "generated scoreboard", "fake kit text")),
    "golf": _rule("golf", SportSurface.COURSE, False, False,
        ("fairway", "green", "gallery", "clubhouse atmosphere", "weather and landscape"),
        ("plausible hole and green relationship",),
        ("invented tournament text", "wrong equipment anatomy", "fake scorecard")),
    "boxing": _rule("boxing", SportSurface.RING, True, True,
        ("arena haze", "ring lights", "crowd", "walkout tunnel"),
        ("four-sided ring", "parallel ropes", "credible corner posts"),
        ("broken rope geometry", "generated belt text", "fake sponsor marks")),
    "mma": _rule("mma", SportSurface.CAGE, True, True,
        ("arena atmosphere", "walkout lighting", "crowd", "mat texture"),
        ("coherent polygonal cage", "continuous fence geometry"),
        ("broken cage geometry", "generated promotion logos", "fake text")),
    "wrestling": _rule("wrestling", SportSurface.MAT, True, True,
        ("arena lighting", "crowd", "mat texture"),
        ("coherent competition mat", "centred contest circle"),
        ("invented mat markings", "fake result text")),
    "judo": _rule("judo", SportSurface.MAT, True, True,
        ("arena ambience", "tatami texture", "crowd"),
        ("coherent contest area and safety zone"),
        ("invented mat layout", "fake scoreboard")),
    "taekwondo": _rule("taekwondo", SportSurface.MAT, True, True,
        ("arena ambience", "mat texture", "crowd"),
        ("coherent contest area"),
        ("invented mat layout", "fake scoreboard")),
    "athletics": _rule("athletics", SportSurface.TRACK, True, True,
        ("stadium ambience", "track texture", "crowd", "finish-line atmosphere"),
        ("parallel lanes", "continuous lane numbering geometry", "credible curve perspective"),
        ("invented lane topology", "generated timing board", "fake result text")),
    "formula_1": _rule("formula_1", SportSurface.ROAD, False, True,
        ("pit-lane atmosphere", "grandstands", "trackside lighting", "garage ambience"),
        ("physically continuous drivable circuit segment",),
        ("generated sponsor typography", "fake car numbers when exact identity matters", "impossible track intersections")),
    "motorsport": _rule("motorsport", SportSurface.ROAD, False, True,
        ("pit lane", "garage", "trackside", "crowd"),
        ("continuous road surface",),
        ("generated sponsor typography", "fake numbers", "impossible track topology")),
    "swimming": _rule("swimming", SportSurface.POOL, True, True,
        ("aquatic arena", "water caustics", "crowd", "starting-block ambience"),
        ("parallel lanes", "consistent lane ropes", "aligned starting blocks"),
        ("warped lane geometry", "generated timing board", "fake result text")),
    "cycling": _rule("cycling", SportSurface.ROAD, False, False,
        ("road", "mountain stage", "peloton atmosphere", "finish-zone ambience"),
        ("continuous plausible road perspective",),
        ("generated jersey sponsor text", "impossible bicycle geometry", "fake timing text")),
    "rowing": _rule("rowing", SportSurface.WATER, True, True,
        ("water atmosphere", "shoreline", "crowd", "weather"),
        ("parallel race lanes", "credible buoy alignment"),
        ("warped boat anatomy", "fake timing board")),
    "sailing": _rule("sailing", SportSurface.WATER, False, False,
        ("sea", "wind", "shoreline", "weather", "fleet atmosphere"),
        (),
        ("impossible rigging", "fake sail numbers when identity matters", "fake result text")),
    "ice_hockey": _rule("ice_hockey", SportSurface.ICE, True, True,
        ("arena crowd", "ice texture", "bench/tunnel atmosphere"),
        ("coherent rink", "centre line", "blue lines", "faceoff circles", "aligned goals"),
        ("invented rink markings", "generated scoreboard", "fake jersey text")),
    "winter_sport": _rule("winter_sport", SportSurface.SNOW, False, False,
        ("snow environment", "mountain atmosphere", "crowd", "weather"), (),
        ("fake timing text", "impossible equipment geometry")),
    "table_tennis": _rule("table_tennis", SportSurface.TABLE, True, True,
        ("indoor arena", "dramatic light", "crowd"),
        ("rectangular table", "centred net", "credible table proportions"),
        ("warped table geometry", "fake score display")),
    "snooker": _rule("snooker", SportSurface.TABLE, True, True,
        ("arena darkness", "table light", "audience"),
        ("rectangular table", "six pockets", "credible cushion geometry"),
        ("wrong pocket count", "fake score display", "impossible ball layout when exact state matters")),
    "darts": _rule("darts", SportSurface.PRECISION, True, True,
        ("arena crowd", "stage lights", "walk-on atmosphere"),
        ("standard circular dartboard topology",),
        ("invented segment numbers", "fake score display")),
    "gymnastics": _rule("gymnastics", SportSurface.OPEN_ENVIRONMENT, False, True,
        ("arena atmosphere", "apparatus area", "spotlight", "crowd"), (),
        ("impossible body anatomy", "wrong apparatus geometry", "fake score display")),
    "weightlifting": _rule("weightlifting", SportSurface.OPEN_ENVIRONMENT, False, True,
        ("competition platform", "arena lighting", "crowd"), (),
        ("incorrect barbell plates when exact weight matters", "fake attempt/result text")),
    "equestrian": _rule("equestrian", SportSurface.OPEN_ENVIRONMENT, False, False,
        ("arena", "course atmosphere", "crowd", "landscape"), (),
        ("impossible horse anatomy", "invented obstacle sequence", "fake score text")),
    "esports": _rule("esports", SportSurface.ABSTRACT, False, True,
        ("arena crowd", "stage lighting", "player desk atmosphere"), (),
        ("generated game UI", "fake team logos", "fake scoreboard", "unreadable screen text")),
}


class SportVisualRuleRegistry:
    _ALIASES = {
        "soccer": "football", "association_football": "football", "كرة القدم": "football",
        "كرة السلة": "basketball", "كرة المضرب": "tennis", "التنس": "tennis",
        "بادل": "padel", "الريشة الطائرة": "badminton", "كرة الطائرة": "volleyball",
        "كرة اليد": "handball", "بيسبول": "baseball", "كرة القدم الأمريكية": "american_football",
        "رجبي": "rugby", "كريكيت": "cricket", "الملاكمة": "boxing", "مصارعة": "wrestling",
        "جودو": "judo", "تايكوندو": "taekwondo", "فورمولا 1": "formula_1", "f1": "formula_1",
        "العاب القوى": "athletics", "ألعاب القوى": "athletics", "السباحة": "swimming",
        "ركوب الدراجات": "cycling", "التجديف": "rowing", "الإبحار": "sailing",
        "الهوكي": "ice_hockey", "تنس الطاولة": "table_tennis", "السنوكر": "snooker",
        "السهام": "darts", "الجمباز": "gymnastics", "رفع الأثقال": "weightlifting",
        "الفروسية": "equestrian", "الرياضات الإلكترونية": "esports",
    }

    def get(self, sport: str) -> SportVisualRule:
        if not isinstance(sport, str) or not sport.strip():
            raise ValueError("sport must be non-empty")
        raw = sport.strip().casefold()
        key = raw.replace("-", "_").replace(" ", "_")
        key = self._ALIASES.get(raw, self._ALIASES.get(key, key))
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
