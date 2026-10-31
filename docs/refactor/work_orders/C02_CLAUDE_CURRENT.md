# C02 — Claude A | A-20261031-10 | FAST-3 SINGLE EXECUTION ORDER

**PIN AT START:** `integration/p1.5` HEAD at issuance `959ca9e9fdade3963fa25a2d12710d66ab218741`; remote `ORDER_FILE_BLOB_SHA` from this document; Actor branch `work/p15-a-reporter-pure-20261021` HEAD at start. Previous 09h order blob `348042a4957e35f026acd40e0a65f1d73533b6cf` is **8/8 REMOTE_DONE**, no repeat. A newly issued order never cancels an Actor's already pinned start order. This C-file is the only task specification: DO NOT read D00, RF, queue, C03, handoffs or select tasks independently.

**EIGHT MANDATORY NEW BODY MOVES:** Execute every item 1–8 or record individual evidence-based BLOCKED; continue other safe items after first PASS/commit/push failure. Exact SOURCE blob and target function absence verified at Actor remote. On refreshed SHA, classify already-moved actual BODY as REMOTE_DONE, not new work; if SOURCE changed and safety cannot be established, mark that item STALE/BLOCKED and continue. Move calculation BODY exactly once, leave thin facade and patch seam, preserve exceptions and output ordering. One normal targeted unittest/pytest/smoke exit0 is G2; no forced -O/full peer/hosted CI. Actor writes ONLY own code/tests; C04 integrates and C05 decides G1/G2/G3/DONE/STATUS. No operational/trading effects, real broker/guard/Step5C/UEF, RunLab, live network, real State, frozen oracle, CI or force push.

## A1 | RF-035 | libs/reporting/q8_historical_review.py::_text @ L49 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_scalar_projection.py::_text` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure text. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a1_text_owner.py`, explicit input→expected: ' unknown ' -> ''; 'valid' -> 'valid'. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a1_text_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A2 | RF-035 | libs/reporting/q8_historical_review.py::_weighted_avg @ L58 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_scalar_projection.py::_weighted_avg` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _weighted_avg(total: float, weight: int) -> float:
    return round(total / weight, 4) if weight > 0 else 0.0
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure scalar. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a2_weighted_avg_owner.py`, explicit input→expected: (3,2)->1.5; weight=0 ->0.0. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a2_weighted_avg_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A3 | RF-035 | libs/reporting/q8_historical_review.py::_quant_shadow_candidate_root @ L66 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_day_projection.py::_quant_shadow_candidate_root` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _quant_shadow_candidate_root(reports_root: Path) -> Path:
    return Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure path, no mkdir. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a3_quant_shadow_candidate_root_owner.py`, explicit input→expected: Path('/tmp/reports')->Path('/tmp/data/logs/quant_shadow_candidates'). Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_day_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a3_quant_shadow_candidate_root_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A4 | RF-035 | libs/reporting/q8_historical_review.py::_decision_for_reclaim_subtype @ L239 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_decision_projection.py::_decision_for_reclaim_subtype` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _decision_for_reclaim_subtype(row: Mapping[str, Any]) -> str:
    name = _text(row.get("name"))
    observed = _int(row.get("observed_count"))
    ret5 = _float(row.get("avg_return_5m_pct")) or 0.0
    ret15 = _float(row.get("avg_return_15m_pct")) or 0.0
    ret60 = _float(row.get("avg_return_60m_pct")) or 0.0
    mae5 = _float(row.get("avg_mae_5m_pct")) or 0.0
    if observed < 30:
        return "retain_observation_sample_small"
    if name.endswith("true_below_vwap_failure") and ret5 > 0 and ret15 > 0:
        return "review_classifier_or_label"
    if ret5 > 0 and ret15 > 0 and mae5 > -0.5:
        return "adjust_and_retest_candidate"
    if ret5 < 0 and ret15 < 0:
        return "keep_blocked"
    if ret60 > 0 and ret5 <= 0:
        return "hold_observation_longer_horizon_only"
    return "retain_under_observation"
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. read-only classification, facade._text/_int/_float; never promote. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a4_decision_for_reclaim_subtype_owner.py`, explicit input→expected: {'name':'x','observed_count':1}->'retain_observation_sample_small'. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_decision_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a4_decision_for_reclaim_subtype_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A5 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_as_dict @ L93 | SOURCE_BLOB=b536862b59964141ccbcc55c9e0352254176c625

**TARGET:** `libs/reporting/post_exit_shadow_scalar_projection.py::_as_dict` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a5_as_dict_owner.py`, explicit input→expected: {'x':1}->{'x':1}; []->{}. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a5_as_dict_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A6 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_as_list @ L97 | SOURCE_BLOB=b536862b59964141ccbcc55c9e0352254176c625

