"""RF-066 C2/C3: actual demo graph stays offline and confines its writes."""

from __future__ import annotations

import json
import socket

from graphs.nodes import build_decision_context
from scripts.examples import demo_m22_graph_with_hydration as demo


def test_rf066_graph_demo_uses_no_yfinance_and_writes_only_in_temp_cwd(monkeypatch, tmp_path, capsys):
    def forbidden_yfinance(*_args, **_kwargs):
        raise AssertionError("offline demo must not request yfinance")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(build_decision_context, "_fetch_yfinance_seed", forbidden_yfinance)

    if demo.main(["--json"]) != 0:
        raise AssertionError("graph demo failed")

    payload = json.loads(capsys.readouterr().out)
    if payload["scanner_skill"]["fallback"] is not False:
        raise AssertionError(payload["scanner_skill"])
    if list(tmp_path.iterdir()):
        raise AssertionError("graph demo escaped the artifact isolation")


def test_rf066_graph_timeout_demo_never_opens_socket_or_escapes_temp_cwd(monkeypatch, tmp_path, capsys):
    """Exercise the real graph path, not an injected graph, on its timeout branch."""

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("offline graph demo must not open a socket")

    def forbidden_yfinance(*_args, **_kwargs):
        raise AssertionError("offline graph demo must not request yfinance")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(socket, "socket", forbidden_socket)
    monkeypatch.setattr(build_decision_context, "_fetch_yfinance_seed", forbidden_yfinance)

    if demo.main(["--simulate-timeout", "--json"]) != 0:
        raise AssertionError("timeout graph demo failed")

    payload = json.loads(capsys.readouterr().out)
    if payload["skill_fetch"]["errors_total"] != 5:
        raise AssertionError(payload["skill_fetch"])
    if payload["scanner_skill"]["fallback"] is not True:
        raise AssertionError(payload["scanner_skill"])
    if list(tmp_path.iterdir()):
        raise AssertionError("timeout graph demo escaped the artifact isolation")
