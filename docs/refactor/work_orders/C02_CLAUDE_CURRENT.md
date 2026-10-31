# C02 — Claude A | A-20261031-14 | FAST-3 VERIFIED EIGHT BODY MOVES

**PIN AT START:** CANONICAL_HEAD_AT_ISSUANCE=`967fce1a8288c851f1d835cb495b14e95c7e6750`; fetch live ORDER_FILE_BLOB_SHA from `integration/p1.5`; ACTOR_REMOTE_SHA_AT_DESIGN=`4efeab48c58fc08d25d6618325933625265fa2a6`; OLD_ORDER_BLOB=`d5e0099495b7faeea1b23f9425fb6becf0062af8`. Latest #11 6538883509 and C04/C05 #36 6539112357 / 6539183890 prove previous A1–A8 8/8 actual SOURCE BODY MOVEs REMOTE_DONE at actor SHA. **Do not repeat any old body, same-SHA PASS, KEEP, or previous test.** Current order is new 8 items, each independently executable. Exact actor and integration source blobs were inspected; every listed target path was 404 on actor branch and absent from integration directory listing. The six previous reserves have been promoted to executable items only in this new document; two additional source functions were inspected and verified. Current six *future* reserves are NOT VERIFIED (see bottom).

## SINGLE FILE EXECUTION CONTRACT (NO EXTERNAL DOCUMENTS)

Read only this C02 file; do NOT read D00, RF, queue, C03, handoffs, or choose work. At start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, ACTOR_REMOTE_SHA, and each SOURCE_BLOB. Actor owns RF-035 libs/reporting read-only controlled mock report projection; other actor code is forbidden. Do all eight A/B items, not only first success. If one item is blocked or source changes, record its exact reason and continue the other seven. Move **exact computation BODY** to TARGET, retaining SOURCE same-name, same-signature, defaults, annotations, public import and only a thin delegation wrapper. Never leave a second copy of BODY in SOURCE, never import SOURCE from TARGET. Use lazy import inside SOURCE wrapper if needed to preserve caller import timing. For module-global references in the original body, Owner takes keyword-only `facade` and resolves `facade.NAME` at call time, SOURCE passes `sys.modules[__name__]` or existing `_migration_sys.modules[__name__]`; preserve monkeypatch after import and recursion semantics. For pure functions, no facade needed. Preserve exceptions, stdout, key ordering, generator laziness and all callers. If a function is already moved on fresh actor HEAD, mark REMOTE_DONE and do NOT reimplement; notify C03 of depleted supply.

**Safety:** Only fake/in-memory/TemporaryDirectory tests. Absolutely no live broker/account, real orders, operating State, Guard, Step5C, UEF, RunLab, network, deployment, CI workflow, frozen oracle, force push or protected policy edits. Do not run `main` or touch live paths. Only own source, new Owner module and new targeted test paths. No RF/STATUS/queue/D00/C03/C04/C05/doc edits. Normal targeted unittest or pytest exit0 is sufficient G2; no full-peer/-O/full-CI blanket requirements. Commit own code/tests, approved non-force remote delivery, then independently re-fetch actor HEAD and exact SOURCE/TARGET/test blobs; local-only is NOT G1, failed terminal HTTPS is PUSH_BLOCKED and must not stop other safe items. C04 owns integration, C05 owns G1/G2/G3 and RF/STATUS/DONE.

