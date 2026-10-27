import os, sys, subprocess, tempfile, json, pathlib, shutil
TREE = pathlib.Path(sys.argv[1]).resolve()
CLI = TREE / "scripts/diagnostics/run_m29_disaster_recovery_drill.py"
def snap(p):
    return sorted(str(x.relative_to(p)) for x in p.rglob("*") if "__pycache__" not in x.parts)
before = snap(TREE)
res = {}
for opt in ([], ["-O"]):
  for mode in ("ok", "inject", "noclear"):
    base = pathlib.Path(tempfile.mkdtemp(prefix="rf063_"))
    sentinel = base / "sentinel.txt"; sentinel.write_text("keep")
    d = dict(work=base/"work", arch=base/"arch", rest=base/"rest", rep=base/"rep")
    stale = d["rest"]/"stale.txt"; d["rest"].mkdir(); stale.write_text("old")
    args = ["--working-dataset-root",str(d["work"]),"--archive-dir",str(d["arch"]),"--restored-dataset-root",str(d["rest"]),"--report-dir",str(d["rep"]),"--day","2026-02-21","--json"]
    if mode=="inject": args.append("--inject-fail")
    if mode=="noclear": args.append("--no-clear")
    env = dict(os.environ, PYTHONUTF8="0", PYTHONIOENCODING="cp949", PYTHONDONTWRITEBYTECODE="1")
    cwd = base/"cwd"; cwd.mkdir()
    p = subprocess.run([sys.executable,*opt,str(CLI),*args],cwd=cwd,env=env,capture_output=True)
    out = p.stdout.decode("cp949"); err = p.stderr.decode("cp949","replace")
    o = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
    key = f"{'O' if opt else 'N'}:{mode}"
    res[key] = dict(rc=p.returncode, ok=o.get("ok"), parity=o.get("parity",{}).get("ok"), mism=o.get("archive_integrity",{}).get("hash_mismatch_total"),
        nf=len(o.get("failures",[])), stale_removed=not stale.exists(), sentinel=sentinel.exists(), stderr=len(err),
        cwd_files=len(list(cwd.rglob("*"))), rest_exists=d["rest"].exists(), rep_files=len(list(d["rep"].rglob("*"))) if d["rep"].exists() else 0)
    shutil.rmtree(base, ignore_errors=True)
after = snap(TREE)
print(json.dumps(res, indent=0))
print("tree_unchanged", before==after, set(after)-set(before))
