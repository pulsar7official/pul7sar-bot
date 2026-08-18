
import os
import json
import re
import time
import random
import logging
import subprocess
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import urlparse, quote

import requests
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageOps, ImageFont
from ddgs import DDGS

# ==============================================================================
# الإعدادات الأساسية
# ==============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
LOG = logging.getLogger("pul7sar")

GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX", "").strip()
GIT_AUTO_PUSH = os.environ.get("GIT_AUTO_PUSH", "true").strip().lower() == "true"
USE_VISUAL_ENGINE = (
    os.environ.get("USE_VISUAL_ENGINE", "false").strip().lower() == "true"
)

# مفتاح TheSportsDB المجاني
THESPORTSDB_API_KEY = "3"

HISTORY_FILE = "posted_history.json"
MAX_HISTORY_ITEMS = 300
ARTICLE_MAX_AGE_HOURS = 48
FINAL_IMAGE_PATH = "processed_image.jpg"
POST_INTERVAL_MINUTES = 10

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PUL7SAR-Bot/3.0)"}

LOGO_PATH = "logo.png"
MIN_LANDSCAPE_RATIO = 1.05

# Phase 13 — Visual Engine is lazy/application-scoped and OFF by default.
_VISUAL_ENGINE = None


def _get_visual_engine():
    """Lazy-initialize and return the application-scoped Visual Engine."""
    global _VISUAL_ENGINE
    if _VISUAL_ENGINE is None and USE_VISUAL_ENGINE:
        LOG.info("Initializing Visual Engine (lazy load)...")
        from engine.bootstrap import create_engine

        _VISUAL_ENGINE = create_engine()
        LOG.info(
            "Visual Engine initialized successfully "
            "(infrastructure-only mode)"
        )
    return _VISUAL_ENGINE

# ==============================================================================
# قاعدة بيانات الشهرة والأحداث (نظام الأولويات الديناميكي)
# ==============================================================================

FAME_SCORES = {
    # أساطير كرة القدم
    "messi": 10, "ronaldo": 10, "maradona": 10, "pele": 10,
    "zidane": 9, "ronaldinho": 9, "beckham": 8,
    # نجوم العالم
    "mbappe": 9, "haaland": 9, "neymar": 9, "benzema": 9,
    "lewandowski": 8, "kane": 8, "salah": 8,
    # نجوم كبار
    "de bruyne": 8, "van dijk": 8, "modric": 8, "kroos": 8,
    "ramos": 8, "marcelo": 7, "iniesta": 8, "xavi": 8,
    # نجوم الأندية الكبرى
    "vinicius": 7, "bellingham": 7, "saka": 7, "martinelli": 7,
    "odegaard": 7, "rice": 7, "musiala": 7, "wirtz": 7,
    "pedri": 7, "gavi": 7, "ansu fati": 7, "lamine yamal": 7,
    # مدربون
    # ملاحظة: "zidane" مُعرَّف مرة واحدة فقط أعلى القاموس (ضمن أساطير كرة القدم بقيمة 9)
    # لتفادي التعريف المكرر السابق الذي كان يُسقِط قيمته إلى 8 دون قصد (تكرار مفتاح بقاموس Python).
    "guardiola": 9, "ancelotti": 9, "klopp": 8, "mourinho": 8,
    "ten hag": 7, "arteta": 7, "pochettino": 7,
    "tuchel": 7, "nagelsmann": 7, "spalletti": 7,
    # رياضات أخرى
    "nadal": 9, "djokovic": 9, "federer": 9, "alcaraz": 8,
    "hamilton": 8, "verstappen": 8, "leclerc": 7,
}

EVENT_KEYWORDS = {
    "title": 10, "champion": 10, "cup": 9, "final": 9,
    "transfer": 8, "sign": 8, "signed": 8, "deal": 7,
    "injury": 8, "injured": 8, "out": 6,
    "sacked": 9, "fired": 9, "resign": 8,
    "record": 10, "historic": 10, "unbeaten": 9,
    "derby": 8, "clasico": 8, "classic": 7,
    "goal": 7, "score": 6, "win": 6, "victory": 7,
}

RARITY_KEYWORDS = {
    "unbeaten": 10, "undefeated": 10, "invincible": 10,
    "first time": 9, "first ever": 9, "historic": 9,
    "shock": 8, "unexpected": 8, "surprise": 8,
    "rare": 7, "unique": 7, "never": 7,
}

# ==============================================================================
# STOPWORDS وإعدادات RSS
# ==============================================================================

STOPWORDS = {
    "the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "with", "after",
    "before", "vs", "is", "are", "was", "were", "by", "from", "as", "his", "her",
    "their", "up", "out", "new", "says", "how", "why", "what",
    "في", "من", "على", "عن", "إلى", "هذا", "هذه", "ذلك", "التي", "الذي", "مع",
    "بعد", "قبل", "أن", "إن", "كان", "قال", "كل",
}

RSS_URLS = [
    "https://www.skysports.com/rss/12040",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://news.google.com/rss/search?q=football+transfer+news+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d",
    "https://news.google.com/rss/search?q=champions+league+news+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d",
    "https://news.google.com/rss/search?q=real+madrid+barcelona+milan+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d",
]

SKIP_KEYWORDS = ["quiz", "guess", "challenge", "poll", "vote", "10 things", "rank", "rumour"]

# نطاقات القنوات التلفزيونية التي نستبدل صورها
CHANNEL_LOGO_DOMAINS = ["bbci.co.uk", "skysports.com"]

TRUSTED_IMAGE_DOMAINS = [
    "wikipedia.org", "wikimedia.org",
    "espncdn.com", "espn.com",
    "uefa.com", "fifa.com",
    "reuters.com", "apnews.com",
    "gettyimages.com",
    "premierleague.com", "laliga.com", "bundesliga.com", "legaseriea.it", "ligue1.com",
    "theguardian.com", "independent.co.uk", "mirror.co.uk", "standard.co.uk",
    "goal.com", "90min.com", "football-italia.net", "marca.com", "as.com",
    "realmadrid.com", "fcbarcelona.com", "manutd.com", "liverpoolfc.com",
    "mancity.com", "chelseafc.com", "arsenal.com", "tottenhamhotspur.com",
    "psg.fr", "fcbayern.com", "juventus.com", "acmilan.com", "inter.it",
]

# ==============================================================================
# المرحلة 2 — استخراج الكيانات ونوع الرياضة (لمطابقة الصور بدقة، راجع Master Plan §2.3)
# ==============================================================================
# دليل حقيقي دفع لبناء هذا القسم: نُشرت صورة منتخب إنجلترا لكرة القدم مع خبر عن
# رياضة أخرى تماماً (نتيجة 61-54 بنصف نهائي دورة الكومنولث -- على الأرجح نتبول).
# السبب: كلمة "إنجلترا" وحدها كانت كافية ليقبل النظام أول صورة إنجليزية متاحة
# بغض النظر عن الرياضة. الحل: استخراج نوع الرياضة كبُعد إلزامي مستقل عن اسم الفريق،
# والتحقق من عدم تعارضه مع نص أي صورة مرشحة قبل قبولها.

# خرائط الرياضة من مسار الرابط (الإشارة الأدق والأكثر موثوقية -- تُقرأ مباشرة من
# بنية الموقع المصدر وليست تخميناً نصياً). مثال: skysports.com/rss/12040 هو في
# الواقع خلاصة "جميع الرياضات" العامة للموقع (وليس كرة قدم فقط كما قد يوحي رقمها)،
# لذلك لا يمكن الاعتماد على مصدر الخلاصة نفسه لتحديد الرياضة -- لازم القراءة من
# مسار كل رابط مقال على حدة.
SPORT_PATH_MAP = {
    "football": "football", "soccer": "football",
    "cricket": "cricket",
    "netball": "netball",
    "rugby-union": "rugby", "rugby-league": "rugby", "rugby": "rugby",
    "tennis": "tennis",
    "golf": "golf",
    "boxing": "boxing",
    "darts": "darts",
    "snooker": "snooker",
    "athletics": "athletics",
    "cycling": "cycling",
    "swimming": "swimming",
    "f1": "motorsport", "formula1": "motorsport", "formula-1": "motorsport",
    "motorsport": "motorsport", "racing": "motorsport",
    "basketball": "basketball",
    "hockey": "hockey",
    "gymnastics": "gymnastics",
}

