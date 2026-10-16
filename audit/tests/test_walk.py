# Copyright (c) 2026 Martial Systems LLC. MIT License, see LICENSE.
"""Walk scheduler: hang cases from the 1.6.0 bug report must terminate."""
from datetime import datetime, timedelta, timezone

from upgrade_audit.walk import SPAWN_ACK_SECONDS_DEFAULT, _parse_ts, empty_walk, step

T0 = datetime(2026, 10, 16, 10, 0, 0, tzinfo=timezone.utc)


def snap(t, agents=(), spawned=(), **kw):
    d = {"now": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "agents": list(agents), "spawned": list(spawned)}
    d.update(kw)
    return d


def run_until_complete(state, snaps_fn, limit=50):
    for i in range(limit):
        actions = step(state, snaps_fn(i))
        if actions["walk_complete"]:
            return i, actions
    raise AssertionError("walk never completed: {0}".format(state))


def test_unbound_slot_never_acked_terminates():
    """Bug 1: a reserved auditor whose subagent never launches used to hold forever."""
    state = empty_walk(["a"], kill="none")
    first = step(state, snap(T0))
    assert first["spawn"] == [{"repo": "a", "role": "auditor"}]
    # Parent never reports a spawn. 13 hours of snapshots.
    step_s = timedelta(seconds=SPAWN_ACK_SECONDS_DEFAULT)
    i, actions = run_until_complete(state, lambda i: snap(T0 + step_s * (i + 1)))
    assert any(r["repo"] == "a" and r["reason"] == "spawn_timeout" for r in state["skipped"])
    assert "a|auditor" in state["respawned"]  # retried once before skipping
    assert actions["join"]["ids"] == []


def test_slot_within_ack_window_is_kept():
    state = empty_walk(["a"])
    step(state, snap(T0))
    step(state, snap(T0 + timedelta(seconds=30)))
    assert len(state["in_flight"]) == 1 and not state["skipped"]


def test_acked_agent_missing_from_snapshot_terminates():
    """Bug 2: an agent absent from every snapshot used to be skipped over forever."""
    state = empty_walk(["a"], kill="none")
    step(state, snap(T0))
    step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "ag1"}],
                     agents=[{"id": "ag1", "status": "running"}]))
    assert state["in_flight"][0]["agent_id"] == "ag1"
    step_s = timedelta(seconds=SPAWN_ACK_SECONDS_DEFAULT)
    i, _ = run_until_complete(state, lambda i: snap(T0 + step_s * (i + 1)))
    assert any(r["reason"] in ("lost", "spawn_timeout") for r in state["skipped"])


def test_missing_agent_that_reappears_is_not_dropped():
    state = empty_walk(["a"])
    step(state, snap(T0))
    step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "ag1"}],
                     agents=[{"id": "ag1", "status": "running"}]))
    step(state, snap(T0 + timedelta(seconds=60)))  # missing once
    assert "missing_since" in state["in_flight"][0]
    step(state, snap(T0 + timedelta(seconds=120), agents=[{"id": "ag1", "status": "running"}]))
    assert "missing_since" not in state["in_flight"][0]
    step(state, snap(T0 + timedelta(seconds=SPAWN_ACK_SECONDS_DEFAULT + 60),
                     agents=[{"id": "ag1", "status": "running"}]))
    assert state["in_flight"] and not state["skipped"]


def test_lost_verifier_marks_unverified_not_skipped():
    state = empty_walk(["a"])
    state["pending_verify"] = ["a"]
    state["queue"] = []
    state["respawned"] = ["a|verifier"]
    step(state, snap(T0))
    out = step(state, snap(T0 + timedelta(seconds=SPAWN_ACK_SECONDS_DEFAULT)))
    assert out["unverify"] == [{"repo": "a", "reason": "spawn_timeout"}]
    assert "a" in state["done"] and out["walk_complete"]


def test_naive_local_timestamp_is_not_read_as_utc(monkeypatch):
    """Bug 3: a naive local `now` must convert through the local zone."""
    monkeypatch.setenv("TZ", "America/Indiana/Indianapolis")
    import time
    time.tzset()
    try:
        ts = _parse_ts("2026-10-16T06:00:00")
        assert ts == datetime(2026, 10, 16, 10, 0, 0, tzinfo=timezone.utc)
        # Stall kill: agent quiet 20 min in UTC terms, snapshot stamped in naive local.
        state = empty_walk(["a"], kill="stall", stall_seconds=900)
        step(state, snap(T0))
        step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "ag1"}],
                         agents=[{"id": "ag1", "status": "running"}]))
        out = step(state, {"now": "2026-10-16T06:20:00", "agents": [{"id": "ag1", "status": "running"}]})
        assert [k["id"] for k in out["kill"]] == ["ag1"]
    finally:
        monkeypatch.delenv("TZ")
        time.tzset()


def test_first_snapshot_after_spawn_does_not_reset_stall_timer():
    """Bug 7: the placeholder token made the first real snapshot look like progress."""
    state = empty_walk(["a"], kill="stall", stall_seconds=900)
    step(state, snap(T0))
    agent = {"id": "ag1", "status": "running"}
    step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "ag1"}], agents=[agent]))
    step(state, snap(T0 + timedelta(seconds=600), agents=[agent]))
    assert state["in_flight"][0]["last_progress_at"] == "2026-10-16T10:00:00Z"
    out = step(state, snap(T0 + timedelta(seconds=900), agents=[agent]))
    assert out["kill"] and out["kill"][0]["reason"] == "stall"


def test_growing_output_counts_as_progress():
    state = empty_walk(["a"], kill="stall", stall_seconds=900)
    step(state, snap(T0))
    step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "ag1"}],
                     agents=[{"id": "ag1", "status": "running"}]))
    out = step(state, snap(T0 + timedelta(seconds=900), agents=[{"id": "ag1", "status": "running", "output": "x"}]))
    assert not out["kill"]


def test_unbound_fix_slot_times_out_and_walk_completes():
    """Bug 6: a reserved fix slot that is never acked must close the fix, not hang."""
    state = empty_walk(["a"])
    state.update({"queue": [], "done": ["a"], "pending_fix": ["a"]})
    out = step(state, snap(T0))
    assert out["spawn"] == [{"repo": "a", "role": "fix"}] and not out["walk_complete"]
    step_s = timedelta(seconds=SPAWN_ACK_SECONDS_DEFAULT)
    run_until_complete(state, lambda i: snap(T0 + step_s * (i + 1)))
    assert state["fix_skipped"][0]["repo"] == "a"
    assert "a" in state["done"] and not state["skipped"]


def test_fix_not_reserved_before_audit_done():
    state = empty_walk(["a"])
    state.update({"queue": [], "pending_fix": ["a"]})
    out = step(state, snap(T0))
    assert out["spawn"] == []


def test_full_happy_path():
    state = empty_walk(["a"])
    step(state, snap(T0))
    step(state, snap(T0, spawned=[{"repo": "a", "role": "auditor", "id": "au"}],
                     agents=[{"id": "au", "status": "completed"}]))
    assert state["in_flight"][0]["role"] == "verifier"
    out = step(state, snap(T0, spawned=[{"repo": "a", "role": "verifier", "id": "ve"}],
                           agents=[{"id": "ve", "status": "completed"}]))
    assert out["walk_complete"] and out["validate"] == ["repos/a.json"]
