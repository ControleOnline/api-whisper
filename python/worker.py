"""Transcribes queued audio files and posts the text back to the main API.

var/audio/{domain}/{id}.{ext}  ->  var/transcripted/{id}.json  ->  POST API_ENDPOINT

The model is loaded only when there is work and released after WHISPER_IDLE_UNLOAD seconds idle,
so the (small) server keeps its memory for the other services. Failed callbacks are retried.
"""
import gc
import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_IN = os.path.join(BASE_DIR, "var/audio")
TRANSCRIPTED = os.path.join(BASE_DIR, "var/transcripted")

load_dotenv(os.path.join(BASE_DIR, ".env"))

API_ENDPOINT = os.getenv("API_ENDPOINT", "")
CALLBACK_TOKEN = os.getenv("API_TOKEN", "")
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
LANGUAGE = os.getenv("WHISPER_LANGUAGE", "pt")
IDLE_UNLOAD = int(os.getenv("WHISPER_IDLE_UNLOAD", "120"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2"))
RETRY_SECONDS = int(os.getenv("CALLBACK_RETRY_SECONDS", "60"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("whisper-worker")

_model = None
_last_used = 0.0
_next_try = {}


def model():
    global _model, _last_used
    if _model is None:
        import whisper  # heavy import: only when needed

        log.info("loading model %s", MODEL_NAME)
        _model = whisper.load_model(MODEL_NAME, device="cpu")
    _last_used = time.time()
    return _model


def release_idle_model():
    global _model
    if _model is not None and time.time() - _last_used > IDLE_UNLOAD:
        log.info("releasing idle model")
        _model = None
        gc.collect()


def pending_audio():
    for root, _, files in os.walk(AUDIO_IN):
        for name in sorted(files):
            if not name.endswith(".part") and not name.startswith("."):
                yield os.path.join(root, name)


def transcribe(path):
    domain = os.path.basename(os.path.dirname(path))
    file_id, _ = os.path.splitext(os.path.basename(path))
    out = os.path.join(TRANSCRIPTED, f"{file_id}.json")
    if os.path.exists(out):
        return
    try:
        result = model().transcribe(path, language=LANGUAGE, fp16=False)
        text = (result.get("text") or "").strip()
    except Exception as error:  # unreadable audio: report empty text, do not loop on it
        log.warning("transcription failed for %s: %s", path, error)
        text = ""
    with open(out + ".part", "w", encoding="utf-8") as f:
        json.dump({"id": file_id, "domain": domain, "text": text}, f, ensure_ascii=False)
    os.replace(out + ".part", out)
    log.info("transcribed %s/%s (%d chars)", domain, file_id, len(text))


def deliver(json_path):
    if time.time() < _next_try.get(json_path, 0):
        return
    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)
    headers = {"Content-Type": "application/json", "X-Whisper-Token": CALLBACK_TOKEN, "App-Domain": payload["domain"]}
    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=30)
        ok = 200 <= response.status_code < 300
    except requests.RequestException as error:
        log.warning("callback error for %s: %s", payload["id"], error)
        ok = False
    if not ok:
        _next_try[json_path] = time.time() + RETRY_SECONDS
        return
    for path in pending_audio():
        if os.path.splitext(os.path.basename(path))[0] == payload["id"]:
            os.remove(path)
    os.remove(json_path)
    _next_try.pop(json_path, None)
    log.info("delivered %s", payload["id"])


def main():
    os.makedirs(AUDIO_IN, exist_ok=True)
    os.makedirs(TRANSCRIPTED, exist_ok=True)
    log.info("worker started (model %s, idle unload %ss)", MODEL_NAME, IDLE_UNLOAD)
    while True:
        for path in pending_audio():
            transcribe(path)
        for name in sorted(os.listdir(TRANSCRIPTED)):
            if name.endswith(".json"):
                deliver(os.path.join(TRANSCRIPTED, name))
        release_idle_model()
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
