# Agentra P1.5 FAST-3 — C01 B NEW verified BODY MOVE order (9 items)

**C03 issue 2026-10-30 17h KST.** Previous order blob `1264b7480f9af841fed45c5d3a8eb49d8d793bc0` is **REMOTE_DONE 8/8**, confirmed actor remote HEAD `3f36f7185a5db639ce73fd93b0f62695f5df2570` and #12 latest delivery; do not re-read old PASS or reimplement. Owner branch: `work/p15-b-operator-structure-20261022`; canonical `integration/p1.5`. **Read this file only as assignment**; no D00/RF/INDEX/T00/queue/C03/HANDOFF lookup or self-selection. Source and target ownership was checked by C03. This order is new, does not retroactively cancel any already-started prior run.

**Preflight for each item:** fetch origin, capture canonical integration SHA, this C01 blob, actor remote SHA and current actor SHA. Exact verified source `scripts/diagnostics/check_trade_report_runtime_regression.py` blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f` at actor HEAD `3f36f7185a5db639ce73fd93b0f62695f5df2570`. C03 verified every target below **404/missing** on actor remote; same source/target paths are not assigned to the other actor. If concurrent actor work has already delivered an exact item, classify REMOTE_DONE by current source wrapper+target+test blobs; never rerun same-SHA tests, then proceed with remaining safe items. Stop a conflicting item only, not the entire order.

**Required implementation:** Move **actual existing function BODY**, not a copy, into its specified single new Owner TARGET. Leave original name, signature, defaults, annotations and thin wrapper in SOURCE. Target may accept keyword-only `facade`; call with `facade=sys.modules[__name__]` (SOURCE already imports sys) and resolve original globals/helpers **at invocation** via `facade.NAME` to preserve monkeypatch and recursive call semantics. No reverse import from target to SOURCE. Preserve ordered dict keys, exact output bytes, exceptions, reference identity, lazy calls and caller behavior. Capture before/after golden outputs with 3–4 fake/temporary fixtures each; test negative/monkeypatch seam. Normal targeted `.venv/bin/python -m pytest -q -p no:cacheprovider tests/<item-test>.py` exit0 (or equivalent isolated stdlib smoke if pytest absent); no forced -O/full peer/hosted CI. Commit only code/new targeted tests, normal non-force push **only actor branch**, re-fetch remote ref and SOURCE/TARGET/TEST blob SHA after each push. HTTPS credentials failure is PUSH_BLOCKED only: preserve local commit, approved exact reviewed-tree GitHub write if equivalence provable; otherwise LOCAL_ONLY, report error and continue next safe item. No probe commits, no main, no D00/C01/C02/RF/STATUS/C04/C05/HANDOFF or other actor branch writes. Do not touch Broker/Guard/Step5C/UEF/real-mode/RunLab runtime, operational state or frozen oracles. G1/G2/G3 and RF DONE remain C04/C05 acceptance, not this document commit.

### B1 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_safe_int` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L50–57) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_safe_int`

**Actual BODY:** Move int(float(value)) with (None,'') fallback, broad Exception fallback, exact default conversion; pure calculation.

**Targeted fixtures, input→expected:** '12.9' default0→12; 'bad' default7→7; None default4→4; -2.7→-2.

**Test:** `tests/test_p15_rf063_evidence_safe_int_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B1 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B2. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B2 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_is_empty_placeholder` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L72–88) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_is_empty_placeholder`

**Actual BODY:** Move recursive type classification for None/bool/numeric/string/list/dict, retaining recursive call through facade._is_empty_placeholder at invocation and dict values iteration order.

**Targeted fixtures, input→expected:** None→True; False/0/[]→True; {'x':[]}→True; {'x':1}→False; monkeypatch facade._is_empty_placeholder recursive spy.

**Test:** `tests/test_p15_rf063_evidence_empty_placeholder_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B2 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B3. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B3 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_has_substantive_entry_evidence` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L90–111) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_has_substantive_entry_evidence`

**Actual BODY:** Move entry run_id/ts/price/qty/scanner_context/execution_context/details evidence predicates exactly; no broker/IO.

**Targeted fixtures, input→expected:** {}→False; {'run_id':'R'}→True; {'price':0}→False; {'execution_context':{'order_id':'O'}}→True.

**Test:** `tests/test_p15_rf063_evidence_entry_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B3 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B4. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B4 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_has_substantive_exit_evidence` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L113–135) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_has_substantive_exit_evidence`

**Actual BODY:** Move exit run_id/ts/reason/price/qty/execution_details/monitor_context predicates exactly.

**Targeted fixtures, input→expected:** {}→False; {'reason_human':'stop'}→True; {'qty':0}→False; {'monitor_context':{'trigger_type':'exit'}}→True.

