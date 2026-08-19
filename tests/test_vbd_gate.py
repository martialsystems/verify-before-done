# Copyright (c) 2026 Martial Systems LLC. MIT.
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from vbd_gate import (  # noqa: E402
    dash_errors,
    main,
    skip_landing_errors,
)


def test_skip_panel_containing_chart_fails():
    html = """
    <a class="skip-juicy" href="#panel">skip</a>
    <section id="panel" class="panel">
      <div class="chart-wrap" id="chart"></div>
    </section>
    """
    errs = skip_landing_errors(html)
    assert errs
    assert any("visual target" in e for e in errs)


def test_skip_direct_to_chart_ok():
    html = """
    <a class="skip-juicy" href="#chart">skip</a>
    <section id="panel" class="panel">
      <div class="chart-wrap" id="chart"></div>
    </section>
    """
    assert skip_landing_errors(html) == []


def test_no_skip_control_ok():
    assert skip_landing_errors("<p>no skip</p>") == []


def test_dash_errors_on_md(tmp_path: Path):
    p = tmp_path / "NOTE.md"
    p.write_text("Channels — named slots\n", encoding="utf-8")
    errs = dash_errors([p])
    assert errs
    p.write_text("Channels: named slots\n", encoding="utf-8")
    assert dash_errors([p]) == []


def test_claim_done_requires_promote_flag(tmp_path: Path):
    rc = main(["check", "--app-root", str(tmp_path), "--claim-done"])
    assert rc == 2


def _git(cwd: Path, *args: str) -> None:
    subprocess.check_call(["git", *args], cwd=str(cwd), stdout=subprocess.DEVNULL)


def test_check_clean_git_repo(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("Hello: world\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    rc = main(
        [
            "check",
            "--app-root",
            str(tmp_path),
            "--claim-done",
            "--not-promoted",
            "unique to this fixture",
        ]
    )
    assert rc == 0


def test_check_fails_new_html_skip_panel(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    (tmp_path / "board.html").write_text(
        '<a class="skip-juicy" href="#panel">s</a>'
        '<section id="panel"><div class="chart-wrap" id="g"></div></section>\n',
        encoding="utf-8",
    )
    rc = main(["check", "--app-root", str(tmp_path)])
    assert rc == 2
