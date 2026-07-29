import os
import json
import re
import time
import random
import logging
import subprocess
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import quote

import requests
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageOps, ImageFont
from duckduckgo_search import DDGS

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

LOGO_PATH = "logo.png"
MIN_LANDSCAPE_RATIO = 1.05

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

            articles.append({"title": title, "summary": clean_summary, "link": link})

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
    text = re.sub(r"[*_~`]+", "", text)

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

def download_image(url: str, require_landscape: bool = True):
    def _get():
        r = requests.get(url, headers=HTTP_HEADERS, timeout=10)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        if img.size[0] < 600 or img.size[1] < 400:
            raise ValueError("الصورة صغيرة جداً")
        if require_landscape:
            ratio = img.size[0] / img.size[1]
            if ratio < MIN_LANDSCAPE_RATIO:
                return None
        return img

    return retry(_get, attempts=2, what=f"تحميل صورة {url}")

# ==============================================================================
# نظام استخراج الصور الذكي (تدرج هرمي 4 مراحل)
# ==============================================================================

def extract_image_from_article(url: str):
    """المرحلة 1: سحب الصورة مباشرة من رابط الخبر الأصلي"""
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img = download_image(og_img["content"], require_landscape=True)
            if img:
                LOG.info("تم العثور على الصورة مباشرة من رابط المقال الأصلي!")
                return img
    except Exception as exc:
        LOG.debug("لم يتم العثور على صورة في المقال الأصلي: %s", exc)
    return None

def search_wikipedia_image(query: str):
    """المرحلة 2: البحث والسحب من ويكيبيديا"""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json"
        r = requests.get(search_url, headers=HTTP_HEADERS, timeout=10)
        data = r.json()
        results = data.get("query", {}).get("search", [])
        if results:
            page_title = results[0]["title"]
            page_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={quote(page_title)}&pithumbsize=1000&format=json"
            r2 = requests.get(page_url, headers=HTTP_HEADERS, timeout=10)
            pages = r2.json().get("query", {}).get("pages", {})
            for _, page_info in pages.items():
                thumb = page_info.get("thumbnail", {}).get("source")
                if thumb:
                    img = download_image(thumb, require_landscape=True)
                    if img:
                        LOG.info("تم العثور على صورة من ويكيبيديا بنجاح!")
                        return img
    except Exception as exc:
        LOG.debug("فشل جلب الصورة من ويكيبيديا: %s", exc)
    return None

def search_images_duckduckgo(query: str):
    """المرحلة 3: البحث عبر DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=5))
            for r in results:
                img_url = r.get("image")
                if not img_url:
                    continue
                img = download_image(img_url, require_landscape=True)
                if img:
                    LOG.info("تم العثور على صورة عبر DuckDuckGo بنجاح!")
                    return img
    except Exception as exc:
        LOG.debug("خطأ في بحث صور DuckDuckGo: %s", exc)
    return None

def search_google_images_efficient(query: str):
    """المرحلة 4 والأخيرة: مفتاح بحث جوجل كخط دفاع أخير"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_CX:
        return None
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_CX, "q": query, "searchType": "image", "num": 3, "safe": "active"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        items = response.json().get("items", [])
        for item in items:
            img_url = item.get("link")
            if not img_url:
                continue
            img = download_image(img_url, require_landscape=True)
            if img:
                LOG.info("تم العثور على صورة عبر Google Custom Search API!")
                return img
    except Exception as exc:
        LOG.debug("خطأ في بحث جوجل: %s", exc)
    return None

def get_smart_image(article_link: str, img_query: str):
    """تنفيذ التدرج الهرمي الخماسي للصور"""
    # 1. المصدر نفسه
    if article_link:
        img = extract_image_from_article(article_link)
        if img: return img
    
    if img_query:
        # 2. ويكيبيديا
        img = search_wikipedia_image(img_query)
        if img: return img
        
        # 3. DuckDuckGo
        img = search_images_duckduckgo(img_query)
        if img: return img
        
        # 4. مفتاح جوجل الأخير
        img = search_google_images_efficient(img_query)
        if img: return img
        
    return None

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

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = 130
            ratio = logo_w / logo.size[0]
            logo = logo.resize((logo_w, int(logo.size[1] * ratio)), Image.Resampling.LANCZOS)
            alpha_channel = logo.split()[3].point(lambda p: int(p * 0.85))
            logo.putalpha(alpha_channel)
            margin = 22
            canvas.alpha_composite(logo, dest=(margin, margin))
        except Exception as exc:
            LOG.warning("تعذر وضع العلامة المائية: %s", exc)

    canvas.convert("RGB").save(FINAL_IMAGE_PATH, quality=95)

