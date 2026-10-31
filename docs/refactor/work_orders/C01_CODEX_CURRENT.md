# C01 — Codex B | B-20261031-09 | FAST-3 SINGLE EXECUTION ORDER

**PRE-FLIGHT:** Canonical integration HEAD at issuance `d64fe61b777892d91e9aba6bb580f6fa63f967c5`; ORDER_FILE_BLOB_SHA is the blob of THIS file when fetched at run start; Owner branch `work/p15-b-operator-structure-20261022`. Pin all three before work. Do not read D00, RF, queue, handoffs or separate design; all executable scope is inline below. A later order does not retroactively cancel the pinned start order. This order supersedes the previous 08h 8/8 REMOTE_DONE batch; do not rerun prior tests. RF owner RF-063 exclusive, no other Actor paths. SOURCE blob must match current owner HEAD or mark STALE/BLOCKED and continue independent items; no guesswork.

**MANDATORY 8 REAL BODY MOVES:** every numbered item independently implement or provide item-specific blocker; do not stop at first PASS/commit. Move computation BODY (not copy) into specified new Owner, keep original signature/defaults/annotations/docstring as thin facade wrapper, preserve lazy generator behavior, exceptions, output ordering, caller imports and post-import monkeypatch. TARGET must NOT import SOURCE (no cycles); if global name lookup is needed, Owner accepts keyword-only `facade` and resolves globals from facade at CALL time, wrapper passes `sys.modules[__name__]` (import sys as private alias if needed). Preserve generator iteration-time lookup. Test before/after parity with fake/temp inputs; one normal exit0 scoped unittest or pytest is G2. No mandatory -O, full peer or CI. Source-only module names and existing caller public paths remain unchanged. Do not touch real accounts, Broker/Guard/Step5C/UEF, live network, production State/DB, RunLab, deploy, scheduler, frozen oracle or real orders. Read-only reporting calculations only.

