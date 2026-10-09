"""Conservative static index of P1.5.2 Reporting façade consumers.

NEVER infer a symbol is dead from the absence of a statically recognizable call.
Runs on a clean checked-out tree; does not execute project source code.
"""
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"
TARGETS = {
    "libs.reporting.trade_report_ai": "libs/reporting/trade_report_ai.py",
    "libs.reporting.trade_report_markdown_clean": "libs/reporting/trade_report_markdown_clean.py",
    "libs.reporting.trade_story_pipeline": "libs/reporting/trade_story_pipeline.py",
}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


def expr_path(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = expr_path(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def literal_str(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def scan_source(path: str, source: str, names: dict[str, set[str]]) -> tuple[list[dict], list[dict]]:
    """Return direct references and unresolved dynamic/wildcard evidence."""
    refs: list[dict] = []
    hazards: list[dict] = []
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError) as exc:
        return [], [{"file": path, "kind": "PARSE_ERROR", "detail": str(exc)[:180]}]
    modules: dict[str, str] = {}
    direct: dict[str, tuple[str, str]] = {}

    def put(target: str, symbol: str, lineno: int, kind: str) -> None:
        if target in names and symbol in names[target]:
            refs.append({"file": path, "line": lineno, "module": target,
                         "symbol": symbol, "kind": kind})

    def hazard(target: str, lineno: int, kind: str, detail: str = "") -> None:
        hazards.append({"file": path, "line": lineno, "module": target,
                        "kind": kind, "detail": detail[:160]})

    def target_of(node: ast.AST) -> str | None:
        expr = expr_path(node)
        if not expr:
            return None
        for alias, target in sorted(modules.items(), key=lambda x: -len(x[0])):
            if expr == alias or expr.startswith(alias + "."):
                if expr == alias:
                    return target
                # The module itself, not an attribute of it, is required here.
                if expr.startswith(alias + ".") and alias != target.split(".")[-1]:
                    if expr == alias + "." + target.split(".")[-1]:
                        return target
        if expr in TARGETS:
            return expr
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in TARGETS:
                    modules[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module in TARGETS:
                for name in node.names:
                    if name.name == "*":
                        hazard(node.module, node.lineno, "WILDCARD_IMPORT")
                    else:
                        direct[name.asname or name.name] = (node.module, name.name)
                        put(node.module, name.name, node.lineno, "DIRECT_IMPORT")
            elif node.module == "libs.reporting":
                for name in node.names:
                    target = node.module + "." + name.name
                    if target in TARGETS:
                        modules[name.asname or name.name] = target

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in direct:
            target, symbol = direct[node.id]
            put(target, symbol, node.lineno, "IMPORTED_NAME_USAGE")
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            expression = expr_path(node)
            if not expression:
                continue
            for alias, target in modules.items():
                prefix = alias + "."
                if expression.startswith(prefix):
                    suffix = expression[len(prefix):]
                    put(target, suffix.split(".")[0], node.lineno, "MODULE_ATTRIBUTE")
        elif isinstance(node, ast.Call):
            called = expr_path(node.func) or ""
            if called in {"getattr", "setattr", "delattr", "hasattr"} and len(node.args) >= 2:
                module = target_of(node.args[0])
                if module:
                    symbol = literal_str(node.args[1])
                    if symbol is None:
                        hazard(module, node.lineno, "DYNAMIC_ATTR", called)
                    else:
                        put(module, symbol, node.lineno, "MONKEYPATCH_OR_DYNAMIC_ATTR" if called in {"setattr", "delattr"} else "LITERAL_ATTR")
            if called.endswith("patch.object") and len(node.args) >= 2:
                module = target_of(node.args[0])
                if module:
                    symbol = literal_str(node.args[1])
                    if symbol is None:
                        hazard(module, node.lineno, "DYNAMIC_PATCH_OBJECT")
                    else:
                        put(module, symbol, node.lineno, "PATCH_OBJECT")
            if called.endswith(".setattr") and len(node.args) >= 2:
                module = target_of(node.args[0])
                if module:
                    symbol = literal_str(node.args[1])
                    if symbol is None:
                        hazard(module, node.lineno, "DYNAMIC_MONKEYPATCH")
                    else:
                        put(module, symbol, node.lineno, "MONKEYPATCH")
            if called in {"patch", "mock.patch", "unittest.mock.patch"} or called.endswith(".patch"):
                if node.args:
                    dotted = literal_str(node.args[0])
                    if dotted:
                        for module in TARGETS:
                            if dotted.startswith(module + "."):
                                put(module, dotted[len(module) + 1:].split(".")[0],
                                    node.lineno, "STRING_PATCH")
                    elif any(module in source for module in TARGETS):
                        hazard("*", node.lineno, "DYNAMIC_PATCH_TARGET")
            if called in {"importlib.import_module", "import_module"} and node.args:
                dotted = literal_str(node.args[0])
                if dotted in TARGETS:
                    hazard(dotted, node.lineno, "DYNAMIC_MODULE_IMPORT")
                elif dotted is None and any(module in source for module in TARGETS):
                    hazard("*", node.lineno, "COMPUTED_MODULE_IMPORT")
    # A source file can hold repeated references to the same symbol at a single line.
    refs = list({(r["file"], r["line"], r["module"], r["symbol"], r["kind"]):
                 r for r in refs}.values())
    return sorted(refs, key=lambda r: (r["line"], r["symbol"], r["kind"])), hazards


def collect(root: Path = ROOT) -> dict[str, Any]:
    ledger = json.loads((root / LEDGER.relative_to(ROOT)).read_text(encoding="utf-8"))
    names = {row["path"][:-3].replace("/", "."): {x["name"] for x in row["symbols"]}
             for row in ledger["files"]}
    assert names.keys() == TARGETS.keys()
    references: list[dict] = []
    hazards: list[dict] = []
    parsed = 0
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.as_posix() in TARGETS.values():
            continue  # Self-references are not external consumer evidence.
        code = path.read_text(encoding="utf-8-sig", errors="replace")
        a, b = scan_source(rel.as_posix(), code, names)
        references.extend(a)
        hazards.extend(b)
        parsed += 1
    kinds = Counter(r["kind"] for r in references)
    referenced = {(x["module"], x["symbol"]) for x in references}
    return {
        "schema_version": "p152-static-consumer-evidence-v1",
        "evidence_scope": "STATIC_ONLY_NOT_LOCAL_RUNTIME_PROOF",
        "source_ledger": str(LEDGER.relative_to(ROOT)),
        "files_scanned": parsed,
        "symbols_in_ledger": sum(map(len, names.values())),
        "symbols_with_static_refs": len(referenced),
        "symbols_without_static_refs_NOT_DEAD": sum(map(len, names.values())) - len(referenced),
        "reference_kinds": dict(sorted(kinds.items())),
        "references": sorted(references, key=lambda r: (r["module"], r["symbol"], r["file"], r["line"])),
        "hazards": sorted(hazards, key=lambda r: (r["file"], r.get("line", 0), r["kind"])),
        "acceptance": "P1.5.2 OPEN: no static finding authorizes deleting or renaming a façade symbol.",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="branch_output/p152_facade_consumer_static_coverage.json")
    args = ap.parse_args()
    payload = collect()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("P1.5.2 STATIC FACADE CONSUMER INDEX:", payload["symbols_in_ledger"],
          "symbols;", payload["symbols_with_static_refs"], "statically referenced;",
          len(payload["hazards"]), "dynamic/wildcard/parse hazards; scanned",
          payload["files_scanned"], "Python files; all unreferenced symbols UNKNOWN NOT DEAD")


if __name__ == "__main__":
    main()
