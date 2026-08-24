#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. MIT.
"""Verify-before-done gates: checks an agent (or you) can forget.

Prose VBD cannot see a phone or remember to fetch. This command fails closed
on the repeatable misses. Judgment (quality bar, honest residuals) stays prose.

  python3 vbd_gate.py check --app-root DIR
  python3 vbd_gate.py check --app-root DIR --claim-done --not-promoted 'unique to this product'
  python3 vbd_gate.py hook-install --app-root DIR

If DIR/vbd.runtime.json exists, --claim-done and pre-push run those argv
commands (cwd is DIR, no shell). Plain check does not, unless --with-runtime.
The Stop hook never runs them. Missing file is skip, not fail.

Each run appends one JSON line to ~/.grok/logs/vbd_gate.jsonl (VBD_GATE_LOG).
Exit 0 pass, 2 fail. Does not discard local work. Does not pull.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

PACK_ROOT = Path(__file__).resolve().parent
HOOK_MARK = "vbd-gate-pre-push"
RUNTIME_FILE = "vbd.runtime.json"
RUNTIME_TIMEOUT_DEFAULT = 120
RUNTIME_TIMEOUT_CAP = 600
DASH_CHARS = ("\u2014", "\u2013")
UI_SUFFIX = {".html", ".css"}
PROSE_SUFFIX = {".md", ".txt", ".html"}
DASH_ALLOW = {"VERIFY_BEFORE_DONE.md", "punctuation-lists.md"}
SKIP_CLASS = "skip-juicy"
CHART_HINT = re.compile(r"(chart-wrap|chart_wrap)", re.I)
RUNTIME_ITEM_KEYS = {"id", "argv", "timeout_s", "paths"}


class _SkipParser(HTMLParser):
    """Collect every .skip-juicy hash href and whether each landing id is a chart wrap."""

    def __init__(self, skip_class: str) -> None:
        super().__init__()
        self.skip_class = skip_class
        self.hrefs: List[str] = []
        self.targets: Dict[str, Tuple[bool, bool]] = {}
        self._stack: List[Tuple[str, Optional[str], Set[str]]] = []
        self._open_ids: List[Tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        classes = set((ad.get("class") or "").split())
        eid = ad.get("id") or None
        self._stack.append((tag, eid, classes))
        if tag == "a" and self.skip_class in classes:
            href = ad.get("href") or ""
            if href.startswith("#") and len(href) > 1:
                self.hrefs.append(href)
        class_blob = ad.get("class") or ""
        is_chart = "chart-wrap" in classes or bool(CHART_HINT.search(class_blob))
        is_visual = is_chart or tag == "canvas" or bool(
            CHART_HINT.search(class_blob + " " + (eid or ""))
        )
        if eid:
            was_chart, was_contains = self.targets.get(eid, (False, False))
            self.targets[eid] = (was_chart or is_chart, was_contains)
            self._open_ids.append((eid, len(self._stack)))
        if is_visual:
            for tid, _depth in self._open_ids:
                is_chart_tid, contains_tid = self.targets.get(tid, (False, False))
                if eid == tid and is_chart:
                    self.targets[tid] = (True, contains_tid)
                else:
                    self.targets[tid] = (is_chart_tid, True)

    def handle_endtag(self, tag: str) -> None:
        if self._stack:
            self._stack.pop()
        depth = len(self._stack)
        self._open_ids = [(tid, d) for tid, d in self._open_ids if d <= depth]


def skip_landing_errors(html: str) -> List[str]:
    """Fail if any skip jump lands on a section that *contains* the chart."""
    p = _SkipParser(SKIP_CLASS)
    try:
        p.feed(html)
    except Exception as exc:
        return ["html parse failed: {0}".format(exc)]
    errs: List[str] = []
    seen: Set[str] = set()
    for href in p.hrefs:
        if href in seen:
            continue
        seen.add(href)
        meta = p.targets.get(href[1:])
        if not meta:
            continue
        is_chart, contains_chart = meta
        if contains_chart and not is_chart:
            errs.append(
                "skip {0} lands on a section that contains a chart; "
                "point href at the visual target (the chart wrap), not the panel".format(href)
            )
    return errs


def _git(root: Path, args: Sequence[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=check,
    )


def is_git(root: Path) -> bool:
    return (root / ".git").exists() or _git(root, ["rev-parse", "--is-inside-work-tree"]).returncode == 0


def git_fetch(root: Path) -> Optional[str]:
    proc = _git(root, ["fetch"])
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if "No remote" in err or "does not appear to be a git repository" in err:
            return None
        return "git fetch failed: {0}".format(err or proc.returncode)
    return None


def origin_ahead_errors(root: Path) -> List[str]:
    up = _git(root, ["rev-parse", "--abbrev-ref", "@{upstream}"])
    if up.returncode != 0:
        return []
    counts = _git(root, ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
    if counts.returncode != 0:
        return []
    parts = (counts.stdout or "0\t0").strip().split()
    behind = int(parts[1]) if len(parts) > 1 else 0
    if behind <= 0:
        return []
    dirty = _git(root, ["status", "--porcelain"])
    dirty_n = len([ln for ln in (dirty.stdout or "").splitlines() if ln.strip()])
    if dirty_n:
        return [
            "origin is ahead ({0} commit(s)) and the tree is dirty; "
            "stash, commit, or report both; do not discard or reset --hard".format(behind)
        ]
    return [
        "origin is ahead ({0} commit(s)) and the tree is clean; pull before claiming done".format(
            behind
        )
    ]


def changed_paths(
    root: Path,
    *,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    tracked_only: bool = False,
) -> List[Path]:
    names: Set[str] = set()
    if from_ref and to_ref and to_ref != "0" * 40:
        if from_ref == "0" * 40:
            diff = _git(root, ["diff", "--name-only", to_ref])
        else:
            diff = _git(root, ["diff", "--name-only", from_ref, to_ref])
        names.update(ln.strip() for ln in (diff.stdout or "").splitlines() if ln.strip())
    else:
        cmds = (
            ["diff", "--name-only", "HEAD"],
            ["diff", "--cached", "--name-only"],
        )
        if not tracked_only:
            cmds = cmds + (["ls-files", "--others", "--exclude-standard"],)
        for args in cmds:
            proc = _git(root, args)
            names.update(ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip())
    out: List[Path] = []
    for n in sorted(names):
        p = root / n
        if p.is_file():
            out.append(p)
    return out


def _added_lines(root: Path, path: Path, from_ref: Optional[str], to_ref: Optional[str]) -> Optional[str]:
    """Return added text if a git diff is available; None means scan the whole file."""
    try:
        rel = str(path.relative_to(root))
    except ValueError:
        return None
    if from_ref and to_ref and to_ref != "0" * 40:
        args = ["diff", "-U0", from_ref, to_ref, "--", rel]
    else:
        tracked = _git(root, ["ls-files", "--", rel])
        if not (tracked.stdout or "").strip():
            return None
        args = ["diff", "-U0", "HEAD", "--", rel]
    proc = _git(root, args)
    if proc.returncode != 0:
        return None
    added = [
        ln[1:]
        for ln in (proc.stdout or "").splitlines()
        if ln.startswith("+") and not ln.startswith("+++")
    ]
    return "\n".join(added)


def dash_errors(
    paths: Iterable[Path],
    *,
    root: Optional[Path] = None,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
) -> List[str]:
    errs: List[str] = []
    for p in paths:
        if p.suffix.lower() not in PROSE_SUFFIX:
            continue
        if p.name in DASH_ALLOW:
            continue
        text: Optional[str] = None
        if root is not None:
            text = _added_lines(root, p, from_ref, to_ref)
        if text is None:
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
        for i, line in enumerate(text.splitlines(), 1):
            if _line_has_bad_dash(line):
                errs.append("{0}:{1}: decorative em/en dash".format(p, i))
                break
    return errs


def _line_has_bad_dash(line: str) -> bool:
    """Fail decorative list/apposition dashes; allow ironic cut-off em dashes.

    Allowed: Friday—actually (letter/word cut-off, no spaces around U+2014).
    Banned: Term — definition (space-dash-space) and any U+2013.
    """
    if "\u2013" in line:
        return True
    if "\u2014" not in line:
        return False
    if re.search(r"\s\u2014\s", line):
        return True
    for m in re.finditer("\u2014", line):
        i = m.start()
        left = line[i - 1] if i > 0 else ""
        right = line[i + 1] if i + 1 < len(line) else ""
        if not (left.isalnum() and right.isalnum()):
            return True
    return False


def skip_path_errors(paths: Iterable[Path]) -> List[str]:
    errs: List[str] = []
    for p in paths:
        if p.suffix.lower() != ".html":
            continue
        try:
            html = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for e in skip_landing_errors(html):
            errs.append("{0}: {1}".format(p, e))
    return errs


def viewport_errors(root: Path, paths: Iterable[Path]) -> List[str]:
    ui = [p for p in paths if p.suffix.lower() in UI_SUFFIX]
    if not ui:
        return []
    vs = root / "viewer" / "scripts" / "viewport_sanity.py"
    if not vs.is_file():
        return []
    proc = subprocess.run(
        [sys.executable, str(vs)],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    return [
        "viewport_sanity exit {0}: {1}".format(
            proc.returncode, " | ".join(tail[-5:]) or "no output"
        )
    ]


def _as_text(blob: Any) -> str:
    if blob is None:
        return ""
    if isinstance(blob, bytes):
        return blob.decode("utf-8", errors="replace")
    return str(blob)


def _output_tail(*chunks: Any, n: int = 5) -> str:
    text = "\n".join(_as_text(c) for c in chunks if c)
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return " | ".join(lines[-n:])


def load_runtime_config(
    root: Path,
) -> Tuple[Optional[List[Dict[str, Any]]], List[str]]:
    """Parse vbd.runtime.json. None checks means the file is absent (skip)."""
    path = root / RUNTIME_FILE
    if not path.is_file():
        return None, []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, ["{0}: invalid JSON: {1}".format(RUNTIME_FILE, exc)]
    if not isinstance(raw, dict):
        return None, ["{0}: root must be an object".format(RUNTIME_FILE)]
    extra = set(raw.keys()) - {"runtime_checks"}
    if extra:
        return None, [
            "{0}: unknown keys: {1}".format(RUNTIME_FILE, ", ".join(sorted(extra)))
        ]
    if "runtime_checks" not in raw:
        return None, ["{0}: missing runtime_checks".format(RUNTIME_FILE)]
    items = raw["runtime_checks"]
    if not isinstance(items, list):
        return None, ["{0}: runtime_checks must be an array".format(RUNTIME_FILE)]
    checks: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for i, item in enumerate(items):
        prefix = "{0}: runtime_checks[{1}]".format(RUNTIME_FILE, i)
        if not isinstance(item, dict):
            return None, ["{0}: must be an object".format(prefix)]
        unknown = set(item.keys()) - RUNTIME_ITEM_KEYS
        if unknown:
            return None, [
                "{0}: unknown keys: {1}".format(prefix, ", ".join(sorted(unknown)))
            ]
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip():
            return None, ["{0}: id must be a nonempty string".format(prefix)]
        ident = ident.strip()
        if ident in seen:
            return None, ["{0}: duplicate id {1!r}".format(prefix, ident)]
        seen.add(ident)
        argv = item.get("argv")
        if isinstance(argv, str):
            return None, [
                "{0}: argv must be an array of strings, not a shell string".format(
                    prefix
                )
            ]
        if not isinstance(argv, list) or not argv:
            return None, ["{0}: argv must be a nonempty array of strings".format(prefix)]
        if not all(isinstance(a, str) and a != "" for a in argv):
            return None, ["{0}: argv entries must be nonempty strings".format(prefix)]
        timeout_s: float = float(RUNTIME_TIMEOUT_DEFAULT)
        if "timeout_s" in item:
            ts = item["timeout_s"]
            if isinstance(ts, bool) or not isinstance(ts, (int, float)):
                return None, ["{0}: timeout_s must be a positive number".format(prefix)]
            timeout_s = float(ts)
            if timeout_s <= 0:
                return None, ["{0}: timeout_s must be a positive number".format(prefix)]
            if timeout_s > RUNTIME_TIMEOUT_CAP:
                return None, [
                    "{0}: timeout_s {1} exceeds cap {2}".format(
                        prefix, timeout_s, RUNTIME_TIMEOUT_CAP
                    )
                ]
        path_globs: List[str] = []
        if "paths" in item:
            raw_paths = item["paths"]
            if isinstance(raw_paths, str):
                return None, [
                    "{0}: paths must be an array of glob strings, not a string".format(
                        prefix
                    )
                ]
            if not isinstance(raw_paths, list) or not raw_paths:
                return None, [
                    "{0}: paths must be a nonempty array of glob strings".format(prefix)
                ]
            if not all(isinstance(p, str) and p.strip() for p in raw_paths):
                return None, [
                    "{0}: paths entries must be nonempty strings".format(prefix)
                ]
            path_globs = [p.replace("\\", "/").strip() for p in raw_paths]
        checks.append(
            {
                "id": ident,
                "argv": list(argv),
                "timeout_s": timeout_s,
                "paths": path_globs,
            }
        )
    return checks, []


def _run_one_runtime(
    root: Path, spec: Dict[str, Any]
) -> Tuple[List[str], Dict[str, Any]]:
    ident = spec["id"]
    name = "runtime:{0}".format(ident)
    argv = spec["argv"]
    timeout_s = spec["timeout_s"]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        msg = "{0}: command not found: {1}".format(name, argv[0])
        return [msg], _gate(name, [msg])
    except OSError as exc:
        msg = "{0}: cannot execute {1}: {2}".format(name, argv[0], exc)
        return [msg], _gate(name, [msg])
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - t0
        tail = _output_tail(exc.stdout, exc.stderr)
        msg = "{0}: timeout after {1:.1f}s (limit {2}s){3}".format(
            name,
            elapsed,
            timeout_s,
            (": " + tail) if tail else "",
        )
        return [msg], _gate(name, [msg])
    elapsed = time.monotonic() - t0
    if proc.returncode == 0:
        detail = "exit 0 in {0:.1f}s".format(elapsed)
        return [], _gate(name, [], detail=detail)
    tail = _output_tail(proc.stdout, proc.stderr)
    msg = "{0}: exit {1} in {2:.1f}s{3}".format(
        name,
        proc.returncode,
        elapsed,
        (": " + tail) if tail else "",
    )
    return [msg], _gate(name, [msg])


def _glob_re(pat: str) -> re.Pattern:
    """Translate a POSIX glob with ** to a fullmatch regex."""
    i = 0
    out: List[str] = []
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if pat.startswith("**", i) and (i + 2 == len(pat) or pat[i + 2] != "*"):
            out.append(".*")
            i += 2
            continue
        c = pat[i]
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(out) + "$")


def rel_glob_match(rel: str, pattern: str) -> bool:
    """True if repo-relative path matches a glob. `src/**` is the whole tree under src."""
    rel = rel.replace("\\", "/").lstrip("./")
    pat = pattern.replace("\\", "/").lstrip("./")
    if not rel or not pat:
        return False
    if rel == pat:
        return True
    if pat == "**" or pat == "**/**":
        return True
    if pat.endswith("/**"):
        prefix = pat[:-3]
        if prefix == "":
            return True
        return rel == prefix or rel.startswith(prefix + "/")
    return _glob_re(pat).fullmatch(rel) is not None


def any_path_match(rels: Sequence[str], globs: Sequence[str]) -> bool:
    return any(rel_glob_match(rel, g) for rel in rels for g in globs)


def touch_rel_paths(
    root: Path,
    *,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
) -> List[str]:
    """Dirty/untracked paths, plus unpublished commits vs upstream when no refs."""
    names: Set[str] = set()
    for p in changed_paths(root, from_ref=from_ref, to_ref=to_ref):
        try:
            names.add(str(p.relative_to(root)).replace("\\", "/"))
        except ValueError:
            names.add(p.name)
    if from_ref and to_ref:
        return sorted(names)
    if is_git(root):
        up = _git(root, ["rev-parse", "--abbrev-ref", "@{upstream}"])
        if up.returncode == 0:
            diff = _git(root, ["diff", "--name-only", "@{upstream}...HEAD"])
            names.update(
                ln.strip().replace("\\", "/")
                for ln in (diff.stdout or "").splitlines()
                if ln.strip()
            )
    return sorted(names)


def runtime_errors(
    root: Path,
    *,
    touch_rels: Optional[Sequence[str]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Execute vbd.runtime.json argv lists. Missing file skips.

    A check with `paths` globs runs only when a touched path matches.
    No `paths` key: always run (the pack's own tests).
    """
    checks, cfg_errs = load_runtime_config(root)
    if cfg_errs:
        return cfg_errs, [_gate("runtime", cfg_errs)]
    if checks is None:
        return [], [
            _gate("runtime", [], skipped=True, detail="no {0}".format(RUNTIME_FILE))
        ]
    if not checks:
        return [], [_gate("runtime", [], skipped=True, detail="empty runtime_checks")]
    rels = list(touch_rels) if touch_rels is not None else touch_rel_paths(root)
    errs: List[str] = []
    gates: List[Dict[str, Any]] = []
    for spec in checks:
        globs = spec.get("paths") or []
        name = "runtime:{0}".format(spec["id"])
        if globs and not any_path_match(rels, globs):
            gates.append(
                _gate(name, [], skipped=True, detail="no matching paths")
            )
            continue
        more, rec = _run_one_runtime(root, spec)
        errs.extend(more)
        gates.append(rec)
    return errs, gates


