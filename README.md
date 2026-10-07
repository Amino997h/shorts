# Automated AI Video Creator 🎬

This Python script is a fully automated tool that creates short videos from scratch based on a simple text prompt.

## Features:
1. **AI Script Generation**: Connects to an OpenAI-compatible local ChatGPT API to write an engaging script in Arabic and generate relevant image keywords.
2. **Text-to-Speech (TTS)**: Converts the generated Arabic script into high-quality audio using `gTTS`.
3. **Automated Image Scraping**: Scrapes real, highly relevant images from Bing directly without needing an API key.
4. **Automated Video Editing**: Uses `MoviePy` to stitch the images together into a synced slideshow over the generated voiceover, and exports an MP4 file.

## Requirements:
- Python 3.8+
- `pip install moviepy==1.0.3 gTTS requests`
- A running local OpenAI-compatible API (e.g. at `http://127.0.0.1:8008/v1/chat/completions`)

## Usage:
Simply run the script:
```bash
python video_maker.py
```
Type your topic (e.g. "تاريخ الذكاء الاصطناعي"), and wait for the magic to happen! The final video will be automatically opened when ready.
