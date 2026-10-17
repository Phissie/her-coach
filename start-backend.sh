#!/bin/bash
echo "=== Cycle Coach — Backend ==="
cd "$(dirname "$0")/backend"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000