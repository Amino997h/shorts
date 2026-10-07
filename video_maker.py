import os
import sys
import json
import urllib.request
import urllib.parse
import re
import requests
import time
from urllib.error import URLError, HTTPError
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# --- 1. دوال جلب الصور ---
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
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

# --- 2. دوال الذكاء الاصطناعي (API المحلي) ---
def generate_script(topic):
    api_url = "http://127.0.0.1:8008/v1/chat/completions"
    api_key = "sk-chatgpt-local-secret-key"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Write a short voiceover script for a video about the following topic: "{topic}".
    CRITICAL INSTRUCTION:
    - The script MUST be written in ENGLISH language. Even if the topic is provided in Arabic, you must write the voiceover script in English.
    - The length of the script must be perfectly suited for a 40 to 60 seconds YouTube Short (approx 60 to 80 words).
    - Provide ONLY the English text. Do not add any titles, quotes, or markdown formatting. Just the continuous text.
    """
    
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "stream": False}
    print("\n[الخطوة 1]: جاري التفكير وكتابة السكريبت...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"خطأ في الاتصال بالسيرفر المحلي: {e}")
        return None

def get_image_timings_from_segments(segments):
    api_url = "http://127.0.0.1:8008/v1/chat/completions"
    api_key = "sk-chatgpt-local-secret-key"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Below is the transcribed audio of a video with exact timestamps for each segment:
    {json.dumps(segments, ensure_ascii=False, indent=2)}
    
    Your task is to assign relevant images to cover the entire duration of the audio from start to finish.
    You decide how many images are needed, and the exact start and end time for each image based on the spoken text.
    
    CRITICAL INSTRUCTIONS:
    - Respond ONLY with a valid JSON array of objects. Do not write any explanations or conversational text.
    - Everything in your response MUST be in English.
    - Each object must have:
      * "keyword": A strong, descriptive search keyword in English to find a matching image for this segment.
      * "start": The exact start time in seconds (float).
      * "end": The exact end time in seconds (float).
    """
    
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "stream": False}
    print("\n[الخطوة 4]: إرسال التوقيتات للذكاء الاصطناعي لاختيار الصور وتوقيتها الدقيق...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        text = response.json()['choices'][0]['message']['content'].strip()
        
        if text.startswith("```json"): text = text[7:-3].strip()
        elif text.startswith("```"): text = text[3:-3].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"خطأ أثناء استخراج توقيت الصور: {e}")
        return None

