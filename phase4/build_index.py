#!/usr/bin/env python3
"""Phase 4 - build_index.py: load -> chunk -> embed -> FAISS. Re-runnable, no duplicates.

Usage:
    python build_index.py            # skips if no file changed
    python build_index.py --rebuild  # force full rebuild
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
RESULTS_DIR = HERE / "results"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED = (".txt", ".md", ".pdf")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_txt(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    return [{"text": text, "source": path.name, "page": 1}] if text else []


def load_pdf(path: Path):
    from pypdf import PdfReader
    pages = []
    for i, page in enumerate(PdfReader(str(path)).pages):
        text = (page.extract_text() or "").strip()
        if len(text) > 50:
            pages.append({"text": text, "source": path.name, "page": i + 1})
    return pages


def list_files(data_dir: Path):
    return [p for p in sorted(data_dir.iterdir()) if p.is_file() and p.suffix.lower() in SUPPORTED]


def load_all_docs(files):
    docs = []
    for p in files:
        docs.extend(load_pdf(p) if p.suffix.lower() == ".pdf" else load_txt(p))
    print(f"Loaded {len(docs)} pages from {len(files)} files")
    return docs


def chunk_fixed(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Fixed character windows with overlap. Stops when the window reaches the end."""
    assert 0 <= overlap < size
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


def chunk_paragraph(text, max_size=CHUNK_SIZE):
    """Paragraph-aware: merge short paragraphs up to max_size; hard-split oversize ones."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for para in paras:
        if len(para) > max_size:
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.extend(chunk_fixed(para, max_size, CHUNK_OVERLAP))
        elif len(cur) + len(para) + 2 <= max_size:
            cur = f"{cur}\n\n{para}" if cur else para
        else:
            chunks.append(cur)
            cur = para
    if cur:
        chunks.append(cur)
    return chunks


def build_index(force=False):
    RESULTS_DIR.mkdir(exist_ok=True)
    manifest_path = RESULTS_DIR / "manifest.json"
    index_path = RESULTS_DIR / "faiss.index"
    meta_path = RESULTS_DIR / "chunks_metadata.json"

    files = list_files(DATA_DIR)
    current = {p.name: file_hash(p) for p in files}
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    outputs_exist = index_path.exists() and meta_path.exists()
    if not force and outputs_exist and current == old:
        print(f"No changes ({len(current)} files). Index up to date.")
        return
    added = sorted(set(current) - set(old))
    removed = sorted(set(old) - set(current))
    changed = sorted(n for n in current if n in old and current[n] != old[n])
    print(f"added={added} changed={changed} removed={removed}")

    chunks, seen = [], set()
    for doc in load_all_docs(files):
        for i, text in enumerate(chunk_fixed(doc["text"])):
            h = hashlib.sha256(text.encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            chunks.append({"text": text, "source": doc["source"], "page": doc["page"],
                           "chunk_id": f"{doc['source']}_p{doc['page']}_c{i}"})
    if not chunks:
        raise SystemExit("No chunks produced. Put .txt/.md/.pdf files in data/.")
    print(f"{len(chunks)} unique chunks")

    model = SentenceTransformer(MODEL_NAME)
    emb = model.encode([c["text"] for c in chunks], batch_size=32, show_progress_bar=True).astype("float32")
    faiss.normalize_L2(emb)                      # normalise BEFORE adding: inner product == cosine
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)

    # write outputs, manifest LAST so a crash never leaves a manifest claiming a good index
    faiss.write_index(index, str(index_path))
    meta_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(current, indent=2))
    print(f"Index built: {index.ntotal} vectors, dim={emb.shape[1]} -> {index_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="force full rebuild")
    build_index(force=ap.parse_args().rebuild)
