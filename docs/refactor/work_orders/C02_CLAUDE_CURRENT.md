# C02 — Claude A | A-20261031-09 | FAST-3 SINGLE EXECUTION ORDER

**PRE-FLIGHT:** Canonical integration HEAD at issuance `d64fe61b777892d91e9aba6bb580f6fa63f967c5`; ORDER_FILE_BLOB_SHA is the blob of THIS file when fetched at run start; Owner branch `work/p15-a-reporter-pure-20261021`. Pin all three before work. Do not read D00, RF, queue, handoffs or separate design; all executable scope is inline below. A later order does not retroactively cancel the pinned start order. This order supersedes the previous 08h 8/8 REMOTE_DONE batch; do not rerun prior tests. RF owner RF-035 exclusive, no other Actor paths. SOURCE blob must match current owner HEAD or mark STALE/BLOCKED and continue independent items; no guesswork.

**MANDATORY 8 REAL BODY MOVES:** every numbered item independently implement or provide item-specific blocker; do not stop at first PASS/commit. Move computation BODY (not copy) into specified new Owner, keep original signature/defaults/annotations/docstring as thin facade wrapper, preserve lazy generator behavior, exceptions, output ordering, caller imports and post-import monkeypatch. TARGET must NOT import SOURCE (no cycles); if global name lookup is needed, Owner accepts keyword-only `facade` and resolves globals from facade at CALL time, wrapper passes `sys.modules[__name__]` (import sys as private alias if needed). Preserve generator iteration-time lookup. Test before/after parity with fake/temp inputs; one normal exit0 scoped unittest or pytest is G2. No mandatory -O, full peer or CI. Source-only module names and existing caller public paths remain unchanged. Do not touch real accounts, Broker/Guard/Step5C/UEF, live network, production State/DB, RunLab, deploy, scheduler, frozen oracle or real orders. Read-only reporting calculations only.

## A1 | RF-035 | libs/reporting/q8_historical_review.py::_float @ L32 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_scalar_projection.py::_float` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        text = str(value).strip().replace("%", "").replace(",", "")
        if not text:
            return None
        return float(text)
    except Exception:
        return None
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: no globals. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a1_float_owner.py`; explicit input→expected: '12.5%' -> 12.5; '' and 'bad' -> None. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a1_float_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A2.

## A2 | RF-035 | libs/reporting/q8_historical_review.py::_int @ L44 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_scalar_projection.py::_int` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(float(str(value).replace(",", "")))
    except Exception:
        return 0
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: no globals. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a2_int_owner.py`; explicit input→expected: '1,200' -> 1200; 'bad' -> 0. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a2_int_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A3.

## A3 | RF-035 | libs/reporting/q8_historical_review.py::_pct_from_ratio @ L53 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_scalar_projection.py::_pct_from_ratio` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _pct_from_ratio(value: Any) -> float | None:
    parsed = _float(value)
    if parsed is None:
        return None
    return parsed * 100.0 if abs(parsed) <= 1.0 else parsed
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade._float. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a3_pct_from_ratio_owner.py`; explicit input→expected: 0.25 -> 25.0; 15 -> 15.0; None -> None. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a3_pct_from_ratio_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A4.

## A4 | RF-035 | libs/reporting/q8_historical_review.py::_avg @ L65 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_scalar_projection.py::_avg` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: no globals. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a4_avg_owner.py`; explicit input→expected: [1,2,3] -> 2.0; [] -> 0.0. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a4_avg_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A5.

## A5 | RF-035 | libs/reporting/q8_historical_review.py::_iter_days @ L73 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_day_projection.py::_iter_days` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _iter_days(start: str, end: str) -> Iterable[str]:
    from datetime import date, timedelta

    current = date.fromisoformat(str(start)[:10])
    last = date.fromisoformat(str(end)[:10])
    while current <= last:
        yield current.isoformat()
        current += timedelta(days=1)
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: generator: wrapper MUST yield from Owner; preserve lazy date parsing and exception timing. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a5_iter_days_owner.py`; explicit input→expected: 2026-10-29..2026-10-31 -> three ISO dates in order; inverted interval -> []. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_day_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a5_iter_days_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A6.

## A6 | RF-035 | libs/reporting/q8_historical_review.py::_trade_id_from_path @ L102 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_day_projection.py::_trade_id_from_path` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _trade_id_from_path(path: Path) -> str:
    try:
        return path.parents[1].name
    except Exception:
        return ""
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: no globals. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a6_trade_id_from_path_owner.py`; explicit input→expected: Path('/tmp/T001/abc/report.json') -> 'T001'; invalid parent -> ''. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_day_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a6_trade_id_from_path_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A7.

## A7 | RF-035 | libs/reporting/q8_historical_review.py::_aggregate_return_rows @ L316 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_aggregate_projection.py::_aggregate_return_rows` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _aggregate_return_rows(rows: Sequence[Mapping[str, Any]], key: str, *, limit: int = 12) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        value = _text(row.get(key)) or "missing"
        pnl = row.get("pnl_pct")
        if isinstance(pnl, (int, float)):
            grouped[value].append(float(pnl))
    out: List[Dict[str, Any]] = []
    for name, values in grouped.items():
        if not values:
            continue
        out.append(
            {
                "name": name,
                "count": len(values),
                "win_count": sum(1 for value in values if value > 0),
                "loss_count": sum(1 for value in values if value < 0),
                "win_rate": round(sum(1 for value in values if value > 0) / len(values), 4),
                "avg_return_pct": _avg(values),
            }
        )
    out.sort(key=lambda row: (int(row["count"]), abs(float(row["avg_return_pct"]))), reverse=True)
    return out[:limit]
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade.defaultdict, facade._text, facade._avg; preserve ordering and stable sort. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a7_aggregate_return_rows_owner.py`; explicit input→expected: [{'axis':'alpha','pnl_pct':2.0},{'axis':'alpha','pnl_pct':-1.0}], key='axis' -> count2, win_rate0.5, avg_return_pct0.5; empty -> []. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_aggregate_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a7_aggregate_return_rows_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue A8.

## A8 | RF-035 | libs/reporting/q8_historical_review.py::_md_table @ L690 | SOURCE_BLOB=c96a8053ae393dc5cf0618bb774e59afa1074b37

**TARGET exclusive new Owner:** `libs/reporting/q8_historical_markdown_table_projection.py::_md_table` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> List[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(item) for item in row) + " |")
    return out
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: no globals. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf035_09h_a8_md_table_owner.py`; explicit input→expected: headers ['a','b'], rows [['x',2]] -> ['| a | b |','| --- | --- |','| x | 2 |']. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_markdown_table_projection.py` then `python -m unittest tests/test_p15_rf035_09h_a8_md_table_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue Aall other safe items.

