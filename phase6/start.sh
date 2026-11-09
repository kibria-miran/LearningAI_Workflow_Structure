#!/bin/sh
set -e
# build the index on first start (no-op when data is unchanged)
python /app/phase4/build_index.py
exec uvicorn app:app --app-dir /app --host 0.0.0.0 --port 8000