def _fetch_failed(gates: Sequence[Dict[str, Any]]) -> bool:
    return any(
        g.get("name") == "fetch" and not g.get("ok") and not g.get("skipped")
        for g in gates
    )


def append_runtime(
    root: Path,
    errs: List[str],
    gates: List[Dict[str, Any]],
    *,
    enabled: bool,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    touch_rels: Optional[Sequence[str]] = None,
) -> None:
    """Mutate errs/gates. No-op when disabled or when fetch already failed."""
    if not enabled or _fetch_failed(gates):
        return
    rels = (
        list(touch_rels)
        if touch_rels is not None
        else touch_rel_paths(root, from_ref=from_ref, to_ref=to_ref)
    )
    more, more_gates = runtime_errors(root, touch_rels=rels)
    errs.extend(more)
    gates.extend(more_gates)


def _gate(name: str, errs: List[str], *, skipped: bool = False, detail: str = "") -> Dict[str, Any]:
    rec: Dict[str, Any] = {"name": name, "ok": not errs, "detail": detail or "; ".join(errs)}
    if skipped:
        rec["skipped"] = True
        rec["ok"] = True
    return rec


def log_path() -> Path:
    env = os.environ.get("VBD_GATE_LOG", "").strip()
    if env:
        return Path(os.path.expanduser(env))
    return Path.home() / ".grok" / "logs" / "vbd_gate.jsonl"


