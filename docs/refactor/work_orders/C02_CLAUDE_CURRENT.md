# Agentra FAST-3 C02 — Claude A single-file execution order (A1–A10)

**C03 issuance:** 2026-10-30, replaces fully REMOTE_DONE A1–A9 order blob `7f3c2af364622e4ee77bb76d16ab239b22c1327c`. All old nine are REMOTE_DONE, never repeat. Actor: Claude A exclusively, canonical `integration/p1.5`, authorized `work/p15-a-reporter-pure-20261021`. Read **only this C02 file** as assignment; no RF/INDEX/T00/D00/C03/queue/HANDOFF exploration or self-selection.

**Preflight:** fetch origin and record canonical HEAD, C02 blob, A remote HEAD and current local A SHA before each item. Verified SOURCE `libs/reporting/llm_artifacts.py` remote A blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c` (777 LOC) at A HEAD `85549ddb008a2b7a542f6518062db7f279398c9e`. All five new target modules were 404 on A remote; source/target overlap with B is zero. If a concurrent A run already moved any exact SOURCE/TARGET, mark REMOTE_DONE without rework/retesting old SHA, continue next safe item.

**Every-item implementation:** Move existing **entire calculation BODY** into specified single Owner TARGET, leaving original function name/signature/defaults as a thin wrapper in SOURCE. For dependency-bearing targets append keyword-only `facade` and call `facade=sys.modules[__name__]` from SOURCE (add `import sys` there if needed); all global helper lookups must occur at call time through facade (e.g. normalize_llm_status, split_prompt_messages, utc_now_iso, json/hashlib) to preserve monkeypatch semantics. No TARGET→facade module import, duplicate BODY, IO, persistence, network, live LLM calls or time-dependent unpatched test. Preserve byte output, dict order, nested identity, exception types, and legacy public signatures. For each 3–4 fixture cases, capture baseline before moving and compare with target/wrapper after; freeze clock where relevant. Existing `tests/test_rf035_*` / LLM artifact tests are read-only regression references; do not edit frozen tests.

**Delivery:** prepared `.venv/bin/python -m pytest -q -p no:cacheprovider <new targeted test>` normal exit0 (or isolated stdlib smoke when pytest unavailable). -O/full peer/hosted CI not required by D00 FAST-3. Commit **only code/tests**, normal non-force push to A branch, verify remote ref SHA plus SOURCE/TARGET/test blobs after each push. HTTPS credential failure blocks push only; preserve local commits, use approved exact-tree connector only when same reviewed commit tree is faithfully deliverable, else LOCAL_ONLY with SHA and next safe item. No probe commits. Never touch D00/C01/C02/RF/STATUS/C04/C05/HANDOFF or B branch. First PASS, partial push failure, short duration are not stop conditions; finish all safe A1–A10. Issue #11 single concise report with real START/END, order/input/remote SHA, each item status, before/after source LOC/blob, normal test exits, push ref/blob, FIRST_BLOCKER/NEXT. C03 document issuance is not code G1/G2/G3 or RF DONE.

### A1 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::split_prompt_messages` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L142–160) → TARGET `libs/reporting/llm_artifacts_prompt_projection.py::split_prompt_messages`

**BODY:** Move role-filtering loop, list/dict type gates, system/user order and '\n\n' joins verbatim. This is pure prompt text projection; do not merge system/user or trim individual content differently.

**Targeted fixtures (input → expected):** [{'role':'system','content':'S1'},{'role':'user','content':'U'},{'role':'system','content':'S2'}] → ('S1\n\nS2','U'); None → ('',''); rows with role='assistant' or non-dict skipped; role=' SYSTEM ' → system and empty content skipped.

**Test:** `tests/test_p15_rf035_llm_split_messages_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A2 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A2 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::split_prompt_text` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L161–193) → TARGET `libs/reporting/llm_artifacts_prompt_projection.py::split_prompt_text`

**BODY:** Move [system]/[user] multiline parser, role-flush logic and fallback raw prompt verbatim. Preserve exact whitespace, case-insensitive tags, repeated sections and empty handling.

