"""RF-061 C1/C2: the only external consumer of ``libs.tools.tool_facade.ToolFacade`` is ``scripts/approval_cli.py``.

Only argument parsing and a fake ToolFacade are exercised: the real facade, Settings, Supervisor and
Step5C paths are never constructed. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

CLI = Path(__file__).resolve().parents[1] / "scripts" / "approval_cli.py"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.fixture()
def cli(monkeypatch):
    spec = importlib.util.spec_from_file_location("approval_cli_under_test", CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def real_facade_forbidden(*_a, **_k):
        raise AssertionError("real ToolFacade must not be constructed")

    monkeypatch.setattr(mod, "ToolFacade", real_facade_forbidden)
    return mod


@pytest.mark.parametrize("argv", [["--help"], ["preview", "--help"], ["approve", "--help"], ["reject", "--help"], ["list", "--help"]])
def test_help_exits_zero_before_any_facade_is_built(cli, argv, capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    _eq(exc.value.code, 0)
    if "usage" not in capsys.readouterr().out.lower():
        raise AssertionError("usage text expected")


@pytest.mark.parametrize("argv", [[], ["bogus"], ["list", "--limit", "x"]])
def test_bad_arguments_exit_two_before_any_facade_is_built(cli, argv):
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    _eq(exc.value.code, 2)


def test_subcommands_route_to_the_matching_facade_method_with_a_fake(cli, monkeypatch, capsys):
    calls = []

    class FakeFacade:
        def preview_intent(self, **kw):
            calls.append(("preview", kw)); return {"op": "preview"}

        def approve_intent(self, **kw):
            calls.append(("approve", kw)); return {"op": "approve"}

        def reject_intent(self, **kw):
            calls.append(("reject", kw)); return {"op": "reject"}

        def list_intents(self, **kw):
            calls.append(("list", kw)); return {"op": "list"}

    monkeypatch.setattr(cli, "ToolFacade", FakeFacade)
    _eq(cli.main(["preview", "--intent-id", "i1"]), 0)
    _eq(cli.main(["approve"]), 0)
    _eq(cli.main(["reject", "--intent-id", "i2", "--reason", "no"]), 0)
    _eq(cli.main(["list", "--limit", "3"]), 0)
    _eq(calls, [("preview", {"intent_id": "i1"}), ("approve", {"intent_id": None}),
                ("reject", {"intent_id": "i2", "reason": "no"}), ("list", {"limit": 3})])
    out = capsys.readouterr().out
    _eq([json.loads(chunk)["op"] for chunk in out.replace("}\n{", "}\x00{").split("\x00")], ["preview", "approve", "reject", "list"])