# خرائط الرياضة من الكلمات المفتاحية بالنص (احتياطي عندما لا يكشف الرابط الرياضة،
# مثل روابط Google News العامة) -- إنجليزي وعربي معاً.
SPORT_TEXT_KEYWORDS = {
    "football": "football", "soccer": "football", "premier league": "football",
    "champions league": "football", "la liga": "football", "bundesliga": "football",
    "cricket": "cricket", "ashes": "cricket", "test match": "cricket", "the hundred": "cricket",
    "netball": "netball",
    "rugby": "rugby",
    "tennis": "tennis", "wimbledon": "tennis",
    "golf": "golf", "masters": "golf", "ryder cup": "golf",
    "boxing": "boxing",
    "formula 1": "motorsport", "f1": "motorsport", "grand prix": "motorsport", "motogp": "motorsport",
    "athletics": "athletics",
    "cycling": "cycling", "tour de france": "cycling",
    "swimming": "swimming",
    "basketball": "basketball", "nba": "basketball",
    "hockey": "hockey",
    "كرة القدم": "football", "دوري الأبطال": "football", "الدوري الإنجليزي": "football",
    "الكريكيت": "cricket", "الرجبي": "rugby", "التنس": "tennis",
    "الجولف": "golf", "الملاكمة": "boxing", "الدراجات": "cycling",
    "السباحة": "swimming", "كرة السلة": "basketball", "الفورمولا": "motorsport",
}

# أندية ومنتخبات شائعة (اسم موحّد بالإنجليزية للبحث ولمطابقة نص الصورة المرشحة)
CLUB_KEYWORDS = {
    "real madrid": "Real Madrid", "barcelona": "Barcelona", "bayern": "Bayern Munich",
    "man city": "Manchester City", "manchester city": "Manchester City",
    "man utd": "Manchester United", "manchester united": "Manchester United",
    "liverpool": "Liverpool", "psg": "Paris Saint-Germain", "chelsea": "Chelsea",
    "arsenal": "Arsenal", "juventus": "Juventus", "ac milan": "AC Milan", "inter milan": "Inter Milan",
    "tottenham": "Tottenham Hotspur",
    "england": "England", "france": "France", "spain": "Spain", "germany": "Germany",
    "brazil": "Brazil", "argentina": "Argentina", "portugal": "Portugal", "italy": "Italy",
    "netherlands": "Netherlands", "new zealand": "New Zealand", "australia": "Australia",
}


def detect_sport_from_url(link: str):
    """يقرأ نوع الرياضة من مقاطع مسار الرابط نفسه -- إشارة أدق من تخمين النص."""
    try:
        segments = [s.lower() for s in urlparse(link).path.split("/") if s]
    except Exception:
        return None
    for seg in segments:
        if seg in SPORT_PATH_MAP:
            return SPORT_PATH_MAP[seg]
    return None


def detect_sport_from_text(text: str):
    """احتياطي: يكشف الرياضة من كلمات مفتاحية بالعنوان/الملخص عند تعذّر قراءتها من الرابط."""
    text_l = text.lower()
    for kw, sport in SPORT_TEXT_KEYWORDS.items():
        if kw in text_l:
            return sport
    return None


