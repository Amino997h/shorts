# Automated AI Shorts & Video Creator 🎬 (v3)

نظام متكامل ومؤتمت بالكامل لصناعة مقاطع الفيديو القصيرة (YouTube Shorts / TikTok / Reels) بجودة عالية وبشكل فوري بالذكاء الاصطناعي، بدءاً من كتابة السكربت وحتى التصدير والنشر.

---

## 🌟 الوصف (Description)

هذا المشروع يوفر حلاً شاملاً وسريعاً لإنشاء مقاطع فيديو عمودية (9:16) جاهزة للنشر تلقائياً:
1. **توليد السكربت الذكي (AI Scripting):** يتصل بالذكاء الاصطناعي (Local ChatGPT / OpenAI API) لصياغة قصة مشوقة ومقسمة إلى مشاهد محددة مع كلمات مفتاحية دقيقة للصور.
2. **التعليق الصوتي الاحترافي (Edge TTS):** تحويل النص إلى صوت طبيعي بجودة استوديو باستخدام أصوات Microsoft Edge العصبية (Neural Voices) مثل `GuyNeural`.
3. **تحميل الصور بالتوازي (Fast Parallel Image Fetching):** تنزيل أحدث الصور المناسبة لكل مشهد بشكل متوازٍ (`ThreadPoolExecutor`) لتوفير الوقت.
4. **تزامن الكلمات والترجمة الحركية (Faster-Whisper):** استخراج التوقيت الدقيق لكل كلمة وعرض ترجمة سينمائية متحركة على الشاشة بألوان وخطوط جذابة.
5. **مونتاج الفيديو والمؤثرات (MoviePy & FFmpeg):**
   - دمج خلفية ألعاب (Gameplay Background) بالأسفل مع مقاطع أو صور القصة بالأعلى.
   - إضافة هوك جذب انتباه في البداية (Hook Overlay).
   - موسيقى خلفية هادئة متناسقة.
   - خاتمة احترافية سريعة مع زر الاشتراك مع قص الصمت الميت في نهاية الكلام تلقائياً.
6. **معالجة فائقة السرعة (High-Speed Multi-threading):** تصيير الفيديو باستخدام 8 مسارات معالجة وتسريع Whisper لتوليد الفيديو في وقت قياسي.
7. **واجهة تحكم ويب عصرية (Modern Compact Web GUI):** واجهة مدمجة ومريحة (Dashboard) تعمل من المتصفح للتحكم في الإعدادات والمواضيع والأصوات بكل سهولة.
8. **النشر التلقائي (Telegram Auto-Upload):** رفع الفيديو النهائي إلى قنوات تيليجرام فور اكتماله مع وصف مناسب وهاشتاغات.

---

## 🛠️ متطلبات التثبيت (Installation)

### 1. المتطلبات الأساسية
- مثبت لغة **Python 3.8** أو أعلى (يوصى بـ Python 3.10 أو 3.11).
- برنامج **FFmpeg** مثبت ومضاف إلى متغيرات البيئة (PATH).

### 2. تثبيت الحزم المطلوبة
افتح موجه الأوامر (Terminal / CMD / PowerShell) داخل مجلد المشروع، وقم بتثبيت المكتبات التالية:

```bash
pip install moviepy==1.0.3 faster-whisper edge-tts requests gradio pillow
```

> [!NOTE]
> تأكد من تثبيت `moviepy==1.0.3` لتوافق التأثيرات الصوتية ومسارات المونتاج.

---

## ⚙️ الإعدادات (Configuration)

يحتوي المشروع على ملف `config.json` يحتوي على مسارات الموارد وإعدادات الذكاء الاصطناعي والتيليجرام:

```json
{
    "api_url": "http://127.0.0.1:8008/v1/chat/completions",
    "api_key": "sk-chatgpt-local-secret-key",
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "channel_id": "YOUR_TELEGRAM_CHANNEL_ID",
    "upload_to_telegram": true,
    "voice": "en-US-GuyNeural - en-US (Male)",
    "gameplay_path": "path/to/gameplay.mp4",
    "hook_dir": "path/to/hook_folder",
    "bg_music_path": "path/to/bg_music.mp4",
    "outro_path": "path/to/outro.mp4"
}
```

---

## 🚀 طريقة الاستعمال (Usage)

يمكنك تشغيل المشروع بطريقتين:

### 1. عبر واجهة الويب (Web GUI) - الطريقة الموصى بها
واجهة سهلة ومدمجة بدون الحاجة للتمرير، تتيح لك كتابة المواضيع، واختيار الأصوات، وتغيير الإعدادات بنقرة زر:
```bash
python web_gui.py
```
ثم افتح الرابط في المتصفح: `http://127.0.0.1:7860`

---

### 2. عبر سطر الأوامر (Command Line)
يمكنك إنشاء فيديو مباشر بتحديد الموضوع:
```bash
python video_maker.py --topic "The Secret of the Bermuda Triangle"
```

أو المعالجة بالدفعات (Batch Mode) باستخدام ملف نصي أو قائمة مواضيع:
```bash
python video_maker.py --playlist topics.json
```

---

## 📁 هيكلية المخرجات
- يتم حفظ المشاريع المنشأة في مجلد `video_workspace/`.
- يحتوي كل مشروع على السكربت، الصوت المستخرج، الصور المجمعة، وملف الفيديو النهائي `final_video.mp4`.
