"""Read-only, bounded retained-symbol exclusions; no runtime imports or moves."""
import ast
import hashlib
import json
from pathlib import Path
from scripts.refactor.monitor_evidence_ast import evidence_dump

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = "docs/refactor/work_projects/evidence/monitor/continuous/current_scope.json"


def produce():
    inventory = json.loads((ROOT / INVENTORY).read_text(encoding="utf-8"))
    trees = {r["path"]: ast.parse((ROOT / r["path"]).read_text(encoding="utf-8-sig"))
             for r in inventory["modules"]}
    references = {}
    for path, tree in trees.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                name = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else None
                if name:
                    references.setdefault(name, set()).add(path + ":" + str(n.lineno))
    rows = []
    for module in inventory["modules"]:
        definitions = {}
        for node in trees[module["path"]].body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions[node.name] = node
                if isinstance(node, ast.ClassDef):
                    definitions.update({node.name + "." + n.name: n for n in node.body
                                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))})
        for symbol in module["symbols"]:
            if symbol["disposition"] in {"IMPLEMENTATION_MOVED_VERIFIED", "KEEP_PUBLIC_COMPAT_WRAPPER"}:
                continue
            node = definitions[symbol["symbol"]]
            calls = sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)})
            stores = sorted({ast.unparse(n) for n in ast.walk(node)
                             if isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, (ast.Store, ast.Del))})
            controls = sorted({type(n).__name__ for n in ast.walk(node)
                               if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.Raise, ast.With, ast.Await))})
            name = symbol["symbol"].split(".")[-1]
            callers = sorted(references.get(name, set()))
            rows.append({"path": module["path"], "symbol": symbol["symbol"],
                         "ast_sha256": hashlib.sha256(evidence_dump(node).encode()).hexdigest(),
                         "LOC": symbol["LOC"], "disposition": symbol["disposition"],
                         "decision": "EXCLUDE_FROM_FURTHER_MOVES", "reason": symbol["reason"],
                         "calls": calls, "attribute_or_subscript_writes": stores,
                         "control_flow": controls, "bounded_syntactic_callers": callers,
                         "limit": "Syntactic references only; dynamic consumers and callback effects remain protected. No purity claim."})
    return {"schema": "monitor.retained_boundary.v1", "code_sha": inventory["code_sha"],
            "state": "LOCAL_SAFE_SCOPE_FROZEN_PENDING_INDEPENDENT_REVIEW",
            "decision": "Retain every remaining definition at its existing compatibility/authority boundary; no additional move is justified by this static evidence.",
            "symbols": rows, "symbol_count": len(rows)}


if __name__ == "__main__":
    print(json.dumps(produce(), ensure_ascii=True, indent=2))