def extract_entities(article: dict) -> dict:
    """
    يستخرج من الخبر: اللاعب (إن وُجد)، النادي/المنتخب (إن وُجد)، ونوع الرياضة
    (العنصر الأهم لتفادي صورة من رياضة مختلفة تماماً عن الخبر)، واستعلام بحث نصي.
    يُستخدم لبناء استعلامات البحث *و* للتحقق من صلة كل صورة مرشحة قبل قبولها.
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    text_l = f"{title} {summary}".lower()

    sport = article.get("sport") or detect_sport_from_text(text_l)

    player = next((name for name in FAME_SCORES if name in text_l), None)
    club = next((canon for key, canon in CLUB_KEYWORDS.items() if key in text_l), None)

    if player:
        query = player
    elif club:
        query = club
    else:
        words = re.findall(r"[a-zA-Z]{4,}", title)
        query = " ".join(words[:2]) if words else None

    # استعلام مُوضَّح السياق -- يُستخدم فقط لمصادر البحث النصي العام (Google،
    # Wikimedia، DDGS). القاعدة عامة (تنطبق على أي اسم لاعب أو نادٍ مطابَق، لا
    # اسم بعينه): كل اسم مفرد مأخوذ مباشرة من FAME_SCORES أو CLUB_KEYWORDS قد
    # يتصادم مع كلمة/مكان/معنى آخر تماماً -- سواء أسماء أندية (مثال حقيقي:
    # "Arsenal" يصطدم مع "Arsenale" الترسانة التاريخية بمدينة البندقية) أو أسماء
    # لاعبين (أمثلة حقيقية بقاموسنا: "Stones" لاعب إنجليزي = أيضاً "أحجار"،
    # "Rice" = "أرز"، "Kane"، "Walker"، "Young"، "Cole" -- كلها كلمات إنجليزية
    # شائعة بمفردها). لذلك نضيف سياقاً رياضياً صريحاً لأي استعلام قائم على كيان
    # مطابَق مباشرة، بلا استثناء لاسم بعينه. TheSportsDB لا تحتاج هذا (قاعدة
    # بياناتها رياضية حصراً أصلاً فلا لبس فيها).
    search_query = query
    if sport and sport != "football":
        context = f"{sport} player" if player else f"{sport} team"
    else:
        context = "footballer" if player else "football club"
    if player and query == player:
        search_query = f"{query} {context}"
    elif club and query == club:
        search_query = f"{query} {context}"
    elif query:
        # لا كيان محدد مطابَق -- الاستعلام كلمات عامة من العنوان، معرَّضة هي
        # الأخرى لتصادم المعنى. إضافة كلمة الرياضة نفسها (أو "sport" افتراضياً)
        # لا تحدد كياناً بعينه لكنها تحيّز نتائج البحث نحو المحتوى الرياضي.
        search_query = f"{query} {sport or 'sport'}"

    LOG.info("🔎 كيانات الخبر: لاعب=%s | نادٍ=%s | رياضة=%s | استعلام=%s | استعلام موضَّح=%s",
             player, club, sport, query, search_query)
    return {"player": player, "club": club, "sport": sport, "query": query, "search_query": search_query}


def is_candidate_relevant(candidate_text: str, entities: dict) -> bool:
    """
    تحقق موحّد من صلة صورة مرشحة، يُطبَّق على كل مصادر الصور بلا استثناء (كانت
    هذه الفجوة الأساسية سابقاً: TheSportsDB وGoogle وWikimedia كانت تقبل أول
    نتيجة بلا أي تحقق). القاعدة الحاسمة: لو عرفنا رياضة الخبر ونص الصورة يذكر
    صراحة رياضة أخرى مختلفة، تُرفض الصورة فوراً بغض النظر عن أي تطابق اسمي.
    """
    text_l = (candidate_text or "").lower()

    entity_sport = entities.get("sport")
    if entity_sport and text_l:
        for kw, sport in SPORT_TEXT_KEYWORDS.items():
            if sport and sport != entity_sport and kw in text_l:
                LOG.info("🚫 رفض صورة: نصها يذكر رياضة '%s' بينما رياضة الخبر '%s'", sport, entity_sport)
                return False

    if not text_l:
        # لا يوجد نص وصفي للصورة (بعض المصادر لا تعيد عنواناً) -- نقبل فقط لو ما
        # كان عندنا كيان محدد أصلاً نطالب بمطابقته
        return not (entities.get("player") or entities.get("club"))

    if entities.get("player") and entities["player"] in text_l:
        return True
    if entities.get("club") and entities["club"].lower() in text_l:
        return True
    if entities.get("query"):
        q_words = re.findall(r"[a-zA-Z]{3,}", entities["query"].lower())
        if q_words and any(w in text_l for w in q_words):
            return True

    return not (entities.get("player") or entities.get("club"))

# ==============================================================================
# دوال الخطوط والمساعدة
# ==============================================================================

def _load_bold_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def retry(fn, attempts=3, delay=2.0, what="operation"):
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            LOG.warning("محاولة %d/%d فشلت في %s: %s", i, attempts, what, exc)
            if i < attempts:
                time.sleep(delay * i)
    LOG.error("فشلت كل المحاولات في %s: %s", what, last_exc)
    return None

# ==============================================================================
# دوال إدارة السجل
# ==============================================================================

def load_history():
    data = {"links": [], "titles": []}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    data["links"] = loaded.get("links", [])
                    data["titles"] = loaded.get("titles", [])
        except (json.JSONDecodeError, OSError) as exc:
            LOG.warning("تعذر قراءة السجل، سيبدأ فارغاً: %s", exc)
    return data


def save_history(history):
    history["links"] = history["links"][-MAX_HISTORY_ITEMS:]
    history["titles"] = history["titles"][-MAX_HISTORY_ITEMS:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        LOG.error("فشل حفظ السجل: %s", exc)


def significant_words(title: str) -> set:
    words = re.findall(r"[a-zA-Z\u0600-\u06FF]{4,}", title.lower())
    return {w for w in words if w not in STOPWORDS}


# عتبة موحّدة لاعتبار خبرين "نفس الحدث" -- خُفّضت من 0.6 إلى 0.45 لأن عناوين
# مصادر مختلفة (Sky/BBC/ESPN/Google News) عن نفس الحدث غالباً تتشابه جزئياً فقط
# وليست متطابقة حرفياً (دليل حقيقي: 3 صياغات مختلفة تماماً لنفس مباراة
# أرسنال-جيرونا نُشرت 3 مرات لأن التداخل بينها كان أقل من 0.6).
SIMILARITY_THRESHOLD = 0.45


def title_similarity_ratio(title_a: str, title_b: str) -> float:
    """نسبة تداخل الكلمات الدالة بين عنوانين -- أساس مشترك لكشف التكرار والتجميع."""
    words_a = significant_words(title_a)
    words_b = significant_words(title_b)
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / min(len(words_a), len(words_b))


def is_topic_repeated(new_title: str, posted_titles: list) -> bool:
    if len(significant_words(new_title)) < 2:
        return False
    return any(title_similarity_ratio(new_title, pt) >= SIMILARITY_THRESHOLD for pt in posted_titles)


def _same_story(article_a: dict, article_b: dict) -> bool:
    """
    يقرر إن كان مقالان يغطيان نفس الحدث. تداخل الكلمات وحده غير كافٍ (مُختبَر
    فعلياً: 3 صياغات مختلفة تماماً لنفس مباراة أرسنال-جيرونا سجّلت تداخلاً بين
    0.28 و0.43 فقط -- تحت عتبة SIMILARITY_THRESHOLD). لذلك نضيف إشارة إضافية:
    نفس النادي/اللاعب المستخرج من العنوانين + تداخل ولو جزئي (0.2 فأكثر) --
    يلتقط حالات "Arsenal beat Girona" مقابل "Tzolis makes Arsenal debut in
    Girona clash" حيث الصياغة مختلفة تماماً لكن الحدث واحد. نشترط أيضاً كلمتين
    مشتركتين على الأقل (وليس فقط اسم النادي نفسه) لتفادي دمج قصتين مختلفتين
    تماماً تشتركان فقط باسم النادي (مُختبَر: "صفقة انتقال جديدة" مقابل "تكريم
    أسطورة سابقة" -- نفس النادي، حدثان مختلفان كلياً، لا يجب دمجهما).
    """
    words_a = significant_words(article_a["title"])
    words_b = significant_words(article_b["title"])
    if not words_a or not words_b:
        return False
    overlap = words_a & words_b
    ratio = len(overlap) / min(len(words_a), len(words_b))
    if ratio >= SIMILARITY_THRESHOLD:
        return True
    entity_a = extract_entities(article_a)
    entity_b = extract_entities(article_b)
    same_entity = (
        (entity_a.get("club") and entity_a.get("club") == entity_b.get("club"))
        or (entity_a.get("player") and entity_a.get("player") == entity_b.get("player"))
    )
    return bool(same_entity and len(overlap) >= 2 and ratio >= 0.2)


def cluster_similar_articles(articles: list) -> list:
    """
    يجمّع الأخبار المتشابهة (نفس الحدث مغطّى من مصادر مختلفة) ضمن دورة الجلب
    نفسها، ويختار من كل مجموعة ممثلاً واحداً فقط -- بالأولوية القصوى لمن معه
    صورة أصلية تنجح فعلياً (وليس فقط موجودة بالحقل)، تماشياً مع فكرة: بما أن عدة
    مصادر تغطي نفس الحدث، نختار المصدر الذي نقدر نسحب صورته منه فعلياً بدل
    الاعتماد على محرك البحث الخارجي الأقل دقة. هذا يحل مشكلتي التكرار وجودة
    الصورة معاً (دليل حقيقي: نفس مباراة أرسنال-جيرونا نُشرت 3 مرات بنتائج صور
    متفاوتة الجودة لأن كل نسخة عولجت كخبر مستقل).
    """
    clusters: list = []
    for article in articles:
        placed = False
        for cluster in clusters:
            if _same_story(article, cluster[0]):
                cluster.append(article)
                placed = True
                break
        if not placed:
            clusters.append([article])

    representatives = []
    for cluster in clusters:
        if len(cluster) == 1:
            representatives.append(cluster[0])
            continue
        LOG.info("🔗 تجميع %d مقالات عن نفس الحدث على الأرجح: %s", len(cluster), cluster[0]["title"][:60])
        best = None
        for candidate in sorted(cluster, key=calculate_priority, reverse=True):
            img_url = candidate.get("image")
            if img_url and not is_channel_image_url(img_url):
                img = download_image(img_url)
                if img:
                    best = candidate
                    LOG.info("✅ اختيار المصدر الذي نجحت صورته الأصلية: %s", candidate["link"])
                    break
        if best is None:
            best = max(cluster, key=calculate_priority)
            LOG.info("⚠️ لا صورة أصلية صالحة بين المصادر المتشابهة -- اختيار الأعلى أولوية")
        representatives.append(best)
    return representatives

# ==============================================================================
# دوال Git
# ==============================================================================

def git_commit_and_push():
    if not GIT_AUTO_PUSH:
        LOG.info("GIT_AUTO_PUSH معطّل — تخطي الحفظ في Git.")
        return
    try:
        subprocess.run(["git", "config", "user.name", "pul7sar-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "pul7sar-bot@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", HISTORY_FILE], check=True)
        status = subprocess.run(["git", "status", "--porcelain", HISTORY_FILE],
                                 capture_output=True, text=True, check=True)
        if not status.stdout.strip():
            LOG.info("لا تغييرات في السجل — لا حاجة لعملية commit.")
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        subprocess.run(["git", "commit", "-m", f"chore: update posted history ({ts})"], check=True)
        subprocess.run(["git", "push"], check=True)
        LOG.info("تم دفع السجل إلى المستودع بنجاح.")
    except subprocess.CalledProcessError as exc:
        LOG.error("فشلت عملية Git: %s | %s", exc, exc.stderr)

# ==============================================================================
# دوال جلب الأخبار
# ==============================================================================

def fetch_articles(posted_links_set, posted_titles):
    articles = []
    for url in RSS_URLS:
        def _fetch(u=url):
            r = requests.get(u, headers=HTTP_HEADERS, timeout=15)
            r.raise_for_status()
            return feedparser.parse(r.content)

        feed = retry(_fetch, attempts=2, what=f"جلب RSS من {url}")
        if not feed:
            continue

        for entry in feed.entries[:12]:
            link = entry.get("link", entry.get("id", ""))
            title = entry.get("title", "")
            if not link or not title:
                continue

            if not getattr(entry, "published_parsed", None):
                continue
            pub_ts = time.mktime(entry.published_parsed)
            if time.time() - pub_ts > ARTICLE_MAX_AGE_HOURS * 3600:
                continue

            if any(kw in title.lower() for kw in SKIP_KEYWORDS):
                continue
            if link in posted_links_set or is_topic_repeated(title, posted_titles):
                continue

            summary_html = entry.get("summary", title)
            soup = BeautifulSoup(summary_html, "html.parser")
            clean_summary = soup.get_text()

            image_url = None
            if getattr(entry, "media_content", None):
                image_url = entry.media_content[0].get("url")
            elif getattr(entry, "media_thumbnail", None):
                image_url = entry.media_thumbnail[0].get("url")
            else:
                img_tag = soup.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag.get("src")

            articles.append({
                "title": title, "summary": clean_summary, "link": link, "image": image_url,
                # نكشف الرياضة من مسار الرابط لحظة الجلب -- الخلاصة نفسها مختلطة (كل
                # الرياضات) رغم أن اسمها "12040" قد يوحي بأنها كرة قدم فقط؛ لهذا
                # نعتمد على مسار كل رابط مقال على حدة وليس على مصدر الخلاصة.
                "sport": detect_sport_from_url(link),
            })

    LOG.info("تم العثور على %d مقال صالح بعد الفلترة.", len(articles))
    return articles

# ==============================================================================
# دوال توليد المحتوى عبر Groq
# ==============================================================================

def call_groq(prompt: str):
    def _call():
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "openai/gpt-oss-120b", "temperature": 0.6,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    return retry(_call, attempts=3, what="توليد المحتوى عبر Groq")

# ==============================================================================
# المرحلة 3 — سلسلة المعالجة العربية بـ7 طبقات فعلية (راجع Master Plan §2.4)
# ==============================================================================
# الفرق الجوهري عن التصميم السابق: كل طبقة هنا تُصلح النص لا ترفضه، والبوابة
# النهائية (Layer 7) وحدها مخوَّلة برفض المنشور بالكامل -- وفقط بعد استنفاد كل
# محاولات الإصلاح. سابقاً كانت validate_arabic_text تُسقِط الخبر كاملاً بمجرد
# سطر واحد فيه مشكلة، حتى لو باقي الخبر ممتاز -- وهو ما كان يُهدر أخباراً صالحة.

# نطاقات يونيكود لأنظمة كتابة أخرى غير عربية مطلقاً (تُستخدم بالطبقة 2 والبوابة
# النهائية 7). سابقاً كان الفلتر يستهدف الأحرف اللاتينية فقط.
NON_ARABIC_SCRIPT_PATTERN = re.compile(
    "["
    "\u0400-\u04FF"   # سيريلي
    "\u0370-\u03FF"   # يوناني
    "\u0590-\u05FF"   # عبري
    "\u4E00-\u9FFF"   # صيني/ياباني (كانجي/هانزي)
    "\u3040-\u30FF"   # ياباني (هيراغانا/كاتاكانا)
    "\uAC00-\uD7AF"   # كوري (هانغل)
    "\u0900-\u097F"   # هندي (ديفاناغري)
    "\u0250-\u02AF"   # رموز صوتية IPA
    "\uFFFD"          # رمز تلف الترميز
    "]"
)


def layer1_raw_clean(text: str) -> str:
    """الطبقة 1: تنظيف النص الخام -- رموز ماركداون، ترقيم عربي موحّد، مسافات زائدة."""
    text = re.sub(r"[*~`]+", "", text)
    text = text.replace('(', '（').replace(')', '）')
    text = text.replace(',', '،')
    text = text.replace('?', '؟')
    text = re.sub(r'\.([^\s.])', r'. \1', text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def layer2_strip_non_arabic_script(text: str) -> str:
    """
    الطبقة 2: إزالة أي محارف من أنظمة كتابة أخرى (سيريلي/يوناني/عبري/صيني/
    ياباني/كوري/هندي/رموز IPA/رمز تلف الترميز) بالإضافة للكلمات اللاتينية غير
    المسموحة -- مع استثناء الروابط والهاشتاقات المتعمَّدة (مثل #PUL7SAR). الأرقام
    محمية دائماً (ضرورية لأسعار الانتقالات والنتائج، لا تُحذف أبداً).
    """
    text = NON_ARABIC_SCRIPT_PATTERN.sub("", text)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("#") or "http://" in line or "https://" in line:
            cleaned_lines.append(line)
            continue
        tokens = line.split(" ")
        kept = []
        for tok in tokens:
            core = tok.strip(".,!؟?،؛:")
            if core and re.search(r"[a-zA-Z]", core) and not core.startswith("#"):
                continue
            kept.append(tok)
        cleaned_line = re.sub(r"\s{2,}", " ", " ".join(kept)).strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines).strip()


def layer3_fix_broken_words(text: str) -> str:
    """
    الطبقة 3: كشف/إصلاح الكلمات غير المنطقية. تكرار حرف عربي واحد 3 مرات فأكثر
    (أثر شائع لتلف الترميز أو خطأ OCR، مثل "الااااا") يُختزل لحرف واحد بدل حذف
    الكلمة كاملة. الكلمات الأطول من 25 حرفاً (نادرة جداً بالعربية الفصحى، غالباً
    محارف ملتصقة بلا مسافات بسبب خطأ استخراج نص) تُحذف لأنها غير قابلة للإصلاح.
    """
    def _shrink_repeats(word: str) -> str:
        return re.sub(r"([\u0600-\u06FF])\1{2,}", r"\1", word)

    fixed_words = []
    for w in text.split(" "):
        core = w.strip(".,!؟?،؛:\n")
        if core and len(core) > 25 and not core.startswith("#") and "http" not in core:
            LOG.info("🚫 Layer3: حذف كلمة غير منطقية (طول شاذ %d حرفاً): %s...", len(core), core[:15])
            continue
        fixed_words.append(_shrink_repeats(w))
    return " ".join(fixed_words)


def layer4_spelling_correction(text: str) -> str:
    """الطبقة 4: تصحيح إملائي فقط عبر تمرير Groq ضيق النطاق (لا يغيّر المعنى/الأسلوب/الطول)."""
    prompt = (
        "صحح الأخطاء الإملائية فقط في النص العربي التالي، دون تغيير المعنى أو "
        "الأسلوب أو ترتيب الجمل أو حذف أي كلمة أو رقم. أعد النص المصحَّح فقط بلا "
        "أي مقدمة أو تعليق إضافي:\n\n" + text
    )
    corrected = call_groq(prompt)
    return corrected.strip() if corrected else text


def layer5_grammar_correction(text: str) -> str:
    """الطبقة 5: مراجعة نحوية فقط (تطابق الجملة الفعلية/الاسمية، التذكير/التأنيث) عبر Groq."""
    prompt = (
        "راجع النص العربي التالي نحوياً فقط (تطابق الجملة الفعلية والاسمية، "
        "التذكير والتأنيث، الجمع والمفرد) دون تغيير المعنى أو الأسلوب أو حذف أي "
        "كلمة أو رقم. أعد النص المصحَّح فقط بلا أي مقدمة أو تعليق إضافي:\n\n" + text
    )
    corrected = call_groq(prompt)
    return corrected.strip() if corrected else text


def layer6_editorial_style(text: str) -> str:
    """
    الطبقة 6: تحسين الأسلوب الصحفي -- جمل أوضح، حذف الحشو والتكرار، مع الحفاظ
    الكامل على كل حقيقة/رقم/اسم كما هو. لا يقصّر النص جذرياً هنا -- التقصير
    لصيغة "خبر مختصر + تعليق أول" مسؤولية generate_short_content (المرحلة 4)،
    التي تطلب من Groq الصياغة القصيرة مباشرة بدل تشذيب نص طويل بعد كتابته.
    """
    prompt = (
        "حسّن الأسلوب الصحفي للنص العربي التالي: اجعل الجمل أوضح وأقصر حيثما "
        "أمكن، واحذف أي حشو أو تكرار غير ضروري، دون حذف أي حقيقة أو رقم أو اسم "
        "مذكور ودون تغيير المعنى العام أو تقليص طول النص بشكل كبير. أعد النص فقط "
        "بلا أي مقدمة أو تعليق إضافي:\n\n" + text
    )
    styled = call_groq(prompt)
    return styled.strip() if styled else text


def layer7_final_qa_gate(text: str) -> bool:
    """
    الطبقة 7: المراجعة النهائية -- بوابة الرفض الوحيدة في كامل الخط، وتُشغَّل فقط
    بعد محاولات الإصلاح بالطبقات 1-6 (وليس عند أول عيب كما كان سابقاً).
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    total_chars = len(re.sub(r'[#\s]', '', text))
    if total_chars > 0 and arabic_chars / total_chars < 0.3:
        LOG.error("Layer7: نسبة الأحرف العربية منخفضة جداً بعد كل محاولات الإصلاح")
        return False
    if re.search(r'[\*\#\~\_\`]{2,}', text):
        LOG.error("Layer7: رموز ماركداون متبقية بعد التصحيح")
        return False
    for line in text.split('\n'):
        if line.strip().startswith('#'):
            continue
        if re.search(r'[a-zA-Z]{4,}', line):
            LOG.error("Layer7: كلمات لاتينية طويلة متبقية بعد التصحيح")
            return False
    if '\ufffd' in text:
        LOG.error("Layer7: رمز تلف ترميز متبقٍ بعد التصحيح")
        return False
    if NON_ARABIC_SCRIPT_PATTERN.search(text):
        LOG.error("Layer7: محارف من نظام كتابة غير عربي متبقية بعد التصحيح")
        return False
    return True


def ensure_perfect_arabic(text: str, max_length: int = 1020) -> str:
    """
    ينفّذ سلسلة المعالجة السباعية كاملة (الطبقات 1-7، بما فيها تصحيحات Groq
    الثلاث). يُستخدم للنص الأساسي المنشور (تعليق الصورة) حيث الجودة اللغوية
    أهم اعتبار. max_length قابل للتخصيص لأن حدود تليجرام تختلف بين تعليق
    الصورة (1024 حرفاً) ورسالة التعليق الأول (4096 حرفاً).
    """
    if not text:
        LOG.critical("النص فارغ")
        return None

    text = layer1_raw_clean(text)
    text = layer2_strip_non_arabic_script(text)
    text = layer3_fix_broken_words(text)
    text = layer4_spelling_correction(text)
    text = layer5_grammar_correction(text)
    text = layer6_editorial_style(text)
    # طبقات Groq (4-6) قد تُعيد رموز ماركداون أو مسافات زائدة من عندها -- تنظيف
    # أخير سريع بنفس منطق الطبقة 1 قبل بوابة الفحص، بدل تكراره داخل كل طبقة.
    text = layer1_raw_clean(text)

    if not layer7_final_qa_gate(text):
        LOG.critical("النص لم يجتز المراجعة النهائية رغم كل محاولات الإصلاح - سيُرفض المنشور")
        return None

    if len(text) > max_length:
        text = text[:max_length - 3].rstrip() + "..."
    LOG.info("✅ النص اجتاز الطبقات السبع بنجاح")
    return text


def ensure_arabic_light(text: str, max_length: int = 4000) -> str:
    """
    نسخة مخفَّفة من سلسلة المعالجة -- طبقات 1-3 الحتمية + بوابة الفحص 7 فقط،
    بلا استدعاءات Groq إضافية (4-6). تُستخدم للتحليل المطوّل (التعليق الأول،
    المرحلة 4) حيث الأولوية لسلامة النص الأساسية لا الصقل الأسلوبي الكامل --
    فشل هذا النص لا يُسقط المنشور بأكمله، بل يُلغى نشر التعليق الأول فقط
    (راجع publish_single_article).
    """
    if not text:
        return None
    text = layer1_raw_clean(text)
    text = layer2_strip_non_arabic_script(text)
    text = layer3_fix_broken_words(text)
    if not layer7_final_qa_gate(text):
        LOG.warning("التحليل المطوّل لم يجتز الفحص النهائي -- سيُنشر الخبر بلا تعليق أول")
        return None
    if len(text) > max_length:
        text = text[:max_length - 3].rstrip() + "..."
    return text

# ==============================================================================
# دوال الصور ومصادرها
# ==============================================================================

def download_image(url: str, require_landscape: bool = True):
    def _get():
        r = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        if img.size[0] < 600:
            raise ValueError("الصورة صغيرة جداً")
        if require_landscape:
            ratio = img.size[0] / img.size[1]
            if ratio < MIN_LANDSCAPE_RATIO:
                LOG.info("تجاهل صورة عمودية/شبه مربعة (نسبة %.2f)", ratio)
                return None
        return img
    return retry(_get, attempts=2, what=f"تحميل صورة")


# ==============================================================================
# الشعار — إعدادات ثابتة (لا تُغيَّر بين الصور مهما كان مصدرها)
# ==============================================================================
# القرار الهندسي: الشعار يُلصق حصراً على القماشة النهائية 1280x720 داخل
# build_final_image() -- وليس على الصورة الخام قبل القص/التحجيم. هذا يضمن أن
# الحجم/الموضع/الشفافية/الهوامش ثابتة تماماً في كل صورة تُنشر، بغض النظر عن أبعاد
# الصورة المصدر. (السبب الجذري السابق لتذبذب الشعار وظهور "أثر إزالة ملصق":
# كان اللصق يتم على الصورة بأبعادها الأصلية قبل ImageOps.fit، فيعيد القص/التحجيم
# حساب موضع وحجم كل بكسل بما فيها الشعار الملصَق مسبقاً — راجع Master Plan §2.2)
WATERMARK_WIDTH = 170
WATERMARK_MARGIN = 24


def place_watermark_fixed(canvas_rgba):
    """
    يضع الشعار بحجم/موضع/هوامش/دقة ثابتة تماماً على القماشة النهائية الجاهزة فقط.
    يُستدعى مرة واحدة حصراً من build_final_image() بعد اكتمال القص والتحجيم إلى
    1280x720 -- هذا هو الإصلاح الجذري لمشكلتي "الشعار غير الثابت" و"أثر إزالة
    الملصق" في آنٍ واحد.
    """
    if not os.path.exists(LOGO_PATH):
        LOG.warning("⚠️ ملف الشعار غير موجود - سيُنشر بدون علامة مائية")
        return canvas_rgba
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        ratio = WATERMARK_WIDTH / logo.size[0]
        logo_h = int(logo.size[1] * ratio)
        logo = logo.resize((WATERMARK_WIDTH, logo_h), Image.Resampling.LANCZOS)

        pos_x, pos_y = WATERMARK_MARGIN, WATERMARK_MARGIN

        # لصق الشعار مباشرة بشفافيته الأصلية فقط -- بلا أي ظل أو مستطيل خلفية
        # اصطناعي. طُلب صراحة عدم إظهار أي "مستطيل أو خيال وهمي" حول الشعار:
        # الشفافية الحقيقية للـ PNG (logo.png) هي الفاصل الوحيد بين الشعار والصورة.
        canvas_rgba.alpha_composite(logo, dest=(pos_x, pos_y))

        LOG.info("✅ تم وضع الشعار بحجم ثابت %dpx عند (%d, %d)", WATERMARK_WIDTH, pos_x, pos_y)
    except Exception as e:
        LOG.warning(f"⚠️ فشل وضع الشعار: {e}")
    return canvas_rgba


# تحويل قيم "strSport" التي تُرجعها TheSportsDB إلى تصنيفنا الموحّد للرياضة
THESPORTSDB_SPORT_MAP = {
    "soccer": "football", "cricket": "cricket", "rugby union": "rugby", "rugby league": "rugby",
    "netball": "netball", "tennis": "tennis", "golf": "golf", "motorsport": "motorsport",
    "formula 1": "motorsport", "basketball": "basketball", "ice hockey": "hockey",
    "field hockey": "hockey", "boxing": "boxing", "athletics": "athletics", "cycling": "cycling",
    "swimming": "swimming", "gymnastics": "gymnastics", "darts": "darts", "snooker": "snooker",
}


def search_thesportsdb_image(entities: dict):
    """
    البحث عن صور لاعبين/أندية من TheSportsDB. المفتاح المجاني: 3.
    يستخدم حقل "strSport" الذي تُرجعه TheSportsDB نفسها كفلتر حاسم -- وهو أدق
    إشارة رياضة متاحة (تأتي من قاعدة بيانات منظّمة وليست تخميناً نصياً)، ويُطبَّق
    قبل قبول أي نتيجة (كان هذا المصدر سابقاً يقبل أول نتيجة بلا أي تحقق).
    """
    query = entities.get("query")
    if not query:
        return None
    entity_sport = entities.get("sport")

    def _matches_sport(str_sport: str) -> bool:
        if not entity_sport:
            return True
        mapped = THESPORTSDB_SPORT_MAP.get((str_sport or "").strip().lower())
        return mapped is None or mapped == entity_sport

    def _search():
        # البحث عن لاعب
        url = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_API_KEY}/searchplayers.php?p={quote(query)}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            for player in (r.json().get("player") or []):
                if not _matches_sport(player.get("strSport")):
                    LOG.info("🚫 TheSportsDB: تجاهل لاعب رياضته '%s' لا تطابق رياضة الخبر '%s'",
                             player.get("strSport"), entity_sport)
                    continue
                img_url = player.get("strCutout") or player.get("strThumb") or player.get("strRender")
                if img_url and img_url.startswith("http"):
                    return img_url
        except Exception:
            pass

        # البحث عن نادي
        url2 = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_API_KEY}/searchteams.php?t={quote(query)}"
        try:
            r2 = requests.get(url2, timeout=10)
            r2.raise_for_status()
            for team in (r2.json().get("teams") or []):
                if not _matches_sport(team.get("strSport")):
                    LOG.info("🚫 TheSportsDB: تجاهل فريق رياضته '%s' لا تطابق رياضة الخبر '%s'",
                             team.get("strSport"), entity_sport)
                    continue
                img_url = team.get("strTeamBadge") or team.get("strTeamJersey") or team.get("strTeamLogo")
                if img_url and img_url.startswith("http"):
                    return img_url
        except Exception:
            pass

        return None

    img_url = retry(_search, attempts=2, what=f"بحث TheSportsDB عن '{query}'")
    if not img_url:
        return None
    return download_image(img_url)


