#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 PUL7SAR Ultimate Sports Engine
==============================================================================
An autonomous sports-news pipeline that:
  1. Pulls fresh sports headlines from a curated set of RSS feeds.
  2. Filters out stale, low-quality, or already-published items.
  3. Rewrites each story into polished Classical Arabic (فصحى) using the
     Groq Llama-3.3-70b model.
  4. Sources a matching, non-repetitive cover image (original article image
     first, DuckDuckGo image search as a fallback).
  5. Composes a branded 1280x720 "cover-fit" graphic with a logo + bottom
     stripe using Pillow.
  6. Publishes the final image + caption to a Telegram channel.
  7. Persists de-duplication state to posted_history.json and pushes the
     updated file back to the Git repository.

Designed to run unattended every hour via GitHub Actions.

Required environment variables:
  TELEGRAM_BOT_TOKEN   - Telegram bot token (from @BotFather)
  TELEGRAM_CHANNEL_ID  - Target channel id/username (e.g. "@my_channel")
  GROQ_API_KEY         - API key for Groq (https://console.groq.com)

Optional environment variables:
  MAX_POSTS_PER_RUN    - How many articles to publish per run (default: 1)
  GIT_AUTO_PUSH        - "true"/"false", whether to commit+push history
                          (default: "true" -- set to "false" for local tests)

Expected repository layout:
  ./main.py
  ./posted_history.json          (auto-created if missing)
  ./assets/logo_red.png
  ./assets/logo_blue.png
  ./requirements.txt
==============================================================================
"""

import os
import re
import io
import json
import time
import random
import string
import hashlib
import logging
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple

import requests
import feedparser
from PIL import Image, ImageDraw, ImageFont

try:
    from ddgs import DDGS  # modern package name
except ImportError:  # pragma: no cover - fallback for older installs
    from duckduckgo_search import DDGS  # type: ignore


# ==============================================================================
# CONFIGURATION
# ==============================================================================

LOG = logging.getLogger("pul7sar")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --- Secrets / required config -----------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

# --- Behaviour toggles --------------------------------------------------------
MAX_POSTS_PER_RUN = int(os.environ.get("MAX_POSTS_PER_RUN", "1"))
GIT_AUTO_PUSH = os.environ.get("GIT_AUTO_PUSH", "true").strip().lower() == "true"

# --- Paths ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "posted_history.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATHS = {
    "red": os.path.join(ASSETS_DIR, "logo_red.png"),
    "blue": os.path.join(ASSETS_DIR, "logo_blue.png"),
}
BRAND_COLORS = {
    "red": (198, 26, 42),     # elegant crimson red
    "blue": (18, 62, 130),    # deep royal blue
}

# --- RSS sources -----------------------------------------------------------
RSS_FEEDS: List[Tuple[str, str]] = [
    ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml"),
    ("Sky Sports", "https://www.skysports.com/rss/12040"),
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("Google News - Sports", "https://news.google.com/rss/search?q=sports&hl=en-US&gl=US&ceid=US:en"),
]

ARTICLE_MAX_AGE_HOURS = 48
MAX_HISTORY_AGE_DAYS = 30

LOW_QUALITY_KEYWORDS = [
    "quiz", "poll", "vote now", "caption competition", "guess the",
    "trivia", "how well do you know", "spot the ball", "sudoku",
    "crossword", "horoscope",
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 PUL7SAR-Bot/1.0"
    )
}

CANVAS_SIZE = (1280, 720)
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


# ==============================================================================
# UTILITIES
# ==============================================================================

def _retry(fn, attempts: int = 3, base_delay: float = 2.0, what: str = "operation"):
    """Generic retry wrapper with exponential backoff for flaky network calls."""
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - we want to catch & retry broadly here
            last_exc = exc
            LOG.warning("Attempt %d/%d failed for %s: %s", attempt, attempts, what, exc)
            if attempt < attempts:
                time.sleep(base_delay * attempt)
    LOG.error("All %d attempts failed for %s: %s", attempts, what, last_exc)
    return None


def normalize_text(text: str) -> str:
    """Lowercase + strip punctuation/whitespace for fuzzy duplicate comparisons."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


# ==============================================================================
# HISTORY / DE-DUPLICATION
# ==============================================================================

def load_history() -> Dict[str, str]:
    """
    Load posted_history.json.
    Structure: { "<hash>": "<iso_timestamp>" }
    """
    if not os.path.exists(HISTORY_FILE):
        LOG.info("No existing history file found -- starting fresh.")
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            LOG.warning("History file had unexpected format -- resetting.")
            return {}
    except (json.JSONDecodeError, OSError) as exc:
        LOG.error("Could not read history file (%s) -- starting fresh.", exc)
        return {}


def save_history(history: Dict[str, str]) -> None:
    """Prune entries older than MAX_HISTORY_AGE_DAYS, then write to disk."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_HISTORY_AGE_DAYS)
    pruned = {}
    for h, ts in history.items():
        try:
            if datetime.fromisoformat(ts) >= cutoff:
                pruned[h] = ts
        except ValueError:
            continue  # drop malformed timestamps

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(pruned, f, ensure_ascii=False, indent=2)
        LOG.info("History saved (%d active entries).", len(pruned))
    except OSError as exc:
        LOG.error("Failed to write history file: %s", exc)


def article_fingerprints(article: Dict[str, Any]) -> List[str]:
    """Return hashes representing this article's link + normalized title."""
    link_hash = sha256(article["link"].strip().lower())
    title_hash = sha256(normalize_text(article["title"]))
    return [link_hash, title_hash]


def is_duplicate(article: Dict[str, Any], history: Dict[str, str]) -> bool:
    return any(fp in history for fp in article_fingerprints(article))


def mark_as_posted(article: Dict[str, Any], history: Dict[str, str]) -> None:
    now_iso = datetime.now(timezone.utc).isoformat()
    for fp in article_fingerprints(article):
        history[fp] = now_iso


# ==============================================================================
# STEP 1: FETCH & FILTER RSS ARTICLES
# ==============================================================================

def _extract_image_url(entry: Any) -> Optional[str]:
    """Best-effort extraction of an image URL from a feedparser entry."""
    # media_content / media_thumbnail (common in BBC/Sky/ESPN feeds)
    for key in ("media_content", "media_thumbnail"):
        media = getattr(entry, key, None)
        if media:
            url = media[0].get("url")
            if url:
                return url

    # enclosures (podcasts/images attached directly)
    for enc in getattr(entry, "enclosures", []) or []:
        enc_type = enc.get("type", "")
        if "image" in enc_type and enc.get("href"):
            return enc["href"]

    # fallback: look for an <img> tag inside the summary/description HTML
    summary_html = getattr(entry, "summary", "") or ""
    match = re.search(r'<img[^>]+src="([^"]+)"', summary_html)
    if match:
        return match.group(1)

    return None


def fetch_all_articles() -> List[Dict[str, Any]]:
    """Pull and normalize entries from every configured RSS feed."""
    articles: List[Dict[str, Any]] = []

    for source_name, url in RSS_FEEDS:
        def _parse(u=url):
            feed = feedparser.parse(u, request_headers=HTTP_HEADERS)
            if feed.bozo and not feed.entries:
                raise RuntimeError(f"Feed parse error: {feed.bozo_exception}")
            return feed

        feed = _retry(_parse, what=f"fetching RSS feed '{source_name}'")
        if not feed:
            continue

        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = re.sub(r"<[^>]+>", "", getattr(entry, "summary", "") or "").strip()

            if not title or not link:
                continue

            published_dt = None
            if getattr(entry, "published_parsed", None):
                published_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif getattr(entry, "updated_parsed", None):
                published_dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            articles.append({
                "source": source_name,
                "title": title,
                "link": link,
                "summary": summary,
                "published": published_dt,
                "image_url": _extract_image_url(entry),
            })

    LOG.info("Fetched %d raw articles from %d feeds.", len(articles), len(RSS_FEEDS))
    return articles


def is_fresh(article: Dict[str, Any]) -> bool:
    published = article.get("published")
    if published is None:
        # Unable to verify age -- err on the side of caution and skip.
        return False
    age = datetime.now(timezone.utc) - published
    return timedelta(0) <= age <= timedelta(hours=ARTICLE_MAX_AGE_HOURS)


def is_low_quality(article: Dict[str, Any]) -> bool:
    haystack = f"{article['title']} {article['summary']}".lower()
    return any(kw in haystack for kw in LOW_QUALITY_KEYWORDS)


def filter_and_rank_articles(
    articles: List[Dict[str, Any]], history: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Apply freshness, quality, and de-dup filters; return newest-first."""
    good = []
    for a in articles:
        if not is_fresh(a):
            continue
        if is_low_quality(a):
            continue
        if is_duplicate(a, history):
            continue
        good.append(a)

    good.sort(key=lambda a: a["published"], reverse=True)
    LOG.info("%d articles passed freshness/quality/dedup filters.", len(good))
    return good


# ==============================================================================
# STEP 2: AI CONTENT GENERATION (GROQ / LLAMA-3.3-70B)
# ==============================================================================

SYSTEM_PROMPT = """أنت محرر أخبار رياضية محترف تعمل لصالح منصة "PUL7SAR". مهمتك صياغة الخبر الرياضي المُرسل إليك بلغة عربية فصحى راقية واحترافية.

التزم حرفيًا بالقواعد التالية:
1. اذكر نوع الرياضة والبطولة/المسابقة في بداية الخبر مباشرة، حتى يعرف القارئ طبيعة الحدث فور قراءة أول جملة.
2. لا تستخدم أي رموز تنسيق مثل ** أو * أو ~ أو أي رموز Markdown أخرى.
3. لا تُدرج أي كلمات أجنبية غير مُعرَّبة داخل النص؛ ترجم أو عرّب أسماء الأشخاص والأندية والبطولات بشكل صحيح إلى العربية.
4. يجب ألا يتجاوز النص الإخباري 1000 حرف، على أن ينتهي بهاشتاغات عربية مناسبة للخبر، وبهاشتاغ #PUL7SAR في النهاية.
5. اكتب بأسلوب سلس، دقيق، وخالٍ من الحشو أو المبالغة.
6. في نهاية ردك تمامًا، وبعد الهاشتاغات، أضف سطرًا جديدًا يحتوي على وسم البحث عن الصورة بهذا الشكل الدقيق تمامًا (بالإنجليزية):
[IMG_SEARCH: <a short precise English search query describing the main subject, e.g. player name, team, stadium, or event>]

لا تكتب أي مقدمات أو تعليقات خارج هذا التنسيق. أعد فقط نص الخبر متبوعًا بالهاشتاغات ثم وسم البحث عن الصورة."""


def _build_user_prompt(article: Dict[str, Any]) -> str:
    return (
        f"العنوان: {article['title']}\n"
        f"المصدر: {article['source']}\n"
        f"تفاصيل إضافية: {article['summary'][:1500]}\n\n"
        "اكتب الخبر الآن وفق التعليمات."
    )


def strip_markdown_artifacts(text: str) -> str:
    """Safety net: strip stray markdown symbols the model might still emit."""
    text = re.sub(r"[*~`_]{1,3}", "", text)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)  # md headers only
    return text.strip()


def generate_ai_content(article: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Calls the Groq API to rewrite the article in Arabic.
    Returns {"text": "<arabic body + hashtags>", "img_query": "<english query>"}
    or None on unrecoverable failure.
    """
    if not GROQ_API_KEY:
        LOG.error("GROQ_API_KEY is not set -- cannot generate content.")
        return None

    def _call():
        resp = requests.post(
            GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "temperature": 0.6,
                "max_tokens": 700,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(article)},
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    result = _retry(_call, what="Groq content generation")
    if not result:
        return None

    try:
        raw = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        LOG.error("Unexpected Groq response shape: %s", result)
        return None

    # Extract the [IMG_SEARCH: ...] tag from the end of the response.
    match = re.search(r"\[IMG_SEARCH:\s*(.+?)\]\s*$", raw, flags=re.DOTALL)
    if match:
        img_query = match.group(1).strip()
        body = raw[: match.start()].strip()
    else:
        LOG.warning("No [IMG_SEARCH:] tag found -- falling back to title-based query.")
        img_query = article["title"]
        body = raw.strip()

    body = strip_markdown_artifacts(body)

    # Enforce the 1000-character hard limit on the Arabic body (safety net;
    # the model is instructed to respect this already).
    if len(body) > 1000:
        body = body[:997].rstrip() + "..."

    if not body:
        LOG.error("Generated body was empty after processing.")
        return None

    return {"text": body, "img_query": img_query}


# ==============================================================================
# STEP 3: IMAGE SOURCING
# ==============================================================================

def _download_and_validate_image(url: str) -> Optional[bytes]:
    """Download a URL and confirm it is a genuinely decodable image."""
    def _get():
        r = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        r.raise_for_status()
        content = r.content
        if len(content) < 5000:  # tiny/placeholder images aren't useful
            raise ValueError("Image too small, likely a placeholder or icon.")
        # Validate it actually decodes as an image.
        img = Image.open(io.BytesIO(content))
        img.verify()
        return content

    return _retry(_get, attempts=2, what=f"downloading image {url}")


def get_original_image(article: Dict[str, Any]) -> Optional[bytes]:
    """Priority 1: use the article's own attached image, if any and valid."""
    url = article.get("image_url")
    if not url:
        return None
    LOG.info("Attempting to use original article image: %s", url)
    return _download_and_validate_image(url)


def search_ddgs_image(query: str, max_results: int = 15) -> Optional[bytes]:
    """
    Priority 2: search DuckDuckGo Images for a matching photo.
    Results are shuffled so that repeated topics (e.g. "Wembley Stadium")
    don't always yield the exact same picture across multiple posts.
    """
    def _search():
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                region="wt-wt",
                safesearch="moderate",
                size="Large",
                max_results=max_results,
            ))
        return results

    results = _retry(_search, attempts=2, what=f"DuckDuckGo image search '{query}'")
    if not results:
        LOG.warning("No DDG image results for query: %s", query)
        return None

    random.shuffle(results)  # avoid reusing the same top-ranked image repeatedly

    for result in results:
        img_url = result.get("image")
        if not img_url:
            continue
        data = _download_and_validate_image(img_url)
        if data:
            LOG.info("Selected DDG image for query '%s': %s", query, img_url)
            return data

    LOG.warning("All DDG candidate images failed validation for query: %s", query)
    return None


