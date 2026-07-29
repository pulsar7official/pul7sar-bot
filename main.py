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

# نطاقات موثوقة فقط لصور DDGS الاحتياطية. استبعدت BBC وSky عمداً لأن صورهم
# الإخبارية غالباً لقطات فيديو فيها "لوجو" القناة مدموج بالبكسلات نفسها،
# ما يتعارض بصرياً مع علامتنا التجارية. القائمة موسّعة عمداً بمواقع الأندية
# الرسمية وصحف كبرى تنشر صوراً محررة (editorial) نظيفة بدون شعار مدموج،
# لتقليل حالات اللجوء للصورة الاحتياطية دون التضحية بمصداقية الصورة.
TRUSTED_IMAGE_DOMAINS = [
    "wikipedia.org", "wikimedia.org",
    "espncdn.com", "espn.com",
    "uefa.com", "fifa.com",
    "reuters.com", "apnews.com",
    "gettyimages.com",
    "premierleague.com", "laliga.com", "bundesliga.com", "legaseriea.it", "ligue1.com",
    "theguardian.com", "independent.co.uk", "mirror.co.uk", "standard.co.uk",
    "goal.com", "90min.com", "football-italia.net", "marca.com", "as.com",
    # مواقع الأندية الرسمية — صور محررة نظيفة، بدون شعار قناة مدموج
    "realmadrid.com", "fcbarcelona.com", "manutd.com", "liverpoolfc.com",
    "mancity.com", "chelseafc.com", "arsenal.com", "tottenhamhotspur.com",
    "psg.fr", "fcbayern.com", "juventus.com", "acmilan.com", "inter.it",
]

LOGO_PATH = "logo.png"  # شعار شفاف واحد يوضع كعلامة مائية صغيرة فقط — بدون شريط لوني

# الحد الأدنى لنسبة العرض إلى الارتفاع حتى تُقبل الصورة — يستبعد الصور
# العمودية (صور بروفايل ويكيبيديا مثلاً) التي تنتج قصاً مشوهاً عند
# تحويلها لمقاس أفقي 1280x720 بطريقة الـ Cover. خُفّض من 1.2 إلى 1.05
# ليقبل صوراً مربعة تقريباً (شائعة بصور الأندية) دون قبول صور عمودية حقيقية.
MIN_LANDSCAPE_RATIO = 1.05


