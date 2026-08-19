from pathlib import Path
from PIL import Image, ImageDraw
from engine.bootstrap import create_engine
from engine.integration.article_adapter import render_article_with_engine

def _sample_image():
    w,h=1600,1000
    image=Image.new("RGB",(w,h),(16,33,52))
    draw=ImageDraw.Draw(image)
    for y in range(h):
        t=y/max(1,h-1)
        draw.line((0,y,w,y),fill=(int(15+10*t),int(28+60*t),int(55+20*t)))
    draw.rectangle((0,620,w,h),fill=(24,78,55))
    return image

def main():
    engine=create_engine()
    article={"title":"ريال مدريد يحسم المواجهة بثلاثية ويواصل صدارة الدوري","summary":""}
    news=render_article_with_engine(article,engine=engine,selected_image=_sample_image(),entity="real_madrid")
    news_path=Path(__file__).with_name("preview_news.jpg")
    news_path.write_bytes(news)

    default=engine.execute({"template":"default","platform":"telegram"})
    default_path=Path(__file__).with_name("preview_default.jpg")
    default_path.write_bytes(default)

    for path in (news_path,default_path):
        with Image.open(path) as img:
            print(path.name,img.format,img.size,img.mode,path.stat().st_size)

if __name__=="__main__":
    main()
