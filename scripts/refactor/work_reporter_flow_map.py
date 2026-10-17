"""R8 C3: producer -> read model -> narrative/renderer -> consumer map (static import graph, read-only).

Producers: scripts/* report entry points (from report_inventory.json) and graphs reporter nodes. Consumers: apps/api modules
that read report artifacts. For each producer the transitive libs.reporting / libs.agents.reporter modules are listed with
their R8 inventory category, so duplicate pipelines (producers sharing renderers) are visible."""
import ast
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVD = ROOT / "docs/refactor/work_projects/evidence/reporter"


def imports_of(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
    except SyntaxError:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module)
            out |= {f"{n.module}.{a.name}" for a in n.names}
        elif isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
    return out


def mod_path(mod):
    p = ROOT / (mod.replace(".", "/") + ".py")
    if p.is_file():
        return p
    p = ROOT / mod.replace(".", "/") / "__init__.py"
    return p if p.is_file() else None


def closure(start, limit=400):
    seen, todo = set(), [start]
    while todo and len(seen) < limit:
        p = todo.pop()
        for m in imports_of(p):
            if not m.startswith(("libs.reporting", "libs.agents.reporter")):
                continue
            q = mod_path(m)
            if q and q not in seen:
                seen.add(q)
                todo.append(q)
    return seen


def main():
    inv = {r["path"]: r["category"] for r in json.loads((EVD / "r8_file_inventory.json").read_text(encoding="utf-8"))["rows"]}
    producers = [e["report_producer"] for e in json.loads((EVD / "report_inventory.json").read_text(encoding="utf-8"))["entries"]]
    producers += [p.relative_to(ROOT).as_posix() for p in (ROOT / "graphs/nodes").glob("reporter*.py")]
    consumers = [p.relative_to(ROOT).as_posix() for p in (ROOT / "apps/api").rglob("*.py")
                 if any(m.startswith("libs.reporting") for m in imports_of(p))]
    flows, used_by = {}, defaultdict(list)
    for prod in producers + consumers:
        mods = sorted(q.relative_to(ROOT).as_posix() for q in closure(ROOT / prod))
        flows[prod] = {"role": "consumer_api" if prod.startswith("apps/") else "producer",
                       "modules": len(mods), "by_category": {}, "renderers": [m for m in mods if "markdown" in m or "render" in m][:12]}
        for m in mods:
            c = inv.get(m, "AGENTS_OWNER" if m.startswith("libs/agents/reporter") else "OTHER")
            flows[prod]["by_category"][c] = flows[prod]["by_category"].get(c, 0) + 1
            used_by[m].append(prod)
    shared = {m: sorted(set(v)) for m, v in used_by.items() if len(set(v)) >= 4}
    doc = {"schema": "agentra.work.reporter.flow_map.v1", "flows": flows,
           "modules_shared_by_4plus_entrypoints": {m: len(v) for m, v in sorted(shared.items(), key=lambda kv: -len(kv[1]))[:40]}}
    (EVD / "r8_flow_map.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for k, v in flows.items():
        print(k, v["role"], v["modules"])


if __name__ == "__main__":
    main()