def source_cover_image(article: Dict[str, Any], img_query: str) -> Optional[bytes]:
    """Try the article's own image first, then fall back to image search."""
    image_bytes = get_original_image(article)
    if image_bytes:
        return image_bytes

    LOG.info("No usable original image -- searching DuckDuckGo for: %s", img_query)
    return search_ddgs_image(img_query)


# ==============================================================================
# STEP 4: IMAGE PROCESSING (PILLOW)
# ==============================================================================

def cover_fit(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """
    Resize + center-crop an image to completely fill target_size without
    distortion or letterboxing (the classic CSS `background-size: cover`
    behaviour).
    """
    img = img.convert("RGB")
    target_w, target_h = target_size
    src_w, src_h = img.size

    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try a few common system fonts, falling back to Pillow's default."""
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


def add_branding(img: Image.Image, brand: str) -> Image.Image:
    """
    Add a sleek colored stripe at the bottom of the canvas and place the
    PUL7SAR logo cleanly in the top-left corner.
    """
    img = img.convert("RGBA")
    width, height = img.size
    color = BRAND_COLORS.get(brand, BRAND_COLORS["red"])

    # --- Bottom brand stripe with a subtle gradient/transparency fade ---
    stripe_height = int(height * 0.10)
    stripe = Image.new("RGBA", (width, stripe_height), color + (235,))
    # Soft top edge fade so the stripe blends into the photo.
    fade = Image.new("L", (width, stripe_height), 255)
    fade_draw = ImageDraw.Draw(fade)
    fade_rows = max(1, stripe_height // 3)
    for row in range(fade_rows):
        alpha = int(255 * (row / fade_rows))
        fade_draw.line([(0, row), (width, row)], fill=alpha)
    stripe.putalpha(fade)
    img.alpha_composite(stripe, dest=(0, height - stripe_height))

    # --- "PUL7SAR" wordmark on the stripe (kept simple & legible) ---
    draw = ImageDraw.Draw(img)
    font = _load_font(int(stripe_height * 0.42))
    text = "PUL7SAR SPORTS"
    text_y = height - stripe_height + int(stripe_height * 0.28)
    draw.text((24, text_y), text, font=font, fill=(255, 255, 255, 255))

    # --- Logo in the top-left corner ---
    logo_path = LOGO_PATHS.get(brand)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_target_w = int(width * 0.14)
            ratio = logo_target_w / logo.width
            logo = logo.resize((logo_target_w, int(logo.height * ratio)), Image.LANCZOS)
            margin = int(width * 0.02)
            img.alpha_composite(logo, dest=(margin, margin))
        except Exception as exc:  # noqa: BLE001
            LOG.warning("Failed to place logo (%s): %s", logo_path, exc)
    else:
        LOG.warning("Logo file not found for brand '%s' at %s -- skipping logo.", brand, logo_path)

    return img.convert("RGB")


def build_final_image(raw_image_bytes: bytes) -> io.BytesIO:
    """Full pipeline: decode -> cover-fit to 1280x720 -> brand -> encode JPEG."""
    source_img = Image.open(io.BytesIO(raw_image_bytes))
    fitted = cover_fit(source_img, CANVAS_SIZE)

    brand = random.choice(list(BRAND_COLORS.keys()))
    branded = add_branding(fitted, brand)

    buffer = io.BytesIO()
    branded.save(buffer, format="JPEG", quality=92, optimize=True)
    buffer.seek(0)
    return buffer


def build_placeholder_image() -> io.BytesIO:
    """Last-resort branded placeholder when no image could be sourced at all."""
    img = Image.new("RGB", CANVAS_SIZE, (30, 30, 30))
    brand = random.choice(list(BRAND_COLORS.keys()))
    branded = add_branding(img, brand)
    buffer = io.BytesIO()
    branded.save(buffer, format="JPEG", quality=92)
    buffer.seek(0)
    return buffer


# ==============================================================================
# STEP 5: TELEGRAM PUBLISHING
# ==============================================================================

def send_telegram_photo(image_buffer: io.BytesIO, caption: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        LOG.error("Telegram credentials are not fully configured.")
        return False

    # Telegram caption hard limit for photos is 1024 characters.
    if len(caption) > 1024:
        caption = caption[:1021].rstrip() + "..."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    def _send():
        image_buffer.seek(0)
        files = {"photo": ("cover.jpg", image_buffer, "image/jpeg")}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": caption}
        r = requests.post(url, data=data, files=files, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram API returned an error: {payload}")
        return payload

    result = _retry(_send, attempts=3, what="Telegram sendPhoto")
    return result is not None


# ==============================================================================
# STEP 6: GIT PERSISTENCE
# ==============================================================================

def git_commit_and_push() -> None:
    """Commit posted_history.json and push it back to the repository."""
    if not GIT_AUTO_PUSH:
        LOG.info("GIT_AUTO_PUSH disabled -- skipping commit/push.")
        return

    def run(cmd: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd, cwd=BASE_DIR, check=True, capture_output=True, text=True
        )

    try:
        run(["git", "config", "user.name", "pul7sar-bot"])
        run(["git", "config", "user.email", "pul7sar-bot@users.noreply.github.com"])
        run(["git", "add", "posted_history.json"])

        # If there's nothing to commit, `git commit` exits non-zero -- handle gracefully.
        status = run(["git", "status", "--porcelain", "posted_history.json"])
        if not status.stdout.strip():
            LOG.info("No changes to posted_history.json -- nothing to commit.")
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        run(["git", "commit", "-m", f"chore: update posted history ({timestamp})"])
        run(["git", "push"])
        LOG.info("posted_history.json committed and pushed successfully.")
    except subprocess.CalledProcessError as exc:
        LOG.error(
            "Git operation failed: %s\nstdout: %s\nstderr: %s",
            exc, exc.stdout, exc.stderr,
        )
    except Exception as exc:  # noqa: BLE001
        LOG.error("Unexpected error during git commit/push: %s", exc)


# ==============================================================================
# MAIN ORCHESTRATION
# ==============================================================================

def _validate_config() -> bool:
    missing = [
        name for name, value in [
            ("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
            ("TELEGRAM_CHANNEL_ID", TELEGRAM_CHANNEL_ID),
            ("GROQ_API_KEY", GROQ_API_KEY),
        ] if not value
    ]
    if missing:
        LOG.critical("Missing required environment variable(s): %s", ", ".join(missing))
        return False
    return True


def process_single_article(article: Dict[str, Any]) -> bool:
    """Run the full pipeline for one article. Returns True on successful publish."""
    LOG.info("Processing article: '%s' (%s)", article["title"], article["source"])

    ai_result = generate_ai_content(article)
    if not ai_result:
        LOG.warning("Skipping article -- AI content generation failed.")
        return False

    image_bytes = source_cover_image(article, ai_result["img_query"])
    if image_bytes:
        try:
            image_buffer = build_final_image(image_bytes)
        except Exception as exc:  # noqa: BLE001
            LOG.error("Image processing failed (%s) -- using placeholder.", exc)
            image_buffer = build_placeholder_image()
    else:
        LOG.warning("No image could be sourced -- using branded placeholder.")
        image_buffer = build_placeholder_image()

    success = send_telegram_photo(image_buffer, ai_result["text"])
    if success:
        LOG.info("Successfully published article: '%s'", article["title"])
    else:
        LOG.error("Failed to publish article to Telegram: '%s'", article["title"])
    return success


def main() -> None:
    LOG.info("========== PUL7SAR Ultimate Sports Engine -- run started ==========")

    if not _validate_config():
        LOG.critical("Aborting run due to invalid configuration.")
        return

    history = load_history()
    raw_articles = fetch_all_articles()
    candidates = filter_and_rank_articles(raw_articles, history)

    if not candidates:
        LOG.info("No fresh, unpublished, high-quality articles found this run.")
        return

    posted_count = 0
    history_changed = False

    for article in candidates:
        if posted_count >= MAX_POSTS_PER_RUN:
            break

        try:
            published = process_single_article(article)
        except Exception as exc:  # noqa: BLE001 - never let one bad article kill the run
            LOG.error("Unhandled error while processing '%s': %s", article["title"], exc)
            published = False

        if published:
            mark_as_posted(article, history)
            history_changed = True
            posted_count += 1
            # Small pause to be a good citizen towards Telegram / Groq rate limits.
            time.sleep(2)

    if history_changed:
        save_history(history)
        git_commit_and_push()
    else:
        LOG.info("No articles were successfully published this run.")

    LOG.info("Posted %d/%d target article(s) this run.", posted_count, MAX_POSTS_PER_RUN)
    LOG.info("========== PUL7SAR Ultimate Sports Engine -- run finished ==========")


if __name__ == "__main__":
    main()
