# C01 — Codex B | B-20261031-13 | FAST-3 CONTINUATION — SIX VERIFIED REMAINING BODY MOVES

**PIN AT START:** integration/p1.5 HEAD at issuance `bd46731caf6d4950af3457694d689e0bbb0f784b`; ORDER_FILE_BLOB_SHA=fetch this document from `integration/p1.5`; B actor remote HEAD at design `10a234f02c87f0210e5c50b4e039f7d6907e7aa4`. Previous B-20261031-10 order blob `fa87f666b9ef9769b815d3d200f8ebfba20150e3` was 2/8 REMOTE_DONE and 6/8 still unimplemented remotely. #12 comment 6538201693 reports B5/B6 `_print_human`/`_print_summary` moved to `scripts/diagnostics/strategist_query_render_projection.py` and normal unittest 2 exit0; remote B source blob `ca96ad4782c7557c66c21d808a829c925655f39d`, Owner blob `2c786e7a3d0cac485b645d354ae299fea84cac84` verified. **B5/B6 are REMOTE_DONE, NOT executable and NOT to be repeated.** Their old SOURCE_BLOB `f368e15c` is stale and deliberately removed from this order.

**SIX EXECUTABLE REMAINING ITEMS ONLY:** B1–B4 and B7–B8 below are RF-063 B-exclusive diagnostics calculation BODY moves. Actual original source still present: `query_m25_notification_events.py` SOURCE_BLOB `ec1f122a60875da5fbea743d42ddeca75bc07c7f`, `query_commander_resilience_events.py` SOURCE_BLOB `caebd5b1466a7f408a70be98ee94b89d5cda5e01`. Their three target modules `notification_query_time_projection.py`, `notification_query_env_projection.py`, `notification_query_cli_projection.py` and `commander_resilience_query_projection.py` were rechecked 404 at B HEAD. Six independent safe moves remain, so D00 replacement threshold (<6) is NOT met. The prior LOCAL_ONLY B1–B4/B7–B8 bytes were pruned and do not count as remote completion; reimplement from exact pinned bodies below, not stale local commit. All six must be executed or individually evidence-BLOCKED; do not stop at first PASS, partial commit or push error.

**Single execution contract:** Do NOT read D00, RF, queue, C03 or handoffs, and do not independently select work. At start pin CANONICAL_HEAD/ORDER_FILE_BLOB_SHA/OWNER_REMOTE_SHA. Move real BODY to target once, SOURCE keeps same-signature thin wrapper, caller and use-time monkeypatch seam, exception/output/generator behavior; no reverse target→source import. Normal targeted unittest/pytest exit0 once per changed scope suffices G2; no mandatory -O/full peer/hosted CI. Actor modifies/pushes own code/tests only; no docs/RF/STATUS/queue. Fake/temp only, no live network, Broker/Guard/Step5C/UEF, operating State, RunLab, frozen oracle, deployment or force push. If terminal push blocked, continue all safe items and preserve exact-tree evidence; LOCAL_ONLY is not G1. C04 integrates, C05 judges G1/G2/G3/DONE.

## B1 | RF-063 | scripts/diagnostics/query_m25_notification_events.py::_to_epoch @ L26 | SOURCE_BLOB=ec1f122a60875da5fbea743d42ddeca75bc07c7f

**TARGET:** `scripts/diagnostics/notification_query_time_projection.py::_to_epoch` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade.datetime/timezone. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b1_to_epoch_owner.py`, explicit input→expected: '2026-10-31T00:00:00Z'->UTC epoch; ''->None. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_m25_notification_events.py scripts/diagnostics/notification_query_time_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b1_to_epoch_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## B2 | RF-063 | scripts/diagnostics/query_m25_notification_events.py::_utc_day @ L49 | SOURCE_BLOB=ec1f122a60875da5fbea743d42ddeca75bc07c7f

**TARGET:** `scripts/diagnostics/notification_query_time_projection.py::_utc_day` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _utc_day(ts: Any) -> str:
    epoch = _to_epoch(ts)
    if epoch is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade._to_epoch/datetime/timezone; freeze clock. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b2_utc_day_owner.py`, explicit input→expected: '2026-10-31T01:00:00Z'->'2026-10-31'; None->mocked UTC date. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_m25_notification_events.py scripts/diagnostics/notification_query_time_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b2_utc_day_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## B3 | RF-063 | scripts/diagnostics/query_m25_notification_events.py::_env_str @ L21 | SOURCE_BLOB=ec1f122a60875da5fbea743d42ddeca75bc07c7f

