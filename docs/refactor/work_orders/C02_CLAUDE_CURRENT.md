# C02 — Agentra FAST-3 Claude A | ORDER A-20261031-04 | 8 NEW verified BODY MOVEs

**Remote preflight:** integration HEAD `f4b6f4ee21c3a27396ea87d1de98dcec35d3dffb`; A remote HEAD `85128e3877832afbdd7ca9179fd81419cdb026e1`. #11 comment 6530396167 A-03 reports A1–A8 REMOTE_DONE with normal targeted 45 PASS; C03 verified new Owner files and old SOURCE wrapper on A. **Do not repeat A-03.** RF-035 is Claude A's exclusive reporting Owner; B RF-063/RF-065 paths do not overlap. This C02 is the **only execution order**; do not read D00/RF/queue/C03 or select work independently.

**Safety and execution:** At start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, A_REMOTE_SHA and SOURCE blob; if an item was already moved on a newer remote SHA, mark REMOTE_DONE and continue, never duplicate. Execute **all A1–A8**, not only first PASS. Move each exact displayed computation BODY from SOURCE to TARGET; keep original signature/annotations/docstring with a thin wrapper and import Owner module, no duplicate calculation. `symbol_trade_report.py` begins with UTF-8 BOM: **preserve BOM**. Existing SOURCE imports `sys as _r3_sys`; wrapper can use `_r3_sys.modules[__name__]` to pass `facade` for call-time monkeypatch compatibility. TARGET must never import SOURCE. For pure functions facade is unnecessary; for helper/IO functions inject `facade` keyword-only, resolve helpers from facade when called (including nested generator iteration). Shared Owner files must append functions without overwriting earlier ones. Capture original output/error first and assert original-vs-Owner-vs-wrapper exact parity, negative cases and patch seams. Run `python -m py_compile` on SOURCE/TARGET and the named normal targeted test (pytest exit0 or equivalent exact stdlib smoke). Only fake dictionaries, temp dirs and controlled clock; **no live Broker/Guard/Step5C/UEF/RunLab, real account, order, production report/State/DB, network, or operational apply**. Commit only A code/new tests on `work/p15-a-reporter-pure-20261021`, normal push, re-fetch A remote HEAD and SOURCE/TARGET/TEST blobs; no force push. Push failure=LOCAL_ONLY/PUSH_BLOCKED, continue next safe item. Each item separately IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN in #11. G1/G2 are remote code/normal scoped test; C04/C05 own G3/DONE. No forced -O, full peer or per-RF CI.

## A1 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_read_json` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_read_projection.py::_read_json` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_read_projection._read_json` without a facade unless a seam requires it. facade.json.loads at call time; broad exception and dict-only result; preserve UTF-8 read and no writes. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a1_read_json_owner.py`. Inputs/expected: missing tmp JSON→{}; valid {'ok':1}→same; JSON list/malformed→{}; patch facade.json.loads to raise and verify {}. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_read_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a1_read_json_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A2**.

## A2 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_iter_jsonl` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_read_projection.py::_iter_jsonl` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    yield row

    return _gen()
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_read_projection._iter_jsonl` with keyword-only `facade=_r3_sys.modules[__name__]`. facade.json.loads at iterator advance, not construction; preserve missing→plain [] and lazy file opening; sorted order is NOT introduced. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a2_iter_jsonl_owner.py`. Inputs/expected: missing path→[]; tmp JSONL with {'a':1}, [], bad line, {'b':2} yields two dicts in file order; patch json.loads after iterator creation to confirm lazy seam. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_read_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a2_iter_jsonl_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A3**.

## A3 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_contains_any` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_text_projection.py::_contains_any` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _contains_any(text: str, needles: List[str]) -> bool:
    lowered = str(text or "").strip().lower()
    return any(needle in lowered for needle in needles)
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_text_projection._contains_any` without a facade unless a seam requires it. pure text comparison, do not normalize needles; exact original case sensitivity for needles. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a3_contains_any_owner.py`. Inputs/expected: ('AbC',['bc'])→true; ('AbC',['BC'])→false; ('',['x'])→false; no mutation. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_text_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a3_contains_any_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A4**.

