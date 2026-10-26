#!/usr/bin/env python3
"""RF-033 InputWorker.tick exact source AST, fake-only consumer/exception test."""
import ast,hashlib,os,pathlib
from datetime import datetime
from zoneinfo import ZoneInfo
src=pathlib.Path(os.environ["AGENTRA_RF033_WORKER_SOURCE"]).read_bytes()
expected="2184c9ee571411baadc728c71863cfa0af3c3967"
got=hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()
if got!=expected:raise SystemExit("SOURCE_MISMATCH "+got)
tree=ast.parse(src)
cl=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=="InputWorker"]
if len(cl)!=1:raise SystemExit("CLASS_NOT_FOUND")
module=ast.Module(body=cl,type_ignores=[])
ast.fix_missing_locations(module)
day="2026-10-26"
def epoch(d,hm):return int(datetime.fromisoformat(d+"T"+hm).replace(tzinfo=ZoneInfo("Asia/Seoul")).timestamp())
state={"captured":True,"research":{"btc_usd_daily":[1],"woori_daily":[2]},"research_fail":False,"candle_fail":False,"publish_fail":False}
calls={"research":0,"candles":0,"publish":0}
def merge_capture_into_signal_payload(x,day):
    return {"btc_0855_capture_status":"CAPTURED" if state["captured"] else "MISSING"}
def load_btc_signal_rows(day):
    calls["research"]+=1
    if state["research_fail"]:raise RuntimeError("research provider failed")
    return {"research_context":state["research"]}
def load_woori_candles(day,state_path,allow_fresh_fetch):
    calls["candles"]+=1
    if not allow_fresh_fetch:raise SystemExit("EXPECTED_TRUE_FETCH_FLAG")
    if state["candle_fail"]:raise OSError("candle provider failed")
    return [{"ts":epoch(day,"09:01")}]
def publish_input(**kwargs):
    calls["publish"]+=1
    if state["publish_fail"]:raise PermissionError("publish failed")
    return kwargs
env=dict(epoch=epoch,merge_capture_into_signal_payload=merge_capture_into_signal_payload,
         load_btc_signal_rows=load_btc_signal_rows,load_woori_candles=load_woori_candles,
         publish_input=publish_input)
exec(compile(module,"<exact_worker_class>","exec"),env)
Worker=env["InputWorker"]
cases=0
def ck(x,label):
    global cases
    cases+=1
    if not x:raise SystemExit("FAIL "+label)
w=Worker(day,"/fake_reports","/fake_state")
pre=w.tick(epoch(day,"08:59"))
ck(pre["candles"]==[] and calls["candles"]==0,"pre_open_no_candle_fetch")
ck(pre["signals"]["research_context"]==state["research"],"research_injected")
ck(calls["research"]==1,"first_research")
mid=w.tick(epoch(day,"09:00"))
ck(len(mid["candles"])==1 and calls["candles"]==1,"capture_opens_candle")
ck(calls["research"]==1,"research_cache")
ck(mid["reports_root"]=="/fake_reports" and mid["now_epoch"]==epoch(day,"09:00"),"publish_forward")
state["captured"]=False
no=w.tick(epoch(day,"09:01"))
ck(no["candles"]==[] and calls["candles"]==1,"uncaptured_no_fetch")
state["captured"]=True
state["research_fail"]=True
w2=Worker(day,"/fake_reports","/fake_state")
failed=w2.tick(epoch(day,"08:59"))
ck(failed["signals"]["research_context"]=={} and w2.research is None,"research_fail_soft")
state["research_fail"]=False
state["research"]={"btc_usd_daily":[1]}
w3=Worker(day,"/fake_reports","/fake_state")
partial=w3.tick(epoch(day,"08:59"))
ck(partial["signals"]["research_context"]=={} and w3.research is None,"partial_research_discard")
state["research"]={"btc_usd_daily":[1],"woori_daily":[2]}
state["candle_fail"]=True
try:w3.tick(epoch(day,"09:00"))
except OSError as exc:ck(str(exc)=="candle provider failed","candle_exception_propagates")
else:raise SystemExit("FAIL expected candle exception")
state["candle_fail"]=False
state["publish_fail"]=True
try:w3.tick(epoch(day,"09:00"))
except PermissionError:ck(True,"publish_exception_propagates")
else:raise SystemExit("FAIL expected publish exception")
ck(calls["publish"]>=3,"publish_called")
print(f"RF033_LEAD_WORKER_CONSUMER_OK cases={cases} source={expected[:8]} calls={calls} fetch=FAKE_ONLY thread=NOT_RUN")
