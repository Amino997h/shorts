import os
import sys
import glob
import json
import urllib.request
import urllib.parse
import re
import requests
from urllib.error import URLError, HTTPError
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

# --- 1. دوال جلب الصور (البحث من Bing) ---
def scrape_bing_images(query):
    url = "https://www.bing.com/images/async?q=" + urllib.parse.quote(query) + "&first=1&count=20"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        urls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html)
        if not urls:
            urls = re.findall(r'murl":"(.*?)"', html)
        return urls
    except Exception as e:
        print(f"خطأ أثناء البحث عن الصورة: {e}")
        return []

def download_image(url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    safe_url = urllib.parse.quote(url, safe=':/&?=#+;@%')
    req = urllib.request.Request(safe_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        return True
    except:
        return False

# --- 2. دوال الذكاء الاصطناعي (باستخدام API المحلي الخاص بك) ---
def generate_script_and_keywords(topic):
    # نستخدم السيرفر المحلي الخاص بك
    api_url = "http://127.0.0.1:8008/v1/chat/completions"
    api_key = "sk-chatgpt-local-secret-key"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    أريد إنشاء فيديو قصير عن الموضوع التالي: "{topic}"
    الرجاء توفير مخرجاتك في هذا التنسيق بالضبط، بدون أي نص إضافي:

    SCRIPT:
    [اكتب هنا النص المشوق للفيديو باللغة العربية، يجب أن يكون متصلاً وبدون فواصل أو ترقيم لكي يقرأه المعلق الصوتي بشكل طبيعي ومستمر. يجب أن يكون طوله حوالي 5 أسطر]

    IMAGES:
    [اكتب هنا 5 كلمات مفتاحية قوية للبحث عن صور تناسب النص. يجب أن تكون الكلمات المفتاحية باللغة الإنجليزية لنتائج بحث أدق، ومفصولة بفاصلة. مثال: ancient computer, old floppy disk, modern laptop, server room, artificial intelligence]
    """
    
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    print("\nجاري التفكير وكتابة السكريبت باستخدام السيرفر المحلي الخاص بك...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        text = data['choices'][0]['message']['content']
        
        script_part = text.split("SCRIPT:")[1].split("IMAGES:")[0].strip()
        images_part = text.split("IMAGES:")[1].strip()
        keywords = [k.strip() for k in images_part.split(",") if k.strip()]
        
        return script_part, keywords
    except Exception as e:
        print(f"\nحدث خطأ في الاتصال بالسيرفر المحلي (تأكد من تشغيل Start_ChatGPT_API.bat): {e}")
        return None, []

# --- 3. العملية الأساسية ---
def main():
    print("\n" + "="*50)
    print("=== 🎬 صانع الفيديوهات الآلي بالذكاء الاصطناعي 🎬 ===")
    print("="*50)
    
    topic = input("\nما هو موضوع الفيديو الذي تريد صنعه؟ (مثال: الذكاء الاصطناعي، تاريخ الأندلس...)\n> ").strip()
    if not topic:
        return
        
    # الخطوة 1: توليد السكريبت
    script, keywords = generate_script_and_keywords(topic)
    if not script:
        return
        
    print("\n--- السكريبت الذي تم تأليفه ---")
    print(script)
    print("---------------------------------")
    
    # إعداد مجلد العمل
    workspace = os.path.join(r"C:\Users\User\Documents\antigravity\dazzling-curie", "video_workspace")
    if not os.path.exists(workspace):
        os.makedirs(workspace)
        
    # الخطوة 2: تحويل النص إلى صوت
    print("\n[الخطوة 2]: تحويل النص إلى صوت احترافي...")
    audio_path = os.path.join(workspace, "voiceover.mp3")
    try:
        tts = gTTS(text=script, lang='ar', slow=False)
        tts.save(audio_path)
        print(f"تم تسجيل الصوت وحفظه بنجاح.")
    except Exception as e:
        print(f"فشل في إنشاء الصوت: {e}")
        return
    
    # الخطوة 3: تحميل الصور
    print("\n[الخطوة 3]: استخراج الصور المناسبة من الإنترنت...")
    downloaded_images = []
    
    for i, kw in enumerate(keywords[:5]): # نأخذ أول 5 كلمات مفتاحية
        print(f"البحث عن: {kw}")
        urls = scrape_bing_images(kw)
        if urls:
            for url in urls[:5]:
                img_path = os.path.join(workspace, f"img_{i}.jpg")
                if download_image(url, img_path):
                    downloaded_images.append(img_path)
                    print(f"✓ تم تحميل الصورة {i+1} بنجاح.")
                    break
                    
    if not downloaded_images:
        print("فشل في تحميل الصور، لا يمكن إكمال المونتاج.")
        return
        
    # الخطوة 4: المونتاج
    print("\n[الخطوة 4]: دمج الصور والصوت لإنتاج الفيديو النهائي...")
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
        
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        duration_per_image = audio_duration / len(downloaded_images)
        
        clips = []
        for img_path in downloaded_images:
            clip = ImageClip(img_path).set_duration(duration_per_image)
            clips.append(clip)
            
        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio_clip)
        
        final_video_path = os.path.join(workspace, f"Final_Video.mp4")
        print("\n⏳ جاري تصدير الفيديو (يرجى الانتظار، قد يستغرق دقيقة)...")
        
        video.write_videofile(final_video_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
        
        print("\n" + "="*50)
        print(f"🎉 مبرووووك! تم إنتاج الفيديو بنجاح:")
        print(f"📁 المسار: {final_video_path}")
        print("="*50)
        
        os.startfile(final_video_path)
        
    except Exception as e:
        print(f"\nحدث خطأ مفاجئ أثناء المونتاج: {e}")

if __name__ == "__main__":
    main()