def git_head(root: Path) -> Optional[str]:
    proc = _git(root, ["rev-parse", "HEAD"])
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def append_log(record: Dict[str, Any]) -> None:
    """Best-effort. A full disk must not change the gate result."""
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    except OSError as exc:
        print("vbd_gate: log write failed: {0}".format(exc), file=sys.stderr)


def emit_log(
    *,
    event: str,
    root: Path,
    errs: List[str],
    gates: List[Dict[str, Any]],
    promoted: Optional[str] = None,
) -> None:
    append_log(
        {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": event,
            "cwd": str(root),
            "ok": not errs,
            "gates": gates,
            "promoted": promoted,
            "git_head": git_head(root) if is_git(root) else None,
        }
    )


def run_checks(
    root: Path,
    *,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    do_fetch: bool = True,
    tracked_only: bool = False,
    skip_if_clean: bool = False,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    gates: List[Dict[str, Any]] = []
    errs: List[str] = []
    if not is_git(root):
        gates.append(_gate("git", [], skipped=True, detail="not a git repo"))
        return errs, gates
    paths = changed_paths(
        root, from_ref=from_ref, to_ref=to_ref, tracked_only=tracked_only
    )
    if skip_if_clean and not paths:
        gates.append(_gate("skip_if_clean", [], skipped=True, detail="no changed files"))
        return errs, gates
    if do_fetch:
        fe = git_fetch(root)
        if fe:
            gates.append(_gate("fetch", [fe]))
            return [fe], gates
        gates.append(_gate("fetch", []))
        oa = origin_ahead_errors(root)
        gates.append(_gate("origin_ahead", oa))
        errs.extend(oa)
    else:
        gates.append(_gate("fetch", [], skipped=True, detail="not requested"))
    de = dash_errors(paths, root=root, from_ref=from_ref, to_ref=to_ref)
    gates.append(_gate("dashes", de))
    errs.extend(de)
    se = skip_path_errors(paths)
    gates.append(_gate("skip_landing", se))
    errs.extend(se)
    ve = viewport_errors(root, paths)
    ui = [p for p in paths if p.suffix.lower() in UI_SUFFIX]
    vs = root / "viewer" / "scripts" / "viewport_sanity.py"
    if not ui:
        gates.append(_gate("viewport_sanity", [], skipped=True, detail="no html/css in change set"))
    elif not vs.is_file():
        gates.append(_gate("viewport_sanity", [], skipped=True, detail="no viewer/scripts/viewport_sanity.py"))
    else:
        gates.append(_gate("viewport_sanity", ve))
        errs.extend(ve)
    return errs, gates


def hook_script(gate_path: Path) -> str:
    return (
        "#!/bin/sh\n"
        "# {0}\n"
        "set -e\n"
        "GATE=\"${{VBD_GATE:-{1}}}\"\n"
        "if [ ! -f \"$GATE\" ]; then\n"
        "  echo \"vbd_gate: missing $GATE\" >&2\n"
        "  exit 2\n"
        "fi\n"
        "exec python3 \"$GATE\" hook-run --app-root \"$(git rev-parse --show-toplevel)\"\n"
    ).format(HOOK_MARK, gate_path)


def hook_install(root: Path) -> None:
    hook_dir = root / ".git" / "hooks"
    if not hook_dir.is_dir():
        # gitdir file (worktree) or missing
        gitdir = _git(root, ["rev-parse", "--git-path", "hooks"])
        if gitdir.returncode != 0:
            raise SystemExit("hook-install: not a git repo: {0}".format(root))
        hook_dir = Path(gitdir.stdout.strip())
        if not hook_dir.is_absolute():
            hook_dir = root / hook_dir
        hook_dir.mkdir(parents=True, exist_ok=True)
    path = hook_dir / "pre-push"
    body = hook_script(PACK_ROOT / "vbd_gate.py")
    if path.is_file():
        old = path.read_text(encoding="utf-8")
        if HOOK_MARK not in old and old.strip():
            raise SystemExit(
                "hook-install: {0} exists and is not a VBD hook; "
                "leave it (finish-later). Install by hand if you want both.".format(path)
            )
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("installed {0}".format(path))


def grok_hook_install() -> None:
    dest_dir = Path.home() / ".grok" / "hooks"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "vbd-stop.json"
    stop_py = PACK_ROOT / "vbd_stop_hook.py"
    cmd = "{0} {1}".format(sys.executable, stop_py)
    payload = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": cmd,
                            "timeout": 90,
                        }
                    ]
                }
            ]
        }
    }
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("installed {0}".format(dest))


