import os
import json
import re
import requests
import feedparser
from bs4 import BeautifulSoup
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO
from urllib.parse import quote

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

# مصادر الأخبار الرياضية الكبرى
rss_urls = [
    "https://www.skysports.com/rss/12040",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.goal.com/feeds/en/news",
    "https://theathletic.com/feed/",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://www.calciomercato.com/en/rss"
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
            for entry in feed.entries[:10]:
                link = entry.get('link', entry.get('id', ''))
                title = entry.get('title', '')
                
                # استبعاد المسابقات والألغاز
                skip_keywords = ['quiz', 'guess', 'challenge', 'poll', 'vote', '10 things', 'rank']
                if any(kw in title.lower() for kw in skip_keywords):
                    continue

                if link in posted_links or is_topic_repeated(title):
                    continue

                summary = entry.get('summary', title)
                soup_clean = BeautifulSoup(summary, "html.parser")
                clean_summary = soup_clean.get_text()

                # استخراج صورة المصدر الأصلية إن وجدت
                image_url = None
                if 'media_content' in entry and len(entry.media_content) > 0:
                    image_url = entry.media_content[0].get('url')
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    image_url = entry.enclosures[0].get('href')
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
    if any(k in t for k in ['milan', 'liverpool', 'arsenal', 'bayern', 'barcelona', 'barca']):
        return "#E50914"
    elif any(k in t for k in ['real madrid', 'tottenham', 'spurs']):
        return "#FEA326"
    elif any(k in t for k in ['chelsea', 'inter', 'psg']):
        return "#0055A5"
    return BRAND_RED

groq_url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}

if is_what_if_post:
    prompt = """
    أنت محرر رياضي محترف في منصة PUL7SAR. اكتب فقرة تفاعلية مشوقة بعنوان "ماذا لو؟" عن سيناريو تاريخي في كرة القدم.
    - اكتب باللغة العربية الفصحى فقط. ممنوع منعاً باتاً إدراج أي حروف أجنبية، إنجليزية، أو رموز غريبة في النص الإخباري.
    - ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟
    - اختم بسؤال تفاعلي للمتابعين، مع هاشتاق #PUL7SAR.
    
    في نهاية ردك، اترك خطاً جديداً ثم اكتب حصراً كلمات بحث إنجليزية دقيقة للعثور على صورة حقيقية مناسبة بهذا الشكل:
    [IMG_SEARCH: historical football match stadium professional photo]
    """
    stripe_color = BRAND_RED
    article_image_url = None
else:
    prompt = f"""
    أنت محرر صحفي رياضي احترافي لمنصة PUL7SAR.
    تنبيه صارم جداً: اكتب حصراً بلغة عربية فصحى سليمة 100%. ممنوع نهائياً كتابة أي كلمات إنجليزية أو حروف أجنبية داخل النص الإخباري. ترجم كل اسم نادي أو لاعب أو مصطلح إلى العربية بوضوح ودقة.
    يجب أن يكون المنشور خبراً رياضياً حقيقياً، رسمياً، ومباشراً.
    
    الخبر الرياضي الخام:
    العنوان: {selected_article['title']}
    التفاصيل: {selected_article['summary']}

    قم بصياغة منشور رياضي رسمي وشيق يتحدث عن هذا الخبر فقط:
    - ابدأ بعنوان رئيسي جذاب ومثير.
    - اشرح تفاصيل الخبر بأسلوب ممتع ومختصر.
    - استخدم الإيموجيات الرياضية المناسبة.
    - أنهِ المنشور بهشتاجات عربية صحيحة مع هشتاج المنصة #PUL7SAR.

    في نهاية ردك، اترك خطاً جديداً ثم قم باستخراج كلمات بحث إنجليزية دقيقة ومحددة للغاية (تتضمن اسم اللاعب أو النادي أو الحدث الرئيسي المذكور في الخبر) لنتمكن من البحث عن صورة حقيقية واقعية لها في الإنترنت بهذا الشكل حصراً:
    [IMG_SEARCH: exact player name or club and event keywords for photo search]
    """
    stripe_color = get_stripe_color(selected_article['title'] + " " + selected_article['summary'])
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
    img_query = "professional football match player stadium"
    clean_text = full_ai_response.strip()