def search_google_images_efficient(entities: dict):
    query = entities.get("search_query") or entities.get("query")
    if not query or not GOOGLE_API_KEY or not GOOGLE_CSE_CX:
        return None
    def _search():
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_CX, "q": query,
                  "searchType": "image", "num": 5, "safe": "active"}
        r = requests.get(url, params=params, headers=HTTP_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("items", [])
    results = retry(_search, attempts=2, what=f"بحث Google عن '{query}'")
    if not results:
        return None
    for item in results:
        img_url = item.get("link")
        if not img_url:
            continue
        # تحقق الصلة قبل حتى تنزيل الصورة (يوفر رصيد الشبكة): عنوان النتيجة +
        # مقتطف السياق (title/snippet) يُقارَنان بكيانات الخبر ونوع رياضته.
        candidate_text = f"{item.get('title', '')} {item.get('snippet', '')}"
        if not is_candidate_relevant(candidate_text, entities):
            LOG.info("🚫 Google: تجاهل نتيجة غير ذات صلة: %s", item.get("title"))
            continue
        img = download_image(img_url)
        if img and img.size[0] >= 800 and img.size[1] >= 500:
            LOG.info("✅ تم جلب صورة من Google")
            return img
    return None


def search_wikimedia_commons(entities: dict):
    query = entities.get("search_query") or entities.get("query")
    if not query:
        return None
    def _search():
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "list": "search", "srnamespace": 6,
                    "srsearch": f"{query} filetype:bitmap", "srlimit": 15, "format": "json"},
            headers=HTTP_HEADERS, timeout=10,
        )
        r.raise_for_status()
        return r.json().get("query", {}).get("search", [])
    results = retry(_search, attempts=2, what=f"بحث Wikimedia Commons عن '{query}'")
    if not results:
        return None
    # فلترة الصلة أولاً على عناوين الملفات المرشحة (رخيصة، قبل أي تحميل شبكي)،
    # ثم عشوائية بين ما تبقّى فقط -- كان الترتيب سابقاً عشوائياً بلا أي فلترة.
    relevant = [item for item in results if is_candidate_relevant(item.get("title", ""), entities)]
    if not relevant:
        LOG.info("🚫 Wikimedia Commons: لا نتيجة تطابق كيانات/رياضة الخبر")
        return None
    random.shuffle(relevant)
    for item in relevant[:10]:
        title = item.get("title")
        if not title:
            continue
        def _get_url(t=title):
            r2 = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={"action": "query", "titles": t, "prop": "imageinfo",
                        "iiprop": "url", "format": "json"},
                headers=HTTP_HEADERS, timeout=10,
            )
            r2.raise_for_status()
            pages = r2.json().get("query", {}).get("pages", {})
            for page in pages.values():
                infos = page.get("imageinfo")
                if infos:
                    return infos[0].get("url")
            return None
        img_url = retry(_get_url, attempts=1, what=f"رابط صورة Commons")
        if not img_url:
            continue
        img = download_image(img_url)
        if img and img.size[0] >= 800:
            return img
    return None


