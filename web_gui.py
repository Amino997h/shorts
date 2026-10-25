import gradio as gr
import subprocess
import os
import sys
import json
import time
import shutil
import html
import re
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
    
    # تحديد رموز الحالة التقنية (Status Token)
    substep_token = "WORKING"
    if status_type == "error":
        substep_token = "ERROR"
    elif percentage >= 100:
        substep_token = "COMPLETED"
    elif "[الخطوة 1]" in step_title or "السكربت" in step_title:
        substep_token = "GENERATING_SCRIPT"
    elif "[الخطوة 2]" in step_title or "الصوت" in step_title:
        substep_token = "SYNTHESIZING_VOICE"
    elif "[الخطوة 3]" in step_title or "Whisper" in step_title:
        substep_token = "WHISPER_SYNCING"
    elif "[الخطوة 4]" in step_title or "تخطيط" in step_title:
        substep_token = "STORYBOARDING"
    elif "[الخطوة 5]" in step_title or "الصور" in step_title:
        substep_token = "SCRAPING_MEDIA"
    elif "[الخطوة 6]" in step_title or "المونتاج" in step_title or "الرندر" in step_title:
        substep_token = "COMPOSING"
    elif "[الخطوة 7]" in step_title or "تيليجرام" in step_title:
        substep_token = "PUBLISHING"

    # تنسيق وتلوين أسطر الهاكر
    formatted_logs = []
    for line in logs:
        line_clean = line.strip()
        if not line_clean:
            continue
        ts = datetime.now().strftime("%H:%M:%S")
        safe_line = html.escape(line_clean)
        
        # تحويل الأسطر إلى تنسيقات الهاكر الأنيقة والمطابقة للتصميم
        if "BATCH_SUCCESS" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-400 font-bold">BATCH_SUCCESS</span> <span class="text-emerald-300">{safe_line.replace("BATCH_SUCCESS", "").strip()}</span></p>')
        elif "BATCH_INIT" in line_clean or "Starting video" in line_clean:
            formatted_logs.append(f'<p><span class="text-yellow-400 font-bold">BATCH_INIT</span> <span class="text-slate-300">{safe_line.replace("BATCH_INIT", "").replace("EXECUTE:", "").strip()}</span></p>')
        elif "[الخطوة 1]" in line_clean or "كتابة السكربت" in line_clean or "API_POST" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-300 font-bold">API_POST</span> <span class="text-emerald-400">{safe_line}</span></p>')
        elif "تم توليد السكربت" in line_clean or "SCRIPT_200" in line_clean or "--- السكريبت ---" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-400 font-bold">SCRIPT_200</span> <span class="text-emerald-300">{safe_line}</span></p>')
        elif "[الخطوة 2]" in line_clean or "توليد الصوت" in line_clean or "EDGE_TTS" in line_clean:
            formatted_logs.append(f'<p><span class="text-yellow-400 font-bold">EDGE_TTS</span> <span class="text-yellow-300">{safe_line}</span></p>')
        elif "[الخطوة 3]" in line_clean or "Whisper" in line_clean or "WHISPER_SYNC" in line_clean:
            formatted_logs.append(f'<p><span class="text-cyan-400 font-bold">WHISPER_SYNC</span> <span class="text-cyan-300">{safe_line}</span></p>')
        elif "جاري البحث عن:" in line_clean or "BING" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-300 font-bold">BING_QUERY</span> <span class="text-emerald-200">{safe_line}</span></p>')
        elif "IMG_200" in line_clean or "تم تنزيل وتدقيق" in line_clean or "تم تحميل:" in line_clean or "[الخطوة 5]" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-400 font-bold">IMG_200</span> <span class="text-emerald-300">{safe_line}</span></p>')
        elif "[الخطوة 6]" in line_clean or "المونتاج" in line_clean or "COMPOSITOR" in line_clean or "Rendering" in line_clean:
            formatted_logs.append(f'<p><span class="text-purple-400 font-bold">COMPOSITOR</span> <span class="text-purple-300">{safe_line}</span></p>')
        elif "✓" in line_clean or "تم إنتاج الفيديو" in line_clean or "SUCCESS" in line_clean:
            formatted_logs.append(f'<p><span class="text-emerald-400 font-bold">[OK]</span> <span class="text-emerald-300">{safe_line}</span></p>')
        elif "⚠️" in line_clean or "تنبيه" in line_clean or "WARN" in line_clean:
            formatted_logs.append(f'<p><span class="text-yellow-400 font-bold">[WARN]</span> <span class="text-yellow-300">{safe_line}</span></p>')
        elif "❌" in line_clean or "خطأ" in line_clean or "ERROR" in line_clean:
            formatted_logs.append(f'<p><span class="text-rose-400 font-bold">[ERROR]</span> <span class="text-rose-300">{safe_line}</span></p>')
        else:
            formatted_logs.append(f'<p><span class="text-slate-500 font-mono">[{ts}]</span> <span class="text-slate-400 font-mono">> {safe_line}</span></p>')

    if not formatted_logs:
        formatted_logs.append('<p><span class="text-emerald-500 font-bold">[SYSTEM_READY]</span> <span class="text-slate-400">Core Synthesizer initialized. HTTP/7860</span></p>')
        formatted_logs.append('<p><span class="text-cyan-400 font-bold">[PIPELINE]</span> <span class="text-slate-300">Modules: Script, TTS, Whisper, Compositor ACTIVE</span></p>')
        formatted_logs.append('<p><span class="text-yellow-400 font-bold">[STANDBY]</span> <span class="text-slate-300">> Awaiting process initiation...</span></p>')

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

    # تجهيز تفاصيل الوضعين (Batch vs Single)
    if mode == "batch" and batch_info:
        b_pct = batch_info.get("pct", 0.0)
        b_comp = batch_info.get("completed", 0)
        b_curr = batch_info.get("current", 1)
        b_rem = batch_info.get("remaining", 0)
        b_avg = batch_info.get("avg_sec", "--")
        b_total = b_comp + b_rem + (1 if b_rem > 0 or b_comp < b_curr else 0)
        if b_total == 0:
            b_total = max(b_curr, 1)

        batch_header_html = f"""
        <div class="cyber-batch-card bg-slate-50 border border-slate-200 rounded-xl p-3.5 mb-3 space-y-2">
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
            <div class="w-full bg-slate-200 h-3 rounded-full overflow-hidden p-0.5" style="height: 12px; background: #e2e8f0; border-radius: 9999px;">
                <div class="bg-gradient-to-l from-emerald-500 to-teal-600 h-full rounded-full transition-all duration-500 shadow-sm" style="width: {b_pct:.1f}%; height: 100%; border-radius: 9999px; background: linear-gradient(to left, #10b981, #0d9488);"></div>
            </div>
        </div>
        """

        # نصوص الصندوقين مطابقة 100% للبريفيو المعتمد
        spiral_top_tag = f"ACTIVE_WORKER [#{b_curr}]"
        spiral_center_badge = f'<span class="z-10 text-emerald-300 font-black text-xl font-mono tracking-widest">#{b_curr}</span>'
        spiral_status_bottom = f'<span class="text-[10px] text-emerald-600 mt-0.5">[STATUS: {substep_token}]</span>'

        term_head_left = f'<span class="font-bold text-emerald-400">BATCH_QUEUE: [{b_curr}/{b_total} VIDEOS]</span>'
        term_head_right = '<span class="text-emerald-600 text-[10px]">ACTIVE WORKER</span>'
        term_foot_left = f'<span>TOTAL_COMPLETED: {b_comp}</span>'
        term_foot_right = '<span class="text-emerald-400 font-bold">SYSTEM_HEALTH: 100%</span>'
    else:
        batch_header_html = ""
        spiral_top_tag = "CURRENT_PROCESS"
        spiral_center_badge = f"""
        <div class="z-10 flex flex-col items-center">
            <span class="text-emerald-300 font-black text-lg tracking-widest">{pct_display}</span>
            <span class="{badge_class} text-[10px] font-bold">{badge_text}</span>
        </div>
        """
        spiral_status_bottom = f'<span class="text-[10px] text-emerald-600 mt-0.5">[{safe_step}]</span>'

        term_head_left = """
        <span class="font-bold text-emerald-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            ROOT@AI-CORE: ~/TERMINAL_FEED
        </span>
        """
        term_head_right = '<span class="text-slate-500 text-[10px]">LIVE STREAMING // HTTP/7860</span>'
        term_foot_left = f'<span>STATUS: {badge_text}</span>'
        term_foot_right = '<span class="text-emerald-400 font-bold">100% TELEMETRY VERIFIED</span>'

    return f"""
    <div class="cyber-deck-wrapper w-full select-none" dir="rtl">
        {batch_header_html}
        <div class="cyber-deck-grid grid grid-cols-12 gap-3">
            <!-- 1. الدوامة المربعة الحلزونية (شاشة CRT داكنة) -->
            <div class="cyber-spiral-panel col-span-3 cyber-chassis rounded-xl p-4 flex flex-col items-center justify-between text-center font-mono">
                <div class="text-[11px] font-bold text-yellow-400 pb-1 border-b border-slate-800 w-full mb-1">
                    {spiral_top_tag}
                </div>
                
                <div class="spiral-stage w-24 h-24 flex items-center justify-center relative my-2">
                    <div class="w-20 h-20 spiral-box absolute"></div>
                    <div class="w-14 h-14 spiral-box-inner absolute"></div>
                    <div class="spiral-center-badge">
                        {spiral_center_badge}
                    </div>
                </div>

                <div class="text-xs font-bold text-emerald-400 truncate max-w-[190px] mt-1" title="{safe_topic}">
                    "{safe_topic}"
                </div>
                {spiral_status_bottom}
            </div>

            <!-- 2. شاشة تيرمينال الهاكر العريضة (شاشة CRT داكنة) -->
            <div class="cyber-terminal-panel col-span-9 cyber-chassis hacker-screen rounded-xl p-3.5 flex flex-col justify-between" dir="ltr">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800 text-[11px]">
                    {term_head_left}
                    {term_head_right}
                </div>

                <!-- الأسطر التفصيلية بنمط فلكس معكوس للتمرير التلقائي السلس -->
                <div class="hacker-terminal-logs hacker-scroll">
                    <p class="text-emerald-400 animate-pulse font-bold">> {safe_step} <span class="hacker-cursor"></span></p>
                    {reversed_log_html}
                </div>

                <div class="pt-2 border-t border-slate-900 text-[10px] text-slate-500 flex justify-between font-mono">
                    {term_foot_left}
                    {term_foot_right}
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

def extract_topics_from_file(file_obj):
    """
    استخراج فائق المرونة لقائمة المواضيع من أي ملف يتم رفعه عبر Gradio:
    - يدعم مختلف أشكال كائن file_obj في إصدارات Gradio (str, dict, tempfile, FileData, file-like).
    - يدعم ملفات JSON (قائمة نصوص، أو كائن يحتوي مفتاح topics/videos/list، أو قائمة قواميس).
    - يدعم ملفات TXT العادية (سطر لكل موضوع).
    - يدعم ملفات utf-8-sig (BOM)، utf-8، cp1256 (Windows Arabic)، وغيرها.
    """
    if not file_obj:
        return []

    # معالجة التفاف الملف في قائمة (في حال رفع مفرد داخل مصفوفة)
    if isinstance(file_obj, list):
        if not file_obj:
            return []
        file_obj = file_obj[0]

    raw_bytes = None

    # الحالة 1: قاموس بيانات Gradio (e.g. {"name": "...", "path": "..."})
    if isinstance(file_obj, dict):
        path = file_obj.get("path") or file_obj.get("name")
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                raw_bytes = f.read()
        elif "data" in file_obj:
            data = file_obj["data"]
            raw_bytes = data.encode("utf-8") if isinstance(data, str) else data

    # الحالة 2: كائن له خاصية 'path' (مثل Gradio v4+ FileData)
    elif hasattr(file_obj, "path") and isinstance(file_obj.path, str) and os.path.exists(file_obj.path):
        with open(file_obj.path, "rb") as f:
            raw_bytes = f.read()

    # الحالة 3: كائن له خاصية 'name' (مثل tempfile._TemporaryFileWrapper أو NamedString)
    elif hasattr(file_obj, "name") and isinstance(file_obj.name, str) and os.path.exists(file_obj.name):
        with open(file_obj.name, "rb") as f:
            raw_bytes = f.read()

    # الحالة 4: مسار كـ string أو نص مباشر
    elif isinstance(file_obj, str):
        if os.path.exists(file_obj):
            with open(file_obj, "rb") as f:
                raw_bytes = f.read()
        else:
            raw_bytes = file_obj.encode("utf-8")

    # الحالة 5: كائن شبيه بالملفات (file-like) يحتوي دالة .read()
    elif hasattr(file_obj, "read"):
        data = file_obj.read()
        if isinstance(data, bytes):
            raw_bytes = data
        elif isinstance(data, str):
            raw_bytes = data.encode("utf-8")

    if not raw_bytes:
        return []

    # فك الترميز بمرونة عالية لمنع أي خطأ ترميز
    content = None
    for enc in ("utf-8-sig", "utf-8", "cp1256", "windows-1256", "iso-8859-1", "latin-1"):
        try:
            content = raw_bytes.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if content is None:
        content = raw_bytes.decode("utf-8", errors="replace")

    # تنظيف علامة BOM والمسافات الزائدة
    content = content.lstrip('\ufeff').strip()
    if not content:
        return []

    # إزالة تغليف Markdown إذا قام المستخدم بنسخ كود مثل ```json ... ```
    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    def _extract_from_item(item):
        """استخراج نص الموضوع من أي عنصر (سلسلة نصية، قاموس، أو غيره)"""
        if isinstance(item, str):
            val = item.strip()
            return val if val else None
        elif isinstance(item, dict):
            # البحث عن المفاتيح الشائعة أولاً
            for key in ("topic", "title", "subject", "name", "prompt", "text", "query", "عنوان", "الموضوع", "موضوع"):
                if key in item and item[key]:
                    val = str(item[key]).strip()
                    if val:
                        return val
            # وإلا اختيار أول قيمة نصية غير فارغة
            for val in item.values():
                if isinstance(val, str) and val.strip():
                    return val.strip()
            # أو أي قيمة أولية (رقم / قيمة صالحة)
            for val in item.values():
                if val is not None and not isinstance(val, (dict, list)):
                    s = str(val).strip()
                    if s:
                        return s
        elif item is not None:
            s = str(item).strip()
            if s:
                return s
        return None

    topics = []

    # المحاولة 1: قراءة الملف كـ JSON
    try:
        parsed_json = json.loads(content)
    except Exception:
        parsed_json = None

    if parsed_json is not None:
        # أ) JSON مصفوفة من العناصر
        if isinstance(parsed_json, list):
            for it in parsed_json:
                t = _extract_from_item(it)
                if t:
                    topics.append(t)
        # ب) JSON كائن يحتوي على مصفوفة مواضيع
        elif isinstance(parsed_json, dict):
            list_found = None
            for key in ("topics", "list", "videos", "items", "data", "prompts", "titles", "queue", "مواضيع", "قائمة"):
                if key in parsed_json and isinstance(parsed_json[key], list):
                    list_found = parsed_json[key]
                    break
            if list_found is None:
                for v in parsed_json.values():
                    if isinstance(v, list):
                        list_found = v
                        break
            if list_found is not None:
                for it in list_found:
                    t = _extract_from_item(it)
                    if t:
                        topics.append(t)
            else:
                # إذا كان القاموس نفسه يمثل موضوعاً واحداً
                t = _extract_from_item(parsed_json)
                if t:
                    topics.append(t)

    # المحاولة 2: في حال لم يكن JSON صالحاً أو لم ينتج مواضيع، تحليله كملف نصي عادي سطر بسطر
    if not topics:
        for line in content.splitlines():
            line = line.strip()
            if not line or line in ("[", "]", "{", "}"):
                continue
            # دعم سطور JSON المستقلة (JSONL)
            if (line.startswith("{") and line.endswith("}")) or (line.startswith("[") and line.endswith("]")):
                try:
                    item = json.loads(line)
                    if isinstance(item, list):
                        for sub in item:
                            t = _extract_from_item(sub)
                            if t:
                                topics.append(t)
                    else:
                        t = _extract_from_item(item)
                        if t:
                            topics.append(t)
                    continue
                except Exception:
                    pass

            # تنظيف الفواصل البادئة والنقاط التعدادية وعلامات التنصيص
            clean_line = line.rstrip(",")
            m = re.match(r"^(\s*[-*•]\s+|\s*\d+[\.\-\)]\s+)(.*)$", clean_line)
            if m:
                clean_line = m.group(2).strip()
            if (clean_line.startswith('"') and clean_line.endswith('"')) or (clean_line.startswith("'") and clean_line.endswith("'")):
                clean_line = clean_line[1:-1].strip()

            if clean_line and clean_line not in ("[", "]", "{", "}"):
                topics.append(clean_line)

    return topics

def run_batch_topics(file_obj):
    if not file_obj:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="يرجى اختيار ملف", topic="--", logs=["❌ لم يتم رفع أي ملف."], status_type="error")
        return
        
    config_errors = validate_config()
    if config_errors:
        err_msg = "⛔ خطأ في الإعدادات:\n" + "\n".join(config_errors)
        yield render_dashboard_html(mode="batch", percentage=0, step_title="خطأ في الإعدادات", topic="--", logs=[err_msg], status_type="error")
        return
        
    try:
        topics = extract_topics_from_file(file_obj)
    except Exception as e:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="خطأ قراءة", topic="--", logs=[f"❌ خطأ غير متوقع أثناء معالجة الملف: {e}"], status_type="error")
        return
        
    if not topics:
        yield render_dashboard_html(mode="batch", percentage=0, step_title="ملف فارغ أو غير مدعوم", topic="--", logs=["❌ تعذر استخراج أي مواضيع صالحة من الملف. يرجى التأكد من رفع ملف JSON أو ملف نصي TXT يحتوي على المواضيع."], status_type="error")
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
            if mode == "batch":
                log_buffer.append(f"BATCH_SUCCESS [{current_num}/{total_num}] '{topic}' exported cleanly")
            else:
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

css = r"""
html, body { 
    min-height: 100vh;
    margin: 0;
    padding: 0;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    direction: rtl; 
    text-align: right; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Consolas', monospace;
    background-color: #f1f5f9;
    color: #0f172a;
}
.gradio-container { 
    max-width: 100% !important; 
    width: 98% !important; 
    min-height: 100vh !important;
    height: auto !important;
    margin: 0 auto !important; 
    padding: 6px 12px 24px 12px !important; 
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
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
    overflow: visible !important;
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
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 2px 0 !important;
}