## A1 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_deep_first` @ L31 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_lookup_projection.py::_deep_first` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def _deep_first(value: Any, *keys: str) -> str:
    if isinstance(value, Mapping):
        for key in keys:
            if _text(value.get(key)):
                return _text(value.get(key))
        for child in value.values():
            found = _deep_first(child, *keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _deep_first(child, *keys)
            if found:
                return found
    return ""
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `Mapping`, `_text`, recursive `_deep_first` (resolve through facade at use-time); recursion must stay in new owner, patch seam tested. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** nested in-memory dict only.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a1_deep_first_owner.py`. Input → expected: `{'outer':[{'order_id':'007'}]}`, keys=`('order_id',)` → `'007'`; missing key → `''`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_lookup_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a1_deep_first_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A2**.

## A2 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_position_strategy` @ L48 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_lookup_projection.py::_position_strategy` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def _position_strategy(state: Mapping[str, Any], symbol: str) -> dict[str, Any]:
    persisted = _mapping(state.get("persisted_state"))
    contexts = _mapping(persisted.get("position_strategy_context"))
    row = _mapping(contexts.get(symbol))
    return _mapping(row.get("output"))
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `_mapping` via facade. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** read-only fake state.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a2_position_strategy_owner.py`. Input → expected: state `{'persisted_state':{'position_strategy_context':{'A':{'output':{'controlled_mock_lane':True}}}}}` and symbol `A` → `{'controlled_mock_lane':True}`; missing symbol → `{}`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_lookup_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a2_position_strategy_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A3**.

## A3 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_ledger_row` @ L65 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_ledger_projection.py::_ledger_row` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def _ledger_row(
    *, root: Path, day: str, symbol: str, order_id: str = "", run_id: str = ""
) -> dict[str, Any]:
    path = root / "data" / "logs" / "controlled_mock_lanes" / day / "lane_submissions.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    rows = payload.get("submissions") if isinstance(payload, Mapping) else []
    symbol_matches = [
        dict(row) for row in list(rows or [])
        if isinstance(row, Mapping) and _text(row.get("symbol")) == symbol
    ]
    if order_id:
        exact = [row for row in symbol_matches if _text(row.get("order_id")).lstrip("0") == order_id.lstrip("0")]
        if exact:
            return exact[-1]
    if run_id:
        exact = [row for row in symbol_matches if _text(row.get("run_id")) == run_id]
        if exact:
            return exact[-1]
    return {}
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `Path`, `json`, `Mapping`, `_text` via facade; preserve last-match and exception catches. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** only TemporaryDirectory root; never production paths.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a3_ledger_row_owner.py`. Input → expected: tmp root `/data/logs/controlled_mock_lanes/2026-10-31/lane_submissions.json` with `{'submissions':[{'symbol':'A','order_id':'0012'}]}`; `order_id='12'` → matching row; invalid JSON → `{}`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_ledger_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a3_ledger_row_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A4**.

## A4 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::build_controlled_lane_report_surface` @ L89 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_surface_build_projection.py::build_controlled_lane_report_surface` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def build_controlled_lane_report_surface(
    state: Mapping[str, Any], *, day: str = "", root: Path | str | None = None,
    prior_entry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Recover controlled-lane entry evidence without same-symbol guessing."""
    execution = _mapping(state.get("execution"))
    order = _mapping(execution.get("order"))
    meta = _mapping(order.get("meta"))
    prior = _mapping(prior_entry)
    lane = _first_mapping(meta.get("controlled_mock_lane"), prior.get("controlled_mock_lane"))
    symbol = _text(order.get("symbol") or execution.get("symbol") or prior.get("symbol") or state.get("symbol"))
    strategy = _first_mapping(meta.get("position_strategy_snapshot"), prior.get("position_strategy_snapshot"))
    if not strategy and symbol:
        strategy = _position_strategy(state, symbol)
    if not lane and day and root is not None and symbol:
        order_id = _deep_first(prior, "order_id", "ord_no")
        entry_run_id = _text(prior.get("run_id"))
        lane = _ledger_row(root=Path(root), day=day, symbol=symbol, order_id=order_id, run_id=entry_run_id)
        if lane and not strategy:
            strategy = _fixed_lane_strategy()
    if not lane or not strategy.get("controlled_mock_lane"):
        return {}
    lane_id = _text(lane.get("lane_id"))
    return {
        "schema_version": "controlled_mock_lane_report.v2",
        "lane_id": lane_id,
        "lane_label": LANE_LABELS.get(lane_id, lane_id),
        "symbol": _text(lane.get("symbol") or symbol),
        "signal_id": _text(lane.get("signal_id")),
        "signal_epoch": lane.get("signal_epoch"),
        "entry_run_id": _text(lane.get("run_id") or prior.get("run_id")),
        "entry_order_id": _text(lane.get("order_id") or _deep_first(prior, "order_id", "ord_no")),
        "score": lane.get("score"),
        "evidence": _mapping(lane.get("evidence")),
        "daily_limit": lane.get("daily_limit"),
        "reservation": _mapping(lane.get("reservation")),
        "strategy_horizon": _text(strategy.get("strategy_horizon")),
        "expected_hold_window": _mapping(strategy.get("expected_hold_window")),
        "llm_used": bool(strategy.get("llm_used")),
        "stage3_horizon_review_allowed": bool(strategy.get("horizon_revision_allowed", True)),
        "selection_authority": "deterministic_independent_lane",
        "scanner_rank_applicable": False,
        "execution_scope": "kiwoom_mock_only",
    }
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `_mapping`, `_text`, `_first_mapping`, `_position_strategy`, `_deep_first`, `_ledger_row`, `_fixed_lane_strategy`, `Path`, `LANE_LABELS` through call-time facade; retain public export. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** read-only fake state, root=None or temp fixture; no broker or live.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a4_build_controlled_lane_report_surface_owner.py`. Input → expected: fake state `execution.order.meta.controlled_mock_lane={'lane_id':'L','symbol':'A'}` and `position_strategy_snapshot={'controlled_mock_lane':True}` → `schema_version='controlled_mock_lane_report.v2'`, `execution_scope='kiwoom_mock_only'`; no lane → `{}`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_surface_build_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a4_build_controlled_lane_report_surface_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A5**.

