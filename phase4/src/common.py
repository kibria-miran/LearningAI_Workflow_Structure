"""Shared helpers: locate Phase 3 tracker, fail loudly if missing."""
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent      # phase4/
ROOT = PHASE_DIR.parent                                  # folder holding phase3/, phase4/ ...


def load_tracker():
    """Return tracked_call from phase3/tracker.py. No silent mock."""
    for p in (PHASE_DIR, ROOT / "phase3"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    try:
        from tracker import tracked_call
    except ImportError as e:
        raise SystemExit(
            "Cannot import tracker.py. Put it in phase4/ or keep it in ../phase3/.\n"
            f"Original error: {e}"
        )
    return tracked_call
