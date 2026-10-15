from pathlib import Path
from scripts.refactor.inventory_p15_consumers import inspect


def test_inventory_is_readonly_and_finds_observed_edges(tmp_path: Path):
    sources = {
        "libs/a/__init__.py": "",
        "libs/a/owner.py": "VALUE=1\n",
        "libs/a/user.py": "from .owner import VALUE\n",
        "libs/b/other.py": "from libs.a import owner\nimport importlib\nimportlib.import_module('libs.a.owner')\n",
        "libs/b/unknown.py": "import importlib\nimportlib.import_module('libs.'+'a.owner')\n",
        "scripts/runner.py": "from libs.a.owner import VALUE\n",
        "config/ops.yml": "run: scripts/runner.py\n",
    }
    for p, body in sources.items():
        path = tmp_path / p
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    r = inspect(tmp_path, sorted(sources))
    assert r["python"] == 6
    assert r["parse_errors"] == {}
    assert r["dynamic_literal_edges"] == 1
    assert r["dynamic_nonliteral_calls"] == 1
    assert r["root_script_count"] == 1
    assert r["root_script_refs"]["scripts/runner.py"] == ["config/ops.yml"]
    assert r["static_edges"] >= 3
