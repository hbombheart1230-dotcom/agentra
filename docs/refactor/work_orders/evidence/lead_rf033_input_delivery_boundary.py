#!/usr/bin/env python3
"""RF-033 input_delivery exact Git-blob, isolated tmp-only behavioral contract.
Run with AGENTRA_RF033_SOURCE=/path/to/exact/input_delivery.py python [-O] harness.py.
No import of project code, no broker/network/fetch, no operational paths.
"""
import ast
import copy
import hashlib
import json
import os
import pathlib
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

EXPECTED = "42525d0321771e99f518f422047f2388782312dd"
src_path = os.environ["AGENTRA_RF033_SOURCE"]
src = pathlib.Path(src_path).read_bytes()
got = hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()
if got != EXPECTED:
    raise SystemExit("SOURCE_BLOB_MISMATCH "+got)
tree = ast.parse(src)
names = {"input_path","publish_input","load_candidate_input","merge_fresh_btc_into_preserved_report"}
fn = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
if {n.name for n in fn} != names:
    raise SystemExit("MISSING_OWNER_FUNCTION")
module = ast.Module(body=fn,type_ignores=[])
ast.fix_missing_locations(module)
cases=0
def ck(cond, name):
    global cases
    cases += 1
    if not cond:
        raise SystemExit("FAIL "+name)
