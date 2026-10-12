"""P1.5.8 first pass: canonical runtime names are additive compatibility aliases.

Legacy modules/CLI/env/state names stay authoritative; the canonical names resolve the legacy implementation at
call time and are purely additive.
"""
import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

ALIASES = [
    ("graphs.pipelines.live_cycle", "run_live_cycle_once", "graphs.pipelines.m13_live_loop", "run_m13_once"),
    ("graphs.pipelines.runtime_tick", "run_runtime_tick", "graphs.pipelines.m13_tick", "run_m13_tick"),
    ("graphs.pipelines.eod_report", "run_eod_report", "graphs.pipelines.m13_eod_report", "run_m13_eod_report"),
]


@pytest.mark.parametrize("canon_mod,canon_name,legacy_mod,legacy_name", ALIASES)
def test_canonical_alias_delegates_at_call_time(canon_mod, canon_name, legacy_mod, legacy_name, monkeypatch):
    canon = importlib.import_module(canon_mod)
    legacy = importlib.import_module(legacy_mod)
    assert callable(getattr(legacy, legacy_name))  # legacy name unchanged
    seen = {}

    def spy(*args, **kwargs):
        seen["args"], seen["kwargs"] = args, kwargs
        return "legacy-result"

    monkeypatch.setattr(legacy, legacy_name, spy)
    assert getattr(canon, canon_name)(1, a=2) == "legacy-result"
    assert seen == {"args": (1,), "kwargs": {"a": 2}}


def test_entrypoint_alias_main_delegates_and_keeps_root(monkeypatch):
    canon = importlib.import_module("libs.runtime.entrypoints.live_loop")
    legacy = importlib.import_module("libs.runtime.entrypoints.m13_live_loop")
    assert canon.ROOT == legacy.ROOT
    monkeypatch.setattr(legacy, "main", lambda argv=None: 7 if argv == ["x"] else -1)
    assert canon.main(["x"]) == 7


def test_canonical_cli_script_is_a_thin_alias_and_help_works():
    text = (ROOT / "scripts" / "run_live_loop.py").read_text(encoding="utf-8")
    assert "libs.runtime.entrypoints.live_loop import" in text
    assert not [l for l in text.splitlines() if l.startswith(("from ", "import ")) and "m13" in l]
    # legacy CLI still present
    assert (ROOT / "scripts" / "run_m13_live_loop.py").is_file()
    for script in ("run_live_loop.py", "run_m13_live_loop.py"):
        r = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), "--help"], cwd=ROOT,
                           capture_output=True, encoding="utf-8", errors="replace", timeout=120)
        assert r.returncode == 0, (script, r.stderr[-400:])
        assert "--lock-path" in r.stdout


def test_live_loop_env_precedence_canonical_then_legacy_then_default(monkeypatch):
    from libs.runtime.entrypoint_common import live_loop_env
    for name in ("LIVE_LOOP_LOCK_PATH", "M13_LIVE_LOCK_PATH"):
        monkeypatch.delenv(name, raising=False)
    assert live_loop_env("LIVE_LOOP_LOCK_PATH", "M13_LIVE_LOCK_PATH", "d") == "d"
    monkeypatch.setenv("M13_LIVE_LOCK_PATH", "legacy")
    assert live_loop_env("LIVE_LOOP_LOCK_PATH", "M13_LIVE_LOCK_PATH", "d") == "legacy"   # exactly the old behaviour
    monkeypatch.setenv("LIVE_LOOP_LOCK_PATH", "canonical")
    assert live_loop_env("LIVE_LOOP_LOCK_PATH", "M13_LIVE_LOCK_PATH", "d") == "canonical"
    monkeypatch.setenv("LIVE_LOOP_LOCK_PATH", "")
    assert live_loop_env("LIVE_LOOP_LOCK_PATH", "M13_LIVE_LOCK_PATH", "d") == ""          # set-but-empty is honoured


def test_every_lock_env_read_goes_through_the_single_resolver():
    """One resolver => no code path can end up with two different lock paths from the alias."""
    pat = re.compile(r"os\.getenv\(\s*[\"'](M13_LIVE_LOCK_PATH|M13_LIVE_LOCK_STALE_SEC)[\"']")
    offenders = []
    for base in ("libs", "scripts", "graphs", "apps"):
        for p in (ROOT / base).rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            if pat.search(p.read_text(encoding="utf-8-sig", errors="replace")):
                offenders.append(str(p.relative_to(ROOT)))
    assert offenders == [], offenders
    users = [p for p in (ROOT / "libs").rglob("*.py") if "live_loop_env(" in p.read_text(encoding="utf-8-sig", errors="replace")]
    assert len(users) >= 4
