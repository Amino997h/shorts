import gradio as gr
import subprocess
import os
import sys
import json
import time
import shutil
import html
from collections import deque
from datetime import datetime

CONFIG_FILE = 'config.json'
STATE_FILE = 'state.json'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_ASSETS_DIR = r"C:\Users\User\OneDrive\Desktop\resilt"
DEFAULT_HOOKS_DIR = os.path.join(DEFAULT_ASSETS_DIR, "hook")

def load_config():
    default_config = {
        "api_url": "http://127.0.0.1:8008/v1/chat/completions",
        "api_key": "YOUR_API_KEY_HERE",
        "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "channel_id": "YOUR_TELEGRAM_CHANNEL_ID",
        "upload_to_telegram": True,
        "voice": "en-US-GuyNeural - en-US (Male)",
        "gameplay_path": r"C:\Users\User\OneDrive\Desktop\resilt\document_5936256664112996112.mp4",
        "hook_dir": r"C:\Users\User\OneDrive\Desktop\resilt\hook",
        "hook_audio_source": r"C:\Users\User\OneDrive\Desktop\resilt\Am4wYTiHHx8.mp4",
        "bg_music_path": r"C:\Users\User\OneDrive\Desktop\resilt\_gYjh863j4g.mp4",
        "outro_path": r"C:\Users\User\OneDrive\Desktop\resilt\6993530118_tk_2x.mp4"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

def save_config(api_url, api_key, bot_token, channel_id, upload_to_telegram, voice, gameplay_path, hook_dir, hook_audio_source, bg_music_path, outro_path):
    config = {
        "api_url": api_url.strip(),
        "api_key": api_key.strip(),
        "bot_token": bot_token.strip(),
        "channel_id": channel_id.strip(),
        "upload_to_telegram": bool(upload_to_telegram),
        "voice": voice.strip(),
        "gameplay_path": gameplay_path.strip(),
        "hook_dir": hook_dir.strip(),
        "hook_audio_source": hook_audio_source.strip(),
        "bg_music_path": bg_music_path.strip(),
        "outro_path": outro_path.strip()
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return "✅ تم حفظ وتطبيق الإعدادات بنجاح!"
    except Exception as e:
        return f"❌ خطأ أثناء حفظ الإعدادات: {e}"

def validate_config():
    config = load_config()
    errors = []
    
    if not config.get("api_url") or "127.0.0.1" not in config.get("api_url") and not config.get("api_url").startswith("http"):
        errors.append("رابط الـ API غير صالح.")
    if config.get("upload_to_telegram", True):
        if not config.get("bot_token") or ":" not in config.get("bot_token") or "YOUR_TELEGRAM" in config.get("bot_token"):
            errors.append("توكن بوت تيليجرام غير صالح.")
        if not config.get("channel_id") or "YOUR_TELEGRAM" in config.get("channel_id"):
            errors.append("معرف القناة غير صالح.")
            
    gp = config.get("gameplay_path", "")
    if gp and not os.path.exists(gp):
        errors.append(f"ملف الجيم بلاي غير موجود: {gp}")
        
    hk = config.get("hook_dir", "")
    if hk and not os.path.exists(hk):
        errors.append(f"مجلد الهوكات غير موجود: {hk}")
        
    bg = config.get("bg_music_path", "")
    if bg and not os.path.exists(bg):
        errors.append(f"ملف موسيقى الخلفية غير موجود: {bg}")
        
    out = config.get("outro_path", "")
    if out and not os.path.exists(out):
        errors.append(f"ملف الخاتمة غير موجود: {out}")
        
    return errors

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"queue": [], "current_index": 0, "in_progress": False}

def save_state(state):
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

def check_resume_status():
    state = load_state()
    if state.get("in_progress") and state.get("queue"):
        total = len(state["queue"])
        curr = state.get("current_index", 0) + 1
        if curr <= total:
            return gr.update(visible=True, value=f"⚠️ **تنبيه:** توجد قائمة سابقة غير مكتملة متوقفة عند الفيديو ({curr}/{total}). هل تريد الاستكمال؟")
    return gr.update(visible=False, value="")

# ==============================================================
# --- المكونات البصرية الحية (Live Cyber Dashboard Generator) ---
# ==============================================================

def render_dashboard_html(mode="single", percentage=0, step_title="في الانتظار...", topic="--", logs=None, batch_info=None, status_type="active"):
    """
    توليد واجهة المتابعة الحية بنظام Technical Synthesizer Deck:
    تصميم فاتح أنيق مع شاشتي هاكر داكنتين CRT (الدوامة والكونسول).
    """
    if logs is None:
        logs = []
    
    # تنسيق وتلوين أسطر الهاكر
    formatted_logs = []
    for line in logs:
        line_clean = line.strip()
        if not line_clean:
            continue
        ts = datetime.now().strftime("%H:%M:%S")
        safe_line = html.escape(line_clean)
        
        if "[الخطوة" in line_clean or "STEP" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-emerald-300 font-bold">[STEP]</span> <span class="text-emerald-400">{safe_line}</span></p>')
        elif "✓" in line_clean or "تم" in line_clean or "اكتمل" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-emerald-400 font-bold">[OK]</span> <span class="text-emerald-300">{safe_line}</span></p>')
        elif "⚠️" in line_clean or "تنبيه" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-yellow-400 font-bold">[WARN]</span> <span class="text-yellow-300">{safe_line}</span></p>')
        elif "❌" in line_clean or "خطأ" in line_clean or "ERR" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-rose-400 font-bold">[ERROR]</span> <span class="text-rose-300">{safe_line}</span></p>')
        elif "جاري البحث عن:" in line_clean or "BING" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-cyan-400 font-bold">[SCRAPE]</span> <span class="text-cyan-300">{safe_line}</span></p>')
        elif "🎮" in line_clean or "🎵" in line_clean or "🎯" in line_clean or "🎬" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-purple-400 font-bold">[MEDIA]</span> <span class="text-purple-300">{safe_line}</span></p>')
        else:
            formatted_logs.append(f'<p><span class="text-emerald-700">[{ts}]</span> <span class="text-slate-400 font-mono">> {safe_line}</span></p>')

    if not formatted_logs:
        formatted_logs.append('<p><span class="text-emerald-700">[SYSTEM]</span> <span class="text-slate-500">> Awaiting process initiation...</span></p>')

    # ترتيب عكسي ليعمل التمرير التلقائي بالـ CSS flex-direction: column-reverse
    reversed_log_html = "".join(reversed(formatted_logs))

    # ألوان وحالة الدوامة المربعة
    if status_type == "error":
        badge_text = "ERROR"
        badge_class = "text-rose-400"
        pct_display = "ERR"
    elif percentage >= 100:
        badge_text = "DONE"
        badge_class = "text-emerald-400"
        pct_display = "100%"
    else:
        badge_text = "WORKING"
        badge_class = "text-emerald-500 animate-pulse"
        pct_display = f"{int(percentage)}%"

    safe_topic = html.escape(topic)
    safe_step = html.escape(step_title)

    # قالب وضع الجملة الإضافي بالأعلى (Batch Progress Header)
    batch_header_html = ""
    if mode == "batch" and batch_info:
        b_pct = batch_info.get("pct", 0)
        b_comp = batch_info.get("completed", 0)
        b_curr = batch_info.get("current", 0)
        b_rem = batch_info.get("remaining", 0)
        b_avg = batch_info.get("avg_sec", "--")
        
        batch_header_html = f"""
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-3.5 mb-3 space-y-2">
            <div class="flex justify-between items-center text-xs">
                <div class="flex items-center gap-2">
                    <span class="text-slate-800 font-bold">التقدم العام للقائمة كاملة:</span>
                    <span class="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">{b_pct:.1f}%</span>
                </div>
                <div class="text-slate-600 font-mono text-xs flex items-center gap-4">
                    <span>✅ المكتمل: <strong class="text-emerald-700 font-bold text-sm">{b_comp}</strong> فيديو</span>
                    <span>⚡ الجاري: <strong class="text-amber-600 font-bold text-sm">#{b_curr}</strong></span>
                    <span>⏳ المتبقي: <strong class="text-slate-800 font-bold text-sm">{b_rem}</strong> فيديو</span>
                    <span class="bg-slate-200/70 border border-slate-300 px-2.5 py-1 rounded-md text-slate-800 flex items-center gap-1 font-sans">
                        <span>⏱️ متوسط الوقت لكل مقطع:</span>
                        <strong class="text-emerald-700 font-mono font-bold text-sm">{b_avg}</strong>
                    </span>
                </div>
            </div>
            <div class="w-full bg-slate-200 h-3 rounded-full overflow-hidden p-0.5">
                <div class="bg-gradient-to-l from-emerald-500 to-teal-600 h-full rounded-full transition-all duration-500 shadow-sm" style="width: {b_pct:.1f}%;"></div>
            </div>
        </div>
        """

    worker_label = f"ACTIVE_WORKER [#{batch_info.get('current', 1)}]" if (mode == "batch" and batch_info) else "ACTIVE_PROCESS"

    return f"""
    <div class="w-full select-none" dir="rtl">
        {batch_header_html}
        <div class="grid grid-cols-12 gap-3">
            <!-- 1. الدوامة المربعة الحلزونية (شاشة CRT داكنة) -->
            <div class="col-span-3 cyber-chassis rounded-xl p-4 flex flex-col items-center justify-center text-center font-mono">
                <div class="text-[11px] font-bold text-emerald-500 pb-1 border-b border-slate-800 w-full mb-1">
                    {worker_label}
                </div>
                
                <div class="w-28 h-28 flex items-center justify-center relative my-2">
                    <div class="w-24 h-24 spiral-box absolute"></div>
                    <div class="w-16 h-16 spiral-box-inner absolute"></div>
                    <div class="z-10 flex flex-col items-center">
                        <span class="text-emerald-300 font-black text-lg tracking-widest">{pct_display}</span>
                        <span class="{badge_class} text-[10px] font-bold">{badge_text}</span>
                    </div>
                </div>

                <div class="text-xs text-emerald-400 font-bold truncate max-w-[190px] mt-1" title="{safe_topic}">
                    "{safe_topic}"
                </div>
                <span class="text-[10px] text-emerald-600 mt-0.5 truncate max-w-[190px]">[{safe_step}]</span>
            </div>

            <!-- 2. شاشة تيرمينال الهاكر العريضة (شاشة CRT داكنة) -->
            <div class="col-span-9 cyber-chassis hacker-screen rounded-xl p-3.5 flex flex-col justify-between" dir="ltr">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800 text-[11px]">
                    <span class="font-bold text-emerald-400 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                        ROOT@AI-CORE: ~/TERMINAL_FEED
                    </span>
                    <span class="text-slate-500 text-[10px]">LIVE STREAMING // HTTP/7860</span>
                </div>

                <!-- الأسطر التفصيلية بنمط فلكس معكوس للتمرير التلقائي السلس -->
                <div class="hacker-terminal-logs hacker-scroll">
                    <p class="text-emerald-400 animate-pulse font-bold">> {safe_step} <span class="hacker-cursor"></span></p>
                    {reversed_log_html}
                </div>

                <div class="pt-2 border-t border-slate-900 text-[10px] text-slate-500 flex justify-between font-mono">
                    <span>STATUS: {badge_text}</span>
                    <span class="text-emerald-400 font-bold">100% TELEMETRY VERIFIED</span>
                </div>
            </div>
        </div>
    </div>
    """

def run_single_topic(topic):
    config_errors = validate_config()
    if config_errors:
        err_msg = "⛔ خطأ في الإعدادات:\n" + "\n".join(config_errors)
        yield render_dashboard_html(mode="single", percentage=0, step_title="خطأ في الإعدادات", topic=topic, logs=[err_msg], status_type="error")
        return
        
    for progress_data in execute_topic_stream(topic, 1, 1, mode="single"):
        yield render_dashboard_html(**progress_data)

def run_batch_topics(file_obj):
    if not file_obj:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="يرجى اختيار ملف", topic="--", logs=["❌ لم يتم رفع أي ملف JSON."], status_type="error")
        return
        
    config_errors = validate_config()
    if config_errors:
        err_msg = "⛔ خطأ في الإعدادات:\n" + "\n".join(config_errors)
        yield render_dashboard_html(mode="batch", percentage=0, step_title="خطأ في الإعدادات", topic="--", logs=[err_msg], status_type="error")
        return
        
    try:
        with open(file_obj.name, 'r', encoding='utf-8') as f:
            topics = json.load(f)
        if not isinstance(topics, list):
            yield render_dashboard_html(mode="batch", percentage=0, step_title="تنسيق غير صالح", topic="--", logs=["❌ تنسيق الملف غير صالح. يجب أن يكون قائمة JSON."], status_type="error")
            return
    except Exception as e:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="خطأ قراءة", topic="--", logs=[f"❌ خطأ في قراءة الملف: {e}"], status_type="error")
        return
        
    if not topics:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="ملف فارغ", topic="--", logs=["❌ الملف فارغ ولا يحتوي على مواضيع."], status_type="error")
        return

    state = {"queue": topics, "current_index": 0, "in_progress": True, "completed_times": []}
    save_state(state)
    
    yield from process_queue_stream()