## B1 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_to_epoch @ L26 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_scalar_projection.py::_to_epoch` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _to_epoch(ts: Any) -> Optional[int]:
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)

    s = str(ts).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        pass

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade.datetime/timezone. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b1_to_epoch_owner.py`; explicit input→expected: '2026-10-31T00:00:00Z' -> int(datetime(2026,10,31,tzinfo=UTC).timestamp()); '' -> None. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_scalar_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b1_to_epoch_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B2.

## B2 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_utc_day @ L51 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_scalar_projection.py::_utc_day` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _utc_day(ts: Any) -> str:
    epoch = _to_epoch(ts)
    if epoch is None:
        return date.today().isoformat()
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade._to_epoch/date/datetime/timezone; no live clock in test. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b2_utc_day_owner.py`; explicit input→expected: '2026-10-31T01:00:00Z' -> '2026-10-31'; None -> mocked facade.date.today().isoformat(). Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_scalar_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b2_utc_day_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B3.

## B3 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_to_float @ L58 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_scalar_projection.py::_to_float` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _to_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: pure. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b3_to_float_owner.py`; explicit input→expected: '3.5' -> 3.5; None and 'bad' -> None. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_scalar_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b3_to_float_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B4.

## B4 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_extract_noop_reason @ L75 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_summary_projection.py::_extract_noop_reason` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _extract_noop_reason(payload: Dict[str, Any]) -> str:
    packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
    intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
    reason = str(intent.get("reason") or "").strip()
    if reason:
        return reason
    trace = payload.get("trace") if isinstance(payload.get("trace"), dict) else {}
    raw_intent = trace.get("raw_intent") if isinstance(trace.get("raw_intent"), dict) else {}
    reason = str(raw_intent.get("reason") or "").strip()
    return reason or "unknown"
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: pure nested mapping. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b4_extract_noop_reason_owner.py`; explicit input→expected: decision_packet.intent.reason='A' -> 'A'; trace.raw_intent.reason='B' -> 'B'; {} -> 'unknown'. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_summary_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b4_extract_noop_reason_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B5.

## B5 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_build_summary @ L87 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_summary_projection.py::_build_summary` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _build_summary(rows: List[Dict[str, Any]], *, day: str) -> Dict[str, Any]:
    run_ids = {str(r.get("run_id") or "") for r in rows if str(r.get("run_id") or "").strip()}

    verdict_reason_total: Counter[str] = Counter()
    broker_code_total: Counter[str] = Counter()
    broker_failure_total: Counter[str] = Counter()
    noop_reason_total: Counter[str] = Counter()
    llm_latency_ms: List[float] = []
    llm_total = 0
    llm_ok_total = 0
    llm_error_total = 0
    execution_total = 0
    verdict_block_total = 0
    broker_success_total = 0
    broker_fail_total = 0
    broker_unknown_total = 0

    for r in rows:
        stage = str(r.get("stage") or "")
        event = str(r.get("event") or "")
        payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}

        if stage == "execute_from_packet" and event == "verdict":
            if payload.get("allowed") is False:
                verdict_block_total += 1
                reason = str(payload.get("reason") or "").strip() or "unknown"
                verdict_reason_total[reason] += 1

        if stage == "execute_from_packet" and event == "execution":
            execution_total += 1
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            bcode = str(ex_payload.get("broker_code") or "").strip()
            if bcode:
                broker_code_total[bcode] += 1
            b_ok = _broker_code_success(ex_payload.get("broker_code"))
            if b_ok is None:
                if "api_ok" in ex_payload:
                    b_ok = bool(ex_payload.get("api_ok"))
                else:
                    broker_unknown_total += 1
            if b_ok is True:
                broker_success_total += 1
            elif b_ok is False:
                broker_fail_total += 1
                k = bcode or "unknown"
                broker_failure_total[k] += 1

        if stage == "decision" and event == "trace":
            packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
            intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
            action = str(intent.get("action") or "").strip().upper()
            if action == "NOOP":
                noop_reason_total[_extract_noop_reason(payload)] += 1

        if stage == "strategist_llm" and event == "result":
            llm_total += 1
            if payload.get("ok") is True:
                llm_ok_total += 1
            else:
                llm_error_total += 1
            lat = _to_float(payload.get("latency_ms"))
            if lat is not None and lat >= 0.0:
                llm_latency_ms.append(float(lat))

    noop_total = int(sum(noop_reason_total.values()))
    noop_reason_ratio = {
        str(k): (float(v) / float(noop_total) if noop_total > 0 else 0.0)
        for k, v in noop_reason_total.items()
    }
    focus_noop_reasons = ("model_no_signal", "missing_rationale", "post_exit_cooldown")
    focus_ratio = {k: float(noop_reason_ratio.get(k, 0.0)) for k in focus_noop_reasons}

    out = {
        "schema_version": "ops_diagnostic.v1",
        "day": day,
        "events": int(len(rows)),
        "runs": int(len(run_ids)),
        "execution": {
            "execution_total": int(execution_total),
            "verdict_block_total": int(verdict_block_total),
            "verdict_reason_topN": [
                {"reason": str(reason), "count": int(cnt)}
                for reason, cnt in verdict_reason_total.most_common(10)
            ],
            "broker_success_total": int(broker_success_total),
            "broker_fail_total": int(broker_fail_total),
            "broker_unknown_total": int(broker_unknown_total),
            "broker_success_rate": (
                float(broker_success_total) / float(execution_total) if execution_total > 0 else 0.0
            ),
            "broker_code_topN": [
                {"broker_code": str(code), "count": int(cnt)}
                for code, cnt in broker_code_total.most_common(10)
            ],
            "broker_failure_topN": [
                {"broker_code": str(code), "count": int(cnt)}
                for code, cnt in broker_failure_total.most_common(10)
            ],
        },
        "noop": {
            "total": int(noop_total),
            "reason_total": {str(k): int(v) for k, v in noop_reason_total.items()},
            "reason_ratio": {str(k): float(v) for k, v in noop_reason_ratio.items()},
            "focus_reason_ratio": focus_ratio,
        },
        "strategist_llm": {
            "total": int(llm_total),
            "ok_total": int(llm_ok_total),
            "error_total": int(llm_error_total),
            "latency_ms": _numeric_summary(llm_latency_ms),
        },
    }
    return out
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade.Counter/_broker_code_success/_extract_noop_reason/_to_float/_numeric_summary; NO real broker call. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b5_build_summary_owner.py`; explicit input→expected: fake NOOP decision + strategist_llm result -> noop.total=1, strategist_llm.total=1; [] -> zero totals. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_summary_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b5_build_summary_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B6.

## B6 | RF-063 | scripts/diagnostics/generate_ops_diagnostic_report.py::_build_markdown @ L202 | SOURCE_BLOB=2e39f6482f092351276790af5f96c1530326ce8e

**TARGET exclusive new Owner:** `scripts/diagnostics/ops_diagnostic_markdown_projection.py::_build_markdown` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _build_markdown(summary: Dict[str, Any]) -> str:
    exe = summary.get("execution") if isinstance(summary.get("execution"), dict) else {}
    noop = summary.get("noop") if isinstance(summary.get("noop"), dict) else {}
    llm = summary.get("strategist_llm") if isinstance(summary.get("strategist_llm"), dict) else {}

    lines: List[str] = [
        f"# Ops Diagnostic Report ({summary.get('day')})",
        "",
        f"- schema_version: **{summary.get('schema_version')}**",
        f"- events: **{int(summary.get('events') or 0)}**",
        f"- runs: **{int(summary.get('runs') or 0)}**",
        "",
        "## Execution",
        "",
        f"- execution_total: **{int(exe.get('execution_total') or 0)}**",
        f"- verdict_block_total: **{int(exe.get('verdict_block_total') or 0)}**",
        f"- broker_success_total: **{int(exe.get('broker_success_total') or 0)}**",
        f"- broker_fail_total: **{int(exe.get('broker_fail_total') or 0)}**",
        f"- broker_unknown_total: **{int(exe.get('broker_unknown_total') or 0)}**",
        f"- broker_success_rate: **{float(exe.get('broker_success_rate') or 0.0):.2%}**",
        "",
        "### verdict_reason_topN",
        "",
    ]

    top_verdict = exe.get("verdict_reason_topN") if isinstance(exe.get("verdict_reason_topN"), list) else []
    if top_verdict:
        for row in top_verdict:
            if not isinstance(row, dict):
                continue
            lines.append(f"- {row.get('reason')}: {int(row.get('count') or 0)}")
    else:
        lines.append("- (none)")

    lines += ["", "### broker_failure_topN", ""]
    top_fail = exe.get("broker_failure_topN") if isinstance(exe.get("broker_failure_topN"), list) else []
    if top_fail:
        for row in top_fail:
            if not isinstance(row, dict):
                continue
            lines.append(f"- {row.get('broker_code')}: {int(row.get('count') or 0)}")
    else:
        lines.append("- (none)")

    lines += ["", "## NOOP", "", f"- total: **{int(noop.get('total') or 0)}**", "", "### focus_reason_ratio", ""]
    focus = noop.get("focus_reason_ratio") if isinstance(noop.get("focus_reason_ratio"), dict) else {}
    for key in ("model_no_signal", "missing_rationale", "post_exit_cooldown"):
        lines.append(f"- {key}: {float(focus.get(key) or 0.0):.2%}")

    latency = llm.get("latency_ms") if isinstance(llm.get("latency_ms"), dict) else {}
    lines += [
        "",
        "## Strategist LLM",
        "",
        f"- total: **{int(llm.get('total') or 0)}**",
        f"- ok_total: **{int(llm.get('ok_total') or 0)}**",
        f"- error_total: **{int(llm.get('error_total') or 0)}**",
        f"- latency_ms_p50: **{float(latency.get('p50') or 0.0):.1f}**",
        f"- latency_ms_p95: **{float(latency.get('p95') or 0.0):.1f}**",
        "",
    ]
    return "\n".join(lines)
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: pure deterministic formatting. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b6_build_markdown_owner.py`; explicit input→expected: {'day':'2026-10-31'} -> starts '# Ops Diagnostic Report (2026-10-31)' and contains '## Execution'. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/generate_ops_diagnostic_report.py scripts/diagnostics/ops_diagnostic_markdown_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b6_build_markdown_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B7.