## A4 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_clean_symbol_code` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_text_projection.py::_clean_symbol_code` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _clean_symbol_code(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "unknown", "none", "null", "-"}:
        return ""
    return text
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_text_projection._clean_symbol_code` without a facade unless a seam requires it. pure text cleaning; preserve original case for valid codes and leading zeros. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a4_clean_symbol_code_owner.py`. Inputs/expected: ' unknown '→''; ' 005930 '→'005930'; None→''; '-'→''. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_text_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a4_clean_symbol_code_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A5**.

## A5 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_ratio` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_scalar_projection.py::_ratio` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_scalar_projection._ratio` without a facade unless a seam requires it. pure arithmetic; do not change <=0 denominator behavior or introduce rounding. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a5_ratio_owner.py`. Inputs/expected: (4,2)→2.0; (4,0)→0.0; (4,-2)→0.0; float inputs preserve result. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_scalar_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a5_ratio_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A6**.

## A6 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_summary_input_path_for_report` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_path_projection.py::_summary_input_path_for_report` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _summary_input_path_for_report(report_path: Path) -> Path:
    return Path(report_path).with_name("ai_trade_summary_input.json")
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_path_projection._summary_input_path_for_report` with keyword-only `facade=_r3_sys.modules[__name__]`. facade.Path resolved at invocation; no filesystem mkdir/write. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a6_summary_input_path_for_report_owner.py`. Inputs/expected: Path('/tmp/a.md')→Path('/tmp/ai_trade_summary_input.json'); patched facade.Path called; no files created. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_path_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a6_summary_input_path_for_report_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A7**.

