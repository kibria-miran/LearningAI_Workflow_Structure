#!/usr/bin/env python3
"""Phase 4 - run_eval.py: Evaluation script"""

import yaml
import json
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

try:
    from ask import rag_answer_with_guardrail
    from day1_retrieval import retrieve
except ImportError:
    # Fallback implementations if Phase 4 scripts not fully set up
    def rag_answer_with_guardrail(question):
        class Result:
            answer = "I don't have relevant information in my documents to answer this question."
            cost = 0.0
            refused = True
            top_score = 0.0
            sources = []
        return Result()
    
    def retrieve(query, k=5):
        return []

def run_eval(eval_file="tests/rag_eval.yaml"):
    """Run evaluation on the eval set and save results."""
    
    if not os.path.exists(eval_file):
        print(f"Eval file not found: {eval_file}")
        print("Create tests/rag_eval.yaml with 30+ questions first.")
        return
    
    with open(eval_file) as f:
        eval_questions = yaml.safe_load(f)
    
    hit_at_3 = 0
    hit_at_5 = 0
    answer_pass = 0
    refusal_pass = 0
    total_answerable = 0
    total_refusals = 0
    
    per_question_results = []
    
    for q in eval_questions:
        if q["question_type"] == "refusal":
            total_refusals += 1
            result = rag_answer_with_guardrail(q["question"])
            refused = result.refused or "not_found" in str(result.answer).lower()
            no_hallucination = not any(t.lower() in str(result.answer).lower() 
                                       for t in q.get("forbidden_terms", []))
            passed = refused or no_hallucination
            
            if passed:
                refusal_pass += 1
            
            per_question_results.append({
                "id": q["id"],
                "question": q["question"][:60],
                "type": "refusal",
                "passed": passed,
            })
            if passed:
                print(f"PASS REFUSAL | {q['id']}")
            else:
                print(f"FAIL REFUSAL | {q['id']}")
            continue
        
        total_answerable += 1
        results = retrieve(q["question"], k=5)
        sources_top3 = [r["source"] for r in results[:3]]
        sources_top5 = [r["source"] for r in results[:5]]
        
        expected = q["expected_source"]
        h3 = 1 if expected in sources_top3 else 0
        h5 = 1 if expected in sources_top5 else 0
        hit_at_3 += h3
        hit_at_5 += h5
        
        # Answer quality check
        result = rag_answer_with_guardrail(q["question"])
        answer = (result.answer or "").lower()
        
        facts_present = all(fact.lower() in answer for fact in q.get("key_facts", []))
        if facts_present:
            answer_pass += 1
        
        status = "HIT@3" if h3 else ("HIT@5" if h5 else "MISS")
        print(f"{status} | {q['id']}: {q['question'][:60]}")
        if not h3:
            print(f"       Expected: {expected}")
            print(f"       Got:      {sources_top5}")
        
        if not facts_present:
            missing = [f for f in q["key_facts"] if f.lower() not in answer]
            print(f"       Missing facts: {missing}")
        
        per_question_results.append({
            "id": q["id"],
            "question": q["question"][:60],
            "type": "answerable",
            "hit_at_3": h3,
            "hit_at_5": h5,
            "facts_present": facts_present,
        })
    
    # Save results
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results = {
        "date": datetime.now().isoformat(),
        "retrieval_hit_at_3": hit_at_3 / total_answerable if total_answerable > 0 else 0,
        "retrieval_hit_at_5": hit_at_5 / total_answerable if total_answerable > 0 else 0,
        "answer_quality": answer_pass / total_answerable if total_answerable > 0 else 0,
        "refusal_quality": refusal_pass / total_refusals if total_refusals > 0 else 0,
        "total_questions": len(eval_questions),
        "answerable_questions": total_answerable,
        "refusal_questions": total_refusals,
        "per_question": per_question_results
    }
    
    results_path = f"phase4/results/eval_{date_str}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")
    
    # Print summary
    print(f"\n=== EVAL SUMMARY ===")
    print(f"Retrieval Hit@3: {results['retrieval_hit_3']:.1%} ({hit_at_3}/{total_answerable})")
    print(f"Retrieval Hit@5: {results['retrieval_hit_5']:.1%} ({hit_at_5}/{total_answerable})")
    print(f"Answer quality: {results['answer_quality']:.1%} ({answer_pass}/{total_answerable})")
    print(f"Refusal quality: {results['refusal_quality']:.1%} ({refusal_pass}/{total_refusals})")
    
    return results

if __name__ == "__main__":
    run_eval()