import os,sys,socket,subprocess,sqlite3,tempfile,runpy,io,contextlib,json,pathlib
wt=sys.argv[1]; fmt=sys.argv[2]
def blk(*a,**k): raise RuntimeError("blocked")
socket.socket.connect=blk; subprocess.Popen=blk; sqlite3.connect=blk
tmp=pathlib.Path(tempfile.mkdtemp(prefix="rf063_"))
os.chdir(tmp); sys.path.insert(0,wt)
import importlib.util
sp=importlib.util.spec_from_file_location("m23",wt+"/scripts/diagnostics/run_m23_closeout_check.py")
m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
argv=["--event-log-path",str(tmp/"ev.jsonl"),"--report-dir",str(tmp/"rep"),"--day","2026-10-27"]
if fmt=="json": argv.append("--json")
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    rc=m.main(argv)
out=buf.getvalue()
files=sorted(str(p.relative_to(tmp)) for p in tmp.rglob("*") if p.is_file())
print("rc",rc,"__debug__",__debug__,"fmt",fmt); print(out[:400]); print("files",len(files),"wt_dirty_check_below")
