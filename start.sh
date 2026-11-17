#!/bin/bash
# Local/dev start (production uses deploy/systemd units). Binds to localhost: nginx proxies it.
set -e
cd "$(dirname "$0")"
set -a; [ -f .env ] && . ./.env; set +a
cd python
../venv/bin/uvicorn api:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8090}" &
exec ../venv/bin/python worker.py
