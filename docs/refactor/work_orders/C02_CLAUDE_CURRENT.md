# C02 — Claude A | A-20261031-11 | FAST-3 SINGLE EXECUTION ORDER

**PIN AT START:** integration/p1.5 issuance INPUT_HEAD=`bdab684749b90aac12f7e2ca037eee0adbcd5388`; C02 blob SHA from remote at start; A Actor branch `work/p15-a-reporter-pure-20261021` HEAD at design=`c56a0d7e0e867aceb818a0ccfe0473fe81faab69`. Previous A-20261031-10 order blob `ec2f78ac7fb9ffaf86b6d0fd419ecd21fa488244` is **8/8 REMOTE_DONE** at A HEAD `c56a0d7e0e867aceb818a0ccfe0473fe81faab69`; do not repeat. The new order never cancels a previously pinned run. This is the ONLY task specification; A must not read D00/RF/queue/C03/handoffs or select its own tasks.

**EIGHT NEW MANDATORY RF-035 SOURCE BODY MOVES:** execute A1–A8, or individually mark evidenced BLOCKED and continue all remaining safe items. The six former reserve functions have been re-verified against the **current A source blobs** and their original full BODY remains identical; target paths absent. A7/A8 are new read-only freshness predicate moves. Keep original signature, defaults, annotations, caller-visible import/monkeypatch and exception timing; SOURCE thin wrapper, Owner single BODY, no duplicate. For facade globals pass the source module at **call time**; preserve generators via `yield from`. Target never imports SOURCE. Use only fake/temp and mocked clock; no real broker/order/Guard/UEF/Step5C, operating state, live network, deployment, CI, frozen oracle or RunLab changes. Normal targeted unittest/pytest/smoke exit0 once per changed range suffices G2; no mandatory -O/full peer/hosted CI. A edits only own code/tests, pushes own branch normally and re-fetches remote SHA; C04 integrates, C05 alone accepts G1/G2/G3/DONE.

## A1 | RF-035 | libs/reporting/q8_historical_review.py::_read_json @ L18 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_read_projection.py::_read_json` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a1_read_json_owner.py`. Input→expected: temp JSON dict -> dict; invalid -> {}.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_read_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a1_read_json_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A2.

## A2 | RF-035 | libs/reporting/q8_historical_review.py::_iter_quant_shadow_candidate_rows @ L70 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_read_projection.py::_iter_quant_shadow_candidate_rows` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only, yield from; facade._quant_shadow_candidate_root/_iter_days/_read_json/Mapping. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a2_iter_quant_shadow_candidate_rows_owner.py`. Input→expected: temp 2-day fixture skips latest.json, stable order.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_read_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a2_iter_quant_shadow_candidate_rows_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A3.

## A3 | RF-035 | libs/reporting/q8_historical_review.py::_extract_trade_rows @ L243 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_trade_projection.py::_extract_trade_rows` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._read_json/_pct_from_ratio/_text/_trade_id_from_path. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a3_extract_trade_rows_owner.py`. Input→expected: temp ai_trade_summary.json -> trade_id/symbol/pnl_pct.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_trade_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a3_extract_trade_rows_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A4.

## A4 | RF-035 | libs/reporting/q8_historical_review.py::_daily_summary_rows @ L284 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_daily_projection.py::_daily_summary_rows` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._iter_days/_read_json/_int/_float/_text. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a4_daily_summary_rows_owner.py`. Input→expected: temp daily_summary.json -> one trade_count row.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_daily_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a4_daily_summary_rows_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A5.

## A5 | RF-035 | libs/reporting/q8_historical_review.py::_pattern_rows_from_daily_summaries @ L430 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_pattern_projection.py::_pattern_rows_from_daily_summaries` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. fake/temp read-only; facade._iter_days/_read_json/_text/_int/_float/_weighted_avg/defaultdict. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a5_pattern_rows_from_daily_summaries_owner.py`. Input→expected: temp two-day patterns -> weighted average and stable sort.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_pattern_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a5_pattern_rows_from_daily_summaries_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A6.

