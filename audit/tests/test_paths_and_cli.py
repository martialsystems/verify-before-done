# Copyright (c) 2026 Martial Systems LLC. MIT License, see LICENSE.
import pytest

from upgrade_audit import cli
from upgrade_audit.catalog import default_catalog
from upgrade_audit.paths import package_checkout, user_catalog_path
from upgrade_audit.send_grok import send_grok_supported


def test_user_catalog_is_outside_pack(tmp_path):
    p = user_catalog_path()
    assert str(p).startswith(str(tmp_path))
    assert package_checkout() not in p.parents


def test_user_catalog_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("UPGRADE_AUDIT_CATALOG", str(tmp_path / "x.yaml"))
    assert user_catalog_path() == (tmp_path / "x.yaml").resolve()


def test_adopt_writes_user_catalog_not_pack(monkeypatch):
    from upgrade_audit.github import RemoteRepo
    remotes = [RemoteRepo(name="r1", is_fork=False, is_archived=False, url="https://github.com/me/r1")]
    monkeypatch.setattr(cli, "list_owned_repos", lambda owner: remotes, raising=False)
    monkeypatch.setattr(cli, "current_login", lambda: "me", raising=False)
    shipped = (package_checkout() / "catalog" / "repos.yaml").read_text()
    try:
        cli.main(["inventory", "--adopt"])
    except SystemExit:
        pass
    assert (package_checkout() / "catalog" / "repos.yaml").read_text() == shipped
    assert user_catalog_path().is_file()
    cat = default_catalog()
    assert cat.source == user_catalog_path() and len(cat.in_scope) == 1


def test_shipped_catalog_is_empty():
    cat = default_catalog()
    assert cat.owner == "" and cat.in_scope == []


@pytest.mark.parametrize("plat,ok", [("darwin", True), ("linux", False), ("win32", False)])
def test_send_grok_gate(plat, ok):
    assert send_grok_supported(plat) is ok


def test_send_grok_hidden_off_macos(monkeypatch):
    monkeypatch.setattr(cli, "send_grok_supported", lambda: False)
    choices = cli.build_parser()._subparsers._group_actions[0].choices
    assert "send-grok" not in choices
    assert "self-audit" not in choices


def test_doctor_gh_is_warning(monkeypatch):
    from upgrade_audit import pack
    real = pack._ok
    monkeypatch.setattr(pack, "_ok", lambda cmd: (False, "not logged in") if cmd[0] == "gh" else real(cmd))
    code, lines = pack.doctor()
    assert any(line.startswith("WARN gh") for line in lines)
    assert not any(line.startswith("FAIL gh") for line in lines)
