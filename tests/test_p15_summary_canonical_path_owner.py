"""P15: strategist_llm_summary ``_canonical_strategist_path_for_response`` moved to strategist_llm_summary_path_projection.canonical_strategist_path_for_response; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_path_projection as owner

GOLDEN = ["74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "8ad0e3108eb9ccba0669209203650440cf7ef1d75faf999e872523871bd384a4", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "8ad0e3108eb9ccba0669209203650440cf7ef1d75faf999e872523871bd384a4", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "b02eee17fa93f727dfe2e4056c3346c499de79c54cab4a47e653e0fe52fd92fe", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b", "13510e50b6d9ba11ded5730b81586b2905247dfc0d2d6d3ad1d6bbffee8c47e7"]

PATHS = [
    "response.json", "reports/llm/2026-10-20/run1/strategist/response.json", "reports/llm/2026-10-20/run1/response.json", "reports/llm/2026-10-20/run1/a/response.json", "/abs/reports/llm/D/R/response.json",
    "reports/other/2026-10-20/run1/strategist/response.json", "reports/llm/D/R/strategist/other.json", "x/llm/D/R/strategist/sub/response.json", "llm/D/R/response.json", "a/b/response.json", "reports/foo/llm/2026-10-20/run9/strategist/response.json",
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(PATHS)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = PATHS[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._canonical_strategist_path_for_response(Path(a))) == GOLDEN[i]
    assert _safe(lambda: owner.canonical_strategist_path_for_response(Path(a))) == GOLDEN[i]
    assert a == snap


def test_path_mapping_and_none_cases_without_touching_the_filesystem(tmp_path):
    f = lambda p: m._canonical_strategist_path_for_response(Path(p))
    assert f("response.json") is None and f("reports/llm/2026-10-20/run1/response.json") is None and f("reports/other/2026-10-20/run1/strategist/response.json") is None
    assert f("reports/llm/D/R/strategist/other.json") is None
    assert f("reports/llm/2026-10-20/run1/strategist/response.json") == Path("reports/canonical/2026-10-20/run1/strategist.json")
    assert f("reports/llm/2026-10-20/run1/a/response.json") == Path("reports/canonical/2026-10-20/run1/strategist.json")                  # nested category layout: day/run taken one level up
    assert f("x/llm/D/R/strategist/sub/response.json") == Path("x/canonical/D/strategist/strategist.json")                                   # second-level fallback keeps category as the run dir
    assert f("reports/foo/llm/2026-10-20/run9/strategist/response.json") == Path("reports/foo/canonical/2026-10-20/run9/strategist.json")
    before = sorted(tmp_path.iterdir())
    f(str(tmp_path / "llm" / "d" / "r" / "strategist" / "response.json"))
    assert sorted(tmp_path.iterdir()) == before                                                                                              # no filesystem access / creation


def test_owner_is_pure_and_takes_no_facade():
    assert "facade" not in inspect.signature(owner.canonical_strategist_path_for_response).parameters


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._canonical_strategist_path_for_response).splitlines()) <= 3