**TARGET:** `scripts/diagnostics/notification_query_env_projection.py::_env_str` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _env_str(name: str, default: str) -> str:
    raw = str(os.getenv(name, "") or "").strip()
    return raw if raw else str(default)
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade.os; mock getenv, no .env. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b3_env_str_owner.py`, explicit input→expected: fake env ' yes '->'yes'; missing->default. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_m25_notification_events.py scripts/diagnostics/notification_query_env_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b3_env_str_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## B4 | RF-063 | scripts/diagnostics/query_m25_notification_events.py::_build_parser @ L60 | SOURCE_BLOB=ec1f122a60875da5fbea743d42ddeca75bc07c7f

**TARGET:** `scripts/diagnostics/notification_query_cli_projection.py::_build_parser` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

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

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade.argparse/_env_str; parse only. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b4_build_parser_owner.py`, explicit input→expected: parse_args(['--json']).json is True; fake env default. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_m25_notification_events.py scripts/diagnostics/notification_query_cli_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b4_build_parser_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## B7 | RF-063 | scripts/diagnostics/query_commander_resilience_events.py::_is_incident_event @ L24 | SOURCE_BLOB=caebd5b1466a7f408a70be98ee94b89d5cda5e01

**TARGET:** `scripts/diagnostics/commander_resilience_query_projection.py::_is_incident_event` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _is_incident_event(rec: Dict[str, Any]) -> bool:
    event = str(rec.get("event") or "")
    payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
    if event == "error":
        return True
    if event == "transition" and str(payload.get("transition") or "") == "cooldown":
        return True
    if event == "resilience":
        reason = str(payload.get("reason") or "")
        if reason in ("cooldown_active", "incident_threshold_cooldown"):
            return True
    return False
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure read-only event label. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b7_is_incident_event_owner.py`, explicit input→expected: {'event':'error'}->True; {'event':'route'}->False. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_commander_resilience_events.py scripts/diagnostics/commander_resilience_query_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b7_is_incident_event_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## B8 | RF-063 | scripts/diagnostics/query_commander_resilience_events.py::_filtered_events @ L38 | SOURCE_BLOB=caebd5b1466a7f408a70be98ee94b89d5cda5e01

**TARGET:** `scripts/diagnostics/commander_resilience_query_projection.py::_filtered_events` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _filtered_events(
    rows: List[Dict[str, Any]],
    *,
    run_id: str = "",
    only_incidents: bool = False,
    include_route: bool = False,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for rec in rows:
        if rec.get("stage") != "commander_router":
            continue
        event = str(rec.get("event") or "")
        if event == "route" and not include_route:
            continue
        if run_id and str(rec.get("run_id") or "") != run_id:
            continue
        if only_incidents and not _is_incident_event(rec):
            continue
        out.append(rec)
    return out
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. facade._is_incident_event; stable order. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Mandatory normal targeted test:** `tests/test_p15_rf063_10h_b8_filtered_events_owner.py`, explicit input→expected: commander_router/error and other/error -> one commander_router/error. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Run `python -m py_compile scripts/diagnostics/query_commander_resilience_events.py scripts/diagnostics/commander_resilience_query_projection.py` then `python -m unittest tests/test_p15_rf063_10h_b8_filtered_events_owner.py -v` normal exit0. Commit ONLY own code/test, push normally, re-fetch remote SOURCE/TARGET/test blobs. If blocked, record exact error and continue all other safe items.

## SIX VERIFIED FUTURE RESERVES — NOT EXECUTABLE THIS ORDER

Revalidated at B remote `10a234f02c87f0210e5c50b4e039f7d6907e7aa4`: commander source blob `caebd5b1466a7f408a70be98ee94b89d5cda5e01`, incident timeline source blob `c47b817cef0c29957d010c105487594ae5a874c6`; all six named reserve target modules still absent (404). These remain design-only and cannot replace an executable item without a new C03 order.

All six have actual SOURCE BODY and exclusive absent TARGET verified at Actor HEAD; no reserve is code implementation or test PASS. Promote only by a future new C03 order.

### R1 VERIFIED | RF-063 | scripts/diagnostics/query_commander_resilience_events.py::_summary @ L60 | SOURCE_BLOB=caebd5b1466a7f408a70be98ee94b89d5cda5e01

**TARGET:** `scripts/diagnostics/commander_resilience_summary_projection.py::_summary` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _summary(rows: List[Dict[str, Any]], *, total_matched: int) -> Dict[str, Any]:
    event_total: Dict[str, int] = {}
    cooldown_transitions = 0
    intervention_total = 0
    error_total = 0
    latest_status = ""
    latest_run_id = ""

    for rec in rows:
        event = str(rec.get("event") or "")
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        event_total[event] = int(event_total.get(event, 0)) + 1

        is_cooldown_transition = (
            event == "transition"
            and (
                str(payload.get("transition") or "") == "cooldown"
                or str(payload.get("reason") or "") == "cooldown_active"
            )
        )
        is_cooldown_resilience = (
            event == "resilience"
            and str(payload.get("reason") or "") == "incident_threshold_cooldown"
        )
        if is_cooldown_transition or is_cooldown_resilience:
            cooldown_transitions += 1
        if event == "intervention":
            intervention_total += 1
        if event == "error":
            error_total += 1

        status = str(payload.get("status") or "")
        if status:
            latest_status = status
        latest_run_id = str(rec.get("run_id") or latest_run_id)

    return {
        "total_matched": int(total_matched),
        "shown": int(len(rows)),
        "event_total": event_total,
        "cooldown_transition_total": int(cooldown_transitions),
        "intervention_total": int(intervention_total),
        "error_total": int(error_total),
        "latest_status": latest_status,
        "latest_run_id": latest_run_id,
    }
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure read-only counters. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b1_summary_owner.py`, explicit input→expected: [error] total_matched=1 -> error_total=1, shown=1. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R2 VERIFIED | RF-063 | scripts/diagnostics/query_commander_resilience_events.py::_print_human @ L108 | SOURCE_BLOB=caebd5b1466a7f408a70be98ee94b89d5cda5e01

