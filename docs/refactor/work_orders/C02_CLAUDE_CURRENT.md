# Agentra P1.5 FAST-3 — C02 A-20261030-23 NEW 8 verified RF-035 BODY MOVEs

**C03 supply (UTC measured issuance):** 2026-10-30T14:02:56.409Z. Canonical INPUT_SHA `130498f922874a932ad9e41b77625e5177f6a5dd`; A remote HEAD `92bde2e7c89aba6c97372d4fc56b73c70f394bc6`; old C02 blob `d48318ce25ab2595ac14b833cbc10528ddfd9731`. The previous A1–A8 (controlled_validation_daily six, strategist_llm_summary two) are **8/8 REMOTE_DONE**, confirmed at A `92bde2e7c89aba6c97372d4fc56b73c70f394bc6` and Issue #11 `6523832263` with normal 26 PASS; NEVER retest/reassign them. New SOURCE blobs: `libs/reporting/daily_report_generator.py`=`cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf`, `libs/reporting/market_regime_rail_review.py`=`e6cfd5280d597602ba167ec1d3cc5fac29080a3c`; same on A/integration. All four new TARGET paths absent (404) on both branches before issuance. RF-035 exclusive Claude A ownership includes both SOURCE files per RF-035 coverage; B owns unrelated RF-063/065 and must not be touched. This document is design/supply, NOT G1/G2/G3 implementation.

**One-file execution contract:** Read only this C02 to execute; no D00, RF, queue, detailed design, or autonomous task choice. Pin remote integration SHA/C02 blob/A remote SHA/local SHA before each item. Work only on `work/p15-a-reporter-pure-20261021` and code/test paths listed below. Move every original calculation BODY to one new owner, leave original exact-signature thin facade wrapper, preserve call-time monkeypatch and original bytes/errors; no duplicate body or reverse import. Add `from __future__ import annotations` and necessary typing imports in new modules. Run isolated normal targeted tests; FAST-3 G2 needs one normal exit0, not mandatory -O/full peer/CI. Execute A1→A8 sequentially; one BLOCKED item never cancels remaining safe items. Commit code/tests only; normal push A and refetch remote SHA/blob/tree after each push. Terminal HTTPS auth failure: preserve local commit, use approved exact-tree write only when reviewed tree/parent identity provable, else PUSH_BLOCKED and continue safely. Do not touch B branch, integration code, D00/C01/C02/RF/queue/STATUS/HANDOFF/C04/C05, main, production logs, runtime state, real broker/order, Guard/Step5C/UEF, RunLab or operating policy. All fixtures fake/tmp only; never execute real trading or report generation on live paths. C04 integrates, C05 exclusively judges G1/G2/G3/DONE.