def search_ddgs_image(entities: dict, query: str, require_relevance: bool = True):
    def _search():
        with DDGS() as ddgs:
            return list(ddgs.images(query, max_results=20))
    results = retry(_search, attempts=2, what=f"بحث DDG عن '{query}'")
    if not results:
        return None
    trusted = [r for r in results if is_trusted_domain(r.get("image", ""))]
    if not trusted:
        return None
    if require_relevance:
        candidates = [r for r in trusted if is_candidate_relevant(r.get("title", ""), entities)]
    else:
        candidates = trusted
    random.shuffle(candidates)
    for r in candidates:
        img_url = r.get("image")
        if not img_url:
            continue
        img = download_image(img_url)
        if img and img.size[0] >= 800 and img.size[1] >= 500:
            return img
    return None


def is_trusted_domain(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower()
        return any(domain == d or domain.endswith("." + d) for d in TRUSTED_IMAGE_DOMAINS)
    except Exception:
        return False


def is_channel_image_url(url: str) -> bool:
    """التحقق إذا كانت الصورة من قناة تلفزيونية (نستبدلها)"""
    if not url:
        return False
    return any(domain in url for domain in CHANNEL_LOGO_DOMAINS)


def get_best_image_for_article(article: dict) -> Image.Image:
    """
    الحصول على أفضل صورة للخبر من جميع المصادر، بالاعتماد على استخراج الكيانات
    (لاعب/نادٍ/نوع رياضة) والتحقق من صلة كل نتيجة قبل قبولها (راجع Master Plan
    §2.3). ملاحظة حاسمة: أُزيل مسار "DDGS Generic" الذي كان يقبل أي صورة بلا أي
    شرط صلة كملاذ أخير -- هذا كان يخالف صراحة شرط "ممنوع صورة عشوائية عند الفشل".
    الآن: لو لم تُوجد أي صورة تجتاز فحص الصلة من أي مصدر، تُعاد None ليستخدم
    المستدعي البطاقة الاحتياطية بدلاً من صورة غير متحقق من صلتها.
    """
    entities = extract_entities(article)
    if not entities.get("query"):
        LOG.warning("لا يوجد استعلام بحث صالح (لا لاعب/نادٍ/كلمات دالة بالعنوان) -- سيُستخدم البطاقة الاحتياطية")
        return None

    image_sources = [
        ("TheSportsDB", lambda: search_thesportsdb_image(entities)),
        ("Google", lambda: search_google_images_efficient(entities)),
        ("Wikimedia Commons", lambda: search_wikimedia_commons(entities)),
        ("DDGS Trusted", lambda: search_ddgs_image(
            entities, entities.get("search_query") or entities["query"], require_relevance=True)),
    ]

    for source_name, source_fn in image_sources:
        LOG.info(f"🔍 محاولة جلب صورة من {source_name}...")
        img = source_fn()
        if img:
            LOG.info(f"✅ تم جلب صورة من {source_name}")
            # لا نضع الشعار هنا عمداً -- يُلصق مرة واحدة فقط داخل build_final_image()
            # بعد القص/التحجيم النهائي (راجع الإصلاح الجذري في place_watermark_fixed أعلاه).
            return img

    LOG.info("🚫 لم تُوجد صورة تجتاز فحص الصلة من أي مصدر -- سيُستخدم البطاقة الاحتياطية بدل صورة عشوائية")
    return None

# ==============================================================================
# البطاقة الاحتياطية الاحترافية
# ==============================================================================

def build_placeholder_professional():
    """بطاقة احتياطية بتصميم احترافي وأنيق"""
    img = Image.new("RGB", (1280, 720), (10, 22, 40))
    draw = ImageDraw.Draw(img, "RGBA")

    # تدرج خلفية
    for y in range(720):
        shade = int(10 + (y / 720) * 30)
        draw.line([(0, y), (1280, y)], fill=(shade, shade + 10, shade + 30))

    # إطار ذهبي داخلي
    draw.rectangle([(40, 40), (1240, 680)], outline=(255, 215, 0, 150), width=2)
    draw.rectangle([(50, 50), (1230, 670)], outline=(255, 215, 0, 50), width=1)

    # خطوط جانبية حمراء (لون العلامة التجارية)
    draw.rectangle([(40, 40), (60, 680)], fill=(220, 38, 38, 200))
    draw.rectangle([(1220, 40), (1240, 680)], fill=(220, 38, 38, 200))

    # شعار كبير في المنتصف
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 280
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, ((1280 - logo_w) // 2, 210), logo)
        except Exception:
            pass

    # نص SPORTS NEWS
    font_big = _load_bold_font(40)
    draw.text((640, 370), "SPORTS NEWS", font=font_big, fill=(255, 255, 255, 220), anchor="mm")

    # خط فاصل ذهبي
    draw.line([(400, 420), (880, 420)], fill=(255, 215, 0, 120), width=1)

    # نص تحت
    font_medium = _load_bold_font(24)
    draw.text((640, 460), "أخبار رياضية دقيقة ومصداقية عالية", font=font_medium,
              fill=(180, 190, 210, 180), anchor="mm")

    # هاشتاق
    font_small = _load_bold_font(28)
    draw.text((640, 530), "#PUL7SAR", font=font_small, fill=(255, 215, 0, 200), anchor="mm")

    return img.convert("RGB")

# ==============================================================================
# دوال نظام الأولويات
# ==============================================================================

def get_fame_score(text: str) -> int:
    text_lower = text.lower()
    max_score = 0
    for name, score in FAME_SCORES.items():
        if name in text_lower:
            max_score = max(max_score, score)
    if max_score == 0:
        big_clubs = ["real madrid", "barcelona", "bayern", "man city", "liverpool", "psg",
                     "manchester united", "chelsea", "arsenal", "juventus", "ac milan", "inter"]
        for club in big_clubs:
            if club in text_lower:
                max_score = max(max_score, 6)
                break
    return max_score


def get_event_score(text: str) -> int:
    text_lower = text.lower()
    max_score = 5
    for keyword, score in EVENT_KEYWORDS.items():
        if keyword in text_lower:
            max_score = max(max_score, score)
    return max_score


def get_rarity_score(text: str) -> int:
    text_lower = text.lower()
    max_score = 5
    for keyword, score in RARITY_KEYWORDS.items():
        if keyword in text_lower:
            max_score = max(max_score, score)
    return max_score


def calculate_priority(article: dict) -> float:
    title = article.get("title", "")
    summary = article.get("summary", "")
    text = title + " " + summary
    fame = get_fame_score(text)
    event = get_event_score(text)
    rarity = get_rarity_score(text)
    priority = (fame * 2) + (event * 3) + (rarity * 1.5)
    LOG.info(f"📊 تقييم الخبر: شهرة={fame}, حدث={event}, ندرة={rarity} → أولوية={priority:.1f}")
    return priority


def sort_articles_by_priority(articles: list) -> list:
    for article in articles:
        article["_priority"] = calculate_priority(article)
    return sorted(articles, key=lambda x: x.get("_priority", 0), reverse=True)

# ==============================================================================
# دوال الصورة النهائية والإرسال
# ==============================================================================

def build_final_image(base_img):
    """
    يبني الصورة النهائية بالقياس الثابت 1280x720: يقص/يحجّم الصورة الخام أولاً،
    ثم يضع الشعار في الخطوة الأخيرة فقط على القماشة الجاهزة (راجع
    place_watermark_fixed أعلاه للسبب الهندسي). يُطبَّق على كل الصور مهما كان
    مصدرها -- بما فيها البطاقة الاحتياطية -- لضمان علامة مائية ثابتة دائماً.
    """
    canvas = Image.new("RGB", (1280, 720), (15, 23, 42))
    bg = ImageOps.fit(base_img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas.paste(bg, (0, 0))
    canvas = canvas.convert("RGBA")

    canvas = place_watermark_fixed(canvas)

    canvas.convert("RGB").save(FINAL_IMAGE_PATH, quality=95)


def send_telegram_photo(caption: str):
    """يرسل الصورة مع تعليقها، ويعيد معرّف الرسالة (message_id) لاستخدامه لاحقاً
    عند نشر التعليق الأول كردّ على هذه الرسالة بالتحديد -- أو None عند الفشل."""
    if len(caption) > 1024:
        caption = caption[:1021].rstrip() + "..."

    def _send():
        with open(FINAL_IMAGE_PATH, "rb") as photo_file:
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"photo": photo_file},
                timeout=30,
            )
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok"):
            raise RuntimeError(payload)
        return payload

    payload = retry(_send, attempts=3, what="إرسال الصورة إلى تليجرام")
    if not payload:
        return None
    return payload.get("result", {}).get("message_id")


def send_telegram_first_comment(reply_to_message_id: int, text: str) -> bool:
    """
    ينشر التحليل المطوّل كتعليق أول -- رد مباشر (reply) على رسالة الصورة نفسها،
    وليس رسالة منفصلة عشوائية بالقناة (راجع طلب المستخدم الأصلي: "ينشر كتعليق
    أول أسفل المنشور في فيسبوك" -- على تليجرام المكافئ الأقرب هو رد على الرسالة).
    """
    if len(text) > 4096:
        text = text[:4093].rstrip() + "..."

    def _send():
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "reply_to_message_id": reply_to_message_id},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok"):
            raise RuntimeError(payload)
        return payload

    return retry(_send, attempts=2, what="إرسال التعليق الأول إلى تليجرام") is not None

