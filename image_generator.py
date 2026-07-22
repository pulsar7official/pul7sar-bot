import os
import requests
from PIL import Image, ImageDraw
from io import BytesIO

def add_logo_and_stripe(image_url, stripe_color_hex="#FF1E38"):
    final_image_path = "processed_image.jpg"
    try:
        # تحميل الصورة الأصلية للخبر
        img_res = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(img_res.content)).convert("RGB")
        
        img = img.resize((1280, 720))
        draw = ImageDraw.Draw(img)

        # تدرج سفلي للنص
        gradient = Image.new('RGBA', (1280, 200), (0,0,0,0))
        g_draw = ImageDraw.Draw(gradient)
        for y in range(200):
            alpha = int((y / 200.0) * 180)
            g_draw.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
        img.paste(gradient, (0, 520), gradient)

        # شريط التصميم السفلي
        hex_color = stripe_color_hex.lstrip('#')
        rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        draw.rectangle([(0, 710), (1280, 720)], fill=rgb_color)

        # فحص خلفية منطقة الشعار (أعلى اليسار) لاختيار اللون الأنسب
        logo_box = img.crop((45, 35, 285, 115))
        dominant_color = logo_box.resize((1, 1)).getpixel(0)
        r, g, b = dominant_color[:3]
        
        # إذا كانت الخلفية محمرة بشكل قسري، يتحول للأزرق، وإلا فالأحمر أساسي
        use_blue = (r > (g + 40) and r > (b + 40) and r > 90)
        
        red_path = "logo_red.png"
        blue_path = "logo_blue.png"
        
        target_logo_path = blue_path if (use_blue and os.path.exists(blue_path)) else red_path
        if not os.path.exists(target_logo_path):
            target_logo_path = red_path if os.path.exists(red_path) else blue_path

        # لصق الشعار بدقة وتنسيق احترافي
        if os.path.exists(target_logo_path):
            logo = Image.open(target_logo_path).convert("RGBA")
            w_percent = (240 / float(logo.size[0]))
            h_size = int(float(logo.size[1]) * float(w_percent))
            logo = logo.resize((240, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, (45, 35), logo)

        img.save(final_image_path, quality=95)
        return final_image_path
    except Exception as e:
        print(f"⚠️ خطأ في معالجة الصورة: {e}")
        return None
