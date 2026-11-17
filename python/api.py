"""Receives audio files to transcribe (queued on disk, processed by worker.py).

POST /transcrip  (multipart: domain, id, audio) — header X-Whisper-Token required.
"""
import hmac
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Header, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_IN = os.path.join(BASE_DIR, "var/audio")

load_dotenv(os.path.join(BASE_DIR, ".env"))

WHISPER_TOKEN = os.getenv("WHISPER_TOKEN", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
# Names become paths: only safe characters (no "/", "..", etc.).
DOMAIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.:-]{0,190}$")
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
EXTENSIONS = {".webm", ".ogg", ".oga", ".opus", ".mp3", ".m4a", ".mp4", ".aac", ".wav", ".amr", ".3gp"}

app = FastAPI(title="Controle Online Transcription API")


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcrip")
async def transcrip(
    domain: str = Form(...),
    id: str = Form(...),
    audio: UploadFile = Form(...),
    x_whisper_token: str = Header(default=""),
):
    if not WHISPER_TOKEN or not hmac.compare_digest(x_whisper_token, WHISPER_TOKEN):
        raise HTTPException(status_code=401, detail="invalid token")
    if not DOMAIN_RE.match(domain) or ".." in domain or not ID_RE.match(id):
        raise HTTPException(status_code=400, detail="invalid domain or id")

    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in EXTENSIONS:
        raise HTTPException(status_code=415, detail="unsupported audio type")

    content = await audio.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="audio too large")

    target_dir = os.path.join(AUDIO_IN, domain)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, f"{id}{ext}")
    # Written under a temporary name and renamed: the worker never reads a half-written file.
    with open(file_path + ".part", "wb") as f:
        f.write(content)
    os.replace(file_path + ".part", file_path)

    return {"status": "queued", "id": id, "domain": domain}