# ==============================================================================
# المرحلة 4 — خبر مختصر + تعليق أول (راجع Master Plan §2.5 وطلب المستخدم الأصلي)
# ==============================================================================
# بدل توليد مقال طويل واحد ثم عدم فعل شيء بطوله، نطلب من Groq مباشرة نموذج
# محتوى بحقلين منفصلين: short_post (ينشر كتعليق الصورة، أسلوب فوتكس/محمد عواد:
# عنوان جذاب+افتتاحية قوية+اختصار شديد) وlong_analysis (ينشر كتعليق أول منفصل
# أسفل المنشور، بلا حذف أي تحليل أو شرح). التصميم قائم على قاموس content بسيط
# {short_post, long_analysis} حتى يسهل لاحقاً بناء محوّلات نشر لمنصات أخرى
# (X, Threads) تستهلك نفس النموذج دون تغيير منطق التوليد.

def generate_short_content(article: dict) -> dict:
    """
    يولّد محتوى الخبر بصيغة JSON منظّمة عبر Groq. short_post قصير جداً (3-5
    أسطر)، يبدأ بإيموجي + جملة افتتاحية قوية تجذب القارئ خلال أول ثانيتين،
    بأسلوب صحفي يحاكي منصة فوتكس والصحفي محمد عواد -- بلا إطالة ولا حشو ولا
    تكرار. long_analysis يحمل الشرح/التحليل المطوّل الذي لا يُحذف، بل يُنشر
    منفصلاً كتعليق أول.
    """
    prompt_lines = [
        "أنت محرر رياضي محترف في منصة PUL7SAR، أسلوبك يحاكي منصة فوتكس والصحفي محمد عواد:",
        "عنوان جذاب، افتتاحية قوية، اختصار شديد، احترافية، بلا إطالة ولا حشو ولا تكرار.",
        "لغة عربية فصحى سليمة تماماً، بلا أي خطأ إملائي أو نحوي، وأسماء اللاعبين/الأندية صحيحة.",
        "",
        "الخبر:",
        "العنوان: " + article.get("title", ""),
        "المحتوى: " + article.get("summary", ""),
        "",
        "أعد ردك بصيغة JSON صحيحة فقط (بلا أي نص أو ماركداون خارج الأقواس)، بهذا الشكل بالضبط:",
        "{",
        '  "short_post": "خبر مختصر جداً (3-5 أسطر كحد أقصى)، يبدأ بإيموجي مناسب (⚽ 🏆 🔥) ثم جملة',
        '   افتتاحية قوية تجذب القارئ خلال أول ثانيتين، جاهز للنشر المباشر بلا أي حشو، ينتهي بهاشتاقات',
        '   عربية مناسبة + #PUL7SAR",',
        '  "long_analysis": "شرح أو تحليل موسّع للخبر (فقرة أو فقرتين) يغطي السياق والتفاصيل',
        '   والتوقعات -- هذا المحتوى ينشر كتعليق أول منفصل، لا تحذف منه أي تحليل مفيد"',
        "}",
    ]
    prompt = "\n".join(prompt_lines)

    raw = call_groq(prompt)
    if not raw:
        return None

    # النموذج قد يضيف أسوار ماركداون حول JSON رغم التعليمات -- إزالتها قبل التحليل
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        LOG.error("فشل تحليل JSON من Groq لمحتوى الخبر المنظّم")
        return None

    if not data.get("short_post"):
        LOG.error("محتوى JSON ناقص (short_post مفقود) من Groq")
        return None

    return {"short_post": data.get("short_post", ""), "long_analysis": data.get("long_analysis", "")}