## A7 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_iter_trade_lifecycles` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_lifecycle_projection.py::_iter_trade_lifecycles` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _iter_trade_lifecycles(reports_root: Path) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    trades_root = reports_root / "trades"
    if not trades_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(trades_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = _read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(trades_root.rglob("lifecycle_bundle.json")):
            bundle = _read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = _normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_lifecycle_projection._iter_trade_lifecycles` with keyword-only `facade=_r3_sys.modules[__name__]`. facade._read_json and facade._normalize_lifecycle_bundle resolved at iterator advance; preserve sorted rglob, canonical-before-bundle, seen_trade_ids, lazy generator, missing→plain []. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a7_iter_trade_lifecycles_owner.py`. Inputs/expected: tmp reports/trades with canonical lifecycle for T1 and bundles for T1,T2: T1 once (canonical wins), T2 normalized once; missing trades root→[]; fake facade helpers verify monkeypatch after generator creation. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_lifecycle_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a7_iter_trade_lifecycles_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue A8**.

## A8 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_iter_trade_lifecycles_for_day` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_lifecycle_projection.py::_iter_trade_lifecycles_for_day` (404 on A/integration)

**Exact computation BODY to MOVE (remove from SOURCE, thin wrapper remains):**

```python
def _iter_trade_lifecycles_for_day(reports_root: Path, day: str) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    day_root = resolve_trade_day_root(reports_root, str(day or "").strip())
    if not day_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(day_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = _read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(day_root.rglob("lifecycle_bundle.json")):
            bundle = _read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = _normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()
```

**Wrapper/callers/monkeypatch:** Original name, full signature, callers, return and exception behavior remain. Wrapper delegates to `symbol_trade_lifecycle_projection._iter_trade_lifecycles_for_day` with keyword-only `facade=_r3_sys.modules[__name__]`. facade.resolve_trade_day_root at invocation and facade._read_json/_normalize_lifecycle_bundle at iteration; same sorted/dedup/lazy semantics; never access real reports. TARGET is single computation Owner; no SOURCE reverse import.

**New normal targeted test:** `tests/test_p15_rf035_04h_a8_iter_trade_lifecycles_for_day_owner.py`. Inputs/expected: fake facade.resolve_trade_day_root→tmp day root; canonical T1 and duplicate bundle T1 plus new T2→T1,T2 once; missing day→[]; verify facade seam and input day stripping. Check original/Owner/wrapper parity and exceptions; no real IO/effects. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_lifecycle_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_04h_a8_iter_trade_lifecycles_for_day_owner.py` normal exit0 (or exact stdlib smoke). Commit only code/test, push A and re-fetch remote HEAD + 3 blobs. If blocked record reason and **continue final report**.

## RESERVE_VERIFIED — 6/6 design-only, NOT executable in A-04

C03 inspected each real unmoved SOURCE body at the A remote blobs shown, checked six new TARGET paths absent on A/integration, RF-035 A exclusive and no B path overlap. All are read-only or pure under fake/temp; none has been implemented/tested. Recheck HEAD/source/target before promotion. Reserve is **not** additional work for A this run.

### R1 RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_extract_trade_artifact_snapshot` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_artifact_projection.py::_extract_trade_artifact_snapshot` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def _extract_trade_artifact_snapshot(
    *,
    report_path: Path,
    operator_brief_path: Path,
    lifecycle_bundle_path: Path,
) -> Dict[str, Any]:
    report = _read_json(report_path)
    brief = _read_json(operator_brief_path)
    bundle = _read_json(lifecycle_bundle_path)
    report_executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
    report_market = report.get("market_context_at_entry") if isinstance(report.get("market_context_at_entry"), dict) else {}
    report_entry = report.get("entry_decision") if isinstance(report.get("entry_decision"), dict) else {}
    report_final = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
    feedback = (
        bundle.get("strategist_feedback_input")
        if isinstance(bundle.get("strategist_feedback_input"), dict)
        else report.get("strategist_feedback_input")
        if isinstance(report.get("strategist_feedback_input"), dict)
        else {}
    )
    shared_facts = (
        bundle.get("shared_facts")
        if isinstance(bundle.get("shared_facts"), dict)
        else report.get("shared_facts")
        if isinstance(report.get("shared_facts"), dict)
        else {}
    )
    trade_outcome = bundle.get("trade_outcome") if isinstance(bundle.get("trade_outcome"), dict) else {}
    report_shared_facts = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
    artifact_result_pct = _pick_result_pct(
        trade_outcome.get("return_pct"),
        shared_facts.get("return_pct"),
        shared_facts.get("pnl_pct"),
        report_shared_facts.get("return_pct"),
        report_shared_facts.get("pnl_pct"),
    )
    entry_reason_text = str(report_entry.get("summary") or "").strip()
    actual_entry_reason_text = _actual_entry_reason_from_artifacts(
        report_path=Path(report_path),
        report_entry_summary=entry_reason_text,
        bundle=bundle,
        feedback=feedback,
    )
    exit_reason_text = str(shared_facts.get("exit_reason") or "").strip()
    if not exit_reason_text:
        exit_reason_text = str(report_final.get("summary") or "").strip()
    entry_pattern_type = str(feedback.get("entry_pattern_type") or "").strip() or _classify_entry_pattern(actual_entry_reason_text or entry_reason_text)
    exit_pattern_type = str(feedback.get("exit_pattern_type") or "").strip() or _classify_exit_pattern(exit_reason_text)
    clean_entry_reason = _clean_symbol_reason(actual_entry_reason_text or entry_reason_text, axis="entry")
    clean_exit_reason = _clean_symbol_reason(exit_reason_text, axis="exit")
    return {
        "report_headline": _clean_symbol_free_text(report_executive.get("headline") or report.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_executive_summary": _clean_symbol_free_text(report_executive.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_market_summary": str(report_market.get("summary") or "").strip(),
        "report_entry_summary": clean_entry_reason,
        "actual_entry_reason": clean_entry_reason,
        "report_final_conclusion": _clean_symbol_free_text(report_final.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_headline": _clean_symbol_free_text(brief.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_executive_summary": _clean_symbol_free_text(brief.get("executive_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_risk_summary": _clean_symbol_free_text(brief.get("risk_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_next_checkpoints": _list_text(brief.get("next_checkpoints"), limit=3),
        "entry_pattern_type": _clean_symbol_pattern(entry_pattern_type, axis="entry", fallback_reason=clean_entry_reason),
        "exit_pattern_type": _clean_symbol_pattern(exit_pattern_type, axis="exit", fallback_reason=clean_exit_reason),
        "thesis_invalidation_code": _clean_symbol_code(feedback.get("thesis_invalidation_code")),
        "improvement_tags": _list_text(feedback.get("improvement_tags"), limit=6),
        "review_flags": _list_text(feedback.get("review_flags"), limit=6),
        "artifact_result_pct": artifact_result_pct,
    }
```

**Seam/safety:** facade._read_json, _pick_result_pct, _actual_entry_reason_from_artifacts, _classify_entry_pattern/_classify_exit_pattern and clean helpers; read-only fake JSON paths. Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** tmp report/brief/bundle with fake return_pct 1.25, entry summary and feedback→artifact_result_pct=1.25, required fields present; missing files→empty/defaults; exact helper monkeypatch parity. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

### R2 RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_build_history_index` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_history_projection.py::_build_history_index` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def _build_history_index(reports_root: Path, symbol: str) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    normalized_symbol = str(symbol or "").strip().upper()
    for path, obj in _iter_trade_lifecycles(reports_root):
        if str(obj.get("symbol") or "").strip().upper() != normalized_symbol:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        entry = obj.get("entry") if isinstance(obj.get("entry"), dict) else {}
        exit_row = obj.get("exit") if isinstance(obj.get("exit"), dict) else {}
        artifacts = obj.get("artifacts") if isinstance(obj.get("artifacts"), dict) else {}
        trade_id = str(obj.get("trade_id") or "")
        trade_day = str(obj.get("day") or "")
        trade_root = (
            path.parent
            if path.name == "lifecycle_bundle.json"
            else path.parent.parent
        )
        expected_report_path = trade_root / "reports" / "ai_trade_report.json"
        expected_operator_brief_path = trade_root / "reports" / "operator_brief.json"
        lifecycle_bundle_path = trade_root / "lifecycle_bundle.json"
        artifact_snapshot = _extract_trade_artifact_snapshot(
            report_path=Path(str(artifacts.get("ai_trade_report_json") or expected_report_path)),
            operator_brief_path=Path(str(artifacts.get("operator_brief_json") or expected_operator_brief_path)),
            lifecycle_bundle_path=Path(str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path)),
        )
        trade_status = str(obj.get("status") or "").strip()
        if exit_row:
            last_action = "SELL"
        elif trade_status.lower() == "open":
            last_action = "HOLD"
        elif entry:
            last_action = "BUY"
        else:
            last_action = ""
        run_id = (
            str(entry.get("run_id") or "").strip()
            or str(exit_row.get("run_id") or "").strip()
            or str(obj.get("entry_strategist_run_id") or "").strip()
        )
        result_pct = _result_pct_from_lifecycle(obj)
        if result_pct is None:
            result_pct = _safe_float(artifact_snapshot.get("artifact_result_pct"))
        raw_entry_reason = str(summary.get("entry_reason_human") or "")
        artifact_entry_reason = str(artifact_snapshot.get("actual_entry_reason") or "")
        entry_reason_raw = (
            artifact_entry_reason
            if _should_prefer_artifact_entry_reason(raw_entry_reason, artifact_entry_reason)
            else raw_entry_reason
        )
        entry_reason = _clean_symbol_reason(entry_reason_raw, axis="entry")
        exit_reason = _clean_symbol_reason(summary.get("exit_reason_human"), axis="exit")
        entry_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("entry_pattern_type"),
            axis="entry",
            fallback_reason=entry_reason,
        )
        exit_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("exit_pattern_type"),
            axis="exit",
            fallback_reason=exit_reason,
        )
        history.append(
            {
                "trade_id": trade_id,
                "date": trade_day,
                "run_id": run_id,
                "status": trade_status,
                "last_status": trade_status,
                "last_action": last_action,
                "entry_reason": entry_reason,
                "exit_reason": exit_reason,
                "lifecycle_summary": _clean_lifecycle_summary(
                    trade_id=trade_id,
                    status=trade_status,
                    entry_reason=entry_reason,
                    exit_reason=exit_reason,
                ),
                "operator_conclusion": str(summary.get("operator_conclusion_human") or ""),
                "playbook": str((((entry.get("strategist_context") or {}) if isinstance(entry.get("strategist_context"), dict) else {}).get("playbook")) or ""),
                "hold_seconds": _hold_seconds_from_lifecycle(obj),
                "result_pct": result_pct,
                "trade_origin": str(obj.get("trade_origin") or ""),
                "lifecycle_completeness": str(obj.get("lifecycle_completeness") or ""),
                "evidence_recovery_used": bool(obj.get("evidence_recovery_used")),
                "report_path": str(artifacts.get("ai_trade_report_json") or expected_report_path),
                "operator_brief_path": str(artifacts.get("operator_brief_json") or expected_operator_brief_path),
                "lifecycle_bundle_path": str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path),
                "trade_root_path": str(trade_root),
                "report_headline": str(artifact_snapshot.get("report_headline") or ""),
                "report_executive_summary": str(artifact_snapshot.get("report_executive_summary") or ""),
                "report_market_summary": str(artifact_snapshot.get("report_market_summary") or ""),
                "report_entry_summary": str(artifact_snapshot.get("report_entry_summary") or entry_reason or ""),
                "report_final_conclusion": str(artifact_snapshot.get("report_final_conclusion") or ""),
                "brief_headline": str(artifact_snapshot.get("brief_headline") or ""),
                "brief_executive_summary": str(artifact_snapshot.get("brief_executive_summary") or ""),
                "brief_risk_summary": str(artifact_snapshot.get("brief_risk_summary") or ""),
                "brief_next_checkpoints": list(artifact_snapshot.get("brief_next_checkpoints") or []),
                "entry_pattern_type": entry_pattern_type,
                "exit_pattern_type": exit_pattern_type,
                "thesis_invalidation_code": _clean_symbol_code(artifact_snapshot.get("thesis_invalidation_code")),
                "improvement_tags": list(artifact_snapshot.get("improvement_tags") or []),
                "review_flags": list(artifact_snapshot.get("review_flags") or []),
            }
        )
    history.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("trade_id") or "")))
    return history
