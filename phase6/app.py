"""Phase 6 - app.py: FastAPI wrapper around the Phase 4 RAG system.

Local:  uvicorn app:app --reload        (from phase6/, with ../phase4 index built)
Docker: see docker-compose.yml
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "phase4", ROOT / "phase3"):      # same layout locally and in the image
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

APP_API_KEY = os.getenv("APP_API_KEY", "")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app = FastAPI(title="RAG Application API", version="1.0.0")
if ALLOWED_ORIGINS:                                # no wildcard: list real origins or none
    app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                       allow_methods=["GET", "POST"], allow_headers=["*"])


class Query(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def require_key(x_api_key: str = Header(default="")):
    if APP_API_KEY and x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


@app.get("/")
def root():
    return {"message": "RAG Application is running", "version": app.version}


@app.get("/health")
def health():
    """Liveness + readiness: is the index present?"""
    results = ROOT / "phase4" / "results"
    ready = (results / "faiss.index").exists() and (results / "chunks_metadata.json").exists()
    return {"status": "ok" if ready else "degraded", "index_ready": ready}


# plain `def` (not async): FastAPI runs it in a thread pool, so the slow
# embed + LLM call does not block other requests.
@app.post("/query", dependencies=[Depends(require_key)])
def query_rag(body: Query):
    try:
        from ask import rag_answer
        r = rag_answer(body.question)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:                      # budget cap, provider failure
        raise HTTPException(status_code=502, detail=str(e))
    # a refusal is a valid answer, not an error: n8n can branch on "refused"
    return {"answer": r["answer"], "sources": r["sources"], "refused": r["refused"], "cost": r["cost"]}