## A5 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::controlled_lane_surface_from_report` @ L135 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_surface_read_projection.py::controlled_lane_surface_from_report` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def controlled_lane_surface_from_report(report: Mapping[str, Any]) -> dict[str, Any]:
    fact_payload = _mapping(report.get("fact_payload"))
    trade = _mapping(fact_payload.get("trade"))
    lifecycle = _first_mapping(report.get("trade_lifecycle"), report.get("lifecycle"), trade.get("trade_lifecycle"), trade.get("lifecycle"))
    entry = _mapping(lifecycle.get("entry"))
    lifecycle_bundle = _first_mapping(report.get("lifecycle_bundle"), trade.get("lifecycle_bundle"))
    bundle_entry = _mapping(_mapping(lifecycle_bundle.get("lifecycle")).get("entry"))
    return _first_mapping(
        report.get("controlled_mock_lane"), trade.get("controlled_mock_lane"),
        lifecycle_bundle.get("controlled_mock_lane"), entry.get("controlled_mock_lane"),
        bundle_entry.get("controlled_mock_lane"),
    )
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `_mapping`, `_first_mapping` through facade; retain lookup precedence. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** in-memory report only.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a5_controlled_lane_surface_from_report_owner.py`. Input → expected: `{'fact_payload':{'trade':{'controlled_mock_lane':{'lane_id':'L'}}}}` → `{'lane_id':'L'}`; missing → `{}`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_surface_read_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a5_controlled_lane_surface_from_report_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A6**.

## A6 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::render_controlled_lane_report_lines` @ L238 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_markdown_projection.py::render_controlled_lane_report_lines` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def render_controlled_lane_report_lines(report: Mapping[str, Any]) -> list[str]:
    surface = controlled_lane_surface_from_report(report)
    if not surface:
        return []
    evidence = _mapping(surface.get("evidence"))
    window = _mapping(surface.get("expected_hold_window"))
    lines = [
        f"* 실행 레인: **{_text(surface.get('lane_label')) or _text(surface.get('lane_id'))}**",
        f"* 신호 ID: `{_text(surface.get('signal_id')) or '-'}`",
        f"* 선택 권한: {_text(surface.get('selection_authority')) or 'deterministic_independent_lane'}",
        f"* Scanner 순위: {'해당 없음' if surface.get('scanner_rank_applicable') is False else '적용'}",
        f"* LLM 사용: {'예' if surface.get('llm_used') else '아니오'}",
    ]
    if surface.get("score") not in (None, ""):
        lines.append(f"* 신호 점수: {surface.get('score')}")
    if evidence:
        evidence_text = " / ".join(f"{key}={value}" for key, value in evidence.items() if value not in (None, "", [], {}))
        if evidence_text:
            lines.append(f"* 고정 가설 근거: {evidence_text}")
    if window:
        lines.append("* 고정 보유 구간: " f"최소 {window.get('min_sec', '-')}초 / 목표 {window.get('target_sec', '-')}초 / 최대 {window.get('max_sec', '-')}초")
    if surface.get("stage3_horizon_review_allowed"):
        lines.append("* R3 연결: 허용. 3차 전략가의 보유기간 재검토를 적용할 수 있습니다.")
    else:
        lines.append("* R3 연결: 차단. 독립 레인과 고정 horizon 비교를 위해 3차 전략가가 보유기간을 변경하지 않습니다.")
    lines.append("* 주문 범위: 키움 모의투자 검증 전용")
    return lines
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `controlled_lane_surface_from_report`, `_mapping`, `_text` via facade; exact Korean text and ordering. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** in-memory markdown only.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a6_render_controlled_lane_report_lines_owner.py`. Input → expected: `{'controlled_mock_lane':{'lane_id':'L','expected_hold_window':{'min_sec':300,'target_sec':1800,'max_sec':14400}}}` → lines include `키움 모의투자 검증 전용` and `L`; absent surface → `[]`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_markdown_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a6_render_controlled_lane_report_lines_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A7**.