# ==============================================================================
# نشر مقال واحد
# ==============================================================================

def _render_article_legacy(article: dict) -> None:
    """Legacy image rendering path with unchanged behavior."""
    image_url = article.get("image")
    base_img = None

    if image_url and not is_channel_image_url(image_url):
        base_img = download_image(image_url)

    if base_img is None:
        base_img = get_best_image_for_article(article)

    if base_img is None:
        LOG.info("استخدام البطاقة الاحتياطية")
        base_img = build_placeholder_professional()

    build_final_image(base_img)


def publish_single_article(article: dict) -> bool:
    """نشر مقال واحد: صورة + خبر مختصر (تعليق الصورة) + تحليل مطوّل (تعليق أول)."""
    LOG.info(f"📰 نشر خبر: {article.get('title', '')[:50]}...")

    # 1. توليد المحتوى بصيغة منظّمة (المرحلة 4: خبر مختصر + تحليل منفصل)
    content = generate_short_content(article)
    if not content:
        LOG.error("فشل توليد المحتوى")
        return False

    short_post = ensure_perfect_arabic(content["short_post"], max_length=1020)
    if short_post is None:
        LOG.error("الخبر المختصر لم يجتز الفحص اللغوي - لن يتم النشر")
        return False

    # التحليل المطوّل يمر بفحص أخف (بلا استدعاءات Groq إضافية) -- فشله لا يُسقط
    # المنشور بأكمله، فقط يُلغي نشر التعليق الأول (راجع ensure_arabic_light).
    long_analysis = ensure_arabic_light(content.get("long_analysis", ""), max_length=4000)

    # 2. Phase 13: feature-flagged Visual Engine integration.
    # Initialization, rendering, and output writing intentionally share
    # the same outer production safety boundary.
    if USE_VISUAL_ENGINE:
        try:
            engine = _get_visual_engine()

            if engine is not None:
                LOG.info(
                    "Visual Engine integration path enabled — "
                    "infrastructure-only mode"
                )
                from engine.integration.article_adapter import render_article_with_engine

                engine_bytes = render_article_with_engine(
                    article,
                    engine=engine,
                )
                with open(FINAL_IMAGE_PATH, "wb") as f:
                    f.write(engine_bytes)
                LOG.info("Visual Engine rendered image successfully")
            else:
                LOG.warning(
                    "Visual Engine is None despite flag being true — "
                    "falling back to legacy"
                )
                _render_article_legacy(article)

        except Exception as exc:
            LOG.exception(
                f"Visual Engine integration failed: {exc}. "
                "Falling back to legacy renderer."
            )
            _render_article_legacy(article)
    else:
        _render_article_legacy(article)

    # 3. النشر — Telegram path remains unchanged

    message_id = send_telegram_photo(short_post)
    if not message_id:
        LOG.error("فشل النشر على تليجرام")
        return False

    # 4. التعليق الأول (المرحلة 4) -- فقط لو نجا التحليل المطوّل من الفحص
    if long_analysis:
        if send_telegram_first_comment(message_id, long_analysis):
            LOG.info("✅ نُشر التحليل المطوّل كتعليق أول")
        else:
            LOG.warning("⚠️ فشل نشر التعليق الأول -- الخبر الأساسي نُشر بنجاح رغم ذلك")

    return True