## A1 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_iter_events` blob `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` → TARGET `libs/reporting/daily_report_generator_read_projection.py::_iter_events` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _iter_events(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    def gen():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    return gen()
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `daily_report_generator_read_projection._iter_events`; add `import sys` to SOURCE if needed. `json.loads` → `facade.json.loads` inside the lazy nested generator; preserve missing-path [] vs generator and broad Exception swallowing. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_1_iter_events_owner.py`: tmp_path absent → []; JSONL lines `{\"event\":1}`, `BAD`, blank, `{\"event\":2}` → ordered `[{'event':1},{'event':2}]`; patched facade.json.loads raising → no rows. Compare list() of pre-move source, owner and wrapper; no production logs. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_read_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_1_iter_events_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A2; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A2 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_find_trade_dir` blob `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` → TARGET `libs/reporting/daily_report_generator_read_projection.py::_find_trade_dir` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _find_trade_dir(reports_root: Path, day: str, trade_id: str) -> Path | None:
    direct = reports_root / "trades" / day / trade_id
    if direct.exists():
        return direct
    matches = sorted((reports_root / "trades" / day).glob(f"*/{trade_id}"))
    return matches[0] if matches else None
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `daily_report_generator_read_projection._find_trade_dir`; add `import sys` to SOURCE if needed. No module-global helper; exact-signature thin wrapper may delegate without facade. Preserve direct path priority and sorted `glob` fallback, including glob metacharacter behavior. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_2_find_trade_dir_owner.py`: tmp_path/trades/2026-10-30/T1 direct → direct; only tmp_path/trades/2026-10-30/SYM/T1 → nested; absent → None; two nested dirs → sorted first. No production report root. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_read_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_2_find_trade_dir_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A3; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A3 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_broker_closed_symbols_from_alignment` blob `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` → TARGET `libs/reporting/daily_report_generator_trade_projection.py::_broker_closed_symbols_from_alignment` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _broker_closed_symbols_from_alignment(broker_alignment: Dict[str, Any] | None) -> set[str]:
    if not isinstance(broker_alignment, dict):
        return set()
    snapshot = broker_alignment.get("account_snapshot") if isinstance(broker_alignment.get("account_snapshot"), dict) else {}
    symbols = snapshot.get("day_trade_closed_symbols") if isinstance(snapshot.get("day_trade_closed_symbols"), list) else []
    out = {
        normalize_symbol(symbol, allow_test_symbols=True)
        for symbol in symbols
        if normalize_symbol(symbol, allow_test_symbols=True)
    }
    rows = snapshot.get("day_trade_diary_rows") if isinstance(snapshot.get("day_trade_diary_rows"), list) else []
    for row in rows:
        if not isinstance(row, dict) or not bool(row.get("closed_by_day_trade_diary")):
            continue
        symbol = normalize_symbol(row.get("symbol"), allow_test_symbols=True)
        if symbol:
            out.add(symbol)
    return out
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `daily_report_generator_trade_projection._broker_closed_symbols_from_alignment`; add `import sys` to SOURCE if needed. `normalize_symbol` → `facade.normalize_symbol` at invocation time, including repeated calls in set comprehension and diary loop; preserve allow_test_symbols=True and skip invalid rows. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_3_broker_closed_symbols_from_alignment_owner.py`: None → empty set; fake snapshot day_trade_closed_symbols=['aaa'] plus diary row symbol='bbb', closed_by_day_trade_diary=True → {'AAA','BBB'} under patched source normalize_symbol uppercasing; unclosed and non-dict diary rows ignored; patch seam and baseline parity. No broker connection or account query. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_trade_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_3_broker_closed_symbols_from_alignment_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A4; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A4 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_render_residual_positions_markdown` blob `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` → TARGET `libs/reporting/daily_report_generator_trade_projection.py::_render_residual_positions_markdown` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _render_residual_positions_markdown(residual: Dict[str, Any]) -> List[str]:
    positions = residual.get("positions") if isinstance(residual.get("positions"), list) else []
    lines = ["", "## 장마감 잔여 보유 종목", ""]
    if not bool(residual.get("available")):
        lines.append("- 상태 스냅샷을 읽지 못해 잔여 보유 종목을 확인하지 못했습니다.")
        return lines
    if not positions:
        lines.append("- 장마감 기준 잔여 보유 종목이 없습니다.")
        return lines
    closeout = residual.get("closeout_state") if isinstance(residual.get("closeout_state"), dict) else {}
    reconciled = (
        residual.get("reconciled_closed_positions")
        if isinstance(residual.get("reconciled_closed_positions"), list)
        else []
    )
    closeout_mode = str(closeout.get("mode") or "").strip()
    closeout_reason = str(closeout.get("reason") or "").strip()
    if closeout_mode or closeout_reason:
        closeout_line = f"- closeout 상태: {closeout_mode or '-'} / {closeout_reason or '-'}"
        closeout_note = str(closeout.get("report_note") or "").strip()
        if closeout_note:
            closeout_line += f" ({closeout_note})"
        lines.append(closeout_line)
    if reconciled:
        symbols = ", ".join(
            str(row.get("symbol") or "").strip()
            for row in reconciled
            if isinstance(row, dict) and str(row.get("symbol") or "").strip()
        )
        if symbols:
            lines.append(f"- 장중 청산 확인: {symbols}는 당일 전량 매도 기록으로 잔여 보유에서 제외했습니다.")
    for row in positions:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "-")
        status = str(row.get("status") or "잔여 보유")
        qty = int(row.get("qty") or 0)
        avg_price = row.get("avg_price")
        current_price = row.get("current_price")
        pnl_ratio = row.get("account_pnl_ratio")
        reason = str(row.get("overnight_reason") or "").strip()
        decision_label = str(row.get("overnight_decision_label") or "").strip()
        price_text = f"평균 {avg_price:,.0f}" if isinstance(avg_price, (int, float)) and avg_price else "평균 -"
        current_text = f"현재 {current_price:,.0f}" if isinstance(current_price, (int, float)) and current_price else "현재 -"
        ratio_text = f" / 평가 손익률 {float(pnl_ratio) * 100:.2f}%" if isinstance(pnl_ratio, (int, float)) else ""
        detail = f"- {symbol}: {status} / {qty}주 / {price_text} / {current_text}{ratio_text}"
        if decision_label:
            detail += f" / 오버나이트 판단: {decision_label}"
        if reason and not bool(row.get("overnight_decision_missing")):
            detail += f" / 사유 {reason}"
        if bool(row.get("weekend_carry")):
            detail += f" / 주말 보유 {int(row.get('holding_gap_days') or 3)}일"
        lines.append(detail)
        if bool(row.get("weekend_carry")) and not bool(row.get("allow_weekend_carry")):
            lines.append("  - 주의: 금요일 carry 승인이라 주말 갭 리스크가 포함됩니다.")
        missing_detail = str(row.get("overnight_missing_detail") or "").strip()
        if bool(row.get("overnight_decision_missing")) and missing_detail:
            lines.append(f"  - 판단 기록 근거: {missing_detail}")
        signals = [str(x) for x in list(row.get("overnight_positive_signals") or []) if str(x or "").strip()]
        blockers = [str(x) for x in list(row.get("overnight_blockers") or []) if str(x or "").strip()]
        if signals:
            lines.append(f"  - 승인 근거: {', '.join(signals[:5])}")
        if blockers:
            lines.append(f"  - 차단/주의 근거: {', '.join(blockers[:5])}")
    return lines
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `daily_report_generator_trade_projection._render_residual_positions_markdown`; add `import sys` to SOURCE if needed. No global helpers. Pure dict→ordered Markdown lines; preserve numeric formatting, all Korean text, weekend carry warnings, errors and list order. Do not read live positions. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_4_render_residual_positions_markdown_owner.py`: {'available':False} → snapshot-unavailable line; {'available':True,'positions':[]} → no-position line; fake one row qty=2, avg_price=1000, current_price=1100, account_pnl_ratio=.1, weekend_carry=True → `2주`, `평가 손익률 10.00%`, weekend warning; qty='invalid' raises ValueError in both. No live account. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_trade_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_4_render_residual_positions_markdown_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A5; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A5 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::_to_float` blob `e6cfd5280d597602ba167ec1d3cc5fac29080a3c` → TARGET `libs/reporting/market_regime_rail_review_scalar_projection.py::_to_float` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `market_regime_rail_review_scalar_projection._to_float`; add `import sys` to SOURCE if needed. No module globals; exact signature/default. Preserve catch-all Exception and float(default) conversion, including NaN semantics. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_5_to_float_owner.py`: '2.5'→2.5; None/default=1→1.0; 'bad'/default=3→3.0; float('nan') remains nan (math.isnan); invalid default propagates ValueError as original. Fake values only. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_review_scalar_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_5_to_float_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A6; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A6 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::_indicator` blob `e6cfd5280d597602ba167ec1d3cc5fac29080a3c` → TARGET `libs/reporting/market_regime_rail_review_scalar_projection.py::_indicator` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _indicator(snapshot: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    macro = snapshot.get("macro_indicators") if isinstance(snapshot.get("macro_indicators"), Mapping) else {}
    indicators = macro.get("indicators") if isinstance(macro.get("indicators"), Mapping) else {}
    row = indicators.get(key) if isinstance(indicators.get(key), Mapping) else {}
    return row
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `market_regime_rail_review_scalar_projection._indicator`; add `import sys` to SOURCE if needed. `Mapping` in every isinstance → `facade.Mapping` at call time. Return the original row object (identity), not a copy; missing/invalid branches {}. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_6_indicator_owner.py`: {'macro_indicators':{'indicators':{'kospi':{'change_pct':1}}}}→same row object; missing/invalid nested dict→{}; facade.Mapping patch seam with compatible mapping type; no macro file read. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_review_scalar_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_6_indicator_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A7; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A7 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::_change_pct` blob `e6cfd5280d597602ba167ec1d3cc5fac29080a3c` → TARGET `libs/reporting/market_regime_rail_review_scalar_projection.py::_change_pct` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def _change_pct(snapshot: Mapping[str, Any], key: str) -> float:
    index_moves = snapshot.get("index_moves") if isinstance(snapshot.get("index_moves"), Mapping) else {}
    move_key = f"{key}_pct"
    if move_key in index_moves:
        return _to_float(index_moves.get(move_key), 0.0)
    return _to_float(_indicator(snapshot, key).get("change_pct"), 0.0)
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `market_regime_rail_review_scalar_projection._change_pct`; add `import sys` to SOURCE if needed. `Mapping` → `facade.Mapping`; `_to_float` → `facade._to_float`; `_indicator` → `facade._indicator` at call time. Preserve index_moves explicit key precedence and fallback. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_7_change_pct_owner.py`: {'index_moves':{'kospi_pct':'1.2'}}→1.2; fallback macro_indicators.indicators.kospi.change_pct='-0.4'→-0.4; empty→0.0; patch facade._to_float sentinel to prove call-time seam; no real market inputs. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_review_scalar_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_7_change_pct_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue A8; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## A8 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::render_market_regime_rail_markdown` blob `e6cfd5280d597602ba167ec1d3cc5fac29080a3c` → TARGET `libs/reporting/market_regime_rail_review_markdown_projection.py::render_market_regime_rail_markdown` (new, A/integration 404 verified)

**MOVE exactly this original calculation BODY** from SOURCE into TARGET (not a copy). Preserve signature, docstring, output, exception, ordering, lazy evaluation and monkeypatch behavior:

```python
def render_market_regime_rail_markdown(rail: Mapping[str, Any], *, day: str) -> str:
    inputs = rail.get("market_inputs") if isinstance(rail.get("market_inputs"), Mapping) else {}
    lines = [
        f"# Market Regime Rail Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Rail",
        "",
        f"- rail_id: `{rail.get('rail_id') or 'not_available'}`",
        f"- confidence: `{rail.get('rail_confidence') or 'none'}`",
        f"- behavior_effect: `{rail.get('behavior_effect') or 'evaluation_only'}`",
        f"- source: `{rail.get('source') or '-'}`",
        f"- rationale: {rail.get('rationale') or '-'}",
        "",
        "## Market Inputs",
        "",
    ]
    for key in (
        "kospi_pct",
        "kosdaq_pct",
        "kospi200_pct",
        "krx_night_futures_pct",
        "breadth",
        "nasdaq_pct",
        "sp500_pct",
        "usdkrw_pct",
        "dxy_pct",
        "vix_level",
        "vix_pct",
        "global_sentiment_score",
    ):
        lines.append(f"- {key}: **{float(inputs.get(key) or 0.0):.4f}**")
    if inputs.get("krx_night_futures_status") or inputs.get("krx_night_futures_pressure"):
        lines.append(f"- krx_night_futures_status: `{inputs.get('krx_night_futures_status') or '-'}`")
        lines.append(f"- krx_night_futures_pressure: `{inputs.get('krx_night_futures_pressure') or '-'}`")
    sanity = rail.get("market_input_sanity") if isinstance(rail.get("market_input_sanity"), Mapping) else {}
    warnings = sanity.get("warnings") if isinstance(sanity.get("warnings"), list) else []
    if warnings:
        lines += ["", "## Market Input Sanity", ""]
        lines.append(f"- status: `{sanity.get('status') or 'warning'}`")
        lines.append(f"- extreme_move_requires_confirmation: `{bool(sanity.get('extreme_move_requires_confirmation'))}`")
        for row in warnings[:8]:
            if not isinstance(row, Mapping):
                continue
            lines.append(
                "- warning: "
                f"`{row.get('code')}` {row.get('index') or '-'} "
                f"change_pct={float(row.get('change_pct') or 0.0):.4f} "
                f"severity=`{row.get('severity') or '-'}`"
            )
    lines += ["", "## Expected Tactical Behavior", ""]
    for item in list(rail.get("expected_tactical_behavior") or []):
        lines.append(f"- {item}")
    lines += ["", "## Q8 Review Focus", ""]
    for item in list(rail.get("q8_review_focus") or []):
        lines.append(f"- `{item}`")
    return "\n".join(lines).rstrip() + "\n"
```

**Owner/wrapper contract:** SOURCE original `def` and signature remains, but BODY becomes one thin delegate to `market_regime_rail_review_markdown_projection.render_market_regime_rail_markdown`; add `import sys` to SOURCE if needed. `Mapping` checks → `facade.Mapping` at call time; exact original order, `.rstrip()+'\n'`, float precision, warning limit 8, no IO. Keep public signature `rail, *, day` on SOURCE. For facade items, TARGET may add a keyword-only `facade` parameter and SOURCE passes `facade=sys.modules[__name__]`; TARGET must not import SOURCE. Retain all public callers and existing imports; if target already contains earlier items, append without overwriting.

**Normal targeted fixture:** `tests/test_p15_rf035_23h_8_render_market_regime_rail_markdown_owner.py`: rail={} day='2026-10-30'→exact heading and `evaluation_only`; market_inputs.kospi_pct=1.23456→`1.2346`; fake sanity warnings + expected_tactical_behavior + q8_review_focus→same ordered bytes; numeric 'bad' raises ValueError. No policy/Guard/market execution. Record BEFORE baseline and AFTER wrapper/owner byte/value/exception parity. `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_review_markdown_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_8_render_market_regime_rail_markdown_owner.py` normal exit0 (if pytest unavailable, provide reproducible stdlib normal smoke with exact command/exit). Commit only source/owner/test, push only A, refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. On a source-blob conflict or protected effect, mark this item BLOCKED with exact SHA and continue Anext safe assigned item; on HTTPS push failure preserve local commit and continue disjoint safe item without overwriting.

## Future reserve — 6/6 VERIFIED design, **not executable in this A order**

All six were independently checked against A remote `92bde2e7c89aba6c97372d4fc56b73c70f394bc6` and the RF-035 Claude-A-exclusive file coverage. The SOURCE functions below have actual non-wrapper bodies; each TARGET was 404 on A and integration before this issue. These are **future candidates only**, not extra tasks, tests or remote implementations. After current A1–A8, C03 must revalidate source blobs, dependency/caller compatibility and target absence before promoting them to the next complete 8–10-item C02. No actor self-selection.

- **R1 RF-035** SOURCE `libs/reporting/daily_report_generator.py::_build_trade_report_integrity` blob `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf`, 75-line BODY → TARGET `libs/reporting/daily_report_generator_integrity_projection.py::_build_trade_report_integrity` (404 both). Reads only temp trade-report existence and a passed-in broker_alignment **dict**, never queries broker. Calls `_broker_closed_symbols_from_alignment`, `_find_trade_dir`, `normalize_symbol` through facade at invocation time; preserve report status/key counts and list order. Fake fixture: empty trade_index→checked 0/status ok; missing tmp reports→missing_reports; fake closed symbol with report-open row→broker_lifecycle_mismatch; no live broker/state.
- **R2 RF-035** SOURCE `libs/reporting/metrics_report_generator.py::_iter_events` blob `1f0fa8dd454ce0d32645bbe6de7a6e1f3c587954`, 20-line BODY → TARGET `libs/reporting/metrics_report_generator_read_projection.py::_iter_events` (404 both). Read-only lazy JSONL generator; `facade.json.loads` at iteration time, invalid/non-dict rows skipped. Fixture: missing tmp→[]; valid dict+JSON array+bad line→only dict; patch loads error→skip. No production event log.
- **R3 RF-035** SOURCE `libs/reporting/llm_daily_summary.py::_build_messages` blob `e847ee3941da571732364e3f2d0d5741f93ce363`, 29-line BODY → TARGET `libs/reporting/llm_daily_summary_message_projection.py::_build_messages` (404 both). Pure fake state/policy → system/user prompt list; no LLM invocation, network, order, state write. Fixture: eod_day wins over policy day; fake approvals/denials/runs appear in user content; missing values preserve exact formatting and message order. Preserve original prompt bytes; no prompt policy changes.
- **R4 RF-035** SOURCE `libs/reporting/strategist_llm_summary.py::_utc_now_iso` blob `b75edd9c2823f525556a15a6dc79b49d562b2f20`, 4-line BODY → TARGET `libs/reporting/strategist_llm_summary_clock_projection.py::_utc_now_iso` (404 both). Clock-only UTC ISO formatting, `facade.datetime`/`facade.timezone` call-time. Fixture: fake 2026-10-30T00:00:00+00:00→exact ISO string; patched clock seam. No actual clock-sensitive operational run.
- **R5 RF-035** SOURCE `libs/reporting/market_regime_rail_review.py::load_latest_macro_snapshot` blob `e6cfd5280d597602ba167ec1d3cc5fac29080a3c`, 9-line BODY → TARGET `libs/reporting/market_regime_rail_review_read_projection.py::load_latest_macro_snapshot` (404 both). Read-only path `root/day[:10]/latest.json`; preserve default root signature, `facade.json.loads`, broad exception, and return shape. Fixture: tmp root missing→available false/error; valid dict→available true/path; malformed JSON→same error. No real macro feed, policy change or Guard.
- **R6 RF-035** SOURCE `libs/reporting/strategist_llm_summary.py::render_strategist_llm_summary_markdown` blob `b75edd9c2823f525556a15a6dc79b49d562b2f20`, **active second definition at ~L583**, ~165-line BODY → TARGET `libs/reporting/strategist_llm_summary_render_projection.py::render_strategist_llm_summary_markdown` (404 both). Pure dict→Markdown text; earlier shadowed legacy definition at ~L318 is **not** a new item and must not be moved/recounted. All `_as_dict/_as_list/_text/_bullet_lines/_quality_audit_lines/_strategy_score_lines_clean/_render_stage_specific_summary_markdown_clean` and other helper calls use call-time facade; preserve exact Korean/section order and newline bytes. Fixture: empty fake payload→stable headings; fake strategy_frame/readout→exact output; is_stage_specific true→patched facade stage renderer; no files, LLM or trading effects. Before issuance, recheck duplicate-definition resolution and source/target parity.

**Reserve test status:** all tests NOT_RUN (design fixtures only). The next C03 order must inline full original bodies, wrappers, tests and push checks for selected reserves. A1–A8 above remain the only current mandatory tasks.

## Final A report

Report in Issue #11: `ORDER_ID=A-20261030-23 | CANONICAL_HEAD | C02_BLOB | A_REMOTE_BEFORE/AFTER | A1..A8 IMPLEMENTED/BLOCKED | SOURCE_BLOBS_BEFORE/AFTER | OWNER_BLOBS | TARGETED_NORMAL_COMMAND/EXIT | LOCAL_ONLY/PUSH_VERIFIED | FIRST_BLOCKER | NEXT | START_KST/END_KST` (only actual measured times). No RF DONE claim. A code/test only.