def is_vbd_pack(root: Path) -> bool:
    return (
        (root / "vbd_gate.py").is_file()
        and (root / "VERIFY_BEFORE_DONE.md").is_file()
        and (root / "AGENTS.md.drop-in").is_file()
    )


def graphforge_root() -> Optional[Path]:
    env = os.environ.get("GRAPHFORGE_ROOT", "").strip()
    p = Path(os.path.expanduser(env)) if env else Path.home() / "graphforge"
    if (p / "scripts" / "sync_bundled_companions.py").is_file():
        return p.resolve()
    return None


def publish_vbd_to_graphforge(vbd_root: Path) -> str:
    """Copy this pack into private GraphForge and push. Operator PC distribution."""
    if os.environ.get("VBD_SKIP_GF_PUBLISH", "").strip() in ("1", "true", "yes"):
        print("publish-gf: skipped (VBD_SKIP_GF_PUBLISH)")
        return "skipped"
    gf = graphforge_root()
    if gf is None:
        print("publish-gf: no GraphForge checkout; skip")
        return "skipped"
    sync = gf / "scripts" / "sync_bundled_companions.py"
    proc = subprocess.run(
        [sys.executable, str(sync), "--vbd-root", str(vbd_root)],
        cwd=str(gf),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "publish-gf: sync failed\n{0}{1}".format(proc.stdout or "", proc.stderr or "")
        )
    files = ["bundled/verify-before-done", "bundled/SOURCE.json", "bundled/README.md"]
    subprocess.check_call(["git", "add", "--"] + files, cwd=str(gf))
    quiet = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--"] + files,
        cwd=str(gf),
    )
    if quiet.returncode == 0:
        print("publish-gf: GraphForge bundle already current")
        return "unchanged"
    sha = git_head(vbd_root) or "unknown"
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Martial Systems LLC"
    env["GIT_AUTHOR_EMAIL"] = "25778085+martialsystems@users.noreply.github.com"
    env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
    env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
    msg = "Refresh bundled VBD from pack @{0}.\n".format(sha)
    subprocess.check_call(
        ["git", "commit", "-m", msg, "--"] + files,
        cwd=str(gf),
        env=env,
    )
    push = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        cwd=str(gf),
        capture_output=True,
        text=True,
    )
    if push.returncode != 0:
        raise SystemExit(
            "publish-gf: graphforge push failed\n{0}{1}".format(push.stdout or "", push.stderr or "")
        )
    print("publish-gf: pushed GraphForge bundle for VBD {0}".format(sha))
    return "pushed"


