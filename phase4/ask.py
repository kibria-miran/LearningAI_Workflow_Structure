#!/usr/bin/env python3
"""Phase 4 - ask.py: CLI Q&A with sources + refusal guardrail."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.common import load_tracker
from src.retrieve import retrieve, SIMILARITY_THRESHOLD

tracked_call = load_tracker()

NOT_FOUND = "NOT_FOUND"
REFUSAL_TEXT = "I don't have relevant information in my documents to answer this question."

RAG_SYSTEM = f"""You are a document Q&A assistant.
Answer ONLY from the context provided in the user message.
If the answer is not in the context, reply with exactly: {NOT_FOUND}
Never use outside knowledge. Never invent details. Be concise."""


def _refusal(top_score, chunks=()):
    return {"answer": REFUSAL_TEXT, "sources": [], "cost": 0.0, "refused": True,
            "top_score": top_score, "chunks": list(chunks)}


def rag_answer(question: str, k: int = 4) -> dict:
    """Return dict: answer, sources, cost, refused, top_score, chunks."""
    chunks = retrieve(question, k=k)
    top = chunks[0]["score"] if chunks else 0.0
    if top < SIMILARITY_THRESHOLD:                       # guardrail: no LLM call, no cost
        return _refusal(top, chunks)

    context = "\n\n---\n\n".join(f"[Source: {c['source']} p{c['page']}]\n{c['text']}" for c in chunks)
    res = tracked_call([
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ])
    if not res.get("success") or res.get("finish_reason") != "stop":
        raise RuntimeError(f"LLM call failed: error={res.get('error')} finish={res.get('finish_reason')}")

    answer = (res["content"] or "").strip()
    if NOT_FOUND in answer.upper():                      # model itself says no evidence
        out = _refusal(top, chunks)
        out["cost"] = res.get("cost", 0.0)
        return out

    seen, sources = set(), []
    for c in chunks:
        key = (c["source"], c["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"source": c["source"], "page": c["page"], "score": round(c["score"], 3)})
    return {"answer": answer, "sources": sources, "cost": res.get("cost", 0.0),
            "refused": False, "top_score": top, "chunks": chunks}


rag_answer_with_guardrail = rag_answer   # name used in the week guides


def main():
    print("RAG Q&A  (type 'quit' to exit)")
    total = 0.0
    while True:
        try:
            q = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue
        r = rag_answer(q)
        total += r["cost"]
        print("\nAnswer:", r["answer"])
        if r["sources"]:
            print("Sources:", " | ".join(f"{s['source']} p{s['page']}" for s in r["sources"]))
        print(f"(top_score={r['top_score']:.2f}  cost=${r['cost']:.6f}  session=${total:.6f})")


if __name__ == "__main__":
    main()
