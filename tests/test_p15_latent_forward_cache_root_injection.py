"""P15 C02-1: latent forward candle cache root is explicitly injectable; default path unchanged."""
from __future__ import annotations

import inspect
import json
from datetime import datetime
from pathlib import Path

from libs.reporting.opening_rank1_shadow import latent_forward as lf

DAY = "2026-10-20"
EPOCH = int(datetime.fromisoformat(f"{DAY}T09:10:00+09:00").timestamp())


def _watch():
    return {"through_day": DAY, "rows": [{"watch_id": "w1", "symbol": "005930", "initial_day": DAY, "redetections": [
        {"first_signal_evidence": {"day": DAY, "decision_epoch": EPOCH, "decision_id": "d1", "rank": 1}}]}]}


def _setup(tmp_path, status="VALID"):
    day_dir = tmp_path / "opening" / DAY
    day_dir.mkdir(parents=True)
    (day_dir / "opening_rank1_shadow_daily.json").write_text(json.dumps({"day_status": status}), encoding="utf-8")
    out = tmp_path / "opening" / "latent"
    out.mkdir()
    return out


def _fakes(monkeypatch, calls):
    rows = [{"ts": EPOCH + 60 * i, "open": 100.0 + i, "high": 102.0 + i, "low": 99.0, "close": 101.0 + i} for i in (1, 2, 3)]

    def fake_load(**kw):
        calls.append(kw)
        return {s: list(rows) for s in kw["symbols"]}, {}

    monkeypatch.setattr(lf, "load_opening_candles", fake_load)
    monkeypatch.setattr(lf, "load_broker_cost_profile", lambda *_a, **_k: {})
    monkeypatch.setattr(lf, "build_evaluation_cost_bases", lambda *_a, **_k: {"live_deployment_equity": {"total_drag_with_slippage_pct": 0.1}, "mock_observed": {"total_drag_with_slippage_pct": 0.0}})


def test_explicit_cache_root_is_only_cache_location_and_is_reused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = _setup(tmp_path)
    calls: list = []
    _fakes(monkeypatch, calls)
    cache = tmp_path / "cache"
    r1 = lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp_path / "state.json", output_root=out, allow_fresh_fetch=False, cache_root=cache)
    cached = cache / DAY / "005930.json"
    assert cached.is_file() and [p for p in cache.rglob("*") if p.is_file()] == [cached]
    assert json.loads(cached.read_text(encoding="utf-8"))["symbol"] == "005930"
    j1, m1 = Path(r1["json"]).read_text(encoding="utf-8"), Path(r1["markdown"]).read_text(encoding="utf-8")
    r2 = lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp_path / "state.json", output_root=out, allow_fresh_fetch=False, cache_root=cache)
    assert len(calls) == 1 and r2["summary"] == r1["summary"]
    assert Path(r2["json"]).read_text(encoding="utf-8") == j1 and Path(r2["markdown"]).read_text(encoding="utf-8") == m1
    assert not (tmp_path / "data").exists()                                   # no CWD-relative default cache created
    assert calls[0]["allow_fresh_fetch"] is False and calls[0]["symbols"] == ("005930",)
    assert r1["summary"]["observed_30m_count"] == 0 and r1["summary"]["fresh_trigger_count"] == 1


def test_allow_fresh_fetch_true_is_forwarded_unchanged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = _setup(tmp_path)
    calls: list = []
    _fakes(monkeypatch, calls)
    lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp_path / "s.json", output_root=out, allow_fresh_fetch=True, cache_root=tmp_path / "cache")
    assert calls[0]["allow_fresh_fetch"] is True


def test_invalid_trigger_day_touches_neither_cache_nor_loader(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = _setup(tmp_path, status="INVALID")
    calls: list = []
    _fakes(monkeypatch, calls)
    cache = tmp_path / "cache"
    r = lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp_path / "s.json", output_root=out, allow_fresh_fetch=True, cache_root=cache)
    assert calls == [] and not cache.exists() and not (tmp_path / "data").exists()
    assert r["summary"]["excluded_trigger_count"] == 1
    rows = json.loads(Path(r["json"]).read_text(encoding="utf-8"))["rows"]
    assert rows[0]["forward_status"] == "EXCLUDED_TRIGGER_DAY_INTEGRITY"


def test_signature_is_backward_compatible_and_default_path_is_static():
    sig = inspect.signature(lf.build_latent_reactivation_forward)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == ["watch_payload", "state_path", "output_root", "allow_fresh_fetch", "cache_root"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params)
    assert sig.parameters["cache_root"].default is None
    src = inspect.getsource(lf.build_latent_reactivation_forward)
    assert 'Path("data/research/opening_rank1_shadow/latent_forward_candles")' in src   # default path unchanged (statically confirmed, never executed)
