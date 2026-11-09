================================================================
PHASE 3 — PROJECT STRUCTURE
================================================================

This file shows the complete folder structure you'll build
across Weeks 0–5. Reference it at the start of each week
to know where you are and what's coming.

phase3/
├── .env                        <- your API key (NEVER commit this)
├── .env.example                <- template showing required variables (commit this)
├── .gitignore                  <- must include .env and venv/
├── notes.md                    <- your learning journal, updated daily
├── README.md                   <- added in capstone week
│
├── config/
│   └── prices.json             <- DeepSeek token pricing (Week 2 D2)
│
├── tests/
│   ├── assertions.json         <- 10 programmatic tests (Week 2 D4)
│   └── evals.json              <- judgment questions reviewed weekly (Week 2 D4)
│
├── results
│   ├── usage.jsonl             <- every API call logged here (Week 2 D1)
│   └── 2026-10-13_14-22-01.json  <- dated test run results (Week 2 D5)
│
├── cli_chat.py                 <- multi-turn chatbot (Week 1 deliverable)
├── tracker.py                  <- wraps every API call, logs cost (Week 2 deliverable)
├── extractor.py                <- structured JSON extraction (Week 3 deliverable)
├── assistant.py                <- tool-calling agent (Week 4 deliverable)
├── run_tests.py                <- runs all assertions in one command (Week 2 D5)
├── weekly_self_check.py        <- regression guard: run at end of each week
└── phase4_outline.txt          <- Phase 4 curriculum preview (RAG, embeddings, multi-agent)

----------------------------------------------------------------
FILE PURPOSES AT A GLANCE
----------------------------------------------------------------

.env
  Contains: DEEPSEEK_API_KEY=sk-...
  Never committed. Listed in .gitignore.
  Verify: git log -p | grep "sk-" should return nothing.

.env.example
  Contains: DEEPSEEK_API_KEY=your_key_here
  Committed. Documents what variables are required.
  Anyone cloning your repo knows what to put in .env.

config/prices.json
  Contains: token costs per model.
  Update this whenever DeepSeek changes pricing.
  tracker.py reads this to calculate cost per call.

tests/assertions.json
  Contains: 10 test cases with check_type, prompt, system.
  run_tests.py reads this and runs all tests automatically.
  These are programmatic checks — pass or fail, no judgment.

tests/evals.json
  Contains: judgment questions you review weekly.
  Not run automatically. You open this file once a week,
  run each prompt manually, and record your assessment.

results/usage.jsonl
  Contains: one JSON line per API call.
  Every tracked_call() appends here.
  Use this to audit spending and debug failures.

results/DATE.json
  Contains: full results of one run_tests.py execution.
  Compare two dated files to see what a prompt change broke.

cli_chat.py
  A command-line chatbot. Maintains conversation history.
  Has a system prompt. Checks finish_reason.

tracker.py
  The central wrapper for all API calls.
  Logs: timestamp, model, prompt_hash, tokens, cost, latency, error.
  Enforces: daily and monthly budget caps.
  Handles: RateLimitError with exponential backoff.
  Accepts: tools= parameter for Week 4 tool calling.
  Provides: tracked_stream() for streaming calls (Week 3 D6).

extractor.py
  Takes messy text, returns validated JSON via Pydantic.
  Retries on parse failure (max 2 retries).
  Uses tracker.py for all API calls.

assistant.py
  A tool-calling agent for a real business task.
  Loop capped at 5 iterations.
  Uses safe_execute for error handling.
  Requires human approval for risky tools.
  Uses tracker.py for all API calls.

run_tests.py
  Reads tests / assertions.json.
  Runs each test via tracker.py.
  Prints PASS/FAIL for each.
  Saves results to results/DATE.json.
  Shows total cost at the end.

----------------------------------------------------------------
WHAT GETS BUILT EACH WEEK
----------------------------------------------------------------

Week 0: .env, .env.example, .gitignore, notes.md, venv
Week 1: cli_chat.py
Week 2: tracker.py, config/prices.json, run_tests.py,
        tests/assertions.json, tests/evals.json, results/
Week 3: extractor.py
Week 4: assistant.py (uses all of the above)
Week 5: README.md, capstone project

----------------------------------------------------------------
QUICK REFERENCE — COMMANDS
----------------------------------------------------------------

Setup (once):
  python -m venv venv && source venv/bin/activate
  pip install "openai>=1.40" python-dotenv pydantic requests

Daily:
  source venv/bin/activate
  git add . && git commit -m "week X dY: [what you did]"

Run tests:
  python run_tests.py

Check spending:
  cat results/usage.jsonl | python -c "
  import sys, json
  lines = [json.loads(l) for l in sys.stdin]
  total = sum(l['cost'] for l in lines)
  print(f'Total: \${total:.6f} across {len(lines)} calls')
  "

Verify no key in git history:
  git log -p | grep "sk-"

================================================================