## SIX FUTURE RESERVES — VERIFIED DESIGN ONLY; NOT EXECUTABLE THIS ORDER

The following six are independent candidate BODY MOVEs, not completed code, not actor work in this pinned order. C03 checked actual SOURCE bodies, Owner RF and exclusive TARGET function absence at actor HEAD. Do NOT implement until next C03 explicitly promotes into a new order. If target collision appears, reverify before promotion.

### R1 VERIFIED | RF-035 | `libs/reporting/q8_historical_review.py::_text` L60 blob `c96a8053ae393dc5cf0618bb774e59afa1074b37` → `libs/reporting/q8_historical_scalar_projection.py::_text`

Actual unrelocated body:
```python
def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text
```
Test hypothesis: ' unknown ' -> ''; 'valid' -> 'valid'. Seam/safety: pure; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R2 VERIFIED | RF-035 | `libs/reporting/q8_historical_review.py::_weighted_avg` L69 blob `c96a8053ae393dc5cf0618bb774e59afa1074b37` → `libs/reporting/q8_historical_scalar_projection.py::_weighted_avg`

Actual unrelocated body:
```python
def _weighted_avg(total: float, weight: int) -> float:
    return round(total / weight, 4) if weight > 0 else 0.0
```
Test hypothesis: (3,2)->1.5; weight0->0.0. Seam/safety: pure; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R3 VERIFIED | RF-035 | `libs/reporting/q8_historical_review.py::_quant_shadow_candidate_root` L83 blob `c96a8053ae393dc5cf0618bb774e59afa1074b37` → `libs/reporting/q8_historical_day_projection.py::_quant_shadow_candidate_root`

Actual unrelocated body:
```python
def _quant_shadow_candidate_root(reports_root: Path) -> Path:
    return Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"
```
Test hypothesis: Path('/tmp/reports')->Path('/tmp/data/logs/quant_shadow_candidates'); no IO. Seam/safety: pure path only; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R4 VERIFIED | RF-035 | `libs/reporting/q8_historical_review.py::_decision_for_reclaim_subtype` L259 blob `c96a8053ae393dc5cf0618bb774e59afa1074b37` → `libs/reporting/q8_historical_decision_projection.py::_decision_for_reclaim_subtype`

Actual unrelocated body:
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
Test hypothesis: observed_count=1 -> retain_observation_sample_small; read-only report classification, no promotion execution. Seam/safety: facade._text/_int/_float; no policy changes; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R5 VERIFIED | RF-035 | `libs/reporting/post_exit_shadow_recap.py::_as_dict` L93 blob `b536862b59964141ccbcc55c9e0352254176c625` → `libs/reporting/post_exit_shadow_scalar_projection.py::_as_dict`

Actual unrelocated body:
```python
def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}
```
Test hypothesis: {'x':1} -> {'x':1}; [] -> {}. Seam/safety: pure; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R6 VERIFIED | RF-035 | `libs/reporting/post_exit_shadow_recap.py::_as_list` L97 blob `b536862b59964141ccbcc55c9e0352254176c625` → `libs/reporting/post_exit_shadow_scalar_projection.py::_as_list`

Actual unrelocated body:
```python
def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []
```
Test hypothesis: [1] -> [1]; {} -> []. Seam/safety: pure; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

## REPORT / PUSH / STOP CONDITIONS

Report to #11: `ORDER_ID=A-20261031-09 | CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | A1..A8 individual IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. Measured START_KST/END_KST/ELAPSED_MIN only, no estimates. A Git authentication failure blocks push only; continue all other safe item work. No RF/STATUS/C04/C05/D00/document/CI changes, no force-push. Actor code/test only. G1 remote code, G2 scoped normal test, G3 C04/C05 only; document publication itself is not G1/G2/G3.