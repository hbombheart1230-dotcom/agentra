"""P15 A3: ``_build_parser`` moved to live_execution_bundle_runner_build_parser; only parse_args is called (main is never run)."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from types import SimpleNamespace

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_build_parser as owner

GOLDEN = ["9e63210e44fdd86f34f5797d43f44294140f6e185199c027747a1abc8e341ba0", "f1dbb5462bd267c7b1fdbbc7f4dabf7e1b47cf3c0d952f266e24d654b08471eb", "83f32e20fd3353803694188fc80c67b3096269dd7547aeb9e3f6039f58757ade", "c125ee148c39dffc3466abed52dbfeadfb4a270c88739d776a8fec24bc42e9e6", "EXIT:2", "EXIT:2", "EXIT:2"]
HELP_SHA = "362ab7d0acc2f560cefbd7273309e33e0a8e21c559478d667cb0ae9562a58b50"
ARGV = [[], ["--max-runs", "3", "--json", "--target-symbol", "005930"], ["--trade-report-ai"], ["--no-trade-report-ai"], ["--trade-report-ai", "--no-trade-report-ai"], ["--max-runs", "x"], ["--bogus"]]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


def _parse(parser, argv, capsys):
    try:
        out = _h(vars(parser.parse_args(argv)))
    except SystemExit as exc:
        capsys.readouterr()
        return "EXIT:%r" % (exc.code,)
    return out


@pytest.mark.parametrize("i", range(len(ARGV)))
def test_wrapper_and_owner_parse_like_the_pre_move_parser(i, capsys):
    assert _parse(r._build_parser(), ARGV[i], capsys) == GOLDEN[i]
    assert _parse(owner._build_parser(facade=r), ARGV[i], capsys) == GOLDEN[i]


def test_help_text_and_defaults_are_unchanged():
    parser = r._build_parser()
    parser.prog = "golden.py"                                                   # prog name is part of the usage text
    assert hashlib.sha256(parser.format_help().encode()).hexdigest() == HELP_SHA
    d = vars(r._build_parser().parse_args([]))
    assert list(d) == ["env_path", "event_log_path", "evidence_log_path", "report_dir", "reports_root", "intents_path", "day", "max_runs", "target_run_id", "target_symbol",
                       "role", "trade_report_ai", "trade_report_ai_model", "trade_report_ai_temperature", "trade_report_ai_max_tokens", "json"]
    assert d["max_runs"] == 50 and d["trade_report_ai"] is None and d["json"] is False and d["role"] == "intraday_trade_report_bundle"
    p = r._build_parser().parse_args(["--max-runs", "3", "--json", "--target-symbol", "005930", "--trade-report-ai-temperature", "0.5"])
    assert (p.max_runs, p.json, p.target_symbol, p.trade_report_ai_temperature) == (3, True, "005930", 0.5)


def test_exclusive_group_exit_code(capsys):
    for argv in (["--trade-report-ai", "--no-trade-report-ai"], ["--max-runs", "x"]):
        with pytest.raises(SystemExit) as exc:
            r._build_parser().parse_args(argv)
        assert exc.value.code == 2
    capsys.readouterr()
    assert r._build_parser().parse_args(["--trade-report-ai"]).trade_report_ai is True
    assert r._build_parser().parse_args(["--no-trade-report-ai"]).trade_report_ai is False


def test_facade_argparse_use_time_patch_reaches_the_owner(monkeypatch):
    import argparse as real
    made = []

    class Spy(real.ArgumentParser):
        def __init__(self, *a, **k):
            made.append(k)
            super().__init__(*a, **k)

    monkeypatch.setattr(r, "argparse", SimpleNamespace(ArgumentParser=Spy))
    parser = r._build_parser()
    assert isinstance(parser, Spy) and made == [{"description": "Generate run-level aggregated execution bundles and per-trade reports."}]


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    assert "from libs.reporting.live_execution_bundle_runner import" not in inspect.getsource(owner)
    assert len(inspect.getsource(r._build_parser).splitlines()) <= 3