```

**Seam/safety:** facade._iter_trade_lifecycles, _extract_trade_artifact_snapshot and all clean/pct helpers at call time; read-only; preserve sorted (date,trade_id). Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** fake 2 lifecycle rows out of order for same symbol→sorted history with expected trade_id/action; different symbol filtered; no disk writes. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

### R3 RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::collect_symbols_for_day` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` → TARGET `libs/reporting/symbol_trade_symbol_projection.py::collect_symbols_for_day` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def collect_symbols_for_day(
    events_path: Path,
    reports_root: Path,
    day: str,
    trade_index: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    target_day = str(day or "").strip()
    symbols: List[str] = []
    seen: set[str] = set()

    index_rows = trade_index if trade_index is not None else build_daily_trade_index(reports_root, target_day)
    for row in index_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    for row in iter_jsonl_events(events_path, day=target_day):
        ts_day = datetime.fromtimestamp(_to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")), tz=timezone.utc).strftime("%Y-%m-%d") if _to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")) > 0 else ""
        if ts_day != target_day:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        detail = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
        for candidate in (
            detail.get("symbol"),
            payload.get("symbol"),
            order.get("symbol"),
            order.get("stk_cd"),
        ):
            symbol = str(candidate or "").strip().upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols
```

**Seam/safety:** facade.build_daily_trade_index, iter_jsonl_events, _to_epoch, datetime/timezone at call time; fake tmp log only; preserve index-first dedup and timestamp filtering. Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** fake index symbols ['005930'], fake same-day events ['000660','005930'] and other-day event→['005930','000660']; case-normalize and dedup. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

