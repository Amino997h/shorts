import gradio as gr
import subprocess
import os
import sys
import json
import time

CONFIG_FILE = 'config.json'
STATE_FILE = 'state.json'

def load_config():
    default_config = {
        "api_url": "http://127.0.0.1:8008/v1/chat/completions",
        "api_key": "sk-chatgpt-local-secret-key",
        "bot_token": "8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ",
        "channel_id": "-1004247712091"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except:
            pass
    return default_config

def save_config(api_url, api_key, bot_token, channel_id):
    config = {
        "api_url": api_url.strip(),
        "api_key": api_key.strip(),
        "bot_token": bot_token.strip(),
        "channel_id": channel_id.strip()
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return "✅ تم حفظ الإعدادات بنجاح!"
    except Exception as e:
        return f"❌ خطأ أثناء الحفظ: {e}"

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
        json.dump(state, f, indent=4)

def check_resume_status():
    state = load_state()
    if state.get("in_progress") and state.get("current_index", 0) < len(state.get("queue", [])):
        total = len(state['queue'])
        current = state['current_index'] + 1
        return gr.update(visible=True, value=f"⚠️ يوجد عمل غير مكتمل! توقف البرنامج عند الفيديو ({current} من {total}). اضغط على 'استكمال العمل' للمتابعة.")
    return gr.update(visible=False)

def run_single_topic(topic):
    yield from execute_topic(topic, 1, 1)

def run_batch_topics(json_file):
    if not json_file:
        yield "❌ يرجى رفع ملف JSON صالح!"
        return
        
    try:
        with open(json_file.name, 'r', encoding='utf-8') as f:
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

    # حفظ حالة جديدة
    state = {"queue": topics, "current_index": 0, "in_progress": True}
    save_state(state)
    
    yield from process_queue()

def resume_batch():
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
    
    overall_status = f"📚 جاري بدء إنتاج الجملة ({total} فيديوهات)\\n" + "="*40 + "\\n"
    yield overall_status
    
    for i in range(start_index, total):
        topic = queue[i]
        
        # تحديث نقطة الحفظ
        state["current_index"] = i
        save_state(state)
        
        # تشغيل موضوع واحد
        for update in execute_topic(topic, i + 1, total, prefix=overall_status):
            yield update
            
        # بعد الانتهاء من موضوع، تحديث النص الإجمالي
        overall_status += f"✅ اكتمل الفيديو ({i + 1}/{total}): {topic}\\n"
        yield overall_status
        
    # عند الانتهاء من الكل
    state["in_progress"] = False
    save_state(state)
    yield overall_status + "\\n🎉🎉 اكتملت جميع الفيديوهات في القائمة بنجاح! 🎉🎉"

def execute_topic(topic, current_num, total_num, prefix=""):
    if not topic.strip():
        yield prefix + "❌ يرجى إدخال موضوع صالح أولاً!"
        return
        
    start_time = time.time()
    header = f"🚀 [فيديو {current_num}/{total_num}] جاري العمل على: {topic}\\n" + "-"*40 + "\\n"
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
            
            if "[الخطوة" in line_stripped or "✓" in line_stripped or "خطأ" in line_stripped or "الوصف الجاهز" in line_stripped or "تم النشر" in line_stripped or "--- السكريبت ---" in line_stripped:
                status_text += f"🔹 {line_stripped}\\n"
                yield status_text
            elif line_stripped.startswith("جاري البحث عن:") or "تنبيه" in line_stripped:
                status_text += f"   - {line_stripped}\\n"
                yield status_text
                
        process.stdout.close()
        process.wait()
        
        elapsed = round(time.time() - start_time, 1)
        
        if process.returncode == 0:
            status_text += f"\\n🎉 اكتملت المهمة! (استغرق {elapsed} ثانية)\\n\\n"
        else:
            status_text += f"\\n❌ خطأ (كود {process.returncode}). (استغرق {elapsed} ثانية)\\n\\n"
            
        yield status_text
        
    except Exception as e:
        yield status_text + f"\\n❌ حدث خطأ غير متوقع: {e}\\n"

css = """
body { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.gradio-container { max-width: 900px !important; }
"""

with gr.Blocks(title="🎬 صانع الفيديوهات الآلي", theme=gr.themes.Soft(primary_hue="blue"), css=css) as demo:
    gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🎬 صانع الفيديوهات الآلي الاحترافي</h1>")
    
    current_config = load_config()
    
    with gr.Tabs():
        with gr.TabItem("🚀 صناعة فيديو مفرد"):
            gr.Markdown("أدخل موضوعاً واحداً لإنشاء فيديو مباشر.")
            with gr.Row():
                single_topic_input = gr.Textbox(label="موضوع الفيديو", placeholder="مثال: أسرار الفضاء...", scale=4)
            with gr.Row():
                single_start_btn = gr.Button("🚀 بدء الإنتاج", variant="primary")
            single_output_log = gr.Textbox(label="شاشة المتابعة الحية 📺", lines=15, interactive=False)
            single_start_btn.click(fn=run_single_topic, inputs=single_topic_input, outputs=single_output_log)

        with gr.TabItem("📚 الإنتاج بالجملة (JSON)"):
            gr.Markdown("ارفع ملف JSON يحتوي على قائمة مواضيع. سيقوم الذكاء الاصطناعي بصناعتها ونشرها واحداً تلو الآخر.")
            gr.Markdown("*مثال على محتوى الملف:* `[\"الذكاء الاصطناعي\", \"تاريخ روما\", \"اقتصاد الصين\"]`")
            
            resume_alert = gr.Markdown(visible=False)
            resume_btn = gr.Button("🔄 استكمال العمل السابق", variant="stop", visible=False)
            
            with gr.Row():
                json_file_input = gr.File(label="ملف المواضيع (JSON)", file_types=[".json"])
            with gr.Row():
                batch_start_btn = gr.Button("🚀 بدء إنتاج القائمة", variant="primary")
                
            batch_output_log = gr.Textbox(label="شاشة المتابعة الحية 📺", lines=15, interactive=False)
            
            batch_start_btn.click(fn=run_batch_topics, inputs=json_file_input, outputs=batch_output_log)
            resume_btn.click(fn=resume_batch, outputs=batch_output_log)
            
            # التحقق من وجود جلسة سابقة عند فتح التبويبة
            demo.load(fn=check_resume_status, outputs=resume_alert)
            demo.load(fn=lambda: gr.update(visible=True) if load_state().get("in_progress") else gr.update(visible=False), outputs=resume_btn)

        with gr.TabItem("⚙️ الإعدادات (API & Telegram)"):
            with gr.Group():
                api_url_input = gr.Textbox(label="رابط الـ API", value=current_config["api_url"])
                api_key_input = gr.Textbox(label="مفتاح الـ API Key", value=current_config["api_key"], type="password")
            with gr.Group():
                bot_token_input = gr.Textbox(label="توكن بوت تيليجرام", value=current_config["bot_token"], type="password")
                channel_id_input = gr.Textbox(label="مُعرّف القناة", value=current_config["channel_id"])
                
            save_btn = gr.Button("💾 حفظ الإعدادات", variant="secondary")
            save_status = gr.Markdown("")
            save_btn.click(fn=save_config, inputs=[api_url_input, api_key_input, bot_token_input, channel_id_input], outputs=save_status)

if __name__ == "__main__":
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
