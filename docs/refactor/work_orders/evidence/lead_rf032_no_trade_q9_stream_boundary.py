"""RF-032 read-only isolated q9-window stream consumer test.
Source transcription from integration/p1.5 libs/reporting/evaluation/no_trade_attribution.py
GitHub blob 967aca16db2926cc00b0a7761d1534cf4b84540b.
This is not a full-module or whole-repository test; dependencies are injected fakes.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections.abc import Mapping


def _q9_window_view(row: Mapping[str, object]) -> dict[str, object]:
    """The only parts of a q9 window `build_no_trade_attribution_report` reads (non-mappings read as {})."""
    view: dict[str, object] = {}
    scanner = row.get("scanner_control")
    if isinstance(scanner, Mapping):
        view["scanner_control"] = {"top1_symbol": scanner.get("top1_symbol")}
    strategist = row.get("strategist_selection")
    if isinstance(strategist, Mapping):
        view["strategist_selection"] = {"selected_symbol": strategist.get("selected_symbol")}
    commander = row.get("commander_final")
    if isinstance(commander, Mapping):
        observation = commander.get("monitor_observation")
        view["commander_final"] = {
            key: commander.get(key)
            for key in ("selected_symbol", "decision", "monitor_intent", "reason", "detail", "monitor_reason")
        }
        if isinstance(observation, Mapping):
            view["commander_final"]["monitor_observation"] = {"reason": observation.get("reason")}
    return view


def _q9_windows(reports_root: Path, day: str) -> list[dict[str, object]]:
    # Streamed and reduced to the fields the report reads: the ~120 MB windows file is no longer parsed
    # whole (and its regular rows are not all kept) just to count a handful of fields per window.
    path = reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    windows: list[dict[str, object]] = []
    try:
        for row in iter_json_array(path, "windows"):
            if isinstance(row, dict) and not is_synthetic_evaluation_row(row) and is_regular_session_evaluation_row(row):
                windows.append(_q9_window_view(row))
    except ValueError:
        return []  # unreadable windows file == no windows (what _read_json -> {} gave)
    return windows


count=0

def check(cond, label):
    global count
    if not cond: raise RuntimeError(f"FAIL {label}")
    count+=1

raw={"scanner_control":{"top1_symbol":"005930","extra":12},
     "strategist_selection":{"selected_symbol":"000660","noise":4},
     "commander_final":{"selected_symbol":"005930","decision":"approve","monitor_intent":"NOOP",
                         "reason":"test","detail":"d","monitor_reason":None,
                         "monitor_observation":{"reason":"monitor","unused":7},"ignored":42},
     "unrelated":{"large":"payload"}}
view=_q9_window_view(raw)
check(set(view)=={"scanner_control","strategist_selection","commander_final"},"projection keys")
check(view["scanner_control"]=={"top1_symbol":"005930"},"scanner reduced")
check(view["strategist_selection"]=={"selected_symbol":"000660"},"strategist reduced")
check(view["commander_final"]["monitor_observation"]=={"reason":"monitor"},"observation reduced")
check("ignored" not in view["commander_final"],"commander extra dropped")
check(raw["commander_final"]["monitor_observation"]["unused"]==7,"input unmodified")
check(_q9_window_view({"scanner_control":[],"strategist_selection":0,"commander_final":"bad"})=={},"nonmapping")
check(_q9_window_view({"commander_final":{"monitor_observation":[]}})["commander_final"].get("monitor_observation") is None,"malformed observation")

seen=[]
def is_synthetic_evaluation_row(r): return r.get("kind")=="synthetic"
def is_regular_session_evaluation_row(r): return r.get("kind")!="offhours"
def iter_json_array(path, key):
    seen.append((path,key))
    yield raw
    yield {"kind":"synthetic"}
    yield {"kind":"offhours"}
    yield "not a dict"
    yield {"scanner_control":{"top1_symbol":"035420"}}

root=Path("/tmp/rf032_fake_reports")
rows=_q9_windows(root,"2026-10-26")
check(len(rows)==2,"regular rows only")
check(rows[1]=={"scanner_control":{"top1_symbol":"035420"}},"second reduced")
check(seen==[(root/"operator_summary"/"daily"/"2026-10-26"/"q9_decision_windows.json","windows")],"exact path/key")
check(raw["unrelated"]=={"large":"payload"},"no input mutation")

def iter_json_array(path,key):
    yield raw
    raise ValueError("bad streamed json")
check(_q9_windows(root,"2026-10-26")==[],"ValueError drops partial")

def iter_json_array(path,key):
    raise OSError("unavailable read")
    yield raw
try: _q9_windows(root,"2026-10-26")
except OSError: check(True,"OSError propagated")
else: check(False,"OSError propagated")

def iter_json_array(path,key):
    raise RuntimeError("unexpected reader failure")
    yield raw
try: _q9_windows(root,"2026-10-26")
except RuntimeError: check(True,"RuntimeError propagated")
else: check(False,"RuntimeError propagated")

print(f"RF032_NO_TRADE_Q9_STREAM_OK cases={count} writes=0 network=0 broker=0")