## B7 | RF-063 | scripts/diagnostics/query_trade_reason_chain.py::_event_intent_id @ L29 | SOURCE_BLOB=89ff494d90d9c58ced19634cc877a7af82f60172

**TARGET exclusive new Owner:** `scripts/diagnostics/trade_reason_intent_projection.py::_event_intent_id` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _event_intent_id(payload: Dict[str, Any]) -> Optional[str]:
    packet = payload.get("decision_packet")
    packet = packet if isinstance(packet, dict) else {}
    intent = packet.get("intent")
    intent = intent if isinstance(intent, dict) else {}
    ids = {str(value).strip() for value in (
        payload.get("intent_id"), packet.get("intent_id"), intent.get("intent_id")
    ) if value is not None and str(value).strip()}
    # Conflicting IDs are not an attribution basis; empty means legacy ID-less.
    return next(iter(ids)) if len(ids) == 1 else None if ids else ""
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: pure; conflict attribution fail-closed unchanged. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b7_event_intent_id_owner.py`; explicit input→expected: matching explicit IDs -> 'A'; conflicting IDs -> None; missing -> ''. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/query_trade_reason_chain.py scripts/diagnostics/trade_reason_intent_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b7_event_intent_id_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue B8.

## B8 | RF-063 | scripts/diagnostics/query_trade_reason_chain.py::_build_rows @ L41 | SOURCE_BLOB=89ff494d90d9c58ced19634cc877a7af82f60172

**TARGET exclusive new Owner:** `scripts/diagnostics/trade_reason_rows_projection.py::_build_rows` (verified ABSENT at actor remote preflight). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _build_rows(
    events: List[Dict[str, Any]],
    *,
    run_id_filter: str = "",
    action_filter: str = "",
    only_broker_success: bool = False,
) -> List[Dict[str, Any]]:
    by_run: Dict[str, Dict[str, Any]] = {}
    out: List[Dict[str, Any]] = []
    execution_counts = Counter(str(rec.get("run_id") or "").strip() for rec in events
                               if rec.get("stage") == "execute_from_packet" and rec.get("event") == "execution")

    for rec in events:
        run_id = str(rec.get("run_id") or "").strip()
        if not run_id:
            continue
        if run_id not in by_run:
            by_run[run_id] = {}
        ctx = by_run[run_id]

        stage = str(rec.get("stage") or "").strip()
        event = str(rec.get("event") or "").strip()
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}

        if stage == "strategist_llm" and event == "result":
            intent_id = _event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("llm", {})[intent_id] = payload
            continue

        if stage == "decision" and event == "trace":
            intent_id = _event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("decision", {})[intent_id] = payload
            continue

        if stage == "execute_from_packet" and event == "verdict":
            intent_id = _event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("verdict", {})[intent_id] = payload
            continue

        if stage == "execute_from_packet" and event == "execution":
            order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            action = str(order.get("action") or "").strip().upper()
            if action not in ("BUY", "SELL"):
                continue

            if run_id_filter and run_id != run_id_filter:
                continue
            if action_filter and action != action_filter:
                continue

            broker_ok = _broker_code_success(ex_payload.get("broker_code"))
            if only_broker_success and broker_ok is not True:
                continue

            intent_id = _event_intent_id(payload)

            def context(kind: str) -> Dict[str, Any]:
                candidates = ctx.get(kind, {})
                if intent_id:
                    return candidates.get(intent_id, {})
                # Preserve legacy single-execution decision/LLM context only.
                # Verdict attribution always requires a matching explicit ID.
                if (intent_id == "" and kind != "verdict" and execution_counts[run_id] == 1
                        and set(candidates) == {""}):
                    return candidates[""]
                return {}

            llm = context("llm")
            decision = context("decision")
            decision_trace = decision.get("trace") if isinstance(decision.get("trace"), dict) else {}
            decision_packet = decision.get("decision_packet") if isinstance(decision.get("decision_packet"), dict) else {}
            decision_intent = decision_packet.get("intent") if isinstance(decision_packet.get("intent"), dict) else {}
            verdict = context("verdict")
            decision_rationale = str(decision_trace.get("rationale") or "")
            if not decision_rationale:
                decision_rationale = str(decision_intent.get("rationale") or "")
            llm_intent_rationale = str(llm.get("intent_rationale") or "")
            if not decision_rationale and llm_intent_rationale:
                decision_rationale = llm_intent_rationale

            row = {
                "ts": str(rec.get("ts") or ""),
                "run_id": run_id,
                "action": action,
                "symbol": str(order.get("symbol") or ""),
                "qty": order.get("qty"),
                "price": order.get("price"),
                "order_type": order.get("order_type"),
                "execution_reason": str(payload.get("reason") or ""),
                "allowed": payload["allowed"] if "allowed" in payload else verdict.get("allowed"),
                "verdict_reason": str(verdict.get("reason") or ""),
                "broker_code": str(ex_payload.get("broker_code") or ""),
                "broker_ok": broker_ok,
                "broker_message": str(ex_payload.get("broker_message") or ""),
                "order_id": str(ex_payload.get("order_id") or ""),
                "decision_strategy": str(decision_trace.get("strategy") or ""),
                "decision_rationale": decision_rationale,
                "decision_reason": str(decision_intent.get("reason") or ""),
                "llm_provider": str(llm.get("provider") or ""),
                "llm_model": str(llm.get("model") or ""),
                "llm_ok": llm.get("ok"),
                "llm_intent_action": str(llm.get("intent_action") or ""),
                "llm_intent_reason": str(llm.get("intent_reason") or ""),
                "llm_intent_rationale": llm_intent_rationale,
                "llm_latency_ms": llm.get("latency_ms"),
            }
            out.append(row)

    return out
```

