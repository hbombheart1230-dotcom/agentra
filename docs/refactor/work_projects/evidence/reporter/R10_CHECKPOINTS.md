# Reporter R10 checkpoints (issue-ready; no GitHub write access in this session)

## R10-000 — P15-WORK-004 fix (START_SHA 3b549d753f3cebbb2f7d843318e38e494bb698a8)
- REVIEW_ACK P15-WORK-004 (P2): `tests/test_work_reporter_r8_read_via_callback_parity.py`
  - removed `_wallclock_normalized` (blanket regex over the whole JSON); outputs are now compared as RAW bytes.
  - generated timestamps made deterministic by `_freeze_clock`: every loaded libs/graphs module attribute bound to `datetime.datetime` is monkeypatched to a frozen subclass (2026-10-17T09:00:00+00:00) for both BASE and current calls.
  - populated success fixture: `trades/2026-10-17/.../lifecycle/trade_lifecycle.json` + `carryover_exit_index.json`; explicit success arguments for `day`/`*_day`/`symbol` parameters; POSITIVE assertion that `build_daily_trade_index` actually returns the populated trade (exact trade_id list incl. carryover row).
  - negative: changing an input timestamp inside the lifecycle by one minute changes the compared output bytes (asserted); frozen-clock test asserts byte-stable `build_post_exit_shadow_recap` output containing the frozen instant.
- TESTS: parity file 25 PASS (22 moves + set size + 2 new); `-O` for read-contracts + parity + renderer-bytes: see next line in commit.
