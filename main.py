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

HISTORY_FILE = "posted_history.json"
MAX_HISTORY_ITEMS = 300
ARTICLE_MAX_AGE_HOURS = 48
FINAL_IMAGE_PATH = "processed_image.jpg"

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PUL7SAR-Bot/2.0)"}

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

CHANNEL_LOGO_DOMAINS = ["bbci.co.uk", "skysports.com"]

LOGO_PATH = "logo.png"

MIN_LANDSCAPE_RATIO = 1.05

# ==============================================================================
# البطاقات الاحتياطية - 4 تصاميم مختلفة
# ==============================================================================

PLACEHOLDER_STYLE = 1  # 1=ملعب, 2=تلفزيون, 3=عصري, 4=بطاقة لاعب

def _load_bold_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_placeholder_style1():
    """البطاقة 1: ملعب كرة قدم"""
    img = Image.new("RGB", (1280, 720), (34, 139, 34))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(40, 40), (1240, 680)], outline=(255, 255, 255, 100), width=3)
    draw.line([(640, 40), (640, 680)], fill=(255, 255, 255, 80), width=2)
    draw.ellipse([(540, 240), (740, 480)], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([(40, 200), (160, 520)], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([(1120, 200), (1240, 520)], outline=(255, 255, 255, 80), width=2)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 200
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, ((1280 - logo_w) // 2, 240), logo)
        except Exception:
            pass
    font = _load_bold_font(36)
    draw.text((640, 490), "⚡ SPORTS NEWS ⚡", font=font, fill=(255, 255, 255, 200), anchor="mm")
    font_small = _load_bold_font(22)
    draw.text((640, 560), "#PUL7SAR", font=font_small, fill=(255, 215, 0, 200), anchor="mm")
    return img.convert("RGB")


def build_placeholder_style2():
    """البطاقة 2: شاشة تلفزيون"""
    img = Image.new("RGB", (1280, 720), (20, 20, 30))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(80, 40), (1200, 680)], outline=(100, 100, 120, 255), width=8)
    draw.rectangle([(100, 60), (1180, 600)], outline=(80, 80, 100, 255), width=2)
    draw.rectangle([(110, 70), (1170, 590)], fill=(10, 12, 25, 230))
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 120
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, (140, 85), logo)
        except Exception:
            pass
    font_big = _load_bold_font(52)
    draw.text((640, 220), "⚡ خَبَر عاجِل ⚡", font=font_big, fill=(255, 50, 50, 255), anchor="mm")
    font_medium = _load_bold_font(32)
    draw.text((640, 320), "BREAKING NEWS", font=font_medium, fill=(200, 200, 220, 200), anchor="mm")
    draw.line([(300, 380), (980, 380)], fill=(255, 215, 0, 150), width=2)
    font_small = _load_bold_font(24)
    draw.text((640, 430), "تابعونا للحصول على آخر المستجدات", font=font_small, fill=(180, 190, 210, 200), anchor="mm")
    draw.text((640, 480), "#PUL7SAR", font=font_small, fill=(255, 215, 0, 200), anchor="mm")
    draw.ellipse([(540, 610), (560, 630)], fill=(255, 50, 50, 200))
    draw.ellipse([(620, 610), (640, 630)], fill=(50, 50, 255, 200))
    draw.ellipse([(700, 610), (720, 630)], fill=(50, 255, 50, 200))
    return img.convert("RGB")


