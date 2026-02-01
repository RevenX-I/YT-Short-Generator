# ShortsGPT Premium

A modular, automated video creation tool using Gemini, Pexels, Edge-TTS, Faster-Whisper, and MoviePy.

## 🚀 Setup

### 1. System Requirements
- **ImageMagick**: Must be installed.
    - Windows: Check "Install legacy utilities (e.g. convert)" during installation.
    - Linux: `sudo apt-get install imagemagick`
- **FFmpeg**: Usually installed with dependencies, but ensure it is in your PATH.

### 2. Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Keys
Rename `.env.example` to `.env` (or create `.env`) and add your keys:
- `GEMINI_API_KEY`: For script generation.
- `PEXELS_API_KEY`: For downloading stock footage.

### 4. Fonts
Download a bold font like **Montserrat Black** and place it in `fonts/Montserrat-Black.ttf`.

## 🏃‍♂️ Usage
Run the Streamlit dashboard:
```bash
streamlit run main.py
```

## 🏗️ Architecture
- **Brain**: `src/content_engine.py` (Gemini)
- **Assets**: `src/media_fetcher.py` (Pexels + EdgeTTS)
- **Sync**: `src/subtitle_gen.py` (Faster-Whisper)
- **Editor**: `src/video_editor.py` (MoviePy)
