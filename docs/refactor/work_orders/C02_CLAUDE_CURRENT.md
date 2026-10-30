# Agentra P1.5 FAST-3 — C02 A-20261030-2156 NEW 8 verified SOURCE BODY MOVEs

**C03 supply**: 2026-10-30 KST. INPUT integration HEAD `510087deb66fc2680e2044457f57d2244ca81e7d`; A remote `a9303b0d0f653ec266bf3a66c7be6738e7871586`; previous C02 blob `d39bb8e16a9bbd251d8b721385bf3fb8ee027619`. Previous A1–A8 RF-035 were **REMOTE_DONE** at A `a9303b0d0f653ec266bf3a66c7be6738e7871586` (#11 comment `6522784886`, 65 normal PASS, exact ref verified); never reassign or retest them as new work. Current new 8 SOURCE functions below have non-wrapper bodies on remote A/integration; controlled source blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9`, summary source blob `59535490fc816ebd5d336c5d3f11e70f67f76eaa`; all six new target paths were confirmed 404 on A and integration. Owner RF-035, Claude A only. Codex B owns RF-063/RF-065 and is untouched.

**Mandatory execution / safe scope:** Before EACH item fetch origin and pin remote integration SHA, C02 blob, remote A SHA and local A SHA. Work only on `work/p15-a-reporter-pure-20261021`, code and tests; never D00/C01/C02/RF/queue/STATUS/HANDOFF/C04/C05, B branch, main, live broker, real trading, Guard, Step5C, UEF, RunLab, operating logs or state. Use prepared `.venv/bin/python`/pytest; normal targeted exit0 is FAST-3 G2 (no mandatory -O/full peer/hosted CI). For each item preserve original SOURCE signature/docstring/exception/output, MOVE its actual BODY to the designated single TARGET, and replace SOURCE with a thin delegate using `facade=sys.modules[__name__]` (add `import sys` to controlled module if absent). TARGET must NOT import SOURCE; resolve listed globals through `facade` at call time to retain monkeypatch compatibility. Source original body must not remain duplicated. When TARGET has multiple items, append rather than overwrite. `from __future__ import annotations` and explicit typing imports in TARGET. SOURCE remains the only public facade; keep `__all__` and caller imports. Test baseline before move against identical fixtures, then wrapper vs owner, negative cases and patch seam. Run `py_compile` and isolated normal pytest; commit code/tests only, push normally to A, re-fetch exact remote ref and source/target/test blob after each push. On HTTPS failure preserve local commit, use approved exact-tree path only if identity proven; otherwise mark PUSH_BLOCKED and continue next non-overwriting safe item. One item blocked does not cancel others. Report real START/END, per-item normal exit, SOURCE before/after, TARGET/TEST blob, remote SHA, FIRST_BLOCKER/NEXT in #11. C04/C05 own G1/G2/G3 integration/DONE; this order is not implementation.

## A1 — RF-035 | `libs/reporting/controlled_validation_daily.py::_display_evaluation_status` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_status_projection.py::_display_evaluation_status`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _display_evaluation_status(
    *, lane_id: str, day: str, status: str, reason: str
) -> tuple[str, str]:
    """Do not present expected post-window expiry as a delivery incident."""
    if lane_id != "BTC_WOORI" or status != "INPUT_DELAY" or reason != "q12_candidate_input_stale":
        return status, reason
    try:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        session_day = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return status, reason
    if session_day < now.date() or (
        session_day == now.date() and now.time() > time(9, 12)
    ):
        return "WINDOW_CLOSED", "q12_opening_candidate_window_closed"
    return status, reason
```

**TARGET conversion / wrapper / monkeypatch:** datetime→facade.datetime; ZoneInfo→facade.ZoneInfo; time→facade.time. Keep datetime.now call inside TARGET at invocation time; never cache clock. SOURCE wrapper must keep original keyword-only signature and docstring. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade=datetime/time/ZoneInfo at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_display_status_owner.py`. fake clock 2026-10-30 09:13 Asia/Seoul; lane BTC_WOORI, day 2026-10-29, INPUT_DELAY/q12_candidate_input_stale → (WINDOW_CLOSED,q12_opening_candidate_window_closed); same day 09:10 → original tuple; other lane, invalid date → unchanged. Patch SOURCE datetime to fake and compare pre-move baseline/owner/wrapper. Isolation: No real clock-dependent production run; patch clock in isolated test. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_status_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_display_status_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A2 without overwriting.