### R4 RF-035 | SOURCE `libs/reporting/report_source_helpers.py::build_policy_surface_quality_snapshot` blob `8471837632ec1c7659ba2cbcfe5ee44ec84bf42d` → TARGET `libs/reporting/report_source_policy_projection.py::build_policy_surface_quality_snapshot` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def build_policy_surface_quality_snapshot(events_path: Path, reports_root: Path, day: str) -> Dict[str, Any]:
    try:
        runtime_health = build_phase_5_2_5_3_runtime_health(
            reports_root=reports_root,
            event_log_path=events_path,
            day=day,
            limit=500,
        )
    except FileNotFoundError:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["no_canonical_monitor_runs_found"],
            },
        }
    except Exception:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["policy_surface_quality_summary_unavailable"],
            },
        }

    summary = runtime_health.get("policy_surface_quality_summary")
    if not isinstance(summary, dict):
        summary = build_policy_surface_quality_summary([])
    chart_summary = runtime_health.get("chart_structure_decision_hint_summary")
    if not isinstance(chart_summary, dict):
        chart_summary = build_chart_structure_decision_hint_summary([])
    return {
        "summary": dict(summary),
        "executive_summary": build_policy_surface_quality_executive_summary(summary),
        "chart_structure_summary": dict(chart_summary),
        "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
        "source": {
            "run_count": int(runtime_health.get("run_count") or 0),
            "date": day,
            "source": "daily_monitor_artifacts",
            "health_schema_version": str(runtime_health.get("schema_version") or ""),
        },
    }
