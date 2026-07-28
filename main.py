import os
import json
import re
import requests
import feedparser
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter
from io import BytesIO

# قراءة مفاتيح التشغيل الأساسية
groq_key = os.environ.get("GROQ_API_KEY", "").strip()
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# سجل منع التكرار
history_file = "posted_history.json"
history_data = {"links": [], "titles": []}
if os.path.exists(history_file):
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, list):
                history_data["links"] = content
            elif isinstance(content, dict):
                history_data = content
    except:
        pass

posted_links = set(history_data.get("links", []))
posted_titles = [t.lower() for t in history_data.get("titles", [])]

def is_topic_repeated(new_title):
    nt = new_title.lower()
    for pt in posted_titles:
        common_words = set(nt.split()).intersection(set(pt.split()))
        if len(common_words) >= 3:
            return True
    return False

# [تحديث المصادر مع قيد زمني صارم &tbs=qdr:d لجلب أخبار الـ 24 ساعة الأخيرة فقط]
rss_urls = [
    "https://www.skysports.com/rss/12040",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://news.google.com/rss/search?q=football+transfer+news+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d",
    "https://news.google.com/rss/search?q=champions+league+news+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d",
    "https://news.google.com/rss/search?q=real+madrid+barcelona+milan+arabic&hl=ar&gl=AE&ceid=AE:ar&tbs=qdr:d"
]

current_hour = datetime.utcnow().hour
is_what_if_time = (current_hour == 18)

selected_article = None
is_what_if_post = False

if is_what_if_time:
    is_what_if_post = True
else:
    articles = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                link = entry.get('link', entry.get('id', ''))
                title = entry.get('title', '')
                
                # فحص زمني دقيق: استبعاد أي خبر مضى عليه أكثر من 48 ساعة
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_timestamp = time.mktime(entry.published_parsed)
                    if time.time() - pub_timestamp > 48 * 3600:
                        continue

                skip_keywords = ['quiz', 'guess', 'challenge', 'poll', 'vote', '10 things', 'rank', 'rumour']
                if any(kw in title.lower() for kw in skip_keywords):
                    continue

                if link in posted_links or is_topic_repeated(title):
                    continue

                summary = entry.get('summary', title)
                soup_clean = BeautifulSoup(summary, "html.parser")
                clean_summary = soup_clean.get_text()

                image_url = None
                if 'media_content' in entry and len(entry.media_content) > 0:
                    image_url = entry.media_content[0].get('url')
                elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                    image_url = entry.media_thumbnail[0].get('url')
                else:
                    img_tag = soup_clean.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag.get('src')

                articles.append({
                    'title': title,
                    'summary': clean_summary,
                    'link': link,
                    'image': image_url
                })
        except Exception as e:
            print(f"⚠️ خطأ في المصدر {url}: {e}")

    if articles:
        selected_article = random.choice(articles)
        posted_links.add(selected_article['link'])
        posted_titles.append(selected_article['title'])
    else:
        exit(0)

BRAND_RED = "#FF1E38"

def get_stripe_color(text):
    t = text.lower()
    if any(k in t for k in ['milan', 'liverpool', 'arsenal', 'bayern', 'barcelona']):
        return "#E50914"
    elif any(k in t for k in ['real madrid', 'tottenham', 'f1', 'فورمولا']):
        return "#FEA326"
    elif any(k in t for k in ['chelsea', 'inter', 'psg', 'سيدات', 'womens']):
        return "#0055A5"
    return BRAND_RED

groq_url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}

article_text_sample = (selected_article['title'] + " " + selected_article['summary']) if not is_what_if_post else ""
is_women_topic = any(k in article_text_sample.lower() for k in ['سيدات', 'نسائية', 'women', 'female', 'girls'])

