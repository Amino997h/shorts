# تم التحديث عبر MCP بنجاح
import os
import subprocess
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
        "channel_id": "-1004247712091",
        "voice": "en-US-GuyNeural - en-US (Male)"
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

def generate_voice(text, output_path):
    voice = CONFIG.get("voice", "en-US-GuyNeural - en-US (Male)")
    print(f"   🎙️ جاري توليد الصوت الواقعي الطبيعي ({voice})...")
    try:
        from gradio_client import Client
        import shutil
        client = Client("innoai/Edge-TTS-Text-to-Speech", verbose=False)
        result = client.predict(
            text,
            voice,
            0, # rate
            0, # pitch
            api_name="/tts_interface"
        )
        temp_audio = result[0]
        shutil.copy(temp_audio, output_path)
        print("   ✓ تم توليد الصوت العصبي فائق الجودة بنجاح!")
        return True
    except Exception as e:
        print(f"   ⚠️ تعذر الاتصال بمحرك الصوت العصبي ({e})، جاري التراجع إلى الصوت البديل...")
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            return True
        except Exception as e2:
            print(f"خطأ أثناء توليد الصوت: {e2}")
            return False

# --- 2. دوال الذكاء الاصطناعي (API المحلي) ---
def generate_script(topic):
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Write a high-retention viral voiceover script for a YouTube Short / TikTok about: "{topic}".
    
    CRITICAL STRUCTURE REQUIREMENTS:
    1. THE HOOK (First 2-3 seconds / exactly 5 to 9 words):
       - The very first sentence MUST be an irresistible, curiosity-inducing psychological HOOK that immediately stops the viewer from swiping away.
       - NEVER start with greetings ("Hello", "Hey everyone"), intro phrases ("Today we talk about"), or boring definitions.
       - Start immediately with a shocking fact, a provocative question, or an unbelievable mystery (e.g., "The biggest secret nobody tells you about...", "What if everything you believe about...", "You won't believe what happens when...").
    2. THE STORY & VALUE (Next 40-50 seconds):
       - Fast-paced, punchy, engaging narrative that quickly rewards the curiosity created by the hook.
    3. LANGUAGE & FORMAT:
       - The script MUST be written in ENGLISH (even if the topic is provided in Arabic).
       - Total length: exactly 85 to 105 words (rich, high-retention narrative, about 5 seconds longer than standard).
       - Output ONLY the spoken voiceover script text with no titles, quotes, brackets, or markdown formatting.
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
            
        try:
            return json.loads(text)
        except Exception:
            import json_repair
            repaired = json_repair.repair_json(text, return_objects=True)
            if isinstance(repaired, list) and len(repaired) > 0:
                return repaired
            raise
    except Exception as e:
        print(f"⚠️ تعذر استخراج توقيتات الصور من الذكاء الاصطناعي ({e})، جاري التوليد التلقائي لخطة الصور...")
        fallback_plan = []
        for s in segments:
            clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', s.get("text", "")).strip()
            words = [w for w in clean_text.split() if len(w) > 3]
            kw = " ".join(words[:4]) if words else "cinematic visual"
            fallback_plan.append({
                "keyword": kw,
                "start": s["start"],
                "end": s["end"]
            })
        return fallback_plan if fallback_plan else None

# --- 3. العملية الأساسية ---