**Wrapper/callers/monkeypatch:** Preserve original signature and imports. SOURCE delegates exactly once to Owner (for generator `_iter_days` use `yield from owner(...)`, not `return iterator`). TARGET must contain the above computation once, SOURCE no duplicate. Global/patch seam: facade.Counter/_event_intent_id/_broker_code_success; read-only event projection, NEVER broker IO. Preserve dynamic facade references and error type/message, including bad inputs. If an item has existing target on refreshed HEAD, classify REMOTE_DONE only if actual BODY moved and wrapper present; never overwrite an unrelated target.

**Targeted normal test:** new `tests/test_p15_rf063_09h_b8_build_rows_owner.py`; explicit input→expected: fake execution BUY order with run_id='r1', symbol='TEST', broker_code='0' -> one row action BUY/run_id r1; filter SELL -> []. Assert baseline-vs-Owner-vs-wrapper output and negative/error behavior, monkeypatch after import where applicable, no real IO. For generator check lazy behavior and `list(...)`. For stdout-only diagnostics use `redirect_stdout(StringIO())`. Run `python -m py_compile scripts/diagnostics/query_trade_reason_chain.py scripts/diagnostics/trade_reason_rows_projection.py` then `python -m unittest tests/test_p15_rf063_09h_b8_build_rows_owner.py -v` (normal exit 0). Commit only code/test on OWN branch and normal push; re-fetch owner HEAD, SOURCE/TARGET/test blobs. If test/permission/push blocked, record exact command, error, local vs remote state, continue Ball other safe items.

