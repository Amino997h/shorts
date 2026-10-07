import gradio as gr
import subprocess
import os
import sys
import json

CONFIG_FILE = 'config.json'

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

def run_video_maker(topic):
    if not topic.strip():
        return "❌ يرجى إدخال موضوع صالح أولاً!"
        
    if os.name == 'nt':
        subprocess.Popen(['cmd.exe', '/k', 'python', 'video_maker.py', '--topic', topic], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(['python', 'video_maker.py', '--topic', topic])
        
    return f"✅ تم استلام الطلب!\\n🚀 جاري تشغيل سكريبت الإنتاج لموضوع: {topic}\\nيمكنك متابعة تقدم التحميل والمونتاج في الشاشة السوداء التي ظهرت للتو."

css = """
body {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.gradio-container {
    max-width: 900px !important;
}
"""

with gr.Blocks(title="🎬 صانع الفيديوهات الآلي", theme=gr.themes.Soft(primary_hue="blue"), css=css) as demo:
    gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🎬 صانع الفيديوهات الآلي الاحترافي</h1>")
    
    current_config = load_config()
    
    with gr.Tabs():
        with gr.TabItem("🚀 صناعة فيديو جديد"):
            gr.Markdown("<p style='text-align: center; font-size: 16px;'>أدخل موضوع الفيديو بالأسفل وسيتكفل الذكاء الاصطناعي بكل شيء (السكريبت، الصوت، الصور، المونتاج، والنشر على تيليجرام).</p>")
            with gr.Row():
                topic_input = gr.Textbox(label="موضوع الفيديو", placeholder="مثال: أسرار الفضاء، الذكاء الاصطناعي، شرح التداول...", scale=4)
            with gr.Row():
                start_btn = gr.Button("🚀 بدء الإنتاج", variant="primary", size="lg")
            output_log = gr.Textbox(label="حالة النظام", lines=4, interactive=False)
            
            start_btn.click(fn=run_video_maker, inputs=topic_input, outputs=output_log)

        with gr.TabItem("⚙️ الإعدادات (API & Telegram)"):
            gr.Markdown("قم بتعديل مفاتيح الربط هنا وسيتم حفظها مباشرة في النظام.")
            with gr.Group():
                api_url_input = gr.Textbox(label="رابط الـ API (Local LLM / OpenAI)", value=current_config["api_url"])
                api_key_input = gr.Textbox(label="مفتاح الـ API Key", value=current_config["api_key"], type="password")
            
            with gr.Group():
                bot_token_input = gr.Textbox(label="توكن بوت تيليجرام (Bot Token)", value=current_config["bot_token"], type="password")
                channel_id_input = gr.Textbox(label="مُعرّف قناة تيليجرام (Channel ID)", value=current_config["channel_id"])
                
            save_btn = gr.Button("💾 حفظ الإعدادات", variant="secondary")
            save_status = gr.Markdown("")
            
            save_btn.click(
                fn=save_config,
                inputs=[api_url_input, api_key_input, bot_token_input, channel_id_input],
                outputs=save_status
            )

if __name__ == "__main__":
    print("جاري تشغيل الموقع المحلي...")
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