# --- 4. النشر على تيليجرام ---
def upload_to_telegram(video_path, topic, script=""):
    print("\n[الخطوة 7]: جاري توليد عنوان ووصف فيروسي متوافق مع الخوارزميات (YouTube Shorts & Telegram)...")
    import requests
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    script_context = f"\nVideo Script:\n{script}\n" if script else ""
    
    prompt = f"""
    You are a viral YouTube Shorts and TikTok content strategist.
    Write an irresistible, high-CTR metadata package for this video topic: "{topic}".{script_context}
    
    CRITICAL REQUIREMENTS:
    - Everything MUST be written in ENGLISH language.
    - Structure EXACTLY in 4 lines:
      Line 1 (ATTRACTIVE TITLE): A viral, curiosity-driven title with 1-2 relevant emojis (e.g. "😱 Why Trees Are Rarer Than Diamonds in Space! 💎").
      Line 2 (HOOK DESCRIPTION): One fascinating, curiosity-inducing sentence revealing the core mind-blowing truth from the video.
      Line 3 (CALL TO ACTION): A short, engaging question prompting comments (e.g. "Did you know this? Let us know what you think below! 👇").
      Line 4 (VIRAL HASHTAGS): Exactly 6 high-traffic, algorithm-friendly hashtags matching the topic (e.g. #Shorts #DidYouKnow #Viral #Facts #ScienceFacts #MindBlowing).
      
    - Output ONLY the 4 lines. Do NOT write labels like "Line 1:", brackets, or conversational preamble.
    """
    
    def generate_smart_fallback(t):
        clean_t = t.strip().title()
        return (
            f"🤯 The Mind-Blowing Truth About {clean_t}! 🚀\n"
            f"Discover the unbelievable facts you never knew about {clean_t}!\n"
            f"Did you know this? Share your thoughts in the comments! 👇\n"
            f"#Shorts #DidYouKnow #Viral #Facts #Trending #MindBlowing"
        )
    
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "stream": False}
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        raw_caption = response.json()['choices'][0]['message']['content'].strip()
        
        # حماية صارمة: التأكد من أن الوصف لا يتجاوز حد تيليجرام ولا يحتوي على مخرجات الشاشة
        if len(raw_caption) > 800 or any(bad_word in raw_caption for bad_word in ["الخطوة", "Whisper", "جاري", "Building video", "MoviePy"]):
            print("⚠️ الوصف المستلم من السيرفر غير ملائم، استخدام القالب الفيروسي المعتمد.")
            caption = generate_smart_fallback(topic)
        else:
            caption = raw_caption
    except Exception as e:
        print(f"خطأ أثناء توليد الوصف: {e}")
        caption = generate_smart_fallback(topic)
        
    caption = caption[:1000] # ضمان عدم تجاوز حد تيليجرام الصارم (1024 حرف)
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