def is_trusted_domain(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower()
        return any(domain == d or domain.endswith("." + d) for d in TRUSTED_IMAGE_DOMAINS)
    except Exception:
        return False


def is_relevant_result(result: dict, query: str) -> bool:
    """
    تحقق تقريبي من صلة نتيجة بحث DDGS بموضوع الاستعلام: يشترط تطابق كلمة
    مفتاحية واحدة على الأقل من الاستعلام مع عنوان النتيجة، لتفادي صور
    حقيقية المصدر لكنها عن موضوع/رياضة مختلفة تماماً (مثل صورة كريكيت
    على خبر كرة قدم لمجرد أن كلاهما من نفس الموقع الموثوق).
    """
    title = (result.get("title") or "").lower()
    if not title:
        return True  # لا معلومات كافية للحكم — لا نستبعد النتيجة تعسفياً
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


def sanitize_news_text(text: str) -> str:
    # إزالة رموز الماركداون فقط أولاً
    text = re.sub(r"[*_~`]+", "", text)

    # إزالة أي كلمة لاتينية/رقمية شاردة متسربة داخل النص العربي (خطأ أو
    # تشويش من النموذج)، مع استثناء الهاشتاقات (#PUL7SAR وغيرها) والروابط
    # بالكامل. نحذف الكلمة الشاردة فقط ونُبقي بقية الجملة سليمة، بعكس
    # الأسلوب القديم الذي كان يحذف السطر كاملاً ويكسر المعنى.
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("#") or "http://" in line or "https://" in line:
            cleaned_lines.append(line)  # هاشتاقات/روابط — لا تُلمس
            continue
        tokens = line.split(" ")
        kept = []
        for tok in tokens:
            core = tok.strip(".,!؟?،؛:")
            # نحذف فقط الكلمة التي فيها حرف لاتيني (English) — الأرقام
            # (أسعار الانتقالات، النتائج، السنوات) لازم تبقى دائماً.
            if core and re.search(r"[a-zA-Z]", core) and not core.startswith("#"):
                continue
            kept.append(tok)
        cleaned_line = re.sub(r"\s{2,}", " ", " ".join(kept)).strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
                LOG.info("تجاهل صورة عمودية/شبه مربعة (نسبة %.2f) تسبب قصاً سيئاً: %s", ratio, url)
                return None
        return img

    return retry(_get, attempts=2, what=f"تحميل صورة {url}")


def search_wikipedia_image(query: str):
    """
    مصدر سريع للأسماء المشهورة جداً: صورة ملخص صفحة ويكيبيديا الرئيسية.
    محدود لأنه صورة واحدة فقط (غالباً بروفايل رسمي عمودي).
    """
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
    # ملاحظة: أغلب صور بروفايل ويكيبيديا عمودية، فستُرفض تلقائياً هنا
    # (require_landscape=True داخل download_image) وينتقل الكود لمصدر أوسع.
    return download_image(img_url)


def search_wikimedia_commons(query: str):
    """
    مصدر أوسع بكثير من ملخص ويكيبيديا: يبحث مباشرة في مستودع Wikimedia
    Commons (ملايين الصور الحقيقية المرفوعة بترخيص حر من مصورين صحفيين
    ومساهمين)، ويرجّع عدة مرشحين بدل صورة واحدة فقط — يرفع الاحتمالية
    بشكل كبير مع الحفاظ الكامل على أصالة الصورة (كل صورة موثقة ومصدرها معروف).
    """
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
    for item in results[:12]:  # سقف محاولات معقول لتفادي إبطاء التشغيل
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


# استعلام احتياطي أخير عام لكنه حقيقي ومرتبط بالرياضة عموماً — يُستخدم فقط
# لو فشل البحث عن الاسم/الحدث المحدد بكل المصادر أعلاه، لتفادي الصورة
# الفارغة بقدر الإمكان مع البقاء ضمن نطاقات موثوقة 100%.
GENERIC_FALLBACK_QUERY = "professional football stadium match action"




def search_ddgs_image(query: str, require_relevance: bool = True):
    """
    بحث احتياطي مقيّد بنطاقات موثوقة (TRUSTED_IMAGE_DOMAINS). لو require_relevance
    مفعّل (الوضع الافتراضي)، يُشترط تطابق كلمة من الاستعلام مع عنوان النتيجة
    لتفادي صور حقيقية المصدر لكنها عن موضوع مختلف تماماً. يُعطَّل هذا الشرط فقط
    عند استخدام GENERIC_FALLBACK_QUERY (عام بطبيعته، لا يوجد "عنوان" محدد ليطابقه).
    """
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


def build_final_image(base_img):
    """
    تصميم نظيف بدون شريط لوني ضخم أو نص "PUL7SAR SPORTS" — فقط علامة
    مائية صغيرة شفافة بالزاوية، لمظهر احترافي يشبه منشورات وسائل إعلام حقيقية.
    """
    canvas = Image.new("RGB", (1280, 720), (15, 23, 42))
    bg = ImageOps.fit(base_img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas.paste(bg, (0, 0))
    canvas = canvas.convert("RGBA")

    # تدرج خفيف جداً أعلى اليسار فقط لضمان وضوح اللوجو فوق أي خلفية فاتحة
    corner_gradient = Image.new("RGBA", (260, 140), (0, 0, 0, 0))
    cg_draw = ImageDraw.Draw(corner_gradient)
    for y in range(140):
        alpha = int(max(0, 100 - y * 0.9))
        cg_draw.line([(0, y), (260, y)], fill=(0, 0, 0, alpha))
    canvas.alpha_composite(corner_gradient, dest=(0, 0))

    # علامة مائية صغيرة وشفافة بأعلى اليسار — بدون شريط لوني وبدون نص كبير
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 130
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            # شفافية خفيفة (85%) حتى تبان كعلامة مائية أنيقة لا تطغى على الصورة
            alpha_channel = logo.split()[3].point(lambda p: int(p * 0.85))
            logo.putalpha(alpha_channel)
            margin = 22
            canvas.alpha_composite(logo, dest=(margin, margin))
        except Exception as exc:
            LOG.warning("تعذر وضع العلامة المائية: %s", exc)
    else:
        LOG.warning("ملف الشعار %s غير موجود — سيتم النشر بدون علامة مائية.", LOGO_PATH)

    canvas.convert("RGB").save(FINAL_IMAGE_PATH, quality=95)


def _load_bold_font(size: int) -> ImageFont.FreeTypeFont:
    """أفضل خط عريض متاح على عامل GitHub Actions (Ubuntu)، بديل نظيف عن الخط الافتراضي."""
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


def build_placeholder_image():
    """
    بطاقة مصمّمة بقصد (وليست شاشة سوداء فارغة) تُستخدم فقط لو تعذر جلب أي
    صورة حقيقية إطلاقاً من كل المصادر. تشبه بطاقات "الخبر السريع" النصية
    التي تنشرها حسابات رياضية حقيقية أحياناً، فلا تبان كخطأ بالنظام.
    """
    img = Image.new("RGB", (1280, 720), (10, 14, 26))
    draw = ImageDraw.Draw(img, "RGBA")

    # تدرج خلفية ناعم من الأعلى للأسفل
    for y in range(720):
        shade = int(10 + (y / 720) * 22)
        draw.line([(0, y), (1280, y)], fill=(shade, shade + 6, shade + 20))

    # دائرة توهج خفيفة بالمنتصف تعطي إحساس "سبوت لايت" بدل الفراغ التام
    glow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([340, 60, 940, 660], fill=(70, 90, 160, 35))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # خط رفيع علوي وسفلي بلون العلامة التجارية كإطار بصري بسيط
    draw.rectangle([(0, 0), (1280, 4)], fill=(220, 38, 38, 255))
    draw.rectangle([(0, 716), (1280, 720)], fill=(220, 38, 38, 255))

    # اللوجو إن وُجد، وإلا كتابة اسم العلامة كبديل
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 220
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            img.paste(logo, ((1280 - logo_w) // 2, 300), logo)
        except Exception:
            pass
    else:
        font_big = _load_bold_font(64)
        draw.text((640, 340), "PUL7SAR", font=font_big, fill=(255, 255, 255, 255), anchor="mm")

    font_small = _load_bold_font(22)
    draw.text((640, 470), "SPORTS NEWS", font=font_small, fill=(180, 190, 210, 230), anchor="mm")

    return img.convert("RGB")


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


def main():
    if not (GROQ_KEY and BOT_TOKEN and CHAT_ID):
        LOG.critical("متغيرات البيئة الأساسية ناقصة (GROQ_API_KEY / TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).")
        return

    if not os.path.exists(LOGO_PATH):
        LOG.warning(
            "⚠️ ملف الشعار '%s' غير موجود بجذر الريبو — سيتم نشر الصور "
            "بدون علامة مائية حتى يُرفع الملف.", LOGO_PATH,
        )

    history = load_history()
    posted_links_set = set(history["links"])
    posted_titles = history["titles"]

    is_what_if_time = datetime.now(timezone.utc).hour == 18
    selected_article = None

    if not is_what_if_time:
        articles = fetch_articles(posted_links_set, posted_titles)
        if not articles:
            LOG.info("لا توجد مقالات صالحة جديدة في هذا التشغيل.")
            return
        selected_article = random.choice(articles)

    if is_what_if_time:
        # مبني كقائمة أسطر مربوطة بـ "\n" بدل f-string متعدد الأسطر،
        # لتفادي أي كسر ناتج عن نسخ/لصق علامات اقتباس ذكية أو أسطر مفقودة.
        prompt_lines = [
            'أنت محرر رياضي محترف في منصة PUL7SAR. اكتب فقرة تفاعلية مشوقة بعنوان "ماذا لو؟" عن سيناريو تاريخي في كرة القدم.',
            "- اكتب باللغة العربية الفصحى الواضحة والاحترافية حصراً، بدون أي كلمات أجنبية غير معربة.",
            "- ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟",
            "- اختم بسؤال تفاعلي للمتابعين، مع هاشتاق #PUL7SAR.",
            "- الحجم لا يتجاوز 900 حرف. ممنوع رموز التنسيق مثل ** أو *.",
            "",
            "في نهاية ردك اترك خطاً جديداً واكتب حصراً اسم لاعب أو حدث تاريخي محدد بالإنجليزية (مثال حقيقي: Diego Maradona 1986 World Cup)، وليس وصفاً عاماً:",
            "[IMG_SEARCH: <اسم شخص أو حدث حقيقي محدد>]",
        ]
        prompt = "\n".join(prompt_lines)
        article_image_url = None
    else:
        prompt_lines = [
            "أنت رئيس تحرير رياضي مخضرم لمنصة PUL7SAR. مهمتك صياغة الخبر التالي بأسلوب احترافي واضح منذ السطر الأول.",
            "",
            "تعليمات صارمة:",
            "1. اكتب حصراً بلغة عربية فصحى سليمة 100%، بدون أي كلمة أجنبية أو ترجمة ركيكة؛ عرّب الأسماء بدقة.",
            "2. حدد نوع الرياضة والمنافسة بوضوح تام في بداية الخبر.",
            "3. الحجم لا يتجاوز 900 حرف. ممنوع رموز التنسيق (** أو *).",
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
            "في نهاية ردك اترك خطاً جديداً وحدد اسم اللاعب أو الفريق أو الملعب المذكور في الخبر بالضبط،",
            "مكتوباً بإنجليزية صحيحة (اسمه الحقيقي الرسمي كما يُكتب في المصادر الإنجليزية، وليس وصفاً عاماً مثل 'football player celebrating')، بهذا الشكل حصراً:",
            "[IMG_SEARCH: <الاسم الحقيقي المحدد>]",
        ]
        prompt = "\n".join(prompt_lines)
        article_image_url = selected_article.get("image")

    ai_response = call_groq(prompt)
    if not ai_response:
        LOG.error("فشل توليد المحتوى — إنهاء التشغيل بدون نشر.")
        return

    match = re.search(r"\[IMG_SEARCH:\s*([\s\S]*?)\]", ai_response)
    if match:
        img_query = match.group(1).strip()
        clean_text = ai_response.replace(match.group(0), "").strip()
    else:
        img_query = None
        clean_text = ai_response.strip()

    clean_text = sanitize_news_text(clean_text)
    if len(clean_text) > 1020:
        clean_text = clean_text[:1017] + "..."

    # ترتيب مصادر الصور من الأدق للأقل دقة:
    # 1) صورة المقال الأصلية (لو وُجدت) — الأكثر دقة دائماً.
    # 2) ويكيبيديا للاسم المحدد — صورة واحدة موثقة بصاحب الاسم.
    # 3) Wikimedia Commons — مستودع أوسع بكثير لنفس الاسم (عدة مرشحين).
    # 4) بحث DDGS مقيّد بنطاقات موثوقة + مرتبط بالموضوع.
    # 5) بحث DDGS عام (صورة رياضية حقيقية لكن غير مرتبطة بالاسم تحديداً) — يقلل حالات الصورة الفارغة.
    # 6) صورة احتياطية مصمّمة (فقط لو فشلت كل المصادر الحقيقية أعلاه).
    base_img = None
    if article_image_url:
        base_img = download_image(article_image_url)

    if base_img is None and img_query:
        base_img = search_wikipedia_image(img_query)

    if base_img is None and img_query:
        base_img = search_wikimedia_commons(img_query)

    if base_img is None and img_query:
        base_img = search_ddgs_image(img_query)

    if base_img is None:
        LOG.info("لا صورة مرتبطة بالاسم المحدد — محاولة أخيرة بصورة رياضية عامة حقيقية.")
        base_img = search_ddgs_image(GENERIC_FALLBACK_QUERY, require_relevance=False)

    if base_img is None:
        LOG.warning("تعذر جلب أي صورة حقيقية على الإطلاق — استخدام البطاقة الاحتياطية المصمّمة.")
        base_img = build_placeholder_image()

    build_final_image(base_img)

    if not send_telegram_photo(clean_text):
        LOG.error("فشل النشر على تليجرام — لن يتم تحديث السجل.")
        return

    if selected_article:
        history["links"].append(selected_article["link"])
        history["titles"].append(selected_article["title"])
        save_history(history)
        git_commit_and_push()

    LOG.info("تم نشر المنشور بنجاح ✅")


if __name__ == "__main__":
    main()