clean_text = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\u0400-\u04ff\uac00-\ud7af]+', '', clean_text)
clean_text = re.sub(r'\b(light|ban|vs|fc)\b', '', clean_text, flags=re.IGNORECASE)

final_image_path = "processed_image.jpg"
image_success = False

def build_final_image(base_img):
    # قص وتعديل الأبعاد باحترافية تامة بدون أي مط أو تشوه
    img = ImageOps.fit(base_img, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    draw = ImageDraw.Draw(img)

    gradient = Image.new('RGBA', (1280, 220), (0,0,0,0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(220):
        alpha = int((y / 220.0) * 200)
        g_draw.line([(0, y), (1280, y)], fill=(15, 23, 42, alpha))
    img.paste(gradient, (0, 500), gradient)

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
        
        # الشعار في أقصى الزاوية اليسرى العليا بدقة
        img.paste(logo, (8, 8), logo)
    except Exception as e:
        print(f"⚠️ تنبيه حول الشعار: {e}")

    img.save(final_image_path, quality=95)
    return True

base_img = None

# 1. محاولة جلب صورة المصدر الأصلية أولاً
if article_image_url and article_image_url.startswith('http'):
    try:
        print(f"📥 جاري محاولة جلب الصورة الأصلية من المصدر الرياضي...")
        headers_img = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        img_res = requests.get(article_image_url, headers=headers_img, timeout=15)
        if img_res.status_code == 200:
            base_img = Image.open(BytesIO(img_res.content)).convert("RGB")
            print("✅ تم بنجاح استخدام الصورة الأصلية للخبر من المصدر.")
    except Exception as e:
        print(f"⚠️ تعذر تحميل صورة المصدر ({e})...")

# 2. إذا لم تتوفر صورة المصدر، نقوم بالبحث في الإنترنت عن صورة حقيقية باستخدام كلمات البحث المستخرجة
if base_img is None:
    try:
        print(f"🔍 جاري البحث في الإنترنت عن صورة حقيقية للكلمات: {img_query}...")
        search_url = f"https://html.duckduckgo.com/html/?q={quote(img_query + ' football soccer photo')}"
        headers_search = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        search_res = requests.get(search_url, headers=headers_search, timeout=15)
        
        if search_res.status_code == 200:
            soup = BeautifulSoup(search_res.text, 'html.parser')
            # البحث عن أول رابط صوري أو صورة حقيقية في نتائج البحث
            img_candidates = soup.find_all('img')
            for candidate in img_candidates:
                src = candidate.get('src', '')
                if src.startswith('http') and not any(x in src.lower() for x in ['logo', 'icon', 'ad', 'banner']):
                    img_fetch = requests.get(src, headers=headers_search, timeout=10)
                    if img_fetch.status_code == 200:
                        base_img = Image.open(BytesIO(img_fetch.content)).convert("RGB")
                        print("✅ تم بنجاح جلب صورة حقيقية من الإنترنت مرتبطة بالخبر!")
                        break
    except Exception as e:
        print(f"⚠️ تعذر جلب الصورة من الويب ({e})...")

# 3. خطة احتياطية أخيرة في حال تعذر جلب أي صورة (توليد خلفية استادية رياضية احترافية داكنة)
if base_img is None:
    print(f"⚠️ استخدام خلفية استادية رياضية بديلة...")
    base_img = Image.new("RGB", (1280, 720), color=(15, 23, 42))
    draw_bg = ImageDraw.Draw(base_img)
    for i in range(0, 1280, 60):
        draw_bg.line([(i, 0), (i + 150, 720)], fill=(25, 38, 65), width=2)

image_success = build_final_image(base_img)

# النشر على تيليجرام
if image_success and os.path.exists(final_image_path):
    tele_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(final_image_path, 'rb') as photo_file:
        tele_payload = {"chat_id": chat_id, "caption": clean_text}
        tele_res = requests.post(tele_url, data=tele_payload, files={'photo': photo_file})
else:
    tele_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    tele_payload = {"chat_id": chat_id, "text": clean_text}
    tele_res = requests.post(tele_url, json=tele_payload)

if tele_res.status_code == 200:
    print("🚀 تم النشر بنجاح بالاعتماد على الصور الحقيقية!")
    history_data["links"] = list(posted_links)[-100:]
    history_data["titles"] = posted_titles[-100:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)
else:
    raise Exception(f"❌ خطأ تليجرام: {tele_res.text}")