def compress_speech_pauses(audio_path, factor=0.30, min_silence_len=250, silence_thresh=-35):
    """تقليص الفراغات الصامتة بين الجمل إلى 30% من المدة الأصلية لتسريع وتيرة الكلام دون تسريع الكلمات نفسها."""
    try:
        from pydub import AudioSegment
        from pydub.silence import detect_silence
        audio = AudioSegment.from_file(audio_path)
        silences = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        if not silences:
            return
        new_audio = AudioSegment.empty()
        last_end = 0
        for s_start, s_end in silences:
            new_audio += audio[last_end:s_start]
            dur = s_end - s_start
            kept_len = max(90, int(dur * factor))
            new_audio += audio[s_start : s_start + kept_len]
            last_end = s_end
        new_audio += audio[last_end:]
        old_sec = round(len(audio)/1000, 1)
        new_sec = round(len(new_audio)/1000, 1)
        print(f"   ✂️ تم تقليص فترات الصمت بين الجمل إلى 30% من الأصل بنجاح ({old_sec}s ➔ {new_sec}s)!")
        new_audio.export(audio_path, format="mp3")
    except Exception as e:
        print(f"   ⚠️ تعذر تقليص الصمت بين الجمل ({e})، سيتم استخدام الصوت الأصلي.")

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
    if not generate_voice(script, audio_path):
        print("فشل توليد الصوت! سيتم التوقف.")
        return

    # تقليص الفراغ في الكلام بين الجمل لحوالي 30% من الأصلي
    compress_speech_pauses(audio_path, factor=0.30)
    
    print("\n[الخطوة 3]: استخراج التوقيت الدقيق للكلمات (Faster-Whisper)...")
    speech_end_time = None
    try:
        from faster_whisper import WhisperModel
        # نستخدم موديل صغير للسرعة
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments_iter, info = model.transcribe(audio_path, language="en", word_timestamps=True)
        
        words_list = []
        for s in segments_iter:
            for w in s.words:
                words_list.append(w)
        speech_end_time = round(words_list[-1].end + 0.08, 2) if words_list else None
                
        segments = []
        current_chunk = []
        for w in words_list:
            current_chunk.append(w)
            w_text = w.word.strip()
            # فصل الجمل تماماً عند علامات الترقيم لمنع دمج نهاية جملة مع بداية جملة أخرى
            ends_sentence = any(w_text.endswith(p) for p in ('.', '!', '?', ';', ':'))
            if len(current_chunk) >= 3 or ends_sentence:
                text = " ".join([item.word.strip() for item in current_chunk])
                segments.append({
                    "start": round(current_chunk[0].start, 2),
                    "end": round(current_chunk[-1].end, 2),
                    "text": text,
                    "words": [{"word": item.word.strip(), "start": item.start, "end": item.end} for item in current_chunk]
                })
                current_chunk = []
                
        if current_chunk:
            text = " ".join([item.word.strip() for item in current_chunk])
            segments.append({
                "start": round(current_chunk[0].start, 2),
                "end": round(current_chunk[-1].end, 2),
                "text": text,
                "words": [{"word": item.word.strip(), "start": item.start, "end": item.end} for item in current_chunk]
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
        from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ColorClip, VideoClip, CompositeAudioClip
        import moviepy.video.fx.all as vfx
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        audio_clip = AudioFileClip(audio_path)
        
        # 1. إعداد الخلفية الأساسية (خلفية داكنة راقية بدقة 1080x1920)
        bg_clip = ColorClip(size=(1080, 1920), color=(15, 15, 18)).set_duration(audio_clip.duration)
        clips = [bg_clip]

        # 2. إعداد مقطع الجيم بلاي في النصف السفلي (Y: 960 إلى 1920) مع اختيار مقطع عشوائي في كل مرة
        gameplay_path = r"C:\Users\User\OneDrive\Desktop\resilt\videoplayback.mp4"
        if os.path.exists(gameplay_path):
            try:
                import random
                # فحص مدة فيديو الجيم بلاي
                probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", gameplay_path]
                res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                total_gameplay_dur = float(res.stdout.strip())
                
                needed_dur = audio_clip.duration + 1.0
                max_start = max(0, total_gameplay_dur - needed_dur - 2.0)
                random_start = random.uniform(5.0, max_start) if max_start > 5.0 else 0.0
                print(f"   🎮 تم اختيار مقطع جيم بلاي عشوائي يبدأ من الثانية {random_start:.1f} إلى {random_start + needed_dur:.1f}...")

                slice_path = os.path.join(workspace, "gameplay_slice.mp4")
                cut_cmd = [
                    "ffmpeg", "-y", "-ss", f"{random_start:.2f}", "-t", f"{needed_dur:.2f}",
                    "-i", gameplay_path,
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                    "-an", slice_path
                ]
                subprocess.run(cut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                gameplay_clip = VideoFileClip(slice_path).without_audio()
                # جعل الارتفاع 960 وملء العرض 1080
                gameplay_clip = gameplay_clip.resize(height=960)
                if gameplay_clip.w < 1080:
                    gameplay_clip = gameplay_clip.resize(width=1080)
                x_center = gameplay_clip.w / 2
                gameplay_clip = gameplay_clip.crop(x1=x_center - 540, y1=0, x2=x_center + 540, y2=960)
                gameplay_clip = (
                    gameplay_clip.set_position((0, 960))
                    .set_duration(audio_clip.duration)
                )
                clips.append(gameplay_clip)
            except Exception as e_gp:
                print(f"   ⚠️ تعذر تجهيز مقطع الجيم بلاي ({e_gp})، سيتم المتابعة بدونه.")
        else:
            print("   ⚠️ ملف الجيم بلاي غير موجود، سيتم الاعتماد على الخلفية الأساسية.")

        # 3. خط فاصل احترافي ودقيق في المنتصف بين الصور والجيم بلاي (عند Y = 958)
        divider_clip = ColorClip(size=(1080, 4), color=(35, 35, 42)).set_duration(audio_clip.duration).set_position((0, 958))
        clips.append(divider_clip)

        # 4. إضافة الصور التوضيحية في النصف العلوي (Y: 0 إلى 960)
        # المنطقة المخصصة للصور: العرض حتى 1000 والارتفاع حتى 880 (مركز الـ Y عند 480)
        for info in downloaded_clips_info:
            img_path = info["path"]
            
            # التأكد من أن الصورة بنظام الألوان RGB وتجنب أعطال الأبيض والأسود (Grayscale)
            from PIL import Image
            with Image.open(img_path) as pil_img:
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                    pil_img.save(img_path)
                    
            img = ImageClip(img_path)
            w_ratio = 1000 / img.w
            h_ratio = 880 / img.h
            scale = min(w_ratio, h_ratio)
            
            clip = img.resize(scale)
            # توسيطها في النصف العلوي تماماً
            center_y = 480
            clip = (clip.set_position(("center", center_y - clip.h / 2))
                        .set_start(info["start"])
                        .set_duration(info["duration"]))
            clips.append(clip)
            
        # 3. إضافة الترجمة الاحترافية (The Bold Font + Italic + Wide + Word-by-Word Highlight)
        font_path = os.path.join(os.path.dirname(__file__), "theboldfont.ttf")
        if not os.path.exists(font_path):
            font_path = "theboldfont.ttf"
            
        try:
            font = ImageFont.truetype(font_path, 68)
        except:
            try:
                font = ImageFont.truetype("arialbd.ttf", 64)
            except:
                font = ImageFont.load_default()

        for i, seg in enumerate(segments):
            words = seg.get("words", [])
            if not words: continue
            
            clean_words = [w["word"].strip() for w in words]
            space_w = font.getlength(" ")
            word_lens = [font.getlength(w) for w in clean_words]
            total_text_w = sum(word_lens) + space_w * (len(clean_words) - 1)
            
            pad_x, pad_y = 50, 35
            box_w = int(total_text_w + pad_x * 2)
            box_h = 160
            
            # حساب المواقع الأفقية الثابتة لكل كلمة
            word_positions = []
            cur_x = pad_x
            for w_len in word_lens:
                word_positions.append(cur_x)
                cur_x += w_len + space_w

            class KaraokeClipGenerator:
                def __init__(self, words, clean_words, word_positions, box_w, box_h, pad_y):
                    self.words = words
                    self.clean_words = clean_words
                    self.word_positions = word_positions
                    self.box_w = box_w
                    self.box_h = box_h
                    self.pad_y = pad_y
                    self.cached_frames = {}
                    
                def render_frame(self, active_idx):
                    if active_idx in self.cached_frames:
                        return self.cached_frames[active_idx]
                        
                    box = Image.new('RGBA', (self.box_w, self.box_h), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(box)
                    y = self.pad_y
                    
                    for idx, w_text in enumerate(self.clean_words):
                        x = self.word_positions[idx]
                        # 1. شادو ظل أسود عميق وكبير في الخلفية لعزل النص تماماً
                        draw.text((x + 7, y + 9), w_text, font=font, fill=(0, 0, 0, 230), stroke_width=8, stroke_fill=(0, 0, 0, 230))
                        
                        # 2. النص الأساسي: أصفر للكلمة المنطوقة حالياً، وأبيض ناصع في باقي الكلمات
                        is_active = (idx == active_idx)
                        color = "#FFFF00" if is_active else "#FFFFFF"
                        draw.text((x, y), w_text, font=font, fill=color, stroke_width=7, stroke_fill="black")
                        
                    # 3. جعل الكلام أعرض (Wider stretch)
                    wider_w = int(self.box_w * 1.18)
                    wider = box.resize((wider_w, self.box_h), Image.Resampling.LANCZOS)
                    
                    # 4. إمالة السطر (Italic slant عبر Affine Transformation)
                    shear_extra = 45
                    sheared = wider.transform(
                        (wider_w + shear_extra, self.box_h),
                        Image.AFFINE,
                        (1, -0.18, 0, 0, 1, 0),
                        resample=Image.Resampling.BICUBIC
                    )
                    
                    # 5. الحماية الصارمة من تجاوز حدود الشاشة وترك هوامش أمان (Safe Margin Auto-Scaler)
                    MAX_SAFE_WIDTH = 860  # يضمن ترك هامش أمان لا يقل عن 110 بكسل من كل جانب
                    if sheared.width > MAX_SAFE_WIDTH:
                        scale_factor = MAX_SAFE_WIDTH / sheared.width
                        final_w = int(sheared.width * scale_factor)
                        final_h = int(self.box_h * scale_factor)
                        sheared = sheared.resize((final_w, final_h), Image.Resampling.LANCZOS)
                    else:
                        final_w = sheared.width
                        final_h = self.box_h
                    
                    # 6. التوسيط في شريط الترجمة في منتصف الشاشة (1080x260)
                    canvas = Image.new('RGBA', (1080, 260), (0, 0, 0, 0))
                    pos_x = (1080 - final_w) // 2
                    pos_y = (260 - final_h) // 2
                    canvas.paste(sheared, (pos_x, pos_y), sheared)
                    
                    import numpy as np
                    frame_array = np.array(canvas)
                    self.cached_frames[active_idx] = frame_array
                    return frame_array

                def generate(self, t):
                    current_global_t = t + self.words[0]['start']
                    active_idx = -1
                    
                    for idx, w in enumerate(self.words):
                        if w['start'] <= current_global_t <= w['end']:
                            active_idx = idx
                            break
                            
                    if active_idx == -1:
                        # إذا كان بين كلمتين، نميز الكلمة التي تم نطقها للتو
                        for idx, w in enumerate(self.words):
                            if current_global_t >= w['start']:
                                active_idx = idx
                                
                    if active_idx == -1 and len(self.words) > 0:
                        active_idx = 0
                        
                    return self.render_frame(active_idx)

                def get_rgb(self, t):
                    return self.generate(t)[:, :, :3]
                    
                def get_mask(self, t):
                    return self.generate(t)[:, :, 3] / 255.0

            gen = KaraokeClipGenerator(words, clean_words, word_positions, box_w, box_h, pad_y)
            duration = seg["end"] - seg["start"]
            if duration <= 0: duration = 0.1
            
            txt_clip = VideoClip(gen.get_rgb, duration=duration).set_mask(VideoClip(gen.get_mask, ismask=True, duration=duration))
            # وضع الترجمة في المنتصف تماماً فوق الخط الفاصل بين النصفين (مركز Y = 960)
            txt_clip = txt_clip.set_start(seg["start"]).set_position(("center", 960 - 130))
            
            clips.append(txt_clip)

        video = CompositeVideoClip(clips, size=(1080, 1920))
        
        # 4. دمج صوت الخلفية الموسيقية (يبدأ دائماً من أول الفيديو، ولا يمتد فوق الخاتمة)
        bg_music_path = r"C:\Users\User\OneDrive\Desktop\resilt\_gYjh863j4g.mp4"
        if os.path.exists(bg_music_path):
            print("\n   🎵 دمج صوت الخلفية الموسيقية بمستوى متوازن (12%) يبدأ من أول الكليب...")
            try:
                bg_music = (
                    AudioFileClip(bg_music_path)
                    .subclip(0, audio_clip.duration)
                    .volumex(0.12)
                    .audio_fadeout(0.4)
                )
                final_audio = CompositeAudioClip([audio_clip, bg_music])
                video = video.set_audio(final_audio)
            except Exception as e_bg:
                print(f"   ⚠️ تعذر دمج صوت الخلفية ({e_bg})، استخدام الصوت الرئيسي فقط.")
                video = video.set_audio(audio_clip)
        else:
            video = video.set_audio(audio_clip)
        
        # حفظ النتائج في مسار C:\Users\User\OneDrive\Desktop\resilt\ai
        output_dir = r"C:\Users\User\OneDrive\Desktop\resilt\ai"
        os.makedirs(output_dir, exist_ok=True)
        clean_topic = re.sub(r'[\\/*?:"<>|]', "", topic).strip() or "video"
        final_video_path = os.path.join(output_dir, f"{clean_topic}.mp4")
        counter = 1
        while os.path.exists(final_video_path):
            final_video_path = os.path.join(output_dir, f"{clean_topic}_{counter}.mp4")
            counter += 1
        print("\n⏳ جاري تصدير الفيديو (الرجاء الانتظار، قد يستغرق بعض الوقت بناءً على قوة جهازك)...")
        video.write_videofile(final_video_path, fps=24, codec="libx264", audio_codec="aac")
        try:
            video.close()
            audio_clip.close()
        except:
            pass

        # --- دمج الخاتمة التلقائي وقص الصمت النهائي بعد اكتمال البرنامج الأصلي بالكامل ---
        outro_path = r"C:\Users\User\OneDrive\Desktop\resilt\6993530118_tk_2x.mp4"
        if os.path.exists(outro_path):
            print("\n🎬 [الخاتمة]: جاري إزالة صمت النهاية ودمج فيديو الاشتراك في نهاية المقطع...")
            temp_with_outro = os.path.join(workspace, "temp_final_outro.mp4")
            
            # معرفة لحظة انتهاء الكلام بدقة لقطع الصمت الميت
            cut_time = speech_end_time if (speech_end_time and speech_end_time < audio_clip.duration) else None
            
            if cut_time:
                silence_gap = round(audio_clip.duration - cut_time, 2)
                print(f"   ✂️ تم رصد {silence_gap} ثانية صمت ميت بعد انتهاء الكلام — قطع فوري وانتقال للخاتمة!")
                filter_complex = (
                    f"[0:v]trim=0:{cut_time:.2f},setpts=PTS-STARTPTS,fps=24[v0];"
                    f"[0:a]atrim=0:{cut_time:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a0];"
                    f"[1:v]scale=1080:1920,setsar=1,fps=24[v1];"
                    f"[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];"
                    f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
                )
            else:
                filter_complex = (
                    "[0:v]scale=1080:1920,setsar=1,fps=24[v0];"
                    "[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];"
                    "[1:v]scale=1080:1920,setsar=1,fps=24[v1];"
                    "[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];"
                    "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
                )

            try:
                cmd = [
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-i", final_video_path,
                    "-i", outro_path,
                    "-filter_complex", filter_complex,
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    temp_with_outro
                ]
                subprocess.run(cmd, check=True)
                os.replace(temp_with_outro, final_video_path)
                print("✓ تم دمج خاتمة الاشتراك بنجاح وانتقال فوري بدون أي صمت!")
            except Exception as e_outro:
                print(f"⚠️ تعذر دمج الخاتمة ({e_outro})، سيتم استخدام الفيديو الأصلي.")
        
        total_time = round(time.time() - global_start_time, 2)
        print("\n" + "="*50)
        print(f"🎉 تم إنتاج الفيديو بتزامن دقيق للصور!")
        print(f"⏱️ مدة العملية كلها: {total_time} ثانية.")
        print(f"📁 المسار: {final_video_path}")
        print("="*50)
        
        # استدعاء دالة تيليجرام
        upload_to_telegram(final_video_path, topic, script)
        
        os.startfile(final_video_path)
        
    except Exception as e:
        print(f"\nخطأ أثناء المونتاج: {e}")

if __name__ == "__main__":
    main()

# MCP Sync Check