with tempfile.TemporaryDirectory(prefix="rf033_lead_") as td:
    root=pathlib.Path(td)
    reports=root/"reports"
    captures=root/"captures"
    day="2026-10-26"
    tz=ZoneInfo("Asia/Seoul")
    def epoch(d, hm):
        return int(datetime.fromisoformat(d+"T"+hm).replace(tzinfo=tz).timestamp())
    now=epoch(day,"09:05")
    counts={"merge":0,"btc":0,"features":0,"publish":0}
    def read(p):
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    def capture_paths(d,root):
        return {"snapshot":pathlib.Path(root)/d/"btc.json"}
    def merge_capture_into_signal_payload(payload,day,root):
        counts["merge"]+=1
        return {"btc_0855_capture_status":"CAPTURED","btc_status":"OBSERVED"}
    def _btc_0855(signals,day):
        counts["btc"]+=1
        return {"status":signals.get("btc_status","MISSING"),"day":day}
    def build_hypothesis_features(day,candles,btc_signals):
        counts["features"]+=1
        return {"entry_methods":{"p":1},"candles":len(candles)}
    def publish(p,payload):
        counts["publish"]+=1
        pathlib.Path(p).parent.mkdir(parents=True,exist_ok=True)
        pathlib.Path(p).write_text(json.dumps(payload),encoding="utf-8")
    env=dict(Path=pathlib.Path,deepcopy=copy.deepcopy,datetime=datetime,KST=tz,
             epoch=epoch,DEFAULT_ROOT=captures,SCHEMA="q12_candidate_input.v1",
             HYPOTHESIS_CONTRACT_ID="fixture_contract",read=read,
             capture_paths=capture_paths,merge_capture_into_signal_payload=merge_capture_into_signal_payload,
             _btc_0855=_btc_0855,build_hypothesis_features=build_hypothesis_features,
             publish=publish)
    exec(compile(module,"<exact_git_blob_functions>", "exec"),env)
    ip=env["input_path"]
    loader=env["load_candidate_input"]
    writer=env["publish_input"]
    merge=env["merge_fresh_btc_into_preserved_report"]
    input_file=ip(reports,day)
    ck(input_file == reports/"evaluation/baseline_btc_woori_tech"/day/"q12_candidate_input.json","input_path")
    legacy={"features":{"entry_methods":{"legacy":1}},"note":{"a":[1]}}
    orig=copy.deepcopy(legacy)
    a=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(a==legacy and a is not legacy,"no_file_legacy_copy")
    a["note"]["a"].append(2)
    ck(legacy==orig,"legacy_deepcopy")
    rows=[{"ts":epoch(day,"08:59")},{"ts":epoch(day,"09:00")},
          {"ts":epoch(day,"09:04")},{"ts":epoch(day,"09:06")},{"ts":epoch(day,"15:31")}]
    s={"btc_0855_capture_status":"MISSING"}
    result=writer(day=day,reports_root=reports,signals=s,candles=rows,now_epoch=now)
    ck(counts["publish"]==1 and input_file.exists(),"tmp_writer")
    ck(result["features"]["candles"]==2 and result["candle_latest_epoch"]==epoch(day,"09:04"),"lookahead_candle_filter")
    ck(result["btc_capture_status"]=="MISSING" and result["delivery_owner"]=="q12_input_worker","published_schema")
    ck(rows[0]["ts"]==epoch(day,"08:59") and s=={"btc_0855_capture_status":"MISSING"},"writer_inputs_unmodified")
    current=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(current["delivery_status"]=="CURRENT" and current["features"]["entry_methods"]=={"p":1},"fresh_input")
    ck(current["generated_epoch"]==now,"fresh_time")
    stale=loader(reports_root=reports,day=day,now_epoch=now+91,legacy=legacy)
    ck(stale["delivery_status"]=="INPUT_DELAY" and stale["features"]["entry_methods"]=={},"stale_before_close")
    closed=loader(reports_root=reports,day=day,now_epoch=epoch(day,"09:13"),legacy=legacy)
    ck(closed["delivery_status"]=="WINDOW_CLOSED" and closed["delivery_reason"]=="q12_opening_candidate_window_closed","stale_after_close")
    ck(read(input_file)["features"]["entry_methods"]=={"p":1},"stale_not_written_back")
    bad=read(input_file)
    bad["day"]="2026-10-25"
    input_file.write_text(json.dumps(bad),encoding="utf-8")
    invalid=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(invalid["delivery_reason"]=="q12_candidate_input_invalid" and invalid["features"]=={},"day_mismatch")
    bad["day"]=day; bad["schema_version"]="unknown"
    input_file.write_text(json.dumps(bad),encoding="utf-8")
    invalid=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(invalid["delivery_status"]=="INPUT_DELAY","schema_mismatch")
    bad["schema_version"]="q12_candidate_input.v1";bad["generated_epoch"]=now+1
    input_file.write_text(json.dumps(bad),encoding="utf-8")
    invalid=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(invalid["delivery_reason"]=="q12_candidate_input_invalid","future_input")
    input_file.write_text("{broken",encoding="utf-8")
    invalid=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(invalid["delivery_reason"]=="q12_candidate_input_invalid","malformed_input")
    snap=capture_paths(day,captures)["snapshot"]
    snap.parent.mkdir(parents=True,exist_ok=True)
    snap.write_text(json.dumps({"day":day,"target_epoch":epoch(day,"08:55")}),encoding="utf-8")
    over=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(over["features"]["btc_0855"]["status"]=="OBSERVED" and counts["merge"]==1,"capture_overlay")
    ck(over["btc_delivery_source"]==str(snap),"capture_provenance")
    snap.write_text(json.dumps({"day":"2026-10-25","target_epoch":epoch(day,"08:55")}),encoding="utf-8")
    fail=loader(reports_root=reports,day=day,now_epoch=now,legacy=legacy)
    ck(fail["features"]["btc_0855"]["reason"]=="btc_0855_capture_invalid","capture_bad_day")
    snap.write_text(json.dumps({"day":day,"target_epoch":epoch(day,"08:55")}),encoding="utf-8")
    early=loader(reports_root=reports,day=day,now_epoch=epoch(day,"08:54"),legacy=legacy)
    ck(early["features"]["btc_0855"]["reason"]=="btc_0855_capture_invalid","capture_early_time")
    preserved={"features":{"entry_methods":{"legacy":2}},"observations":{"notes":[1]}}
    preserved_orig=copy.deepcopy(preserved)
    no=merge(preserved,{"btc_0855_capture_status":"MISSING"},day)
    ck(no==preserved and no is not preserved,"no_capture_preserves")
    yes=merge(preserved,{"btc_0855_capture_status":"CAPTURED","btc_status":"OBSERVED"},day)
    ck(yes["features"]["btc_0855"]["status"]=="OBSERVED" and yes["btc_delivery_source"]=="canonical_0855_capture","merge_fresh")
    ck(yes["observations"]==preserved["observations"] and preserved==preserved_orig,"merge_preserves_unrelated")
    missing=merge(preserved,{"btc_0855_capture_status":"CAPTURED","btc_status":"MISSING"},day)
    ck("btc_delivery_source" not in missing,"merge_unobserved_no_override")
    all_files={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    ck(all_files=={"reports/evaluation/baseline_btc_woori_tech/"+day+"/q12_candidate_input.json",
                    "captures/"+day+"/btc.json"},"tmp_only_files")
print(f"RF033_LEAD_INPUT_DELIVERY_OK cases={cases} source={EXPECTED[:8]} writes=tmp_only fetch=0 order=0")
