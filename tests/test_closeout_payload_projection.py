"""Closeout memory fix: the shadow-payload loader's opt-in `keys=` projection.

Pins (a) the legacy full-payload path is unchanged, (b) `keys=` keeps only the requested
top-level keys, (c) `q9_decision_windows.json` is never opened when the q9 key is not
requested, (d) every consumer converted to `keys=` provably reads only `candidates` /
`generated_at`, and (e) the consumer outputs are identical with and without the projection.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import libs.reporting.quant_shadow_candidate_evaluation as qsce
from libs.reporting.q8_shadow_blocker_review import build_q8_shadow_blocker_review
from libs.reporting.quant_shadow_candidate_evaluation import (
    CANDIDATE_EVALUATION_PAYLOAD_KEYS,
    build_quant_shadow_candidate_evaluation,
    iter_quant_shadow_candidate_payloads,
    load_quant_shadow_candidate_payloads,
)
from libs.reporting.strategist_llm_evaluation import build_strategist_llm_evaluation

ROOT = Path(__file__).resolve().parents[1]
DAY = "2026-10-07"


def _candidate(symbol: str, reason: str, role: str, rank: int, base_price: float) -> dict:
    return {
        "symbol": symbol,
        "reason": reason,
        "shadow_role": role,
        "rank": rank,
        "quant_tactic_id": "vwap_reclaim_pullback",
        "would_enter": rank == 1,
        "shadow_forward_base": {"available": True, "baseline_epoch": 1791331200, "baseline_price": base_price},
    }


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """reports/ + data/logs/quant_shadow_candidates/<day>/*.json + q9_decision_windows.json."""
    monkeypatch.chdir(tmp_path)  # attach_forward_outcomes() default reads ./data/state.json
    reports = tmp_path / "reports"
    shadow_dir = tmp_path / "data" / "logs" / "quant_shadow_candidates" / DAY
    shadow_dir.mkdir(parents=True)
    windows_path = reports / "operator_summary" / "daily" / DAY / "q9_decision_windows.json"
    windows_path.parent.mkdir(parents=True)
    windows_path.write_text(
        json.dumps({"windows": [{"decision_id": "d1", "commander_final": {"selected_symbol": "005930", "decision": "BUY"}}]}),
        encoding="utf-8",
    )
    for index, (symbol, reason) in enumerate(
        [("005930", "breakout_not_ready"), ("000660", "volume_confirmation_missing"), ("005930", "breakout_not_ready")]
    ):
        payload = {
            "schema_version": "x.v1",
            "run_id": f"run-{index}",
            "q9_decision_id": "d1",
            "generated_at": f"2026-10-07T00:0{index}:00+00:00",
            "trigger": "tick",
            "summary": {"n": index},
            "candidates": [_candidate(symbol, reason, "top_pick", 1, 100.0 + index), _candidate("035720", reason, "runner_up_evaluated", 2, 50.0)],
            "q9_decision_candidates": [{"symbol": symbol, "rank": 1, "q9_decision_role": "B_STRATEGIST_RANKED", "blob": "x" * 2000}],
        }
        (shadow_dir / f"2026100700{index}000Z_run{index}.json").write_text(json.dumps(payload), encoding="utf-8")
    (shadow_dir / "latest.json").write_text(json.dumps({"ignored": True}), encoding="utf-8")
    return {"reports": reports, "windows": windows_path, "shadow_dir": shadow_dir}


def test_keys_subset_retains_only_requested_keys(world):
    payloads = load_quant_shadow_candidate_payloads(
        reports_root=world["reports"], days=[DAY], keys=CANDIDATE_EVALUATION_PAYLOAD_KEYS
    )
    assert len(payloads) == 3  # latest.json still excluded
    for payload in payloads:
        assert set(payload) == {"candidates", "generated_at"}
        assert len(payload["candidates"]) == 2


def test_keys_none_is_the_unchanged_legacy_path(world):
    payloads = load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY])
    explicit = load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=None)
    assert payloads == explicit
    for payload in payloads:
        assert {"q9_decision_candidates", "summary", "run_id", "trigger"} <= set(payload)
    # legacy augmentation still adds the commander row from q9_decision_windows.json
    roles = {row["q9_decision_role"] for row in payloads[0]["q9_decision_candidates"]}
    assert "C_COMMANDER_FINAL" in roles


def _record_reads(monkeypatch):
    opened: list[str] = []
    real = qsce._read_json

    def spy(path):
        opened.append(Path(path).name)
        return real(path)

    monkeypatch.setattr(qsce, "_read_json", spy)
    return opened


def test_q9_windows_not_opened_when_q9_key_excluded(world, monkeypatch):
    opened = _record_reads(monkeypatch)
    load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=CANDIDATE_EVALUATION_PAYLOAD_KEYS)
    assert "q9_decision_windows.json" not in opened
    assert sum(name.endswith(".json") and name != "latest.json" for name in opened) == 3


@pytest.mark.parametrize("keys", [None, ("candidates", "generated_at", "q9_decision_candidates")])
def test_q9_windows_still_read_when_needed(world, monkeypatch, keys):
    opened = _record_reads(monkeypatch)
    load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=keys)
    assert "q9_decision_windows.json" in opened


def test_keys_projection_is_lazy_per_file(world):
    iterator = iter_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=("candidates",))
    first = next(iterator)
    assert set(first) == {"candidates"}


def test_missing_requested_key_is_simply_absent(world):
    payloads = load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=("candidates", "no_such_key"))
    assert all(set(p) == {"candidates"} for p in payloads)


def _minute_rows():
    return {
        "005930": [
            {"ts": 1791331200, "close": 100.0, "high": 100.0, "low": 100.0},
            {"ts": 1791331500, "close": 101.0, "high": 102.0, "low": 99.5},
            {"ts": 1791332100, "close": 103.0, "high": 104.0, "low": 99.0},
        ],
        "000660": [{"ts": 1791331200, "close": 100.0, "high": 100.0, "low": 100.0}, {"ts": 1791331500, "close": 99.0, "high": 100.0, "low": 98.0}],
        "035720": [{"ts": 1791331200, "close": 50.0, "high": 50.0, "low": 50.0}, {"ts": 1791331500, "close": 51.0, "high": 51.0, "low": 50.0}],
    }


def test_consumer_outputs_identical_with_and_without_projection(world):
    full = load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY])
    slim = load_quant_shadow_candidate_payloads(reports_root=world["reports"], days=[DAY], keys=CANDIDATE_EVALUATION_PAYLOAD_KEYS)

    assert build_quant_shadow_candidate_evaluation(slim) == build_quant_shadow_candidate_evaluation(full)
    assert build_q8_shadow_blocker_review(slim, minute_rows_by_symbol=_minute_rows()) == build_q8_shadow_blocker_review(
        full, minute_rows_by_symbol=_minute_rows()
    )
    rows = [{"symbol": "005930", "side": "BUY", "return_pct": 1.0}]
    assert build_strategist_llm_evaluation(rows, slim) == build_strategist_llm_evaluation(rows, full)
    # candidate counts unchanged, and ordering is the payload (file-name) order
    assert [len(p["candidates"]) for p in slim] == [len(p["candidates"]) for p in full]
    assert [p["generated_at"] for p in slim] == [p["generated_at"] for p in full]


def _payload_keys_read(source_path: str, function_names: set[str]) -> set[str]:
    """String keys read off the loop variable named `payload` inside the given functions."""
    tree = ast.parse((ROOT / source_path).read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name in function_names):
            continue
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "get"
                and isinstance(sub.func.value, ast.Name)
                and sub.func.value.id == "payload"
                and sub.args
                and isinstance(sub.args[0], ast.Constant)
            ):
                found.add(sub.args[0].value)
            if (
                isinstance(sub, ast.Subscript)
                and isinstance(sub.value, ast.Name)
                and sub.value.id == "payload"
                and isinstance(sub.slice, ast.Constant)
            ):
                found.add(sub.slice.value)
    return found


@pytest.mark.parametrize(
    "path,functions",
    [
        ("libs/reporting/quant_shadow_candidate_evaluation.py", {"build_quant_shadow_candidate_evaluation"}),
        ("libs/reporting/q8_shadow_blocker_review.py", {"_candidate_rows"}),
        ("libs/reporting/strategist_llm_evaluation.py", {"_shadow_rows"}),
    ],
)
def test_converted_consumers_read_only_the_projected_keys(path, functions):
    keys = _payload_keys_read(path, functions)
    assert keys, f"expected to find payload reads in {path}"
    assert keys <= set(CANDIDATE_EVALUATION_PAYLOAD_KEYS), (path, keys)


def _calls_with_projection(source_path: str, function_name: str) -> bool:
    tree = ast.parse((ROOT / source_path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            for sub in ast.walk(node):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Name)
                    and sub.func.id == "load_quant_shadow_candidate_payloads"
                ):
                    return any(
                        kw.arg == "keys" and isinstance(kw.value, ast.Name) and kw.value.id == "CANDIDATE_EVALUATION_PAYLOAD_KEYS"
                        for kw in sub.keywords
                    )
    return False


def test_closeout_path_actually_uses_the_projection():
    assert _calls_with_projection("libs/reporting/q8_shadow_blocker_review.py", "generate_q8_shadow_blocker_review")
    assert _calls_with_projection("libs/reporting/operator_period_summary.py", "build_operator_daily_summary_artifact_payload")
