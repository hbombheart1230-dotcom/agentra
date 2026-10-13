"""T3-0: the static purity closure checker is portable, tri-state and fail-closed (ADVISORY evidence only)."""
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))

import p158_static_purity_closure as C  # noqa: E402


def _tree(tmp_path, files):
    for rel, src in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(src), encoding="utf-8")
    return str(tmp_path)


def _verdict(tmp_path, files, module, function, **kw):
    root = _tree(tmp_path, files)
    return C.check_function(root, module, function, **kw)


def test_script_has_no_hardcoded_local_path_and_requires_explicit_root():
    text = (ROOT / "scripts/refactor/p158_static_purity_closure.py").read_text(encoding="utf-8")
    assert "C:/AgentraEvidence" not in text and "r3_seam_clone" not in text and "C:\\\\" not in text
    assert "ADVISORY" in text


def test_pure_function_with_known_pure_stdlib_is_pure(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        import json
        def f(x):
            return json.dumps({"a": str(x).strip().lower()}, ensure_ascii=False)
        """}, "m.py", "f")
    assert r.verdict == C.PURE, r.as_dict()


def test_direct_io_is_impure(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        def f(p):
            return open(p).read()
        """}, "m.py", "f")
    assert r.verdict == C.IMPURE and any("open" in f.detail for f in r.findings)


def test_transitive_io_through_project_import_is_impure_with_chain(tmp_path):
    r = _verdict(tmp_path, {
        "libs/__init__.py": "",
        "libs/helper.py": """
            from pathlib import Path
            def load(p):
                return Path(p).read_text()
            """,
        "libs/m.py": """
            from libs.helper import load
            def mid(p):
                return load(p)
            def f(p):
                return mid(p)
            """}, "libs/m.py", "f")
    assert r.verdict == C.IMPURE
    chain = next(f.chain for f in r.findings if f.kind == C.IMPURE)
    assert chain[0].endswith("m.py::f") and any(c.endswith("helper.py::load") for c in chain)


def test_unresolved_call_is_unknown_not_pure(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        def f(x):
            return mystery(x)
        """}, "m.py", "f")
    assert r.verdict == C.UNKNOWN


def test_depth_exhaustion_is_unknown(tmp_path):
    src = "\n".join(f"def f{i}(x):\n    return f{i + 1}(x)\n" for i in range(8)) + "def f8(x):\n    return x\n"
    r = _verdict(tmp_path, {"m.py": src}, "m.py", "f0", max_depth=3)
    assert r.verdict == C.UNKNOWN and any("depth" in f.detail for f in r.findings)
    ok = _verdict(tmp_path, {"m.py": src}, "m.py", "f0", max_depth=64)
    assert ok.verdict == C.PURE


def test_external_unknown_import_is_unknown(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        import numpy as np
        def f(x):
            return np.mean(x)
        """}, "m.py", "f")
    assert r.verdict == C.UNKNOWN


def test_dynamic_facade_dispatch_is_unknown_without_module_and_resolved_with_it(tmp_path):
    files = {
        "owner.py": """
            def g(x, *, facade):
                return facade.pure_fn(x) + facade.load_it(x)
            """,
        "runner.py": """
            from pathlib import Path
            def pure_fn(x):
                return str(x)
            def load_it(p):
                return Path(p).read_text()
            """}
    root = _tree(tmp_path, files)
    assert C.check_function(root, "owner.py", "g").verdict == C.UNKNOWN
    r = C.check_function(root, "owner.py", "g", facade_module="runner.py")
    assert r.verdict == C.IMPURE
    pure_files = {"owner2.py": "def g(x, *, facade):\n    return facade.pure_fn(x)\n"}
    root2 = _tree(tmp_path, pure_files)
    assert C.check_function(root2, "owner2.py", "g", facade_module="runner.py").verdict == C.PURE


def test_recursion_cycle_terminates_and_pure_cycle_is_pure(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        def a(n):
            return b(n - 1) if n else 0
        def b(n):
            return a(n)
        """}, "m.py", "a")
    assert r.verdict == C.PURE
    r2 = _verdict(tmp_path, {"m2.py": """
        def a(n):
            return b(n)
        def b(n):
            print(n)
            return a(n - 1)
        """}, "m2.py", "a")
    assert r2.verdict == C.IMPURE


def test_dynamic_dispatch_through_local_variable_or_subscript_is_unknown(tmp_path):
    r = _verdict(tmp_path, {"m.py": """
        def f(deps, x):
            fn = deps["callable"]
            return fn(x)
        def g(deps, x):
            return deps["callable"](x)
        """}, "m.py", "f")
    assert r.verdict == C.UNKNOWN
    assert _verdict(tmp_path, {"m.py": "def g(deps, x):\n    return deps['c'](x)\n"}, "m.py", "g").verdict == C.UNKNOWN


def test_clock_env_and_logging_are_impure(tmp_path):
    for src in ("import os\ndef f():\n    return os.getenv('X')\n",
                "from datetime import datetime\ndef f():\n    return datetime.now()\n",
                "import logging\ndef f():\n    logging.info('x')\n",
                "def f(p):\n    return p.exists()\n"):
        assert _verdict(tmp_path, {"m.py": src}, "m.py", "f").verdict == C.IMPURE, src


def test_check_lines_picks_only_statements_in_range(tmp_path):
    root = _tree(tmp_path, {"m.py": """
        def f(p):
            a = str(p).strip()
            b = open(p)
            return a
        """})
    assert C.check_lines(root, "m.py", "f", 3, 3).verdict == C.PURE
    assert C.check_lines(root, "m.py", "f", 4, 4).verdict == C.IMPURE
    assert C.check_lines(root, "m.py", "f", 90, 91).verdict == C.UNKNOWN  # nothing in range -> not proven


def test_relative_imports_reexports_and_star_imports_are_followed(tmp_path):
    root = _tree(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/parts/__init__.py": "",
        "pkg/parts/core.py": """
            def io_helper(p):
                return open(p).read()
            def pure_helper(x):
                return str(x)
            """,
        "pkg/parts/api.py": "from .core import *\n",
        "pkg/facade.py": "from .parts.api import pure_helper, io_helper as legacy_io\n",
        "pkg/user.py": """
            from .facade import pure_helper, legacy_io
            def ok(x):
                return pure_helper(x)
            def bad(p):
                return legacy_io(p)
            """,
    })
    assert C.check_function(root, "pkg/user.py", "ok").verdict == C.PURE
    assert C.check_function(root, "pkg/user.py", "bad").verdict == C.IMPURE
