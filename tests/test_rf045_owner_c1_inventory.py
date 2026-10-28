"""RF-045 C1: explicit owner action classes, without running their effects."""

from __future__ import annotations

import ast
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_EXPECTED = {
    "__init__.py": ("KEEP_PURE", set()),
    "api_response.py": ("KEEP_PURE", set()),
    "event_logger.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"mkdir", "open"}),
    "event_logger_compat.py": ("KEEP_WRAPPER", set()),
    "evidence_identity.py": ("KEEP_PURE", set()),
    "http_client.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"request"}),
    "log_maintenance.py": ("TEMP_FAKE_EFFECT_REQUIRED", {"mkdir", "rmtree", "unlink", "write_text"}),
    "path_isolation.py": ("KEEP_PURE", set()),
    "settings.py": ("KEEP_ENV_READER", set()),
    "symbols.py": ("KEEP_PURE", set()),
}
_EFFECT_NAMES = {"mkdir", "open", "request", "rmtree", "unlink", "write_text"}


def _effect_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
            if name in _EFFECT_NAMES:
                found.add(name)
    return found


def test_rf045_all_core_owners_have_explicit_effect_classification():
    """C1 classification guards current pure/wrapper/env/temp-fake boundaries."""
    owners = {path.name for path in (_ROOT / "libs/core").glob("*.py")}
    assert owners == set(_EXPECTED)
    assert {
        name: _effect_names(_ROOT / "libs/core" / name) for name in _EXPECTED
    } == {name: expected[1] for name, expected in _EXPECTED.items()}