**TARGET:** `scripts/diagnostics/commander_resilience_render_projection.py::_print_human` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _print_human(path: Path, rows: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    print("=== Commander Resilience Events ===")
    print(f"path={path}")
    print(f"total_matched={summary.get('total_matched')} shown={summary.get('shown')}")
    print(
        f"cooldown_transition_total={summary.get('cooldown_transition_total')} "
        f"intervention_total={summary.get('intervention_total')} "
        f"error_total={summary.get('error_total')}"
    )
    print(f"latest_run_id={summary.get('latest_run_id')} latest_status={summary.get('latest_status')}")
    for rec in rows:
        ts = str(rec.get("ts") or "")
        run_id = str(rec.get("run_id") or "")
        event = str(rec.get("event") or "")
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        key = ""
        if event == "transition":
            key = (
                f"transition={payload.get('transition')} status={payload.get('status')} "
                f"reason={payload.get('reason')} cooldown_until_epoch={payload.get('cooldown_until_epoch')}"
            )
        elif event == "resilience":
            key = (
                f"reason={payload.get('reason')} incident_count={payload.get('incident_count')} "
                f"incident_threshold={payload.get('incident_threshold')} "
                f"cooldown_until_epoch={payload.get('cooldown_until_epoch')}"
            )
        elif event == "intervention":
            key = f"type={payload.get('type')} at_epoch={payload.get('at_epoch')}"
        elif event == "error":
            key = f"error_type={payload.get('error_type')} error={payload.get('error')}"
        elif event == "end":
            key = f"status={payload.get('status')} path={payload.get('path')}"
        elif event == "route":
            key = f"mode={payload.get('mode')}"
        print(f"{ts} run_id={run_id} event={event} {key}".strip())
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. redirect stdout only. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b2_print_human_owner.py`, explicit input→expected: empty rows stdout header and totals. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R3 VERIFIED | RF-063 | scripts/diagnostics/reconstruct_incident_timeline.py::_incident_trigger @ L57 | SOURCE_BLOB=c47b817cef0c29957d010c105487594ae5a874c6

**TARGET:** `scripts/diagnostics/incident_timeline_trigger_projection.py::_incident_trigger` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _incident_trigger(row: Dict[str, Any]) -> Tuple[bool, str]:
    stage = str(row.get("stage") or "")
    event = str(row.get("event") or "")
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

    if stage == "commander_router" and event == "error":
        reason = str(payload.get("error_type") or payload.get("error") or "commander_error")
        return True, f"commander_router:error:{reason}"

    if stage == "commander_router" and event == "transition":
        transition = str(payload.get("transition") or "").strip().lower()
        if transition == "cooldown":
            reason = str(payload.get("reason") or "cooldown_transition")
            return True, f"commander_router:transition:{reason}"

    if stage == "commander_router" and event == "resilience":
        reason = str(payload.get("reason") or "").strip().lower()
        if reason in ("cooldown_active", "incident_threshold_cooldown"):
            return True, f"commander_router:resilience:{reason}"

    if stage == "execute_from_packet" and event == "error":
        reason = str(payload.get("error") or "execute_error")
        return True, f"execute_from_packet:error:{reason}"

    return False, ""
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure incident labeling, no Guard effects. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b3_incident_trigger_owner.py`, explicit input→expected: commander_router/error error_type=E -> (True,'commander_router:error:E'). Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R4 VERIFIED | RF-063 | scripts/diagnostics/reconstruct_incident_timeline.py::_is_recovery @ L84 | SOURCE_BLOB=c47b817cef0c29957d010c105487594ae5a874c6

**TARGET:** `scripts/diagnostics/incident_timeline_recovery_projection.py::_is_recovery` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _is_recovery(row: Dict[str, Any]) -> Tuple[bool, str]:
    stage = str(row.get("stage") or "")
    event = str(row.get("event") or "")
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

    if stage == "commander_router" and event == "intervention":
        return True, "commander_router:intervention"
    if stage == "commander_router" and event == "end":
        status = str(payload.get("status") or "").strip().lower()
        if status in ("ok", "resuming", "normal"):
            return True, f"commander_router:end:{status or 'ok'}"
    if stage == "commander_router" and event == "resilience":
        reason = str(payload.get("reason") or "").strip().lower()
        if reason in ("cooldown_not_active", "resume_applied", "operator_resumed"):
            return True, f"commander_router:resilience:{reason}"
    if stage == "execute_from_packet" and event == "end":
        return True, "execute_from_packet:end"
    return False, ""
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure recovery labeling. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b4_is_recovery_owner.py`, explicit input→expected: commander_router/intervention -> (True,'commander_router:intervention'). Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R5 VERIFIED | RF-063 | scripts/diagnostics/reconstruct_incident_timeline.py::_event_reason @ L104 | SOURCE_BLOB=c47b817cef0c29957d010c105487594ae5a874c6

**TARGET:** `scripts/diagnostics/incident_timeline_reason_projection.py::_event_reason` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _event_reason(row: Dict[str, Any]) -> str:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    for key in ("reason", "error_type", "error", "status"):
        v = payload.get(key)
        if v:
            return str(v)
    return ""
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b5_event_reason_owner.py`, explicit input→expected: payload.reason='x' -> 'x'; {}->''. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.

### R6 VERIFIED | RF-063 | scripts/diagnostics/reconstruct_incident_timeline.py::_build_markdown @ L113 | SOURCE_BLOB=c47b817cef0c29957d010c105487594ae5a874c6

**TARGET:** `scripts/diagnostics/incident_timeline_markdown_projection.py::_build_markdown` (confirmed function ABSENT at Actor HEAD; same Actor RF Owner). **EXACT COMPUTATION BODY TO MOVE:**

```python
def _build_markdown(out: Dict[str, Any]) -> str:
    lines = [
        f"# Incident Timeline Reconstruction ({out.get('day')})",
        "",
        f"- ok: **{bool(out.get('ok'))}**",
        f"- events: **{int(out.get('events') or 0)}**",
        f"- runs: **{int(out.get('runs') or 0)}**",
        f"- incident_total: **{int(out.get('incident_total') or 0)}**",
        f"- recovered_incident_total: **{int(out.get('recovered_incident_total') or 0)}**",
        f"- unresolved_incident_total: **{int(out.get('unresolved_incident_total') or 0)}**",
        "",
        "## Trigger Totals",
        "",
    ]
    trigger_total = out.get("trigger_total") if isinstance(out.get("trigger_total"), dict) else {}
    if trigger_total:
        for k, v in sorted(trigger_total.items()):
            lines.append(f"- {k}: {int(v)}")
    else:
        lines.append("- (none)")

    lines += ["", "## Recovery Totals", ""]
    recovery_total = out.get("recovery_total") if isinstance(out.get("recovery_total"), dict) else {}
    if recovery_total:
        for k, v in sorted(recovery_total.items()):
            lines.append(f"- {k}: {int(v)}")
    else:
        lines.append("- (none)")

    ttr = out.get("ttr_sec") if isinstance(out.get("ttr_sec"), dict) else {}
    lines += [
        "",
        "## Time To Recovery (sec)",
        "",
        f"- count: {int(float(ttr.get('count') or 0.0))}",
        f"- avg: {float(ttr.get('avg') or 0.0):.3f}",
        f"- p50: {float(ttr.get('p50') or 0.0):.3f}",
        f"- p95: {float(ttr.get('p95') or 0.0):.3f}",
        f"- max: {float(ttr.get('max') or 0.0):.3f}",
        "",
        "## Failures",
        "",
    ]
    failures = out.get("failures") if isinstance(out.get("failures"), list) else []
    if failures:
        for msg in failures:
            lines.append(f"- {msg}")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)
```

**Thin wrapper / callers / monkeypatch / isolation:** SOURCE retains same signature, defaults, annotations, import/caller surface and exception timing; only delegates to Owner, with no duplicate BODY. TARGET never imports SOURCE. Where source globals are used, Owner accepts keyword-only `facade` and resolves global names at call time, SOURCE passes `sys.modules[__name__]`; preserve monkeypatch after import. Generator uses `yield from` (not eager list) and lazy exception timing. pure markdown, no IO. No live orders, Broker/Guard/UEF/Step5C, network, operating state, CI, deploy, RunLab or frozen oracles.

**Reserve hypothesis, NOT EXECUTABLE NOW:** `tests/test_p15_rf063_10h_b6_build_markdown_owner.py`, explicit input→expected: day=2026-10-31 events=0 -> header and zero events. Verify original baseline vs owner vs wrapper, negative/exception and patch seam, fake/temp only. Reverify blob/target at promotion; reserve is not code completion or G1/G2.


## REPORT AND CONTINUITY

Report to #12: `ORDER_ID=B-20261031-13 | CANONICAL_HEAD | ORDER_BLOB | B_REMOTE_HEAD_BEFORE/AFTER | B1,B2,B3,B4,B7,B8 IMPLEMENTED/REMOTE_DONE/BLOCKED | B5,B6 REMOTE_DONE_FROM_PREVIOUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | NEW_BODY_MOVES | FIRST_BLOCKER | NEXT_SAFE_ITEM | START_KST/END_KST/ELAPSED_MIN`. Times measured only, never inferred from comment timestamps. B5/B6 are not new work. R1–R6 reserve is design-only, NOT executable. Normal push and re-fetch branch HEAD/blob; report PUSH_BLOCKED separately if auth fails, continue remaining safe items. No C04/C05/RF/STATUS/doc edits.