**Test:** `tests/test_p15_rf063_evidence_exit_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B4 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B5. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B5 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_is_closed_trade` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L59–70) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_is_closed_trade`

**Actual BODY:** Move lifecycle status normalization and closed/exited/sell fallback; call facade._has_substantive_exit_evidence at invocation, preserve OPEN short-circuit.

**Targeted fixtures, input→expected:** {'status':'open'} + {'run_id':'R'}→False; {'status':'closed'}+{}→True; {'status':'unknown'}+{'run_id':'R'}→True; unknown+{}→False; monkeypatch facade exit predicate.

**Test:** `tests/test_p15_rf063_evidence_closed_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B5 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B6. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B6 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_section_provenance_all_fallback` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L137–146) → TARGET `scripts/diagnostics/trade_artifact_evidence_predicates.py::_section_provenance_all_fallback`

**Actual BODY:** Move filtering of dict provenance sections and all fallback/unknown/missing classification, including false for empty/non-dict.

**Targeted fixtures, input→expected:** {}→False; {'section_provenance':{'a':{'source':'fallback'},'b':{'source':'unknown'}}}→True; mixed 'model'→False; non-dict sections only→False.

**Test:** `tests/test_p15_rf063_evidence_provenance_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B6 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B7. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B7 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_parse_case` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L148–157) → TARGET `scripts/diagnostics/trade_artifact_case_projection.py::_parse_case`

**Actual BODY:** Move colon-split/strip, day/trade_id/optional target_run_id ordered dict and exact ValueError text.

**Targeted fixtures, input→expected:** '2026-10-30:TRD_1:RUN_1'→day/trade_id/target_run_id exact; '2026-10-30:TRD_1'→target_run_id ''; 'bad'→ValueError('invalid case spec: bad'); ' :TRD'→ValueError.

**Test:** `tests/test_p15_rf063_case_parse_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B7 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B8. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B8 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_normalize_cases` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L159–172) → TARGET `scripts/diagnostics/trade_artifact_case_projection.py::_normalize_cases`

**Actual BODY:** Move default-case projection, ordered dedupe by (day,trade_id), first target_run_id wins; resolve facade.DEFAULT_GOLDEN_CASES and facade._parse_case at invocation.

**Targeted fixtures, input→expected:** []→3 DEFAULT_GOLDEN_CASES with target_run_id ''; ['2026-10-30:T:R1','2026-10-30:T:R2']→one R1; same trade ID on two days→two rows; patch facade._parse_case spy called once per input.

**Test:** `tests/test_p15_rf063_case_normalize_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B8 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to B9. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### B9 — RF-063 | SOURCE `scripts/diagnostics/check_trade_report_runtime_regression.py::_command_to_text` (blob `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f`, L212–214) → TARGET `scripts/diagnostics/trade_artifact_command_text.py::_command_to_text`

**Actual BODY:** Move only ' '.join(str(part) for part in command), no subprocess execution or shell quoting change.

**Targeted fixtures, input→expected:** ['python','-m','pytest']→'python -m pytest'; []→''; ['a',12,None]→'a 12 None'; original list remains unchanged.

**Test:** `tests/test_p15_rf063_command_text_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For B9 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to remaining earlier individually BLOCKED items. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.
## KEEP / next six VERIFIED reserve (C03-owned; not part of B1–B9)

KEEP `_emit_text` stdout effect, `_read_json` file read, `_resolve_trade_context` IO aggregation, `_run_python_json` subprocess, `validate_trade_artifact_chain` mixed file reads, `_build_parser`/main CLI and command builders. Do not move these merely to increase counts. New B items are **pure predicates/case/text projections** from RF-063; no report file reads, process launch, runtime mutation, order or broker activity.

**RESERVE_VERIFIED=6 (future order only, not permission for B self-selection):** RF-065 source `scripts/research/run_phase5_validation_bundle.py` B remote blob `7f7b2aa0717131b4de178050dd9b3a55051561ad`, current real bodies and call dependencies inspected, targets `scripts/research/phase5_validation_read_projection.py` and `scripts/research/phase5_validation_markdown.py` both 404 on B remote. R1 `_iter_events` L29–48 → read_projection::_iter_events, temp JSONL valid/invalid lines and missing file; R2 `_read_json` L49–58 → read_projection::_read_json, tmp valid/invalid/missing JSON; R3 `_to_day_key` L59–80 → read_projection::_to_day_key, epoch/ISO/Z/invalid; R4 `_resolve_day` L81–89 → read_projection::_resolve_day, requested day/latest event/fixed date fallback, facade._iter_events/_to_day_key and clock patch; R5 `_safe_rel` L90–96 → read_projection::_safe_rel, same-root/child/outside path; R6 `_render_bundle_markdown` L113–292 → phase5_validation_markdown::_render_bundle_markdown, empty/partial/full payload byte parity and facade._safe_rel/json use-time patch. R1/R2/R4 are **read-only file access in tmp_path only**, no writer or subprocess. Recheck actor HEAD, exact source bodies and target 404 before issuing next order. No tests run by C03; reserve is preflight source/target/effect verification only.

**Final report:** #12 actual START/END, canonical/order/owner SHA, B1–B9 individually IMPLEMENTED/REMOTE_DONE/BLOCKED, source before/after LOC/blobs, normal targeted exit, push remote SHA/blob or exact error, FIRST_BLOCKER/NEXT. C04/C05 handle selective integration/G1–G3.