if is_what_if_post:
    prompt = """
    أنت محرر رياضي محترف في منصة PUL7SAR. اكتب فقرة تفاعلية مشوقة بعنوان "ماذا لو؟" عن سيناريو تاريخي في كرة القدم.
    - اكتب باللغة العربية الفصحى فقط وبدون أي إدراج لرموز الماركداون أو النجوم أو الكلمات الأجنبية أو الألفاظ الركيكة.
    - ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟
    - اختم بسؤال تفاعلي للمتابعين، مع هاشتاق #PUL7SAR.
    - حجم النص ألا يتجاوز 900 حرف.
    
    في نهاية ردك، اترك خطاً جديداً ثم اكتب حصراً كلمات بحث إنجليزية رياضية بهذا الشكل:
    [IMG_SEARCH: modern professional football stadium match soccer goal celebration]
    """
    stripe_color = BRAND_RED
    article_image_url = None
else:
    gender_tag = "womens football match professional action" if is_women_topic else "modern professional football match action stadium"
    prompt = f"""
    أنت محرر صحفي رياضي احترافي لمنصة PUL7SAR.
    
    تعليمات صارمة جداً بشأن اللغة والصياغة:
    1. اكتب حصراً بلغة عربية فصحى سليمة، رصينة، ومصقولة احترافياً 100%. ممنوع منعاً باتاً استخدام أي كلمات ركيكة أو عامية أو غير مفهومة.
    2. ممنوع نهائياً ولأي سبب كان كتابة أي كلمات أجنبية داخل النص الإخباري. الأسماء الأجنبية تُكتب بحروف عربية معربة فقط.
    3. الأسلوب: خبري، رسمي، ومشوق. الحجم: لا يتجاوز 900 حرف.
    4. التنسيق: ممنوع استخدام رموز التنسيق الماركداون (مثل ** أو * أو ~).
    
    الخبر الرياضي الخام المستخرج من المصادر (الحديثة حصراً):
    العنوان: {selected_article['title']}
    التفاصيل: {selected_article['summary']}

    قم بصياغة منشور رياضي احترافي بالكامل:
    - ابدأ بعنوان رئيسي جذاب ومعبر.
    - اشرح الخبر بفقرات واضحة مع إيموجيات رياضية مناسبة.
    - أنهِ المنشور لهاشتاقات عربية مناسبة مع #PUL7SAR.

    في نهاية ردك، اترك خطاً جديداً ثم حدد بدقة نوع الرياضة بالإنجليزية لتستخدم في البحث عن صورة صحيحة حديثة بهذا الشكل حصراً:
    [IMG_SEARCH: {gender_tag}]
    """
    stripe_color = get_stripe_color(article_text_sample)
    article_image_url = selected_article.get('image')

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": prompt}]
}

res = requests.post(groq_url, json=payload, headers=headers)
if res.status_code != 200:
    raise Exception(f"❌ خطأ من Groq: {res.text}")

full_ai_response = res.json()['choices'][0]['message']['content']

image_search_match = re.search(r'\[IMG_SEARCH:\s*([\s\S]*?)\]', full_ai_response)
if image_search_match:
    img_query = image_search_match.group(1).strip()
    clean_text = full_ai_response.replace(image_search_match.group(0), "").strip()
else:
    img_query = "womens football match" if is_women_topic else "modern football match stadium"
    clean_text = full_ai_response.strip()

