"""Green-first hostile probes and real frozen-stage obstruction, without editing frozen Owners."""
import ast
import importlib
from pathlib import Path

import pytest

from test_p15_operator_brief_folder_parity import ROOT, PREFIX, baseline, pinned, run

# Use the real pytest rewrite import hook even under python -O. A raw
# spec.loader.exec_module would erase the frozen checker's asserts.
pytest.register_assert_rewrite("test_p153_operator_ui_moved_bodies")


@pytest.mark.parametrize("kind", ["chart", "stop_priority", "guard", "rank", "section_order", "market_status", "prompt_budget", "unicode", "missing_key", "extra_callback"])
def test_real_green_baseline_then_hostile_projection_difference(kind, monkeypatch):
    case = "long" if kind == "prompt_budget" else "filters"
    original = run(case, "base", monkeypatch)
    assert run(case, "candidate", monkeypatch) == original
    evidence = importlib.import_module("apps.operator_ui.data_access_brief_evidence_projection_p15")
    market = importlib.import_module("apps.operator_ui.data_access_brief_market_sections")
    presentation = importlib.import_module("apps.operator_ui.data_access_brief_presentation_projection_p15")
    facade = importlib.import_module("apps.operator_ui.data_access_core")
    if kind in {"chart", "extra_callback"}:
        target = evidence.chart_evidence
        def bad(*a, **kw):
            result = target(*a, **kw)
            if kind == "chart": result[0].append("FORGED CHART PASS")
            else: kw["facade"]._safe_int("extra_callback", 0)
            return result
        monkeypatch.setattr(evidence, "chart_evidence", bad)
    elif kind == "stop_priority":
        monkeypatch.setattr(evidence, "merge_stop_evidence", lambda *a: {"mutated_priority": "snapshot_before_runtime"})
    elif kind == "guard":
        target = market.build_market_readout
        def bad(*a, **kw):
            macro, rows = target(*a, **kw)
            for row in rows: row["status"] = "PASS"
            return macro, rows
        monkeypatch.setattr(market, "build_market_readout", bad)
    elif kind == "prompt_budget":
        target = facade._trim_text
        monkeypatch.setattr(facade, "_trim_text", lambda text, *, max_len: target(text, max_len=3))
    elif kind == "unicode":
        # Core retains the imported function alias; mutate the ACTUAL use-site,
        # not the unreferenced post-import owner attribute.
        monkeypatch.setattr(facade, "_sanitize_operator_brief_text_r3_impl", lambda text, *, facade: str(text))
    else:
        name = "market_context" if kind == "market_status" else "scanner_focus"
        target = getattr(presentation, name)
        def bad(*a, **kw):
            row = target(*a, **kw)
            if kind == "rank": row["selected_rank"] = 999
            if kind == "section_order": row = dict(reversed(list(row.items())))
            if kind == "market_status": row["defensive_mode"] = "disabled"
            if kind == "missing_key": row.pop("selected_symbol")
            return row
        monkeypatch.setattr(presentation, name, bad)
    assert run(case, "candidate", monkeypatch) != original


@pytest.mark.parametrize("owner,function", [
    ("data_access_brief_canonical_input", "_build_canonical_trade_brief_input"),
    ("data_access_brief_compaction", "_compact_operator_brief_input_for_llm"),
    ("data_access_brief_sanitation", "_sanitize_operator_brief_text"),
])
def test_actual_r3_gate_rejects_even_equivalent_body_reorganization(owner, function, monkeypatch):
    path = ROOT / PREFIX / (owner + ".py")
    source = path.read_text(encoding="utf-8")
    assert source.replace("\r\n", "\n") == pinned(owner)
    gate = importlib.import_module("test_p153_operator_ui_moved_bodies")
    row = next(r for r in gate.MOVES if r[1] == function)
    gate.test_use_site_qualification_is_the_only_body_change(*row)  # The REAL frozen positive first.
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function + "_r3_impl")
    fn.body = [ast.If(test=ast.Constant(True), body=fn.body, orelse=[])]
    changed = ast.unparse(ast.fix_missing_locations(tree))
    reader = Path.read_text
    def overlay(p, *a, **kw):
        return changed if p == path else reader(p, *a, **kw)
    with monkeypatch.context() as m:
        m.setattr(Path, "read_text", overlay)
        with pytest.raises(AssertionError) as rejected:
            gate.test_use_site_qualification_is_the_only_body_change(*row)
        assert function in str(rejected.value)
    assert path.read_text(encoding="utf-8") == source  # No pinned file ever written.
