# What was broken, what changed

## phase4
- run_eval.py: `sys` never imported; imported non-existent `day1_retrieval` / `rag_answer_with_guardrail`; silent ImportError fallback made every run "refused"; `.refused` on a dict; KeyError `retrieval_hit_3`; wrong results path. Rewritten (+ `--retrieval-only`, `--diff`).
- tests/rag_eval.yaml: 28 of 36 expected sources were .pdf files that do not exist (data/ has 5 .txt). Rebuilt: 28 answerable + 8 refusal, every source/key_fact verified against data/.
- ask.py: silent mock tracker returned NOT_FOUND; treated tracker result as object (it is a dict); model reloaded per question; unused citation function. Rewritten; model/index cached in src/retrieve/dense.py.
- build_index.py: manifest edited before success, deleted files undetected, normalize order, no --rebuild. Fixed.
- Added: requirements, .gitignore, .env.example, notes.md, weekly_self_check.py, accurate PROJECT_STRUCTURE.md.

## phase5
- agent.py: tracker not importable from phase5; search_docs called a non-existent function and a cwd-relative path; calculator used eval() (9**9**9 hangs); bad tool-arg JSON crashed the loop; success flag unchecked. Fixed (AST calculator, arg errors returned to the model).
- Added week3_4 ... week10 guides, PROJECT_STRUCTURE.md, weekly_self_check.py, folder skeleton.

## phase6
- Dockerfile copied only phase6 but app imports phase4 -> would crash; container ran `python app.py` which never starts a server; image tag typo `n8nnio`; n8n basic-auth env vars no longer exist; `deepseek` pip package is wrong (use openai); HTTPException(404) was swallowed into a 500; wildcard CORS + credentials; async endpoint blocking the event loop; no auth; no healthcheck/volumes. All fixed.
- Added stage A-E guides, start.sh, Dockerfile.dockerignore, PROJECT_STRUCTURE.md.

## phase7
- Added week1-6 guides, PROJECT_STRUCTURE.md; runbook rollback now uses git tags; config.json gains per-run budget.

## Not verified
Embedding model download and the DeepSeek API were not available here: pipeline logic was tested with a stub embedder and stub tracker. Run `python weekly_self_check.py` in phase4 on your machine.
