# RF-033 baseline_btc_woori_tech/vnext/storage.py::publish atomic replace / immutable no-clobber / OSError cleanup (tmp-only, no network).
import os, sys, json, copy, importlib, tempfile, builtins
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
import importlib.util  # storage.py is stdlib-only: load by file so the heavy package __init__ (zoneinfo/tzdata) is not imported
_sp = importlib.util.spec_from_file_location("rf033_storage", os.path.join(repo, "libs", "reporting", "baseline_btc_woori_tech", "vnext", "storage.py"))
st = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(st)
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except BaseException as e: return type(e).__name__
tmp = Path(tempfile.mkdtemp(prefix="rf033_stor_")); tmpr = str(tmp.resolve())
def leftovers(d): return sorted(p.name for p in Path(d).iterdir() if p.name.startswith(".q12-"))
# ---- encoded / digest
check(st.encoded({"b": 1, "a": "한"}) == '{"a": "한", "b": 1}'.encode("utf-8"), "sorted keys, ensure_ascii False")
check(st.digest({"a": 1, "b": 2}) == st.digest({"b": 2, "a": 1}), "digest key-order independent")
check(st.encoded({"p": Path("x")}) == b'{"p": "x"}', "default=str")
enc = {"nan": exc_of(st.encoded, {"v": float("nan")}), "inf": exc_of(st.encoded, {"v": float("inf")})}
check(enc == {"nan": "ValueError", "inf": "ValueError"}, "allow_nan False")
# ---- mutable publish: creates parents, replaces atomically, returns value
p = tmp / "a" / "b" / "m.json"; v1 = {"k": 1}; v2 = {"k": 2}; orig = copy.deepcopy(v1)
check(st.publish(p, v1) is v1 and v1 == orig, "mutable returns same value, input unchanged")
check(st.read(p) == v1 and leftovers(p.parent) == [], "mutable first write, no tmp left")
check(st.publish(str(p), v2) == v2 and st.read(p) == v2 and leftovers(p.parent) == [], "mutable overwrite via str path")
# ---- immutable: first wins, second returns existing and does not clobber
q = tmp / "i" / "evidence.json"
check(st.publish(q, v1, immutable=True) == v1 and st.read(q) == v1, "immutable first publish")
ino = os.stat(q).st_ino
r = st.publish(q, v2, immutable=True)
check(r == v1 and st.read(q) == v1 and os.stat(q).st_ino == ino and leftovers(q.parent) == [], "immutable no-clobber returns existing, same inode, tmp removed")
raw = q.read_bytes()
check(st.publish(q, v1, immutable=True) == v1 and q.read_bytes() == raw, "immutable same value idempotent")
# existing broken immutable file -> read raises, file untouched
bq = tmp / "i" / "broken.json"; bq.write_bytes(b"{nope")
check(exc_of(st.publish, bq, v1, immutable=True) == "JSONDecodeError" and bq.read_bytes() == b"{nope" and leftovers(bq.parent) == [], "broken existing immutable: decode error, untouched")
# mutable publish onto a directory path -> OSError, tmp cleaned
dq = tmp / "d" / "dir.json"; dq.mkdir(parents=True)
dexc = exc_of(st.publish, dq, v1)
check(dexc in ("PermissionError", "IsADirectoryError", "OSError") and dq.is_dir() and leftovers(dq.parent) == [], "replace onto directory fails, tmp cleaned")
# ---- injected OSError cleanup (patch only tmp-dir ops)
real_fsync, real_replace, real_link = os.fsync, os.replace, os.link
def fails(name, target, mk):
    r = tmp / ("f_" + name); r.mkdir(); t = r / "x.json"
    setattr(os, target, mk)
    try: e = exc_of(st.publish, t, v1, immutable=(target == "link"))
    finally: setattr(os, target, {"fsync": real_fsync, "replace": real_replace, "link": real_link}[target])
    return e, t.exists(), leftovers(r)
def boom(*a, **k): raise OSError(28, "No space left on device")
def perm(*a, **k): raise PermissionError(13, "denied")
out = {n: fails(n, t, f) for n, t, f in [("fsync", "fsync", boom), ("replace", "replace", perm), ("link", "link", perm)]}
check(all(o == ("OSError" if n == "fsync" else "PermissionError", False, []) for n, o in out.items()), "OSError paths: raised, target absent, tmp cleaned: %r" % out)
# write failure inside stream (encode error before any write) leaves nothing
r = tmp / "enc"; r.mkdir()
check(exc_of(st.publish, r / "x.json", {"v": float("nan")}) == "ValueError" and not (r / "x.json").exists(), "encode ValueError: no target")
check(leftovers(r) == [], "encode ValueError: tmp cleaned")
# failed mutable replace keeps old content
k = tmp / "keep.json"; st.publish(k, v1)
os.replace = perm
try: e = exc_of(st.publish, k, v2)
finally: os.replace = real_replace
check(e == "PermissionError" and st.read(k) == v1 and leftovers(tmp) == [], "failed replace keeps previous content")
# nothing written outside tmp
check(str(k.resolve()).startswith(tmpr), "tmp-only")
print("RF033_STORAGE_PUBLISH_OK mutable=replace immutable=nofollow_link_noclobber same_inode=yes idempotent=yes broken_existing=JSONDecodeError dir_target=%s oserr={fsync,replace,link} cleanup=0_left keep_old_on_fail=yes nan=ValueError debug=%s outside_write=0" % (dexc, __debug__))
