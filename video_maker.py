# تم التحديث عبر MCP بنجاح
import os
import argparse
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
                
        # التحقق من أن الملف المحمل هو صورة صالحة وليس تالفاً
        from PIL import Image
        with Image.open(save_path) as img:
            img.verify()
            
        return True
    except:
        return False

import os
import json
import time

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    default_config = {
        "api_url": "http://127.0.0.1:8008/v1/chat/completions",
        "api_key": "sk-chatgpt-local-secret-key",
        "bot_token": "8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ",
        "channel_id": "-1004247712091"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

CONFIG = load_config()

# --- 2. دوال الذكاء الاصطناعي (API المحلي) ---
def generate_script(topic):
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
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
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
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

# --- 4. النشر على تيليجرام ---
def upload_to_telegram(video_path, topic):
    print("\n[الخطوة 7]: جاري توليد وصف للفيديو لنشره على تيليجرام...")
    import requests
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Write a Telegram post for a video about "{topic}".
    The post MUST be written in ENGLISH language (even if the topic is provided in Arabic).
    Follow this EXACT structure:
    Line 1: An attractive title related to the video (with an emoji).
    Line 2: A short description (first line).
    Line 3: A short description (second line).
    Line 4: 5 relevant viral hashtags.
    
    Do not add any other lines or text. Just exactly 4 lines in English.
    """
    
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "stream": False}
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        caption = response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"خطأ أثناء توليد الوصف: {e}")
        caption = f"New video about: {topic}\n\n#video #shorts #viral #trending"
        
    print(f"\nالوصف الجاهز:\n{caption}\n")
    print("جاري الرفع إلى قناة التيليجرام (قد يستغرق بعض الوقت حسب حجم الفيديو)...")
    
    bot_token = CONFIG.get("bot_token")
    channel_id = CONFIG.get("channel_id")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    try:
        with open(video_path, 'rb') as video_file:
            data = {'chat_id': channel_id, 'caption': caption}
            files = {'video': video_file}
            resp = requests.post(url, data=data, files=files, timeout=600)
            resp.raise_for_status()
        print("✓ تم النشر على قناة تيليجرام بنجاح!")
    except Exception as e:
        print(f"خطأ أثناء النشر على تيليجرام: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args, unknown = parser.parse_known_args()

    global_start_time = time.time()
    
    print("\n" + "="*50)
    print("=== 🎬 صانع الفيديوهات الآلي الاحترافي (مع التزامن الدقيق) 🎬 ===")
    print("="*50)
    
    if args.topic:
        topic = args.topic.strip()
        print(f"\nموضوع الفيديو المستلم: {topic}")
    else:
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
        segments_iter, info = model.transcribe(audio_path, language="en", word_timestamps=True)
        
        words_list = []
        for s in segments_iter:
            for w in s.words:
                words_list.append(w)
                
        segments = []
        chunk_size = 5
        for i in range(0, len(words_list), chunk_size):
            chunk = words_list[i:i+chunk_size]
            text = "".join([w.word for w in chunk]).strip()
            segments.append({
                "start": round(chunk[0].start, 2),
                "end": round(chunk[-1].end, 2),
                "text": text,
                "words": [{"word": w.word, "start": w.start, "end": w.end} for w in chunk]
            })
    except ImportError:
        print("مكتبة faster-whisper غير مثبتة! سيتم التوقف.")
        return
    print("\n[الخطوة 4]: إرسال التوقيتات للذكاء الاصطناعي لاختيار الصور وتوقيتها الدقيق...")
    lite_segments = [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments]
    image_plan = get_image_timings_from_segments(lite_segments)
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
        from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ColorClip, VideoClip
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
        # المنطقة الآمنة عرضها 880 وارتفاعها 1220 (لترك 450 بكسل للنص)
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
            h_ratio = 1220 / img.h
            scale = min(w_ratio, h_ratio)
            
            clip = img.resize(scale)
            # توسيطها في منطقة الـ Safe Zone (التي يبدأ الـ Y الخاص بها من 350)
            center_y = 450 + (1220 / 2)
            clip = (clip.set_position(("center", center_y - clip.h / 2))
                        .set_start(info["start"])
                        .set_duration(info["duration"]))
            clips.append(clip)
            
                # 3. إضافة الترجمة المتزامنة مع تأثير الكتابة الديناميكي
        try:
            font = ImageFont.truetype("arialbd.ttf", 60)
        except:
            font = ImageFont.load_default()
            
        def get_visible_text(words_list, t):
            text = ""
            for w in words_list:
                if t >= w['end']:
                    text += w['word']
                elif t > w['start']:
                    duration = w['end'] - w['start']
                    if duration <= 0: duration = 0.001
                    progress = (t - w['start']) / duration
                    char_count = int(len(w['word']) * progress)
                    text += w['word'][:char_count]
                    break
                else:
                    break
            return text.lstrip()
            
        def get_visible_lines(visible_text, full_lines):
            visible_lines = []
            remaining = len(visible_text)
            for line in full_lines:
                if remaining <= 0:
                    break
                if remaining >= len(line):
                    visible_lines.append(line)
                    remaining -= len(line) + 1
                else:
                    visible_lines.append(line[:remaining])
                    remaining = 0
            return visible_lines

        for i, seg in enumerate(segments):
            text = seg["text"].strip()
            if not text: continue
            words = seg.get("words", [])
            if not words: continue
            
            full_lines = textwrap.wrap(text, width=32)
            
            total_h = 0
            line_metrics = []
            dummy_img = Image.new('RGBA', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            for line in full_lines:
                bbox = dummy_draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                line_metrics.append({'w': w, 'h': h, 'line': line})
                total_h += h + 15
            
            start_y = (450 - total_h) / 2
            
            for metric in line_metrics:
                metric['x'] = (1080 - metric['w']) / 2
                metric['y'] = start_y
                start_y += metric['h'] + 15

            class TextClipGenerator:
                def __init__(self, full_lines, line_metrics, words):
                    self.full_lines = full_lines
                    self.line_metrics = line_metrics
                    self.words = words
                    self.last_t = -1
                    self.last_img = None
                    
                def generate(self, t):
                    if t == self.last_t and self.last_img is not None:
                        return self.last_img
                        
                    img_sub = Image.new('RGBA', (1080, 450), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img_sub)
                    current_global_t = t + self.words[0]['start']
                    
                    vis_text = get_visible_text(self.words, current_global_t)
                    vis_lines = get_visible_lines(vis_text, self.full_lines)
                    
                    import numpy as np
                    if not vis_lines:
                        self.last_img = np.array(img_sub)
                        self.last_t = t
                        return self.last_img
                        
                    for idx, v_line in enumerate(vis_lines):
                        if not v_line: continue
                        x = self.line_metrics[idx]['x']
                        y = self.line_metrics[idx]['y']
                        
                        draw.text((x-3, y-3), v_line, font=font, fill="black")
                        draw.text((x+3, y-3), v_line, font=font, fill="black")
                        draw.text((x-3, y+3), v_line, font=font, fill="black")
                        draw.text((x+3, y+3), v_line, font=font, fill="black")
                        
                        draw.text((x, y), v_line, font=font, fill="yellow")
                    
                    self.last_img = np.array(img_sub)
                    self.last_t = t
                    return self.last_img
                    
                def get_rgb(self, t):
                    return self.generate(t)[:, :, :3]
                    
                def get_mask(self, t):
                    return self.generate(t)[:, :, 3] / 255.0

            gen = TextClipGenerator(full_lines, line_metrics, words)
            duration = seg["end"] - seg["start"]
            
            txt_clip = VideoClip(gen.get_rgb, duration=duration).set_mask(VideoClip(gen.get_mask, ismask=True, duration=duration))
            txt_clip = txt_clip.set_start(seg["start"]).set_position(("center", 0))
            
            clips.append(txt_clip)

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
        
        # استدعاء دالة تيليجرام
        upload_to_telegram(final_video_path, topic)
        
        os.startfile(final_video_path)
        
    except Exception as e:
        print(f"\nخطأ أثناء المونتاج: {e}")

if __name__ == "__main__":
    main()
