"""Offline, read-only P1.5.2 integration closeout inventory.

The remote build is NOT a certification of local C:\\Agentra real output,
all-repo pytest, live LLM semantics or an independent local audit.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PINNED_BEFORE = "2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c"
SOURCE_SCOPE = ("libs/reporting/", "tests/", "docs/", "scripts/refactor/")
WORKFLOW = ".github/workflows/p152-r2c-residual-regression.yml"
FACADES = {
    "libs/reporting/trade_report_ai.py": 182,
    "libs/reporting/trade_report_markdown_clean.py": 209,
    "libs/reporting/trade_story_pipeline.py": 45,
}
SMALL_OWNER_LEDGER = "tests/test_p152_new_owner_dependency_gate.py"
EXPECTED_SMALL_OWNERS = 37
REQUIRED_REMOTE_GATES = (
    "owner_ast_and_import_dag",
    "public_abi_scope",
    "reporting_337_reference_suite",
    "helper_ui_owner_suite",
    "additional_offline_reporting_integration",
    "consumer_static_index",
    "ui_patch_note_sync",
)
LOCAL_GATES = (
    "local_worktree_and_dirty_q12_reconciliation",
    "actual_immutable_json_markdown_byte_parity",
    "actual_source_precedence_and_symbol_rank",
    "captured_llm_prompts_calls_retries_timeouts",
    "complete_repository_pytest_baseline",
    "claude_independent_read_only_review",
    "codex_independent_read_only_review",
    "operator_final_acceptance",
)


def _git(*args: str, root: Path) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=root, encoding="utf-8"
    ).strip()


def owner_files(root: Path) -> tuple[str, ...]:
    source = (root / SMALL_OWNER_LEDGER).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "OWNER_FILES" for target in node.targets):
                result = ast.literal_eval(node.value)
                if not isinstance(result, tuple) or not all(isinstance(x, str) for x in result):
                    raise ValueError("Owner ledger is not a literal tuple of file paths")
                return result
    raise ValueError("Owner ledger missing")


def build_inventory(root: Path = ROOT, *, ref: str = "HEAD") -> dict[str, Any]:
    head = _git("rev-parse", ref, root=root)
    changed = [
        p for p in _git("diff", "--name-only", PINNED_BEFORE, ref, root=root).splitlines()
        if p
    ]
    out_of_scope = [
        p for p in changed
        if not (p.startswith(SOURCE_SCOPE) or p == WORKFLOW)
    ]
    facade = {}
    for path, expected in FACADES.items():
        contents = (root / path).read_text(encoding="utf-8-sig")
        tree = ast.parse(contents)
        count = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    for n in tree.body)
        facade[path] = {
            "physical_loc": len(contents.splitlines()),
            "public_top_level_callable_count": count,
            "expected_callable_count": expected,
            "count_matches": count == expected,
        }
    owners = owner_files(root)
    sizes = {p: len((root / p).read_text(encoding="utf-8").splitlines()) for p in owners}
    over_limit = {p: n for p, n in sizes.items() if n > 350}
    current = (root / "docs/refactor/work_orders/CURRENT.md").read_text(encoding="utf-8")
    code_scope_ok = not out_of_scope
    facade_ok = all(row["count_matches"] for row in facade.values())
    owner_ok = len(owners) == EXPECTED_SMALL_OWNERS and not over_limit and len(owners) == len(set(owners))
    stage_frozen = "P1.5.2 OPEN" in current and "P1.5.3" in current
    return {
        "schema": "p152_integration_acceptance.remote_inventory.v1",
        "git_sha": head,
        "pinned_before_code_sha": PINNED_BEFORE,
        "execution_context": "github_actions_offline_source_only",
        "no_real_broker_or_llm_invocation": True,
        "source_inventory": {
            "modified_paths": changed,
            "forbidden_modified_paths": out_of_scope,
            "façade_public_callable_total": sum(x["public_top_level_callable_count"] for x in facade.values()),
            "facades": facade,
            "new_small_owner_count": len(owners),
            "new_small_owner_max_loc": max(sizes.values()) if sizes else None,
            "oversized_new_owners": over_limit,
            "all_source_checks_pass": code_scope_ok and facade_ok and owner_ok and stage_frozen,
        },
        "remote_suite_gates": {name: "PASS_IF_PRIOR_CI_STEP_SUCCESS" for name in REQUIRED_REMOTE_GATES},
        "local_acceptance_gates": {name: "NOT_RUN_NOT_IN_GITHUB" for name in LOCAL_GATES},
        "p152_stage": "OPEN",
        "p153_stage": "NOT_AUTHORIZED",
        "final_acceptance": "BLOCKED_PENDING_USER_LOCAL_INDEPENDENT_EVIDENCE",
        "closeout_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="branch_output/p152_integration_acceptance_snapshot.json")
    options = parser.parse_args()
    data = build_inventory()
    if not data["source_inventory"]["all_source_checks_pass"]:
        raise SystemExit("P1.5.2 source/scope/Owner/OPEN-state inventory FAIL")
    output = Path(options.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"P1.5.2 REMOTE SOURCE INVENTORY PASS: {data['git_sha']}")
    print(f"PUBLIC ABI COUNT: {data['source_inventory']['façade_public_callable_total']}")
    print(f"BOUNDED SMALL OWNERS: {data['source_inventory']['new_small_owner_count']}")
    print("CLOSEOUT: BLOCKED (user-local data + independent audits NOT RUN)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