## A6 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_fresh_minute_fetch_enabled @ L119 | SOURCE_BLOB=859c85e32bf1e77fa724c08fa20dc2a78a0c7769

**TARGET:** `libs/reporting/post_exit_shadow_env_projection.py::_fresh_minute_fetch_enabled` (target function ABSENT at verified Actor HEAD; RF-035 exclusive A reporting owner). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

```python
def _fresh_minute_fetch_enabled() -> bool:
    raw = str(os.getenv("POST_EXIT_SHADOW_RECAP_FETCH_FRESH_MINUTES", "1")).strip().lower()
    return raw not in {"0", "false", "no", "off"}
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade.os, mock getenv. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles. Preserve original signature, lazy generator timing, original exception and output order. For every facade global read, resolve via `facade` at call time, SOURCE delegates with `facade=sys.modules[__name__]`; target must not import source. Existing callers and import monkeypatch seam must remain compatible. Report-only fake/temp fixture, no live effects.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a6_fresh_minute_fetch_enabled_owner.py`. Input→expected: mock env 'off'->False; '1'->True.. Compare original baseline with Owner and wrapper; include exception and facade monkeypatch parity. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_env_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a6_fresh_minute_fetch_enabled_owner.py -v` (normal exit0). Commit/push ONLY own code/test, re-fetch SOURCE/TARGET/test blob and Actor remote SHA; if blocked report exact reason and continue A7.

## A7 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_rows_reach_epoch @ L128 | SOURCE_BLOB=859c85e32bf1e77fa724c08fa20dc2a78a0c7769

**TARGET:** `libs/reporting/post_exit_shadow_freshness_projection.py::_rows_reach_epoch` (new RF-035 read-only projection owner, target path ABSENT at Actor HEAD). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

```python
def _rows_reach_epoch(rows: Iterable[Mapping[str, Any]], target_epoch: float | None) -> bool:
    if target_epoch is None:
        return False
    return any((_epoch_seconds(row.get("ts")) or 0.0) >= float(target_epoch) for row in rows if isinstance(row, Mapping))
```

**Thin wrapper / callers / monkeypatch / isolation:** Preserve same signature/annotations and facade import surface; SOURCE delegates to Owner using `facade=_r3_sys.modules[__name__]`. Rewrite references `_epoch_seconds`, `_row_kst_hhmmss`, `Mapping` to runtime facade or safe Owner imports, with patch-at-call-time parity; no SOURCE import from TARGET. Preserve short-circuit, generator consumption, exception timing. Only synthetic list rows, no real state, no fresh market fetch or operating action.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a7_rows_reach_epoch_owner.py`. Input→expected: facade._epoch_seconds patched to 200.0; rows=[{'ts':'fake'}], target_epoch=100.0 → True, target_epoch=300.0 → False; None → False. Compare baseline/Owner/wrapper, negative/exception and monkeypatch. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_freshness_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a7_rows_reach_epoch_owner.py -v` normal exit0. Commit/push own code/test, remote SHA/blob re-fetch; on failure record exact blocker and continue other safe items.

## A8 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_rows_reach_regular_close @ L134 | SOURCE_BLOB=859c85e32bf1e77fa724c08fa20dc2a78a0c7769

**TARGET:** `libs/reporting/post_exit_shadow_freshness_projection.py::_rows_reach_regular_close` (new RF-035 read-only projection owner, target path ABSENT at Actor HEAD). **EXACT SOURCE COMPUTATION BODY TO MOVE:**

```python
def _rows_reach_regular_close(rows: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        _row_kst_hhmmss(row) >= "153000"
        for row in rows
        if isinstance(row, Mapping) and _row_kst_hhmmss(row)
    )
