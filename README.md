# Automated AI Shorts & Video Creator 🎬 (v3)

An end-to-end automated system designed to create high-retention, high-quality vertical short videos (YouTube Shorts, TikTok, Instagram Reels) directly from a prompt using AI—covering scriptwriting, neural voiceovers, dynamic captions, editing, and instant publishing.

---

## 🌟 Overview & Key Features

This tool completely automates the production pipeline for short-form video creation:

1. **AI Script Generation**: Connects to an OpenAI-compatible API (e.g., local ChatGPT/LLMs) to craft engaging, suspenseful scripts split into synchronized visual scenes with tailored search keywords.
2. **Studio-Quality Voiceover (Edge TTS)**: Synthesizes ultra-realistic, natural voiceovers using Microsoft Edge Neural Voices (e.g., `GuyNeural`).
3. **High-Speed Parallel Image Fetching**: Downloads the most relevant, high-resolution scene imagery simultaneously using multi-threaded execution (`ThreadPoolExecutor`).
4. **Animated Word-by-Word Subtitles (Faster-Whisper)**: Extracts high-precision word timestamps and burns stylized, high-contrast dynamic subtitles with highlighted keywords into the frame.
5. **Advanced Video Composition (MoviePy & FFmpeg)**:
   - Splits screen dynamically: top section displays the story visual/slideshow, bottom section loops HD gameplay footage.
   - Attention-grabbing visual hook overlay at the beginning.
   - Low-volume atmospheric background music seamlessly mixed beneath the narration.
   - Smart Outro: dynamically trims end-of-speech dead silence and stitches a high-energy subscribe call-to-action video.
6. **Blazing Fast Multi-threaded Rendering**: Optimizes CPU usage with 8-threaded video encoding (`preset="veryfast"`) and multi-core Whisper indexing for lightning-fast turnaround.
7. **Modern Compact Web GUI**: Clean, single-page dashboard built with Gradio—manage voice styles, topics, credentials, and video assets without scrolling.
8. **Automated Telegram Publishing**: Automatically generates engaging English descriptions, trending hashtags, and pushes finished videos directly to your Telegram channel.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.12 (64-bit)** (Required for compiled bytecode runtime).
- **FFmpeg** installed and accessible in your system's `PATH`.

### 2. Quick Installation (One-Click Setup)
If you are on Windows, simply double-click:
- **`install.bat`**: Automatically checks for Python 3.12, installs all required packages, and checks for FFmpeg.

Or install manually using your terminal:
```bash
pip install moviepy==1.0.3 faster-whisper edge-tts requests gradio pillow gtts pydub kokoro-onnx soundfile pyttsx3 json-repair
```

> [!NOTE]
> Ensure you install `moviepy==1.0.3` to maintain full compatibility with the audio filters and composite video FX.

---

## ⚙️ Configuration

The project uses `config.json` to store your local AI endpoints, Telegram credentials, voice settings, and media paths:

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

## 🚀 How to Use

You can run the generator via One-Click Launcher, Web Dashboard, or Command Line.

### 1. One-Click Launcher (Windows)
Simply double-click:
- **`start.bat`**: Automatically launches the dashboard and opens `http://127.0.0.1:7860` in your default browser.

### 2. Modern Web GUI (Manual)
Launch the compact dashboard from the terminal:
```bash
python web_gui.pyc
```
Open your browser and navigate to: `http://127.0.0.1:7860`

---

### 3. Command Line Interface (CLI)
Generate a video directly for a specific topic:

```bash
python video_maker.pyc --topic "The Mystery of the Bermuda Triangle"
```

Or batch-generate videos using a playlist JSON file:

```bash
python video_maker.pyc --playlist topics.json
```

---

## 📁 Output Structure

All generated projects are stored inside the `video_workspace/` directory:
- Generated script text file
- Voiceover audio (`.mp3`)
- Synchronized scene images
- Final rendered video (`final_video.mp4`)