/* ============================================================== */
/* --- لوحة القيادة الحية وشاشات CRT الهاكر الداكنة --- */
/* ============================================================== */

.cyber-deck-wrapper {
    width: 100% !important;
    margin-top: 6px !important;
    box-sizing: border-box !important;
}
.cyber-deck-grid {
    display: flex !important;
    flex-direction: row !important;
    gap: 12px !important;
    align-items: stretch !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
.cyber-spiral-panel {
    width: 250px !important;
    min-width: 250px !important;
    max-width: 260px !important;
    flex-shrink: 0 !important;
    background: #030712 !important;
    border: 1px solid #1e293b !important;
    border-top: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: space-between !important;
    text-align: center !important;
    box-sizing: border-box !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.9), 0 4px 12px -2px rgba(15, 23, 42, 0.12), 0 0 15px -3px rgba(34, 197, 94, 0.12) !important;
}
.cyber-terminal-panel {
    flex: 1 !important;
    min-width: 0 !important;
    background: #030712 !important;
    border: 1px solid #1e293b !important;
    border-top: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-sizing: border-box !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.9), 0 4px 12px -2px rgba(15, 23, 42, 0.12), 0 0 15px -3px rgba(34, 197, 94, 0.12) !important;
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
.spiral-stage {
    width: 90px !important;
    height: 90px !important;
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 6px auto !important;
}
.spiral-box {
    width: 80px !important;
    height: 80px !important;
    position: absolute !important;
    top: 5px !important;
    left: 5px !important;
    box-sizing: border-box !important;
    border: 2.5px solid transparent !important;
    border-top-color: #22c55e !important;
    border-right-color: #4ade80 !important;
    border-radius: 14px !important;
    animation: square-spiral 3s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite !important;
    box-shadow: 0 0 12px rgba(34, 197, 94, 0.35) !important;
}
.spiral-box-inner {
    width: 52px !important;
    height: 52px !important;
    position: absolute !important;
    top: 19px !important;
    left: 19px !important;
    box-sizing: border-box !important;
    border: 2px solid transparent !important;
    border-bottom-color: #15803d !important;
    border-left-color: #86efac !important;
    border-radius: 10px !important;
    animation: square-spiral 2s linear infinite reverse !important;
}
.spiral-center-badge {
    position: relative !important;
    z-index: 10 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    pointer-events: none !important;
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
    overflow-x: hidden !important;
    height: 195px !important;
    min-height: 195px !important;
    max-height: 195px !important;
    padding: 6px 10px !important;
    font-size: 11.5px !important;
    line-height: 1.55 !important;
    box-sizing: border-box !important;
    background: rgba(0, 0, 0, 0.45) !important;
    border-radius: 6px !important;
    border: 1px solid #111827 !important;
}
.hacker-terminal-logs p {
    margin: 1.5px 0 !important;
    padding: 0 !important;
    line-height: 1.5 !important;
    white-space: pre-wrap !important;
    word-break: break-all !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
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
    width: 5px;
}
.hacker-scroll::-webkit-scrollbar-track {
    background: #030712;
}
.hacker-scroll::-webkit-scrollbar-thumb {
    background: #15803d;
    border-radius: 3px;
}

