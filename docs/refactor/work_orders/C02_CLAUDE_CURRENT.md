# Agentra P1.5 FAST-3 — C02 A NEW verified BODY MOVE order (8 items)

**C03 issue 2026-10-30 17h KST.** Previous order blob `7c2cdb74f6deedd6d161c959ff5fa4a914dc5142` is **REMOTE_DONE 10/10**, confirmed actor remote HEAD `1cc562b4319a3d7008bd38c1efcc7d699dd7da16` and #11 latest delivery; do not re-read old PASS or reimplement. Owner branch: `work/p15-a-reporter-pure-20261021`; canonical `integration/p1.5`. **Read this file only as assignment**; no D00/RF/INDEX/T00/queue/C03/HANDOFF lookup or self-selection. Source and target ownership was checked by C03. This order is new, does not retroactively cancel any already-started prior run.

**Preflight for each item:** fetch origin, capture canonical integration SHA, this C02 blob, actor remote SHA and current actor SHA. Exact verified source `libs/reporting/llm_artifacts.py` blob `1c093529d1885e976a49a190a125bcdb99c84afa` at actor HEAD `1cc562b4319a3d7008bd38c1efcc7d699dd7da16`. C03 verified every target below **404/missing** on actor remote; same source/target paths are not assigned to the other actor. If concurrent actor work has already delivered an exact item, classify REMOTE_DONE by current source wrapper+target+test blobs; never rerun same-SHA tests, then proceed with remaining safe items. Stop a conflicting item only, not the entire order.

**Required implementation:** Move **actual existing function BODY**, not a copy, into its specified single new Owner TARGET. Leave original name, signature, defaults, annotations and thin wrapper in SOURCE. Target may accept keyword-only `facade`; call with `facade=sys.modules[__name__]` (SOURCE already imports sys) and resolve original globals/helpers **at invocation** via `facade.NAME` to preserve monkeypatch and recursive call semantics. No reverse import from target to SOURCE. Preserve ordered dict keys, exact output bytes, exceptions, reference identity, lazy calls and caller behavior. Capture before/after golden outputs with 3–4 fake/temporary fixtures each; test negative/monkeypatch seam. Normal targeted `.venv/bin/python -m pytest -q -p no:cacheprovider tests/<item-test>.py` exit0 (or equivalent isolated stdlib smoke if pytest absent); no forced -O/full peer/hosted CI. Commit only code/new targeted tests, normal non-force push **only actor branch**, re-fetch remote ref and SOURCE/TARGET/TEST blob SHA after each push. HTTPS credentials failure is PUSH_BLOCKED only: preserve local commit, approved exact reviewed-tree GitHub write if equivalence provable; otherwise LOCAL_ONLY, report error and continue next safe item. No probe commits, no main, no D00/C01/C02/RF/STATUS/C04/C05/HANDOFF or other actor branch writes. Do not touch Broker/Guard/Step5C/UEF/real-mode/RunLab runtime, operational state or frozen oracles. G1/G2/G3 and RF DONE remain C04/C05 acceptance, not this document commit.

### A1 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::canonical_trade_day_root` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L18–19) → TARGET `libs/reporting/llm_artifacts_path_projection.py::canonical_trade_day_root`

**Actual BODY:** Move Path(reports_root)/'trades'/str(day or '').strip() exactly; no filesystem access.

**Targeted fixtures, input→expected:** Path('reports'),' 2026-10-30 '→Path('reports/trades/2026-10-30'); day None→reports/trades; root Path('/tmp/r')→/tmp/r/trades/<day>.

**Test:** `tests/test_p15_rf035_path_canonical_trade_day_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A1 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A2. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A2 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::_repo_root_from_reports_root` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L60–64) → TARGET `libs/reporting/llm_artifacts_path_projection.py::_repo_root_from_reports_root`

**Actual BODY:** Move Path root name 'reports'→parent, otherwise same root; no IO.

**Targeted fixtures, input→expected:** Path('/x/reports')→Path('/x'); Path('/x/other')→same; Path('reports')→Path('.'); Path('/x/reports/sub')→same.

**Test:** `tests/test_p15_rf035_path_repo_root_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A2 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A3. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A3 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::operator_summary_artifact_root` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L527–538) → TARGET `libs/reporting/llm_artifacts_path_projection.py::operator_summary_artifact_root`

**Actual BODY:** Move operator_summary/daily/weekly/monthly/symbols normalization and no-double-nesting rule exactly.

**Targeted fixtures, input→expected:** Path('reports')→reports/operator_summary; Path('reports/operator_summary')→same; Path('reports/operator_summary/daily')→parent; Path('reports/other')→reports/other/operator_summary.

**Test:** `tests/test_p15_rf035_path_operator_root_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A3 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A4. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A4 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::daily_artifact_paths` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L541–561) → TARGET `libs/reporting/llm_artifacts_path_projection.py::daily_artifact_paths`

**Actual BODY:** Move normalized day and 13-key ordered daily/legacy/root path dict, use facade.operator_summary_artifact_root at invocation.

**Targeted fixtures, input→expected:** reports,' 2026-10-30 '→root_dir reports/operator_summary/daily/2026-10-30; daily_report_json ends daily_report.json; legacy_daily_json ends daily_2026-10-30.json; monkeypatch facade.operator_summary_artifact_root to Path('fake')→root_dir fake/daily/<day>.

**Test:** `tests/test_p15_rf035_path_daily_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A4 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A5. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A5 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::symbol_artifact_paths` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L564–578) → TARGET `libs/reporting/llm_artifacts_path_projection.py::symbol_artifact_paths`

