# Reporter R10 checkpoints (issue-ready; no GitHub write access in this session)

## R10-000 — P15-WORK-004 fix (START_SHA 3b549d753f3cebbb2f7d843318e38e494bb698a8)
- REVIEW_ACK P15-WORK-004 (P2): `tests/test_work_reporter_r8_read_via_callback_parity.py`
  - removed `_wallclock_normalized` (blanket regex over the whole JSON); outputs are now compared as RAW bytes.
  - generated timestamps made deterministic by `_freeze_clock`: every loaded libs/graphs module attribute bound to `datetime.datetime` is monkeypatched to a frozen subclass (2026-10-17T09:00:00+00:00) for both BASE and current calls.
  - populated success fixture: `trades/2026-10-17/.../lifecycle/trade_lifecycle.json` + `carryover_exit_index.json`; explicit success arguments for `day`/`*_day`/`symbol` parameters; POSITIVE assertion that `build_daily_trade_index` actually returns the populated trade (exact trade_id list incl. carryover row).
  - negative: changing an input timestamp inside the lifecycle by one minute changes the compared output bytes (asserted); frozen-clock test asserts byte-stable `build_post_exit_shadow_recap` output containing the frozen instant.
- TESTS: parity file 25 PASS (22 moves + set size + 2 new); `-O` for read-contracts + parity + renderer-bytes: see next line in commit.
- R10-000 `-O` (read-contracts + parity + renderer-bytes): 82 PASS.

## R10-001 — R10-A retained I/O contracts (START_SHA adf1a58696e0a49d5f236c224e9fc07119d06580)
- Classification of the 47 RETAIN_FACADE rows (r8_function_triage.json `r10_class`, from AST effect calls + observation): READ_ONLY 34, WRITER 4, CLOCK_LOG_ENV 3, MODULE_IDENTITY 4, REDEFINITION 2. `generate_post_exit_shadow_recap` was triaged READ_ONLY but observed writing into the temp tree -> reclassified WRITER (claim refuted by evidence).
- New `scripts/refactor/work_reporter_contract_runner.py` (fresh interpreter per tree; frozen clock; ordered fs log of open/read/exists/is_dir/iterdir/glob/rglob/write/mkdir/unlink; resulting temp-tree hashes; temp root prefix scrubbed) and `tests/test_work_reporter_r10_retained_io_contracts.py`:
  - READ_ONLY (31 generic + 3 callback readers via hand-written meta fixtures): BASE tree (`git archive d773709 libs graphs`) vs HEAD on the SAME temp tree (valid/Korean/CRLF/malformed/empty/missing/dir inputs, 7 arg sets); equal outcome bytes or exception type+message, equal ordered fs log, temp tree byte-identical after each run.
  - WRITER / CLOCK_LOG_ENV / MODULE_IDENTITY / REDEFINITION (13): each tree runs on a fresh copy of the same pristine tree at the same absolute path; outcomes, fs log and resulting tree hashes equal. Redefinitions: all definitions AST-identical to BASE and the live function is the effective LAST definition.
  - Negatives: reversing jsonl line order in a mutated BASE copy of symbol_trade_report._iter_jsonl -> observation differs; injecting `raise KeyError` into reporter_analysis._read_json -> differs.
  - Fails loudly (no skip) if the pinned BASE commit is absent (CI needs fetch-depth 0).
- Coverage map `r10a_retained_coverage.json`: 47/47 COVERED (relocation NOT authorised for any).
- TESTS: `python -m pytest -q -p no:cacheprovider tests/test_work_reporter_r10_retained_io_contracts.py` -> 53 PASS, 3 SKIP (the 3 callback readers in the generic parametrisation, each asserted to have a dedicated fixture test), exit 0; same under `-O`. Windows Python 3.13.14.
- NEXT_READY: R10-B artifact producer->API fixtures; R10-D read-only map of 21 NEEDS_AUTHORITY.