def maybe_publish_gf_after_vbd_push(root: Path) -> None:
    if not is_vbd_pack(root):
        return
    publish_vbd_to_graphforge(root)


def parse_hook_refs(text: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local_sha, remote_sha = parts[1], parts[3]
        pairs.append((remote_sha, local_sha))
    return pairs


def cmd_check(args: argparse.Namespace) -> int:
    root = args.app_root.resolve()
    print("=== vbd_gate check {0} ===".format(root))
    errs, gates = run_checks(
        root,
        tracked_only=bool(getattr(args, "tracked_only", False)),
        skip_if_clean=bool(getattr(args, "skip_if_clean", False)),
    )
    promoted: Optional[str] = None
    event = "check"
    if args.claim_done:
        event = "claim-done"
        if not (args.promoted or args.not_promoted):
            msg = (
                "--claim-done requires --promoted <lesson> or "
                "--not-promoted <why> (unique to this product / already in LESSONS.md)"
            )
            errs.append(msg)
            gates.append(_gate("claim_done", [msg]))
        elif args.promoted:
            promoted = args.promoted
            print("  promoted: {0}".format(args.promoted))
            gates.append(_gate("claim_done", []))
        else:
            promoted = "not promoted: {0}".format(args.not_promoted)
            print("  not promoted: {0}".format(args.not_promoted))
            gates.append(_gate("claim_done", []))
    append_runtime(
        root,
        errs,
        gates,
        enabled=bool(args.claim_done or getattr(args, "with_runtime", False)),
    )
    emit_log(event=event, root=root, errs=errs, gates=gates, promoted=promoted)
    if errs:
        for e in errs:
            print("  [FAIL] {0}".format(e))
        return 2
    print("vbd_gate: PASS")
    return 0


def cmd_hook_run(args: argparse.Namespace) -> int:
    root = args.app_root.resolve()
    stdin = sys.stdin.read() if not sys.stdin.isatty() else ""
    pairs = parse_hook_refs(stdin)
    print("=== vbd_gate pre-push {0} ===".format(root))
    errs: List[str] = []
    gates: List[Dict[str, Any]] = []
    fe = git_fetch(root)
    if fe:
        gates.append(_gate("fetch", [fe]))
        emit_log(event="pre-push", root=root, errs=[fe], gates=gates)
        print("  [FAIL] {0}".format(fe))
        return 2
    gates.append(_gate("fetch", []))
    oa = origin_ahead_errors(root)
    gates.append(_gate("origin_ahead", oa))
    errs.extend(oa)
    touch: Set[str] = set()
    if pairs:
        for remote_sha, local_sha in pairs:
            if local_sha == "0" * 40:
                continue
            more, more_gates = run_checks(
                root, from_ref=remote_sha, to_ref=local_sha, do_fetch=False
            )
            errs.extend(more)
            gates.extend(more_gates)
            touch.update(
                touch_rel_paths(root, from_ref=remote_sha, to_ref=local_sha)
            )
    else:
        more, more_gates = run_checks(root, do_fetch=False)
        errs.extend(more)
        gates.extend(more_gates)
        touch.update(touch_rel_paths(root))
    append_runtime(root, errs, gates, enabled=True, touch_rels=sorted(touch))
    emit_log(event="pre-push", root=root, errs=errs, gates=gates)
    if errs:
        for e in errs:
            print("  [FAIL] {0}".format(e))
        print("vbd_gate: push blocked. Fix the gates (or do not claim done).")
        return 2
    print("vbd_gate: PASS")
    maybe_publish_gf_after_vbd_push(root)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd")

    def with_root(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--app-root", type=Path, default=Path("."))

    c = sub.add_parser("check", help="Run gates on the working tree")
    with_root(c)
    c.add_argument("--claim-done", action="store_true")
    c.add_argument("--promoted", default="")
    c.add_argument("--not-promoted", default="")
    c.add_argument(
        "--tracked-only",
        action="store_true",
        help="Ignore untracked files (Stop hook: finish-later dirt must not block Q&A)",
    )
    c.add_argument(
        "--skip-if-clean",
        action="store_true",
        help="Pass immediately when there are no changed files to gate",
    )
    c.add_argument(
        "--with-runtime",
        action="store_true",
        help="Run vbd.runtime.json argv checks even without --claim-done",
    )
    h = sub.add_parser("hook-install", help="Install a pre-push hook in --app-root")
    with_root(h)
    sub.add_parser("grok-hook-install", help="Install the Grok Stop hook under ~/.grok/hooks")
    pg = sub.add_parser("publish-gf", help="Sync this pack into private GraphForge and push")
    with_root(pg)
    r = sub.add_parser("hook-run", help="Invoked by the pre-push hook")
    with_root(r)
    args = p.parse_args(argv)
    cmd = args.cmd or "check"
    if not hasattr(args, "app_root"):
        args.app_root = Path(".")
    if cmd == "check" and not hasattr(args, "claim_done"):
        args.claim_done = False
        args.promoted = ""
        args.not_promoted = ""
        args.tracked_only = False
        args.skip_if_clean = False
        args.with_runtime = False
    if cmd == "hook-install":
        hook_install(args.app_root.resolve())
        return 0
    if cmd == "grok-hook-install":
        grok_hook_install()
        return 0
    if cmd == "hook-run":
        return cmd_hook_run(args)
    if cmd == "publish-gf":
        if not is_vbd_pack(args.app_root.resolve()):
            print("publish-gf: --app-root is not a VBD pack", file=sys.stderr)
            return 2
        publish_vbd_to_graphforge(args.app_root.resolve())
        return 0
    return cmd_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
