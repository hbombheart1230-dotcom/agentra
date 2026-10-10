"""Conservative remote P1.5.2 compatibility debt ledger; never infer DEAD.

Scans static Python users, NOT C:\\Agentra dynamic/runtime consumers.
Creates evidence JSON only; leaves public facade implementations and symbol ledger unchanged.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts.refactor.p152_facade_consumer_scan import collect, LEDGER, ROOT, TARGETS

SEMANTICALLY_UNPROVEN = "UNRESOLVED_NO_LOCAL_CONSUMER_PROOF"


def build_debt_inventory(root: Path = ROOT) -> dict[str, Any]:
    ledger = json.loads((root / LEDGER.relative_to(ROOT)).read_text(encoding="utf-8"))
    coverage = collect(root)
    references = defaultdict(list)
    for row in coverage["references"]:
        references[(row["module"], row["symbol"])].append(row)
    facade_summaries = []
    all_symbols = []
    for group in ledger["files"]:
        module = group["path"][:-3].replace("/", ".")
        assert module in TARGETS, module
        counts = Counter()
        static_referenced = 0
        for symbol in group["symbols"]:
            name = symbol["name"]
            found = references[(module, name)]
            counts[symbol["disposition"]] += 1
            if found:
                static_referenced += 1
            # Always retain, even when the static scan finds no reference.
            decision = "KEEP_PUBLIC_API_PENDING_LOCAL_PROOF"
            if symbol["disposition"] == "WRAPPER":
                decision = "KEEP_WRAPPER_PENDING_LOCAL_PROOF"
            if symbol["disposition"] == "SAFETY_LOCK":
                decision = "KEEP_SAFETY_LOCK"
            all_symbols.append({
                "module": module,
                "symbol": name,
                "physical_loc": symbol["physical_loc"],
                "declared_disposition": symbol["disposition"],
                "remote_recommendation": decision,
                "external_static_references": len(found),
                "static_reference_kinds": dict(sorted(Counter(x["kind"] for x in found).items())),
                "static_consumer_files": sorted({x["file"] for x in found}),
                "dynamic_consumer_status": SEMANTICALLY_UNPROVEN,
                "authority_to_delete_or_rename": False,
            })
        facade_summaries.append({
            "path": group["path"],
            "module": module,
            "physical_loc": group["physical_loc"],
            "public_symbols": len(group["symbols"]),
            "statically_referenced_symbols": static_referenced,
            "not_statically_found_but_not_dead": len(group["symbols"]) - static_referenced,
            "existing_dispositions": dict(sorted(counts.items())),
            "size_target_met": False,
        })
    verified = sum(q["statically_referenced_symbols"] for q in facade_summaries)
    assert len(all_symbols) == coverage["symbols_in_ledger"] == 436
    assert verified == coverage["symbols_with_static_refs"]
    assert all(not s["authority_to_delete_or_rename"] for s in all_symbols)
    return {
        "schema": "p152_prelocal_consumer_debt.v1",
        "evidence_scope": "STATIC_OFFLINE_ONLY_NO_LOCAL_RUNTIME_OR_DYNAMIC_PROOF",
        "source_ledger": str(LEDGER.relative_to(ROOT)),
        "files_scanned": coverage["files_scanned"],
        "public_symbol_total": len(all_symbols),
        "statically_referenced_symbols": verified,
        "not_statically_found_not_dead": len(all_symbols) - verified,
        "static_reference_total": len(coverage["references"]),
        "hazards": coverage["hazards"],
        "facades": facade_summaries,
        "symbol_cases": all_symbols,
        "size_debt_requires_operator_decision": True,
        "local_abi_and_runtime_consumer_gates": "NOT_RUN",
        "deletion_authorized": False,
        "p152": "OPEN",
        "p153": "NOT_AUTHORIZED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="branch_output/p152_prelocal_consumer_debt.json")
    args = parser.parse_args()
    data = build_debt_inventory()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "P1.5.2 CONSERVATIVE CONSUMER DEBT:",
        data["statically_referenced_symbols"], "static-ref /",
        data["public_symbol_total"], "total;",
        data["not_statically_found_not_dead"], "unproven not dead;",
        len(data["hazards"]), "dynamic hazards;"
    )
    print("NOT AUTHORIZED: facade deletion, size goal waiver, P1.5.3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