def build_placeholder_style3():
    """البطاقة 3: أنيقة عصرية"""
    img = Image.new("RGB", (1280, 720), (10, 14, 26))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(720):
        shade = int(10 + (y / 720) * 22)
        draw.line([(0, y), (1280, y)], fill=(shade, shade + 6, shade + 20))
    draw.line([(0, 120), (1280, 120)], fill=(220, 38, 38, 180), width=2)
    draw.line([(0, 600), (1280, 600)], fill=(220, 38, 38, 180), width=2)
    for x in range(100, 1200, 150):
        draw.text((x, 150), "✦", font=_load_bold_font(24), fill=(255, 215, 0, 80), anchor="mm")
        draw.text((x, 570), "✦", font=_load_bold_font(24), fill=(255, 215, 0, 80), anchor="mm")
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 280
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, ((1280 - logo_w) // 2, 210), logo)
        except Exception:
            pass
    font_big = _load_bold_font(48)
    draw.text((640, 350), "SPORTS NEWS", font=font_big, fill=(255, 255, 255, 220), anchor="mm")
    draw.line([(300, 400), (980, 400)], fill=(255, 215, 0, 120), width=1)
    font_medium = _load_bold_font(24)
    draw.text((640, 440), "● ● ● ● ● ● ● ● ● ● ● ●", font=font_medium, fill=(255, 215, 0, 100), anchor="mm")
    font_small = _load_bold_font(28)
    draw.text((640, 510), "#PUL7SAR", font=font_small, fill=(255, 215, 0, 200), anchor="mm")
    return img.convert("RGB")


def build_placeholder_style4():
    """البطاقة 4: بطاقة لاعب (Topps/Panini)"""
    img = Image.new("RGB", (1280, 720), (30, 25, 20))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(60, 40), (1220, 680)], outline=(255, 215, 0, 200), width=6)
    draw.rectangle([(80, 60), (1200, 660)], outline=(255, 215, 0, 100), width=2)
    draw.rectangle([(90, 70), (1190, 650)], fill=(20, 18, 25, 240))
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 100
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, (120, 85), logo)
        except Exception:
            pass
    draw.rectangle([(340, 100), (940, 400)], outline=(255, 215, 0, 150), width=3)
    draw.rectangle([(350, 110), (930, 390)], fill=(15, 13, 20, 200))
    font_big = _load_bold_font(72)
    draw.text((640, 240), "❓", font=font_big, fill=(255, 215, 0, 120), anchor="mm")
    font_star = _load_bold_font(32)
    draw.text((640, 430), "⭐ ⭐ ⭐ ⭐ ⭐", font=font_star, fill=(255, 215, 0, 200), anchor="mm")
    font_year = _load_bold_font(28)
    draw.text((640, 490), "🏅 2026", font=font_year, fill=(255, 215, 0, 180), anchor="mm")
    font_info = _load_bold_font(20)
    draw.text((640, 540), "PUL7SAR SPORTS", font=font_info, fill=(180, 190, 210, 150), anchor="mm")
    font_small = _load_bold_font(24)
    draw.text((640, 590), "#PUL7SAR", font=font_small, fill=(255, 215, 0, 200), anchor="mm")
    return img.convert("RGB")


def build_placeholder_image():
    styles = {
        1: build_placeholder_style1,
        2: build_placeholder_style2,
        3: build_placeholder_style3,
        4: build_placeholder_style4,
    }
    return styles.get(PLACEHOLDER_STYLE, build_placeholder_style1)()


# ==============================================================================
# دوال المساعدة
# ==============================================================================

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


# ==============================================================================
# دوال تنقية النصوص (3 طبقات)
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
                LOG.info("تجاهل صورة عمودية/شبه مربعة (نسبة %.2f): %s", ratio, url)
                return None
        return img
    return retry(_get, attempts=2, what=f"تحميل صورة {url}")


def place_watermark_with_background(image):
    if not os.path.exists(LOGO_PATH):
        LOG.warning("ملف الشعار غير موجود - سيتم النشر بدون علامة مائية")
        return image
    try:
        image = image.convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")
        LOGO_WIDTH = 160
        ratio = LOGO_WIDTH / logo.size[0]
        logo = logo.resize((LOGO_WIDTH, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
        margin_x, margin_y = 20, 20
        logo_w, logo_h = logo.size
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        padding = 15
        overlay_draw.rectangle(
            [
                margin_x - padding,
                margin_y - padding,
                margin_x + logo_w + padding,
                margin_y + logo_h + padding
            ],
            fill=(255, 255, 255, 220)
        )
        image = Image.alpha_composite(image, overlay)
        image.paste(logo, (margin_x, margin_y), logo)
        LOG.info("تم وضع الشعار الموحد مع الخلفية")
        return image.convert("RGB")
    except Exception as e:
        LOG.warning(f"فشل وضع الشعار بخلفية: {e}")
        return image.convert("RGB") if image.mode != "RGB" else image


def search_google_images_efficient(query: str):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_CX:
        LOG.warning("مفاتيح Google Custom Search غير متوفرة - تخطي هذا المصدر")
        return None
    def _search():
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_CX,
            "q": query,
            "searchType": "image",
            "num": 5,
            "safe": "active",
        }
        r = requests.get(url, params=params, headers=HTTP_HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("items", [])
    results = retry(_search, attempts=2, what=f"بحث Google Images عن '{query}'")
    if not results:
        return None
    for item in results:
        img_url = item.get("link")
        if not img_url:
            continue
        img = download_image(img_url)
        if img and img.size[0] >= 800 and img.size[1] >= 500:
            LOG.info("تم جلب صورة من Google Custom Search")
            return img
    LOG.info("لم يتم العثور على صورة مناسبة في Google Custom Search")
    return None


def search_wikipedia_image(query: str):
    def _search():
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": query, "limit": 1,
                    "namespace": 0, "format": "json"},
            headers=HTTP_HEADERS, timeout=10,
        )
        r.raise_for_status()
        results = r.json()
        if len(results) < 2 or not results[1]:
            return None
        title = results[1][0]
        r2 = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}",
            headers=HTTP_HEADERS, timeout=10,
        )
        r2.raise_for_status()
        data = r2.json()
        thumb = data.get("originalimage") or data.get("thumbnail")
        return thumb.get("source") if thumb else None
    img_url = retry(_search, attempts=2, what=f"بحث ويكيبيديا عن '{query}'")
    if not img_url:
        return None
    return download_image(img_url)