```

**Seam/safety:** facade.build_phase_5_2_5_3_runtime_health and summary/chart helpers at call time; fake-only return values; NEVER invoke live health, Step5C or real paths. Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** stub runtime_health run_count=2 with summaries→source.run_count=2; FileNotFoundError→notes ['no_canonical_monitor_runs_found']; generic Exception→['policy_surface_quality_summary_unavailable']. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

### R5 RF-035 | SOURCE `libs/reporting/report_source_helpers.py::build_commander_route_summary` blob `8471837632ec1c7659ba2cbcfe5ee44ec84bf42d` → TARGET `libs/reporting/report_source_route_summary_projection.py::build_commander_route_summary` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def build_commander_route_summary(
    *,
    reports_root: Path,
    day: str,
    day_rows: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    canonical_dir = reports_root / "canonical" / day
    canonical_by_run: Dict[str, Dict[str, Any]] = {}
    if canonical_dir.exists():
        for run_dir in sorted(canonical_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            commander = read_json(run_dir / "commander.json")
            if not commander:
                continue
            row = _commander_route_from_payload(commander, artifact_path=str(run_dir / "commander.json"))
            if row.get("route_selected"):
                canonical_by_run[str(run_dir.name)] = row

    event_rows = day_rows or []
    event_by_run = _event_route_rows(event_rows)

    all_run_ids = set(canonical_by_run) | set(event_by_run)

    by_run: Dict[str, Dict[str, Any]] = {}
    route_selected_total: Counter[str] = Counter()
    strategy_generation_mode_total: Counter[str] = Counter()
    strategist_fallback_total = 0
    source_breakdown: Counter[str] = Counter()
    missing_count = 0

    for run_id in sorted(all_run_ids):
        selected = canonical_by_run.get(run_id)
        if not selected:
            selected = event_by_run.get(run_id)
        if not selected or not str(selected.get("route_selected") or "").strip():
            missing_count += 1
            continue
        by_run[run_id] = dict(selected)
        route_selected_total[str(selected.get("route_selected"))] += 1
        mode = str(selected.get("strategy_generation_mode") or "").strip()
        if mode:
            strategy_generation_mode_total[mode] += 1
        if bool(selected.get("strategist_fallback_used")):
            strategist_fallback_total += 1
        source_breakdown[str(selected.get("route_source") or "unknown")] += 1

    return {
        "route_source": "canonical_commander_preferred",
        "route_source_run_count": int(len(by_run)),
        "route_source_missing_count": int(missing_count),
        "route_selected_total": dict(route_selected_total),
        "strategy_generation_mode_total": dict(strategy_generation_mode_total),
        "strategist_fallback_total": int(strategist_fallback_total),
        "route_source_breakdown": dict(source_breakdown),
        "by_run": by_run,
    }
```

