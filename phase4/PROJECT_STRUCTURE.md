================================================================
PHASE 4 - PROJECT STRUCTURE
================================================================

Run every script from INSIDE phase4/ (cd phase4). tracker.py is
imported from phase4/ or ../phase3/ - it is never copied or mocked.

phase4/
├── .env                        <- same API key as Phase 3 (NEVER commit)
├── .env.example                <- template (commit)
├── .gitignore                  <- .env, venv/, __pycache__/, *.index, *.npy
├── requirements.txt
├── notes.md                    <- learning journal, updated daily
│
├── data/                       <- raw docs (.txt .md .pdf), 20-50 real files
├── src/
│   ├── common.py               <- finds phase3 tracker, fails loudly if absent
│   └── retrieve/
│       ├── dense.py            <- retrieve(query, k): cached model + FAISS
│       └── __init__.py         <- Week 4 adds hybrid.py (BM25 + RRF) here
├── tests/
│   └── rag_eval.yaml           <- 30+ questions, 5+ refusals (Week 3)
├── results/                    <- generated, do not hand-edit
│   ├── faiss.index
│   ├── chunks_metadata.json    <- chunk text + source + page + chunk_id
│   ├── manifest.json           <- file hashes (skip rebuild when unchanged)
│   └── eval_DATE.json          <- one file per eval run
│
├── build_index.py              <- Week 1: load, chunk, embed, index
├── ask.py                      <- Week 2: CLI Q&A, citations, refusal guardrail
├── run_eval.py                 <- Week 3: hit@k, answers, refusals, --diff
└── weekly_self_check.py        <- regression guard, run end of each week

NOTE ON GUIDE FILENAMES
  The week guides tell you to write scratch files named
  day1_retrieval.py and day2_first_rag.py. Those are practice files.
  The finished versions live in src/retrieve/dense.py and ask.py
  (ask.rag_answer_with_guardrail is the same function as rag_answer).
  The guides save embeddings.npy; the final build_index.py does not
  need it (FAISS holds the vectors).

----------------------------------------------------------------
WHAT GETS BUILT EACH WEEK
----------------------------------------------------------------
Week 0: venv, deps, data/, notes.md
Week 1: build_index.py -> results/faiss.index, chunks_metadata.json
Week 2: ask.py (citations, multi-turn, streaming, guardrail)
Week 3: tests/rag_eval.yaml, run_eval.py, baseline numbers
Week 4: src/retrieve/hybrid.py (BM25 + RRF), query rewriting
Week 5: reranker (keep only if eval improves), RAGAS, profiling
Week 6: incremental re-index, retry/fallback, 50-question eval

----------------------------------------------------------------
QUICK REFERENCE
----------------------------------------------------------------
  python build_index.py [--rebuild]
  python ask.py
  python run_eval.py --retrieval-only     # free, no LLM calls
  python run_eval.py                      # full run, saves results/eval_*.json
  python run_eval.py --diff results/A.json results/B.json
  python weekly_self_check.py

KNOWN LIMIT
  The sample data/ has 5 tiny files (6 chunks), so hit@k is easy.
  Replace them with 20-50 of YOUR real docs and rewrite
  tests/rag_eval.yaml for them before trusting any score.
================================================================