def _load_bold_font(size: int) -> ImageFont.FreeTypeFont:
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
    img = Image.new("RGB", (1280, 720), (10, 14, 26))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(720):
        shade = int(10 + (y / 720) * 22)
        draw.line([(0, y), (1280, y)], fill=(shade, shade + 6, shade + 20))

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
        LOG.critical("متغيرات البيئة الأساسية ناقصة.")
        return

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
        prompt_lines = [
            'أنت محرر رياضي محترف في منصة PUL7SAR. اكتب فقرة تفاعلية مشوقة بعنوان "ماذا لو؟" عن سيناريو تاريخي في كرة القدم.',
            "- اكتب باللغة العربية الفصحى الواضحة والاحترافية حصراً، بدون أي كلمات أجنبية غير معربة.",
            "- ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟",
            "- اختم بسؤال تفاعلي للمتابعين، مع وضع هاشتاغات واضحة ومفصولة في النهاية مثل #كرة_القدم #PUL7SAR.",
            "- الحجم لا يتجاوز 900 حرف. ممنوع رموز التنسيق مثل ** أو *.",
            "",
            "في نهاية ردك اترك خطاً جديداً واكتب حصراً اسم لاعب أو حدث تاريخي محدد بالإنجليزية للتوضيح:",
            "[IMG_SEARCH: <اسم شخص أو حدث حقيقي محدد>]",
        ]
        prompt = "\n".join(prompt_lines)
    else:
        prompt_lines = [
            "أنت رئيس تحرير رياضي مخضرم لمنصة PUL7SAR. مهمتك صياغة الخبر التالي بأسلوب احترافي واضح منذ السطر الأول.",
            "",
            "تعليمات صارمة:",
            "1. اكتب حصراً بلغة عربية فصحى سليمة 100%, بدون أي كلمة أجنبية أو ترجمة ركيكة؛ عرّب الأسماء بدقة.",
            "2. حدد نوع الرياضة والمنافسة بوضوح تام في بداية الخبر.",
            "3. الحجم لا يتجاوز 900 حرف. ممنوع رموز التنسيق (** أو *).",
            "4. استخدم هاشتاغات عربية واضحة ومفصولة عن بعضها (مثلاً: #الدوري_الإنجليزي #ريال_مدريد #PUL7SAR) وتجنب الهاشتاغات المتراصة أو المبهمة.",
            "",
            "الخبر الخام:",
            "العنوان: " + selected_article["title"],
            "التفاصيل: " + selected_article["summary"],
            "",
            "الصياغة المطلوبة:",
            "- عنوان رئيسي جذاب يعبر عن الرياضة والحدث بدقة.",
            "- شرح تفصيلي مبسط مع إيموجيات مناسبة.",
            "- إنهاء المنشور بهاشتاغات عربية مفهومة ومفصولة.",
            "",
            "في نهاية ردك اترك خطاً جديداً وحدد اسم اللاعب أو الفريق أو الملعب المذكور في الخبر بالإنجليزية الصحيحة بهذا الشكل حصراً:",
            "[IMG_SEARCH: <الاسم الحقيقي المحدد>]",
        ]
        prompt = "\n".join(prompt_lines)

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

    article_link = selected_article["link"] if selected_article else None
    
    LOG.info("جاري بدء التدرج الهرمي الذكي لجلب الصورة...")
    base_img = get_smart_image(article_link, img_query)

    if base_img is None:
        LOG.warning("فشلت كل مراحل جلب الصور الحقيقية — استخدام البطاقة الاحتياطية.")
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