## SIX FUTURE RESERVES — VERIFIED DESIGN ONLY; NOT EXECUTABLE THIS ORDER

The following six are independent candidate BODY MOVEs, not completed code, not actor work in this pinned order. C03 checked actual SOURCE bodies, Owner RF and exclusive TARGET function absence at actor HEAD. Do NOT implement until next C03 explicitly promotes into a new order. If target collision appears, reverify before promotion.

### R1 VERIFIED | RF-063 | `scripts/diagnostics/query_m25_notification_events.py::_to_epoch` L26 blob `ec1f122a60875da5fbea743d42ddeca75bc07c7f` → `scripts/diagnostics/notification_query_time_projection.py::_to_epoch`

Actual unrelocated body:
```python
def _to_epoch(ts: Any) -> Optional[int]:
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    s = str(ts).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        pass
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None
```
Test hypothesis: '2026-10-31T00:00:00Z' -> UTC epoch; invalid -> None. Seam/safety: facade.datetime/timezone; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R2 VERIFIED | RF-063 | `scripts/diagnostics/query_m25_notification_events.py::_utc_day` L49 blob `ec1f122a60875da5fbea743d42ddeca75bc07c7f` → `scripts/diagnostics/notification_query_time_projection.py::_utc_day`

Actual unrelocated body:
```python
def _utc_day(ts: Any) -> str:
    epoch = _to_epoch(ts)
    if epoch is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```
