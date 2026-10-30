# Agentra P1.5 FAST-3 — A NEW BODY MOVE 8-item single-file execution order

**Issued 2026-10-30 18h KST by C03.** Previous C02 blob `8353c3830b26d964670a3aece1431d1b8b372e55` was REMOTE_DONE (8/8) at owner HEAD `0bb3bedf739eb587bd8838dd40839b931772b0a5`; do not reimplement or retest. New items are separate functions. Canonical `integration/p1.5`; authorized A owner branch `work/p15-a-reporter-pure-20261021`. Read **this order only** for assignment; no D00/RF/queue/INDEX/C03/HANDOFF lookup or self-selection. Starting orders already in flight are not retroactively cancelled.

**Verified source:** `libs/reporting/llm_artifacts.py` exact owner-branch blob `9721ccd6d3b61ed78109faa670481ea5134914a1` at HEAD `0bb3bedf739eb587bd8838dd40839b931772b0a5`. All TARGET files listed below were 404 on owner branch at preflight; no A/B SOURCE/TARGET overlap. Owner RF RF-035; preserve original file Owner. Before each item fetch origin and capture canonical SHA, this order blob, owner remote HEAD and current local HEAD. If source/blob/target differs, inspect exact new code: mark already moved REMOTE_DONE only on wrapper+target+test evidence, otherwise BLOCKED for that item, and continue other safe items without overwriting concurrent changes.

**Per-item mandatory MOVE:** Move actual existing calculation BODY, never copy-and-leave-duplicate. Preserve original SOURCE function name, signature, defaults, annotations, docstring where present, and a thin delegating wrapper. Target can take extra keyword-only `facade`; wrapper passes `facade=sys.modules[__name__]` (SOURCE already imports sys). Use call-time `facade.NAME` for any original global/callee that can be monkeypatched; no reverse TARGET→SOURCE import. Preserve exact output bytes, order, identity, laziness, exception types, original effect boundaries. New target file is owned by this actor and RF. Test **before/after golden parity** in fake/tmp_path only, including explicit normal and negative fixtures below. For each item run `.venv/bin/python -m pytest -q -p no:cacheprovider <targeted test>` and record actual exit; if pytest unavailable use reproducible stdlib normal smoke, do not fabricate PASS. FAST-3 G2 needs one normal targeted exit0; -O/full peer/hosted CI are not mandatory. Commit **only code + new targeted test** for that item, push normally to authorized actor branch, fetch exact remote ref and SOURCE/TARGET/TEST blob SHA after every push. Terminal HTTPS failure is PUSH_BLOCKED only: preserve local commit, use approved connected GitHub write only if exact reviewed tree equivalence can be proven; otherwise report LOCAL_ONLY and proceed to next safe non-overwriting item. No probe commit, no main, no document/RF/STATUS/C04/C05/HANDOFF writes. No protected Broker/Guard/Step5C/UEF, real orders, live network, RunLab runtime, operational DB/state, frozen oracle, production filesystem writes or forced push. C04 integrates; C05 alone decides G1/G2/G3 and RF DONE. Do **all 8** in order; a single PASS/commit/push failure is not a stop condition.

### A1 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::iter_trade_dirs` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L24–45) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::iter_trade_dirs`

**MOVE BODY:** Move the full root.exists/is_dir guard, root.rglob('*') read-only scan, special subdirectory→parent selection, TRD_ prefix or lifecycle/aggregated/trade_lifecycle marker checks, resolved-path dedupe, and `(item.parent.name,item.name)` sorting. Do not eager-cache or change `Path.resolve()`/exception propagation.