# --- 3. العملية الأساسية ---
def main():
    global_start_time = time.time()
    
    print("\n" + "="*50)
    print("=== 🎬 صانع الفيديوهات الآلي الاحترافي (مع التزامن الدقيق) 🎬 ===")
    print("="*50)
    
    topic = input("\nما هو موضوع الفيديو؟ (مثال: أسرار الفضاء)\n> ").strip()
    if not topic:
        return
        
    script = generate_script(topic)
    if not script: return
    
    print("\n--- السكريبت ---")
    print(script)
    
    workspace = os.path.join(r"C:\Users\User\Documents\antigravity\dazzling-curie", "video_workspace")
    os.makedirs(workspace, exist_ok=True)
        
    print("\n[الخطوة 2]: تحويل النص إلى صوت احترافي...")
    audio_path = os.path.join(workspace, "voiceover.mp3")
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(audio_path)
    
    print("\n[الخطوة 3]: استخراج التوقيت الدقيق للكلمات (Faster-Whisper)...")
    try:
        from faster_whisper import WhisperModel
        # نستخدم موديل صغير للسرعة
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments_iter, info = model.transcribe(audio_path, language="en")
        
        segments = []
        for s in segments_iter:
            segments.append({
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "text": s.text.strip()
            })
    except ImportError:
        print("مكتبة faster-whisper غير مثبتة! سيتم التوقف.")
        return
        
    image_plan = get_image_timings_from_segments(segments)
    if not image_plan: return
    
    print("\n[الخطوة 5]: تحميل الصور بناءً على التوقيت...")
    downloaded_clips_info = []
    
    for i, plan in enumerate(image_plan):
        kw = plan['keyword']
        start_t = plan['start']
        end_t = plan['end']
        duration = end_t - start_t
        
        print(f"[{start_t}s -> {end_t}s] جاري البحث عن: {kw}")
        urls = scrape_bing_images(kw)
        if urls:
            for url in urls[:5]:
                img_path = os.path.join(workspace, f"img_{i}.jpg")
                if download_image(url, img_path):
                    downloaded_clips_info.append({
                        "path": img_path,
                        "start": start_t,
                        "end": end_t,
                        "duration": duration
                    })
                    print(f"✓ تم التحميل.")
                    break
                    
    if not downloaded_clips_info:
        print("فشل تحميل أي صورة.")
        return
        
    print("\n[الخطوة 6]: المونتاج الدقيق والتصدير...")
    try:
        from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ColorClip
        import moviepy.video.fx.all as vfx
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        audio_clip = AudioFileClip(audio_path)
        
        # 1. إعداد فيديو الخلفية الرئيسي
        bg_video_path = r"C:\Users\User\Downloads\Video Project.mp4"
        if os.path.exists(bg_video_path):
            bg_clip = VideoFileClip(bg_video_path)
            # تكبيره ليملأ الشاشة (1920) وقص الزوائد من المنتصف ليكون العرض 1080
            bg_clip = bg_clip.resize(height=1920)
            if bg_clip.w < 1080:
                bg_clip = bg_clip.resize(width=1080)
            x_center = bg_clip.w / 2
            bg_clip = bg_clip.crop(x1=x_center-540, y1=0, x2=x_center+540, y2=1920)
            
            # تكرار الخلفية لتناسب مدة الصوت
            bg_clip = bg_clip.fx(vfx.loop, duration=audio_clip.duration)
        else:
            print("تنبيه: فيديو الخلفية غير موجود، سيتم وضع خلفية سوداء.")
            bg_clip = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(audio_clip.duration)
            
        clips = [bg_clip]
        
        # 2. إضافة الصور بحدود دقيقة (Margin Left/Right 100, Top 350, Bottom 250)
        # المنطقة الآمنة (Safe Zone) عرضها 880 وارتفاعها 1320
        for info in downloaded_clips_info:
            img_path = info["path"]
            
            # التأكد من أن الصورة بنظام الألوان RGB وتجنب أعطال الأبيض والأسود (Grayscale)
            from PIL import Image
            with Image.open(img_path) as pil_img:
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                    pil_img.save(img_path)
                    
            img = ImageClip(img_path)
            w_ratio = 880 / img.w
            h_ratio = 1320 / img.h
            scale = min(w_ratio, h_ratio)
            
            clip = img.resize(scale)
            # توسيطها في منطقة الـ Safe Zone (التي يبدأ الـ Y الخاص بها من 350)
            center_y = 350 + (1320 / 2)
            clip = (clip.set_position(("center", center_y - clip.h / 2))
                        .set_start(info["start"])
                        .set_duration(info["duration"]))
            clips.append(clip)
            
        # 3. إضافة الترجمة المتزامنة بدقة فوق الصورة (في المساحة العلوية من 0 إلى 350 بكسل)
        subs_dir = os.path.join(workspace, "subs")
        os.makedirs(subs_dir, exist_ok=True)
        
        try:
            font = ImageFont.truetype("arialbd.ttf", 60)
        except:
            font = ImageFont.load_default()
            
        for i, seg in enumerate(segments):
            text = seg["text"].strip()
            if not text: continue
            
            # إنشاء صورة شفافة للنص
            img_sub = Image.new('RGBA', (1080, 350), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_sub)
            
            lines = textwrap.wrap(text, width=32)
            # حساب الارتفاع الإجمالي للنص
            total_h = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_h += bbox[3] - bbox[1] + 15
                
            current_y = (350 - total_h) / 2
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                line_h = bbox[3] - bbox[1]
                x = (1080 - line_w) / 2
                
                # كتابة النص بحواف سوداء (Stroke)
                draw.text((x-3, current_y-3), line, font=font, fill="black")
                draw.text((x+3, current_y-3), line, font=font, fill="black")
                draw.text((x-3, current_y+3), line, font=font, fill="black")
                draw.text((x+3, current_y+3), line, font=font, fill="black")
                
                # النص الفعلي باللون الأصفر
                draw.text((x, current_y), line, font=font, fill="yellow")
                current_y += line_h + 15
                
            sub_path = os.path.join(subs_dir, f"sub_{i}.png")
            img_sub.save(sub_path)
            
            sub_clip = (ImageClip(sub_path)
                        .set_start(seg["start"])
                        .set_end(seg["end"])
                        .set_position(("center", 0)))
            clips.append(sub_clip)
            
        video = CompositeVideoClip(clips, size=(1080, 1920))
        video = video.set_audio(audio_clip)
        
        final_video_path = os.path.join(workspace, f"Final_Video.mp4")
        print("\n⏳ جاري تصدير الفيديو (الرجاء الانتظار، قد يستغرق بعض الوقت بناءً على قوة جهازك)...")
        video.write_videofile(final_video_path, fps=24, codec="libx264", audio_codec="aac")
        
        total_time = round(time.time() - global_start_time, 2)
        print("\n" + "="*50)
        print(f"🎉 تم إنتاج الفيديو بتزامن دقيق للصور!")
        print(f"⏱️ مدة العملية كلها: {total_time} ثانية.")
        print(f"📁 المسار: {final_video_path}")
        print("="*50)
        
        os.startfile(final_video_path)
        
    except Exception as e:
        print(f"\nخطأ أثناء المونتاج: {e}")

if __name__ == "__main__":
    main()
