
import os
import json
import re
import requests
import feedparser
from bs4 import BeautifulSoup
import random
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO

# قراءة مفاتيح التشغيل
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

# مصادر الأخبار
rss_urls = [
    "https://www.skysports.com/rss/12040",
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.goal.com/feeds/en/news",
    "https://theathletic.com/feed/"
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
                
                if link in posted_links or is_topic_repeated(title):
                    continue

                summary = entry.get('summary', title)
                soup_clean = BeautifulSoup(summary, "html.parser")
                clean_summary = soup_clean.get_text()

                image_url = None
                if 'media_content' in entry and len(entry.media_content) > 0:
                    image_url = entry.media_content[0].get('url')
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    image_url = entry.enclosures[0].get('href')

                if not image_url or not image_url.startswith('http'):
                    image_url = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1280&auto=format&fit=crop"

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
    - اكتب باللغة العربية الفصحى فقط. ممنوع منعاً باتاً إدراج أي حروف أجنبية، إنجليزية، أو رموز غريبة.
    - ابدأ بعنوان مثير يبدأ بـ ⏳ ماذا لو؟
    - اختم بسؤال تفاعلي للمتابعين، مع هاشتاق #PUL7SAR.
    """
    image_url = "https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1280&auto=format&fit=crop"
    stripe_color = BRAND_RED
else:
    prompt = f"""
    أنت محرر صحفي رياضي احترافي لمنصة PUL7SAR.
    تنبيه صارم جداً: اكتب حصراً بلغة عربية فصحى سليمة 100%. ممنوع نهائياً كتابة أي كلمات إنجليزية أو حروف أجنبية أو رموز غريبة. ترجم كل اسم نادي أو لاعب أو مصطلح إلى العربية بوضوح ودقة.
    
    الخبر الرياضي الخام:
    العنوان: {selected_article['title']}
    التفاصيل: {selected_article['summary']}

    قم بصياغة منشور رياضي مستقل وشيق يتحدث عن هذا الخبر فقط:
    - ابدأ بعنوان رئيسي جذاب ومثير.
    - اشرح تفاصيل الخبر بأسلوب ممتع ومختصر.
    - استخدم الإيموجيات الرياضية المناسبة.
    - أنهِ المنشور بهشتاجات عربية صحيحة مع هشتاج المنصة #PUL7SAR.
    """
    image_url = selected_article['image']
    stripe_color = get_stripe_color(selected_article['title'] + " " + selected_article['summary'])

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": prompt}]
}

res = requests.post(groq_url, json=payload, headers=headers)
if res.status_code != 200:
    raise Exception(f"❌ خطأ من Groq: {res.text}")

raw_text = res.json()['choices'][0]['message']['content']

clean_text = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\u0400-\u04ff\uac00-\ud7af]+', '', raw_text)
clean_text = re.sub(r'\b(light|ban|vs|fc)\b', '', clean_text, flags=re.IGNORECASE)

final_image_path = "processed_image.jpg"
image_success = False

try:
    img_res = requests.get(image_url, timeout=10)
    img = Image.open(BytesIO(img_res.content)).convert("RGB")
    
    img = img.resize((1280, 720))
    draw = ImageDraw.Draw(img)

    gradient = Image.new('RGBA', (1280, 200), (0,0,0,0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(200):
        alpha = int((y / 200.0) * 180)
        g_draw.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
    img.paste(gradient, (0, 520), gradient)

    hex_color = stripe_color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([(0, 710), (1280, 720)], fill=rgb_color)

    logo_box = img.crop((45, 35, 285, 115))
    dominant_color = logo_box.resize((1, 1)).getpixel(0)
    r, g, b = dominant_color[:3]
    
    use_blue = (r > (g + 40) and r > (b + 40) and r > 90)
    
    red_path = "logo_red.png"
    blue_path = "logo_blue.png"
    
    target_logo_path = blue_path if (use_blue and os.path.exists(blue_path)) else red_path
    if not os.path.exists(target_logo_path):
        target_logo_path = red_path if os.path.exists(red_path) else blue_path

    if os.path.exists(target_logo_path):
        logo = Image.open(target_logo_path).convert("RGBA")
        w_percent = (240 / float(logo.size[0]))
        h_size = int(float(logo.size[1]) * float(w_percent))
        logo = logo.resize((240, h_size), Image.Resampling.LANCZOS)
        img.paste(logo, (45, 35), logo)

    img.save(final_image_path, quality=95)
    image_success = True
except Exception as e:
    print(f"⚠️ خطأ في معالجة الصورة: {e}")
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
    print("🚀 تم النشر بنجاح مع الصورة والشعار الاحترافي!")
    history_data["links"] = list(posted_links)[-100:]
    history_data["titles"] = posted_titles[-100:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False)
else:
    raise Exception(f"❌ خطأ تليجرام: {tele_res.text}")
