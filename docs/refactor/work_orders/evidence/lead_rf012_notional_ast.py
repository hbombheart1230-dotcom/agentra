"""RF-012 isolated price resolver check. No import of trading modules or network/order calls.
Run from repo root: PYTHONDONTWRITEBYTECODE=1 python [-O] docs/refactor/work_orders/evidence/lead_rf012_notional_ast.py
RF012_SOURCE can point at a detached copy; default requires the exact GitHub blob.
"""
import ast
import copy
import hashlib
import math
import os
from pathlib import Path
from typing import Any, Dict, Tuple

src = Path(os.environ.get("RF012_SOURCE", "graphs/nodes/execute_from_packet.py"))
data = src.read_bytes()
if not os.environ.get("RF012_SOURCE"):
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != "1a10af59e5e9b4035f1c7403e5aeb814f65c8e3a":
        raise SystemExit(f"FAIL: source blob mismatch {blob}")
tree = ast.parse(data.decode("utf-8-sig"), filename=str(src))
names = {"_coerce_float", "_positive_price_from_row", "_resolve_order_price_for_notional_with_source"}
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
if {node.name for node in nodes} != names:
    raise SystemExit("FAIL: exact pure helpers missing")
ns = {
    "Any": Any, "Dict": Dict, "Tuple": Tuple,
    "_extract_order_symbol": lambda order: str(order.get("symbol") or "").strip(),
    "_symbol_matches_row": lambda row, symbol: not symbol or not row.get("symbol") or row.get("symbol") == symbol,
    "_extract_market_quotes_safe": lambda state: state.get("fake_quotes", {}),
    "_canonical_artifact_row": lambda state, agent: {},
}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(src), "exec"), ns)
resolve = ns["_resolve_order_price_for_notional_with_source"]
cases = [
    ("order_direct_inf", {}, {"symbol":"005930","price":float("inf")}, "order.price", "inf"),
    ("order_meta_inf", {}, {"symbol":"005930","meta":{"price":float("inf")}}, "order.meta.price", "inf"),
    ("market_snapshot_inf", {"market_snapshot":{"symbol":"005930","price":float("inf")}}, {"symbol":"005930"}, "market_snapshot.price", "inf"),
    ("selected_inf", {"selected":{"symbol":"005930","price":float("inf")}}, {"symbol":"005930"}, "selected.price", "inf"),
    ("quote_inf", {"fake_quotes":{"005930":{"best_ask":float("inf")}}}, {"symbol":"005930"}, "market.quote.best_ask", "inf"),
    ("inf_over_finite", {"selected":{"symbol":"005930","price":5000},"market_snapshot":{"symbol":"005930","price":float("inf")}}, {"symbol":"005930"}, "market_snapshot.price", "inf"),
    ("nan_ignored", {"market_snapshot":{"symbol":"005930","price":float("nan")}}, {"symbol":"005930"}, "", "zero"),
    ("finite_control", {"market_snapshot":{"symbol":"005930","price":5000}}, {"symbol":"005930"}, "market_snapshot.price", "finite"),
    ("negative_selected_abs", {"selected":{"symbol":"005930","price":-7000}}, {"symbol":"005930"}, "selected.price", "finite"),
]
for label, state, order, source, kind in cases:
    before = copy.deepcopy((state, order))
    value, got_source = resolve(state, order)
    ok = math.isinf(value) if kind == "inf" else value == 0 if kind == "zero" else math.isfinite(value) and value > 0
    if got_source != source or not ok or repr((state, order)) != repr(before):
        raise SystemExit(f"FAIL: {label}: {(value, got_source)}")
print(f"RF012_NOTIONAL_AST_OK cases={len(cases)} inf=6 nan_ignored=1 writes=0 debug={__debug__}")