**Targeted fixtures (input → expected):** '[system]\nS\n[user]\nU' → ('S','U'); 'plain text' → ('','plain text'); '[SYSTEM]\na\n[system]\nb\n[USER]\nc' → ('a\n\nb','c'); None → ('','').

**Test:** `tests/test_p15_rf035_llm_split_text_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A3 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A3 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::normalize_llm_status` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L194–204) → TARGET `libs/reporting/llm_artifacts_status_projection.py::normalize_llm_status`

**BODY:** Move exact status whitelist, lower/strip, line_repaired→salvaged, disabled/unavailable/dry_run→fallback, unknown→caller default. Preserve return case and fallback.

**Targeted fixtures (input → expected):** ' OK '→'ok'; 'line_repaired'→'salvaged'; 'disabled'→'fallback'; 'mystery', default='error'→'error'.

**Test:** `tests/test_p15_rf035_llm_normalize_status_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A4 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A4 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::canonical_llm_status` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L205–213) → TARGET `libs/reporting/llm_artifacts_status_projection.py::canonical_llm_status`

**BODY:** Move canonical mapping and use **facade.normalize_llm_status** at call time. Preserve timeout/network_error/parse_error/empty_response→error and unknown default.

**Targeted fixtures (input → expected):** 'timeout'→'error'; 'line_repaired'→'salvaged'; 'partial'→'partial'; patch facade.normalize_llm_status return 'network_error'→'error'.

**Test:** `tests/test_p15_rf035_llm_canonical_status_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A5 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A5 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::classify_llm_exception` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L214–222) → TARGET `libs/reporting/llm_artifacts_status_projection.py::classify_llm_exception`

**BODY:** Move TimeoutError and timeout text precedence, network marker tuple and default error. No network calls; exception classification only.

**Targeted fixtures (input → expected):** TimeoutError('x')→'timeout'; RuntimeError('timed out')→'timeout'; ConnectionError('dns failure')→'network_error'; ValueError('bad')→'error'.

**Test:** `tests/test_p15_rf035_llm_exception_class_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A6 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A6 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::make_attempt` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L223–258) → TARGET `libs/reporting/llm_artifacts_attempt_projection.py::make_attempt`

**BODY:** Move complete attempt payload builder: split prompts, step/role/model defaults, parsed_output dict/list identity, int(float(latency_ms)), normalized/canonical statuses, meta non-overwrite merge and key order. Use facade.split_prompt_messages/normalize_llm_status/canonical_llm_status at invocation.

**Targeted fixtures (input → expected):** step='', messages=[system S,user U], model='m', latency_ms='12.9' → step primary, prompts S/U, latency 12; status='timeout'→status timeout, llm_status error; meta={'role':'planner','step':'override','custom':1}→step not overwritten, role planner, custom 1; latency_ms='bad'→ValueError preserved.

**Test:** `tests/test_p15_rf035_llm_make_attempt_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A7 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A7 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::build_llm_response_artifact` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L259–381) → TARGET `libs/reporting/llm_artifacts_attempt_projection.py::build_llm_response_artifact`

**BODY:** Move entire 123-line read-only response artifact projection: schema/defaults, last attempt fallback, metadata source precedence, token usage, required_keys and completeness conversion, retry_count, finish_reason and repair_used. Use facade.utc_now_iso/normalize_llm_status/canonical_llm_status at call time; preserve nested alias/copy identity and exact dict insertion order.

**Targeted fixtures (input → expected):** component='scanner',run_id='R', attempts=[{'system_prompt':'S','user_prompt':'U','parsed_output':{'x':1},'model_info':{'model':'m'}}]→schema llm_response_artifact.v1, parsed_output {'x':1}, retry_count 0; status='timeout'→status timeout/llm_status error; meta={'error':'oops','token_usage':{'n':1},'repair_used':True}→error oops/token_usage n1/repair_used true; attempts=[{},{}]→retry_count1, missing required keys empty lists. Freeze facade.utc_now_iso for golden.

**Test:** `tests/test_p15_rf035_llm_response_artifact_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A8 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A8 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::_json_stable_text` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L393–398) → TARGET `libs/reporting/llm_artifacts_hash_projection.py::json_stable_text`