def sanitize_news_text(text):
    text = re.sub(r'[\*\*_~`]', '', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        words = line.split()
        new_words = []
        for w in words:
            if w.startswith('#') or w.isdigit() or not any(char.isalnum() for char in w):
                new_words.append(w)
                continue
            if re.search(r'[a-zA-Z\u0400-\u04FF\u4E00-\u9FFF]', w):
                continue
            if re.search(r'[\u0600-\u06FF]', w):
                new_words.append(w)
        if new_words:
            cleaned_lines.append(' '.join(new_words))
    return '\n'.join(cleaned_lines).strip()

clean_text = sanitize_news_text(clean_text)

if len(clean_text) > 1020:
    clean_text = clean_text[:1017] + "..."

final_image_path = "processed_image.jpg"

def build_final_image(base_img):
    canvas = Image.new("RGB", (1280, 720), (15, 23, 42))
    
    bg = base_img.copy()
    bg = ImageOps.fit(bg, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    bg = bg.filter(ImageFilter.GaussianBlur(20))
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.35)
    canvas.paste(bg, (0, 0))
    
    base_img.thumbnail((1200, 520), Image.Resampling.LANCZOS)
    img_w, img_h = base_img.size
    x_offset = (1280 - img_w) // 2
    y_offset = 60 + (500 - img_h) // 2
    canvas.paste(base_img, (x_offset, y_offset))
    
    draw = ImageDraw.Draw(canvas)
    
    gradient = Image.new('RGBA', (1280, 220), (0,0,0,0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(220):
        alpha = int((y / 220.0) * 210)
        g_draw.line([(0, y), (1280, y)], fill=(15, 23, 42, alpha))
    canvas.paste(gradient, (0, 500), gradient)

    hex_color = stripe_color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([(0, 710), (1280, 720)], fill=rgb_color)

    red_path = "logo_red.png"
    blue_path = "logo_blue.png"
    target_logo_path = red_path if os.path.exists(red_path) else blue_path

    try:
        logo = Image.open(target_logo_path).convert("RGBA")
        w_percent = (190 / float(logo.size[0]))
        h_size = int(float(logo.size[1]) * float(w_percent))
        logo = logo.resize((190, h_size), Image.Resampling.LANCZOS)
        canvas.paste(logo, (8, 8), logo)
    except Exception as e:
        print(f"⚠️ تنبيه حول الشعار: {e}")

    canvas.save(final_image_path, quality=98)
    return True

base_img = None

if selected_article and selected_article.get('image'):
    try:
        res_art_img = requests.get(selected_article['image'], timeout=8)
        if res_art_img.status_code == 200:
            temp_img = Image.open(BytesIO(res_art_img.content)).convert("RGB")
            if temp_img.size[0] >= 700:
                base_img = temp_img
    except:
        pass

if base_img is None:
    api_url = "https://commons.wikimedia.org/w/api.php"
    headers_wiki = {"User-Agent": "Pul7sarBot/2.0 (Contact@pul7sar.com)"}
    try:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": img_query,
            "gsrnamespace": 6,
            "format": "json",
            "gsrlimit": 6,
            "prop": "imageinfo",
            "iiprop": "url|size"
        }
        wiki_res = requests.get(api_url, params=params, headers=headers_wiki, timeout=10)
        if wiki_res.status_code == 200:
            data = wiki_res.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                imageinfo = page_info.get("imageinfo", [])
                if imageinfo and "url" in imageinfo[0]:
                    img_url = imageinfo[0]["url"]
                    img_width = imageinfo[0].get("width", 0)
                    if img_width >= 800 and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        img_fetch = requests.get(img_url, headers=headers_wiki, timeout=8)
                        if img_fetch.status_code == 200:
                            base_img = Image.open(BytesIO(img_fetch.content)).convert("RGB")
                            break
    except:
        pass

if base_img is None:
    fallback_canvas = Image.new("RGB", (1280, 720), (15, 23, 42))
    draw_fb = ImageDraw.Draw(fallback_canvas)
    for i in range(720):
        c = int(15 + (i / 720) * 30)
        draw_fb.line([(0, i), (1280, i)], fill=(c, c + 8, c + 20))
    draw_fb.rectangle([(100, 100), (1180, 620)], outline=(255, 30, 56), width=3)
    draw_fb.text((640, 320), "PUL7SAR SPORTS", fill=(255, 255, 255), anchor="mm")
    base_img = fallback_canvas

image_success = build_final_image(base_img)

if image_success and os.path.exists(final_image_path):
    tele_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(final_image_path, 'rb') as photo_file:
        tele_payload = {"chat_id": chat_id, "caption": clean_text}
        tele_res = requests.post(tele_url, data=tele_payload, files={'photo': photo_file})
else:
    tele_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(final_image_path, 'rb') as photo_file:
        tele_payload = {"chat_id": chat_id, "caption": clean_text}
        tele_res = requests.post(tele_url, data=tele_payload, files={'photo': photo_file})

if tele_res.status_code == 200:
    history_data["links"] = list(posted_links)[-100:]
    history_data["titles"] = posted_titles[-100:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)
else:
    raise Exception(f"❌ خطأ تليجرام: {tele_res.text}")