**Actual BODY:** Move symbol strip/uppercase and ordered symbol-history paths, facade.operator_summary_artifact_root call-time.

**Targeted fixtures, input→expected:** reports,' 005930 '→root_dir reports/operator_summary/symbols/005930; 'abC'→ABC; symbol None→empty terminal name (exact Path semantics); patch facade.operator_summary_artifact_root spy.

**Test:** `tests/test_p15_rf035_path_symbol_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A5 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A6. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A6 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::weekly_artifact_paths` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L581–590) → TARGET `libs/reporting/llm_artifacts_path_projection.py::weekly_artifact_paths`

**Actual BODY:** Move weekly YYYY-Www root and weekly_summary_json/md paths, call facade.operator_summary_artifact_root at invocation.

**Targeted fixtures, input→expected:** reports,' 2026-W44 '→reports/operator_summary/weekly/2026-W44; week ''→weekly root; weekly_summary_md basename weekly_summary.md; monkeypatch facade root→Path('fake') and compare.

**Test:** `tests/test_p15_rf035_path_weekly_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A6 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A7. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A7 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::monthly_artifact_paths` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L593–602) → TARGET `libs/reporting/llm_artifacts_path_projection.py::monthly_artifact_paths`

**Actual BODY:** Move monthly YYYY-MM root and monthly_summary_json/md paths, call facade.operator_summary_artifact_root at invocation.

**Targeted fixtures, input→expected:** reports,' 2026-10 '→reports/operator_summary/monthly/2026-10; month ''→monthly root; monthly_summary_json basename monthly_summary.json; patch facade root→Path('fake') and compare.

**Test:** `tests/test_p15_rf035_path_monthly_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A7 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to A8. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.

### A8 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::trade_artifact_paths` (blob `1c093529d1885e976a49a190a125bcdb99c84afa`, L417–524) → TARGET `libs/reporting/llm_artifacts_trade_path_projection.py::trade_artifact_paths`

**Actual BODY:** Move entire 108-line read-only trade path construction, time_bucket fallback, legacy normalized paths and ordered 60+ key dict. At invocation resolve facade.resolve_trade_day_root / facade.canonical_trade_day_root / facade.find_trade_dir, not a stale import; preserve Path identity, aliases (monitor_evidence_json and monitor_timeline_json), and exact legacy keys. Reads only temp fake directories in tests; never writes production files.

**Targeted fixtures, input→expected:** tmp_path/'reports', day='2026-10-30', trade_id='TRD_1'→trade_root reports/trades/2026-10-30/TRD_1 and entry_json there; time_bucket='09' with no existing dir→trade_root .../09/TRD_1; create fake existing TRD_1 under tmp_path then prefer_existing_day_root=True→existing root wins; patch facade.find_trade_dir to return fake Path and assert exact ordered dict parity.

**Test:** `tests/test_p15_rf035_path_trade_artifact_owner.py`: capture exact pre-move baseline; compare SOURCE wrapper vs TARGET and before/after output, dict key order, exception and patch-time behavior. For A8 on a fixture or safety failure, record exact error as BLOCKED, do not alter policy/effects, then proceed to remaining earlier individually BLOCKED items. **Push** only SOURCE/TARGET/new TEST, verify exact remote ref and blob after each item.
## KEEP / next six VERIFIED reserve (C03-owned; not part of A1–A8)

KEEP `utc_now_iso` clock, `persist_llm_artifact_refs` / `write_json` / `write_text` filesystem effects and all model/network/runtime execution. A1–A7 are pure Path projections; A8 is **read-only** path lookup (fake temp directories only). No real reports, state, orders, broker, or policy changes.

**RESERVE_VERIFIED=6 (future C03 order only):** RF-035 source `libs/reporting/llm_artifacts.py` blob `1c093529d1885e976a49a190a125bcdb99c84afa`, actual bodies L46–141 inspected, TARGET `libs/reporting/llm_artifacts_trade_lookup.py` verified 404 on A remote. R1 `find_trade_dir` L46–57 → trade_lookup::find_trade_dir, fake direct/nested/missing and facade.iter_trade_dirs; R2 `_looks_like_trade_day_dir` L67–82 → trade_lookup::looks_like_trade_day_dir, tmp nested TRD_/nontrade/permission-exception; R3 `misplaced_trade_day_root` L84–96 → trade_lookup::misplaced_trade_day_root, canonical/fallback/blank day with facade._repo_root_from_reports_root and looks_like; R4 `resolve_trade_day_root` L98–106 → trade_lookup::resolve_trade_day_root, canonical exists/fallback exists/neither; R5 `iter_trade_day_roots` L108–124 → trade_lookup::iter_trade_day_roots, canonical+legacy dedupe/sorted tmp tree; R6 `list_misplaced_trade_day_roots` L126–141 → trade_lookup::list_misplaced_trade_day_roots, canonical exclusion/legacy-only and temp exceptions. Read-only filesystem scans restricted to tmp_path; facade lookup at call time. Recheck latest A source/target before issuing next 8–10. No code/test/pytest executed by C03; reserve is source/target/effect verification, not delivered MOVE.

**Final report:** #11 actual START/END, canonical/order/owner SHA, A1–A8 individually IMPLEMENTED/REMOTE_DONE/BLOCKED, source before/after LOC/blobs, normal targeted exit, push remote SHA/blob or exact error, FIRST_BLOCKER/NEXT. C04/C05 own G1–G3 integration/DONE.