Test hypothesis: valid UTC timestamp -> ISO day; None -> mocked clock. Seam/safety: facade._to_epoch/datetime/timezone; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R3 VERIFIED | RF-063 | `scripts/diagnostics/query_m25_notification_events.py::_env_str` L21 blob `ec1f122a60875da5fbea743d42ddeca75bc07c7f` → `scripts/diagnostics/notification_query_env_projection.py::_env_str`

Actual unrelocated body:
```python
def _env_str(name: str, default: str) -> str:
    raw = str(os.getenv(name, "") or "").strip()
    return raw if raw else str(default)
```
Test hypothesis: fake env value ' yes ' -> 'yes'; unset -> default. Seam/safety: facade.os.getenv; no production .env read; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R4 VERIFIED | RF-063 | `scripts/diagnostics/query_m25_notification_events.py::_build_parser` L60 blob `ec1f122a60875da5fbea743d42ddeca75bc07c7f` → `scripts/diagnostics/notification_query_cli_projection.py::_build_parser`

Actual unrelocated body:
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Query M25 notification event log summary.")
    p.add_argument(
        "--event-log-path",
        default=_env_str("M25_NOTIFY_EVENT_LOG_PATH", "data/logs/milestones/m25/notify_events.jsonl"),
    )
    p.add_argument("--day", default=None)
    p.add_argument("--provider", default="", help="Filter by provider (webhook/slack_webhook/none).")
    p.add_argument("--only-escalated", action="store_true", help="Only include escalated route events.")
    p.add_argument(
        "--min-portfolio-guard-alert-total",
        type=int,
        default=0,
        help="Only include events with portfolio_guard_alert_total >= N.",
    )
    p.add_argument("--json", action="store_true")
    return p
