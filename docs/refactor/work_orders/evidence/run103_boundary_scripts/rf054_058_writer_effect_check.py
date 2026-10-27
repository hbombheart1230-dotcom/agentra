# A OWNER temp-only writer/effect check for RF-054 libs/performance and RF-058 libs/storage (real writers, no fakes).
# Usage: (cd <repo>; python [-O] rf054_058_writer_effect_check.py). All writes confined to a mkdtemp dir; network/subprocess blocked.
import os, sys, json, socket, subprocess, tempfile, shutil, threading
from pathlib import Path
sys.path.insert(0, os.getcwd())
def blk(*a, **k): raise OSError("blocked")
socket.socket.connect = blk
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blk)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
tmp = Path(tempfile.mkdtemp(prefix="rf054058_"))
try:
    from libs.performance import performance_aggregator as pa, playbook_stats as ps, strategy_memory as sm
    from libs.storage.state_store import StateStore
    from libs.storage.proposal_store import ProposalStore
    day = "2026-10-27"; rr = tmp / "reports"
    for i, (pb, ret) in enumerate([("pbA", 1.5), ("pbA", -0.5), ("pbB", -2.0)]):
        d = rr / "trades" / day / f"TRD_{i}"; d.mkdir(parents=True)
        (d / "lifecycle_bundle.json").write_text(json.dumps({"symbol": f"00{i}", "playbook": pb, "return_pct": ret}), encoding="utf-8")
    (rr / "trades" / day / "TRD_bad").mkdir(); (rr / "trades" / day / "TRD_bad" / "lifecycle_bundle.json").write_text("{broken", encoding="utf-8")
    before = {p for p in tmp.rglob("*")}
    s = pa.write_performance_summary(rr, day=day)
    check(s["day"] == day, "summary day")
    paths = pa.performance_artifact_paths(rr, day)
    check(paths["summary_json"].is_file() and paths["symbol_stats_json"].is_file(), "summary/symbol files")
    check(json.loads(paths["summary_json"].read_text(encoding="utf-8"))["day"] == day, "summary json")
    p = ps.write_playbook_stats(rr, day=day)
    check(Path(p["artifact_path"]).is_file(), "playbook file")
    m = sm.write_strategy_memory(rr, day=day)
    check(m["status"] in ("ok", "empty") and Path(m["artifact_path"]).is_file(), "memory file")
    os.environ["STRATEGY_MEMORY_PERSIST_ENABLED"] = "off"
    paths["strategy_memory_json"].unlink()
    off = sm.write_strategy_memory(rr, day=day)
    check(off["status"] == "disabled" and not paths["strategy_memory_json"].exists(), "env disabled writes nothing")
    del os.environ["STRATEGY_MEMORY_PERSIST_ENABLED"]
    outside = {q for q in tmp.rglob("*")} - before
    check(all(str(q).startswith(str(rr)) for q in outside), "writes only under reports root")
    # storage
    st = StateStore(str(tmp / "st" / "state.json"))
    d0 = st.load(); check(d0["mock_cash"] == 0.0 and not st.path.exists(), "default load, no write")
    st.save({"mock_cash": 5.0, "open_positions": 1}); check(st.load()["mock_cash"] == 5.0, "roundtrip")
    st.path.write_text("{corrupt", encoding="utf-8"); check(st.load()["mock_cash"] == 0.0, "corrupt resets")
    st.save({"mock_cash": 7.0}); check(st.load()["mock_cash"] == 7.0, "save over corrupt")
    st.save({"mock_positions": ["X"], "broker_truth_position_reconciliation": {"authoritative": True, "generated_at": "2026-10-27T01:00:00Z"}})
    st.save({"mock_positions": ["stale"], "broker_truth_position_reconciliation": {"authoritative": True, "generated_at": "2026-10-27T00:00:00Z"}})
    check(st.load()["mock_positions"] == ["X"], "newer broker truth preserved")
    check(not [q for q in st.path.parent.iterdir() if ".tmp." in q.name], "no leftover tmp")
    ths = [threading.Thread(target=lambda i=i: st.save({"mock_cash": float(i)})) for i in range(4)]
    [t.start() for t in ths]; [t.join() for t in ths]
    check(isinstance(st.load()["mock_cash"], float) and not [q for q in st.path.parent.iterdir() if ".tmp." in q.name], "threaded saves intact")
    ps_ = ProposalStore(str(tmp / "pp" / "p.jsonl")); ps_.save({"a": "한글"}); ps_.save({"b": 2})
    lines = ps_.path.read_text(encoding="utf-8").splitlines()
    check(len(lines) == 2 and json.loads(lines[0])["a"] == "한글", "jsonl append")
    print("RF054_058_WRITER_EFFECT_OK files_under_reports=%d debug=%s" % (len(outside), __debug__))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
