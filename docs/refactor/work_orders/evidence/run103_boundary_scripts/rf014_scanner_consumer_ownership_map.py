# RF-014 read-only file::symbol ownership map: 20 libs/agents/scanner owners -> importing consumers (AST, whole repo), each
# consumer path mapped to its RF owner via FILE_COVERAGE_63182ab2.csv. Flags owners whose consumers belong to other RFs
# (RF-009/019/030/035/074 conflicts). No import of repo code, no execution, no writes. Usage: python script FILE_COVERAGE.csv
import ast, csv, os, sys
from pathlib import Path
root = Path(os.getcwd()).resolve()
cov = {r["path"]: r["rf_id"] for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
owners = sorted(p for p, rf in cov.items() if rf == "RF-014")
check = lambda c, m: None if c else sys.exit("CHECK_FAILED: " + m)
check(len(owners) == 20 and all((root / p).is_file() for p in owners), "20 RF-014 owners present")
def modname(p): return p[:-3].replace("/", ".").removesuffix(".__init__")
mod2path = {modname(p): p for p in owners}
# compatibility shims (libs/runtime/scanner/<name>.py replaces itself in sys.modules by the canonical owner): second-hop alias
for p in owners:
    shim = "libs/runtime/scanner/" + Path(p).name
    if Path(p).name != "__init__.py" and (root / shim).is_file() and "_sys.modules[__name__]" in (root / shim).read_text(encoding="utf-8"):
        mod2path[modname(shim)] = p
syms = {}
for p in owners:
    t = ast.parse((root / p).read_text(encoding="utf-8"))
    syms[p] = [n.name for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
SKIP = {".git", "__pycache__", "node_modules", ".venv", "venv", "reports", "data"}
files = []
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in SKIP]
    files += [Path(dp) / f for f in fn if f.endswith(".py")]
edges = {p: {} for p in owners}   # owner -> consumer path -> set(names)
dyn = {p: [] for p in owners}     # string/importlib references
for f in files:
    rel = f.relative_to(root).as_posix()
    if rel.startswith("docs/refactor/work_orders/evidence/"): continue   # harnesses themselves are not consumers
    try: src = f.read_text(encoding="utf-8"); tree = ast.parse(src)
    except Exception: continue
    pkg = modname(rel).rsplit(".", 1)[0] if "." in modname(rel) else ""
    is_pkg = rel.endswith("__init__.py")
    base_pkg = modname(rel) if is_pkg else pkg
    for n in ast.walk(tree):
        targets = []
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name in mod2path: targets.append((a.name, {"*module*"}))
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            if n.level:
                parts = base_pkg.split(".") if base_pkg else []
                parts = parts[: len(parts) - (n.level - 1)] if n.level > 1 else parts
                mod = ".".join(parts + ([n.module] if n.module else []))
            if mod in mod2path: targets.append((mod, {a.name for a in n.names}))
            for a in n.names:   # from pkg import submodule
                full = mod + "." + a.name
                if full in mod2path: targets.append((full, {"*module*"}))
        for m, names in targets:
            if rel != mod2path[m] and not rel.startswith("libs/runtime/scanner/"): edges[mod2path[m]].setdefault(rel, set()).update(names)
    for m, p in mod2path.items():
        if m in src and rel != p and rel not in edges[p] and ("importlib" in src or "import_module" in src or '"' + m + '"' in src or "'" + m + "'" in src):
            dyn[p].append(rel)
rows = []; conflicts = {}
for p in owners:
    rfs = {}
    for c, names in edges[p].items():
        rf = cov.get(c, "UNMAPPED_TEST" if c.startswith("tests/") else "UNMAPPED")
        rfs.setdefault(rf, []).append(c)
    foreign = {rf: v for rf, v in rfs.items() if rf not in ("RF-014",)}
    rows.append((p, len(edges[p]), sorted(rfs), len(dyn[p])))
    if foreign: conflicts[p] = foreign
other_rf = {}
for p, f in conflicts.items():
    for rf, v in f.items(): other_rf.setdefault(rf, set()).update(v)
for p, n, rfs, d in rows:
    print("%-70s consumers=%-3d rfs=%s dynamic_refs=%d symbols=%d" % (p, n, ",".join(rfs) or "-", d, len(syms[p])))
print("--- foreign consumer RFs (file::symbol counts) ---")
for rf in sorted(other_rf): print(rf, len(other_rf[rf]), sorted(other_rf[rf])[:6])
no_cons = [p for p, n, _, d in rows if n == 0 and d == 0]
print("RF014_OWNERSHIP_MAP_OK owners=20 with_consumers=%d zero_consumers=%s foreign_rfs=%s writes=0 exec=0" % (sum(1 for r in rows if r[1]), [Path(p).name for p in no_cons], sorted(other_rf)))