```

**Thin wrapper / callers / monkeypatch / isolation:** Preserve same signature/annotations and facade import surface; SOURCE delegates to Owner using `facade=_r3_sys.modules[__name__]`. Rewrite references `_epoch_seconds`, `_row_kst_hhmmss`, `Mapping` to runtime facade or safe Owner imports, with patch-at-call-time parity; no SOURCE import from TARGET. Preserve short-circuit, generator consumption, exception timing. Only synthetic list rows, no real state, no fresh market fetch or operating action.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_11h_a8_rows_reach_regular_close_owner.py`. Input→expected: facade._row_kst_hhmmss patched to '153001' for [{'ts':'fake'}] → True; patched to '152959' → False; [] → False. Compare baseline/Owner/wrapper, negative/exception and monkeypatch. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_freshness_projection.py` and `python -m unittest tests/test_p15_rf035_11h_a8_rows_reach_regular_close_owner.py -v` normal exit0. Commit/push own code/test, remote SHA/blob re-fetch; on failure record exact blocker and continue other safe items.
## SIX VERIFIED FUTURE RESERVES — DESIGN ONLY, NOT EXECUTABLE THIS ORDER

All six SOURCE functions and actual BODY were read at A HEAD `c56a0d7e0e867aceb818a0ccfe0473fe81faab69`, with SOURCE blob and exclusive target absence checked. These are **future hypotheses**, not test PASS, not remote code MOVE, and not authorized for execution until new C03 order. Recheck freshness at promotion.

### R1 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/q8_historical_review.py::_aggregate_shadow_summaries @ L326 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_shadow_aggregate_projection.py::_aggregate_shadow_summaries` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str) -> Dict[str, Any]:
    reason_counter: Counter[str] = Counter()
    role_counter: Counter[str] = Counter()
    tactic_counter: Counter[str] = Counter()
    below_vwap_subtype_counter: Counter[str] = Counter()
    below_vwap_subtype_v2_counter: Counter[str] = Counter()
    vwap_reclaim_subtype_forward: Dict[str, ForwardAccumulator] = defaultdict(ForwardAccumulator)
    vwap_reclaim_subtype_forward_days: set[str] = set()
    group_acc: Dict[str, GroupAccumulator] = defaultdict(GroupAccumulator)
    q_days = 0
    q8_group_days = 0
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        q = payload.get("quant_shadow_candidate_evaluation") if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict) else {}
        if q.get("candidate_count") is not None:
            q_days += 1
        for row in list(q.get("by_reason") or []):
            if isinstance(row, Mapping):
                reason_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_role") or []):
            if isinstance(row, Mapping):
                role_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_tactic_id") or []):
            if isinstance(row, Mapping):
                tactic_counter[_text(row.get("name"))] += _int(row.get("count"))
        below_vwap = (
            q.get("below_vwap_reclaim_observation")
            if isinstance(q.get("below_vwap_reclaim_observation"), Mapping)
            else {}
        )
        for row in list(below_vwap.get("by_subtype") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(below_vwap.get("by_subtype_v2") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_v2_counter[_text(row.get("name"))] += _int(row.get("count"))
        lane_forward = (
            q.get("entry_lane_forward_outcomes")
            if isinstance(q.get("entry_lane_forward_outcomes"), Mapping)
            else {}
        )
        for row in list(lane_forward.get("by_lane_subtype") or []):
            if not isinstance(row, Mapping):
                continue
            name = _text(row.get("name"))
            if not name.startswith("vwap_reclaim:"):
                continue
            vwap_reclaim_subtype_forward[name].add(row)
            vwap_reclaim_subtype_forward_days.add(day)
        q8 = payload.get("q8_shadow_blocker_review") if isinstance(payload.get("q8_shadow_blocker_review"), dict) else {}
        groups = list(q8.get("groups") or [])
        if groups:
            q8_group_days += 1
        for row in groups:
            if not isinstance(row, Mapping):
                continue
            reason = _text(row.get("reason") or row.get("name"))
            if not reason:
                continue
            group_acc[reason].add(day, row)
    if not below_vwap_subtype_v2_counter:
        for row in _iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            observation = classify_below_vwap_reclaim_observation(row)
            if not bool(observation.get("applies")):
                continue
            below_vwap_subtype_v2_counter[_text(observation.get("subtype_v2"))] += 1
    subtype_forward_rows = [
        acc.to_dict(name)
        for name, acc in sorted(
            vwap_reclaim_subtype_forward.items(),
            key=lambda item: (item[1].candidate_count, item[0]),
            reverse=True,
        )
    ]
    for row in subtype_forward_rows:
        row["decision"] = _decision_for_reclaim_subtype(row)
    return {
        "q_shadow_day_count": q_days,
        "q8_group_day_count": q8_group_days,
        "by_reason": [{"name": name, "count": count} for name, count in reason_counter.most_common(20) if name],
        "by_role": [{"name": name, "count": count} for name, count in role_counter.most_common(12) if name],
        "by_tactic_id": [{"name": name, "count": count} for name, count in tactic_counter.most_common(12) if name],
        "below_vwap_reclaim_by_subtype": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_by_subtype_v2": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_v2_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_subtype_forward_day_count": len(vwap_reclaim_subtype_forward_days),
        "below_vwap_reclaim_subtype_forward": subtype_forward_rows,
        "q8_blocker_groups": [
            acc.to_dict(reason)
            for reason, acc in sorted(group_acc.items(), key=lambda item: item[1].candidate_count, reverse=True)
        ],
    }
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** empty temp report root for one-day interval → no group days; two fake daily summaries → reason/group totals equal baseline. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

### R2 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/q8_historical_review.py::_promotion_recommendations @ L496 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_recommendation_projection.py::_promotion_recommendations` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def _promotion_recommendations(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    groups = {str(row.get("reason")): dict(row) for row in list(payload.get("q8_blocker_groups") or []) if isinstance(row, Mapping)}
    recs: List[Dict[str, Any]] = []
    defensive = next(
        (
            row
            for row in list(payload.get("trade_by_tactic") or [])
            if str(row.get("name") or "") == "defensive_observe"
        ),
        {},
    )
    if defensive and int(defensive.get("count") or 0) >= 5 and float(defensive.get("avg_return_pct") or 0.0) < 0:
        recs.append(
            {
                "candidate": "risk_off_defensive_observe_no_entry_policy",
                "decision": "promoted_keep",
                "reason": "defensive_observe live trades are negative and 2026-06-08 showed severe risk-off misuse.",
            }
        )
    for reason, label in (
        ("below_vwap_reclaim_not_ready", "subtype_adjust_review"),
        ("breakout_not_ready", "adjust_and_retest"),
        ("pullback_not_mature", "adjust_and_retest"),
        ("volume_confirmation_missing", "retain_strict_or_observe"),
        ("human_chart_sanity_guard_blocked", "retain_veto_review_missed"),
    ):
        row = groups.get(reason) or {}
        if not row:
            continue
        recs.append(
            {
                "candidate": reason,
                "decision": label,
                "candidate_count": row.get("candidate_count"),
                "observed_count": row.get("observed_count"),
                "avg_latest_return_pct": row.get("avg_latest_return_pct"),
                "missed_opportunity_rate": row.get("missed_opportunity_rate"),
                "adverse_rate": row.get("adverse_rate"),
            }
        )
    subtype_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    if subtype_rows:
        strongest = max(
            subtype_rows,
            key=lambda row: (
                float(row.get("avg_return_15m_pct") or 0.0),
                float(row.get("avg_return_5m_pct") or 0.0),
                int(row.get("observed_count") or 0),
            ),
        )
        recs.append(
            {
                "candidate": "below_vwap_reclaim_subtype_policy",
                "decision": "do_not_relax_globally",
                "reason": (
                    f"Subtype forward evidence is mixed; strongest={strongest.get('name')} "
                    f"5m={float(strongest.get('avg_return_5m_pct') or 0.0):.4f}%, "
                    f"15m={float(strongest.get('avg_return_15m_pct') or 0.0):.4f}%. "
                    "Review classifier labels before behavior promotion."
                ),
            }
        )
    return recs
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** {'q8_blocker_groups':[],'trade_by_tactic':[]} → baseline empty recommendation list; fake negative defensive_observe group → identical advisory recommendation. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

### R3 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/q8_historical_review.py::build_q8_historical_review_payload @ L561 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_payload_projection.py::build_q8_historical_review_payload` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def build_q8_historical_review_payload(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> Dict[str, Any]:
    daily_rows = _daily_summary_rows(reports_root, start=start, end=end)
    trade_rows = _extract_trade_rows(reports_root, start=start, end=end)
    return_rows = [row for row in trade_rows if isinstance(row.get("pnl_pct"), (int, float))]
    shadow = _aggregate_shadow_summaries(reports_root, start=start, end=end)
    pattern_by_tactic = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="strategist",
        group_key="by_tactical_strategy",
    )
    pattern_by_exit = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="monitor_exit",
        group_key="by_exit_reason",
    )
    payload: Dict[str, Any] = {
        "schema_version": "q8_historical_review.v1",
        "behavior_effect": "evaluation_only",
        "start": str(start)[:10],
        "end": str(end)[:10],
        "daily_count": len(daily_rows),
        "daily_rows": daily_rows,
        "q8_promotion_eligibility": {
            "promotion_allowed_day_count": sum(1 for row in daily_rows if bool(row.get("q8_promotion_allowed"))),
            "trusted_gate_day_count": sum(1 for row in daily_rows if _text(row.get("q8_trust_gate_status"))),
            "status": (
                "promotion_review_possible"
                if any(bool(row.get("q8_promotion_allowed")) for row in daily_rows)
                else "promotion_blocked_by_trust_gate_or_legacy_data"
            ),
            "rule": "Historical conclusions require daily evaluation_trust_gate.promotion_allowed=true. Legacy daily summaries without trust gate are observation-only.",
        },
        "trade_summary": {
            "trade_report_count": len(trade_rows),
            "return_sample_count": len(return_rows),
            "avg_return_pct": _avg([float(row["pnl_pct"]) for row in return_rows]),
            "win_rate": round(sum(1 for row in return_rows if float(row["pnl_pct"]) > 0) / len(return_rows), 4)
            if return_rows
            else 0.0,
            "truth_sources": [
                {"name": name, "count": count}
                for name, count in Counter(_text(row.get("truth_source")) or "missing" for row in trade_rows).most_common(12)
            ],
        },
        "trade_by_tactic": pattern_by_tactic or _aggregate_return_rows(return_rows, "tactic"),
        "trade_by_entry_reason": _aggregate_return_rows(return_rows, "entry_reason"),
        "trade_by_exit_reason": pattern_by_exit or _aggregate_return_rows(return_rows, "exit_reason"),
        **shadow,
    }
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    if int(eligibility.get("promotion_allowed_day_count") or 0) <= 0:
        payload["promotion_recommendations"] = [
            {
                "candidate": "all_q8_candidates",
                "decision": "retain_under_observation",
                "reason": "no historical day passed the Q8 evaluation trust gate",
            }
        ]
    else:
        payload["promotion_recommendations"] = _promotion_recommendations(payload)
    return payload
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** empty temp reports root with start=end='2026-10-30' → schema_version='q8_historical_review.v1', daily_count=0, promotion gate remains blocked. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

