# Agentra P1.5 FAST-3 — C02 A-20261030-20 NEW 8 verified BODY MOVEs

**C03 supply 2026-10-30 20h KST.** Previous order blob `c5d41b1ad5f71c64f1ad18168621428fe15d7659` A1–A8 are REMOTE_DONE at A HEAD `3522454025395e4d8c67a2bad42863e66e6a5b97` (#11 6520335284), verified SOURCE thin wrappers + new owners and targeted tests. Do not rerun those or earlier same-SHA PASS. This is 8 different functions, RF-035 Claude A exclusive, B read-only. Source `libs/reporting/strategist_llm_evaluation.py` A/integration blob `17345581f395401d29e02e8ed234ec9f430b0550`; new targets scalar/rows/formatting 404 on A and integration preflight.

**Execution contract (all items, not optional):** Actor=Claude A; authorized branch=`work/p15-a-reporter-pure-20261021`; canonical=`integration/p1.5`; source Git blob=`17345581f395401d29e02e8ed234ec9f430b0550`; this order blob at run start must be fetched from canonical (previous blob `c5d41b1ad5f71c64f1ad18168621428fe15d7659` is replaced). Before EACH item: `git fetch origin`, record remote canonical SHA, remote actor SHA, local HEAD, and order blob; use prepared `.venv/bin/python` and pytest when available. Work only in own code and new test files; never write D00/C01/C02/RF/queue/STATUS/HANDOFF/C04/C05, another branch, main, or live operational files. Use one isolated fake/tmp fixture, no network/order/Broker/Guard/Step5C/UEF/RunLab effects. Actual original BODY must be removed from SOURCE and moved into the single TARGET owner, leaving the original exact signature/annotations/defaults/docstring as thin delegation wrapper. Preserve call-time module monkeypatch via `facade=sys.modules[__name__]` (import `sys as _p15_sys` or `sys` already present); target never imports SOURCE, never duplicates BODY or mutates global state. Keep caller public signatures/outputs/identity/exception/order/format unchanged. Each item: pre-move golden output and error, post-move source wrapper and target equality, negative and monkeypatch fixture; `.venv/bin/python -m py_compile SOURCE TARGET`; `.venv/bin/python -m pytest -q -p no:cacheprovider EXACT_TEST` normal exit0 (stdlib normal smoke only when pytest absent), record real exit. FAST-3 G2 does not require -O/full peer/hosted CI. Commit code+targeted tests only, push actor branch normally, refetch remote ref and exact SOURCE/TARGET/TEST blob/tree after every push. HTTPS credential error blocks PUSH only: preserve local commit, approved GitHub exact-tree path only if full reviewed tree/ref equivalence proven; else LOCAL_ONLY, continue next safe non-overwriting item. No probe commits, no force push. Each blocked item is item-local; continue all remaining safe tasks. C04 integrates; C05 alone judges G1/G2/G3/RF DONE.

### A1 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_text` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L10) → `libs/reporting/strategist_llm_evaluation_scalar.py::_text`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_text` to `libs/reporting/strategist_llm_evaluation_scalar.py`; facade none; exact str(value or '')/strip and sentinel lower-case test. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_text_owner.py`: None→''; ' unknown '→''; '  BUY  '→'BUY'; numeric 0→''. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_text_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A2 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_float` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L15) → `libs/reporting/strategist_llm_evaluation_scalar.py::_float`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_float` to `libs/reporting/strategist_llm_evaluation_scalar.py`; facade none; retain broad Exception fallback float(default), do not alter nan/inf. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_float_owner.py`: '2.5'→2.5; None/default=4→4.0; 'bad'/default=3→3.0; invalid default raises ValueError. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_float_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A3 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_shape_from_reason` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L49) → `libs/reporting/strategist_llm_evaluation_rows.py::_shape_from_reason`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _shape_from_reason(reason: str, axis: str = "") -> str:
    reason = _text(reason)
    axis = _text(axis)
    if reason in {"pullback_not_mature", "pullback_below_vwap_reclaim_not_ready"} or axis == "pullback_structure":
        return "pullback"
    if reason == "below_vwap_reclaim_not_ready" or axis == "vwap_relationship":
        return "vwap_reclaim"
    if reason.startswith("breakout_") or axis == "breakout_readiness":
        return "breakout"
    if reason in {"volume_confirmation_missing", "volume_insufficient"} or axis == "volume_confirmation":
        return "volume_confirmation"
    return "other"
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_shape_from_reason` to `libs/reporting/strategist_llm_evaluation_rows.py`; facade._text at call time; no source import in target. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_shape_from_reason_owner.py`: ('breakout_late','')→'breakout'; ('','pullback_structure')→'pullback'; ('','')→'other'; monkeypatch _text spy. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_shape_from_reason_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A4 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_shape_from_tactic` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L63) → `libs/reporting/strategist_llm_evaluation_rows.py::_shape_from_tactic`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _shape_from_tactic(tactic: str) -> str:
    tactic = _text(tactic)
    if tactic in {"vwap_reclaim_pullback", "leader_vwap_reclaim_pullback", "theme_leader_pullback"}:
        return "vwap_reclaim"
    if tactic in {"opening_largecap_surge", "opening_gap_momentum"}:
        return "opening"
    if tactic in {"breakout_continuation", "opening_range_breakout"}:
        return "breakout"
    if tactic in {"lower_vwap_rebound_probe"}:
        return "lower_rebound"
    if tactic in {"defensive_observe"}:
        return "defensive"
    return tactic or "unavailable"
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_shape_from_tactic` to `libs/reporting/strategist_llm_evaluation_rows.py`; facade._text at call time; preserve original branch order. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_shape_from_tactic_owner.py`: 'opening_gap_momentum'→'opening'; 'defensive_observe'→'defensive'; ''→'unavailable'; monkeypatch _text spy. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_shape_from_tactic_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A5 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_top_counter` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L78) → `libs/reporting/strategist_llm_evaluation_rows.py::_top_counter`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _top_counter(counter: Counter[str], *, limit: int = 6) -> List[Dict[str, Any]]:
    return [{"name": name, "count": count} for name, count in counter.most_common(limit) if name]
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_top_counter` to `libs/reporting/strategist_llm_evaluation_rows.py`; Counter.most_common(limit) stable ties and name filtering; no mutation. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_top_counter_owner.py`: Counter({'x':3,'y':1})→[{'name':'x','count':3},{'name':'y','count':1}]; limit=1→x; empty→[]. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_top_counter_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A6 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_closed_rows` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L82) → `libs/reporting/strategist_llm_evaluation_rows.py::_closed_rows`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _closed_rows(rows: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if isinstance(row, Mapping) and _row_closed(row)]
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_closed_rows` to `libs/reporting/strategist_llm_evaluation_rows.py`; facade.Mapping and facade._row_closed at call time; preserve new dict copies and iterable one-pass. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_closed_rows_owner.py`: [{'status':'closed'},{'status':'open'}]→first dict only, not same object; monkeypatch _row_closed spy. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_closed_rows_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A7 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_shadow_rows` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L86) → `libs/reporting/strategist_llm_evaluation_rows.py::_shadow_rows`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _shadow_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, Mapping):
            continue
        for row in list(payload.get("candidates") or []):
            if isinstance(row, Mapping):
                out.append(dict(row))
    return out
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_shadow_rows` to `libs/reporting/strategist_llm_evaluation_rows.py`; facade.Mapping at call time; list(payload.get('candidates') or []) and copy dict exactly. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_shadow_rows_owner.py`: [{'candidates':[{'symbol':'A'},3]},None]→[{'symbol':'A'}]; identity new dict; malformed candidate ignored. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_shadow_rows_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### A8 — RF-035 | `libs/reporting/strategist_llm_evaluation.py::_format_perf` (current blob `17345581f395401d29e02e8ed234ec9f430b0550`, L159) → `libs/reporting/strategist_llm_evaluation_formatting.py::_format_perf`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _format_perf(rows: Sequence[Mapping[str, Any]], *, limit: int = 3) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = _text(row.get("name"))
        if not name:
            continue
        parts.append(
            f"{name} ({row.get('count')}, win {float(row.get('win_rate') or 0.0) * 100:.1f}%, avg {float(row.get('avg_return_pct') or 0.0):.2f}%)"
        )
    return ", ".join(parts) if parts else "none"
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_format_perf` to `libs/reporting/strategist_llm_evaluation_formatting.py`; facade._text at call time; preserve f-string precision, list slice and exception behavior. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf035_eval_format_perf_owner.py`: [{'name':'x','count':2,'win_rate':0.5,'avg_return_pct':1.25}]→'x (2, win 50.0%, avg 1.25%)'; empty/limit0→'none'. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_eval_format_perf_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.


