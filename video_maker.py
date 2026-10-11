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
    
    # حساب الحد الأدنى المتوقع لزمن الصوت لمنع أي ملفات مقطوعة أو فارغة
    words_count = len(text.split())
    expected_min_sec = max(12.0, words_count * 0.22)
    
    # 1. محاولة استخدام الصوت العصبي الفائق (Edge-TTS عبر Gradio) مع إعادة المحاولة والتحقق من الاكتمال
    for attempt in range(1, 3):
        try:
            from gradio_client import Client
            import shutil
            from pydub import AudioSegment
            client = Client("innoai/Edge-TTS-Text-to-Speech", verbose=False)
            result = client.predict(
                text,
                voice,
                0, # rate
                0, # pitch
                api_name="/tts_interface"
            )
            temp_audio = result[0]
            if os.path.exists(temp_audio) and os.path.getsize(temp_audio) > 10000:
                audio_check = AudioSegment.from_file(temp_audio)
                if audio_check.duration_seconds >= expected_min_sec:
                    shutil.copy(temp_audio, output_path)
                    print(f"   ✓ تم توليد الصوت العصبي فائق الجودة بنجاح ({round(audio_check.duration_seconds, 1)}s)!")
                    return True
                else:
                    print(f"   ⚠️ تنبيه: الملف الصوتي المستلم مبتور ({round(audio_check.duration_seconds, 1)}s من أصل {words_count} كلمة)، محاولة ثانية...")
        except Exception as e:
            print(f"   ⚠️ محاولة {attempt} للصوت العصبي تعثرت ({e})...")
        time.sleep(1)

    # 2. التراجع الذكي إلى الصوت البديل المؤكد (gTTS) لضمان عدم توقف أو بتر الفيديو إطلاقاً
    print("   🔄 جاري التحويل الفوري إلى محرك الصوت الاحتياطي المضمون (gTTS)...")
    try:
        from gtts import gTTS
        from pydub import AudioSegment
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        chk = AudioSegment.from_file(output_path)
        print(f"   ✓ تم توليد الصوت البديل بنجاح كامل ({round(chk.duration_seconds, 1)}s)!")
        return True
    except Exception as e2:
        print(f"خطأ أثناء توليد الصوت الاحتياطي: {e2}")
        return False

