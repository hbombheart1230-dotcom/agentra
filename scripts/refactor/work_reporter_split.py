"""Reporter named decomposition helper: split a module into owners with VERBATIM definition bodies.

  python work_reporter_split.py <legacy_module_path> <out_pkg_dir> <doc> <owner=name1,name2,...> ...

Definitions are copied by exact line range; each owner receives only the module-level imports that its code references.
The legacy module is rewritten as an import-only facade that re-exports the same names (same function objects).
Definitions with a name that is not a top-level function / annotated or plain assignment abort the run.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def split(legacy: Path, out_dir: Path, doc: str, groups: dict[str, list[str]], pkg: str) -> None:
    text = legacy.read_text(encoding="utf-8-sig")
    lines = text.split("\n")
    tree = ast.parse(text)
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    defs: dict[str, ast.AST] = {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            defs[n.name] = n
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            defs[n.target.id] = n
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            defs[n.targets[0].id] = n
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        elif isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant):
            continue  # module docstring
        else:
            raise SystemExit(f"unsupported top-level statement: {type(n).__name__} at {n.lineno}")
    assigned = sorted(n for g in groups.values() for n in g)
    if assigned != sorted(defs):
        raise SystemExit(f"groups do not cover definitions exactly: missing={set(defs)-set(assigned)} extra={set(assigned)-set(defs)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    owner_of = {n: o for o, g in groups.items() for n in g}
    for owner, names in groups.items():
        used = {x.id for nm in names for x in ast.walk(defs[nm]) if isinstance(x, ast.Name)}
        used |= {x.value.id for nm in names for x in ast.walk(defs[nm]) if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name)}
        head = [f'"""{doc} ({owner}; definitions copied verbatim from {legacy.as_posix()})."""', "from __future__ import annotations", ""]
        std, local = [], []
        for imp in imports:
            if isinstance(imp, ast.ImportFrom) and imp.module == "__future__":
                continue
            keep = []
            for a in imp.names:
                bound = a.asname or a.name.split(".")[0]
                if bound in used:
                    keep.append(a)
            for nm in sorted(set(names)):
                pass
            if not keep:
                continue
            seg = ast.Import(names=keep) if isinstance(imp, ast.Import) else ast.ImportFrom(module=imp.module, names=keep, level=imp.level)
            (local if (isinstance(imp, ast.ImportFrom) and (imp.module or "").startswith("libs.")) else std).append(ast.unparse(seg))
        # intra-group dependencies on other owners (direct name use) become explicit imports from the sibling owner
        cross: dict[str, list[str]] = {}
        for nm in names:
            for x in ast.walk(defs[nm]):
                if isinstance(x, ast.Name) and x.id in owner_of and owner_of[x.id] != owner and isinstance(x.ctx, ast.Load):
                    cross.setdefault(owner_of[x.id], [])
                    if x.id not in cross[owner_of[x.id]]:
                        cross[owner_of[x.id]].append(x.id)
        body = ["\n".join(lines[defs[nm].lineno - 1 - len(getattr(defs[nm], "decorator_list", [])):defs[nm].end_lineno]) for nm in names]
        out = "\n".join(head) + "\n".join(std) + ("\n" if std else "")
        out += ("\n".join(local) + "\n" if local else "")
        for sibling, nms in sorted(cross.items()):
            out += f"from {pkg}.{sibling} import {', '.join(sorted(nms))}\n"
        out += "\n\n" + "\n\n\n".join(body) + "\n"
        (out_dir / f"{owner}.py").write_text(out, encoding="utf-8", newline="\n")
    fac = ['"""Compatibility facade: implementations live in ' + f"``{pkg}``" + '; names re-exported as the same objects (no code here)."""']
    for owner, names in groups.items():
        fac.append(f"from {pkg}.{owner} import (  # noqa: F401")
        fac.extend(f"    {n}," for n in names)
        fac.append(")")
    legacy.write_text("\n".join(fac) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    legacy_p, out_p, doc_ = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    g = {a.split("=")[0]: a.split("=")[1].split(",") for a in sys.argv[4:]}
    split(legacy_p, out_p, doc_, g, ".".join(out_p.parts[-4:]) if False else out_p.as_posix().replace("/", "."))
