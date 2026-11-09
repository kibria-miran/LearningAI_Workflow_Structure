#!/usr/bin/env python3
"""Phase 4 - ask.py: CLI Q&A with sources"""

import os
import json
import sys
from pathlib import Path

# Add phase4 to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from tracker import tracked_call  # Phase 3 tracker
except ImportError:
    # Mock tracker if Phase 3 not set up
    class TrackedResult:
        def __init__(self, content, cost=0.0):
            self.content = content
            self.cost = cost
    def tracked_call(messages, model="deepseek-chat", **kwargs):
        # Simple mock - in real usage, this calls the LLM API
        class Result:
            content = "NOT_FOUND"
            cost = 0.0
        return Result()

# RAG system prompt
RAG_SYSTEM = """You are a document Q&A assistant.
Answer the user's question using ONLY the context below.
If the answer is not present in the context, respond with exactly: NOT_FOUND
Do not use any knowledge outside the provided context.
Do not make up information."""

SIMILARITY_THRESHOLD = 0.3

def retrieve(query, k=5):
    """Retrieve top-k chunks from FAISS index."""
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    
    index_path = os.path.join(os.path.dirname(__file__), "results", "faiss.index")
    metadata_path = os.path.join(os.path.dirname(__file__), "results", "chunks_metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        return []
    
    index = faiss.read_index(index_path)
    with open(metadata_path) as f:
        chunks = json.load(f)
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vec = model.encode([query]).astype("float32")
    faiss.normalize_L2(vec)
    scores, indices = index.search(vec, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)
    return results

def rag_answer(question, k=4):
    """Get RAG answer with citations."""
    chunks = retrieve(question, k=k)
    top_score = chunks[0]["score"] if chunks else 0.0
    
    # Refusal guardrail
    if top_score < SIMILARITY_THRESHOLD:
        return {
            "answer": "I don't have relevant information in my documents to answer this question.",
            "sources": [],
            "cost": 0.0,
            "refused": True,
            "top_score": top_score
        }
    
    context = "\n\n---\n\n".join(
        f"[Source: {c['source']} p{c['page']}]\n{c['text']}"
        for c in chunks
    )
    messages = [
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]
    result = tracked_call(messages)
    return {
        "answer": result.content if hasattr(result, 'content') else str(result),
        "sources": [{"source": c["source"], "page": c["page"], "score": c["score"]} for c in chunks],
        "cost": getattr(result, 'cost', 0.0),
        "refused": False,
        "top_score": top_score
    }

def format_answer_with_citations(answer, chunks):
    """Append source citations to the answer."""
    if answer.strip() == "NOT_FOUND" or answer.strip() == "I don't have relevant information in my documents to answer this question.":
        return "NOT_FOUND — no relevant information in the documents."
    sources = []
    seen = set()
    for c in chunks:
        key = f"{c['source']} p{c['page']}"
        if key not in seen and c["score"] > 0.3:
            sources.append(key)
            seen.add(key)
    citation_block = "\n\nSources: " + " | ".join(sources) if sources else ""
    return answer + citation_block

def main():
    """CLI loop for Q&A."""
    print("=" * 60)
    print("RAG CLI Q&A Tool")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        question = input("\nEnter your question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        result = rag_answer(question)
        
        print("\n" + "=" * 60)
        print("Answer:", result["answer"])
        if result["sources"]:
            print("Sources:", " | ".join([f"{s['source']} p{s['page']}" for s in result["sources"]]))
        if result["cost"] > 0:
            print(f"Cost: ${result['cost']:.6f}")
        if result.get("refused"):
            print("(Answer refused due to low similarity score)")
        print("=" * 60)

if __name__ == "__main__":
    main()