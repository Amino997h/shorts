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

# ==============================================================
# --- قاموس الترجمة متعدد اللغات (i18n Multi-Language System) ---
# ==============================================================

TRANSLATIONS = {
    "en": {
        # App Header & Meta
        "page_title": "🎬 Automated Video Producer - v4",
        "hero_title": "Automated Video Producer Pro (v4.0)",
        "hero_badge": "CYBER WORKBENCH",
        "hero_subtitle": "AI-Powered Video Generation with Live Synthesizer Deck & Seamless Pipeline",
        "system_online": "SYSTEM_ONLINE",
        "language_label": "🌐 Language / اللغة",
        
        # Tabs
        "tab_single": "🚀 Single Video Production",
        "tab_batch": "📚 Batch Production (JSON / TXT)",
        "tab_assets": "🎥 Media & Assets Management",
        "tab_settings": "⚙️ AI & Telegram Settings",
        
        # Tab 1: Single Video
        "single_topic_label": "Target Video Topic / Prompt",
        "single_topic_placeholder": "Enter topic here... e.g.: Top 5 Mind-Blowing Facts About The Cosmos",
        "single_start_btn": "🚀 Launch Immediate Production",
        "single_initial_step": "System Ready",
        "single_initial_topic": "Awaiting topic input...",
        
        # Tab 2: Batch Production
        "batch_file_label": "Topics Queue File (.json or .txt)",
        "batch_start_btn": "🚀 Process Entire Queue",
        "resume_alert_template": "⚠️ **Alert:** Unfinished queue found paused at video ({curr}/{total}). Would you like to resume?",
        "resume_btn": "🔄 Resume Previous Unfinished Queue",
        "batch_initial_step": "System Standby",
        "batch_initial_topic": "Awaiting file upload...",
        "batch_empty_file_err": "❌ No file uploaded.",
        "batch_parse_err": "❌ Unexpected error while reading topics file: {err}",
        "batch_no_topics_err": "❌ Unable to extract valid topics from file. Please provide a JSON or TXT file.",
        "batch_no_work_left": "No pending tasks to resume.",
        "batch_completed_all": "🎉 Successfully generated all queue videos ({total} videos)!",
        "batch_all_finished_title": "All Videos Completed",
        "batch_all_finished_topic": "Queue Finished",
        
        # Tab 3: Assets Management
        "section_hook_gameplay": "🎮 Gameplay, Hook Videos & Hook Audio",
        "gameplay_label": "🎮 Gameplay Background Video",
        "gameplay_placeholder": "Path to MP4 gameplay file",
        "hook_dir_label": "🎯 Hook Video Folder (Hook Clips)",
        "hook_dir_placeholder": "Path to hook directory",
        "hook_audio_label": "🔊 Hook Transition Audio (1.7x)",
        "hook_audio_placeholder": "Path to hook sound effect",
        "upload_btn_label": "Upload",
        "section_music_outro": "🎵 Background Music & Outro Clip",
        "bg_music_label": "🎵 Background Music (BGM)",
        "bg_music_placeholder": "Path to background music file",
        "outro_label": "🎬 Outro Clip (Final CTA)",
        "outro_placeholder": "Path to outro video file",
        "save_assets_btn": "💾 Save & Apply Asset Paths",
        
        # Tab 4: AI & Telegram Settings
        "section_ai_voice": "🤖 AI Engine & Neural Voiceover",
        "api_url_label": "AI API Endpoint (Chat Completions URL)",
        "api_key_label": "AI API Key",
        "voice_label": "🎙️ Neural Narrator Voice",
        "section_telegram": "✈️ Telegram Auto-Publisher",
        "tg_checkbox_label": "Automatically publish videos to Telegram channel (Default)",
        "tg_checkbox_info": "Uncheck to save videos locally on disk without uploading.",
        "bot_token_label": "Telegram Bot Token",
        "channel_id_label": "Target Channel ID / Username",
        "save_settings_btn": "💾 Save & Apply Core Settings",
        
        # Save & Validation Feedback
        "save_success": "✅ Settings saved and applied successfully!",
        "save_error": "❌ Error saving settings: {err}",
        "config_err_header": "⛔ Configuration Error:\n",
        "config_err_api": "API URL is invalid.",
        "config_err_bot": "Telegram Bot Token is invalid.",
        "config_err_channel": "Telegram Channel ID is invalid.",
        "config_err_gameplay": "Gameplay file not found: {path}",
        "config_err_hook": "Hook folder not found: {path}",
        "config_err_bg": "Background music file not found: {path}",
        "config_err_outro": "Outro file not found: {path}",
        "config_err_step": "Configuration Error",
        "empty_topic_err": "❌ Please enter a valid topic first!",
        "empty_topic_title": "Empty Topic",
        
        # Cyber Synthesizer Deck (Live Dashboard)
        "batch_progress_title": "Overall Batch Queue Progress:",
        "completed_label": "Completed",
        "current_label": "Current",
        "remaining_label": "Remaining",
        "avg_time_label": "Avg Time per clip:",
        "sec_unit": "seconds",
        "calc_in_progress": "Calculating...",
        "videos_unit": "clips",
        "current_process": "CURRENT_PROCESS",
        "active_worker": "ACTIVE_WORKER",
        "status_token_label": "STATUS",
        "sys_ready_log": "Core Synthesizer initialized. HTTP/7860",
        "pipeline_active_log": "Modules: Script, TTS, Whisper, Compositor ACTIVE",
        "standby_log": "> Awaiting process initiation...",
        
        # Generation Pipeline Steps
        "step_init": "Initializing environment and pipeline...",
        "step_1": "Step 1: AI Script Generation...",
        "step_2": "Step 2: Neural Voice Synthesis (GuyNeural)...",
        "step_3": "Step 3: Precise Timestamps (Faster-Whisper)...",
        "step_4": "Step 4: Storyboard & Scene Timing Alignment...",
        "step_5": "Step 5: Parallel Media Scraping & Validation...",
        "step_6": "Step 6: Video Compositing, FX & Rendering...",
        "step_7": "Step 7: Automated Upload to Telegram...",
        "step_done": "Video generated successfully!",
        "step_success_final": "Completed successfully!",
        "step_exec_error": "Execution Error (Code {code})",
        "step_unexpected_error": "An unexpected error occurred"
    },
    
    "ar": {
        # App Header & Meta
        "page_title": "🎬 صانع الفيديوهات الآلي - v4",
        "hero_title": "صانع الفيديوهات الآلي الاحترافي (v4.0)",
        "hero_badge": "CYBER WORKBENCH",
        "hero_subtitle": "الإنتاج الفائق بالذكاء الاصطناعي مع تحكم متكامل ومتابعة حية بدون أي سكرول",
        "system_online": "SYSTEM_ONLINE",
        "language_label": "🌐 اللغة / Language",
        
        # Tabs
        "tab_single": "🚀 إنتاج فيديو مفرد",
        "tab_batch": "📚 إنتاج بالجملة (JSON / TXT)",
        "tab_assets": "🎥 وسائط ومقاطع المونتاج",
        "tab_settings": "⚙️ الإعدادات الأساسية وتيليجرام",
        
        # Tab 1: Single Video
        "single_topic_label": "موضوع الفيديو المطلوب إنتاجه",
        "single_topic_placeholder": "اكتب الموضوع هنا... مثال: أغرب 5 حقائق علمية عن الكون لم تكن تعرفها",
        "single_start_btn": "🚀 بدء الإنتاج الفوري",
        "single_initial_step": "جاهز للبدء",
        "single_initial_topic": "بانتظار إدخال الموضوع...",
        
        # Tab 2: Batch Production
        "batch_file_label": "ملف قائمة المواضيع (JSON أو TXT)",
        "batch_start_btn": "🚀 إنتاج القائمة كاملة",
        "resume_alert_template": "⚠️ **تنبيه:** توجد قائمة سابقة غير مكتملة متوقفة عند الفيديو ({curr}/{total}). هل تريد الاستكمال؟",
        "resume_btn": "🔄 استكمال العمل السابق غير المكتمل",
        "batch_initial_step": "جاهز للبدء",
        "batch_initial_topic": "بانتظار تحميل القائمة...",
        "batch_empty_file_err": "❌ لم يتم رفع أي ملف.",
        "batch_parse_err": "❌ خطأ غير متوقع أثناء معالجة الملف: {err}",
        "batch_no_topics_err": "❌ تعذر استخراج أي مواضيع صالحة من الملف. يرجى التأكد من رفع ملف JSON أو ملف نصي TXT يحتوي على المواضيع.",
        "batch_no_work_left": "لا يوجد عمل غير مكتمل لاستئنافه.",
        "batch_completed_all": "🎉 تم الانتهاء بنجاح من كافة فيديوهات القائمة ({total} فيديو)!",
        "batch_all_finished_title": "اكتملت جميع الفيديوهات",
        "batch_all_finished_topic": "جميع الفيديوهات مكتملة",
        
        # Tab 3: Assets Management
        "section_hook_gameplay": "🎮 الجيم بلاي وفيديوهات الهوك وصوت الهوك",
        "gameplay_label": "🎮 فيديو الجيم بلاي (الخلفية)",
        "gameplay_placeholder": "مسار MP4",
        "hook_dir_label": "🎯 مجلد فيديوهات الهوك (Hook Folder)",
        "hook_dir_placeholder": "مسار المجلد",
        "hook_audio_label": "🔊 صوت نهاية الهوك (1.7x)",
        "hook_audio_placeholder": "مسار صوت الهوك",
        "upload_btn_label": "رفع",
        "section_music_outro": "🎵 الموسيقى التصويرية ومقطع الخاتمة",
        "bg_music_label": "🎵 موسيقى الخلفية (Background Music)",
        "bg_music_placeholder": "مسار ملف الموسيقى",
        "outro_label": "🎬 فيديو الخاتمة (Outro Clip)",
        "outro_placeholder": "مسار فيديو الخاتمة",
        "save_assets_btn": "💾 حفظ وتطبيق مسارات الوسائط",
        
        # Tab 4: AI & Telegram Settings
        "section_ai_voice": "🤖 إعدادات الذكاء الاصطناعي ومعلق الصوت",
        "api_url_label": "رابط الـ API (API Base URL)",
        "api_key_label": "مفتاح الـ API Key",
        "voice_label": "🎙️ صوت الراوي المعتمد بالذكاء الاصطناعي",
        "section_telegram": "✈️ إعدادات النشر على تيليجرام",
        "tg_checkbox_label": "نشر الفيديوهات تلقائياً إلى تيليجرام (مفعّل افتراضياً)",
        "tg_checkbox_info": "إلغاء التحديد يحفظ الفيديو في جهازك فقط دون رفعه للقناة.",
        "bot_token_label": "توكن بوت تيليجرام (Bot Token)",
        "channel_id_label": "مُعرّف القناة (Channel ID)",
        "save_settings_btn": "💾 حفظ وتطبيق كافة الإعدادات الأساسية",
        
        # Save & Validation Feedback
        "save_success": "✅ تم حفظ وتطبيق الإعدادات بنجاح!",
        "save_error": "❌ خطأ أثناء حفظ الإعدادات: {err}",
        "config_err_header": "⛔ خطأ في الإعدادات:\n",
        "config_err_api": "رابط الـ API غير صالح.",
        "config_err_bot": "توكن بوت تيليجرام غير صالح.",
        "config_err_channel": "معرف القناة غير صالح.",
        "config_err_gameplay": "ملف الجيم بلاي غير موجود: {path}",
        "config_err_hook": "مجلد الهوكات غير موجود: {path}",
        "config_err_bg": "ملف موسيقى الخلفية غير موجود: {path}",
        "config_err_outro": "ملف الخاتمة غير موجود: {path}",
        "config_err_step": "خطأ في الإعدادات",
        "empty_topic_err": "❌ يرجى إدخال موضوع صالح أولاً!",
        "empty_topic_title": "موضوع فارغ",
        
        # Cyber Synthesizer Deck (Live Dashboard)
        "batch_progress_title": "التقدم العام للقائمة كاملة:",
        "completed_label": "المكتمل",
        "current_label": "الجاري",
        "remaining_label": "المتبقي",
        "avg_time_label": "متوسط الوقت لكل مقطع:",
        "sec_unit": "ثانية",
        "calc_in_progress": "جاري الحساب...",
        "videos_unit": "فيديو",
        "current_process": "العملية الجارية",
        "active_worker": "المعالج النشط",
        "status_token_label": "الحالة",
        "sys_ready_log": "تم تهيئة النظام المركزي. HTTP/7860",
        "pipeline_active_log": "المكونات: السكربت، الصوت، Whisper، المونتاج نشطة",
        "standby_log": "> بانتظار بدء المعالجة...",
        
        # Generation Pipeline Steps
        "step_init": "بدء تشغيل بيئة المعالجة...",
        "step_1": "كتابة السكربت بالذكاء الاصطناعي...",
        "step_2": "توليد الصوت العصبي (GuyNeural)...",
        "step_3": "استخراج التوقيت الدقيق (Faster-Whisper)...",
        "step_4": "تخطيط توقيتات الصور ومشاهد القصة...",
        "step_5": "تحميل وتدقيق الصور بالتوازي...",
        "step_6": "المونتاج والرندر النهائي والمؤثرات...",
        "step_7": "النشر التلقائي إلى تيليجرام...",
        "step_done": "اكتمل إنتاج الفيديو بنجاح!",
        "step_success_final": "اكتمل بنجاح!",
        "step_exec_error": "خطأ في التنفيذ (كود {code})",
        "step_unexpected_error": "حدث خطأ غير متوقع"
    }
}

