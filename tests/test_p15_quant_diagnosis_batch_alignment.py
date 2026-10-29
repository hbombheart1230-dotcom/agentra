"""P15 C02-4: batch diagnosis writer rejects misaligned input lists before writing anything."""
from __future__ import annotations

import json

import pytest

from libs.reporting.quant_trade_diagnosis import writer as w

DAY = "2026-10-20"


@pytest.fixture
def built(monkeypatch):
    log = []

    def build(**kw):
        log.append(kw["model"]["trade_id"])
        return {"trade_id": kw["model"]["trade_id"], "k": 1}

    monkeypatch.setattr(w, "build_quant_trade_diagnosis", build)
    monkeypatch.setattr(w, "render_quant_trade_diagnosis", lambda p: f"# {p['trade_id']}\n")
    monkeypatch.setattr(w, "resolve_conditional_alpha_context", lambda m, e: {})
    return log


def _dirs(tmp_path, n):
    out = []
    for i in range(n):
        d = tmp_path / f"t{i}"
        d.mkdir()
        out.append(d)
    return out


def _call(tmp_path, dirs, models, evals, attrs):
    return w.write_quant_trade_diagnoses_for_day(
        reports_root=tmp_path / "reports", day=DAY, trade_dirs=dirs,
        models=[{"trade_id": f"M{i}", "symbol": "S"} for i in range(models)],
        evaluations=[{} for _ in range(evals)], attributions=[{} for _ in range(attrs)],
        root_cause_report={}, entry_timing_report={}, conditional_alpha_episodes=[])


@pytest.mark.parametrize("counts", [(2, 2, 1, 2), (2, 2, 2, 1), (2, 1, 2, 2), (1, 2, 2, 2)])
def test_mismatched_lengths_raise_with_counts_and_write_nothing(tmp_path, built, counts):
    dirs = _dirs(tmp_path, counts[0])
    with pytest.raises(ValueError) as exc:
        _call(tmp_path, dirs, counts[1], counts[2], counts[3])
    msg = str(exc.value)
    for name, n in zip(("trade_dirs", "models", "evaluations", "attributions"), counts):
        assert f"'{name}': {n}" in msg
    assert built == []
    assert not any((d / "reports").exists() for d in dirs) and not (tmp_path / "reports").exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(d.name for d in dirs)


def test_aligned_lengths_keep_order_return_keys_and_report_bytes(tmp_path, built):
    dirs = _dirs(tmp_path, 2)
    out = _call(tmp_path, dirs, 2, 2, 2)
    assert set(out) == {"schema_version", "behavior_effect", "day", "trade_count", "written_count", "written"}
    assert out["trade_count"] == out["written_count"] == 2 and built == ["M0", "M1"]
    assert [r["trade_id"] for r in out["written"]] == ["M0", "M1"]
    for i, d in enumerate(dirs):
        j = (d / "reports" / "quant_trade_diagnosis.json").read_bytes()
        assert j == (json.dumps({"trade_id": f"M{i}", "k": 1}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        assert (d / "reports" / "quant_trade_diagnosis.md").read_text(encoding="utf-8") == f"# M{i}\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["t0", "t1"]            # only tmp dirs exist; no broker or real trades path used


def test_zero_everywhere_is_still_accepted(tmp_path, built):
    out = _call(tmp_path, [], 0, 0, 0)
    assert out["trade_count"] == 0 and out["written"] == [] and built == []