**BODY:** Move dict/list stable JSON with ensure_ascii=False, sort_keys=True, compact separators, otherwise str(payload or ''). Keep facade.json.dumps call-time seam and unicode bytes.

**Targeted fixtures (input → expected):** {'b':1,'a':'한'}→'{"a":"한","b":1}'; [2,1]→'[2,1]'; None→''; scalar 0→''; patch facade.json.dumps spy.

**Test:** `tests/test_p15_rf035_llm_stable_json_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A9 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A9 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::_sha256_text` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L399–402) → TARGET `libs/reporting/llm_artifacts_hash_projection.py::sha256_text`

**BODY:** Move SHA-256 of str(text or '').encode('utf-8') exactly, return hexdigest. Use facade.hashlib.sha256 at invocation to preserve module patch seam.

**Targeted fixtures (input → expected):** 'abc'→ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad; ''→e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; None→same empty hash; 0→same empty hash.

**Test:** `tests/test_p15_rf035_llm_sha256_text_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A10 without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

### A10 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::build_compact_input_artifact` (remote blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`, L553–590) → TARGET `libs/reporting/llm_artifacts_compact_projection.py::build_compact_input_artifact`

**BODY:** Move entire compact-input schema builder: json.dumps source/compact lengths, max(0,1-compact/source), component/run/story/day, source path and compact payload identity. Use facade.json.dumps and facade.utc_now_iso at invocation; do not write artifact or change clocks.

**Targeted fixtures (input → expected):** source_input={'a':1,'b':2},compact_input={'a':1}→source_char_count16, compact_input_char_count8, reduction_ratio0.5; invalid source/compact None→{} and reduction_ratio0; story_id='' trade_id='T'→story_id T; patch facade.utc_now_iso→fixed saved_at, original compact dict identity preserved.

**Test:** `tests/test_p15_rf035_llm_compact_input_owner.py`, original vs moved exact value/order/exception and patch seam. **BLOCKED:** log exact function/fixture/error and continue A1–A9 blocked recheck without changing effects. **Push:** code/test only, remote ref and SOURCE/TARGET/TEST blob verification.

## KEEP / verified six-item reserve (C03 only)

KEEP `utc_now_iso` clock, all filesystem readers/writers (`iter_trade_dirs`, `persist_llm_artifact_refs`, `write_json`, `write_text`), live/real effects and unrelated modules. These ten moves are pure LLM artifact **text/status/payload/hash/compact projections**, not model calls or persistence. The original public functions remain facade wrappers, never remove import compatibility. On ownership/effect conflict, SAFETY_BLOCKED only for that item; no new RF discovery by A.

**RESERVE_VERIFIED=6 (not part of A1–A10; A must not execute without next C03 order):** RF-035 SOURCE `libs/reporting/llm_artifacts.py` blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c`; all are actual unwrapped, pure Path projection bodies inspected on A HEAD; TARGET `libs/reporting/llm_artifacts_path_projection.py` was 404 on A remote. Proposed next six, subject to rechecking latest remote source/target: `_repo_root_from_reports_root` L54–60 → `repo_root_from_reports_root` (Path('x/reports')→Path('x')); `operator_summary_artifact_root` L701–714 → `operator_summary_artifact_root` (reports/operator_summary→same); `daily_artifact_paths` L715–737 → `daily_artifact_paths` (daily/YYYY-MM-DD keys and legacy paths); `symbol_artifact_paths` L738–754 → `symbol_artifact_paths` (uppercase symbol); `weekly_artifact_paths` L755–766 → `weekly_artifact_paths` (weekly/YYYY-Www); `monthly_artifact_paths` L767–777 → `monthly_artifact_paths` (monthly/YYYY-MM). No filesystem IO, state writes or Broker/Guard effects. Patch facade.operator_summary_artifact_root at use time for dependent functions. This is a **reserve**, not 6 newly delivered code changes; 8–10 new item order still required when A1–A10 exhausts.

**NEXT:** C04 integrates only verified A source/test SHA, C05 G1/G2/G3/STATUS; C03 replenishes future A order. No actor self-selection.
