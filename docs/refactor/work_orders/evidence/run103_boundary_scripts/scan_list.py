import ast, pathlib, re, sys

files = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
RISK = {"urlopen", "write_text", "write_bytes", "open", "connect", "Popen", "run", "system", "mkdir", "unlink", "rename", "getenv", "sleep", "rmtree", "makedirs", "environ"}
allsrc = {}
for p in pathlib.Path(".").rglob("*.py"):
    s = str(p).replace("\\", "/")
    if s.startswith((".git", "node_modules", ".venv")):
        continue
    try:
        allsrc[s] = p.read_text(encoding="utf-8")
    except Exception:
        pass
dirs = sorted({str(pathlib.Path(f).parent).replace("\\", "/") for f in files})
print(len(files), "files")
for f in files:
    t = ast.parse(allsrc[f])
    risk = set()
    for n in ast.walk(t):
        if isinstance(n, ast.Call):
            nm = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
            if nm in RISK:
                risk.add(nm)
        if isinstance(n, ast.Attribute) and n.attr == "environ":
            risk.add("environ")
    mod = f[:-3].replace("/", ".")
    if mod.endswith(".__init__"):
        mod = mod[:-9]
    short = mod.split(".")[-1]
    ext = [s for s, src in allsrc.items() if s not in files and re.search(r"\b" + re.escape(mod) + r"\b", src)]
    pkg = str(pathlib.Path(f).parent).replace("\\", "/")
    intra = [s for s in files if s != f and str(pathlib.Path(s).parent).replace("\\", "/") == pkg
             and re.search(r"from \.+" + re.escape(short) + r" import|from \. import[^\n]*\b" + re.escape(short) + r"\b|\b" + re.escape(mod) + r"\b", allsrc[s])]
    kinds = sorted({c.split("/")[0] for c in ext})
    print(f"{f.replace('libs/reporting/','')} | risk={','.join(sorted(risk)) or '-'} | ext={len(ext)}({','.join(kinds)}) | intra={len(intra)}")
