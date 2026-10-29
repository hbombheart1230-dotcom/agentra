"""P15 A1: ``_pid_active`` moved to live_execution_bundle_runner_pid_active; fake os/ctypes only (no real process contact)."""
from __future__ import annotations

import inspect
import sys
from types import SimpleNamespace

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_pid_active as owner


def _fake_os(name="posix", kill=None):
    def deny(pid, sig):
        raise AssertionError("os.kill must be faked")
    return SimpleNamespace(name=name, kill=kill or deny)


def _both(monkeypatch, fake):
    monkeypatch.setattr(r, "os", fake)
    return (lambda pid: r._pid_active(pid)), (lambda pid: owner._pid_active(pid, facade=r))


@pytest.mark.parametrize("pid", [0, -1, None, "", "0", -5])
def test_non_positive_pid_is_false_without_any_os_call(monkeypatch, pid):
    for fn in _both(monkeypatch, _fake_os()):
        assert fn(pid) is False


def test_posix_success_permission_and_oserror(monkeypatch):
    calls = []
    for exc, expected in ((None, True), (PermissionError("no"), True), (ProcessLookupError("gone"), False), (OSError("x"), False)):
        def kill(pid, sig, exc=exc):
            calls.append((pid, sig))
            if exc:
                raise exc
        for fn in _both(monkeypatch, _fake_os(kill=kill)):
            assert fn("42") is expected
    assert set(calls) == {(42, 0)} and len(calls) == 8


def test_windows_branch_with_fake_ctypes(monkeypatch):
    events = []

    class Kernel:
        def __init__(self, handle):
            self.handle = handle

        def OpenProcess(self, access, inherit, pid):
            events.append(("open", access, inherit, pid))
            if isinstance(self.handle, Exception):
                raise self.handle
            return self.handle

        def CloseHandle(self, handle):
            events.append(("close", handle))

    for handle, expected in ((0, False), (1234, True), (RuntimeError("boom"), False)):
        monkeypatch.setitem(sys.modules, "ctypes", SimpleNamespace(windll=SimpleNamespace(kernel32=Kernel(handle))))
        for fn in _both(monkeypatch, _fake_os(name="nt")):
            assert fn(77) is expected
    opens = [e for e in events if e[0] == "open"]
    assert opens and all(e == ("open", 0x1000, False, 77) for e in opens)
    assert events.count(("close", 1234)) == 2 and not any(e[0] == "close" and e[1] != 1234 for e in events)


def test_windows_missing_ctypes_attribute_is_false(monkeypatch):
    monkeypatch.setitem(sys.modules, "ctypes", SimpleNamespace())
    for fn in _both(monkeypatch, _fake_os(name="nt")):
        assert fn(5) is False


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    assert "import live_execution_bundle_runner\n" not in inspect.getsource(owner) and "from libs.reporting.live_execution_bundle_runner import" not in inspect.getsource(owner)
    assert len(inspect.getsource(r._pid_active).splitlines()) <= 3
