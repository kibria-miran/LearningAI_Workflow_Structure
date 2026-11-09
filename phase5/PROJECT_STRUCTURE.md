================================================================
PHASE 5 - PROJECT STRUCTURE
================================================================

Run scripts from INSIDE phase5/. agent.py imports tracker.py from
phase5/ or ../phase3/, and search_docs calls ../phase4 (build its
index first: cd ../phase4 && python build_index.py).

phase5/
├── .env / .env.example / .gitignore
├── requirements.txt
├── notes.md
│
├── agent.py                <- Week 1-2: hand-built loop (5 tools, step cap)
├── guardrails.py           <- Week 3-4: loop guard, validation, budget, ...
├── tools/                  <- Week 5: stub action tools (send_email, refund)
├── workspace/              <- the ONLY folder read_file/write_file can touch
│   ├── agent_notes.txt     <- remember()/recall() memory (gitignored)
│   └── outbox.jsonl        <- approved stub actions (gitignored)
├── tests/
│   └── failure_cases.py    <- Week 3-4: one test per guardrail
├── traces/                 <- Week 6: one JSONL per run (gitignored)
├── evals/
│   └── tasks.yaml          <- Week 6: 15-20 end-state tasks
├── run_agent_eval.py       <- Week 6
├── view_trace.py           <- Week 6
├── langgraph_version/      <- Week 8
├── mcp_server/             <- Week 9
└── weekly_self_check.py

----------------------------------------------------------------
WHAT GETS BUILT WHEN
----------------------------------------------------------------
Week 1-2 : agent.py (5 real tasks end to end)
Week 3-4 : guardrails.py + tests/failure_cases.py
Week 5   : risk tiers, approval, injection test
Week 6   : tracing + agent eval
Week 7   : ONE pattern, before/after numbers
Week 8   : same agent in LangGraph
Week 9   : MCP server + client
Week 10  : buffer

SAFETY DEFAULTS
  read_file is locked to workspace/ (basename only).
  calculator uses ast, never eval().
  Unknown tools default to highest risk tier.
================================================================