def search_wikimedia_commons(query: str):
    def _search():
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "list": "search", "srnamespace": 6,
                "srsearch": f"{query} filetype:bitmap", "srlimit": 20, "format": "json",
            },
            headers=HTTP_HEADERS, timeout=10,
        )
        r.raise_for_status()
        return r.json().get("query", {}).get("search", [])
    results = retry(_search, attempts=2, what=f"بحث Wikimedia Commons عن '{query}'")
    if not results:
        return None
    random.shuffle(results)
    for item in results[:12]:
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
        img_url = retry(_get_url, attempts=1, what=f"رابط صورة Commons '{title}'")
        if not img_url:
            continue
        img = download_image(img_url)
        if img and img.size[0] >= 800:
            return img
    return None


GENERIC_FALLBACK_QUERY = "professional football stadium match action"


def search_ddgs_image(query: str, require_relevance: bool = True):
    def _search():
        with DDGS() as ddgs:
            return list(ddgs.images(query, max_results=25))
    results = retry(_search, attempts=2, what=f"بحث DDG عن '{query}'")
    if not results:
        return None
    trusted = [r for r in results if is_trusted_domain(r.get("image", ""))]
    if not trusted:
        LOG.warning("لا نتائج من نطاقات موثوقة لـ '%s'.", query)
        return None
    if require_relevance:
        trusted_relevant = [r for r in trusted if is_relevant_result(r, query)]
        candidates = trusted_relevant if trusted_relevant else trusted
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


# ==============================================================================
# دوال الصورة النهائية
# ==============================================================================

