# RF-052 (A, claimed from UNASSIGNED): portable archive-ref confinement for libs/market_data/receipts.resolve_archive_path. Usage: (cd <repo>; python [-O] rf052_receipts_path_check.py)
import os, sys, tempfile, json, shutil
from pathlib import Path
sys.path.insert(0, os.getcwd())
from libs.market_data import receipts as r
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
root = Path(tempfile.mkdtemp(prefix="rf052_")).resolve(); out = {}
reject = ["", "/etc/passwd", "C:\\evil.raw", "C:evil.raw", "c:/x.raw", "\\\\server\\share\\x", "\\x", "../e.raw", "a/../../e.raw", "a\\..\\..\\e.raw", "a\\..\\b.raw"]
accept = ["kiwoom/p1/005930/" + "a" * 64 + ".raw", "a/b.raw", "a.b/c..d.raw"]
for ref in reject:
    try: r.resolve_archive_path(root, ref); out[ref] = "ACCEPTED"
    except r.ArchivePathError: out[ref] = "rejected"
for ref in accept:
    p = r.resolve_archive_path(root, ref); out[ref] = "ok" if str(p).startswith(str(root)) else "ESCAPE"
check(all(out[x] == "rejected" for x in reject) and all(out[x] == "ok" for x in accept), out)
check(r.content_addressed_ref(provider="kiwoom", producer_id="p1", symbol="005930", raw_sha256="a" * 64) == accept[0], "content-addressed ref still valid")
shutil.rmtree(root, ignore_errors=True)
print(json.dumps(out, sort_keys=True)); print("RF052_RECEIPTS_PATH_OK rejected=%d accepted=%d debug=%s" % (len(reject), len(accept), __debug__))
