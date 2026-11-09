#!/usr/bin/env python3
"""Phase 4 - build_index.py: Embeddings + Chunking + FAISS Index"""

import os
import hashlib
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

def file_hash(path):
    """Compute MD5 hash of a file for dedup."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_txt(path):
    """Load a .txt or .md file."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()
    return [{"text": content, "source": Path(path).name, "page": 1}]

def load_pdf(path):
    """Load a PDF. Returns one dict per page with metadata."""
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if len(text) > 50:
            pages.append({"text": text, "source": Path(path).name, "page": i + 1})
    return pages

def load_all_docs(data_dir):
    """Load all supported files from data_dir."""
    docs = []
    for fname in sorted(os.listdir(data_dir)):
        fpath = os.path.join(data_dir, fname)
        if fname.endswith(".pdf"):
            docs.extend(load_pdf(fpath))
        elif fname.endswith((".txt", ".md")):
            docs.extend(load_txt(fpath))
    print(f"Loaded {len(docs)} pages from {data_dir}")
    return docs

def chunk_fixed(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into fixed-size chunks with overlap (by characters)."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def chunk_paragraph(text, max_size=CHUNK_SIZE):
    """Split on double newlines (paragraphs). Merge short ones."""
    import re
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < max_size:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks

def build_index():
    """Build FAISS index from documents. Idempotent (no duplicates)."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Load file hashes for incremental/dedup
    manifest_path = os.path.join(RESULTS_DIR, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    
    # Find changed/new files
    changed_files = []
    for fname in sorted(os.listdir(DATA_DIR)):
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.isfile(fpath):
            current_hash = file_hash(fpath)
            if manifest.get(fname) != current_hash:
                changed_files.append(fname)
                manifest[fname] = current_hash
    
    if not changed_files and manifest:
        print(f"No changes detected. Index up to date. Unchanged files: {len(manifest)}")
        return
    
    # Load all docs
    docs = load_all_docs(DATA_DIR)
    
    # Build chunks with metadata
    all_chunks = []
    for doc in docs:
        # Use fixed chunking; you can switch to chunk_paragraph
        chunks = chunk_fixed(doc["text"], size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            # Dedup by text hash
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            chunk_id = f"{doc['source']}_p{doc['page']}_c{i}"
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "page": doc["page"],
                "chunk_id": chunk_id,
                "chunk_hash": chunk_hash
            })
    
    # Dedup: remove duplicate chunks
    seen_hashes = set()
    unique_chunks = []
    duplicates_skipped = 0
    for chunk in all_chunks:
        if chunk["chunk_hash"] not in seen_hashes:
            seen_hashes.add(chunk["chunk_hash"])
            unique_chunks.append(chunk)
        else:
            duplicates_skipped += 1
    
    print(f"Total chunks: {len(all_chunks)}, Unique: {len(unique_chunks)}, Duplicates skipped: {duplicates_skipped}")
    
    if not unique_chunks:
        print("No chunks to index.")
        return
    
    # Embed all unique chunks
    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in unique_chunks]
    print(f"Embedding {len(texts)} chunks using {MODEL_NAME}...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = embeddings.astype("float32")
    
    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner Product = cosine similarity (on normalized vectors)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    # Save index
    index_path = os.path.join(RESULTS_DIR, "faiss.index")
    faiss.write_index(index, index_path)
    print(f"Index built: {index.ntotal} vectors, dim={dim}. Saved to {index_path}")
    
    # Save chunk metadata
    metadata = []
    for c in unique_chunks:
        metadata.append({
            "text": c["text"],
            "source": c["source"],
            "page": c["page"],
            "chunk_id": c["chunk_id"]
        })
    
    metadata_path = os.path.join(RESULTS_DIR, "chunks_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {metadata_path}")
    
    # Save manifest for incremental re-indexing
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Total files processed: {len(set(d['source'] for d in [doc for doc in docs]))}")
    print(f"Index complete. Ready for retrieval.")

if __name__ == "__main__":
    build_index()