## Verified future reserve — 6/6, not self-selected by Actor

At A `35224540`, `libs/reporting/strategist_llm_evaluation.py` blob `17345581f395401d29e02e8ed234ec9f430b0550`, six other real un-moved bodies inspected; target `strategist_llm_evaluation_extra_projection.py` absent, formatting owner absent preflight. Do NOT implement these unless future C03 C02 replaces this order. Tests listed are design hypotheses, not PASS:
- R1 RF-035 `libs/reporting/strategist_llm_evaluation.py::_bool` blob `17345581f395401d29e02e8ed234ec9f430b0550` L24 → `libs/reporting/strategist_llm_evaluation_extra_projection.py::_bool`; exact body 6 lines, bool True→True, 1→True, 'yes'→True, 'off'→False; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R2 RF-035 `libs/reporting/strategist_llm_evaluation.py::_row_closed` blob `17345581f395401d29e02e8ed234ec9f430b0550` L32 → `libs/reporting/strategist_llm_evaluation_extra_projection.py::_row_closed`; exact body 4 lines, {'status':'closed'}→True, {'action':'SELL'}→True, {}→False; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R3 RF-035 `libs/reporting/strategist_llm_evaluation.py::_result_pct` blob `17345581f395401d29e02e8ed234ec9f430b0550` L38 → `libs/reporting/strategist_llm_evaluation_extra_projection.py::_result_pct`; exact body 5 lines, {'truth_net_return_pct':'1.5'}→1.5; empty→0; facade._float seam; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R4 RF-035 `libs/reporting/strategist_llm_evaluation.py::_tactic` blob `17345581f395401d29e02e8ed234ec9f430b0550` L45 → `libs/reporting/strategist_llm_evaluation_extra_projection.py::_tactic`; exact body 2 lines, {'quant_tactic_id':'opening_gap_momentum'}→name; facade._text; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R5 RF-035 `libs/reporting/strategist_llm_evaluation.py::_quality_label` blob `17345581f395401d29e02e8ed234ec9f430b0550` L105 → `libs/reporting/strategist_llm_evaluation_extra_projection.py::_quality_label`; exact body 16 lines, []→insufficient_trade_samples; 3 negative same tactic→poor_lane_selection; facade._tactic/_result_pct/_shape_from_tactic; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R6 RF-035 `libs/reporting/strategist_llm_evaluation.py::render_strategist_llm_evaluation_lines` blob `17345581f395401d29e02e8ed234ec9f430b0550` L171 → `libs/reporting/strategist_llm_evaluation_formatting.py::render_strategist_llm_evaluation_lines`; exact body 23 lines, None→[]; {'lane_selection_quality':'aligned_lane_selection'}→header + quality line; facade._format_perf; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.

## Final A report

Issue #11: real START_KST/END_KST/ELAPSED, canonical/order/A before→after SHA, A1–A8 each MOVE/REMOTE_DONE/BLOCKED, source/owner/test blobs and targeted normal command/exit, each push remote ref/blob, FIRST_BLOCKER/NEXT. Local-only is not delivered. No RF DONE claimed by C03 supply.
