#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. MIT.
"""Grok Stop hook: run vbd_gate when the agent tries to finish a turn.

You do not run this. Grok does, on Stop (end of a completed turn).
Exit 2 + JSON block keeps the agent working until the gates pass, or until
the host's continuation limit. Untracked finish-later files are ignored.
A clean tree (no tracked edits) is a pass, so Q&A is not blocked.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
from vbd_gate import run_checks  # noqa: E402


def main() -> int:
    raw = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except ValueError:
        payload = {}
    reason = str(payload.get("reason") or payload.get("stopReason") or "end_turn")
    if reason not in ("end_turn", ""):
        return 0
    if payload.get("stopHookActive"):
        # One forced retry already happened. Do not lock the turn for 8 rounds
        # on finish-later dirt. Pre-push still blocks a forgotten ship.
        return 0
    root = Path(payload.get("workspaceRoot") or payload.get("cwd") or ".").resolve()
    errs = run_checks(root, tracked_only=True, skip_if_clean=True)
    if not errs:
        return 0
    msg = "vbd_gate failed; do not claim done.\n" + "\n".join("  " + e for e in errs)
    sys.stderr.write(msg + "\n")
    sys.stdout.write(
        json.dumps({"decision": "block", "reason": msg}, ensure_ascii=True) + "\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
