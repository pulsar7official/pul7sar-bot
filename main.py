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

# شبكة المصادر الموسعة (تضم الخلاصات التقليدية وخلاصات جوجل المخصصة لجلب أخبار بي إن سبورت وصحافة الانتقالات)
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
    
    في نهاية ردك، اترك خطاً جديداً ثم اكتب حصراً كلمات بحث إنجليزية دقيقة للعثور على صورة حقيقية بهذا الشكل:
    [IMG_SEARCH: historical football stadium match]
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
    4. التنسيق: ممنوع منعاً باتاً استخدام رموز التنسيق الماركداون (مثل ** أو * أو ~) داخل النص.
    
    الخبر الرياضي الخام المستخرج من المصادر:
    العنوان: {selected_article['title']}
    التفاصيل: {selected_article['summary']}

    قم بصياغة منشور رياضي احترافي بالكامل وفقاً للشروط أعلاه:
    - ابدأ بعنوان رئيسي جذاب ومعبر (خالٍ من أي رموز).
    - اكتب فقرات مفصلة وواضحة تشرح الخبر.
    - استخدم الإيموجيات الرياضية المناسبة والاحترافية بين الجمل.
    - أنهِ المنشور بهشتاجات عربية صحيحة مع هشتاج المنصة #PUL7SAR.

    في نهاية ردك، اترك خطاً جديداً ثم قم باستخراج اسم اللاعب الأساسي أو النادي أو الكلمات المفتاحية باللغة الإنجليزية للبحث عن صورة حقيقية له في أرشيف الويب بهذا الشكل حصراً:
    [IMG_SEARCH: exact player or club name keywords]
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
    img_query = "football player match"
    clean_text = full_ai_response.strip()

# [تحصين إضافي] دالة فلترة صارمة جداً لحذف أي كلمات أجنبية تسربت داخل النص العربي
def sanitize_news_text(text):
    # حذف رموز التنسيق والرموز الغريبة نهائياً
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'[_~`]', '_', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        words = line.split()
        new_words = []
        for w in words:
            # حذف أي كلمة تحتوي على حروف إنجليزية ما لم تكن هاشتاقاً يبدأ بـ #
            if re.search(r'[a-zA-Z]', w) and not w.startswith('#'):
                continue
            new_words.append(w)
        if new_words:
            cleaned_lines.append(' '.join(new_words))
    return '\n'.join(cleaned_lines).strip()

# تطبيق الفلترة الحازمة
clean_text = sanitize_news_text(clean_text)

final_image_path = "processed_image.jpg"
image_success = False

def build_final_image(base_img):
    # رفع دقة الصورة وزيادة الحِدة (Sharpness) لضمان جودة فائقة النقاء
    enhancer = ImageEnhance.Sharpness(
