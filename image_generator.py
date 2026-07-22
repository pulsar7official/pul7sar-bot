import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def download_news_image(image_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(image_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert('RGBA')
    except Exception as e:
        print(f"⚠️ تعذر تحميل صورة الخبر الأصلية: {e}")
    return None

def generate_sports_fallback_bg(width, height):
    bg = Image.new('RGBA', (width, height), (10, 12, 18, 255))
    draw = ImageDraw.Draw(bg)
    for y in range(height):
        r = int(12 + (y / height) * 20)
        g = int(15 + (y / height) * 10)
        b = int(25 + (y / height) * 35)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([width // 4, height // 4, 3 * width // 4, 3 * height // 4], fill=(139, 0, 0, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(bg, glow)

def create_pulsar_post_image(headline_text, image_url=None, output_path="pulsar_post.png"):
    width, height = 1080, 1080
    base_img = None
    if image_url:
        base_img = download_news_image(image_url)
        
    if base_img:
        img_ratio = base_img.width / base_img.height
        target_ratio = width / height
        if img_ratio > target_ratio:
            new_width = int(height * img_ratio)
            base_img = base_img.resize((new_width, height), Image.Resampling.LANCZOS)
            left = (new_width - width) // 2
            base_img = base_img.crop((left, 0, left + width, height))
        else:
            new_height = int(width / img_ratio)
            base_img = base_img.resize((width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - height) // 2
            base_img = base_img.crop((0, top, width, top + height))
    else:
        base_img = generate_sports_fallback_bg(width, height)

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    for y in range(160):
        alpha = int(180 * (1 - y / 160))
        draw_ov.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
    for y in range(480, height):
        alpha = int(240 * ((y - 480) / (height - 480)))
        draw_ov.line([(0, y), (width, y)], fill=(8, 10, 15, alpha))

    img = Image.alpha_composite(base_img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)

    primary_red = (180, 0, 0, 255)
    gold = (212, 175, 55, 255)
    dark_card = (16, 18, 26, 235)
    white = (255, 255, 255, 255)

    draw.rectangle([(0, 0), (width, 10)], fill=primary_red)
    draw.rectangle([(0, 10), (width, 14)], fill=gold)

    draw.rectangle([(width - 280, 30), (width - 40, 90)], fill=primary_red)
    draw.rectangle([(40, 30), (220, 90)], fill=gold)

    card_box = [(40, 670), (width - 40, 990)]
    draw.rectangle(card_box, fill=dark_card, outline=(45, 50, 65, 220), width=2)
    draw.rectangle([(width - 55, 670), (width - 40, 990)], fill=primary_red)

    try:
        font_badge = ImageFont.truetype("arial.ttf", 32)
        font_tag = ImageFont.truetype("arial.ttf", 22)
        font_headline = ImageFont.truetype("arial.ttf", 38)
        font_footer = ImageFont.truetype("arial.ttf", 20)
    except:
        font_badge = font_tag = font_headline = font_footer = ImageFont.load_default()

    draw.text((width - 250, 42), "PUL7SAR", fill=white, font=font_badge)
    draw.text((60, 43), "BREAKING", fill=(10, 10, 10, 255), font=font_badge)

    draw.rectangle([(width - 250, 700), (width - 80, 740)], fill=primary_red)
    draw.text((width - 230, 706), "🔴 خبر عاجل", fill=white, font=font_tag)

    words = headline_text.split()
    lines, current_line = [], []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 30:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    y_text = 765
    for line in lines[:3]:
        draw.text((width - 80, y_text), line, fill=white, font=font_headline, anchor="ra")
        y_text += 55

    draw.rectangle([(0, 1030), (width, height)], fill=(10, 10, 12, 255))
    draw.line([(0, 1030), (width, 1030)], fill=gold, width=2)
    
    draw.text((width - 50, 1045), "PUL7SAR | نبض الرياضة العالمية", fill=gold, font=font_footer, anchor="ra")
    draw.text((50, 1045), "@Pulsar7Official", fill=white, font=font_footer)

    img.save(output_path, "PNG")
    return output_path
