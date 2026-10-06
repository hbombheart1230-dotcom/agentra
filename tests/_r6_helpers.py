"""Shared helpers for the R6 / R6.1 / R6.2 evidence tests (not a test module)."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Mapping, Optional


def sync_owner(db_path: Path, *, instance_id: str, generation: int, lease_seconds: float = 3600.0) -> None:
    """Make the canonical runtime-ownership row say: this instance owns generation N with a live lease."""
    from libs.runtime.runtime_ownership import SQLiteRuntimeOwnershipStore

    SQLiteRuntimeOwnershipStore(str(db_path))  # creates the schema
    now = time.time()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "INSERT OR REPLACE INTO runtime_ownership "
            "(id, owner_id, instance_id, boot_id, acquired_at, heartbeat_at, lease_expires_at, generation) "
            "VALUES (1, 'test-owner', ?, '', ?, ?, ?, ?)",
            (instance_id, now, now, now + lease_seconds, int(generation)),
        )
        conn.commit()
    finally:
        conn.close()


def write_snapshot(path: Path, readiness: Mapping[str, Any], *, computed_at: Optional[float] = None) -> None:
    """Persisted readiness snapshot (the revalidation input used by paths without in-memory state)."""
    Path(path).write_text(
        json.dumps({"execution_readiness": dict(readiness), "computed_at_epoch": int(computed_at if computed_at is not None else time.time())}),
        encoding="utf-8",
    )


def count_execute_owned_order_calls(source: str) -> int:
    """AST caller scanner: direct calls, `from ... import execute_owned_order [as x]`, module-qualified
    calls (`mod.execute_owned_order(...)`, `pkg.intent_execution_owner.execute_owned_order(...)`),
    and simple name aliases (`fn = execute_owned_order`). Arbitrary dynamic dispatch is out of scope."""
    import ast

    tree = ast.parse(source)
    names = {"execute_owned_order"}
    changed = True
    while changed:  # follow simple alias chains (x = execute_owned_order; y = x)
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "execute_owned_order" and (alias.asname or alias.name) not in names:
                        names.add(alias.asname or alias.name)
                        changed = True
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                value = node.value
                refers = (isinstance(value, ast.Name) and value.id in names) or (
                    isinstance(value, ast.Attribute) and value.attr == "execute_owned_order")
                if refers and node.targets[0].id not in names:
                    names.add(node.targets[0].id)
                    changed = True
    total = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in names:
            total += 1
        elif isinstance(func, ast.Attribute) and func.attr == "execute_owned_order":
            total += 1
    return total