**Seam/safety:** facade.read_json, _commander_route_from_payload, _event_route_rows, Counter at call time; tmp canonical only; canonical preference and counters. Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** tmp canonical/day/r1/commander.json selects direct, event r1 selects fallback, event r2 selects indirect→r1 canonical wins; run_count2, route totals direct1/indirect1; no writes. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

### R6 RF-035 | SOURCE `libs/reporting/strategist_llm_summary.py::build_strategist_llm_summary_payload` blob `01e6ea1c6786a5f208d6b6afc6d12f18c8d40319` → TARGET `libs/reporting/strategist_llm_summary_payload_projection.py::build_strategist_llm_summary_payload` (404 A/integration)

**Inspected real BODY (design-only):**

```python
def build_strategist_llm_summary_payload(response_json_path: Path) -> Dict[str, Any]:
    source_path = Path(response_json_path)
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    sidecar_meta = _read_json(source_path.with_name("meta.json"))
    payload = _parse_response_body(raw)
    canonical_path, canonical = _load_canonical_strategist(source_path)
    theme_strategy = _as_dict(payload.get("theme_strategy"))
    refresh_trace = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    strategy_detail = _strategy_detail_from_sources(payload, canonical)
    stage_decision = _stage_decision_from_payload(payload, raw, sidecar_meta)
    stage_meta = _stage_meta(payload, raw, sidecar_meta)
    news_usage = _news_usage_from_canonical(canonical)
    market_regime_rail = _market_rail_from_canonical(canonical)
    news_quality = _news_quality_audit(canonical, news_usage)
    risk_off_exception_policy = _as_dict(canonical.get("risk_off_exception_policy")) or build_risk_off_exception_policy(
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
    )
    output_quality = _strategist_output_quality_audit(
        payload=payload,
        canonical=canonical,
        stage_decision=stage_decision,
        strategy_detail=strategy_detail,
        market_rail=market_regime_rail,
        news_quality=news_quality,
    )

    return {
        "schema_version": "strategist_llm_summary.v1",
        "artifact_type": "strategist_llm_summary",
        "source_response_json": str(source_path),
        "source_canonical_strategist_json": str(canonical_path) if canonical_path else "",
        "generated_at": _utc_now_iso(),
        "llm_meta": {
            "stage": _first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": _text(stage_meta.get("stage_name"), ""),
            "call_kind": _text(stage_meta.get("call_kind"), ""),
            "stage_component": _text(stage_meta.get("stage_component"), ""),
            "provider": _first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": _first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": _first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": _first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": _first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": _first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": _first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": _first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": _first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": _operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": _text(payload.get("playbook")),
            "selected_themes": _as_list(payload.get("selected_themes")),
            "theme_selection_mode": _text(theme_strategy.get("selection_mode")),
            "fallback_reason": _text(theme_strategy.get("fallback_reason"), ""),
            "rationale": _text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": _directive(payload, "playbook_action"),
            "entry_policy_action": _directive(payload, "entry_policy_action"),
            "monitor_focus_action": _directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": _directive(payload, "selected_symbol_bias_action"),
            "refresh_action": _directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": _as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": _memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": _as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": _as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": _as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": _text(refresh_trace.get("summary"), ""),
            "bullets": _as_list(refresh_trace.get("bullets")),
            "stages": _as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }
```

**Seam/safety:** facade.json.loads, _read_json, _parse_response_body, _load_canonical_strategist and all policy/render helpers at call time; fake tmp response; no LLM or network. Preserve exact-signature thin SOURCE wrapper and output/error parity if promoted. **Proposed normal targeted fake/tmp fixture:** tmp response {'stage':'strategist','status':'ok'} with mocked canonical/helpers→schema_version strategist_llm_summary.v1, artifact_type strategist_llm_summary, llm_meta.status ok; invalid JSON retains JSONDecodeError. Targeted test NOT_RUN, no code changes; on blocked promotion skip to next verified reserve.

## Required #11 report

`ORDER_ID=A-20261031-04 | CANONICAL_HEAD | ORDER_BLOB_SHA | A_START_REMOTE_SHA | A1..A8 status | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NEW_TESTS_NORMAL_EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only if measured. Do not edit docs/RF/STATUS/other branches. Reserve R1–R6 design only.
