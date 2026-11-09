"""
weekly_self_check.py - Phase 4 regression guard. Run at the end of each week.
Exit 0 = all pass, 1 = something broke.
Usage: python weekly_self_check.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"  PASS  {name}")
    except Exception as e:
        FAIL.append(name)
        print(f"  FAIL  {name} - {e}")


def w1_data_present():
    files = [p for p in (HERE / "data").glob("*") if p.suffix in (".txt", ".md", ".pdf")]
    assert files, "data/ is empty"


def w1_index_built():
    for f in ("faiss.index", "chunks_metadata.json", "manifest.json"):
        assert (HERE / "results" / f).exists(), f"results/{f} missing - run build_index.py"
    import faiss
    idx = faiss.read_index(str(HERE / "results" / "faiss.index"))
    meta = json.loads((HERE / "results" / "chunks_metadata.json").read_text())
    assert idx.ntotal == len(meta), f"index {idx.ntotal} != metadata {len(meta)}"
    ids = [m["chunk_id"] for m in meta]
    assert len(ids) == len(set(ids)), "duplicate chunk_ids"


def w2_retrieve_works():
    from src.retrieve import retrieve
    r = retrieve("refund policy", k=3)
    assert r and "score" in r[0] and "source" in r[0]


def w2_ask_importable():
    import ask
    assert callable(ask.rag_answer)


def w3_eval_valid():
    import yaml
    qs = yaml.safe_load((HERE / "tests" / "rag_eval.yaml").read_text())
    assert len(qs) >= 30, f"only {len(qs)} questions"
    assert sum(q["question_type"] == "refusal" for q in qs) >= 5, "need 5+ refusal questions"
    for q in qs:
        if q["question_type"] != "refusal":
            assert (HERE / "data" / q["expected_source"]).exists(), f"{q['id']}: {q['expected_source']} not in data/"


def w3_baseline_saved():
    assert list((HERE / "results").glob("eval_*.json")), "no eval run saved - run run_eval.py"


for n, f in [("W1 data/ has documents", w1_data_present), ("W1 index built, consistent", w1_index_built),
             ("W2 retrieve() works", w2_retrieve_works), ("W2 ask.rag_answer importable", w2_ask_importable),
             ("W3 eval set valid (30+, 5+ refusals, sources exist)", w3_eval_valid),
             ("W3 baseline eval saved", w3_baseline_saved)]:
    check(n, f)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
