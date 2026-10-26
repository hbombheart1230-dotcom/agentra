import socket, subprocess, sqlite3, sys, tempfile, copy, builtins, os
from pathlib import Path
sys.path.insert(0, os.getcwd())

from libs.reporting.baseline_btc_woori_tech.comparison import build_comparison, _read, _metric, _gross_returns
from libs.reporting.baseline_btc_woori_tech.forward_returns import attach_forward_returns, summarize, summarize_policy_variant
from libs.reporting.baseline_btc_woori_tech import contracts as C

def check(c, m='check'):
    if not c: raise SystemExit('CHECK_FAILED: ' + m)

def _blocked(*a, **k): raise RuntimeError("BLOCKED_EFFECT")
socket.socket = _blocked; socket.create_connection = _blocked
subprocess.Popen = _blocked; sqlite3.connect = _blocked
_open = builtins.open
def _guard_open(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"): raise RuntimeError("BLOCKED_WRITE")
    return _open(f, mode, *a, **k)
builtins.open = _guard_open
_wt = Path.write_text; Path.write_text = lambda *a, **k: _blocked()

KST = 9 * 3600
base = 1_767_000_000
def candles(n=400):
    return [{"ts": base + i * 60, "close": 100 + i * 0.01, "high": 100.5 + i * 0.01, "low": 99.5 + i * 0.01} for i in range(n)]
dec = [{"decision_id": "d1", "generated_at": "x", "eligible": True, "action": "BUY",
        "local_features": {"available": True, "baseline_epoch": base, "baseline_price": 100.0, "baseline_raw_ts": "r"},
        "btc_signal": {"positive": True},
        "policy_variants": {C.STRONG_BTC_POLICY_ID: {"eligible": True}}},
       {"decision_id": "d2", "eligible": False, "local_features": {}, "btc_signal": None}]
dec_snapshot = copy.deepcopy(dec); cds = candles()

markers = {}
# forward_returns: normal + missing/bad
rows = attach_forward_returns(dec, candles=cds)
check(dec == dec_snapshot, "input mutated")
check(len(rows) == 2 and rows[0]["symbol"] == C.TARGET_SYMBOL, 'len(rows) == 2 and rows[0]["symbol"] == C.TARGET_S')
check(rows[0]["returns"]["+5m"]["status"] == "observed", rows[0]["returns"]["+5m"])
check(rows[1]["returns"]["+5m"]["status"] == "pending", 'rows[1]["returns"]["+5m"]["status"] == "pending"')
check(attach_forward_returns([], candles=[]) == [])
check(attach_forward_returns([{}], candles=[])[0]["available"] is False)
try: attach_forward_returns([{"local_features": "bad"}], candles=[]); bad_state = "ok"
except AttributeError: bad_state = "AttributeError"
s = summarize(rows, cost_pct=0.1, slippage_pct=0.05)
from libs.reporting.baseline_samsung_hynix.contracts import HORIZONS as SH
check([h["horizon"] for h in s["horizons"]] == list(SH), "summary horizons are samsung 7-horizon set")
sv = summarize_policy_variant(rows, dec, policy_id=C.STRONG_BTC_POLICY_ID, cost_pct=0.1, slippage_pct=0.05)
check("eligible" not in str(rows) or rows[0]["eligible"] is True and "policy_variant_id" not in rows[0], "rows mutated")
check(summarize_policy_variant([], [], policy_id="x", cost_pct=0, slippage_pct=0)["horizons"])

# comparison
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "q9").mkdir()
    out = build_comparison(day="2026-10-26", summary=s, forward_rows=rows, decisions=dec, cost_pct=0.1, slippage_pct=0.05,
                           reports_root=t / "reports", q9_root=t / "q9", state_path=t / "state.json")
    check(out["evidence_status"] == "INSUFFICIENT_EVIDENCE" and len(out["horizons"]) == 4, 'out["evidence_status"] == "INSUFFICIENT_EVIDENCE" ')
    check(out["horizons"][0]["btc_momentum_only"]["trade_count"] == 1, 'out["horizons"][0]["btc_momentum_only"]["trade_cou')
    check(out["horizons"][0]["woori_buy_and_hold"]["trade_count"] == 1, 'out["horizons"][0]["woori_buy_and_hold"]["trade_co')
    # bad q10 file => fail-soft {}
    (t / "reports" / "evaluation" / "baseline_samsung_hynix" / "2026-10-26").mkdir(parents=True)
    p = t / "reports" / "evaluation" / "baseline_samsung_hynix" / "2026-10-26" / "baseline_samsung_hynix_forward_returns.json"
    _wt(p, "{not json", encoding="utf-8")
    check(_read(p) == {}, '_read(p) == {}')
    _wt(p, "[1]", encoding="utf-8"); assert _read(p) == {}
    check(_read(t / "missing.json") == {}, '_read(t / "missing.json") == {}')
    # valid q10 with trade_count>0 -> COMPARABLE
    import json
    _wt(p, json.dumps({"summary": {"horizons": [{"horizon": "+5m", "top1_net": {"count": 2, "win_rate": 50}}]}}), encoding="utf-8")
    out2 = build_comparison(day="2026-10-26", summary={"horizons": [{"horizon": "+5m", "eligible_entries_net": {"count": 1}}]},
                            forward_rows=rows, decisions=dec, cost_pct=0, slippage_pct=0,
                            reports_root=t / "reports", q9_root=t / "q9", state_path=t / "state.json")
    check(out2["evidence_status"] == "COMPARABLE", 'out2["evidence_status"] == "COMPARABLE"')
    # malformed summary shape
    try:
        build_comparison(day="d", summary={"horizons": ["x"]}, forward_rows=[], decisions=[], cost_pct=0, slippage_pct=0,
                         reports_root=t, q9_root=t / "q9", state_path=t / "s"); shape = "ok"
    except AttributeError: shape = "AttributeError"
    # None metric values
    check(_metric({"count": None, "win_rate": None})["trade_count"] == 0)
    check(_gross_returns([{"returns": None}, {"returns": {"+5m": {"status": "observed", "return_pct": None}}}], "+5m") == [0.0])
    # zip truncation: decisions shorter than rows
    out3 = build_comparison(day="d", summary={}, forward_rows=rows, decisions=dec[:1], cost_pct=0, slippage_pct=0,
                            reports_root=t, q9_root=t / "q9", state_path=t / "s")
    check(out3["horizons"][0]["btc_momentum_only"]["trade_count"] == 1, 'out3["horizons"][0]["btc_momentum_only"]["trade_co')
print(f"RF033_BOUNDARY_OK forward=2 comparison=4 mutation=none bad_local_features={bad_state} bad_summary_shape={shape} io=read_only_blocked_net_write debug={__debug__}")