/* ============================================================== */
/* --- Pure CSS Tailwind Equivalents for Gradio Compatibility --- */
/* ============================================================== */
.grid { display: grid !important; }
.grid-cols-12 { grid-template-columns: repeat(12, minmax(0, 1fr)) !important; }
.col-span-3 { grid-column: span 3 / span 3 !important; }
.col-span-9 { grid-column: span 9 / span 9 !important; }
.gap-1 { gap: 4px !important; }
.gap-1\.5 { gap: 6px !important; }
.gap-2 { gap: 8px !important; }
.gap-3 { gap: 12px !important; }
.gap-4 { gap: 16px !important; }

.flex { display: flex !important; }
.flex-col { flex-direction: column !important; }
.items-center { align-items: center !important; }
.justify-center { justify-content: center !important; }
.justify-between { justify-content: space-between !important; }

.w-full { width: 100% !important; }
.w-2 { width: 8px !important; }
.h-2 { height: 8px !important; }
.w-14 { width: 56px !important; }
.h-14 { height: 56px !important; }
.w-20 { width: 80px !important; }
.h-20 { height: 80px !important; }
.w-24 { width: 96px !important; }
.h-24 { height: 96px !important; }
.h-full { height: 100% !important; }
.h-3 { height: 12px !important; }

.relative { position: relative !important; }
.absolute { position: absolute !important; }
.z-10 { z-index: 10 !important; }

