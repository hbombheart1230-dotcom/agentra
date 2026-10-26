import contextlib, copy, io, json, os, socket, sqlite3, subprocess, sys, tempfile, builtins
from pathlib import Path

sys.path.insert(0, os.getcwd())
import importlib.util

_spec = importlib.util.spec_from_file_location("dps", Path("scripts/research/daily_profitability_scorecard.py"))
dps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dps)  # import only; __main__ guard keeps main() from running
from libs.reporting import profitability_recovery_day1 as P

for k in list(os.environ):
    if any(s in k.upper() for s in ("KEY", "SECRET", "TOKEN", "PASSWORD", "ACCOUNT")):
        os.environ.pop(k)


def check(c, m="check"):
    if not c:
        raise SystemExit("CHECK_FAILED: " + str(m))


def _blocked(*a, **k):
    raise RuntimeError("BLOCKED_EFFECT")


socket.socket = _blocked
socket.create_connection = _blocked
subprocess.Popen = _blocked
subprocess.run = _blocked
sqlite3.connect = _blocked
os.system = _blocked
_open = builtins.open
write_attempts = []


def _guard_open(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"):
        write_attempts.append(str(f))
        raise RuntimeError("BLOCKED_WRITE")
    return _open(f, mode, *a, **k)


builtins.open = _guard_open
_wt = Path.write_text  # fixture writer, only into TemporaryDirectory
Path.write_text = lambda *a, **k: _blocked()


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = dps.main(argv)
    return rc, buf.getvalue()


day = "2026-10-20"
with tempfile.TemporaryDirectory() as t:
    root = Path(t) / "reports"
    d = root / "trades" / day
    closed = d / "T_closed"
    closed.mkdir(parents=True)
    _wt(closed / "lifecycle_bundle.json", json.dumps({
        "trade_id": "T_closed", "symbol": "005930", "status": "closed", "trade_outcome": {"return_pct": "-1.5"},
        "story_type": "decision_only", "hold_evidence_thin": False}), encoding="utf-8")
    opened = d / "T_open"
    opened.mkdir()
    _wt(opened / "lifecycle_bundle.json", json.dumps({"trade_id": "T_open", "exit": {"action": "SELL"}, "trade_outcome": {"return_pct": "bad"}}), encoding="utf-8")
    corrupt = d / "T_corrupt"
    corrupt.mkdir()
    _wt(corrupt / "lifecycle_bundle.json", "{not json", encoding="utf-8")
    listing = sorted(str(p) for p in Path(t).rglob("*"))

    sc = P.build_daily_profitability_scorecard(root, day)
    check(sc["schema_version"] == "daily_profitability_scorecard.v1" and sc["total_trades"] == 3, sc["total_trades"])
    check(sc["closed_trades"] == 2, sc["closed_trades"])
    check(sc["loss_trades"] == 1, "only parseable negative return counts as loss")
    check(sc["lifecycle_linkage_missing_count"] == 3 and sc["holding_evidence_thin_count"] == 3)
    check(sc["execution_fields_missing_count"] == 6 * 3, sc["execution_fields_missing_count"])
    check(sc["closed_trade_decision_only_misclassification_count"] == 1)
    check(sc["top_recurring_diagnostic_weakness"] != "none")
    check([r["return_pct"] for r in sc["rows"]] == [-1.5, None, None], [r["return_pct"] for r in sc["rows"]])

    rc, out = run(["--date", day, "--reports-root", str(root), "--json"])
    check(rc == 0 and json.loads(out) == json.loads(json.dumps(sc, ensure_ascii=False)), "json output equals builder output")
    rc2, text = run(["--date", day, "--reports-root", str(root)])
    check(rc2 == 0 and text.splitlines()[0] == f"[Daily Profitability Scorecard] {day}" and "- total trades: 3" in text and "- closed trades: 2" in text and "- loss trades: 1" in text, text)
    check(len(text.splitlines()) == 8, len(text.splitlines()))

    rc3, out3 = run(["--date", "2026-01-01", "--reports-root", str(Path(t) / "missing"), "--json"])
    check(rc3 == 0 and json.loads(out3)["total_trades"] == 0 and json.loads(out3)["top_recurring_diagnostic_weakness"] == "none")

    argexit = {}
    for name, av in (("no_date", []), ("bad_flag", ["--date", day, "--nope"])):
        try:
            run(av)
            argexit[name] = "no_exit"
        except SystemExit as e:
            argexit[name] = e.code
    check(argexit == {"no_date": 2, "bad_flag": 2}, argexit)
    check(listing == sorted(str(p) for p in Path(t).rglob("*")), "scorecard run changed tree")
    check(write_attempts == [], write_attempts)

print(f"RF065_OFFLINE_PEER_OK trades=3 closed=2 loss=1 json_eq=yes text_lines=8 argparse_exit={argexit['no_date']}/{argexit['bad_flag']} "
      f"write_attempts={len(write_attempts)} io=net_sqlite_subprocess_write_blocked debug={__debug__}")
