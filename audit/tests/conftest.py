# Copyright (c) 2026 Martial Systems LLC. MIT License, see LICENSE.
import pytest


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Keep tests off the real home, GROK_HOME, and per-user catalog."""
    monkeypatch.setenv("GROK_HOME", str(tmp_path / "grok"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.delenv("UPGRADE_AUDIT_CATALOG", raising=False)
    monkeypatch.delenv("UPGRADE_AUDIT_ROOT", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp"))
    (tmp_path / "tmp").mkdir()
