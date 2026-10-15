"""Read-only static contract audit for Agentra's Scripts target-tree wrappers.

This tool deliberately parses source instead of importing or invoking any trading,
research, maintenance, or diagnostic entrypoint.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

_DEFAULT_MANIFEST = "docs/refactor/2026-10-15_scripts_bulk_manifest.json"


def _call_targets(tree: ast.AST, owner: str, method: str) -> list[str]:
    """Return literal module names passed to one documented wrapper API."""
    out: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name):
            continue
        if node.func.value.id != owner or node.func.attr != method or not node.args:
            continue
        if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            out.append(node.args[0].value)
    return out


def _module_path(path: str) -> str:
    if not path.startswith("scripts/") or not path.endswith(".py"):
        raise ValueError(f"not a Python script path: {path}")
    return path[:-3].replace("/", ".")


def _has_statement(statements: list[ast.stmt], source: str) -> bool:
    expected = ast.dump(ast.parse(source).body[0])
    return any(ast.dump(statement) == expected for statement in statements)


def _dispatch_issues(tree: ast.Module, module: str, *, bulk: bool) -> list[str]:
    """Check executable dispatch and ABI aliasing, not merely literal targets."""
    condition = ast.dump(ast.parse("__name__ == '__main__'", mode="eval").body)
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.dump(node.test) == condition]
    if len(guards) != 1:
        return ["exactly one top-level __main__ guard required"]
    guard = guards[0]
    if bulk:
        main = f"_runpy.run_module({module!r}, run_name='__main__')"
        alias = f"_sys.modules[__name__] = _importlib.import_module({module!r})"
    else:
        main = "raise SystemExit(_impl.main())"
        alias = "_sys.modules[__name__] = _impl"
    issues = []
    if not _has_statement(guard.body, main):
        issues.append("executable __main__ dispatch missing or invalid")
    if not _has_statement(guard.orelse, alias):
        issues.append("module-object ABI alias missing or invalid")
    if not bulk and not _has_statement(
        tree.body, f"_impl = _importlib.import_module({module!r})"
    ):
        issues.append("example implementation binding missing or invalid")
    return issues


def audit(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    """Validate that all declared moved implementations retain their public paths.

    No Python module is imported, CLI executed, subprocess spawned, or file written.
    """
    root = root.resolve()
    manifest_path = manifest_path or (root / _DEFAULT_MANIFEST)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = manifest["candidates"]
    moved = [item for item in candidates if item["status"] == "moved"]
    held = [item for item in candidates if item["status"] == "held"]
    wrappers = [item["path"] for item in manifest["root_layout"] if item["kind"] == "compatibility_wrapper"]
    issues: list[str] = []
    checked = 0

    def check_pair(old_path: str, new_path: str, *, bulk: bool) -> None:
        nonlocal checked
        old = root / old_path
        new = root / new_path
        expected_module = _module_path(new_path)
        if not old.is_file():
            issues.append(f"missing legacy entrypoint: {old_path}")
            return
        if not new.is_file():
            issues.append(f"missing canonical implementation: {new_path}")
            return
        try:
            legacy_source = old.read_text(encoding="utf-8-sig")
            legacy_ast = ast.parse(legacy_source, filename=old_path)
            ast.parse(new.read_text(encoding="utf-8-sig"), filename=new_path)
        except (OSError, UnicodeError, SyntaxError) as exc:
            issues.append(f"invalid script: {old_path} or {new_path}: {type(exc).__name__}")
            return
        imported = _call_targets(legacy_ast, "_importlib", "import_module")
        if imported != [expected_module]:
            issues.append(f"legacy import target mismatch: {old_path}: {imported!r} != {expected_module!r}")
        if bulk:
            invoked = _call_targets(legacy_ast, "_runpy", "run_module")
            if invoked != [expected_module]:
                issues.append(f"legacy main target mismatch: {old_path}: {invoked!r} != {expected_module!r}")
        issues.extend(f"{old_path}: {issue}" for issue in
                      _dispatch_issues(legacy_ast, expected_module, bulk=bulk))
        checked += 1

    declared_old = set()
    for entry in moved:
        old_path, new_path = entry["old"], entry["new"]
        declared_old.add(old_path)
        check_pair(old_path, new_path, bulk=True)

    wrapper_set = set(wrappers)
    if len(wrapper_set) != len(wrappers):
        issues.append("duplicate root compatibility wrappers in manifest")
    if not declared_old.issubset(wrapper_set):
        issues.append(f"moved wrappers missing in root layout: {sorted(declared_old - wrapper_set)!r}")
    example_wrappers = sorted(wrapper_set - declared_old)
    for old_path in example_wrappers:
        if not old_path.startswith("scripts/demo_"):
            issues.append(f"unclassified compatibility wrapper: {old_path}")
            continue
        check_pair(old_path, "scripts/examples/" + Path(old_path).name, bulk=False)

    if len(moved) + len(held) != len(candidates):
        issues.append("candidate count does not conserve moved + held")
    if len(wrappers) != len(moved) + len(example_wrappers):
        issues.append("wrapper count mismatch")

    return {
        "candidates": len(candidates),
        "moved": len(moved),
        "held": len(held),
        "root_wrappers": len(wrappers),
        "checked": checked,
        "issues": issues,
        "ok": not issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = audit(args.root, args.manifest)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Scripts wrappers: {result['checked']}/{result['root_wrappers']} checked; "
              f"{len(result['issues'])} issue(s)")
        for issue in result["issues"]:
            print(f"- {issue}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