def build_final_image(base_img):
    canvas = Image.new("RGB", (1280, 720), (15, 23, 42))
    bg = ImageOps.fit(base_img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas.paste(bg, (0, 0))
    canvas = canvas.convert("RGBA")
    corner_gradient = Image.new("RGBA", (260, 140), (0, 0, 0, 0))
    cg_draw = ImageDraw.Draw(corner_gradient)
    for y in range(140):
        alpha = int(max(0, 100 - y * 0.9))
        cg_draw.line([(0, y), (260, y)], fill=(0, 0, 0, alpha))
    canvas.alpha_composite(corner_gradient, dest=(0, 0))
    canvas.convert("RGB").save(FINAL_IMAGE_PATH, quality=95)


# ==============================================================================
# دوال إرسال تليجرام
# ==============================================================================

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
# الدالة الرئيسية
# ==============================================================================

def main():
    if not (GROQ_KEY and BOT_TOKEN and CHAT_ID):
        LOG.critical("متغيرات البيئة الأساسية ناقصة")
        return

    if not os.path.exists(LOGO_PATH):
        LOG.warning("ملف الشعار غير موجود")

    history = load_history()
    posted_links_set = set(history["links"])
    posted_titles = history["titles"]

    is_what_if_time = datetime.now(timezone.utc).hour == 18
    selected_article = None

    if not is_what_if_time:
        articles = fetch_articles(posted_links_set, posted_titles)
        if not articles:
            LOG.info("لا توجد مقالات صالحة جديدة")
            return
        selected_article = random.choice(articles)

    # توليد المحتوى
    if is_what_if_time:
        prompt_lines = [
            'أنت مؤرخ رياضي خبير في منصة PUL7SAR. اكتب فقرة تفاعلية بعنوان "ماذا لو؟" عن لحظة تاريخية حقيقية في كرة القدم.',
            '- اختر موقفاً حقيقياً وقع في مباراة رسمية (نهائي كأس عالم، دوري أبطال أوروبا، كلاسيكو).',
            '- صف الموقف كما حدث، ثم اطرح السؤال: "ماذا لو تغيرت هذه اللحظة؟"',
            '- استعرض السيناريو البديل وتأثيره على تاريخ كرة القدم، الألقاب، والجوائز الفردية.',
            '- اكتب بالعربية الفصحى الواضحة، بدون رموز تنسيق.',
            '- الحجم لا يتجاوز 900 حرف.',
            '- اختم بـ #PUL7SAR وسؤال تفاعلي للمتابعين.',
            '',
            'تنبيه مهم: أي خطأ إملائي أو نحوي أو تشويه في النص يؤدي إلى رفض المنشور.',
            '',
            'في نهاية ردك اترك سطراً جديداً واكتب حصراً اسم لاعب أو حدث تاريخي محدد بالإنجليزية:',
            '[IMG_SEARCH: <اسم شخص أو حدث حقيقي محدد>]',
        ]
        prompt = "\n".join(prompt_lines)
        article_image_url = None
    else:
        prompt_lines = [
            "أنت رئيس تحرير رياضي مخضرم لمنصة PUL7SAR. مهمتك صياغة الخبر التالي بأسلوب احترافي واضح.",
            "",
            "تعليمات صارمة:",
            "1. اكتب حصراً بلغة عربية فصحى سليمة 100%.",
            "2. حدد نوع الرياضة والمنافسة بوضوح تام في بداية الخبر.",
            "3. الحجم لا يتجاوز 900 حرف. ممنوع رموز التنسيق.",
            "4. أي خطأ إملائي أو نحوي يؤدي إلى رفض المنشور.",
            "",
            "الخبر الخام:",
            "العنوان: " + selected_article["title"],
            "التفاصيل: " + selected_article["summary"],
            "",
            "الصياغة المطلوبة:",
            "- عنوان رئيسي جذاب يعبر عن الرياضة والحدث بدقة.",
            "- شرح تفصيلي مبسط مع إيموجيات مناسبة.",
            "- إنهاء المنشور بهاشتاقات عربية مناسبة مع #PUL7SAR.",
            "",
            "في نهاية ردك اترك خطاً جديداً وحدد اسم اللاعب أو الفريق المذكور في الخبر بالضبط،",
            "بالإنجليزية الصحيحة، بهذا الشكل:",
            "[IMG_SEARCH: <الاسم الحقيقي المحدد>]",
        ]
        prompt = "\n".join(prompt_lines)
        article_image_url = selected_article.get("image")

    ai_response = call_groq(prompt)
    if not ai_response:
        LOG.error("فشل توليد المحتوى")
        return

    match = re.search(r"\[IMG_SEARCH:\s*([\s\S]*?)\]", ai_response)
    if match:
        img_query = match.group(1).strip()
        clean_text = ai_response.replace(match.group(0), "").strip()
    else:
        img_query = None
        clean_text = ai_response.strip()

    # تنقية النص
    clean_text = ensure_perfect_arabic(clean_text)
    if clean_text is None:
        LOG.critical("النص مشوه - لن يتم النشر")
        return

    # سلسلة مصادر الصور
    base_img = None

    # 1- صورة المقال
    if article_image_url:
        base_img = download_image(article_image_url)
        if base_img:
            if any(domain in article_image_url for domain in CHANNEL_LOGO_DOMAINS):
                LOG.info("صورة من قناة تلفزيونية - تطبيق تغطية الشعار")
            base_img = place_watermark_with_background(base_img)

    # 2- Google Custom Search
    if base_img is None and img_query:
        base_img = search_google_images_efficient(img_query)
        if base_img:
            base_img = place_watermark_with_background(base_img)

    # 3- ويكيبيديا
    if base_img is None and img_query:
        base_img = search_wikipedia_image(img_query)
        if base_img:
            base_img = place_watermark_with_background(base_img)

    # 4- Wikimedia Commons
    if base_img is None and img_query:
        base_img = search_wikimedia_commons(img_query)
        if base_img:
            base_img = place_watermark_with_background(base_img)

    # 5- DDGS موثوق
    if base_img is None and img_query:
        base_img = search_ddgs_image(img_query, require_relevance=True)
        if base_img:
            base_img = place_watermark_with_background(base_img)

    # 6- DDGS عام
    if base_img is None:
        LOG.info("محاولة أخيرة بصورة رياضية عامة")
        base_img = search_ddgs_image(GENERIC_FALLBACK_QUERY, require_relevance=False)
        if base_img:
            base_img = place_watermark_with_background(base_img)

    # 7- بطاقة احتياطية
    if base_img is None:
        LOG.warning("استخدام البطاقة الاحتياطية")
        base_img = build_placeholder_image()

    build_final_image(base_img)

    if not send_telegram_photo(clean_text):
        LOG.error("فشل النشر على تليجرام")
        return

    if selected_article:
        history["links"].append(selected_article["link"])
        history["titles"].append(selected_article["title"])
        save_history(history)
        git_commit_and_push()

    LOG.info("تم نشر المنشور بنجاح")


if __name__ == "__main__":
    main()
