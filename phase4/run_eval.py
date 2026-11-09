#!/usr/bin/env python3
"""Phase 4 - run_eval.py: retrieval + answer eval.

Usage:
    python run_eval.py --retrieval-only     # free: hit@k only, no LLM calls
    python run_eval.py                      # full: retrieval + answers + refusals
    python run_eval.py --diff A.json B.json # compare two saved runs
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from src.retrieve import retrieve

EVAL_FILE = HERE / "tests" / "rag_eval.yaml"
RESULTS_DIR = HERE / "results"


def pct(a, b):
    return a / b if b else 0.0


def run_eval(retrieval_only=False):
    questions = yaml.safe_load(EVAL_FILE.read_text(encoding="utf-8"))
    if not retrieval_only:
        from ask import rag_answer
    answerable = [q for q in questions if q["question_type"] != "refusal"]
    refusals = [q for q in questions if q["question_type"] == "refusal"]

    rows, h3, h5, ans_ok, ref_ok, cost = [], 0, 0, 0, 0, 0.0

    for q in answerable:
        hits = retrieve(q["question"], k=5)
        srcs = [h["source"] for h in hits]
        a3, a5 = q["expected_source"] in srcs[:3], q["expected_source"] in srcs[:5]
        h3, h5 = h3 + a3, h5 + a5
        row = {"id": q["id"], "type": "answerable", "hit_at_3": a3, "hit_at_5": a5, "got": srcs[:5]}
        if not retrieval_only:
            r = rag_answer(q["question"])
            cost += r["cost"]
            text = r["answer"].lower()
            missing = [f for f in q["key_facts"] if f.lower() not in text]
            row.update(answer_ok=(not r["refused"] and not missing), missing=missing, refused=r["refused"])
            ans_ok += row["answer_ok"]
        rows.append(row)
        print(("HIT@3 " if a3 else "HIT@5 " if a5 else "MISS  ") + f"| {q['id']} {q['question'][:55]}"
              + ("" if a3 else f"  expected={q['expected_source']} got={srcs[:3]}")
              + (f"  missing={row.get('missing')}" if row.get("missing") else ""))

    if not retrieval_only:
        for q in refusals:
            r = rag_answer(q["question"])
            cost += r["cost"]
            leaked = [t for t in q.get("forbidden_terms", []) if t.lower() in r["answer"].lower()]
            ok = r["refused"] and not leaked          # must refuse AND not leak forbidden terms
            ref_ok += ok
            rows.append({"id": q["id"], "type": "refusal", "passed": ok, "top_score": round(r["top_score"], 3)})
            print(("PASS " if ok else "FAIL ") + f"REFUSAL | {q['id']} {q['question'][:50]} (top={r['top_score']:.2f})")

    summary = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "mode": "retrieval_only" if retrieval_only else "full",
        "hit_at_3": pct(h3, len(answerable)), "hit_at_5": pct(h5, len(answerable)),
        "answer_quality": None if retrieval_only else pct(ans_ok, len(answerable)),
        "refusal_quality": None if retrieval_only else pct(ref_ok, len(refusals)),
        "n_answerable": len(answerable), "n_refusal": len(refusals), "cost_usd": round(cost, 6),
        "per_question": rows,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"eval_{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== EVAL SUMMARY ===")
    print(f"Hit@3: {summary['hit_at_3']:.1%}   Hit@5: {summary['hit_at_5']:.1%}")
    if not retrieval_only:
        print(f"Answer quality: {summary['answer_quality']:.1%}   Refusal quality: {summary['refusal_quality']:.1%}")
        print(f"Cost: ${cost:.6f}")
    print(f"Saved: {out}")
    return summary


def diff(a_path, b_path):
    a, b = (json.loads(Path(p).read_text()) for p in (a_path, b_path))
    for k in ("hit_at_3", "hit_at_5", "answer_quality", "refusal_quality"):
        if a.get(k) is not None and b.get(k) is not None:
            print(f"{k:16} {a[k]:.1%} -> {b[k]:.1%}  ({b[k]-a[k]:+.1%})")
    ra = {r["id"]: r for r in a["per_question"]}
    for r in b["per_question"]:
        old = ra.get(r["id"])
        if old and old.get("hit_at_3") != r.get("hit_at_3") and "hit_at_3" in r:
            print(f"  {r['id']}: hit@3 {old.get('hit_at_3')} -> {r.get('hit_at_3')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval-only", action="store_true")
    ap.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"))
    args = ap.parse_args()
    diff(*args.diff) if args.diff else run_eval(args.retrieval_only)
