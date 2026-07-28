import os
import json
import re
import requests
import feedparser
from bs4 import BeautifulSoup
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageOps, ImageEnhance
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

# شبكة المصادر الموسعة
rss_urls = [
    "https://www.skysports.com/rss/12040",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://news.google.com/rss/search?q=bein+sports+football&hl=ar&gl=AE&ceid=AE:ar",
    "https://news.google.com/rss/search?q=Fabrizio+Romano+transfer+news&hl=en&gl=US&ceid=US:en"
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
                
                skip_keywords = ['quiz', 'guess', 'challenge', 'poll', 'vote', '10 things', 'rank', 'rumour', 'gossip', 'opinion']
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
    - اكتب باللغة العربية الفصحى فقط وبدون أي إدراج لرموز الماركداون أو النجوم.
    - ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟
    - اختم بسؤال تفاعلي للمتابعين، مع هاشتاق #PUL7SAR.
    - اجعل النص مختصراً ومركزا بحيث لا يتجاوز 900 حرف.
    
    في نهاية ردك، اترك خطاً جديداً ثم اكتب حصراً كلمات بحث رياضية إنجليزية مخصصة لكرة القدم بهذا الشكل:
    [IMG_SEARCH: historical football stadium match soccer]
    """
    stripe_color = BRAND_RED
    article_image_url = None
else:
    prompt = f"""
    أنت محرر صحفي رياضي احترافي لمنصة PUL7SAR.
    
    تعليمات صارمة جداً بشأن اللغة والصياغة:
    1. اكتب حصراً بلغة عربية فصحى سليمة ومصقولة 100%. ممنوع نهائياً كتابة أي كلمات إنجليزية، أحرف لاتينية، أو أرقام غير عربية داخل النص الإخباري الرئيسي.
    2. يجب ترجمة كل اسم نادي أو لاعب أو مصطلح رياضي إلى العربية بوضوح ودقة تامة.
    3. الأسلوب: يجب أن يكون الأسلوب خبرياً، رسمياً، ومشوقاً في نفس الوقت، وتجنب الركاكة أو الترجمة الحرفية.
    4. الحجم: اجعل محتوى الخبر موجزاً ومكثفاً بحيث لا يتجاوز نهائياً 900 حرف ليتوافق مع معايير النشر.
    5. التنسيق: ممنوع منعاً باتاً استخدام رموز التنسيق الماركداون (مثل ** أو * أو ~) داخل النص.
    
    الخبر الرياضي الخام المستخرج من المصادر:
    العنوان: {selected_article['title']}
    التفاصيل: {selected_article['summary']}

    قم بصياغة منشور رياضي احترافي بالكامل وفقاً للشروط أعلاه:
    - ابدأ بعنوان رئيسي جذاب ومعبر (خالٍ من أي رموز).
    - اكتب فقرات مفصلة وواضحة تشرح الخبر باختصار.
    - استخدم الإيموجيات الرياضية المناسبة والاحترافية بين الجمل.
    - أنهِ المنشور بهشتاجات عربية صحيحة مع هشتاج المنصة #PUL7SAR.

    في نهاية ردك، اترك خطاً جديداً ثم قم حصراً بإرفاق كلمة مفتاحية رياضية بحتة تخص كرة القدم (مثل اسم نادٍ عالمي أو دوري أو مصطلح كرة قدم بالإنجليزية مثل football match أو soccer player) لتفادي أي التباس سياسي أو شخصي بهذا الشكل:
    [IMG_SEARCH: football match stadium soccer player]
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
    img_query = "football match"
    clean_text = full_ai_response.strip()

def sanitize_news_text(text):
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'[_~`]', '_', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        words = line.split()
        new_words = []
        for w in words:
            if re.search(r'[a-zA-Z]', w) and not w.startswith('#'):
                continue
            new_words.append(w)
        if new_words:
            cleaned_lines.append(' '.join(new_words))
    return '\n'.join(cleaned_lines).strip()

clean_text = sanitize_news_text(clean_text)

if len(clean_text) > 1020:
    clean_text = clean_text[:1017] + "..."

final_image_path = "processed_image.jpg"
image_success = False

def build_final_image(base_img):
    enhancer = ImageEnhance.Sharpness(base_img)
    base_img = enhancer.enhance(1.4)

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
        img.paste(logo, (8, 8), logo)
    except Exception as e:
        print(f"⚠️ تنبيه حول الشعار: {e}")

    img.save(final_image_path, quality=98)
    return True

base_img = None

# [تحصين إضافي] تجاهل صور المصادر الخارجية غير المضمونة إذا كانت تحتوي على روابط مشبوهة واعتمد فقط على أرشيف كرة القدم النظيف
# (تم تعطيل جلب صورة المصدر المباشرة إذا كانت عشوائية، والاعتماد حصراً على استعلامات كرة القدم المحمية)

# [تحصين صارم جداً]: إجبار استعلامات البحث على الارتباط بكلمات كرة القدم حصراً
search_queries = [
    "football match stadium professional soccer",
    "soccer players action match UEFA FIFA",
    img_query + " football soccer match",
    "football player action stadium"
]

api_url = "https://commons.wikimedia.org/w/api.php"
headers_wiki = {"User-Agent": "Pul7sarBot/2.0 (Contact@pul7sar.com)"}

for query in search_queries:
    if base_img is not None:
        break
    try:
        print(f"🔍 جاري البحث في أرشيف صور ويكيميديا الرياضي باستخدام: [{query}]...")
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "format": "json",
            "gsrlimit": 8,
            "prop": "imageinfo",
            "iiprop": "url|size"
        }
        wiki_res = requests.get(api_url, params=params, headers=headers_wiki, timeout=12)
        if wiki_res.status_code == 200:
            data = wiki_res.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                imageinfo = page_info.get("imageinfo", [])
                if imageinfo and "url" in imageinfo[0]:
                    img_url = imageinfo[0]["url"]
                    img_width = imageinfo[0].get("width", 0)
                    
                    # التحقق من أن اسم الملف لا يحتوي على أي مصطلحات سياسية أو غير رياضية
                    unwanted_terms = ['polit', 'minister', 'president', 'meeting', 'summit', 'government', 'sign', 'treaty']
                    if any(term in img_url.lower() for term in unwanted_terms):
                        continue

                    if img_width >= 800 and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        img_fetch = requests.get(img_url, headers=headers_wiki, timeout=10)
                        if img_fetch.status_code == 200:
                            temp_base = Image.open(BytesIO(img_fetch.content)).convert("RGB")
                            base_img = temp_base
                            print("✅ تم العثور على صورة رياضية حقيقية عالية الجودة بنجاح من أرشيف ويكيميديا!")
                            break
    except Exception as e:
        print(f"⚠️ خطأ أثناء البحث بـ ({query}): {e}")

if base_img is None:
    print(f"📥 استخدام صورة بديلة طارئة من أرشيف كرة القدم...")
    fallback_photo_url = "https://upload.wikimedia.org/wikipedia/commons/b/b9/Football_iu_1996.jpg"
    try:
        fb_res = requests.get(fallback_photo_url, headers=headers_wiki, timeout=10)
        if fb_res.status_code == 200:
            base_img = Image.open(BytesIO(fb_res.content)).convert("RGB")
    except:
        pass

if base_img is not None:
    image_success = build_final_image(base_img)
else:
    image_success = False

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
    print("🚀 تم النشر بنجاح وبأعلى معايير النقاء والجودة!")
    history_data["links"] = list(posted_links)[-100:]
    history_data["titles"] = posted_titles[-100:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)
else:
    raise Exception(f"❌ خطأ تليجرام: {tele_res.text}")
