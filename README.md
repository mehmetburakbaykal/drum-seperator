# 🥁 Drum Separator App

**Drum Separator** is a lightweight local web app built with **Flask** and **Demucs** that lets you easily remove drums from any song or video — all locally, no internet required.

🎧 Ideal for musicians, remixers, and producers who want instant **drumless** (instrumental) or **drum-only** versions of their tracks.

---

## 🚀 Features

- 🎵 Supports **MP3**, **WAV**, **FLAC**, **M4A**, **AAC**, **OGG**, **MP4**, **MOV**, and **MKV**
- 🧠 Powered by **Facebook’s Demucs** deep learning model
- 💻 Works **entirely offline**
- 🧰 Built with **Python + Flask + FFmpeg**
- 💾 Automatically saves results to your desktop folder:

---

## 🧩 Requirements

- **Python 3.9+**
- **FFmpeg** (installed via Homebrew on macOS or other package managers)
- Python packages: `demucs`, `flask`, `ffmpeg-python`

---

## 🛠️ Setup Instructions

1️⃣ Clone the repository

```
git clone https://github.com/mehmetburakbaykal/drum-seperator.git
cd drum-seperator
```

2️⃣ Create and activate a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

3️⃣ Install dependencies

```
pip install demucs flask ffmpeg-python
```

4️⃣ Run the app

```
python drums_web_v2.py
```

5️⃣ Open your browser

Go to 👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧠 How It Works

1. Upload one or more audio/video files via the web interface.
2. If necessary, FFmpeg extracts the audio.
3. Demucs separates the stems into drums and no_drums.
4. The app automatically converts no_drums to MP3 and saves it to your desktop.

---

## 📁 Output Example

```
~/Desktop/DrumExports/
├── song1_no_drums.mp3
├── test_no_drums.mp3
├── live_video_no_drums.mp3
```

---

## 💡 Notes

- Everything runs locally on your computer — no cloud processing.
- Processing time depends on your CPU / GPU and track length.
- If you’d prefer the drum-only version instead of removing drums, simply edit:

`no_drums_mp3 → drums_mp3`

---

## 🧑‍💻 Developer Tips

To edit the app:
`code ~/drumsep`

To run with auto-reload (debug mode):
`app.run(host="127.0.0.1", port=5000, debug=True)`

Recommended .gitignore:

```
venv/
lib/
bin/
include/
__pycache__/
*.wav
*.mp3
separated/
DrumExports/
.DS_Store
```

## 📝 License

MIT License © 2025 Mehmet Burak Baykal

## ❤️ Credits

- [Facebook Research — Demucs](https://github.com/facebookresearch/demucs)
- [FFmpeg](https://ffmpeg.org/)
- [Flask](https://flask.palletsprojects.com/)
