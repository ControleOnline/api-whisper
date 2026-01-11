import os
import time
import json
import requests
import whisper
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

AUDIO_IN = os.path.join(BASE_DIR, "var/audio")
TRANSCRIPTED = os.path.join(BASE_DIR, "var/transcripted")

load_dotenv(os.path.join(BASE_DIR, ".env"))

API_ENDPOINT = os.getenv("API_ENDPOINT")
API_TOKEN = os.getenv("API_TOKEN")

model = whisper.load_model("base")

class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        domain = os.path.basename(os.path.dirname(event.src_path))
        file_id, _ = os.path.splitext(os.path.basename(event.src_path))

        result = model.transcribe(event.src_path, language="pt")

        payload = {
            "id": file_id,
            "domain": domain,
            "text": result["text"]
        }

        with open(os.path.join(TRANSCRIPTED, f"{file_id}.json"), "w") as f:
            json.dump(payload, f)

class JsonHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        with open(event.src_path) as f:
            payload = json.load(f)

        headers = {
            "Content-Type": "application/json",
            "api-token": API_TOKEN,
            "app-domain": payload["domain"]
        }

        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            audio_path = None

            for root, _, files in os.walk(AUDIO_IN):
                for name in files:
                    if name.startswith(payload["id"] + "."):
                        audio_path = os.path.join(root, name)
                        break

            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

            os.remove(event.src_path)

observer = Observer()
observer.schedule(AudioHandler(), AUDIO_IN, recursive=True)
observer.schedule(JsonHandler(), TRANSCRIPTED, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
