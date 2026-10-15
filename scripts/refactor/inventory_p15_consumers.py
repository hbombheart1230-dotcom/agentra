"""Read-only AST consumer inventory. No imported project module is executed.

A path without observed static consumers is UNKNOWN, never proven unused.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


def module(path: str) -> str:
    name = path[:-3].replace("/", ".")
    return name[:-9] if name.endswith(".__init__") else name


def inspect(root: Path, paths: list[str] | None = None) -> dict:
    if paths is None:
        data = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True).stdout
        paths = sorted(x.decode("utf-8", "surrogateescape") for x in data.split(b"\0") if x)
    py = sorted(x for x in paths if x.endswith(".py"))
    mods = {module(x): x for x in py}
    direct, dynamic, unknown, digests = defaultdict(set), defaultdict(set), defaultdict(list), defaultdict(list)
    errors = {}
    for p in py:
        content = (root / p).read_bytes()
        digests[hashlib.sha256(content).hexdigest()].append(p)
        try:
            tree = ast.parse(content, filename=p)
        except (SyntaxError, ValueError) as exc:
            errors[p] = str(exc)[:160]
            continue
        bits = module(p).split(".")
        pkg = bits if p.endswith("__init__.py") else bits[:-1]
        for node in ast.walk(tree):
            imports = []
            if isinstance(node, ast.Import):
                imports = [x.name for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    prefix = pkg[:len(pkg) - node.level + 1]
                    base = ".".join([*prefix, base] if base else prefix)
                imports = [base] + [base + "." + x.name for x in node.names if x.name != "*"]
            for candidate in imports:
                while candidate not in mods and "." in candidate:
                    candidate = candidate.rsplit(".", 1)[0]
                if candidate in mods and mods[candidate] != p:
                    direct[p].add(mods[candidate])
            if isinstance(node, ast.Call):
                f = node.func
                is_dynamic = (isinstance(f, ast.Name) and f.id == "__import__") or (
                    isinstance(f, ast.Attribute) and f.attr == "import_module")
                if is_dynamic:
                    arg = node.args[0] if node.args else None
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if arg.value in mods:
                            dynamic[p].add(mods[arg.value])
                    else:
                        unknown[p].append(getattr(node, "lineno", 0))
    rev = defaultdict(set)
    for src, deps in direct.items():
        for target in deps:
            rev[target].add(src)
    rev_dyn = defaultdict(set)
    for src, deps in dynamic.items():
        for target in deps:
            rev_dyn[target].add(src)
    scripts = sorted(p for p in py if re.fullmatch(r"scripts/[^/]+\.py", p))
    configs = sorted(p for p in paths if p.startswith(("config/", "deploy/", ".github/", "apps/"))
                     and p.endswith((".py", ".sh", ".ps1", ".bat", ".cmd", ".yml", ".yaml", ".json", ".toml", ".ts", ".tsx")))
    refs = defaultdict(set)
    for p in configs:
        content = (root / p).read_text(encoding="utf-8", errors="replace")
        for target in scripts:
            if target in content or re.search(r"(?<![\w.])" + re.escape(Path(target).name) + r"(?![\w.])", content):
                refs[target].add(p)
    keys = sorted(p for p in py if p.startswith("libs/agent/") and p.count("/") == 2)
    keys += [p for p in (
        "graphs/trading_graph.py", "graphs/nodes/execute_from_packet.py",
        "graphs/nodes/executor_node.py", "graphs/nodes/scanner_node.py",
        "graphs/nodes/monitor_node.py", "graphs/nodes/strategist_node.py",
        "libs/reporting/live_execution_bundle_runner.py") if p in py]
    return {
        "tracked": len(paths), "python": len(py), "parse_errors": errors,
        "static_edges": sum(map(len, direct.values())),
        "dynamic_literal_edges": sum(map(len, dynamic.values())),
        "dynamic_nonliteral_calls": sum(map(len, unknown.values())),
        "unresolved_sites": dict(sorted(unknown.items())),
        "edges": {k: sorted(v) for k, v in sorted(direct.items())},
        "dynamic_edges": {k: sorted(v) for k, v in sorted(dynamic.items())},
        "key_consumers": {p: {"static": sorted(rev[p]), "dynamic": sorted(rev_dyn[p])} for p in sorted(set(keys))},
        "root_script_count": len(scripts),
        "root_script_refs": {p: sorted(refs[p]) for p in scripts if refs[p]},
        "exact_duplicate_groups": [sorted(v) for v in digests.values()
                                   if len(v) > 1 and any(x.startswith(("libs/", "graphs/")) for x in v)],
        "warning": "No observed reference does not prove unused; injected consumers, dynamic calls and external scheduler may be absent.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = inspect(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {k: result[k] for k in ("tracked", "python", "static_edges",
               "dynamic_literal_edges", "dynamic_nonliteral_calls", "root_script_count")}
    summary["parse_errors"] = len(result["parse_errors"])
    summary["key_consumer_counts"] = {k: len(v["static"]) for k, v in result["key_consumers"].items()}
    summary["config_referenced_scripts"] = result["root_script_refs"]
    summary["duplicate_groups_preview"] = result["exact_duplicate_groups"][:12]
    summary["warning"] = result["warning"]
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if result["parse_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
