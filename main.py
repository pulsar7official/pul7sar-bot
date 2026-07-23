final_image_path = "processed_image.jpg"
image_success = False

try:
    # إضافة ترويسة متصفح لكي لا يتم حجب طلب تحميل الصورة من المواقع الإخبارية
    headers_img = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    img_res = requests.get(image_url, headers=headers_img, timeout=10)
    
    if img_res.status_code == 200 and len(img_res.content) > 1000:
        img = Image.open(BytesIO(img_res.content)).convert("RGB")
    else:
        raise Exception("Invalid image content")
        
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

    red_path = "logo_red.png"
    blue_path = "logo_blue.png"
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
    print(f"⚠️ تعذر تحميل صورة الخبر الأصلية، جاري استخدام الصورة الاحتياطية الرياضية: {e}")
    try:
        # صورة احتياطية مضمونة ومستقرة 100%
        fallback_url = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1280&auto=format&fit=crop"
        img_res = requests.get(fallback_url, timeout=10)
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

        if os.path.exists(target_logo_path):
            logo = Image.open(target_logo_path).convert("RGBA")
            w_percent = (240 / float(logo.size[0]))
            h_size = int(float(logo.size[1]) * float(w_percent))
            logo = logo.resize((240, h_size), Image.Resampling.LANCZOS)
            img.paste(logo, (45, 35), logo)

        img.save(final_image_path, quality=95)
        image_success = True
    except Exception as ex:
        print(f"⚠️ فشلت حتى الصورة الاحتياطية: {ex}")
        image_success = False
