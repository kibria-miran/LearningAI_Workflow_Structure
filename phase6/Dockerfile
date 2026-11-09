# Phase 6 - RAG app image.
# BUILD CONTEXT IS THE PARENT FOLDER (it must contain phase3/ phase4/ phase6/):
#   cd phase6 && docker compose build
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/phase3:/app/phase4 \
    HF_HOME=/hf-cache

WORKDIR /app

# CPU-only torch first: avoids a ~2 GB CUDA download
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY phase6/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY phase3/ /app/phase3/
COPY phase4/ /app/phase4/
COPY phase6/app.py phase6/start.sh /app/
RUN chmod +x /app/start.sh && useradd -m appuser \
    && mkdir -p /hf-cache /app/phase3/results /app/phase4/results \
    && chown -R appuser /app /hf-cache
USER appuser

# tracker.py logs to results/usage.jsonl relative to the working directory
WORKDIR /app/phase3
EXPOSE 8000
CMD ["/app/start.sh"]
