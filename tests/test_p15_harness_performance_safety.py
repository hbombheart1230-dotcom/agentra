"""Infrastructure-only regression: immutable caches and non-destructive cleanup."""
import ast
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _wave():
    spec = importlib.util.spec_from_file_location("_perf_wave", ROOT / "tests/test_p154_wave_b_moved_bodies.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cleanup_functions():
    tree = ast.parse((ROOT / "conftest.py").read_text(encoding="utf-8"))
    names = {"_windows_pid_still_alive", "_owning_pid_still_alive"}
    ns = {"os": os}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names],
                            type_ignores=[]), "<cleanup-functions>", "exec"), ns)
    return ns


def test_git_cache_keys_include_sha_and_never_cache_a_failed_read(monkeypatch):
    w = _wave()
    calls = []

    def read(command, **kwargs):
        calls.append(command)
        if command[-1].startswith("bad:"):
            raise subprocess.CalledProcessError(1, command)
        return command[-1].encode()

    monkeypatch.setattr(w.subprocess, "check_output", read)
    assert w._git_source_at("a", "x") == w._git_source_at("a", "x") == "a:x"
    assert w._git_source_at("b", "x") == "b:x"
    assert len(calls) == 2
    for _ in range(2):
        with pytest.raises(subprocess.CalledProcessError):
            w._git_source_at("bad", "x")
    assert len(calls) == 4


def test_cached_text_and_frozen_refs_are_exact_and_input_sensitive():
    w = _wave()
    src = "GLOBAL = 1\ndef f():\n    return GLOBAL\n"
    assert w._function_source(src, "f") == ast.get_source_segment(src, w._func(ast.parse(src), "f"))
    assert w._source_bound(src) == frozenset(w._bound(ast.parse(src)))
    assert w._globals(src, "f") == frozenset({"GLOBAL"})
    assert w._globals(src.replace("GLOBAL", "OTHER"), "f") == frozenset({"OTHER"})
    with pytest.raises(AttributeError):
        w._globals(src, "f").add("ignored")


def test_invalid_pid_never_queried():
    ns = _cleanup_functions()
    assert ns["_owning_pid_still_alive"](0) is False
    assert ns["_owning_pid_still_alive"](-1) is False


def test_live_child_survives_query_and_dead_child_is_detected():
    ns = _cleanup_functions()
    # Pipe handshake ensures the child is fully running before querying it.
    p = subprocess.Popen([sys.executable, "-c", "import sys; print('ready', flush=True); sys.stdin.readline()"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert p.stdout.readline().strip() == "ready"
        assert ns["_owning_pid_still_alive"](p.pid) is True
        assert p.poll() is None
    finally:
        p.communicate("done\n", timeout=10)
    assert p.returncode == 0
    assert ns["_owning_pid_still_alive"](p.pid) is False


def test_windows_dispatch_never_calls_kill():
    ns = _cleanup_functions()
    ns["os"] = types.SimpleNamespace(name="nt")
    ns["_windows_pid_still_alive"] = lambda pid: True
    assert ns["_owning_pid_still_alive"](123) is True


@pytest.mark.parametrize("handle,error,query_ok,exit_code,expected", [
    (0, 87, False, 0, False),
    (0, 5, False, 0, True),
    (1, 0, False, 0, True),
    (1, 0, True, 259, True),
    (1, 0, True, 0, False),
])
def test_windows_query_failure_is_conservative_and_handle_is_closed(
        monkeypatch, handle, error, query_ok, exit_code, expected):
    import ctypes

    class Call:
        def __init__(self, fn):
            self.fn = fn

        def __call__(self, *args):
            return self.fn(*args)

    closed = []

    def query(h, pointer):
        pointer._obj.value = exit_code
        return query_ok

    kernel = types.SimpleNamespace(OpenProcess=Call(lambda *args: handle),
                                   GetExitCodeProcess=Call(query),
                                   CloseHandle=Call(lambda h: closed.append(h)))
    monkeypatch.setattr(ctypes, "WinDLL", lambda *a, **kw: kernel, raising=False)
    monkeypatch.setattr(ctypes, "get_last_error", lambda: error, raising=False)
    ns = _cleanup_functions()
    assert ns["_windows_pid_still_alive"](123) is expected
    assert closed == ([handle] if handle else [])
