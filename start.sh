#!/bin/bash
cd python
uvicorn api:app --host 0.0.0.0 --port 8000 &
python3 worker.py