def resume_batch():
    config_errors = validate_config()
    if config_errors:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="خطأ إعدادات", topic="--", logs=["⛔ لا يمكن الاستئناف قبل تصحيح الإعدادات."], status_type="error")
        return
        
    state = load_state()
    if not state.get("in_progress") or state.get("current_index", 0) >= len(state.get("queue", [])):
        yield render_dashboard_html(mode="batch", percentage=100, step_title="لا يوجد عمل متبقٍ", topic="--", logs=["لا يوجد عمل غير مكتمل لاستئنافه."])
        return
        
    yield from process_queue_stream()

def process_queue_stream():
    state = load_state()
    queue = state.get("queue", [])
    start_index = state.get("current_index", 0)
    completed_times = state.get("completed_times", [])
    total = len(queue)
    
    for i in range(start_index, total):
        topic = queue[i]
        state["current_index"] = i
        save_state(state)
        
        # حساب متوسط الوقت الحقيقي بدقة تامة
        if completed_times:
            avg_sec = sum(completed_times) / len(completed_times)
            avg_str = f"~{avg_sec:.1f} ثانية"
        else:
            avg_str = "جاري الحساب..."

        b_pct = (i / total) * 100.0
        batch_meta = {
            "pct": b_pct,
            "completed": i,
            "current": i + 1,
            "remaining": total - (i + 1),
            "avg_sec": avg_str
        }
        
        t0 = time.time()
        for update in execute_topic_stream(topic, i + 1, total, mode="batch", batch_info=batch_meta):
            yield render_dashboard_html(**update)
            
        elapsed_item = round(time.time() - t0, 1)
        completed_times.append(elapsed_item)
        state["completed_times"] = completed_times
        save_state(state)
        
    state["in_progress"] = False
    save_state(state)
    
    # بعد اكتمال القائمة كلها
    final_avg = f"~{sum(completed_times) / len(completed_times):.1f} ثانية" if completed_times else "--"
    final_batch_meta = {
        "pct": 100.0,
        "completed": total,
        "current": total,
        "remaining": 0,
        "avg_sec": final_avg
    }
    yield render_dashboard_html(mode="batch", percentage=100, step_title="اكتملت جميع الفيديوهات", topic="جميع الفيديوهات مكتملة", logs=[f"🎉 تم الانتهاء بنجاح من كافة فيديوهات القائمة ({total} فيديو)!"], batch_info=final_batch_meta)

