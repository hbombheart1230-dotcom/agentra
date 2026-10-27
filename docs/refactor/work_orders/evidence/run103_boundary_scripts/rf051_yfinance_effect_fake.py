"""RF-051 owner effect check: yfinance/network/write paths under fakes only.

No network (socket blocked, urlopen faked), no real yfinance (sys.modules fake),
writes confined to a temp dir. Prints one JSON line; exit 0 when all checks hold.
"""
import builtins, io, json, logging, os, socket, sys, tempfile, types
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="rf051_")).resolve()
_real_open = builtins.open
def _guard(path, mode="r", *a, **k):
    if any(c in str(mode) for c in "wax+") and not Path(os.fspath(path)).resolve().is_relative_to(TMP):
        raise PermissionError(f"write outside tmp blocked: {path}")
    return _real_open(path, mode, *a, **k)
builtins.open = io.open = _guard
def _no_net(*a, **k): raise PermissionError("network blocked")
socket.socket.connect = _no_net
socket.create_connection = _no_net
import subprocess; subprocess.Popen.__init__ = _no_net  # type: ignore

out = {}
from libs.market import yfinance_support as ys

# 1) dependency missing -> explicit error / once-per-component log
sys.modules["yfinance"] = None  # forces ImportError
try:
    ys.require_yfinance(); out["missing_raises"] = False
except ys.DataSourceDependencyError as e:
    out["missing_raises"] = e.reason == ys.DEPENDENCY_MISSING_REASON
records = []
h = logging.Handler(); h.emit = records.append; logging.getLogger(ys.__name__).addHandler(h)
ys._REPORTED.clear()
a, b = ys.try_yfinance("rf051"), ys.try_yfinance("rf051")
out["try_missing_none_logged_once"] = a is None and b is None and len(records) == 1
out["status_missing"] = ys.yfinance_dependency_status()["available"] is False

from libs.market import global_sentiment as gs
out["fetch_missing_none"] = gs._fetch_last2_closes_yfinance("^GSPC") is None

# 2) fake yfinance -> closes parsed; empty/raising -> None
class _Hist:
    def __init__(self, vals): self.vals = vals; self.empty = not vals
    def __getitem__(self, k): return self
    def dropna(self): return self
    def tolist(self): return list(self.vals)
calls = []
def _ticker(sym):
    calls.append(sym)
    t = types.SimpleNamespace()
    if sym == "RAISE":
        def hist(**k): raise RuntimeError("fake fetch failure")
    else:
        hist = lambda **k: _Hist({"^GSPC": [100.0, 101.0], "EMPTY": []}.get(sym, [5.0]))
    t.history = hist
    return t
sys.modules["yfinance"] = types.SimpleNamespace(Ticker=_ticker, __version__="fake")
out["fake_pair"] = gs._fetch_last2_closes_yfinance("^GSPC")
out["fake_empty_none"] = gs._fetch_last2_closes_yfinance("EMPTY") is None
out["fake_short_none"] = gs._fetch_last2_closes_yfinance("ONE") is None
out["fake_raise_none"] = gs._fetch_last2_closes_yfinance("RAISE") is None

# 3) macro log write: tmp root only, disabled flag writes nothing
os.environ.pop("PYTEST_CURRENT_TEST", None)
root = TMP / "macro"
gs._write_macro_indicator_log({"k": 1}, policy={"macro_indicator_log_enabled": "false", "macro_indicator_log_root": str(root)})
out["log_disabled_no_write"] = not root.exists()
gs._write_macro_indicator_log({"k": 1}, policy={"macro_indicator_log_enabled": "true", "macro_indicator_log_root": str(root)})
out["log_files"] = sorted(p.name.split("_")[-1] for p in root.rglob("*.json"))
# default root (data/...) is outside tmp -> guarded write swallowed, nothing escapes
gs._write_macro_indicator_log({"k": 1}, policy={"macro_indicator_log_enabled": "true"})
out["default_root_blocked_silently"] = True

# 4) KOFIA bond fetch with network blocked -> no raise
from libs.market import korea_bond_yields as kb
import urllib.request
urllib.request.urlopen = _no_net
try:
    res = kb.fetch_korea_bond_yield_overrides({})
    out["bond_blocked_result_type"] = type(res).__name__
    out["bond_blocked_no_raise"] = True
except Exception as e:
    out["bond_blocked_no_raise"] = f"{type(e).__name__}"

ok = (out["missing_raises"] and out["try_missing_none_logged_once"] and out["status_missing"]
      and out["fetch_missing_none"] and out["fake_pair"] == (100.0, 101.0) and out["fake_empty_none"]
      and out["fake_short_none"] and out["fake_raise_none"] and out["log_disabled_no_write"]
      and out["log_files"] == ["indicators.json", "latest.json"] and out["bond_blocked_no_raise"] is True)
print(json.dumps(out, sort_keys=True, default=str))
print("RF051_EFFECT_OK" if ok else "RF051_EFFECT_FAIL")
sys.exit(0 if ok else 1)
