"""Dense (FAISS) retrieval. Model + index are loaded once and cached."""
import json
from functools import lru_cache
from pathlib import Path

MODEL_NAME = "all-MiniLM-L6-v2"
RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
SIMILARITY_THRESHOLD = 0.30   # tune against tests/rag_eval.yaml, not by feel


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def _index_and_chunks():
    import faiss
    idx_path = RESULTS_DIR / "faiss.index"
    meta_path = RESULTS_DIR / "chunks_metadata.json"
    if not idx_path.exists() or not meta_path.exists():
        raise FileNotFoundError("Index missing. Run: python build_index.py")
    index = faiss.read_index(str(idx_path))
    chunks = json.loads(meta_path.read_text(encoding="utf-8"))
    if index.ntotal != len(chunks):
        raise RuntimeError(
            f"Index/metadata mismatch ({index.ntotal} vs {len(chunks)}). Re-run build_index.py --rebuild"
        )
    return index, chunks


def reset_cache():
    _index_and_chunks.cache_clear()


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Top-k chunks with cosine score, best first."""
    import faiss
    index, chunks = _index_and_chunks()
    vec = _model().encode([query]).astype("float32")
    faiss.normalize_L2(vec)
    scores, ids = index.search(vec, min(k, index.ntotal))
    out = []
    for score, i in zip(scores[0], ids[0]):
        if i == -1:
            continue
        c = dict(chunks[i])
        c["score"] = float(score)
        out.append(c)
    return out
