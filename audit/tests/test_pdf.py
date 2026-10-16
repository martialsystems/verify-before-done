# Copyright (c) 2026 Martial Systems LLC. MIT License, see LICENSE.
import json
from pathlib import Path

from upgrade_audit.findings import validate_repo_report
from upgrade_audit.pdf import build_pdf


def _write_mini(run: Path) -> None:
    (run / "repos").mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({"repos": ["demo"], "date": "2026-08-17"}))
    report = {
        "repo": "demo", "github": "me/demo", "local_path": "/tmp/demo",
        "audited_ref": "main", "audited_sha": "abc123", "dirty": False,
        "files_read": ["a.py"],
        "findings": [{
            "repo": "demo", "commit": "abc123", "file": "a.py", "line": 3,
            "error_class": "silent_fallback", "claim": "returns 0 on error",
            "evidence": "except: return 0", "proposed_fix": "raise", "severity": "major",
            "status": "confirmed", "verifier_evidence": "reproduced",
        }],
    }
    (run / "repos" / "demo.json").write_text(json.dumps(report))


def test_fixture_report_validates(tmp_path):
    _write_mini(tmp_path / "run")
    rep = json.loads((tmp_path / "run" / "repos" / "demo.json").read_text())
    assert validate_repo_report(rep) == []


def test_build_pdf(tmp_path):
    run = tmp_path / "run"
    _write_mini(run)
    dest = tmp_path / "out.pdf"
    build_pdf(run, dest, from_ver="4.5", to_ver="4.6", day="2026-08-17")
    from pypdf import PdfReader
    text = "".join(p.extract_text() or "" for p in PdfReader(str(dest)).pages)
    assert dest.stat().st_size > 1000 and "demo" in text