**TARGET:** `libs/reporting/post_exit_shadow_scalar_projection.py::_as_list` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a6_as_list_owner.py`, explicit input→expected: [1]->[1]; {}->[]. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a6_as_list_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A7 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_pct @ L274 | SOURCE_BLOB=b536862b59964141ccbcc55c9e0352254176c625

**TARGET:** `libs/reporting/post_exit_shadow_format_projection.py::_pct` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _pct(value: Any) -> str:
    try:
        return f"{float(value) * 100.0:.2f}%"
    except Exception:
        return "-"
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure display. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a7_pct_owner.py`, explicit input→expected: 0.125->'12.50%'; 'bad'->'-'. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_format_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a7_pct_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## A8 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_price @ L281 | SOURCE_BLOB=b536862b59964141ccbcc55c9e0352254176c625

**TARGET:** `libs/reporting/post_exit_shadow_format_projection.py::_price` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _price(value: Any) -> str:
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return "-"
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure display. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf035_10h_a8_price_owner.py`, explicit input→expected: 1234.6->'1,235'; 'bad'->'-'. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_format_projection.py` then `python -m unittest tests/test_p15_rf035_10h_a8_price_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## SIX VERIFIED FUTURE RESERVES — NOT EXECUTABLE THIS ORDER

All six have actual SOURCE BODY and exclusive absent TARGET verified at Actor HEAD; no reserve is code implementation or test PASS. Promote only by a future new C03 order.

### R1 VERIFIED | RF-035 | libs/reporting/q8_historical_review.py::_read_json @ L17 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_read_projection.py::_read_json` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _read_json(path: Path) -> Dict[str, Any]:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            payload = json.loads(path.read_text(encoding=encoding))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            continue
    return {}
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a1_read_json_owner.py`, explicit input→expected: temp JSON dict -> dict; invalid -> {}. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R2 VERIFIED | RF-035 | libs/reporting/q8_historical_review.py::_iter_quant_shadow_candidate_rows @ L70 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_read_projection.py::_iter_quant_shadow_candidate_rows` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _iter_quant_shadow_candidate_rows(reports_root: Path, *, start: str, end: str) -> Iterable[Dict[str, Any]]:
    root = _quant_shadow_candidate_root(reports_root)
    for day in _iter_days(start, end):
        day_root = root / day
        if not day_root.exists():
            continue
        for path in sorted(day_root.glob("*.json")):
            if path.name == "latest.json":
                continue
            payload = _read_json(path)
            for row in list(payload.get("candidates") or []):
                if isinstance(row, Mapping):
                    yield dict(row)
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only, yield from; facade._quant_shadow_candidate_root/_iter_days/_read_json/Mapping. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a2_iter_quant_shadow_candidate_rows_owner.py`, explicit input→expected: temp 2-day fixture skips latest.json, stable order. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R3 VERIFIED | RF-035 | libs/reporting/q8_historical_review.py::_extract_trade_rows @ L259 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_trade_projection.py::_extract_trade_rows` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _extract_trade_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in sorted((reports_root / "trades").glob("*/**/reports/ai_trade_summary.json")):
        try:
            day = path.parts[path.parts.index("trades") + 1]
        except Exception:
            continue
        if day < start or day > end:
            continue
        payload = _read_json(path)
        trade = payload.get("trade") if isinstance(payload.get("trade"), dict) else {}
        truth = payload.get("truth_surface") if isinstance(payload.get("truth_surface"), dict) else {}
        decision = payload.get("decision_flow") if isinstance(payload.get("decision_flow"), dict) else {}
        quant = payload.get("quant_tactic") if isinstance(payload.get("quant_tactic"), dict) else {}
        pnl_pct = _pct_from_ratio(truth.get("pnl_pct"))
        rows.append(
            {
                "day": day,
                "trade_id": _text(trade.get("trade_id")) or _trade_id_from_path(path),
                "symbol": _text(trade.get("symbol")),
                "status": _text(trade.get("status")),
                "pnl_pct": pnl_pct,
                "truth_source": _text(truth.get("truth_source")),
                "tactic": _text(
                    quant.get("tactic_id")
                    or quant.get("selected_tactic")
                    or trade.get("tactical_strategy")
                    or decision.get("tactical_strategy")
                ),
                "playbook": _text(quant.get("playbook") or trade.get("playbook") or decision.get("playbook")),
                "entry_reason": _text(decision.get("entry_reason") or decision.get("entry_trigger")),
                "exit_reason": _text(decision.get("exit_reason") or decision.get("exit_trigger")),
            }
        )
    return rows
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._read_json/_pct_from_ratio/_text/_trade_id_from_path. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a3_extract_trade_rows_owner.py`, explicit input→expected: temp ai_trade_summary.json -> trade_id/symbol/pnl_pct. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R4 VERIFIED | RF-035 | libs/reporting/q8_historical_review.py::_daily_summary_rows @ L300 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_daily_projection.py::_daily_summary_rows` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _daily_summary_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
        q = (
            payload.get("quant_shadow_candidate_evaluation")
            if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict)
            else {}
        )
        gate = q.get("evaluation_trust_gate") if isinstance(q.get("evaluation_trust_gate"), dict) else {}
        rail = payload.get("market_regime_rail_review") if isinstance(payload.get("market_regime_rail_review"), dict) else {}
        rows.append(
            {
                "day": day,
                "trade_count": _int(metrics.get("trade_count")),
                "closed_trade_count": _int(metrics.get("closed_trade_count")),
                "return_sample_count": _int(metrics.get("return_sample_count")),
                "unavailable_return_count": _int(metrics.get("unavailable_return_count")),
                "win_rate": _float(metrics.get("win_rate")) or 0.0,
                "avg_return_pct": _float(metrics.get("avg_return_pct")) or 0.0,
                "truth_surface_count": _int(metrics.get("truth_surface_count")),
                "shadow_candidate_count": _int(q.get("candidate_count")),
                "shadow_deduped_candidate_count": _int(q.get("deduped_candidate_count")),
                "shadow_duplicate_candidate_count": _int(q.get("duplicate_candidate_count")),
                "shadow_evaluated_count": _int(q.get("evaluated_count")),
                "shadow_would_enter_count": _int(q.get("would_enter_count")),
                "shadow_forward_outcome_coverage": _float(q.get("forward_outcome_coverage")),
                "q8_trust_gate_status": _text(gate.get("status")),
                "q8_promotion_allowed": bool(gate.get("promotion_allowed")),
                "q8_trusted_forward_count": _int(gate.get("trusted_forward_count")),
                "q8_trusted_forward_coverage": _float(gate.get("trusted_forward_coverage")),
                "q8_duplicate_rate": _float(gate.get("duplicate_rate")),
                "market_regime_rail": _text(rail.get("rail_id") or rail.get("market_regime_rail")),
            }
        )
    return rows
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._iter_days/_read_json/_int/_float/_text. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a4_daily_summary_rows_owner.py`, explicit input→expected: temp daily_summary.json -> one trade_count row. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R5 VERIFIED | RF-035 | libs/reporting/q8_historical_review.py::_pattern_rows_from_daily_summaries @ L446 | SOURCE_BLOB=ca4c2f9a8469577ec4ffdf8b9d1a6f9b5d485ec7

**TARGET:** `libs/reporting/q8_historical_pattern_projection.py::_pattern_rows_from_daily_summaries` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _pattern_rows_from_daily_summaries(
    reports_root: Path,
    *,
    start: str,
    end: str,
    section: str,
    group_key: str,
) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "closed_or_realized_count": 0,
            "win_count": 0,
            "loss_count": 0,
            "flat_count": 0,
            "return_sum": 0.0,
            "return_weight": 0,
            "cost_drag_loss_count": 0,
        }
    )
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        pattern = payload.get("pattern_performance") if isinstance(payload.get("pattern_performance"), dict) else {}
        section_payload = pattern.get(section) if isinstance(pattern.get(section), dict) else {}
        rows = section_payload.get(group_key) if isinstance(section_payload.get(group_key), list) else []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            name = _text(row.get("name")) or "missing"
            bucket = grouped[name]
            count = _int(row.get("count"))
            closed = _int(row.get("closed_or_realized_count") or count)
            avg = _float(row.get("avg_return_pct"))
            bucket["count"] += count
            bucket["closed_or_realized_count"] += closed
            bucket["win_count"] += _int(row.get("win_count"))
            bucket["loss_count"] += _int(row.get("loss_count"))
            bucket["flat_count"] += _int(row.get("flat_count"))
            bucket["cost_drag_loss_count"] += _int(row.get("cost_drag_loss_count"))
            if avg is not None and closed > 0:
                bucket["return_sum"] += float(avg) * closed
                bucket["return_weight"] += closed
    out: List[Dict[str, Any]] = []
    for name, bucket in grouped.items():
        closed = int(bucket.get("closed_or_realized_count") or 0)
        wins = int(bucket.get("win_count") or 0)
        out.append(
            {
                "name": name,
                "count": int(bucket.get("count") or 0),
                "closed_or_realized_count": closed,
                "win_count": wins,
                "loss_count": int(bucket.get("loss_count") or 0),
                "flat_count": int(bucket.get("flat_count") or 0),
                "win_rate": round(wins / closed, 4) if closed else 0.0,
                "avg_return_pct": _weighted_avg(float(bucket.get("return_sum") or 0.0), int(bucket.get("return_weight") or 0)),
                "cost_drag_loss_count": int(bucket.get("cost_drag_loss_count") or 0),
            }
        )
    out.sort(key=lambda row: (int(row.get("closed_or_realized_count") or 0), abs(float(row.get("avg_return_pct") or 0.0))), reverse=True)
    return out
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._iter_days/_read_json/_text/_int/_float/_weighted_avg/defaultdict. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a5_pattern_rows_from_daily_summaries_owner.py`, explicit input→expected: temp two-day patterns -> weighted average and stable sort. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R6 VERIFIED | RF-035 | libs/reporting/post_exit_shadow_recap.py::_fresh_minute_fetch_enabled @ L117 | SOURCE_BLOB=b536862b59964141ccbcc55c9e0352254176c625

**TARGET:** `libs/reporting/post_exit_shadow_env_projection.py::_fresh_minute_fetch_enabled` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _fresh_minute_fetch_enabled() -> bool:
    raw = str(os.getenv("POST_EXIT_SHADOW_RECAP_FETCH_FRESH_MINUTES", "1")).strip().lower()
    return raw not in {"0", "false", "no", "off"}
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade.os, mock getenv. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf035_10h_a6_fresh_minute_fetch_enabled_owner.py`, explicit input→expected: mock env 'off'->False; '1'->True. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

## REPORT AND CONTINUITY

Post to Issue #11: `ORDER_ID=A-20261031-10 | CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | A1..A8 statuses | SOURCE/TARGET/TEST_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only if measured. HTTPS auth failure is PUSH_BLOCKED only: continue safe tests, use already approved exact-tree lease workflow if available, never force-push. Report LOCAL_ONLY separately. Reserves are NOT executable in this order. C03 publication is not code G1/G2/G3.