**Wrapper/caller/monkeypatch:** Resolve `facade.Path`, `facade.Dict` only if used and keep original traversal lazy; no SOURCE import in TARGET. `find_trade_dir` must still resolve `facade.iter_trade_dirs` at call time. Leave original SOURCE `iter_trade_dirs` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_iter_dirs_owner.py`; fake/tmp-only input→expected: missing tmp root→[]; tmp/trades/2026-10-30/TRD_1→[TRD_1]; nested TRD_2/brief and TRD_2/lifecycle marker→one TRD_2; two TRD_ names→existing sorted order. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_iter_dirs_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A2.

### A2 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::find_trade_dir` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L48–59) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::find_trade_dir`

**MOVE BODY:** Move trade_id `str(...).strip()` normalization, blank→None, direct directory preference and fallback iteration returning first matching name; no mkdir or writes.

**Wrapper/caller/monkeypatch:** `facade.iter_trade_dirs(root)` must be looked up when called (monkeypatch spy); preserve `Path` and original return identity. Leave original SOURCE `find_trade_dir` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_find_dir_owner.py`; fake/tmp-only input→expected: blank trade_id→None; tmp direct TRD_A→direct; nested TRD_B→nested; missing→None; patch `facade.iter_trade_dirs` to return fake nested Path→same object. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_find_dir_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A3.

### A3 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::_looks_like_trade_day_dir` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L66–80) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::_looks_like_trade_day_dir`

**MOVE BODY:** Move exists/is_dir checks, direct TRD_ child and grandchild detection, `try/except Exception: False` exactly; do not follow or write real production tree.

**Wrapper/caller/monkeypatch:** Preserve original name/signature; target may accept `facade` for call-time globals; keep same exception swallowing only inside original try. Leave original SOURCE `_looks_like_trade_day_dir` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_day_shape_owner.py`; fake/tmp-only input→expected: missing tmp dir→False; tmp/day/TRD_1→True; tmp/day/bucket/TRD_2→True; empty tmp/day→False; monkeypatch Path.iterdir raising OSError→False. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_day_shape_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A4.

### A4 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::misplaced_trade_day_root` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L83–94) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::misplaced_trade_day_root`

**MOVE BODY:** Move normalized day blank guard, canonical path, repo_root/day candidate equality guard, and candidate shape predicate; return candidate or None unchanged.

**Wrapper/caller/monkeypatch:** At invocation call `facade.canonical_trade_day_root`, `facade._repo_root_from_reports_root`, `facade._looks_like_trade_day_dir`; original signature and thin wrapper. Leave original SOURCE `misplaced_trade_day_root` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_misplaced_owner.py`; fake/tmp-only input→expected: day blank→None; tmp repo/day/TRD_1→repo/day; no misplaced day→None; patch facade shape predicate False→None; candidate==canonical→None. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_misplaced_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A5.

### A5 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::resolve_trade_day_root` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L97–104) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::resolve_trade_day_root`

**MOVE BODY:** Move primary canonical path exists-first choice, misplaced fallback when present, otherwise primary. Preserve `Path` identity and short-circuit.

**Wrapper/caller/monkeypatch:** Call `facade.canonical_trade_day_root` and `facade.misplaced_trade_day_root` at invocation, so a monkeypatch remains visible. Leave original SOURCE `resolve_trade_day_root` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_resolve_owner.py`; fake/tmp-only input→expected: tmp canonical existing→canonical; canonical missing and misplaced present→misplaced; both absent→canonical; patch facade misplaced to spy and verify not called when canonical exists. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_resolve_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A6.

### A6 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::iter_trade_day_roots` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L107–122) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::iter_trade_day_roots`

**MOVE BODY:** Move sorted canonical `reports/trades` child discovery, `seen_days` dedupe, sorted repo_root children, shape predicate filtering and ordered list append exactly; preserve exception behavior for missing repo root.

**Wrapper/caller/monkeypatch:** Resolve `facade._repo_root_from_reports_root` and `facade._looks_like_trade_day_dir` at call time; original return list/order. Leave original SOURCE `iter_trade_day_roots` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_iter_roots_owner.py`; fake/tmp-only input→expected: tmp canonical days 2026-10-29/30→two ordered; tmp repo legacy 2026-10-28/TRD_1→legacy appended; legacy duplicate 2026-10-30 excluded; monkeypatch shape False→legacy omitted. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_iter_roots_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A7.