def execute_topic_stream(topic, current_num, total_num, mode="single", batch_info=None):
    if not topic.strip():
        yield {
            "mode": mode,
            "percentage": 0,
            "step_title": "موضوع فارغ",
            "topic": topic,
            "logs": ["❌ يرجى إدخال موضوع صالح أولاً!"],
            "batch_info": batch_info,
            "status_type": "error"
        }
        return

    log_buffer = deque(maxlen=80)
    current_pct = 5
    current_step = "بدء تشغيل بيئة المعالجة..."
    
    log_buffer.append(f"EXECUTE: Starting video #{current_num}/{total_num} -> '{topic}'")
    
    yield {
        "mode": mode,
        "percentage": current_pct,
        "step_title": current_step,
        "topic": topic,
        "logs": list(log_buffer),
        "batch_info": batch_info,
        "status_type": "active"
    }

    try:
        vm_pyc = os.path.join(BASE_DIR, "video_maker.pyc")
        vm_target = vm_pyc if os.path.exists(vm_pyc) else os.path.join(BASE_DIR, "video_maker.py")

        process = subprocess.Popen(
            [sys.executable, '-u', vm_target, '--topic', topic],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        last_yield_time = time.time()
        
        for line in iter(process.stdout.readline, ''):
            line_str = line.strip()
            if not line_str:
                continue

            # تصنيف المراحل والنسبة بدقة من مخرجات video_maker الحقيقية
            if "[الخطوة 1]" in line_str:
                current_pct = 15
                current_step = "كتابة السكربت بالذكاء الاصطناعي..."
            elif "[الخطوة 2]" in line_str:
                current_pct = 30
                current_step = "توليد الصوت العصبي (GuyNeural)..."
            elif "[الخطوة 3]" in line_str:
                current_pct = 48
                current_step = "استخراج التوقيت الدقيق (Faster-Whisper)..."
            elif "[الخطوة 4]" in line_str:
                current_pct = 62
                current_step = "تخطيط توقيتات الصور ومشاهد القصة..."
            elif "[الخطوة 5]" in line_str:
                current_pct = 75
                current_step = "تحميل وتدقيق الصور بالتوازي..."
            elif "[الخطوة 6]" in line_str:
                current_pct = 88
                current_step = "المونتاج والرندر النهائي والمؤثرات..."
            elif "[الخطوة 7]" in line_str:
                current_pct = 95
                current_step = "النشر التلقائي إلى تيليجرام..."
            elif "🎉 تم إنتاج الفيديو" in line_str:
                current_pct = 100
                current_step = "اكتمل إنتاج الفيديو بنجاح!"

            log_buffer.append(line_str)

            # معدل تحديث مضبوط (Throttle) لمنع تهنيج المتصفح
            now = time.time()
            if (now - last_yield_time) >= 0.08 or current_pct in [15, 30, 48, 62, 75, 88, 95, 100]:
                last_yield_time = now
                yield {
                    "mode": mode,
                    "percentage": current_pct,
                    "step_title": current_step,
                    "topic": topic,
                    "logs": list(log_buffer),
                    "batch_info": batch_info,
                    "status_type": "active"
                }

        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            current_pct = 100
            current_step = "اكتمل بنجاح!"
            status_t = "active"
            log_buffer.append("SUCCESS: Video render and pipeline completed cleanly.")
        else:
            status_t = "error"
            current_step = f"خطأ في التنفيذ (كود {process.returncode})"
            log_buffer.append(f"ERROR: Process exited with non-zero returncode {process.returncode}")

        yield {
            "mode": mode,
            "percentage": current_pct,
            "step_title": current_step,
            "topic": topic,
            "logs": list(log_buffer),
            "batch_info": batch_info,
            "status_type": status_t
        }

    except Exception as e:
        log_buffer.append(f"EXCEPTION: {e}")
        yield {
            "mode": mode,
            "percentage": 0,
            "step_title": "حدث خطأ غير متوقع",
            "topic": topic,
            "logs": list(log_buffer),
            "batch_info": batch_info,
            "status_type": "error"
        }

# ==============================================================
# --- تنسيقات CSS العامة (Technical Synthesizer Deck) ---
# ==============================================================

css = """
html, body { 
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden !important;
    direction: rtl; 
    text-align: right; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Consolas', monospace;
    background-color: #f1f5f9;
    color: #0f172a;
}
.gradio-container { 
    max-width: 100% !important; 
    width: 98% !important; 
    height: 100vh !important;
    max-height: 100vh !important;
    margin: 0 auto !important; 
    padding: 6px 12px !important; 
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
.hero-header { 
    background: #ffffff; 
    border: 1px solid #cbd5e1;
    border-right: 4px solid #059669;
    padding: 6px 14px; 
    border-radius: 8px; 
    margin-bottom: 6px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05); 
    flex-shrink: 0;
}
.hero-header h1 { 
    color: #0f172a !important; 
    margin: 0 !important; 
    font-size: 15px !important; 
    font-weight: 700; 
}
.hero-header p { 
    color: #64748b !important; 
    margin: 0 !important; 
    font-size: 11px !important; 
}
.panel-card { 
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 8px; 
    padding: 8px 12px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
}
.panel-title { 
    font-size: 13px !important; 
    font-weight: 700 !important; 
    color: #0f172a !important; 
    margin: 0 0 6px 0 !important; 
    border-bottom: 1.5px solid #f1f5f9; 
    padding-bottom: 3px; 
}
.compact-field {
    margin-bottom: 4px !important;
}
.compact-field label span {
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-bottom: 1px !important;
}
.compact-field input, .compact-field textarea, .compact-field select {
    padding: 3px 8px !important;
    font-size: 12px !important;
    height: 32px !important;
    min-height: 32px !important;
    border-radius: 6px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #f8fafc !important;
}
.compact-file-upload { 
    min-height: 32px !important; 
    height: 32px !important; 
    padding: 0 !important; 
    margin: 0 !important;
}
.compact-file-upload .upload-button, 
.compact-file-upload .wrap { 
    min-height: 30px !important; 
    height: 30px !important; 
    padding: 2px 8px !important; 
    font-size: 11px !important; 
}
.btn-primary-action { 
    height: 36px !important; 
    min-height: 36px !important; 
    font-weight: 700 !important; 
    font-size: 13px !important; 
    border-radius: 6px !important;
    background-color: #059669 !important;
    border: 1px solid #047857 !important;
    color: #ffffff !important;
}
.btn-primary-action:hover {
    background-color: #047857 !important;
}
.tabs {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
.tab-nav { 
    margin-bottom: 6px !important; 
    border-bottom: 2px solid #e2e8f0 !important;
    flex-shrink: 0;
}
.tab-nav > button { 
    font-size: 13px !important; 
    font-weight: 600 !important; 
    padding: 5px 14px !important; 
    color: #64748b !important;
}
.tab-nav > button.selected { 
    color: #059669 !important;
    border-bottom-color: #059669 !important;
}
.tabitem {
    flex: 1 !important;
    overflow: hidden !important;
    padding: 2px 0 !important;
}

/* الشاشتان الداكنتان (Hardware CRT Chassis) */
.cyber-chassis {
    background: #030712 !important;
    border: 1px solid #1e293b !important;
    border-top: 1px solid #334155 !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.9), 0 4px 12px -2px rgba(15, 23, 42, 0.12), 0 0 15px -3px rgba(34, 197, 94, 0.12) !important;
}

@keyframes square-spiral {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.spiral-box {
    border: 2.5px solid transparent;
    border-top-color: #22c55e;
    border-right-color: #4ade80;
    border-radius: 12px;
    animation: square-spiral 3s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
}
.spiral-box-inner {
    border: 2px solid transparent;
    border-bottom-color: #15803d;
    border-left-color: #86efac;
    border-radius: 8px;
    animation: square-spiral 2s linear infinite reverse;
}

.hacker-screen {
    font-family: 'Consolas', 'Courier New', monospace !important;
    color: #22c55e !important;
    text-shadow: 0 0 4px rgba(34, 197, 94, 0.4);
    direction: ltr !important;
    text-align: left !important;
    unicode-bidi: isolate !important;
}
.hacker-terminal-logs {
    display: flex !important;
    flex-direction: column-reverse !important;
    overflow-y: auto !important;
    height: 195px !important;
    max-height: 195px !important;
    padding: 4px 8px !important;
    font-size: 11px !important;
    line-height: 1.5 !important;
}
.hacker-cursor {
    display: inline-block;
    width: 7px;
    height: 13px;
    background-color: #22c55e;
    vertical-align: middle;
    animation: blink 1s step-start infinite;
    box-shadow: 0 0 6px #22c55e;
}
@keyframes blink {
    50% { opacity: 0; }
}
.hacker-scroll::-webkit-scrollbar {
    width: 4px;
}
.hacker-scroll::-webkit-scrollbar-track {
    background: #030712;
}
.hacker-scroll::-webkit-scrollbar-thumb {
    background: #15803d;
    border-radius: 2px;
}
"""

with gr.Blocks(title="🎬 صانع الفيديوهات الآلي - v4", theme=gr.themes.Default(primary_hue="emerald", spacing_size="sm", text_size="sm"), css=css) as demo:
    gr.HTML("""
    <div class="hero-header">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">🎬</span>
                <h1>صانع الفيديوهات الآلي الاحترافي (v4.0)</h1>
                <span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; font-family: monospace;">
                    CYBER WORKBENCH
                </span>
            </div>
            <p>الإنتاج الفائق بالذكاء الاصطناعي مع تحكم متكامل ومتابعة حية بدون أي سكرول</p>
        </div>
        <div style="display: flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-family: monospace; color: #0f172a;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
            <span>SYSTEM_ONLINE</span>
        </div>
    </div>
    """)
    
    current_config = load_config()
    
    with gr.Tabs():
        # ==============================================================
        # --- تبويبة 1: صناعة فيديو مفرد (شاشة حية متقدمة) ---
        # ==============================================================
        with gr.TabItem("🚀 إنتاج فيديو مفرد"):
            with gr.Column(elem_classes=["panel-card"]):
                with gr.Row(equal_height=True):
                    single_topic_input = gr.Textbox(
                        label="موضوع الفيديو المطلوب إنتاجه",
                        placeholder="اكتب الموضوع هنا... مثال: أغرب 5 حقائق علمية عن الكون لم تكن تعرفها",
                        scale=5,
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    single_start_btn = gr.Button("🚀 بدء الإنتاج الفوري", variant="primary", scale=1, elem_classes=["btn-primary-action"])
            
            single_output_log = gr.HTML(
                value=render_dashboard_html(mode="single", percentage=0, step_title="جاهز للبدء", topic="بانتظار إدخال الموضوع...")
            )
            single_start_btn.click(fn=run_single_topic, inputs=single_topic_input, outputs=single_output_log)

        # ==============================================================
        # --- تبويبة 2: الإنتاج بالجملة (لوحة القيادة الحية) ---
        # ==============================================================
        with gr.TabItem("📚 إنتاج بالجملة (JSON)"):
            with gr.Column(elem_classes=["panel-card"]):
                resume_alert = gr.Markdown(visible=False)
                resume_btn = gr.Button("🔄 استكمال العمل السابق غير المكتمل", variant="stop", visible=False, elem_classes=["btn-primary-action"])
                
                with gr.Row(equal_height=True):
                    json_file_input = gr.File(label="ملف قائمة المواضيع (JSON)", file_types=[".json"], scale=4, elem_classes=["compact-file-upload"])
                    batch_start_btn = gr.Button("🚀 إنتاج القائمة كاملة", variant="primary", scale=1, elem_classes=["btn-primary-action"])
                
            batch_output_log = gr.HTML(
                value=render_dashboard_html(mode="batch", percentage=0, step_title="جاهز للبدء", topic="بانتظار تحميل القائمة...")
            )
            
            batch_start_btn.click(fn=run_batch_topics, inputs=json_file_input, outputs=batch_output_log)
            resume_btn.click(fn=resume_batch, outputs=batch_output_log)
            
            demo.load(fn=check_resume_status, outputs=resume_alert)
            demo.load(fn=lambda: gr.update(visible=True) if load_state().get("in_progress") else gr.update(visible=False), outputs=resume_btn)

        # ==============================================================
        # --- تبويبة 3: إدارة وسائط ومونتاج الفيديو ---
        # ==============================================================
        with gr.TabItem("🎥 وسائط ومقاطع المونتاج"):
            with gr.Row():
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>🎮 الجيم بلاي وفيديوهات الهوك وصوت الهوك</div>")
                    with gr.Row(equal_height=True):
                        gameplay_path_input = gr.Textbox(
                            label="🎮 فيديو الجيم بلاي (الخلفية)",
                            value=current_config.get("gameplay_path", ""),
                            placeholder="مسار MP4",
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        gameplay_file_upload = gr.File(label="رفع", file_types=[".mp4", ".mov", ".mkv"], scale=1, elem_classes=["compact-file-upload"])
                    
                    with gr.Row(equal_height=True):
                        hook_dir_input = gr.Textbox(
                            label="🎯 مجلد فيديوهات الهوك (Hook Folder)",
                            value=current_config.get("hook_dir", ""),
                            placeholder="مسار المجلد",
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        hooks_folder_upload = gr.File(
                            label="رفع",
                            file_count="multiple",
                            file_types=[".mp4", ".mov", ".mkv"],
                            scale=1,
                            elem_classes=["compact-file-upload"]
                        )
                    
                    with gr.Row(equal_height=True):
                        hook_audio_input = gr.Textbox(
                            label="🔊 صوت نهاية الهوك (1.7x)",
                            value=current_config.get("hook_audio_source", ""),
                            placeholder="مسار صوت الهوك",
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        hook_audio_upload = gr.File(label="رفع", file_types=[".mp4", ".mp3", ".wav", ".m4a"], scale=1, elem_classes=["compact-file-upload"])

                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>🎵 الموسيقى التصويرية ومقطع الخاتمة</div>")
                    with gr.Row(equal_height=True):
                        bg_music_input = gr.Textbox(
                            label="🎵 موسيقى الخلفية (Background Music)",
                            value=current_config.get("bg_music_path", ""),
                            placeholder="مسار ملف الموسيقى",
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        bg_music_upload = gr.File(label="رفع", file_types=[".mp4", ".mp3", ".wav", ".m4a"], scale=1, elem_classes=["compact-file-upload"])

                    with gr.Row(equal_height=True):
                        outro_path_input = gr.Textbox(
                            label="🎬 فيديو الخاتمة (Outro Clip)",
                            value=current_config.get("outro_path", ""),
                            placeholder="مسار فيديو الخاتمة",
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        outro_upload = gr.File(label="رفع", file_types=[".mp4", ".mov", ".mkv"], scale=1, elem_classes=["compact-file-upload"])

                    with gr.Row():
                        save_assets_btn = gr.Button("💾 حفظ وتطبيق مسارات الوسائط", variant="primary", elem_classes=["btn-primary-action"])
                    save_assets_status = gr.Markdown("")

        # ==============================================================
        # --- تبويبة 4: إعدادات الذكاء الاصطناعي وتيليجرام ---
        # ==============================================================
        with gr.TabItem("⚙️ الإعدادات الأساسية وتيليجرام"):
            with gr.Row():
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>🤖 إعدادات الذكاء الاصطناعي ومعلق الصوت</div>")
                    api_url_input = gr.Textbox(
                        label="رابط الـ API (API Base URL)",
                        value=current_config.get("api_url", ""),
                        placeholder="http://127.0.0.1:8008/v1/chat/completions",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    api_key_input = gr.Textbox(
                        label="مفتاح الـ API Key",
                        value=current_config.get("api_key", ""),
                        type="password",
                        placeholder="sk-...",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    voice_choices = [
                        "en-US-GuyNeural - en-US (Male)",
                        "en-US-ChristopherNeural - en-US (Male)",
                        "en-US-JennyNeural - en-US (Female)",
                        "en-US-BrianMultilingualNeural - en-US (Male)",
                        "en-US-AriaNeural - en-US (Female)"
                    ]
                    current_voice = current_config.get("voice", "en-US-GuyNeural - en-US (Male)")
                    if current_voice not in voice_choices:
                        voice_choices.insert(0, current_voice)
                    voice_input = gr.Dropdown(
                        label="🎙️ صوت الراوي المعتمد بالذكاء الاصطناعي",
                        choices=voice_choices,
                        value=current_voice,
                        elem_classes=["compact-field"]
                    )

                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>✈️ إعدادات النشر على تيليجرام</div>")
                    upload_telegram_checkbox = gr.Checkbox(
                        label="نشر الفيديوهات تلقائياً إلى تيليجرام (مفعّل افتراضياً)",
                        value=current_config.get("upload_to_telegram", True),
                        info="إلغاء التحديد يحفظ الفيديو في جهازك فقط دون رفعه للقناة."
                    )
                    bot_token_input = gr.Textbox(
                        label="توكن بوت تيليجرام (Bot Token)",
                        value=current_config.get("bot_token", ""),
                        type="password",
                        placeholder="YOUR_TELEGRAM_BOT_TOKEN",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    channel_id_input = gr.Textbox(
                        label="مُعرّف القناة (Channel ID)",
                        value=current_config.get("channel_id", ""),
                        placeholder="YOUR_TELEGRAM_CHANNEL_ID",
                        lines=1,
                        elem_classes=["compact-field"]
                    )

            with gr.Row():
                save_api_btn = gr.Button("💾 حفظ وتطبيق كافة الإعدادات الأساسية", variant="primary", elem_classes=["btn-primary-action"])
            save_api_status = gr.Markdown("")

    def do_save(api_url, api_key, bot_token, channel_id, upload_tg, voice, gp, hk_d, hk_s, bg, out):
        return save_config(api_url, api_key, bot_token, channel_id, upload_tg, voice, gp, hk_d, hk_s, bg, out)

    all_inputs = [
        api_url_input, api_key_input, bot_token_input, channel_id_input, upload_telegram_checkbox, voice_input,
        gameplay_path_input, hook_dir_input, hook_audio_input, bg_music_input, outro_path_input
    ]

    save_assets_btn.click(fn=do_save, inputs=all_inputs, outputs=save_assets_status)
    save_api_btn.click(fn=do_save, inputs=all_inputs, outputs=save_api_status)

if __name__ == "__main__":
    import auth_guard
    auth_guard.check_access_or_prompt()
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