## A2 — RF-035 | `libs/reporting/controlled_validation_daily.py::_read` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_read_projection.py::_read`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _read(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}
```

**TARGET conversion / wrapper / monkeypatch:** json.loads→facade.json.loads; json.JSONDecodeError→facade.json.JSONDecodeError; Mapping→facade.Mapping. Preserve exactly (OSError, UnicodeError, JSONDecodeError) except scope. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade.json, facade.Mapping at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_read_owner.py`. tmp_path missing file→{}; valid JSON dict {a:1}→{a:1}; list/invalid JSON→{}; monkeypatch facade.json.loads to raise JSONDecodeError and compare exception swallowing. No actual reports path. Isolation: Read-only temp files. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_read_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_read_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A3 without overwriting.

## A3 — RF-035 | `libs/reporting/controlled_validation_daily.py::_rows` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_read_projection.py::_rows`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _rows(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    return [dict(row) for row in list(payload.get(key) or []) if isinstance(row, Mapping)]
```

**TARGET conversion / wrapper / monkeypatch:** Mapping→facade.Mapping. Preserve list(payload.get(key) or []) iteration and dict(row) copies. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade.Mapping at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_rows_owner.py`. {'x':[{'a':1},4,{'b':2}]} with key x→[{'a':1},{'b':2}]; absent key→[]; mutate returned dict and verify input unchanged; monkeypatch facade.Mapping seam. Isolation: Pure projection; no IO. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_read_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_rows_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A4 without overwriting.

## A4 — RF-035 | `libs/reporting/controlled_validation_daily.py::_executor_broker_outcome` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_read_projection.py::_executor_broker_outcome`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _executor_broker_outcome(reports_root: Path, day: str, run_id: str) -> dict[str, Any]:
    """2026-09-03 daily audit (P1-B): read the actual executor artifact for
    one run_id, to distinguish "the probe reservation was claimed" (what
    `submission_count` below has always measured -- it is written by
    graphs/nodes/monitor_node.py::record_probe_submission at Monitor
    decision time, before Commander approval or execute_from_packet ever
    run) from "a broker HTTP submission was actually attempted" (only
    knowable from executor.json's own submission_attempts/broker_outcome,
    written later by graphs/nodes/execute_from_packet.py). Read-only,
    best-effort: a missing/unreadable artifact yields an empty outcome
    rather than raising."""
    if not run_id:
        return {"broker_outcome": "", "submission_attempts": 0}
    path = Path(reports_root) / "canonical" / day / run_id / "executor.json"
    payload = _read(path)
    try:
        submission_attempts = int(payload.get("submission_attempts") or 0)
    except (TypeError, ValueError):
        submission_attempts = 0
    return {
        "broker_outcome": str(payload.get("broker_outcome") or ""),
        "submission_attempts": submission_attempts,
    }
```

**TARGET conversion / wrapper / monkeypatch:** Path→facade.Path; _read→facade._read. Preserve no-run-id short circuit, int conversion catch, exact return keys. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade.Path and facade._read at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_executor_outcome_owner.py`. run_id=''→{'broker_outcome':'','submission_attempts':0}; tmp_path/canonical/2026-10-30/r1/executor.json containing {'broker_outcome':'REJECTED','submission_attempts':'2'}→REJECTED/2; invalid count→0; spy facade._read. NEVER contact broker. Isolation: Artifact read only in tmp_path; no Broker/Guard/Executor invocation. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_read_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_executor_outcome_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A5 without overwriting.