### A7 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::list_misplaced_trade_day_roots` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L125–140) → TARGET `libs/reporting/llm_artifacts_trade_lookup.py::list_misplaced_trade_day_roots`

**MOVE BODY:** Move repo_root/canonical_root resolution, canonical day-name set comprehension, sorted repo-root scan and shape predicate, canonical exclusion. Do not change behavior when directories are absent.

**Wrapper/caller/monkeypatch:** Resolve `facade._repo_root_from_reports_root` and `facade._looks_like_trade_day_dir` at invocation; preserve original exception paths. Leave original SOURCE `list_misplaced_trade_day_roots` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_trade_lookup_list_misplaced_owner.py`; fake/tmp-only input→expected: tmp canonical 2026-10-30 plus legacy same day→exclude; legacy 2026-10-29/TRD_1→[legacy]; no legacy→[]; patch shape False→[]. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_trade_lookup_list_misplaced_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_trade_lookup.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue A8.

### A8 — RF-035 | SOURCE `libs/reporting/llm_artifacts.py::llm_artifact_paths` (blob `9721ccd6d3b61ed78109faa670481ea5134914a1`, L223–231) → TARGET `libs/reporting/llm_artifacts_run_paths.py::llm_artifact_paths`

**MOVE BODY:** Move `find_llm_run_dir(Path(reports_root),str(day or '').strip(),str(run_id or '').strip())`, component strip and ordered 4-key dict (`base_dir,prompt_json,response_json,meta_json`) unchanged. Only read-only `Path.exists` inside existing finder.

**Wrapper/caller/monkeypatch:** Call `facade.find_llm_run_dir` at invocation, no reverse import, preserve original dict insertion order and Path instances. Leave original SOURCE `llm_artifact_paths` as original-signature thin delegate. Caller imports remain unchanged; TARGET is the single computation owner.

**Normal targeted test:** `tests/test_p15_rf035_llm_run_paths_owner.py`; fake/tmp-only input→expected: tmp reports with missing run→reports/llm/2026-10-30/R/comp; categorized trade_executed/R exists→categorized root; component whitespace trimmed; monkeypatch facade.find_llm_run_dir returning fake Path→ordered dict rooted there. Snapshot exact pre-move result/error and compare SOURCE wrapper and TARGET after MOVE, check call-time monkeypatch and input immutability when applicable. Execute `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_llm_run_paths_owner.py` and record actual exit.

**Safety / delivery / blocked-next:** Only read-only/path/format/CLI-argument computation under temp fixtures; no runtime operation or production artifact mutation. Commit SOURCE + `libs/reporting/llm_artifacts_run_paths.py` + this test only, normal push work/p15-a-reporter-pure-20261021, re-fetch exact remote ref and three blobs. On safety/fixture/credential failure record error and preserved SHA, continue retry any earlier individually BLOCKED safe item, then report remaining blockers.

## KEEP, reserve, final report

KEEP original writer/effect/CLI-main functions and protected operational boundaries. No A/B overlap, no automatic RF DONE, no claims from identical-SHA retests. **RESERVE_VERIFIED=0/6 after consuming the six previously verified candidates**; `RESERVE_NOT_VERIFIED` for the next six until C03 independently checks exact source body, RF ownership, current blob, target 404, caller/patch and safe fixture. Do not self-select a reserve. C03 next source analysis: RF-035 libs/reporting/agent_pipeline_trace.py (read-only report projection functions only); none is a new assigned item.

**Issue #11:** measured START_KST/END_KST/ELAPSED_MIN; canonical/order/owner SHA; A1–A8 each IMPLEMENTED/REMOTE_DONE/BLOCKED; before/after SOURCE blob+LOC, new owner/test blob, normal test command/exit, remote push/ref/blob or exact failure, FIRST_BLOCKER/NEXT. Never claim local-only as delivered.