def t(key, lang=None, **kwargs):
    if not lang:
        lang = load_config().get("ui_language", "en")
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return trans.format(**kwargs)
        except Exception:
            return trans
    return trans

def get_current_lang():
    return load_config().get("ui_language", "en")

def save_language_preference(lang_code):
    cfg = load_config()
    cfg["ui_language"] = lang_code
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving language preference: {e}")
        return False

def load_config():
    default_config = {
        "ui_language": "en",
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
    curr_lang = get_current_lang()
    config = {
        "ui_language": curr_lang,
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
            json.dump(config, f, indent=4, ensure_ascii=False)
        return t("save_success", curr_lang)
    except Exception as e:
        return t("save_error", curr_lang, err=e)

def validate_config():
    config = load_config()
    lang = config.get("ui_language", "en")
    errors = []
    
    if not config.get("api_url") or "127.0.0.1" not in config.get("api_url") and not config.get("api_url").startswith("http"):
        errors.append(t("config_err_api", lang))
    if config.get("upload_to_telegram", True):
        if not config.get("bot_token") or ":" not in config.get("bot_token") or "YOUR_TELEGRAM" in config.get("bot_token"):
            errors.append(t("config_err_bot", lang))
        if not config.get("channel_id") or "YOUR_TELEGRAM" in config.get("channel_id"):
            errors.append(t("config_err_channel", lang))
            
    gp = config.get("gameplay_path", "")
    if gp and not os.path.exists(gp):
        errors.append(t("config_err_gameplay", lang, path=gp))
        
    hk = config.get("hook_dir", "")
    if hk and not os.path.exists(hk):
        errors.append(t("config_err_hook", lang, path=hk))
        
    bg = config.get("bg_music_path", "")
    if bg and not os.path.exists(bg):
        errors.append(t("config_err_bg", lang, path=bg))
        
    out = config.get("outro_path", "")
    if out and not os.path.exists(out):
        errors.append(t("config_err_outro", lang, path=out))
        
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
    curr_lang = get_current_lang()
    if state.get("in_progress") and state.get("queue"):
        total = len(state["queue"])
        curr = state.get("current_index", 0) + 1
        if curr <= total:
            return gr.update(visible=True, value=t("resume_alert_template", curr_lang, curr=curr, total=total))
    return gr.update(visible=False, value="")

# ==============================================================
# --- المكونات البصرية الحية (Live Cyber Dashboard Generator) ---
# ==============================================================

def render_dashboard_html(mode="single", percentage=0, step_title=None, topic="--", logs=None, batch_info=None, status_type="active", lang=None):
    """
    توليد واجهة المتابعة الحية بنظام Technical Synthesizer Deck:
    تصميم فاتح أنيق مع شاشتي هاكر داكنتين CRT (الدوامة والكونسول).
    """
    if logs is None:
        logs = []
    if not lang:
        lang = get_current_lang()
    if step_title is None:
        step_title = t("single_initial_step", lang) if mode == "single" else t("batch_initial_step", lang)
    
    # تحديد رموز الحالة التقنية (Status Token)
    substep_token = "WORKING"
    if status_type == "error":
        substep_token = "ERROR"
    elif percentage >= 100:
        substep_token = "COMPLETED"
    elif "[الخطوة 1]" in step_title or "السكربت" in step_title or "Script" in step_title:
        substep_token = "GENERATING_SCRIPT"
    elif "[الخطوة 2]" in step_title or "الصوت" in step_title or "Voice" in step_title:
        substep_token = "SYNTHESIZING_VOICE"
    elif "[الخطوة 3]" in step_title or "Whisper" in step_title:
        substep_token = "WHISPER_SYNCING"
    elif "[الخطوة 4]" in step_title or "تخطيط" in step_title or "Storyboard" in step_title:
        substep_token = "STORYBOARDING"
    elif "[الخطوة 5]" in step_title or "الصور" in step_title or "Media" in step_title:
        substep_token = "SCRAPING_MEDIA"
    elif "[الخطوة 6]" in step_title or "المونتاج" in step_title or "الرندر" in step_title or "Compositing" in step_title:
        substep_token = "COMPOSING"
    elif "[الخطوة 7]" in step_title or "تيليجرام" in step_title or "Telegram" in step_title:
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
        formatted_logs.append(f'<p><span class="text-emerald-500 font-bold">[SYSTEM_READY]</span> <span class="text-slate-400">{t("sys_ready_log", lang)}</span></p>')
        formatted_logs.append(f'<p><span class="text-cyan-400 font-bold">[PIPELINE]</span> <span class="text-slate-300">{t("pipeline_active_log", lang)}</span></p>')
        formatted_logs.append(f'<p><span class="text-yellow-400 font-bold">[STANDBY]</span> <span class="text-slate-300">> {t("standby_log", lang)}</span></p>')

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
    current_lang = lang if lang else get_current_lang()
    is_ar = (current_lang == "ar")
    deck_dir = "rtl" if is_ar else "ltr"
    progress_gradient = "linear-gradient(to left, #10b981, #0d9488)" if is_ar else "linear-gradient(to right, #10b981, #0d9488)"
    
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
            <div class="flex justify-between items-center text-xs batch-stats-row">
                <div class="flex items-center gap-2">
                    <span class="text-slate-800 font-bold">{t('batch_progress_title', current_lang)}</span>
                    <span class="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">{b_pct:.1f}%</span>
                </div>
                <div class="text-slate-600 font-mono text-xs flex items-center gap-3 batch-stats-badges flex-wrap">
                    <span>✅ {t('completed_label', current_lang)}: <strong class="text-emerald-700 font-bold text-sm">{b_comp}</strong> {t('videos_unit', current_lang)}</span>
                    <span>⚡ {t('current_label', current_lang)}: <strong class="text-amber-600 font-bold text-sm">#{b_curr}</strong></span>
                    <span>⏳ {t('remaining_label', current_lang)}: <strong class="text-slate-800 font-bold text-sm">{b_rem}</strong> {t('videos_unit', current_lang)}</span>
                    <span class="bg-slate-200/70 border border-slate-300 px-2.5 py-1 rounded-md text-slate-800 flex items-center gap-1 font-sans">
                        <span>⏱️ {t('avg_time_label', current_lang)}</span>
                        <strong class="text-emerald-700 font-mono font-bold text-sm">{b_avg}</strong>
                    </span>
                </div>
            </div>
            <div class="w-full bg-slate-200 h-3 rounded-full overflow-hidden p-0.5" style="height: 12px; background: #e2e8f0; border-radius: 9999px;">
                <div class="bg-gradient-to-l from-emerald-500 to-teal-600 h-full rounded-full transition-all duration-500 shadow-sm" style="width: {b_pct:.1f}%; height: 100%; border-radius: 9999px; background: {progress_gradient};"></div>
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
        spiral_top_tag = t("current_process", current_lang)
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
    <div class="cyber-deck-wrapper w-full select-none" dir="{deck_dir}">
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
    curr_lang = get_current_lang()
    config_errors = validate_config()
    if config_errors:
        err_msg = t("config_err_header", curr_lang) + "\n".join(config_errors)
        yield render_dashboard_html(mode="single", percentage=0, step_title=t("config_err_step", curr_lang), topic=topic, logs=[err_msg], status_type="error", lang=curr_lang)
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

def run_single_topic(topic):
    curr_lang = get_current_lang()
    config_errors = validate_config()
    if config_errors:
        err_msg = t("config_err_header", curr_lang) + "\n".join(config_errors)
        yield render_dashboard_html(mode="single", percentage=0, step_title=t("config_err_step", curr_lang), topic=topic, logs=[err_msg], status_type="error")
        return
        
    for progress_data in execute_topic_stream(topic, 1, 1, mode="single"):
        yield render_dashboard_html(**progress_data)

def run_batch_topics(file_obj):
    curr_lang = get_current_lang()
    if not file_obj:
        yield render_dashboard_html(mode="batch", percentage=0, step_title=t("batch_empty_file_err", curr_lang), topic="--", logs=[t("batch_empty_file_err", curr_lang)], status_type="error")
        return
        
    config_errors = validate_config()
    if config_errors:
        err_msg = t("config_err_header", curr_lang) + "\n".join(config_errors)
        yield render_dashboard_html(mode="batch", percentage=0, step_title=t("config_err_step", curr_lang), topic="--", logs=[err_msg], status_type="error")
        return
        
    try:
        topics = extract_topics_from_file(file_obj)
    except Exception as e:
        yield render_dashboard_html(mode="batch", percentage=0, step_title=t("config_err_step", curr_lang), topic="--", logs=[t("batch_parse_err", curr_lang, err=e)], status_type="error")
        return
        
    if not topics:
        yield render_dashboard_html(mode="batch", percentage=0, step_title=t("batch_no_topics_err", curr_lang), topic="--", logs=[t("batch_no_topics_err", curr_lang)], status_type="error")
        return

    state = {"queue": topics, "current_index": 0, "in_progress": True, "completed_times": []}
    save_state(state)
    
    yield from process_queue_stream()

def resume_batch():
    curr_lang = get_current_lang()
    config_errors = validate_config()
    if config_errors:
        yield render_dashboard_html(mode="batch", percentage=0, step_title=t("config_err_step", curr_lang), topic="--", logs=[t("config_err_header", curr_lang) + "\n".join(config_errors)], status_type="error")
        return
        
    state = load_state()
    if not state.get("in_progress") or state.get("current_index", 0) >= len(state.get("queue", [])):
        yield render_dashboard_html(mode="batch", percentage=100, step_title=t("batch_no_work_left", curr_lang), topic="--", logs=[t("batch_no_work_left", curr_lang)])
        return
        
    yield from process_queue_stream()

def process_queue_stream():
    curr_lang = get_current_lang()
    state = load_state()
    queue = state.get("queue", [])
    start_index = state.get("current_index", 0)
    completed_times = state.get("completed_times", [])
    total = len(queue)
    sec_label = t("sec_unit", curr_lang)
    
    for i in range(start_index, total):
        topic = queue[i]
        state["current_index"] = i
        save_state(state)
        
        # حساب متوسط الوقت الحقيقي بدقة تامة
        if completed_times:
            avg_sec = sum(completed_times) / len(completed_times)
            avg_str = f"~{avg_sec:.1f} {sec_label}"
        else:
            avg_str = t("calc_in_progress", curr_lang)

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
    final_avg = f"~{sum(completed_times) / len(completed_times):.1f} {sec_label}" if completed_times else "--"
    final_batch_meta = {
        "pct": 100.0,
        "completed": total,
        "current": total,
        "remaining": 0,
        "avg_sec": final_avg
    }
    yield render_dashboard_html(mode="batch", percentage=100, step_title=t("batch_all_finished_title", curr_lang), topic=t("batch_all_finished_topic", curr_lang), logs=[t("batch_completed_all", curr_lang, total=total)], batch_info=final_batch_meta)

def execute_topic_stream(topic, current_num, total_num, mode="single", batch_info=None):
    curr_lang = get_current_lang()
    if not topic.strip():
        yield {
            "mode": mode,
            "percentage": 0,
            "step_title": t("empty_topic_title", curr_lang),
            "topic": topic,
            "logs": [t("empty_topic_err", curr_lang)],
            "batch_info": batch_info,
            "status_type": "error"
        }
        return

    log_buffer = deque(maxlen=80)
    current_pct = 5
    current_step = t("step_init", curr_lang)
    
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

            # تصنيف المراحل والنسبة بدقة من مخرجات video_maker الحقيقية مع الترجمة
            if "[الخطوة 1]" in line_str:
                current_pct = 15
                current_step = t("step_1", curr_lang)
            elif "[الخطوة 2]" in line_str:
                current_pct = 30
                current_step = t("step_2", curr_lang)
            elif "[الخطوة 3]" in line_str:
                current_pct = 48
                current_step = t("step_3", curr_lang)
            elif "[الخطوة 4]" in line_str:
                current_pct = 62
                current_step = t("step_4", curr_lang)
            elif "[الخطوة 5]" in line_str:
                current_pct = 75
                current_step = t("step_5", curr_lang)
            elif "[الخطوة 6]" in line_str:
                current_pct = 88
                current_step = t("step_6", curr_lang)
            elif "[الخطوة 7]" in line_str:
                current_pct = 95
                current_step = t("step_7", curr_lang)
            elif "🎉 تم إنتاج الفيديو" in line_str:
                current_pct = 100
                current_step = t("step_done", curr_lang)

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
            current_step = t("step_success_final", curr_lang)
            status_t = "active"
            if mode == "batch":
                log_buffer.append(f"BATCH_SUCCESS [{current_num}/{total_num}] '{topic}' exported cleanly")
            else:
                log_buffer.append("SUCCESS: Video render and pipeline completed cleanly.")
        else:
            status_t = "error"
            current_step = t("step_exec_error", curr_lang, code=process.returncode)
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
            "step_title": t("step_unexpected_error", curr_lang),
            "topic": topic,
            "logs": list(log_buffer),
            "batch_info": batch_info,
            "status_type": "error"
        }

# ==============================================================
# --- تنسيقات CSS العامة (Technical Synthesizer Deck) ---
# ==============================================================

def build_app_css(lang="en"):
    is_ar = (lang == "ar")
    page_dir = "rtl" if is_ar else "ltr"
    page_align = "right" if is_ar else "left"
    border_hero = "border-right: 4px solid #059669;" if is_ar else "border-left: 4px solid #059669;"
    font_family = "'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, 'Consolas', monospace"

    return rf"""
html, body {{ 
    min-height: 100vh;
    margin: 0;
    padding: 0;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    direction: {page_dir}; 
    text-align: {page_align}; 
    font-family: {font_family};
    background-color: #f1f5f9;
    color: #0f172a;
    box-sizing: border-box;
}}
*, *:before, *:after {{
    box-sizing: border-box;
}}
.gradio-container {{ 
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
    direction: {page_dir};
    text-align: {page_align};
}}

[dir="rtl"], [dir="rtl"] .gradio-container {{
    direction: rtl !important;
    text-align: right !important;
}}
[dir="ltr"], [dir="ltr"] .gradio-container {{
    direction: ltr !important;
    text-align: left !important;
}}
[dir="rtl"] .hero-header {{
    border-right: 4px solid #059669 !important;
    border-left: 1px solid #cbd5e1 !important;
}}
[dir="ltr"] .hero-header {{
    border-left: 4px solid #059669 !important;
    border-right: 1px solid #cbd5e1 !important;
}}

.hero-header {{ 
    background: #ffffff !important; 
    border: 1px solid #cbd5e1 !important;
    {border_hero}
    padding: 8px 14px !important; 
    border-radius: 10px !important; 
    margin-bottom: 8px !important; 
    display: flex !important; 
    flex-direction: row !important;
    justify-content: space-between !important; 
    align-items: center !important; 
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important; 
    flex-shrink: 0 !important;
    gap: 12px !important;
    box-sizing: border-box !important;
    width: 100% !important;
}}
.hero-info-col {{
    flex: 1 1 auto !important;
    min-width: 240px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}}
.hero-controls-col {{
    flex: 0 0 auto !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
}}
.hero-controls-inner {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 10px !important;
    padding: 0 !important;
    margin: 0 !important;
}}
.cyber-status-badge {{
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    padding: 4px 10px !important;
    border-radius: 9999px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
    color: #38bdf8 !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.5), 0 0 8px rgba(56, 189, 248, 0.15) !important;
    white-space: nowrap !important;
    user-select: none !important;
    height: 32px !important;
    box-sizing: border-box !important;
}}
.cyber-status-badge .status-dot {{
    width: 7px !important;
    height: 7px !important;
    border-radius: 50% !important;
    background: #10b981 !important;
    display: inline-block !important;
    box-shadow: 0 0 6px #10b981 !important;
    animation: status-pulse 2s infinite !important;
}}
@keyframes status-pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.85); }}
}}

/* ============================================================== */
/* --- Cyber Language Segmented Toggle Pill [ EN | AR ] --- */
/* ============================================================== */
.lang-pill-switch {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    min-height: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
    display: inline-flex !important;
    align-items: center !important;
}}
.lang-pill-switch > label,
.lang-pill-switch > span:first-child:not(label span) {{
    display: none !important;
}}
.lang-pill-switch fieldset,
.lang-pill-switch .wrap,
.lang-pill-switch [data-testid="radio-group"],
.lang-pill-switch .gr-form,
.lang-pill-switch > div {{
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 9999px !important;
    padding: 2.5px 3px !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 2px !important;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.6), 0 0 10px rgba(16, 185, 129, 0.12) !important;
    margin: 0 !important;
    width: auto !important;
    min-width: 0 !important;
    height: 32px !important;
    box-sizing: border-box !important;
}}
.lang-pill-switch label {{
    margin: 0 !important;
    padding: 3px 13px !important;
    border-radius: 9999px !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    font-family: inherit !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    user-select: none !important;
    white-space: nowrap !important;
    line-height: 1.3 !important;
    box-shadow: none !important;
    height: 25px !important;
    box-sizing: border-box !important;
}}
.lang-pill-switch label:hover {{
    color: #f8fafc !important;
    background: rgba(255, 255, 255, 0.08) !important;
}}
.lang-pill-switch label:has(input:checked),
.lang-pill-switch label.selected,
.lang-pill-switch label[data-selected="true"] {{
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
}}
.lang-pill-switch input[type="radio"] {{
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
    margin: 0 !important;
}}
.lang-pill-switch label span {{
    font-size: 11.5px !important;
    letter-spacing: 0.02em !important;
    font-weight: 700 !important;
    color: inherit !important;
}}

.panel-card {{ 
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 8px; 
    padding: 8px 12px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
    box-sizing: border-box;
}}
.panel-title {{ 
    font-size: 13px !important; 
    font-weight: 700 !important; 
    color: #0f172a !important; 
    margin: 0 0 6px 0 !important; 
    border-bottom: 1.5px solid #f1f5f9; 
    padding-bottom: 3px; 
}}
.compact-field {{
    margin-bottom: 4px !important;
}}
.compact-field label span {{
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-bottom: 1px !important;
}}
.compact-field input, .compact-field textarea, .compact-field select {{
    padding: 3px 8px !important;
    font-size: 12px !important;
    height: 32px !important;
    min-height: 32px !important;
    border-radius: 6px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #f8fafc !important;
    box-sizing: border-box !important;
}}
.compact-file-upload {{ 
    min-height: 32px !important; 
    height: 32px !important; 
    padding: 0 !important; 
    margin: 0 !important;
    box-sizing: border-box !important;
}}
.compact-file-upload .upload-button, 
.compact-file-upload .wrap {{ 
    min-height: 30px !important; 
    height: 30px !important; 
    padding: 2px 8px !important; 
    font-size: 11px !important; 
    box-sizing: border-box !important;
}}
.btn-primary-action {{ 
    height: 36px !important; 
    min-height: 36px !important; 
    font-weight: 700 !important; 
    font-size: 13px !important; 
    border-radius: 6px !important;
    background-color: #059669 !important;
    border: 1px solid #047857 !important;
    color: #ffffff !important;
    cursor: pointer !important;
}}
.btn-primary-action:hover {{
    background-color: #047857 !important;
}}
.tabs {{
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: visible !important;
}}
.tab-nav {{ 
    margin-bottom: 6px !important; 
    border-bottom: 2px solid #e2e8f0 !important;
    flex-shrink: 0;
}}
.tab-nav > button {{ 
    font-size: 13px !important; 
    font-weight: 600 !important; 
    padding: 5px 14px !important; 
    color: #64748b !important;
}}
.tab-nav > button.selected {{ 
    color: #059669 !important;
    border-bottom-color: #059669 !important;
}}
.tabitem {{
    flex: 1 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 2px 0 !important;
}}

/* ============================================================== */
/* --- لوحة القيادة الحية وشاشات CRT الهاكر الداكنة --- */
/* ============================================================== */

.cyber-deck-wrapper {{
    width: 100% !important;
    margin-top: 6px !important;
    box-sizing: border-box !important;
}}
.cyber-deck-grid {{
    display: flex !important;
    flex-direction: row !important;
    gap: 12px !important;
    align-items: stretch !important;
    width: 100% !important;
    box-sizing: border-box !important;
}}
.cyber-spiral-panel {{
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
}}
.cyber-terminal-panel {{
    flex: 1 1 0 !important;
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
}}

/* الشاشتان الداكنتان (Hardware CRT Chassis) */
.cyber-chassis {{
    background: #030712 !important;
    border: 1px solid #1e293b !important;
    border-top: 1px solid #334155 !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.9), 0 4px 12px -2px rgba(15, 23, 42, 0.12), 0 0 15px -3px rgba(34, 197, 94, 0.12) !important;
}}

@keyframes square-spiral {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}
.spiral-stage {{
    width: 90px !important;
    height: 90px !important;
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 6px auto !important;
}}
.spiral-box {{
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
}}
.spiral-box-inner {{
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
}}
.spiral-center-badge {{
    position: relative !important;
    z-index: 10 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    pointer-events: none !important;
}}

.hacker-screen {{
    font-family: 'Consolas', 'Courier New', monospace !important;
    color: #22c55e !important;
    text-shadow: 0 0 4px rgba(34, 197, 94, 0.4);
    direction: ltr !important;
    text-align: left !important;
    unicode-bidi: isolate !important;
}}
.hacker-terminal-logs {{
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
}}
.hacker-terminal-logs p {{
    margin: 1.5px 0 !important;
    padding: 0 !important;
    line-height: 1.5 !important;
    white-space: pre-wrap !important;
    word-break: break-all !important;
    font-family: 'Consolas', 'Courier New', monospace !important;
}}
.hacker-cursor {{
    display: inline-block;
    width: 7px;
    height: 13px;
    background-color: #22c55e;
    vertical-align: middle;
    animation: blink 1s step-start infinite;
    box-shadow: 0 0 6px #22c55e;
}}
@keyframes blink {{
    50% {{ opacity: 0; }}
}}
.hacker-scroll::-webkit-scrollbar {{
    width: 5px;
}}
.hacker-scroll::-webkit-scrollbar-track {{
    background: #030712;
}}
.hacker-scroll::-webkit-scrollbar-thumb {{
    background: #15803d;
    border-radius: 3px;
}}

/* ============================================================== */
/* --- 100% Fully Responsive Layout & Media Queries --- */
/* ============================================================== */

@media screen and (max-width: 900px) {{
    .cyber-deck-grid {{
        display: flex !important;
        flex-direction: column !important;
        grid-template-columns: none !important;
        gap: 12px !important;
    }}
    .cyber-spiral-panel,
    .cyber-terminal-panel {{
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        grid-column: auto !important;
        padding: 10px !important;
    }}
    .cyber-spiral-panel .truncate {{
        max-width: 90% !important;
    }}
    .hero-header {{
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 8px !important;
        padding: 10px 12px !important;
    }}
    .hero-controls-inner {{
        justify-content: space-between !important;
        width: 100% !important;
        margin-top: 4px !important;
    }}
    .panel-columns-row {{
        flex-direction: column !important;
        gap: 10px !important;
    }}
    .panel-columns-row > div {{
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }}
}}

@media screen and (max-width: 680px) {{
    .action-input-row, .asset-upload-row {{
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 6px !important;
    }}
    .action-input-row > *, .asset-upload-row > * {{
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }}
    .cyber-batch-card .batch-stats-row {{
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 6px !important;
    }}
}}

@media screen and (max-width: 480px) {{
    .gradio-container {{
        width: 100% !important;
        padding: 4px 4px 16px 4px !important;
    }}
    .hero-header {{
        padding: 8px 10px !important;
    }}
    .hero-header h1 {{
        font-size: 13px !important;
    }}
    .hero-controls-inner {{
        flex-wrap: wrap !important;
        gap: 6px !important;
    }}
    .lang-pill-switch label {{
        padding: 3px 9px !important;
        font-size: 10.5px !important;
    }}
    .cyber-status-badge {{
        font-size: 10px !important;
        padding: 4px 8px !important;
    }}
    .hacker-terminal-logs {{
        height: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        font-size: 10.5px !important;
    }}
    .tab-nav > button {{
        padding: 4px 8px !important;
        font-size: 11px !important;
    }}
}}

/* ============================================================== */
/* --- Pure CSS Tailwind Equivalents for Gradio Compatibility --- */
/* ============================================================== */
.grid {{ display: grid !important; }}
.grid-cols-12 {{ grid-template-columns: repeat(12, minmax(0, 1fr)) !important; }}
.col-span-3 {{ grid-column: span 3 / span 3 !important; }}
.col-span-9 {{ grid-column: span 9 / span 9 !important; }}
.gap-1 {{ gap: 4px !important; }}
.gap-1\.5 {{ gap: 6px !important; }}
.gap-2 {{ gap: 8px !important; }}
.gap-3 {{ gap: 12px !important; }}
.gap-4 {{ gap: 16px !important; }}

.flex {{ display: flex !important; }}
.flex-col {{ flex-direction: column !important; }}
.flex-wrap {{ flex-wrap: wrap !important; }}
.items-center {{ align-items: center !important; }}
.justify-center {{ justify-content: center !important; }}
.justify-between {{ justify-content: space-between !important; }}

.w-full {{ width: 100% !important; }}
.w-2 {{ width: 8px !important; }}
.h-2 {{ height: 8px !important; }}
.w-14 {{ width: 56px !important; }}
.h-14 {{ height: 56px !important; }}
.w-20 {{ width: 80px !important; }}
.h-20 {{ height: 80px !important; }}
.w-24 {{ width: 96px !important; }}
.h-24 {{ height: 96px !important; }}
.h-full {{ height: 100% !important; }}
.h-3 {{ height: 12px !important; }}

.relative {{ position: relative !important; }}
.absolute {{ position: absolute !important; }}
.z-10 {{ z-index: 10 !important; }}

.p-0\.5 {{ padding: 2px !important; }}
.p-3\.5 {{ padding: 14px !important; }}
.p-4 {{ padding: 16px !important; }}
.px-2 {{ padding-left: 8px !important; padding-right: 8px !important; }}
.px-2\.5 {{ padding-left: 10px !important; padding-right: 10px !important; }}
.py-0\.5 {{ padding-top: 2px !important; padding-bottom: 2px !important; }}
.py-1 {{ padding-top: 4px !important; padding-bottom: 4px !important; }}
.pb-1 {{ padding-bottom: 4px !important; }}
.pb-2 {{ padding-bottom: 8px !important; }}
.pt-2 {{ padding-top: 8px !important; }}
.mb-1 {{ margin-bottom: 4px !important; }}
.mb-3 {{ margin-bottom: 12px !important; }}
.mt-0\.5 {{ margin-top: 2px !important; }}
.mt-1 {{ margin-top: 4px !important; }}
.my-2 {{ margin-top: 8px !important; margin-bottom: 8px !important; }}

.space-y-2 > * + * {{ margin-top: 8px !important; }}

.rounded {{ border-radius: 4px !important; }}
.rounded-md {{ border-radius: 6px !important; }}
.rounded-xl {{ border-radius: 12px !important; }}
.rounded-full {{ border-radius: 9999px !important; }}

.border {{ border-width: 1px !important; border-style: solid !important; }}
.border-b {{ border-bottom-width: 1px !important; border-bottom-style: solid !important; }}
.border-t {{ border-top-width: 1px !important; border-top-style: solid !important; }}
.border-slate-200 {{ border-color: #e2e8f0 !important; }}
.border-slate-300 {{ border-color: #cbd5e1 !important; }}
.border-slate-800 {{ border-color: #1e293b !important; }}
.border-slate-900 {{ border-color: #0f172a !important; }}
.border-emerald-200 {{ border-color: #a7f3d0 !important; }}

.bg-slate-50 {{ background-color: #f8fafc !important; }}
.bg-slate-200 {{ background-color: #e2e8f0 !important; }}
.bg-emerald-100 {{ background-color: #d1fae5 !important; }}
.bg-emerald-500 {{ background-color: #10b981 !important; }}

.text-emerald-200 {{ color: #a7f3d0 !important; }}
.text-emerald-300 {{ color: #6ee7b7 !important; }}
.text-emerald-400 {{ color: #34d399 !important; }}
.text-emerald-500 {{ color: #10b981 !important; }}
.text-emerald-600 {{ color: #059669 !important; }}
.text-emerald-700 {{ color: #047857 !important; }}
.text-yellow-300 {{ color: #fde047 !important; }}
.text-yellow-400 {{ color: #facc15 !important; }}
.text-amber-600 {{ color: #d97706 !important; }}
.text-cyan-300 {{ color: #67e8f9 !important; }}
.text-cyan-400 {{ color: #22d3ee !important; }}
.text-purple-300 {{ color: #d8b4fe !important; }}
.text-purple-400 {{ color: #c084fc !important; }}
.text-rose-300 {{ color: #fda4af !important; }}
.text-rose-400 {{ color: #fb7185 !important; }}
.text-slate-300 {{ color: #cbd5e1 !important; }}
.text-slate-400 {{ color: #94a3b8 !important; }}
.text-slate-500 {{ color: #64748b !important; }}
.text-slate-600 {{ color: #475569 !important; }}
.text-slate-800 {{ color: #1e293b !important; }}

.font-mono {{ font-family: 'Consolas', 'Courier New', monospace !important; }}
.font-sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }}
.font-bold {{ font-weight: 700 !important; }}
.font-black {{ font-weight: 900 !important; }}

.text-xs {{ font-size: 12px !important; }}
.text-sm {{ font-size: 14px !important; }}
.text-lg {{ font-size: 18px !important; }}
.text-xl {{ font-size: 20px !important; }}
.text-\[10px\] {{ font-size: 10px !important; }}
.text-\[11px\] {{ font-size: 11px !important; }}

.tracking-widest {{ letter-spacing: 0.1em !important; }}
.truncate {{ overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }}
.max-w-\[190px\] {{ max-width: 190px !important; }}
.select-none {{ user-select: none !important; }}
.overflow-hidden {{ overflow: hidden !important; }}

.bg-gradient-to-l {{ background-image: linear-gradient(to left, var(--tw-gradient-stops, #10b981, #0d9488)) !important; }}
.from-emerald-500 {{ --tw-gradient-from: #10b981; }}
.to-teal-600 {{ --tw-gradient-to: #0d9488; }}

@keyframes ping {{
    75%, 100% {{
        transform: scale(2);
        opacity: 0;
    }}
}}
.animate-ping {{
    animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite !important;
}}
@keyframes pulse {{
    50% {{ opacity: .5; }}
}}
.animate-pulse {{
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite !important;
}}
"""

active_lang = get_current_lang()
css = build_app_css(active_lang)

with gr.Blocks(title=t("page_title", active_lang), theme=gr.themes.Default(primary_hue="emerald", spacing_size="sm", text_size="sm"), css=css) as demo:
    with gr.Row(elem_classes=["hero-header"]):
        with gr.Column(scale=8):
            header_html = gr.HTML(f"""
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">🎬</span>
                <h1>{t("hero_title", active_lang)}</h1>
                <span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; font-family: monospace;">
                    {t("hero_badge", active_lang)}
                </span>
            </div>
            <p>{t("hero_subtitle", active_lang)}</p>
            """)
        with gr.Column(scale=4):
            with gr.Row(elem_classes=["items-center", "hero-controls-inner"], equal_height=True):
                lang_selector = gr.Radio(
                    choices=[("English", "en"), ("العربية", "ar")],
                    value=active_lang,
                    show_label=False,
                    container=False,
                    elem_classes=["lang-pill-switch"]
                )
                system_badge_html = gr.HTML(f"""
                <div class="cyber-status-badge" style="display: flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #cbd5e1; padding: 5px 10px; border-radius: 6px; font-size: 11px; font-family: monospace; color: #0f172a; white-space: nowrap;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                    <span>{t("system_online", active_lang)}</span>
                </div>
                """)

    current_config = load_config()
    
    with gr.Tabs():
        # ==============================================================
        # --- تبويبة 1: صناعة فيديو مفرد (شاشة حية متقدمة) ---
        # ==============================================================
        with gr.TabItem(t("tab_single", active_lang)) as tab_single_item:
            with gr.Column(elem_classes=["panel-card"]):
                with gr.Row(equal_height=True, elem_classes=["action-input-row"]):
                    single_topic_input = gr.Textbox(
                        label=t("single_topic_label", active_lang),
                        placeholder=t("single_topic_placeholder", active_lang),
                        scale=5,
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    single_start_btn = gr.Button(t("single_start_btn", active_lang), variant="primary", scale=1, elem_classes=["btn-primary-action"])
            
            single_output_log = gr.HTML(
                value=render_dashboard_html(mode="single", percentage=0, step_title=t("single_initial_step", active_lang), topic=t("single_initial_topic", active_lang))
            )
            single_start_btn.click(fn=run_single_topic, inputs=single_topic_input, outputs=single_output_log)

        # ==============================================================
        # --- تبويبة 2: الإنتاج بالجملة (لوحة القيادة الحية) ---
        # ==============================================================
        with gr.TabItem(t("tab_batch", active_lang)) as tab_batch_item:
            with gr.Column(elem_classes=["panel-card"]):
                resume_alert = gr.Markdown(visible=False)
                resume_btn = gr.Button(t("resume_btn", active_lang), variant="stop", visible=False, elem_classes=["btn-primary-action"])
                
                with gr.Row(equal_height=True, elem_classes=["action-input-row"]):
                    json_file_input = gr.File(label=t("batch_file_label", active_lang), file_types=[".json", ".txt", "text"], scale=4, elem_classes=["compact-file-upload"])
                    batch_start_btn = gr.Button(t("batch_start_btn", active_lang), variant="primary", scale=1, elem_classes=["btn-primary-action"])
                
            batch_output_log = gr.HTML(
                value=render_dashboard_html(
                    mode="batch",
                    percentage=0,
                    step_title=t("batch_initial_step", active_lang),
                    topic=t("batch_initial_topic", active_lang),
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
        with gr.TabItem(t("tab_assets", active_lang)) as tab_assets_item:
            with gr.Row(elem_classes=["panel-columns-row"]):
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    section_hook_md = gr.Markdown(f"<div class='panel-title'>{t('section_hook_gameplay', active_lang)}</div>")
                    with gr.Row(equal_height=True, elem_classes=["asset-upload-row"]):
                        gameplay_path_input = gr.Textbox(
                            label=t("gameplay_label", active_lang),
                            value=current_config.get("gameplay_path", ""),
                            placeholder=t("gameplay_placeholder", active_lang),
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        gameplay_file_upload = gr.File(label=t("upload_btn_label", active_lang), file_types=[".mp4", ".mov", ".mkv"], scale=1, elem_classes=["compact-file-upload"])
                    
                    with gr.Row(equal_height=True, elem_classes=["asset-upload-row"]):
                        hook_dir_input = gr.Textbox(
                            label=t("hook_dir_label", active_lang),
                            value=current_config.get("hook_dir", ""),
                            placeholder=t("hook_dir_placeholder", active_lang),
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        hooks_folder_upload = gr.File(
                            label=t("upload_btn_label", active_lang),
                            file_count="multiple",
                            file_types=[".mp4", ".mov", ".mkv"],
                            scale=1,
                            elem_classes=["compact-file-upload"]
                        )
                    
                    with gr.Row(equal_height=True, elem_classes=["asset-upload-row"]):
                        hook_audio_input = gr.Textbox(
                            label=t("hook_audio_label", active_lang),
                            value=current_config.get("hook_audio_source", ""),
                            placeholder=t("hook_audio_placeholder", active_lang),
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        hook_audio_upload = gr.File(label=t("upload_btn_label", active_lang), file_types=[".mp4", ".mp3", ".wav", ".m4a"], scale=1, elem_classes=["compact-file-upload"])

                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    section_music_md = gr.Markdown(f"<div class='panel-title'>{t('section_music_outro', active_lang)}</div>")
                    with gr.Row(equal_height=True, elem_classes=["asset-upload-row"]):
                        bg_music_input = gr.Textbox(
                            label=t("bg_music_label", active_lang),
                            value=current_config.get("bg_music_path", ""),
                            placeholder=t("bg_music_placeholder", active_lang),
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        bg_music_upload = gr.File(label=t("upload_btn_label", active_lang), file_types=[".mp4", ".mp3", ".wav", ".m4a"], scale=1, elem_classes=["compact-file-upload"])

                    with gr.Row(equal_height=True, elem_classes=["asset-upload-row"]):
                        outro_path_input = gr.Textbox(
                            label=t("outro_label", active_lang),
                            value=current_config.get("outro_path", ""),
                            placeholder=t("outro_placeholder", active_lang),
                            scale=4,
                            lines=1,
                            elem_classes=["compact-field"]
                        )
                        outro_upload = gr.File(label=t("upload_btn_label", active_lang), file_types=[".mp4", ".mov", ".mkv"], scale=1, elem_classes=["compact-file-upload"])

                    with gr.Row():
                        save_assets_btn = gr.Button(t("save_assets_btn", active_lang), variant="primary", elem_classes=["btn-primary-action"])
                    save_assets_status = gr.Markdown("")

        # ==============================================================
        # --- تبويبة 4: إعدادات الذكاء الاصطناعي وتيليجرام ---
        # ==============================================================
        with gr.TabItem(t("tab_settings", active_lang)) as tab_settings_item:
            with gr.Row(elem_classes=["panel-columns-row"]):
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    section_ai_md = gr.Markdown(f"<div class='panel-title'>{t('section_ai_voice', active_lang)}</div>")
                    api_url_input = gr.Textbox(
                        label=t("api_url_label", active_lang),
                        value=current_config.get("api_url", ""),
                        placeholder="http://127.0.0.1:8008/v1/chat/completions",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    api_key_input = gr.Textbox(
                        label=t("api_key_label", active_lang),
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
                        label=t("voice_label", active_lang),
                        choices=voice_choices,
                        value=current_voice,
                        elem_classes=["compact-field"]
                    )

                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    section_tg_md = gr.Markdown(f"<div class='panel-title'>{t('section_telegram', active_lang)}</div>")
                    upload_telegram_checkbox = gr.Checkbox(
                        label=t("tg_checkbox_label", active_lang),
                        value=current_config.get("upload_to_telegram", True),
                        info=t("tg_checkbox_info", active_lang)
                    )
                    bot_token_input = gr.Textbox(
                        label=t("bot_token_label", active_lang),
                        value=current_config.get("bot_token", ""),
                        type="password",
                        placeholder="YOUR_TELEGRAM_BOT_TOKEN",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    channel_id_input = gr.Textbox(
                        label=t("channel_id_label", active_lang),
                        value=current_config.get("channel_id", ""),
                        placeholder="YOUR_TELEGRAM_CHANNEL_ID",
                        lines=1,
                        elem_classes=["compact-field"]
                    )

            with gr.Row():
                save_api_btn = gr.Button(t("save_settings_btn", active_lang), variant="primary", elem_classes=["btn-primary-action"])
            save_api_status = gr.Markdown("")

    # دالة الترجمة الفورية الحية لجميع عناصر الواجهة
    def switch_language_live(selected_lang):
        save_language_preference(selected_lang)
        
        new_header = f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">🎬</span>
            <h1>{t("hero_title", selected_lang)}</h1>
            <span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; font-family: monospace;">
                {t("hero_badge", selected_lang)}
            </span>
        </div>
        <p>{t("hero_subtitle", selected_lang)}</p>
        """
        
        new_badge = f"""
        <div class="cyber-status-badge" style="display: flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #cbd5e1; padding: 5px 10px; border-radius: 6px; font-size: 11px; font-family: monospace; color: #0f172a; white-space: nowrap;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
            <span>{t("system_online", selected_lang)}</span>
        </div>
        """
        
        return [
            header_html.update(value=new_header),
            system_badge_html.update(value=new_badge),
            tab_single_item.update(label=t("tab_single", selected_lang)),
            single_topic_input.update(label=t("single_topic_label", selected_lang), placeholder=t("single_topic_placeholder", selected_lang)),
            single_start_btn.update(value=t("single_start_btn", selected_lang)),
            single_output_log.update(value=render_dashboard_html(mode="single", percentage=0, step_title=t("single_initial_step", selected_lang), topic=t("single_initial_topic", selected_lang))),
            tab_batch_item.update(label=t("tab_batch", selected_lang)),
            resume_btn.update(value=t("resume_btn", selected_lang)),
            json_file_input.update(label=t("batch_file_label", selected_lang)),
            batch_start_btn.update(value=t("batch_start_btn", selected_lang)),
            batch_output_log.update(value=render_dashboard_html(mode="batch", percentage=0, step_title=t("batch_initial_step", selected_lang), topic=t("batch_initial_topic", selected_lang), batch_info={"pct": 0.0, "completed": 0, "current": 1, "remaining": 0, "avg_sec": "--"})),
            tab_assets_item.update(label=t("tab_assets", selected_lang)),
            section_hook_md.update(value=f"<div class='panel-title'>{t('section_hook_gameplay', selected_lang)}</div>"),
            gameplay_path_input.update(label=t("gameplay_label", selected_lang), placeholder=t("gameplay_placeholder", selected_lang)),
            gameplay_file_upload.update(label=t("upload_btn_label", selected_lang)),
            hook_dir_input.update(label=t("hook_dir_label", selected_lang), placeholder=t("hook_dir_placeholder", selected_lang)),
            hooks_folder_upload.update(label=t("upload_btn_label", selected_lang)),
            hook_audio_input.update(label=t("hook_audio_label", selected_lang), placeholder=t("hook_audio_placeholder", selected_lang)),
            hook_audio_upload.update(label=t("upload_btn_label", selected_lang)),
            section_music_md.update(value=f"<div class='panel-title'>{t('section_music_outro', selected_lang)}</div>"),
            bg_music_input.update(label=t("bg_music_label", selected_lang), placeholder=t("bg_music_placeholder", selected_lang)),
            bg_music_upload.update(label=t("upload_btn_label", selected_lang)),
            outro_path_input.update(label=t("outro_label", selected_lang), placeholder=t("outro_placeholder", selected_lang)),
            outro_upload.update(label=t("upload_btn_label", selected_lang)),
            save_assets_btn.update(value=t("save_assets_btn", selected_lang)),
            tab_settings_item.update(label=t("tab_settings", selected_lang)),
            section_ai_md.update(value=f"<div class='panel-title'>{t('section_ai_voice', selected_lang)}</div>"),
            api_url_input.update(label=t("api_url_label", selected_lang)),
            api_key_input.update(label=t("api_key_label", selected_lang)),
            voice_input.update(label=t("voice_label", selected_lang)),
            section_tg_md.update(value=f"<div class='panel-title'>{t('section_telegram', selected_lang)}</div>"),
            upload_telegram_checkbox.update(label=t("tg_checkbox_label", selected_lang), info=t("tg_checkbox_info", selected_lang)),
            bot_token_input.update(label=t("bot_token_label", selected_lang)),
            channel_id_input.update(label=t("channel_id_label", selected_lang)),
            save_api_btn.update(value=t("save_settings_btn", selected_lang))
        ]

    live_ui_outputs = [
        header_html, system_badge_html,
        tab_single_item, single_topic_input, single_start_btn, single_output_log,
        tab_batch_item, resume_btn, json_file_input, batch_start_btn, batch_output_log,
        tab_assets_item, section_hook_md, gameplay_path_input, gameplay_file_upload,
        hook_dir_input, hooks_folder_upload, hook_audio_input, hook_audio_upload,
        section_music_md, bg_music_input, bg_music_upload, outro_path_input, outro_upload, save_assets_btn,
        tab_settings_item, section_ai_md, api_url_input, api_key_input, voice_input,
        section_tg_md, upload_telegram_checkbox, bot_token_input, channel_id_input, save_api_btn
    ]

    # ربط التبديل الفوري مع ضبط اتجاه الصفحة ديناميكياً بدون ريلود
    lang_selector.change(
        fn=switch_language_live,
        inputs=lang_selector,
        outputs=live_ui_outputs,
        js="""(selected_lang) => {
            if (selected_lang === 'ar') {
                document.documentElement.dir = 'rtl';
                document.body.dir = 'rtl';
            } else {
                document.documentElement.dir = 'ltr';
                document.body.dir = 'ltr';
            }
        }"""
    )

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
