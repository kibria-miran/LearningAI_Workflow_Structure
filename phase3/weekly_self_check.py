"""
weekly_self_check.py — Phase 3 regression guard.

Run at the end of each week to confirm earlier deliverables
still work. A failure here means you broke something upstream
while building the current week.

Usage:
    python weekly_self_check.py

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""

import sys
import os
import importlib
import json

PASS = []
FAIL = []

def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"  PASS  {name}")
    except Exception as e:
        FAIL.append(name)
        print(f"  FAIL  {name} — {e}")


# ── W1: cli_chat.py importable ────────────────────────────────
def w1_cli_chat_importable():
    spec = importlib.util.find_spec("cli_chat")
    if spec is None:
        raise ImportError("cli_chat.py not found in current directory")

check("W1 cli_chat.py exists and is importable", w1_cli_chat_importable)


# ── W2: tracker.tracked_call callable ────────────────────────
def w2_tracker_importable():
    import tracker
    assert callable(tracker.tracked_call), "tracked_call is not callable"

check("W2 tracker.tracked_call is callable", w2_tracker_importable)


def w2_budget_cap_exists():
    import tracker
    assert hasattr(tracker, "DAILY_BUDGET_USD"),  "DAILY_BUDGET_USD missing from tracker"
    assert hasattr(tracker, "MONTHLY_BUDGET_USD"), "MONTHLY_BUDGET_USD missing from tracker"
    assert tracker.DAILY_BUDGET_USD > 0
    assert tracker.MONTHLY_BUDGET_USD > 0

check("W2 budget caps defined in tracker", w2_budget_cap_exists)


def w2_usage_log_exists():
    assert os.path.exists("results/usage.jsonl"), \
        "results/usage.jsonl not found — has tracker.py been used yet?"

check("W2 results/usage.jsonl exists", w2_usage_log_exists)


def w2_run_tests_exits_zero():
    import subprocess
    result = subprocess.run(
        [sys.executable, "run_tests.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"run_tests.py exited {result.returncode}\n"
            f"stdout: {result.stdout[-300:]}\n"
            f"stderr: {result.stderr[-300:]}"
        )

check("W2 run_tests.py exits 0", w2_run_tests_exits_zero)


# ── W3: extractor.extract_order works on one sample ──────────
def w3_extractor_works():
    from extractor import extract_order
    result = extract_order("Order #4521 placed by John for $45.99. Item: Blue Hoodie.")
    assert result["success"], f"extract_order failed: {result['error']}"
    assert result["data"] is not None

check("W3 extractor.extract_order works on 1 sample", w3_extractor_works)


# ── W4: assistant.run_agent works on 1 sample ────────────────
def w4_assistant_works():
    from assistant import run_agent
    result = run_agent("What is the status of order 4521?")
    # run_agent returns a dict with success key
    assert isinstance(result, dict), "run_agent must return a dict"
    assert "success" in result, "run_agent dict missing 'success' key"
    assert result["success"], f"run_agent returned failure: {result.get('error')}"

check("W4 assistant.run_agent works on 1 sample", w4_assistant_works)


# ── Summary ───────────────────────────────────────────────────
print()
print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")

if FAIL:
    print("\nFailed checks:")
    for name in FAIL:
        print(f"  - {name}")
    print("\nFix the failures above before continuing to the next week.")
    sys.exit(1)

print("All checks passed. Earlier deliverables are intact.")
sys.exit(0)
