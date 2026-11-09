"""weekly_self_check.py - Phase 5 regression guard. Exit 0 = all pass."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PASS, FAIL = [], []


def check(name, fn):
    try:
        fn(); PASS.append(name); print(f"  PASS  {name}")
    except Exception as e:
        FAIL.append(name); print(f"  FAIL  {name} - {e}")


def agent_imports():
    import agent
    assert callable(agent.run_agent) and len(agent.TOOL_MAP) >= 3


def calculator_safe():
    import agent, json
    assert json.loads(agent.calculator("2+3*4"))["result"] == 14
    assert "error" in json.loads(agent.calculator("__import__('os')"))
    assert "error" in json.loads(agent.calculator("9**9**9"))


def read_file_locked():
    import agent, json
    assert "error" in json.loads(agent.read_file("../../etc/passwd"))


def guardrails_exist():
    import guardrails  # Week 3-4
    for n in ("LoopGuard", "RunBudget", "validate_call"):
        assert hasattr(guardrails, n), f"guardrails.{n} missing"


def failure_tests_pass():
    import subprocess
    r = subprocess.run([sys.executable, "tests/failure_cases.py"], cwd=HERE, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-300:] + r.stderr[-300:]


for n, f in [("W1 agent imports", agent_imports), ("W1 calculator safe", calculator_safe),
             ("W1 read_file locked to workspace", read_file_locked),
             ("W3 guardrails.py has core guards", guardrails_exist),
             ("W3 tests/failure_cases.py passes", failure_tests_pass)]:
    check(n, f)
print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