```
Test hypothesis: parse_args(['--json']) -> json=True, default log path from fake env. Seam/safety: facade.argparse/_env_str; no actual CLI run; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R5 VERIFIED | RF-063 | `scripts/diagnostics/query_strategist_llm_events.py::_print_human` L44 blob `f368e15c2783e26f3fd7dd068ff2a167a76b4339` → `scripts/diagnostics/strategist_query_render_projection.py::_print_human`

Actual unrelocated body:
```python
def _print_human(path: Path, rows: List[Dict[str, Any]]) -> None:
    print("=== Strategist LLM Events ===")
    print(f"path={path}")
    print(f"shown={len(rows)}")
    for rec in rows:
        p = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        ts = str(rec.get("ts") or "")
        run_id = str(rec.get("run_id") or "")
        call_kind = _infer_call_kind(p)
        ok = p.get("ok")
        action = str(p.get("intent_action") or "")
        reason = str(p.get("intent_reason") or "")
        latency = p.get("latency_ms")
        attempts = p.get("attempts")
        prompt_version = str(p.get("prompt_version") or "")
        schema_version = str(p.get("schema_version") or "")
        prompt_tokens = p.get("prompt_tokens")
        completion_tokens = p.get("completion_tokens")
        total_tokens = p.get("total_tokens")
        estimated_cost_usd = p.get("estimated_cost_usd")
        regime = str(p.get("context_regime") or "")
        signal_score = p.get("context_signal_score")
        sym_sent = p.get("context_symbol_sentiment_score")
        global_sent = p.get("context_global_sentiment_score")
        sym_sent_status = str(p.get("context_symbol_sentiment_status") or "")
        global_sent_status = str(p.get("context_global_sentiment_status") or "")
        composite = p.get("context_composite_score")
        err = str(p.get("error_type") or "")
        print(
            f"{ts} run_id={run_id} call_kind={call_kind} ok={ok} action={action} reason={reason} "
            f"latency_ms={latency} attempts={attempts} "
            f"prompt_version={prompt_version} schema_version={schema_version} "
            f"prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} "
            f"total_tokens={total_tokens} estimated_cost_usd={estimated_cost_usd} "
            f"context_regime={regime} context_signal_score={signal_score} "
            f"context_symbol_sentiment_score={sym_sent} context_global_sentiment_score={global_sent} "
            f"context_symbol_sentiment_status={sym_sent_status} "
            f"context_global_sentiment_status={global_sent_status} "
            f"context_composite_score={composite} "
            f"error_type={err}"
        )
```
Test hypothesis: empty rows -> header/path/shown=0; capture stdout only. Seam/safety: facade._infer_call_kind and print seam; no IO beyond redirected stdout; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

### R6 VERIFIED | RF-063 | `scripts/diagnostics/query_strategist_llm_events.py::_print_summary` L87 blob `f368e15c2783e26f3fd7dd068ff2a167a76b4339` → `scripts/diagnostics/strategist_query_render_projection.py::_print_summary`

Actual unrelocated body:
```python
def _print_summary(rows: List[Dict[str, Any]]) -> None:
    by_kind: Dict[str, Dict[str, int]] = {}
    by_reason: Dict[str, int] = {}
    by_action: Dict[str, int] = {}
    for rec in rows:
        p = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        call_kind = _infer_call_kind(p)
        ok = "ok" if bool(p.get("ok")) else "non_ok"
        by_kind.setdefault(call_kind, {})
        by_kind[call_kind][ok] = int(by_kind[call_kind].get(ok) or 0) + 1
        reason = str(p.get("intent_reason") or p.get("status") or "none")
        by_reason[reason] = int(by_reason.get(reason) or 0) + 1
        action = str(p.get("intent_action") or "none")
        by_action[action] = int(by_action.get(action) or 0) + 1

    print("summary.call_kind=", json.dumps(by_kind, ensure_ascii=False, sort_keys=True))
    print("summary.intent_action=", json.dumps(by_action, ensure_ascii=False, sort_keys=True))
    print(
        "summary.intent_reason_top=",
        json.dumps(sorted(by_reason.items(), key=lambda kv: kv[1], reverse=True)[:10], ensure_ascii=False),
    )
```
Test hypothesis: empty rows -> summary.call_kind={} etc; capture stdout only. Seam/safety: facade._infer_call_kind/json/print; no network; wrapper must preserve signature/exception/monkeypatch, normal fake/temp test and push. **RESERVE ONLY, NO EXECUTION NOW.**

## REPORT / PUSH / STOP CONDITIONS

Report to #12: `ORDER_ID=B-20261031-09 | CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | B1..B8 individual IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. Measured START_KST/END_KST/ELAPSED_MIN only, no estimates. A Git authentication failure blocks push only; continue all other safe item work. No RF/STATUS/C04/C05/D00/document/CI changes, no force-push. Actor code/test only. G1 remote code, G2 scoped normal test, G3 C04/C05 only; document publication itself is not G1/G2/G3.