## A5 — RF-035 | `libs/reporting/controlled_validation_daily.py::build_controlled_validation_daily` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_build_projection.py::build_controlled_validation_daily`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def build_controlled_validation_daily(
    *, reports_root: Path, day: str
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    workspace_root = reports_root.parent if reports_root.name.lower() == "reports" else reports_root
    controlled_root = workspace_root / "data" / "logs" / "controlled_mock_lanes" / day
    opening_root = workspace_root / "data" / "logs" / "opening_rank1_controlled_probe" / day
    evaluations = _rows(_read(controlled_root / "lane_evaluations.json"), "evaluations")
    attempts = _rows(_read(controlled_root / "lane_attempts.json"), "attempts")
    submissions = _rows(_read(controlled_root / "lane_submissions.json"), "submissions")
    opening_evaluations = _rows(_read(opening_root / "probe_evaluations.json"), "evaluations")
    opening_submissions = _rows(_read(opening_root / "probe_submissions.json"), "submissions")

    # P1-B (additive, read-only): cross-reference each probe-reservation
    # row against its own executor.json for the ACTUAL broker outcome.
    # `submission_count` below is left completely unchanged for backward
    # compatibility -- these are new, separately-named fields only.
    broker_submission_attempted_count = 0
    broker_outcome_counts: dict[str, int] = {}
    for row in opening_submissions:
        outcome = _executor_broker_outcome(reports_root, day, str(row.get("run_id") or ""))
        if outcome["submission_attempts"] > 0:
            broker_submission_attempted_count += 1
        label = outcome["broker_outcome"] or "UNKNOWN_ARTIFACT"
        broker_outcome_counts[label] = broker_outcome_counts.get(label, 0) + 1

    lane_rows: list[dict[str, Any]] = []
    for lane_id in ("Q10_SEMICONDUCTOR", "Q10_INDEX", "BTC_WOORI"):
        lane_evaluations = [row for row in evaluations if str(row.get("lane_id") or "") == lane_id]
        latest = lane_evaluations[-1] if lane_evaluations else {}
        lane_attempts = [row for row in attempts if str(row.get("lane_id") or "") == lane_id]
        lane_submissions = [row for row in submissions if str(row.get("lane_id") or "") == lane_id]
        # 2026-09-05 Codex audit: `status` on each attempt row now honestly
        # distinguishes PRE_SUBMISSION_BLOCKED (guard blocked before any
        # broker call, Step5B NOT_SENT) from BROKER_REJECTED (an actual
        # broker-side rejection) -- see coordinator.py::_resolve_broker_outcome.
        # This additive breakdown lets a "rejected count" be read directly
        # without it silently absorbing NOT_SENT attempts.
        attempt_status_counts: dict[str, int] = {}
        for row in lane_attempts:
            label = str(row.get("status") or "") or "UNKNOWN"
            attempt_status_counts[label] = attempt_status_counts.get(label, 0) + 1
        evaluation_status, evaluation_reason = _display_evaluation_status(
            lane_id=lane_id,
            day=day,
            status=str(latest.get("status") or "NOT_EVALUATED"),
            reason=str(latest.get("reason") or ""),
        )
        lane_rows.append(
            {
                "lane_id": lane_id,
                "label": LANE_LABELS[lane_id],
                "evaluation_status": evaluation_status,
                "reason": evaluation_reason,
                "observation_count": int(latest.get("observation_count") or 0),
                "attempt_count": len(lane_attempts),
                "attempt_status_counts": attempt_status_counts,
                "submission_count": len(lane_submissions),
                "latest_submission_status": str((lane_submissions[-1] if lane_submissions else {}).get("status") or ""),
            }
        )

    return {
        "schema_version": "controlled_validation_daily.v1",
        "day": day,
        "lanes": lane_rows,
        "opening_alpha": {
            "evaluation_count": len(opening_evaluations),
            "eligible_count": sum(bool(row.get("eligible")) for row in opening_evaluations),
            "applied_count": sum(bool(row.get("applied")) for row in opening_evaluations),
            "submission_count": len(opening_submissions),
            # P1-B (2026-09-03 daily audit): `submission_count` above has
            # always meant "probe reservation claimed" (Monitor-decision-time
            # commit point), not "broker HTTP submission attempted". These
            # two fields make that distinction explicit without touching the
            # existing field's name or meaning.
            "submission_candidate_count": len(opening_submissions),
            "broker_submission_attempted_count": broker_submission_attempted_count,
            "broker_outcome_counts": broker_outcome_counts,
            "reason_counts": {
                reason: sum(1 for row in opening_evaluations if str(row.get("reason") or "") == reason)
                for reason in sorted({str(row.get("reason") or "") for row in opening_evaluations if str(row.get("reason") or "")})
            },
        },
    }
```

**TARGET conversion / wrapper / monkeypatch:** Path→facade.Path; _rows→facade._rows; _read→facade._read; _executor_broker_outcome→facade._executor_broker_outcome; _display_evaluation_status→facade._display_evaluation_status; LANE_LABELS→facade.LANE_LABELS. Preserve exact lane order, counts, broker artifact distinction, dict shape and exception behavior. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade dependencies at call time; no direct TARGET→SOURCE import. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_build_owner.py`. empty tmp_path/reports, day=2026-10-30→schema_version controlled_validation_daily.v1, lanes ordered [Q10_SEMICONDUCTOR,Q10_INDEX,BTC_WOORI], opening_alpha submission_count=0, broker_submission_attempted_count=0; fake JSON lane_attempts and opening probe_submissions + executor artifact→count/UNKNOWN_ARTIFACT parity. Use fake clock for stale BTC path. Isolation: Pure/read-only aggregation over tmp_path; no live order, guard, or state write. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_build_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_build_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A6 without overwriting.