# ==============================================================================
# الدالة الرئيسية
# ==============================================================================

def main():
    if not (GROQ_KEY and BOT_TOKEN and CHAT_ID):
        LOG.critical("متغيرات البيئة الأساسية ناقصة")
        return

    if not os.path.exists(LOGO_PATH):
        LOG.warning("⚠️ ملف الشعار غير موجود")

    history = load_history()
    posted_links_set = set(history["links"])
    posted_titles = history["titles"]

    # جلب الأخبار
    articles = fetch_articles(posted_links_set, posted_titles)
    if not articles:
        LOG.info("لا توجد أخبار جديدة")
        return

    # تجميع الأخبار المتشابهة (نفس الحدث من مصادر مختلفة) قبل أي ترتيب أو نشر
    articles = cluster_similar_articles(articles)

    # ترتيب حسب الأولوية
    sorted_articles = sort_articles_by_priority(articles)

    # النشر
    published_count = 0
    for article in sorted_articles:
        priority = article.get("_priority", 0)
        if priority < 20:
            LOG.info(f"⏭️ تخطي خبر بأولوية منخفضة ({priority:.1f})")
            continue

        if publish_single_article(article):
            published_count += 1
            history["links"].append(article["link"])
            history["titles"].append(article["title"])
            save_history(history)
            git_commit_and_push()

            if published_count < len(sorted_articles):
                LOG.info(f"⏳ انتظار {POST_INTERVAL_MINUTES} دقائق قبل الخبر التالي...")
                time.sleep(POST_INTERVAL_MINUTES * 60)

    LOG.info(f"✅ تم نشر {published_count} خبر")


if __name__ == "__main__":
    main()
