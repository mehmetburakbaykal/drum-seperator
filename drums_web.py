from flask import Flask, request, render_template_string, redirect, url_for, flash
import os, subprocess, tempfile
from pathlib import Path
from werkzeug.utils import secure_filename
from shutil import copyfile

app = Flask(__name__)
app.secret_key = "drumsep-local"

# ——— Ayarlar ———
MODEL = "htdemucs"
OUTPUT_DIR = Path.home() / "Desktop" / "DrumExports"   # çıktılar buraya
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".mp4", ".mov", ".mkv"}

# ——— Basit HTML (tek sayfa) ———
HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>Drum Separator</title>
<style>
  body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:40px;}
  .box{max-width:820px;margin:auto}
  .card{border:1px solid #ddd;border-radius:12px;padding:20px}
  .muted{color:#666}
  button{padding:10px 16px;border-radius:8px;border:1px solid #333;background:#111;color:#fff;cursor:pointer}
  input[type=file]{padding:10px;border:1px dashed #888;border-radius:8px;width:100%;}
  .ok{color:green}
  .err{color:#b00020}
  a{color:#0066cc}
</style>
</head>
<body>
<div class="box">
  <h2>🥁 Davulsuz Versiyon (Demucs)</h2>
  <p class="muted">Desteklenen: mp3, wav, flac, m4a, aac, ogg, mp4, mov, mkv — Çıktılar: <b>{{ outdir }}</b></p>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <div>
      {% for cat,msg in messages %}
        <p class="{{ 'ok' if cat=='ok' else 'err' }}">{{ msg|safe }}</p>
      {% endfor %}
      </div>
    {% endif %}
  {% endwith %}

  <div class="card">
    <form method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">
      <input type="file" name="files" multiple required>
      <p class="muted">Birden fazla seçebilirsin. İşlem bitince klasör otomatik açılacak.</p>
      <button type="submit">Ayrıştır</button>
    </form>
  </div>

</div>
</body>
</html>
"""

def run(cmd, env=None):
    """Komut çalıştır, çıktı ve kodu döndür."""
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)

def separate_to_no_drums_mp3(src_path: Path) -> Path:
    """
    Verilen medya dosyası için:
    - (video ise) sesi WAV'a çıkar
    - Demucs'u --mp3 ile çalıştır
    - no_drums.mp3'yi masaüstündeki OUTPUT_DIR'e <ad>_no_drums.mp3 ismiyle kopyala
    """
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        audio = src_path

        # Video ise sesi çıkar (44100 Hz stereo WAV)
        if src_path.suffix.lower() in {".mp4", ".mov", ".mkv"}:
            audio = td / (src_path.stem + ".wav")
            r = run(["ffmpeg", "-y", "-i", str(src_path), "-vn",
                     "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", str(audio)])
            if r.returncode != 0:
                raise RuntimeError(r.stdout)

        # Demucs: 2 stem (drums/no_drums), direkt MP3 yaz
        env = os.environ.copy()
        env.setdefault("PYTHONWARNINGS", "ignore")
        env.setdefault("TORCHAUDIO_USE_SOUNDFILE", "1")

        r = run(["demucs", "-n", MODEL, "--two-stems", "drums", "--mp3", "-o", str(td), str(audio)], env=env)
        if r.returncode != 0:
            raise RuntimeError(r.stdout)

        # no_drums.mp3'yi al ve hedefe kopyala
        no_drums_mp3 = td / MODEL / audio.stem / "no_drums.mp3"
        if not no_drums_mp3.exists():
            # Çok nadir durumlarda mp3 üretilemezse hata verelim
            raise RuntimeError("no_drums.mp3 bulunamadı. Demucs çıktısı beklenen yerde değil.")

        out_mp3 = OUTPUT_DIR / f"{src_path.stem}_no_drums.mp3"
        copyfile(no_drums_mp3, out_mp3)
        return out_mp3

@app.get("/")
def index():
    return render_template_string(HTML, outdir=str(OUTPUT_DIR))

@app.post("/upload")
def upload():
    files = request.files.getlist("files")
    if not files:
        flash("Dosya seçilmedi.", "err")
        return redirect(url_for("index"))

    ok_count, errs = 0, []
    for f in files:
        if not f.filename:
            continue
        name = secure_filename(f.filename)
        p = Path(name)
        ext = p.suffix.lower()
        if ext not in ALLOWED:
            errs.append(f"Desteklenmeyen tür: {name}")
            continue

        # Geçici dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            f.save(tmp.name)
            tmp_path = Path(tmp.name)

        try:
            out = separate_to_no_drums_mp3(tmp_path)
            ok_count += 1
        except Exception as e:
            errs.append(f"{name}: hata<br><pre>{str(e)[:1200]}</pre>")
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    if ok_count:
        flash(f"{ok_count} dosya başarıyla işlendi. Çıktılar: <b>{OUTPUT_DIR}</b>", "ok")
        # macOS: klasörü aç
        try:
            subprocess.run(["open", str(OUTPUT_DIR)])
        except Exception:
            pass

    for e in errs:
        flash(e, "err")

    return redirect(url_for("index"))

if __name__ == "__main__":
    # Sadece yerelde çalıştırıyoruz
    app.run(host="127.0.0.1", port=5000, debug=False)