## A7 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_mapping` @ L15 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_scalar_projection.py::_mapping` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `Mapping` resolved from facade at call-time; preserve copy semantics. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** pure fake mapping.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a7_mapping_owner.py`. Input → expected: `{'a':1}` → equal new dict; `None` → `{}`; returned dict is distinct object. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a7_mapping_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue A8**.

## A8 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_first_mapping` @ L23 | SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`

**TARGET:** `libs/reporting/controlled_lane_scalar_projection.py::_first_mapping` — NEW exclusive A Owner, verified ABSENT (404) at actor HEAD. **EXACT ORIGINAL BODY TO MOVE:**

```python
def _first_mapping(*values: Any) -> dict[str, Any]:
    for value in values:
        row = _mapping(value)
        if row:
            return row
    return {}
```

**Wrapper/callers/monkeypatch:** SOURCE retains original signature and only delegates; `_mapping` via facade; preserve first nonempty and copy semantics. Keep original imports and caller entrypoints; test wrapper, Owner, and pre-move baseline equality for normal, negative, exceptions, ordering and post-import monkeypatch. Do not alter unrelated callers or tests. **Isolation:** pure fake mappings.

**Targeted normal test (new, not yet run):** `tests/test_p15_rf035_14h_a8_first_mapping_owner.py`. Input → expected: `({}, {'a':1}, {'b':2})` → `{'a':1}`; `(None, [])` → `{}`. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_scalar_projection.py` then `python -m unittest tests/test_p15_rf035_14h_a8_first_mapping_owner.py -v` (or equivalent exact-scope pytest); require actual normal exit0, never fabricate PASS. Commit/push only actor code+test, refetch SHA/blob. If blocked, report precise blocker and **continue report and handoff**.

## FUTURE RESERVE QUEUE — 0/6 VERIFIED, RESERVE_NOT_VERIFIED

All six earlier VERIFIED reserve items were promoted to current A1–A6. **No additional future item is VERIFIED**: do not execute these suggestions, do not count as safe backlog, and do not assign target paths without C03 direct source/target/owner/test verification. C03 next cycle must validate six new functions or record SUPPLY_GAP; the following are investigation leads, not assignments:

- R1 RESERVE_NOT_VERIFIED: controlled_mock_lane_report.py::_text — tiny helper, target/consumer not rechecked
- R2 RESERVE_NOT_VERIFIED: controlled_mock_lane_report.py::_fixed_lane_strategy — mock strategy data, policy scope needs review
- R3 RESERVE_NOT_VERIFIED: controlled_mock_lane_report.py::attach_controlled_lane_report_surface — report mutation seam needs review
- R4 RESERVE_NOT_VERIFIED: controlled_mock_lane_report.py::apply_controlled_lane_story_surface — output mutation and downstream effects need review
- R5 RESERVE_NOT_VERIFIED: q8_shadow_blocker_review.py::_dedupe_rows — target/caller not checked
- R6 RESERVE_NOT_VERIFIED: q8_shadow_blocker_review.py::render_q8_shadow_blocker_review_markdown — markdown parity and target not checked

## REPORT / PUSH / CONTINUITY

Report to #11: `ORDER_ID=A-20261031-14 | CANONICAL_HEAD | ORDER_BLOB_SHA | ACTOR_REMOTE_BEFORE/AFTER | A1..A8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times only when measured. If any of eight blocked, continue all remaining safe tasks; no NO_DELTA if current safe work remains. G1/G2 actor source evidence is distinct from C04 G3 and C05 RF_DONE. RUN_SOURCE_SHA UNKNOWN/RunLab exit255 remains separate SAFETY_HOLD; no runtime changes.