# --- 2. دوال الذكاء الاصطناعي (API المحلي) ---
def generate_script(topic):
    api_url = CONFIG.get("api_url")
    api_key = CONFIG.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    You are an elite YouTube Shorts and TikTok viral scriptwriter with over 100 million views.
    Write an ultra-high-retention viral voiceover script for a short-form video about: "{topic}".
    
    🔥 CRITICAL HOOK MASTERY (First 3 seconds / First sentence):
    - The very first sentence MUST be an irresistible, pattern-interrupting PSYCHOLOGICAL HOOK that physically forces the viewer to stop swiping away.
    - Use proven high-CTR viral hook styles:
      * THE CONTRARIAN TRUTH / MYTH BUSTER: (e.g. "Almost everything you were told about [topic] is a complete lie.", "99% of people think this, but the reality is shocking.")
      * THE URGENT WARNING / FOMO: (e.g. "If you are still doing this in 2026, stop immediately.", "You are losing money every day without knowing this.")
      * THE BIZARRE / IMPOSSIBLE FACT: (e.g. "What if I told you the craziest secret about [topic]?", "This one bizarre fact sounds 100% made up, but it's real.")
      * THE UNCOMFORTABLE QUESTION: (e.g. "Why does nobody talk about what actually happens when...?")
    - ABSOLUTELY FORBIDDEN: NEVER start with greetings ("Hey guys", "Hello everyone"), boring introductions ("Today we will discuss", "Have you ever wondered"), or dry textbook definitions. Dive straight into the shocking hook.

    ⚡ STORY PACING & VALUE (Next 35-45 seconds):
    - Fast-paced, punchy, high-energy sentences that immediately reward the viewer's curiosity.
    - Reveal actionable insights, mind-blowing twists, or practical secrets step-by-step.
    - Keep the tension and curiosity high until the final word.

    📏 STRICT FORMAT & LENGTH:
    - Language: MUST be 100% in ENGLISH (even if the user topic is provided in Arabic).
    - Length: EXACTLY 85 to 105 words (the viral sweet spot for 35 to 45 seconds).
    - Output ONLY the spoken voiceover script text. Do NOT include titles, scene headings, emojis, quotes, or markdown formatting.
    """
    
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "stream": False}
    print("\n[الخطوة 1]: جاري التفكير وكتابة السكريبت الفيروسي الخارق...")
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
    
    bot_token = CONFIG.get("bot_token")
    channel_id = CONFIG.get("channel_id")
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    # فحص حجم الفيديو بدقة لضمان عدم تجاوز حد تيليجرام الصارم (50 ميغابايت)
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    upload_file = video_path
    temp_compressed = None
    
    if file_size_mb >= 48.0:
        print(f"\n   ⚙️ حجم الفيديو ({round(file_size_mb, 1)}MB) يتجاوز حد تيليجرام المسموح للبوتات (50MB).")
        print("   🚀 جاري تكييف الحجم تلقائياً بأعلى جودة لضمان الرفع السلس والمضمون...")
        temp_compressed = os.path.join(os.path.dirname(video_path), "tele_upload_temp.mp4")
        comp_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", video_path,
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-c:a", "copy",
            temp_compressed
        ]
        try:
            import subprocess
            subprocess.run(comp_cmd, check=True)
            upload_file = temp_compressed
            new_mb = os.path.getsize(upload_file) / (1024 * 1024)
            print(f"   ✓ تم تجهيز نسخة النشر لتيليجرام بنجاح ({round(new_mb, 1)}MB)!")
        except Exception as e_comp:
            print(f"   ⚠️ تعذر التكييف التلقائي ({e_comp})، جاري محاولة رفع الملف الأصلي...")
            upload_file = video_path

    # محاولات رفع مؤكدة مع إعادة المحاولة التلقائية في حال حدوث أي تقلب بالشبكة
    for attempt in range(1, 4):
        try:
            print(f"جاري الرفع إلى قناة التيليجرام (المحاولة {attempt}/3)...")
            with open(upload_file, 'rb') as video_file:
                data = {'chat_id': channel_id, 'caption': caption}
                files = {'video': video_file}
                resp = requests.post(url, data=data, files=files, timeout=600)
                resp.raise_for_status()
                res_data = resp.json()
                if res_data.get("ok"):
                    print("✓ تم النشر على قناة تيليجرام بنجاح!")
                    break
        except Exception as e:
            print(f"   ⚠️ المحاولة {attempt} للنشر تعثرت ({e})...")
            if attempt < 3:
                time.sleep(3)
            else:
                print("❌ تعذر النشر على تيليجرام بعد 3 محاولات.")
                
    if temp_compressed and os.path.exists(temp_compressed):
        try:
            os.remove(temp_compressed)
        except:
            pass

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
        # حماية أمان صارمة: إذا كان التقليص يحذف أكثر من نصف الملف فهذا يعني خطأ في كشف الصمت
        if new_sec < old_sec * 0.50:
            print(f"   ⚠️ تنبيه أمان: نسبة تقليص الصمت مبالغ فيها ({old_sec}s ➔ {new_sec}s)، الإبقاء على الصوت الأصلي.")
            return
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
        
        # حماية صارمة: التحقق من اكتمال استخراج الكلمات
        if len(words_list) < 15 and len(script.split()) > 30:
            print("   ⚠️ تنبيه: عدد الكلمات المستخرجة قليل جداً، سيتم استخدام طول الصوت كاملاً بدون قص.")
            speech_end_time = None
        else:
            speech_end_time = round(words_list[-1].end + 0.08, 2) if words_list else None
                
        # قياس عرض الكلمات بدقة لمنع تصغير حجم الخط والحفاظ عليه ضخماً وموحداً دائماً
        font_file = os.path.join(os.path.dirname(__file__), "theboldfont.ttf")
        if not os.path.exists(font_file):
            font_file = "theboldfont.ttf"
        try:
            from PIL import ImageFont
            measure_font = ImageFont.truetype(font_file, 68)
        except:
            from PIL import ImageFont
            measure_font = ImageFont.load_default()
        space_w = measure_font.getlength(" ")

        def calc_chunk_width(chunk):
            if not chunk: return 0
            words = [it.word.strip() for it in chunk]
            w_sum = sum(measure_font.getlength(w) for w in words)
            spaces = space_w * (len(words) - 1)
            return int((w_sum + spaces + 100) * 1.18) + 45

        segments = []
        current_chunk = []
        for w in words_list:
            w_text = w.word.strip()
            # فحص ما إذا كانت إضافة الكلمة ستجعل السطر يتجاوز العرض المسموح (840px)
            tentative_chunk = current_chunk + [w]
            expected_width = calc_chunk_width(tentative_chunk)
            
            # إذا تجاوز العرض الأقصى أو وصل لـ 3 كلمات، نضحي بالكلمة وننهي المجموعة السابقة فوراً
            if current_chunk and (expected_width > 840 or len(current_chunk) >= 3):
                text = " ".join([item.word.strip() for item in current_chunk])
                segments.append({
                    "start": round(current_chunk[0].start, 2),
                    "end": round(current_chunk[-1].end, 2),
                    "text": text,
                    "words": [{"word": item.word.strip(), "start": item.start, "end": item.end} for item in current_chunk]
                })
                current_chunk = [w]
            else:
                current_chunk.append(w)
                
            # فصل الجمل تماماً عند علامات الترقيم لمنع دمج نهاية جملة مع بداية جملة أخرى
            ends_sentence = any(w_text.endswith(p) for p in ('.', '!', '?', ';', ':'))
            if ends_sentence and current_chunk:
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

        # 2. إعداد مقطع الجيم بلاي في النصف السفلي (Y: 960 إلى 1920) بدقة عالية مع اختيار مقطع عشوائي في كل مرة
        gameplay_candidates = [
            r"C:\Users\User\OneDrive\Desktop\resilt\document_5936256664112996112.mp4",
            r"C:\Users\User\OneDrive\Desktop\resilt\videoplayback.mp4"
        ]
        gameplay_path = next((p for p in gameplay_candidates if os.path.exists(p)), None)
        if gameplay_path:
            try:
                import random
                # فحص مدة فيديو الجيم بلاي
                probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", gameplay_path]
                res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                total_gameplay_dur = float(res.stdout.strip())
                
                needed_dur = audio_clip.duration + 1.0
                max_start = max(0, total_gameplay_dur - needed_dur - 2.0)
                random_start = random.uniform(5.0, max_start) if max_start > 5.0 else 0.0
                print(f"   🎮 تم اختيار مقطع جيم بلاي عالي الدقة عشوائي يبدأ من الثانية {random_start:.1f} إلى {random_start + needed_dur:.1f}...")

                slice_path = os.path.join(workspace, "gameplay_slice.mp4")
                # معالجة فورية فائقة الوضوح عبر FFmpeg: ضبط أبعاد 1080x960 مع المحافظة على النسبة الأصلية 16:9 + setsar=1 + fps=24
                cut_cmd = [
                    "ffmpeg", "-y", "-ss", f"{random_start:.2f}", "-t", f"{needed_dur:.2f}",
                    "-i", gameplay_path,
                    "-vf", "scale=1706:960:flags=lanczos,crop=1080:960,setsar=1,fps=24",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-an", slice_path
                ]
                subprocess.run(cut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                gameplay_clip = (
                    VideoFileClip(slice_path)
                    .without_audio()
                    .set_position((0, 960))
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
        video.write_videofile(final_video_path, fps=24, codec="libx264", audio_codec="aac", bitrate="4500k", preset="fast")
        try:
            video.close()
            audio_clip.close()
        except:
            pass

        # --- دمج الهوك البصري الافتتاحي والخاتمة التلقائية وقص الصمت النهائي ---
        hook_dir = r"C:\Users\User\OneDrive\Desktop\resilt\hook"
        hook_audio_source = r"C:\Users\User\OneDrive\Desktop\resilt\Am4wYTiHHx8.mp4"
        outro_path = r"C:\Users\User\OneDrive\Desktop\resilt\6993530118_tk_2x.mp4"
        
        temp_hook_path = None
        if os.path.exists(hook_dir):
            hook_files = [os.path.join(hook_dir, f) for f in os.listdir(hook_dir) if f.lower().endswith(('.mp4', '.mov', '.mkv'))]
            if hook_files:
                selected_hook = random.choice(hook_files)
                hook_name = os.path.basename(selected_hook)
                print(f"\n🎯 [الهوك البصري]: تم اختيار هوك عشوائي ({hook_name}) للبداية...")
                try:
                    # فحص مدة الهوك بدقة كاملة دون أي قص
                    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", selected_hook]
                    res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    hook_dur = float(res.stdout.strip())
                    
                    # فحص مدة الصوت الخارجي لضبط التزامن حتى تنتهي نهاية الصوت مع نهاية الهوك تماماً
                    sound_dur = 0.0
                    if os.path.exists(hook_audio_source):
                        probe_snd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", hook_audio_source]
                        res_snd = subprocess.run(probe_snd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        sound_dur = float(res_snd.stdout.strip())
                    
                    temp_hook_file = os.path.join(workspace, "temp_prepared_hook.mp4")
                    
                    # حساب نقطة بداية الصوت بحيث تنتهي تماماً مع نهاية الهوك، يليه 0.1 ثانية شاشة سوداء صامتة
                    if sound_dur > 0 and sound_dur >= hook_dur:
                        sound_start = round(sound_dur - hook_dur, 3)
                        hook_prep_cmd = [
                            "ffmpeg", "-y", "-loglevel", "error",
                            "-i", selected_hook,
                            "-ss", f"{sound_start:.3f}", "-i", hook_audio_source,
                            "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=24:d=0.1",
                            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:d=0.1",
                            "-filter_complex",
                            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24[v0];"
                            f"[1:a]atrim=0:{hook_dur:.3f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a0];"
                            f"[2:v]setsar=1,fps=24[v_b];"
                            f"[3:a]aresample=44100,aformat=channel_layouts=stereo[a_b];"
                            f"[v0][a0][v_b][a_b]concat=n=2:v=1:a=1[v][a]",
                            "-map", "[v]", "-map", "[a]",
                            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                            "-c:a", "aac", "-b:a", "192k",
                            temp_hook_file
                        ]
                    else:
                        hook_prep_cmd = [
                            "ffmpeg", "-y", "-loglevel", "error",
                            "-i", selected_hook,
                            "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=24:d=0.1",
                            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:d=0.1",
                            "-filter_complex",
                            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24[v0];"
                            f"[2:a]atrim=0:{hook_dur:.3f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a0];"
                            f"[1:v]setsar=1,fps=24[v_b];"
                            f"[2:a]aresample=44100,aformat=channel_layouts=stereo[a_b];"
                            f"[v0][a0][v_b][a_b]concat=n=2:v=1:a=1[v][a]",
                            "-map", "[v]", "-map", "[a]",
                            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                            "-c:a", "aac", "-b:a", "192k",
                            temp_hook_file
                        ]
                        
                    subprocess.run(hook_prep_cmd, check=True)
                    temp_hook_path = temp_hook_file
                    print("   ✓ تم تجهيز الهوك بالكامل مع مزامنة نهاية الصوت والشاشة السوداء (0.1s) بنجاح!")
                except Exception as e_hk:
                    print(f"   ⚠️ تعذر تجهيز الهوك البصري ({e_hk})، سيتم تجاوزه.")

        # تجميع الأجزاء (الهوك + الفيديو الأساسي + الخاتمة)
        has_outro = os.path.exists(outro_path)
        # أمان قاطع: قص الصمت النهائي فقط إذا تجاوز الكلام 15 ثانية وكان الفراغ طبيعياً لا يتجاوز 6 ثوانٍ
        cut_time = speech_end_time if (speech_end_time and speech_end_time > 15.0 and speech_end_time < audio_clip.duration and (audio_clip.duration - speech_end_time) <= 6.0) else None
        
        if temp_hook_path or has_outro:
            print("\n🎬 [المونتاج النهائي]: جاري دمج الأجزاء وقص الصمت الميت...")
            temp_stitched = os.path.join(workspace, "temp_final_stitched.mp4")
            inputs = []
            filter_parts = []
            v_maps = []
            a_maps = []
            input_idx = 0
            
            # 1. إضافة الهوك إن وجد
            if temp_hook_path:
                inputs.extend(["-i", temp_hook_path])
                filter_parts.append(f"[{input_idx}:v]scale=1080:1920,setsar=1,fps=24[v_hk]; [{input_idx}:a]aresample=44100,aformat=channel_layouts=stereo[a_hk];")
                v_maps.append("[v_hk]")
                a_maps.append("[a_hk]")
                input_idx += 1
                
            # 2. إضافة الفيديو الأساسي (مع قص الصمت الميت إن وجد)
            inputs.extend(["-i", final_video_path])
            if cut_time:
                silence_gap = round(audio_clip.duration - cut_time, 2)
                print(f"   ✂️ تم رصد {silence_gap} ثانية صمت ميت بعد انتهاء الكلام — قطع فوري!")
                filter_parts.append(f"[{input_idx}:v]trim=0:{cut_time:.2f},setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=24[v_main]; [{input_idx}:a]atrim=0:{cut_time:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a_main];")
            else:
                filter_parts.append(f"[{input_idx}:v]scale=1080:1920,setsar=1,fps=24[v_main]; [{input_idx}:a]aresample=44100,aformat=channel_layouts=stereo[a_main];")
            v_maps.append("[v_main]")
            a_maps.append("[a_main]")
            input_idx += 1
            
            # 3. إضافة الخاتمة إن وجدت
            if has_outro:
                inputs.extend(["-i", outro_path])
                filter_parts.append(f"[{input_idx}:v]scale=1080:1920,setsar=1,fps=24[v_out]; [{input_idx}:a]aresample=44100,aformat=channel_layouts=stereo[a_out];")
                v_maps.append("[v_out]")
                a_maps.append("[a_out]")
                input_idx += 1
                
            total_segments = len(v_maps)
            concat_inputs = "".join(f"{v_maps[i]}{a_maps[i]}" for i in range(total_segments))
            filter_parts.append(f"{concat_inputs}concat=n={total_segments}:v=1:a=1[v][a]")
            
            full_filter_complex = " ".join(filter_parts)
            stitch_cmd = [
                "ffmpeg", "-y", "-loglevel", "error"
            ] + inputs + [
                "-filter_complex", full_filter_complex,
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k",
                temp_stitched
            ]
            try:
                subprocess.run(stitch_cmd, check=True)
                os.replace(temp_stitched, final_video_path)
                print("✓ تم تجميع الهوك الافتتاحي والفيديو وخاتمة الاشتراك بنجاح تام!")
            except Exception as e_stitch:
                print(f"⚠️ تعذر التجميع النهائي ({e_stitch})، سيتم استخدام الفيديو الأصلي.")
        
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
