import os
from fastapi import FastAPI, UploadFile, Form
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_IN = os.path.join(BASE_DIR, "var/audio")

load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

@app.post("/transcrip")
async def transcrip(
    domain: str = Form(...),
    id: str = Form(...),
    audio: UploadFile = Form(...)
):
    target_dir = os.path.join(AUDIO_IN, domain)
    os.makedirs(target_dir, exist_ok=True)

    ext = os.path.splitext(audio.filename)[1] or ".bin"
    file_path = os.path.join(target_dir, f"{id}{ext}")

    with open(file_path, "wb") as f:
        f.write(await audio.read())

    return {"status": "queued", "id": id, "domain": domain}
