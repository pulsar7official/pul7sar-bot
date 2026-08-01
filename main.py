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

GENERIC_FALLBACK_QUERY = "professional football stadium match action"

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


def is_topic_repeated(new_title: str, posted_titles: list) -> bool:
    new_words = significant_words(new_title)
    if len(new_words) < 2:
        return False
    for pt in posted_titles:
        pt_words = significant_words(pt)
        if not pt_words:
            continue
        overlap = new_words & pt_words
        ratio = len(overlap) / min(len(new_words), len(pt_words))
        if ratio >= 0.6:
            return True
    return False

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

            articles.append({"title": title, "summary": clean_summary, "link": link, "image": image_url})

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
            json={"model": "llama-3.3-70b-versatile", "temperature": 0.6,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    return retry(_call, attempts=3, what="توليد المحتوى عبر Groq")


def get_img_query_from_article(article: dict) -> str:
    """استخراج اسم للبحث عن صورة من عنوان الخبر"""
    title = article.get("title", "")
    # نبحث عن أسماء لاعبين مشهورين في العنوان
    for name in FAME_SCORES.keys():
        if name in title.lower():
            return name
    # نأخذ كلمات دالة من العنوان
    words = re.findall(r"[a-zA-Z]{4,}", title)
    if words:
        return " ".join(words[:2])
    return None

# ==============================================================================
# دوال تنقية النصوص (3 طبقات صارمة)
# ==============================================================================

def sanitize_news_text(text: str) -> str:
    text = re.sub(r"[*\~`]+", "", text)
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
    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fix_arabic_text(text: str) -> str:
    text = text.replace('(', '（').replace(')', '）')
    text = text.replace(',', '،')
    text = text.replace('?', '؟')
    text = re.sub(r'\.([^\s])', r'. \1', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def validate_arabic_text(text: str) -> bool:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    total_chars = len(re.sub(r'[#\s]', '', text))
    if total_chars > 0 and arabic_chars / total_chars < 0.3:
        LOG.error("نسبة الأحرف العربية منخفضة جداً - قد يكون النص مشوهاً")
        return False
    if re.search(r'[\*\#\~\_\`]{2,}', text):
        LOG.error("يوجد رموز ماركداون في النص")
        return False
    lines = text.split('\n')
    for line in lines:
        if line.strip().startswith('#'):
            continue
        if re.search(r'[a-zA-Z]{4,}', line):
            LOG.error("يوجد كلمات لاتينية طويلة في النص")
            return False
    if '\ufffd' in text:
        LOG.error("يوجد أحرف مشوهة (U+FFFD) في النص")
        return False
    return True


def ensure_perfect_arabic(text: str) -> str:
    if not text:
        LOG.critical("النص فارغ")
        return None
    text = sanitize_news_text(text)
    text = fix_arabic_text(text)
    if not validate_arabic_text(text):
        LOG.critical("النص فيه تشويه - سيتم رفض المنشور")
        return None
    if len(text) > 1020:
        text = text[:1017] + "..."
    LOG.info("النص سليم تماماً")
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


def search_thesportsdb_image(query: str):
    """
    البحث عن صور لاعبين/أندية من TheSportsDB
    المفتاح المجاني: 3
    """
    def _search():
        # البحث عن لاعب
        url = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_API_KEY}/searchplayers.php?p={quote(query)}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            players = data.get("player", [])
            if players:
                player = players[0]
                # نفضل الصورة المقطوعة (Cutout) لأنها أنظف
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
            data2 = r2.json()
            teams = data2.get("teams", [])
            if teams:
                team = teams[0]
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


def search_google_images_efficient(query: str):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_CX:
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
        img = download_image(img_url)
        if img and img.size[0] >= 800 and img.size[1] >= 500:
            LOG.info("✅ تم جلب صورة من Google")
            return img
    return None


def search_wikimedia_commons(query: str):
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
    random.shuffle(results)
    for item in results[:10]:
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


def search_ddgs_image(query: str, require_relevance: bool = True):
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
        candidates = [r for r in trusted if is_relevant_result(r, query)]
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


def is_relevant_result(result: dict, query: str) -> bool:
    title = (result.get("title") or "").lower()
    if not title:
        return True
    query_words = [w for w in re.findall(r"[a-zA-Z]{3,}", query.lower())]
    if not query_words:
        return True
    return any(w in title for w in query_words)


def is_channel_image_url(url: str) -> bool:
    """التحقق إذا كانت الصورة من قناة تلفزيونية (نستبدلها)"""
    if not url:
        return False
    return any(domain in url for domain in CHANNEL_LOGO_DOMAINS)


def get_best_image_for_article(article: dict) -> Image.Image:
    """الحصول على أفضل صورة للخبر من جميع المصادر"""
    img_query = get_img_query_from_article(article)
    if not img_query:
        LOG.warning("لا يوجد استعلام للبحث عن صورة")
        return None

    # قائمة مصادر الصور بالترتيب (TheSportsDB أولاً)
    image_sources = [
        ("TheSportsDB", lambda: search_thesportsdb_image(img_query)),
        ("Google", lambda: search_google_images_efficient(img_query)),
        ("Wikimedia Commons", lambda: search_wikimedia_commons(img_query)),
        ("DDGS Trusted", lambda: search_ddgs_image(img_query, require_relevance=True)),
        ("DDGS Generic", lambda: search_ddgs_image(GENERIC_FALLBACK_QUERY, require_relevance=False)),
    ]

    for source_name, source_fn in image_sources:
        LOG.info(f"🔍 محاولة جلب صورة من {source_name}...")
        img = source_fn()
        if img:
            LOG.info(f"✅ تم جلب صورة من {source_name}")
            # لا نضع الشعار هنا عمداً -- يُلصق مرة واحدة فقط داخل build_final_image()
            # بعد القص/التحجيم النهائي (راجع الإصلاح الجذري في place_watermark_fixed أعلاه).
            return img

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


def send_telegram_photo(caption: str) -> bool:
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

    return retry(_send, attempts=3, what="إرسال الصورة إلى تليجرام") is not None

# ==============================================================================
# نشر مقال واحد
# ==============================================================================

def publish_single_article(article: dict) -> bool:
    """نشر مقال واحد مع الصورة المناسبة"""
    LOG.info(f"📰 نشر خبر: {article.get('title', '')[:50]}...")

    # 1. توليد المحتوى
    prompt_lines = [
        "أنت محرر رياضي محترف في منصة PUL7SAR، تتمتع بخبرة 20 عاماً في الصحافة الرياضية العربية.",
        "",
        "مهمتك: صياغة الخبر التالي بأسلوب صحفي عربي احترافي وجذاب.",
        "",
        "تعليمات صارمة:",
        "1. اكتب بأسلوب قصصي مشوق، وليس ترجمة حرفية.",
        "2. استخدم لغة عربية فصحى سليمة، مع مراعاة القواعد النحوية والإملائية.",
        "3. ابدأ بجملة افتتاحية قوية تجذب القارئ.",
        "4. استخدم إيموجي مناسب في بداية الخبر (⚽ 🏆 🔥).",
        "5. ركز على الجوانب المثيرة والمشوقة في الخبر.",
        "6. تجنب تماماً أي أخطاء إملائية أو نحوية.",
        "7. أسماء اللاعبين والأندية يجب أن تكون مكتوبة بشكل صحيح.",
        "",
        "الخبر:",
        "العنوان: " + article.get("title", ""),
        "المحتوى: " + article.get("summary", ""),
        "",
        "الصياغة المطلوبة:",
        "- افتتاحية مثيرة (جملة أو جملتين)",
        "- عرض الأحداث بتسلسل منطقي ومشوق",
        "- خاتمة مع توقعات أو تساؤلات للجمهور",
        "- هاشتاقات مناسبة + #PUL7SAR",
        "",
        "تحذير: أي خطأ إملائي أو نحوي يعني رفض المنشور.",
    ]
    prompt = "\n".join(prompt_lines)

    ai_response = call_groq(prompt)
    if not ai_response:
        LOG.error("فشل توليد المحتوى")
        return False

    clean_text = ensure_perfect_arabic(ai_response)
    if clean_text is None:
        LOG.error("النص مشوه - لن يتم النشر")
        return False

    # 2. الحصول على الصورة
    image_url = article.get("image")
    base_img = None

    # إذا كانت الصورة من قناة تلفزيونية، نستبدلها فوراً
    # (لا نضع الشعار هنا عمداً -- يُلصق حصراً على القماشة النهائية داخل build_final_image()،
    # هذا هو الإصلاح الجذري لمشكلة تذبذب حجم/موضع الشعار، راجع Master Plan §2.2)
    if image_url and not is_channel_image_url(image_url):
        base_img = download_image(image_url)

    # إذا لم تنجح صورة المقال، نبحث في المصادر الأخرى
    if base_img is None:
        base_img = get_best_image_for_article(article)

    # إذا فشل كل شيء، نستخدم البطاقة الاحتياطية
    if base_img is None:
        LOG.info("استخدام البطاقة الاحتياطية")
        base_img = build_placeholder_professional()

    # 3. بناء الصورة النهائية والنشر
    build_final_image(base_img)

    if not send_telegram_photo(clean_text):
        LOG.error("فشل النشر على تليجرام")
        return False

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
