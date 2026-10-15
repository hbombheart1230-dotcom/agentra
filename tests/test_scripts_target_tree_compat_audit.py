"""Static safety gates for the Scripts relocation compatibility auditor."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "scripts/diagnostics/audit_target_tree_compat.py"
SPEC = importlib.util.spec_from_file_location("script_layout_auditor", TOOL)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def _fixture(root: Path, *, corrupt: bool = False) -> None:
    old = root / "scripts/run_alpha.py"
    new = root / "scripts/research/run_alpha.py"
    example_old = root / "scripts/demo_m22.py"
    example_new = root / "scripts/examples/demo_m22.py"
    for path in (old, new, example_old, example_new):
        path.parent.mkdir(parents=True, exist_ok=True)
    new.write_text("def main():\n    return 0\n", encoding="utf-8")
    example_new.write_text("def main():\n    return 0\n", encoding="utf-8")
    old.write_text(
        "import importlib as _importlib\nimport runpy as _runpy\nimport sys as _sys\n"
        "if __name__ == '__main__':\n"
        f"    _runpy.run_module('scripts.research.{'wrong' if corrupt else 'run_alpha'}', run_name='__main__')\n"
        "else:\n    _sys.modules[__name__] = _importlib.import_module('scripts.research.run_alpha')\n",
        encoding="utf-8",
    )
    example_old.write_text(
        "import importlib as _importlib\nimport sys as _sys\n"
        "_impl = _importlib.import_module('scripts.examples.demo_m22')\n"
        "if __name__ == '__main__':\n    raise SystemExit(_impl.main())\n"
        "else:\n    _sys.modules[__name__] = _impl\n",
        encoding="utf-8",
    )
    manifest = {
        "candidates": [
            {"old": "scripts/run_alpha.py", "new": "scripts/research/run_alpha.py", "status": "moved"},
            {"old": "scripts/run_blocked.py", "new": "scripts/research/run_blocked.py", "status": "held"},
        ],
        "root_layout": [
            {"path": "scripts/run_alpha.py", "kind": "compatibility_wrapper"},
            {"path": "scripts/demo_m22.py", "kind": "compatibility_wrapper"},
        ],
    }
    path = root / "docs/refactor/2026-10-15_scripts_bulk_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest), encoding="utf-8")


def test_valid_wrapper_layout(tmp_path: Path) -> None:
    _fixture(tmp_path)
    result = MOD.audit(tmp_path)
    assert result == {"candidates": 2, "moved": 1, "held": 1,
                      "root_wrappers": 2, "checked": 2, "issues": [], "ok": True}


def test_mismatched_cli_dispatch_fails_closed(tmp_path: Path) -> None:
    _fixture(tmp_path, corrupt=True)
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert any("legacy main target mismatch" in x for x in result["issues"])


def test_missing_canonical_file_fails_closed(tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / "scripts/research/run_alpha.py").unlink()
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert any("missing canonical implementation" in x for x in result["issues"])


def test_audit_does_not_execute_target_source(tmp_path: Path) -> None:
    _fixture(tmp_path)
    canonical = tmp_path / "scripts/research/run_alpha.py"
    canonical.write_text("raise RuntimeError('must never execute')\n", encoding="utf-8")
    assert MOD.audit(tmp_path)["ok"]


def test_import_target_without_module_alias_fails_closed(tmp_path: Path) -> None:
    _fixture(tmp_path)
    path = tmp_path / "scripts/run_alpha.py"
    path.write_text(path.read_text().replace("_sys.modules[__name__] =", "_disconnected ="))
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert any("ABI alias" in issue for issue in result["issues"])


def test_run_module_without_main_execution_fails_closed(tmp_path: Path) -> None:
    _fixture(tmp_path)
    path = tmp_path / "scripts/run_alpha.py"
    path.write_text(path.read_text().replace("run_name='__main__'", "run_name='not_main'"))
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert any("executable __main__ dispatch" in issue for issue in result["issues"])


def test_commented_example_dispatch_fails_closed(tmp_path: Path) -> None:
    _fixture(tmp_path)
    path = tmp_path / "scripts/demo_m22.py"
    path.write_text(path.read_text().replace("raise SystemExit(_impl.main())", "pass  # _impl.main()"))
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert any("executable __main__ dispatch" in issue for issue in result["issues"])