.p-0\.5 { padding: 2px !important; }
.p-3\.5 { padding: 14px !important; }
.p-4 { padding: 16px !important; }
.px-2 { padding-left: 8px !important; padding-right: 8px !important; }
.px-2\.5 { padding-left: 10px !important; padding-right: 10px !important; }
.py-0\.5 { padding-top: 2px !important; padding-bottom: 2px !important; }
.py-1 { padding-top: 4px !important; padding-bottom: 4px !important; }
.pb-1 { padding-bottom: 4px !important; }
.pb-2 { padding-bottom: 8px !important; }
.pt-2 { padding-top: 8px !important; }
.mb-1 { margin-bottom: 4px !important; }
.mb-3 { margin-bottom: 12px !important; }
.mt-0\.5 { margin-top: 2px !important; }
.mt-1 { margin-top: 4px !important; }
.my-2 { margin-top: 8px !important; margin-bottom: 8px !important; }

.space-y-2 > * + * { margin-top: 8px !important; }

.rounded { border-radius: 4px !important; }
.rounded-md { border-radius: 6px !important; }
.rounded-xl { border-radius: 12px !important; }
.rounded-full { border-radius: 9999px !important; }

.border { border-width: 1px !important; border-style: solid !important; }
.border-b { border-bottom-width: 1px !important; border-bottom-style: solid !important; }
.border-t { border-top-width: 1px !important; border-top-style: solid !important; }
.border-slate-200 { border-color: #e2e8f0 !important; }
.border-slate-300 { border-color: #cbd5e1 !important; }
.border-slate-800 { border-color: #1e293b !important; }
.border-slate-900 { border-color: #0f172a !important; }
.border-emerald-200 { border-color: #a7f3d0 !important; }

.bg-slate-50 { background-color: #f8fafc !important; }
.bg-slate-200 { background-color: #e2e8f0 !important; }
.bg-emerald-100 { background-color: #d1fae5 !important; }
.bg-emerald-500 { background-color: #10b981 !important; }

.text-emerald-200 { color: #a7f3d0 !important; }
.text-emerald-300 { color: #6ee7b7 !important; }
.text-emerald-400 { color: #34d399 !important; }
.text-emerald-500 { color: #10b981 !important; }
.text-emerald-600 { color: #059669 !important; }
.text-emerald-700 { color: #047857 !important; }
.text-yellow-300 { color: #fde047 !important; }
.text-yellow-400 { color: #facc15 !important; }
.text-amber-600 { color: #d97706 !important; }
.text-cyan-300 { color: #67e8f9 !important; }
.text-cyan-400 { color: #22d3ee !important; }
.text-purple-300 { color: #d8b4fe !important; }
.text-purple-400 { color: #c084fc !important; }
.text-rose-300 { color: #fda4af !important; }
.text-rose-400 { color: #fb7185 !important; }
.text-slate-300 { color: #cbd5e1 !important; }
.text-slate-400 { color: #94a3b8 !important; }
.text-slate-500 { color: #64748b !important; }
.text-slate-600 { color: #475569 !important; }
.text-slate-800 { color: #1e293b !important; }

.font-mono { font-family: 'Consolas', 'Courier New', monospace !important; }
.font-sans { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }
.font-bold { font-weight: 700 !important; }
.font-black { font-weight: 900 !important; }

.text-xs { font-size: 12px !important; }
.text-sm { font-size: 14px !important; }
.text-lg { font-size: 18px !important; }
.text-xl { font-size: 20px !important; }
.text-\[10px\] { font-size: 10px !important; }
.text-\[11px\] { font-size: 11px !important; }

.tracking-widest { letter-spacing: 0.1em !important; }
.truncate { overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
.max-w-\[190px\] { max-width: 190px !important; }
.select-none { user-select: none !important; }
.overflow-hidden { overflow: hidden !important; }

.bg-gradient-to-l { background-image: linear-gradient(to left, var(--tw-gradient-stops, #10b981, #0d9488)) !important; }
.from-emerald-500 { --tw-gradient-from: #10b981; }
.to-teal-600 { --tw-gradient-to: #0d9488; }

@keyframes ping {
    75%, 100% {
        transform: scale(2);
        opacity: 0;
    }
}
.animate-ping {
    animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite !important;
}
@keyframes pulse {
    50% { opacity: .5; }
}
.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite !important;
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
        with gr.TabItem("📚 إنتاج بالجملة (JSON / TXT)"):
            with gr.Column(elem_classes=["panel-card"]):
                resume_alert = gr.Markdown(visible=False)
                resume_btn = gr.Button("🔄 استكمال العمل السابق غير المكتمل", variant="stop", visible=False, elem_classes=["btn-primary-action"])
                
                with gr.Row(equal_height=True):
                    json_file_input = gr.File(label="ملف قائمة المواضيع (JSON أو TXT)", file_types=[".json", ".txt", "text"], scale=4, elem_classes=["compact-file-upload"])
                    batch_start_btn = gr.Button("🚀 إنتاج القائمة كاملة", variant="primary", scale=1, elem_classes=["btn-primary-action"])
                
            batch_output_log = gr.HTML(
                value=render_dashboard_html(
                    mode="batch",
                    percentage=0,
                    step_title="جاهز للبدء",
                    topic="بانتظار تحميل القائمة...",
                    batch_info={"pct": 0.0, "completed": 0, "current": 1, "remaining": 0, "avg_sec": "--"}
                )
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
