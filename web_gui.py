import gradio as gr
import subprocess
import os
import sys
import json
import time
import shutil

CONFIG_FILE = 'config.json'
STATE_FILE = 'state.json'

DEFAULT_ASSETS_DIR = r"C:\Users\User\OneDrive\Desktop\resilt"
DEFAULT_HOOKS_DIR = os.path.join(DEFAULT_ASSETS_DIR, "hook")

def load_config():
    default_config = {
        "api_url": "http://127.0.0.1:8008/v1/chat/completions",
        "api_key": "sk-chatgpt-local-secret-key",
        "bot_token": "8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ",
        "channel_id": "-1004247712091",
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

def validate_config():
    """التحقق من صحة واكتمال الإعدادات الأساسية لضمان عدم حدوث أخطاء أثناء الإنتاج"""
    cfg = load_config()
    errors = []
    
    if not cfg.get("api_url", "").strip():
        errors.append("رابط الـ API غير محدد (مطلوب لكتابة السكريبت واستخراج التوقيتات)")
    if not cfg.get("api_key", "").strip():
        errors.append("مفتاح الـ API Key فارغ")
        
    if cfg.get("upload_to_telegram", True):
        if not cfg.get("bot_token", "").strip():
            errors.append("توكن بوت تيليجرام غير محدد مع تفعيل خيار النشر")
        if not cfg.get("channel_id", "").strip():
            errors.append("مُعرّف القناة في تيليجرام غير محدد مع تفعيل خيار النشر")
            
    gp = cfg.get("gameplay_path", "").strip()
    if gp and not os.path.exists(gp):
        errors.append(f"ملف الجيم بلاي المحدد غير موجود: {gp}")
        
    hk = cfg.get("hook_dir", "").strip()
    if hk and not os.path.exists(hk):
        errors.append(f"مجلد الهوكات المحدد غير موجود: {hk}")
        
    return errors

def save_config(api_url, api_key, bot_token, channel_id, upload_to_telegram, voice,
                gameplay_path, hook_dir, hook_audio_source, bg_music_path, outro_path):
    config = {
        "api_url": (api_url or "").strip(),
        "api_key": (api_key or "").strip(),
        "bot_token": (bot_token or "").strip(),
        "channel_id": (channel_id or "").strip(),
        "upload_to_telegram": bool(upload_to_telegram),
        "voice": (voice or "").strip(),
        "gameplay_path": (gameplay_path or "").strip(),
        "hook_dir": (hook_dir or "").strip(),
        "hook_audio_source": (hook_audio_source or "").strip(),
        "bg_music_path": (bg_music_path or "").strip(),
        "outro_path": (outro_path or "").strip()
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return "✅ تم حفظ جميع الإعدادات والمسارات بنجاح!"
    except Exception as e:
        return f"❌ خطأ أثناء الحفظ: {e}"

def copy_uploaded_file(file_obj, subfolder=None):
    if file_obj is None:
        return None
    try:
        src_path = file_obj.name if hasattr(file_obj, 'name') else str(file_obj)
        if not os.path.exists(src_path):
            return None
        target_dir = os.path.join(DEFAULT_ASSETS_DIR, subfolder) if subfolder else DEFAULT_ASSETS_DIR
        os.makedirs(target_dir, exist_ok=True)
        filename = os.path.basename(src_path)
        dest_path = os.path.join(target_dir, filename)
        shutil.copy2(src_path, dest_path)
        return dest_path
    except Exception as e:
        print(f"Error copying file: {e}")
        return None

def on_upload_gameplay(file_obj):
    dest = copy_uploaded_file(file_obj)
    return dest if dest else gr.update()

def on_upload_hook_audio(file_obj):
    dest = copy_uploaded_file(file_obj)
    return dest if dest else gr.update()

def on_upload_bg_music(file_obj):
    dest = copy_uploaded_file(file_obj)
    return dest if dest else gr.update()

def on_upload_outro(file_obj):
    dest = copy_uploaded_file(file_obj)
    return dest if dest else gr.update()

def on_upload_hooks_folder(files):
    if not files:
        return gr.update(), "لم يتم اختيار ملفات."
    try:
        target_dir = DEFAULT_HOOKS_DIR
        os.makedirs(target_dir, exist_ok=True)
        count = 0
        file_list = files if isinstance(files, list) else [files]
        for f in file_list:
            src = f.name if hasattr(f, 'name') else str(f)
            if os.path.isfile(src):
                fname = os.path.basename(src)
                if fname.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi')):
                    shutil.copy2(src, os.path.join(target_dir, fname))
                    count += 1
        return target_dir, f"✅ تم حفظ {count} فيديو في مجلد الهوكات بنجاح!"
    except Exception as e:
        return gr.update(), f"❌ خطأ: {e}"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"queue": [], "current_index": 0, "in_progress": False}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

def check_resume_status():
    state = load_state()
    if state.get("in_progress") and state.get("current_index", 0) < len(state.get("queue", [])):
        total = len(state['queue'])
        current = state['current_index'] + 1
        return gr.update(visible=True, value=f"⚠️ يوجد عمل غير مكتمل! توقف البرنامج عند الفيديو ({current} من {total}). اضغط على 'استكمال العمل' للمتابعة.")
    return gr.update(visible=False)

def run_single_topic(topic):
    # فحص الإعدادات الإلزامية أولاً لمنع البدء بدونها
    config_errors = validate_config()
    if config_errors:
        err_msg = "⛔ [تنبيه أمان صارم]: لا يمكن إنشاء الفيديو قبل اكتمال الإعدادات الأساسية!\n" + "="*50 + "\n"
        for i, err in enumerate(config_errors, 1):
            err_msg += f"{i}. ❌ {err}\n"
        err_msg += "\n💡 يرجى الذهاب لتبويبة '⚙️ الإعدادات الأساسية وتيليجرام' وحفظ البيانات الصحيحة أولاً."
        yield err_msg
        return
        
    yield from execute_topic(topic, 1, 1)

def run_batch_topics(json_file):
    # فحص الإعدادات الإلزامية أولاً
    config_errors = validate_config()
    if config_errors:
        err_msg = "⛔ [تنبيه أمان صارم]: لا يمكن بدء الإنتاج بالجملة قبل اكتمال الإعدادات الأساسية!\n" + "="*50 + "\n"
        for i, err in enumerate(config_errors, 1):
            err_msg += f"{i}. ❌ {err}\n"
        err_msg += "\n💡 يرجى الذهاب لتبويبة '⚙️ الإعدادات الأساسية وتيليجرام' وحفظ البيانات أولاً."
        yield err_msg
        return
        
    if not json_file:
        yield "❌ يرجى رفع ملف JSON صالح!"
        return
        
    try:
        filepath = json_file.name if hasattr(json_file, 'name') else str(json_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, dict) and "topics" in data:
            topics = data["topics"]
        elif isinstance(data, list):
            topics = data
        else:
            yield "❌ صيغة الملف غير صحيحة. يجب أن يحتوي على مصفوفة من المواضيع."
            return
    except Exception as e:
        yield f"❌ خطأ في قراءة الملف: {e}"
        return
        
    if not topics:
        yield "❌ الملف فارغ ولا يحتوي على مواضيع."
        return

    state = {"queue": topics, "current_index": 0, "in_progress": True}
    save_state(state)
    
    yield from process_queue()

def resume_batch():
    config_errors = validate_config()
    if config_errors:
        yield "⛔ لا يمكن الاستئناف قبل تصحيح الإعدادات في تبويبة الإعدادات!"
        return
        
    state = load_state()
    if not state.get("in_progress") or state.get("current_index", 0) >= len(state.get("queue", [])):
        yield "لا يوجد عمل غير مكتمل لاستئنافه."
        return
        
    yield from process_queue()

def process_queue():
    state = load_state()
    queue = state.get("queue", [])
    start_index = state.get("current_index", 0)
    total = len(queue)
    
    overall_status = f"📚 جاري بدء إنتاج الجملة ({total} فيديوهات)\n" + "="*40 + "\n"
    yield overall_status
    
    for i in range(start_index, total):
        topic = queue[i]
        
        state["current_index"] = i
        save_state(state)
        
        for update in execute_topic(topic, i + 1, total, prefix=overall_status):
            yield update
            
        overall_status += f"✅ اكتمل الفيديو ({i + 1}/{total}): {topic}\n"
        yield overall_status
        
    state["in_progress"] = False
    save_state(state)
    yield overall_status + "\n🎉🎉 اكتملت جميع الفيديوهات في القائمة بنجاح! 🎉🎉"

def execute_topic(topic, current_num, total_num, prefix=""):
    if not topic.strip():
        yield prefix + "❌ يرجى إدخال موضوع صالح أولاً!"
        return
        
    start_time = time.time()
    header = f"🚀 [فيديو {current_num}/{total_num}] جاري العمل على: {topic}\n" + "-"*40 + "\n"
    status_text = prefix + header
    yield status_text
    
    try:
        process = subprocess.Popen(
            ['python', '-u', 'video_maker.py', '--topic', topic],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()
            
            line_stripped = line.strip()
            
            if "[الخطوة" in line_stripped or "✓" in line_stripped or "خطأ" in line_stripped or "الوصف الجاهز" in line_stripped or "تم النشر" in line_stripped or "--- السكريبت ---" in line_stripped or "الخاتمة" in line_stripped or "قص الصمت" in line_stripped or "✂️" in line_stripped or "🎵" in line_stripped or "🎮" in line_stripped or "🎯" in line_stripped or "معلومة" in line_stripped:
                status_text += f"🔹 {line_stripped}\n"
                yield status_text
            elif line_stripped.startswith("جاري البحث عن:") or "تنبيه" in line_stripped:
                status_text += f"   - {line_stripped}\n"
                yield status_text
                
        process.stdout.close()
        process.wait()
        
        elapsed = round(time.time() - start_time, 1)
        
        if process.returncode == 0:
            status_text += f"\n🎉 اكتملت المهمة! (استغرق {elapsed} ثانية)\n\n"
        else:
            status_text += f"\n❌ خطأ (كود {process.returncode}). (استغرق {elapsed} ثانية)\n\n"
            
        yield status_text
        
    except Exception as e:
        yield status_text + f"\n❌ حدث خطأ غير متوقع: {e}\n"

css = """
html, body { 
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden !important; /* منع سكرول المتصفح نهائياً */
    direction: rtl; 
    text-align: right; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #f1f5f9;
    color: #1e293b;
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
/* رأس الصفحة مدمج ونحيف جداً */
.hero-header { 
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%); 
    color: white; 
    padding: 6px 14px; 
    border-radius: 8px; 
    margin-bottom: 6px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.06); 
    flex-shrink: 0;
}
.hero-header h1 { 
    color: #ffffff !important; 
    margin: 0 !important; 
    font-size: 16px !important; 
    font-weight: 700; 
}
.hero-header p { 
    color: #dbeafe !important; 
    margin: 0 !important; 
    font-size: 11px !important; 
}
/* بطاقات الأقسام */
.panel-card { 
    background: #ffffff; 
    border: 1px solid #cbd5e1; 
    border-radius: 8px; 
    padding: 8px 12px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
}
.panel-title { 
    font-size: 13px !important; 
    font-weight: 700 !important; 
    color: #1e3a8a !important; 
    margin: 0 0 6px 0 !important; 
    border-bottom: 1.5px solid #dbeafe; 
    padding-bottom: 3px; 
}
/* تصغير المدخلات ورفع الملفات لتاخذ سطر واحد رفيع */
.compact-field {
    margin-bottom: 4px !important;
}
.compact-field label span {
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-bottom: 1px !important;
}
.compact-field input, .compact-field textarea {
    padding: 3px 8px !important;
    font-size: 12px !important;
    height: 32px !important;
    min-height: 32px !important;
}
/* حقل رفع الملفات مدمج تماماً */
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
/* أزرار العمليات */
.btn-primary-action { 
    height: 36px !important; 
    min-height: 36px !important; 
    font-weight: 700 !important; 
    font-size: 13px !important; 
    border-radius: 6px !important;
}
/* شريط التبويبات */
.tabs {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
.tab-nav { 
    margin-bottom: 6px !important; 
    border-bottom: 2px solid #cbd5e1 !important;
    flex-shrink: 0;
}
.tab-nav > button { 
    font-size: 13px !important; 
    font-weight: 600 !important; 
    padding: 5px 14px !important; 
}
/* محتوى التبويبة يملأ المساحة بدون سكرول */
.tabitem {
    flex: 1 !important;
    overflow: hidden !important;
    padding: 2px 0 !important;
}
"""

with gr.Blocks(title="🎬 صانع الفيديوهات الآلي - v3", theme=gr.themes.Default(primary_hue="blue", spacing_size="sm", text_size="sm"), css=css) as demo:
    gr.HTML("""
    <div class="hero-header">
        <div>
            <h1>🎬 صانع الفيديوهات الآلي الاحترافي (v3)</h1>
            <p>الإنتاج الفائق بالذكاء الاصطناعي مع تحكم متكامل بدون أي سكرول</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">
            ⚡ V3 Ultra-Compact
        </div>
    </div>
    """)
    
    current_config = load_config()
    
    with gr.Tabs():
        # ==============================================================
        # --- تبويبة 1: صناعة فيديو مفرد ---
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
            
            single_output_log = gr.Textbox(
                label="📺 شاشة المتابعة الحية ومجريات العمل", 
                lines=15, 
                interactive=False
            )
            single_start_btn.click(fn=run_single_topic, inputs=single_topic_input, outputs=single_output_log)

        # ==============================================================
        # --- تبويبة 2: الإنتاج بالجملة ---
        # ==============================================================
        with gr.TabItem("📚 إنتاج بالجملة (JSON)"):
            with gr.Column(elem_classes=["panel-card"]):
                resume_alert = gr.Markdown(visible=False)
                resume_btn = gr.Button("🔄 استكمال العمل السابق غير المكتمل", variant="stop", visible=False, elem_classes=["btn-primary-action"])
                
                with gr.Row(equal_height=True):
                    json_file_input = gr.File(label="ملف قائمة المواضيع (JSON)", file_types=[".json"], scale=4, elem_classes=["compact-file-upload"])
                    batch_start_btn = gr.Button("🚀 إنتاج القائمة كاملة", variant="primary", scale=1, elem_classes=["btn-primary-action"])
                
            batch_output_log = gr.Textbox(
                label="📺 شاشة المتابعة الحية ومجريات العمل", 
                lines=14, 
                interactive=False
            )
            
            batch_start_btn.click(fn=run_batch_topics, inputs=json_file_input, outputs=batch_output_log)
            resume_btn.click(fn=resume_batch, outputs=batch_output_log)
            
            demo.load(fn=check_resume_status, outputs=resume_alert)
            demo.load(fn=lambda: gr.update(visible=True) if load_state().get("in_progress") else gr.update(visible=False), outputs=resume_btn)

        # ==============================================================
        # --- تبويبة 3: إدارة وسائط ومونتاج الفيديو (عرض مدمج 100% في الشاشة) ---
        # ==============================================================
        with gr.TabItem("🎥 وسائط ومقاطع المونتاج"):
            with gr.Row():
                # --- العمود الأول (اليمين) ---
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>🎮 الجيم بلاي وفيديوهات الهوك وصوت الهوك</div>")
                    
                    # 1. الجيم بلاي
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
                    gameplay_file_upload.change(fn=on_upload_gameplay, inputs=gameplay_file_upload, outputs=gameplay_path_input)

                    # 2. مجلد الهوكات
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
                    hooks_upload_msg = gr.Markdown("", visible=False)
                    hooks_folder_upload.change(
                        fn=on_upload_hooks_folder,
                        inputs=hooks_folder_upload,
                        outputs=[hook_dir_input, hooks_upload_msg]
                    )

                    # 3. صوت نهاية الهوك
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
                    hook_audio_upload.change(fn=on_upload_hook_audio, inputs=hook_audio_upload, outputs=hook_audio_input)

                # --- العمود الثاني (اليسار) ---
                with gr.Column(scale=1, elem_classes=["panel-card"]):
                    gr.Markdown("<div class='panel-title'>🎵 الموسيقى التصويرية ومقطع الخاتمة</div>")
                    
                    # 4. موسيقى الخلفية
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
                    bg_music_upload.change(fn=on_upload_bg_music, inputs=bg_music_upload, outputs=bg_music_input)

                    # 5. خاتمة الفيديو
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
                    outro_upload.change(fn=on_upload_outro, inputs=outro_upload, outputs=outro_path_input)

                    # زر الحفظ المباشر
                    with gr.Row():
                        save_assets_btn = gr.Button("💾 حفظ وتطبيق مسارات الوسائط", variant="primary", elem_classes=["btn-primary-action"])
                    save_assets_status = gr.Markdown("")

        # ==============================================================
        # --- تبويبة 4: إعدادات الذكاء الاصطناعي وتيليجرام (مضغوطة في شاشة واحدة) ---
        # ==============================================================
        with gr.TabItem("⚙️ الإعدادات الأساسية وتيليجرام"):
            with gr.Row():
                # عمود 1: الذكاء الاصطناعي والصوت
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

                # عمود 2: إعدادات تيليجرام
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
                        placeholder="8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ",
                        lines=1,
                        elem_classes=["compact-field"]
                    )
                    channel_id_input = gr.Textbox(
                        label="مُعرّف القناة (Channel ID)",
                        value=current_config.get("channel_id", ""),
                        placeholder="-1004247712091",
                        lines=1,
                        elem_classes=["compact-field"]
                    )

            # زر الحفظ الموحد بالأسفل
            with gr.Row():
                save_api_btn = gr.Button("💾 حفظ وتطبيق كافة الإعدادات الأساسية", variant="primary", elem_classes=["btn-primary-action"])
            save_api_status = gr.Markdown("")

    # دالة حفظ شاملة للإعدادات
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
