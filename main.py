import os
import json
import feedparser
import google.generativeai as genai
from image_generator import create_pulsar_post_image
from publisher import send_to_telegram

# 1. إعداد مفتاح الذكاء الاصطناعي Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 2. مصادر الأخبار العالمية (RSS Feeds مجانية ومحدثة)
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/sport/rss.xml",        # BBC Sport
    "https://www.espn.com/espn/rss/news",            # ESPN
    "https://www.skysports.com/rss/12040",           # Sky Sports
]

HISTORY_FILE = "published_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def extract_image_url(entry):
    """استخراج رابط صورة الخبر إن وجد"""
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
    return None

def rewrite_with_pulsar_style(news_title, news_summary):
    """صياغة الخبر باستخدام Gemini API بأسلوب PUL7SAR"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    أنت المحرر الرياضي الرئيسي لبراند 'PUL7SAR' (نبض الرياضة العالمية).
    قم بإعادة صياغة هذا الخبر الرياضي بأسلوب عربي حماسي، احترافي، ومباشر مخصص لمنصات التواصل الاجتماعي.

    بيانات الخبر الخام:
    - العنوان: {news_title}
    - التفاصيل: {news_summary}

    قم بصياغة النتيجة بالتنسيق التالي حصراً:
    [TITLE]: عنوان عاجل وقصير جداً بأسلوب حماسي مع إيموجي (لا يتجاوز 10 كلمات)
    [CAPTION]: نص المنشور الكامل باللغة العربية، يحتوي على أبرز التفاصيل في نقاط، سؤال تفاعلي للجمهور، وهاشتاغات البراند: #PUL7SAR #نبض_الرياضة_العالمية
    """
    
    response = model.generate_content(prompt)
    return response.text

def parse_ai_response(response_text):
    """تقسيم الرد إلى عنوان ونص منشور"""
    title = "خبر عاجل من PUL7SAR"
    caption = response_text
    
    if "[TITLE]:" in response_text and "[CAPTION]:" in response_text:
        parts = response_text.split("[CAPTION]:")
        title = parts[0].replace("[TITLE]:", "").strip()
        caption = parts[1].strip()
    return title, caption

def process_latest_news():
    """المحرك الرئيسي للجلب والمعالجة والنشر"""
    history = load_history()
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:5]:
            news_id = entry.link
            
            if news_id in history:
                continue
                
            print(f"⚡️ تم العثور على خبر جديد: {entry.title}")
            summary = getattr(entry, 'summary', '')
            image_url = extract_image_url(entry)
            
            # 1. صياغة النص
            raw_ai_output = rewrite_with_pulsar_style(entry.title, summary)
            pulsar_title, pulsar_caption = parse_ai_response(raw_ai_output)
            
            # 2. توليد الصورة
            image_path = create_pulsar_post_image(headline_text=pulsar_title, image_url=image_url)
            
            # 3. النشر الآلي
            full_caption = f"🚨 *{pulsar_title}*\n\n{pulsar_caption}\n\n⚡️ *PUL7SAR | WORLD SPORTS PULSE*"
            send_to_telegram(image_path, full_caption)
            
            # 4. حفظ في السجل
            history.append(news_id)
            save_history(history)
            
            print("✅ تم نشر الخبر وتحديث السجل بنجاح!")
            return
            
    print("ℹ️ لا توجد أخبار جديدة حالياً.")

if __name__ == "__main__":
    process_latest_news()