## A6 — RF-035 | `libs/reporting/controlled_validation_daily.py::render_controlled_validation_daily_lines` SOURCE blob `26f5c7c44620bdd6197d9250a4eda654e29f34f9` → `libs/reporting/controlled_validation_daily_format_projection.py::render_controlled_validation_daily_lines`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def render_controlled_validation_daily_lines(payload: Mapping[str, Any]) -> list[str]:
    lanes = [dict(row) for row in list(payload.get("lanes") or []) if isinstance(row, Mapping)]
    opening = dict(payload.get("opening_alpha") or {})
    lines = ["", "## Controlled Validation Lanes", ""]
    for row in lanes:
        lines.append(
            f"- {row.get('label')}: `{row.get('evaluation_status')}`"
            f" / reason `{row.get('reason') or '-'}`"
            f" / attempts {int(row.get('attempt_count') or 0)}"
            f" / accepted {int(row.get('submission_count') or 0)}"
        )
    reasons = ", ".join(
        f"{key}={value}" for key, value in dict(opening.get("reason_counts") or {}).items()
    )
    lines.append(
        "- Opening Alpha: "
        f"evaluated {int(opening.get('evaluation_count') or 0)}"
        f" / eligible {int(opening.get('eligible_count') or 0)}"
        f" / applied {int(opening.get('applied_count') or 0)}"
        f" / submitted {int(opening.get('submission_count') or 0)}"
        f" / reasons {reasons or '-'}"
    )
    if "broker_submission_attempted_count" in opening:
        # P1-B (2026-09-03 daily audit, additive): clarifies that
        # "submitted" above counts probe-reservation claims (Monitor
        # decision time), not actual broker HTTP submissions.
        broker_outcomes = ", ".join(
            f"{key}={value}" for key, value in dict(opening.get("broker_outcome_counts") or {}).items()
        )
        lines.append(
            "- Opening Alpha submissions (detail): "
            f"probe_reservation_claimed {int(opening.get('submission_candidate_count') or 0)}"
            f" / broker_submission_attempted {int(opening.get('broker_submission_attempted_count') or 0)}"
            f" / broker_outcomes {broker_outcomes or '-'}"
        )
    return lines
```

**TARGET conversion / wrapper / monkeypatch:** Mapping→facade.Mapping. Preserve exact strings/order, empty initial lines, broker detail conditional and integer conversions. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade.Mapping at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_render_owner.py`. {'lanes':[],'opening_alpha':{}}→['','## Controlled Validation Lanes','','- Opening Alpha: evaluated 0 / eligible 0 / applied 0 / submitted 0 / reasons -']; with one lane + broker_submission_attempted_count=2 verify appended detail line and exact parity; malformed count raises same exception. Isolation: Pure formatting only. Run `.venv/bin/python -m py_compile libs/reporting/controlled_validation_daily.py libs/reporting/controlled_validation_daily_format_projection.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_render_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A7 without overwriting.

## A7 — RF-035 | `libs/reporting/strategist_llm_summary.py::_load_canonical_strategist` SOURCE blob `59535490fc816ebd5d336c5d3f11e70f67f76eaa` → `libs/reporting/strategist_llm_summary_canonical_loader.py::_load_canonical_strategist`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _load_canonical_strategist(source_path: Path) -> Tuple[Path | None, Dict[str, Any]]:
    canonical_path = _canonical_strategist_path_for_response(source_path)
    if canonical_path is not None and canonical_path.exists():
        try:
            raw = json.loads(canonical_path.read_text(encoding="utf-8"))
        except Exception:
            raw = {}
        if isinstance(raw, dict) and raw:
            return canonical_path, dict(raw)

    input_path = _trade_strategist_input_path_for_response(source_path)
    if input_path is None:
        return canonical_path, {}
    try:
        raw_input = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception:
        return input_path, {}
    if not isinstance(raw_input, dict):
        return input_path, {}
    source_input = _as_dict(raw_input.get("source_input"))
    if not source_input:
        return input_path, {}
    canonical = dict(source_input)
    canonical.setdefault("generated_at", raw_input.get("saved_at"))
    canonical.setdefault("run_id", raw_input.get("run_id"))
    return input_path, canonical
```