### R4 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/q8_historical_review.py::render_q8_historical_review_markdown @ L637 | SOURCE_BLOB=1ed6e8755bcacaae445e7ec1ad8c9c8711544af8

**TARGET:** `libs/reporting/q8_historical_markdown_projection.py::render_q8_historical_review_markdown` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def render_q8_historical_review_markdown(payload: Mapping[str, Any]) -> str:
    trade = payload.get("trade_summary") if isinstance(payload.get("trade_summary"), Mapping) else {}
    lines: List[str] = [
        f"# Q8 Historical Review: {payload.get('start')} to {payload.get('end')}",
        "",
        "Purpose: reuse prior live and shadow evidence without mixing incompatible artifact eras.",
        "",
        "This review is evaluation-only. It does not change entry, exit, scanner, Strategist, or execution behavior.",
        "",
        "## Data Windows",
        "",
        "- Live trade performance: usable from 2026-05-18 onward when truth-surface PnL exists.",
        "- Q8 shadow evaluation: most useful from 2026-05-26 onward when candidate shadow summaries are populated.",
        "- Market regime rail: most useful from 2026-06-02 onward when rail IDs are attached to daily summaries.",
        "- Broker truth reconciliation: strongest from 2026-06-08 onward after post-close order-pair repair.",
        "",
        "## Live Trade Summary",
        "",
        f"- Trade report files: **{trade.get('trade_report_count', 0)}**",
        f"- Return samples: **{trade.get('return_sample_count', 0)}**",
        f"- Win rate: **{float(trade.get('win_rate') or 0.0) * 100:.2f}%**",
        f"- Average return: **{float(trade.get('avg_return_pct') or 0.0):.4f}%**",
        "",
    ]
    daily_rows = list(payload.get("daily_rows") or [])
    if daily_rows:
        lines.extend(
            _md_table(
                ["Day", "Trades", "Closed", "Returns", "Missing", "Win", "Avg", "Raw", "Deduped", "Trusted", "Gate", "Allowed", "Rail"],
                [
                    [
                        row.get("day"),
                        row.get("trade_count"),
                        row.get("closed_trade_count"),
                        row.get("return_sample_count"),
                        row.get("unavailable_return_count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.2f}%",
                        row.get("shadow_candidate_count") or 0,
                        row.get("shadow_deduped_candidate_count") or 0,
                        row.get("q8_trusted_forward_count") or 0,
                        row.get("q8_trust_gate_status") or "legacy/no_gate",
                        bool(row.get("q8_promotion_allowed")),
                        row.get("market_regime_rail") or "-",
                    ]
                    for row in daily_rows
                ],
            )
        )
        lines.append("")
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    lines.extend(
        [
            "## Q8 Promotion Eligibility",
            "",
            f"- status: `{eligibility.get('status') or 'unknown'}`",
            f"- trusted gate days: **{eligibility.get('trusted_gate_day_count') or 0}**",
            f"- promotion allowed days: **{eligibility.get('promotion_allowed_day_count') or 0}**",
            f"- rule: {eligibility.get('rule') or '-'}",
            "",
        ]
    )
    lines.extend(["## Trade Pattern Evidence", ""])
    for title, key in (
        ("By Tactic", "trade_by_tactic"),
        ("By Entry Reason", "trade_by_entry_reason"),
        ("By Exit Reason", "trade_by_exit_reason"),
    ):
        rows = list(payload.get(key) or [])
        lines.extend([f"### {title}", ""])
        lines.extend(
            _md_table(
                ["Name", "Count", "Win", "Avg"],
                [
                    [
                        row.get("name"),
                        row.get("count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.3f}%",
                    ]
                    for row in rows[:10]
                ],
            )
        )
        lines.append("")
    lines.extend(
        [
            "## Q8 Shadow Summary",
            "",
            f"- Q8 shadow summary days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Q8 blocker forward-review days: **{payload.get('q8_group_day_count', 0)}**",
            "",
            "### Top Shadow Reasons",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Reason", "Count"],
            [[row.get("name"), row.get("count")] for row in list(payload.get("by_reason") or [])[:15]],
        )
    )
    lines.extend(["", "### Forward Blocker Review", ""])
    lines.extend(
        _md_table(
            ["Reason", "n", "obs", "Latest", "MFE", "MAE", "Missed", "Adverse", "Decision"],
            [
                [
                    row.get("reason"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_latest_return_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_favorable_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_adverse_pct') or 0.0):.4f}%",
                    f"{float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%",
                    f"{float(row.get('adverse_rate') or 0.0) * 100:.1f}%",
                    row.get("dominant_decision") or "-",
                ]
                for row in list(payload.get("q8_blocker_groups") or [])[:10]
            ],
        )
    )
    subtype_rows = list(payload.get("below_vwap_reclaim_by_subtype") or [])
    subtype_v2_rows = list(payload.get("below_vwap_reclaim_by_subtype_v2") or [])
    subtype_forward_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    lines.extend(
        [
            "",
            "## Below-VWAP Reclaim Subtype Review",
            "",
            f"- Subtype count days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Subtype forward days: **{payload.get('below_vwap_reclaim_subtype_forward_day_count', 0)}**",
            "- Note: subtype forward evidence is available only after the entry-lane observation fields were added.",
            "",
            "### Subtype Counts",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Subtype", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_rows[:10]],
        )
    )
    lines.extend(["", "### Subtype V2 Counts", ""])
    lines.extend(
        _md_table(
            ["Subtype V2", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_v2_rows[:12]],
        )
    )
    lines.extend(["", "### Subtype Forward Outcomes", ""])
    lines.extend(
        _md_table(
            ["Subtype", "n", "obs", "3m", "5m", "15m", "30m", "60m", "MFE5", "MAE5", "Decision"],
            [
                [
                    row.get("name"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_return_3m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_15m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_30m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_60m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mfe_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mae_5m_pct') or 0.0):.4f}%",
                    row.get("decision") or "-",
                ]
                for row in subtype_forward_rows[:10]
            ],
        )
    )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(
        _md_table(
            ["Candidate", "Decision", "Evidence"],
            [
                [
                    row.get("candidate"),
                    row.get("decision"),
                    row.get("reason")
                    or (
                        f"n={row.get('candidate_count')}, obs={row.get('observed_count')}, "
                        f"latest={float(row.get('avg_latest_return_pct') or 0.0):.4f}%, "
                        f"missed={float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%, "
                        f"adverse={float(row.get('adverse_rate') or 0.0) * 100:.1f}%"
                    ),
                ]
                for row in list(payload.get("promotion_recommendations") or [])
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Operator Conclusion",
            "",
            "- Prior data is useful, but it must be sliced by artifact era.",
            "- Live trade PnL already shows persistent negative expectancy in stop/trend-break/low-break exits.",
            "- Q8 shadow raw sample size alone is not promotion evidence.",
            "- Promotion review requires trusted same-day forward outcomes, canonical dedupe, and evaluation_trust_gate.promotion_allowed=true.",
            "- Historical reports generated before the trust gate are legacy observation material, not policy-promotion evidence.",
            "",
        ]
    )
    return "\n".join(lines)
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** synthetic empty historical payload → byte-identical Markdown and headings as baseline. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

### R5 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/post_exit_shadow_recap.py::_utc_now_iso @ L51 | SOURCE_BLOB=859c85e32bf1e77fa724c08fa20dc2a78a0c7769

**TARGET:** `libs/reporting/post_exit_shadow_clock_projection.py::_utc_now_iso` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** mock datetime.now(timezone.utc) fixed 2026-10-31T00:00:00+00:00 → exact ISO text. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

### R6 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/post_exit_shadow_recap.py::_read_json @ L55 | SOURCE_BLOB=859c85e32bf1e77fa724c08fa20dc2a78a0c7769

**TARGET:** `libs/reporting/post_exit_shadow_read_projection.py::_read_json` (new, exclusive A RF-035 projection; verify fresh SHA before promotion). **EXACT UNMOVED SOURCE BODY:**

```python
def _read_json(path: Path) -> Dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}
```

**Owner/callers/monkeypatch:** preserve signature and exception timing; SOURCE becomes thin facade wrapper; Owner receives `facade` for module globals at use time (or imports pure stdlib names); no reverse import, no duplicate computation. Evaluation/report-only; use fake/temp roots or mock clock, never real trading/state/network/RunLab. **Reserve G2 hypothesis (NOT EXECUTABLE IN THIS ORDER):** temp {'a':1} JSON → {'a':1}; malformed/non-dict → {}. Compare baseline→Owner→wrapper and patch seam with a new targeted stdlib unittest; require normal exit0 and remote SHA before G1/G2 claim.

## REPORT AND CONTINUITY

Report to #11: `ORDER_ID=A-20261031-11 | CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | A1..A8 per-item status | SOURCE/TARGET/TEST_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only measured. Git auth failure is PUSH_BLOCKED only; continue other safe work. Do not run reserves or modify C01/B/C04/C05/RF/STATUS. A doc publication by C03 is not code G1/G2/G3.
