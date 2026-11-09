================================================================
PHASE 4 — PROJECT STRUCTURE
================================================================

phase4/
├── .env                        <- same API key as Phase 3
├── .gitignore                  <- includes .env, venv/, *.npy
├── notes.md                    <- learning journal, updated daily
│
├── data/                       <- your raw documents (PDF, TXT, MD)
│
├── config/
│   └── prices.json             <- reuse from Phase 3
│
├── src/
│   └── retrieve/               <- retrieval modules
│
├── tests/
│   └── rag_eval.yaml           <- 30+ eval questions with expected answers
│
├── results/
│   ├── embeddings.npy          <- all chunk embeddings
│   ├── faiss.index             <- FAISS vector index
│   ├── chunks_metadata.json    <- chunk text + source + page
│   ├── manifest.json           <- file hashes for incremental re-index
│   └── eval_DATE.json          <- dated eval run results
│
├── build_index.py              <- Week 1 deliverable: load, chunk, embed, index
├── ask.py                      <- Week 2 deliverable: CLI Q&A with sources
├── run_eval.py                 <- Week 3 deliverable: retrieval + answer eval
└── notes.md

----------------------------------------------------------------
WHAT GETS BUILT EACH WEEK
----------------------------------------------------------------

Week 0: data/, .env, notes.md, dependencies installed
Week 1: build_index.py, results/embeddings.npy, results/faiss.index
Week 2: ask.py (CLI Q&A with citations, multi-turn, guardrail)
Week 3: tests/rag_eval.yaml, run_eval.py, baseline scores
Week 4: hybrid retrieval (RRF), query expansion, chunk tuning
Week 5: reranker (optional), RAGAS eval, pipeline profiling
Week 6: incremental re-index, retry/fallback, 50-question eval

================================================================