**TARGET conversion / wrapper / monkeypatch:** _canonical_strategist_path_for_response→facade._canonical_strategist_path_for_response; _trade_strategist_input_path_for_response→facade._trade_strategist_input_path_for_response; json.loads→facade.json.loads; _as_dict→facade._as_dict. Preserve fallback precedence, broad Exception, generated_at/run_id setdefault. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade path selectors/json/_as_dict at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_canonical_loader_owner.py`. fake facade path selectors returning tmp_path canonical.json/input.json; canonical {'run_id':'r'}→(canonical_path,{'run_id':'r'}); missing canonical + input {'source_input':{'x':1},'saved_at':'t','run_id':'r'}→(input_path,{'x':1,'generated_at':'t','run_id':'r'}); invalid/list input→{}; monkeypatch path selectors and json.loads. Isolation: Read-only tmp_path, never production source paths. Run `.venv/bin/python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_canonical_loader.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_canonical_loader_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to A8 without overwriting.

## A8 — RF-035 | `libs/reporting/strategist_llm_summary.py::_market_rail_from_canonical` SOURCE blob `59535490fc816ebd5d336c5d3f11e70f67f76eaa` → `libs/reporting/strategist_llm_summary_market_rail.py::_market_rail_from_canonical`

**Actual original calculation BODY to MOVE (not copy; keep only a thin SOURCE wrapper):**
```python
def _market_rail_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    global_signal = _as_dict(canonical.get("global_sentiment_signal"))
    if not global_signal:
        global_signal = _as_dict(_as_dict(canonical.get("market_context")).get("global_signal"))
    packet = {
        "generated_at": _text(canonical.get("generated_at") or canonical.get("saved_at"), ""),
        "global_sentiment": {
            "score": global_signal.get("score"),
            "status": global_signal.get("status"),
            "source": global_signal.get("source"),
        },
        "index_moves": _as_dict(global_signal.get("index_moves")),
        "korea_indices": _as_dict(global_signal.get("korea_indices")),
        "macro_moves": _as_dict(global_signal.get("macro_moves")),
    }
    return classify_market_regime_rail(packet)
```

**TARGET conversion / wrapper / monkeypatch:** _as_dict→facade._as_dict; _text→facade._text; classify_market_regime_rail→facade.classify_market_regime_rail. Do not import/execute quant runtime classifier directly from TARGET; use spy in tests. TARGET adds keyword-only `facade` and preserves all other args/defaults/return type. SOURCE keeps the exact original signature and delegates to TARGET with `facade=sys.modules[__name__]`. facade._as_dict/_text/classify_market_regime_rail at call time. No reverse import, no duplicated calculation, no eager binding. If source blob changes, inspect diff and STOP this item on conflict rather than overwrite an already moved function.

**Targeted normal test:** `tests/test_p15_rf035_2156_market_rail_owner.py`. fake facade.classify_market_regime_rail(packet) returns {'sentinel':True} and captures packet; canonical {'generated_at':'t','global_sentiment_signal':{'score':0.7,'status':'ok','index_moves':{'KOSPI':1}}}→packet generated_at=t, global_sentiment.score=.7, index_moves.KOSPI=1; fallback market_context.global_signal; compare before/after with same fake. Isolation: Pure packet construction; fake classifier only, no runtime market effect. Run `.venv/bin/python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_market_rail.py` and `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_2156_market_rail_owner.py` (normal exit0 required; if pytest unavailable, reproducible stdlib normal smoke with recorded command/exit). Commit/push only code/test, verify remote A SHA and three file blobs; if blocked preserve local commit and proceed to Aend/report without overwriting.

## Future reserve — RESERVE_NOT_VERIFIED (0/6)

The prior verified R1–R6 controlled_validation_daily candidates are NOW ASSIGNED A1–A6, so they are **not reserve**. No replacement six were independently verified at this input HEAD; do not present old reserve or previously moved helpers as available. C03 must inspect fresh RF-035 SOURCE bodies, unique TARGETs, callers and isolation before next issuance. Potential investigation only (NOT VERIFIED / NOT executable): `strategist_llm_summary.py::_utc_now_iso`, `build_strategist_llm_summary_payload`, final `render_strategist_llm_summary_markdown` and additional distinct reporting source functions; reject duplicate shadowed defs, write-effectful generate and already split wrappers. B's six RF-063 reserve candidates remain in C01 and are not A tasks.

## Final A report

For A1–A8: ORDER_BLOB, integration/A start SHA, original and new source/owner/test blob, normal targeted command/exit, remote A ref/tree equivalence, actual START_KST/END_KST, FIRST_BLOCKER/NEXT. No blanket -O/full peer/CI; no RF DONE claim.
