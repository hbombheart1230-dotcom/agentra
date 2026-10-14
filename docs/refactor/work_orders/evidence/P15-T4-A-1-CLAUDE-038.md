# P15 T4-A.1 — Golden variant conservation closure (Claude)

BASE/review `b06afaa3908cecd03adb9af1aa11e54cf2d566d2` (hosted CI 38561498562 SUCCESS). Codex T4-A verdict **CONDITIONAL_ACCEPT**; T4-B BLOCKED. Scope: the confirmed P1 (golden variant omission false negative), one whitespace cleanup and P2 documentation. No change to Scanner selection/ranking/guard/State/event logic, the four extracted Owners' behavior, Broker/LLM/Supervisor/Executor/Step5C, `main`, live `C:\Agentra`; committed golden fixtures NOT regenerated or modified; sampling algorithm and pinned `PYTHONHASHSEED=0` unchanged.

## 1. P1 — old false negative (reproduced) and repair

**Defect.** `compare_native` iterated only the *computed* variants (`for vid, got in c["variants"].items()`), and `compare_portable` compared only `set(oracle variants) != set(computed variants)`. A variant that was expected for the sample but absent from FEATURE (native) or from both FEATURE and pinned BASE (portable) therefore produced `[]` even though every remaining digest matched. Reproduced by test with the verbatim old logic (`test_variant_conservation_old_false_negative_is_reproduced_and_rejected_by_both_comparators`): old native returns `[]` for an omission; old portable returns `[]` when BASE and FEATURE omit the same ID.

**Repair (`scripts/refactor/p162_scanner_node_freeze_tool.py`).**
* `variant_inventory(rec)` re-derives the COMPLETE variant-ID inventory deterministically from the frozen State (`_variants`), with no sampling; `expected_sample_ids(rec, sample_mod)` applies the unchanged `_sampled()`.
* `inventory_errors(golden, manifest)`: record IDs unique; every record's golden variant ID set equals its derived inventory (no missing/extra), no duplicates, rows well-formed (list of 4, two 64-hex digests, bool); manifest `records`/`variants` equal the fixture totals.
* `compare_native(golden, computed, sample_mod, manifest)`: inventory conserved, computed record-ID set exact, the executed variant-ID set must **equal** the expected sampled set (omission, extra, malformed row, non-dict all fail), digests exact.
* `compare_portable(golden, computed, oracle, sample_mod, manifest)`: expected sampled IDs == pinned-BASE IDs == FEATURE IDs exactly, plus the same inventory/shape checks and exact digest equality; missing/malformed oracle evidence fails closed (existing `validate_oracle`).
* `compute` records `sample_mod` and the test asserts it. The inventory (1,575) and the executed set (sample_mod=4) are deliberately different concepts: the test requires no expected sampled variant to disappear, not that all 1,575 run.

**Negative tests (fast, synthetic from the committed golden; golden files untouched):** missing expected variant in FEATURE (native + portable); missing in pinned BASE; extra unexpected variant (outside the sample, unknown ID, in FEATURE / BASE); equal ID sets with a changed digest; malformed row / non-dict variants; synthetic golden copy missing a variant; record removed/duplicated; manifest `records`/`variants` corrupted; inconsistent computed record set. Omissions are rejected even though every remaining digest matches. Valid complete fixture passes for `sample_mod=4` and `sample_mod=1` (1,575 variants), with 73 records / 1,575 variants preserved.

## 2. Verification

| Item | Result |
|---|---|
| T4-A freeze tests (8) + structural gates (8) | 16 passed |
| Full corpus `verify <fixture> 1` (73 records, all 1,575 variants executed, manifest + inventory checked) | **0 mismatches** |
| Portable mode forced on Windows (pinned BASE `11a11df` executed on the same host; T4-A + T3.5 contract + structural gates) | 34 passed |
| Existing T3.5 contract gates | pass (included above) |
| Whitespace cleanup `ranking_policy_overlay.py` lines 64/103/108 | trailing whitespace removed; `ast.dump` identical before/after (asserted) |
| Golden fixture check | `git diff c8a1131 HEAD -- tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz manifest.json` empty |
| CI accounting | Linux gate step runs the whole freeze file; the Windows native JUnit accounting now requires 8 named tests (3 new) and fails on skip/deselect/missing |

## 3. P2 — cross-seed telemetry (recorded, not changed)

Codex independently ran the 73 BASE States plus 60 tied scenarios under `PYTHONHASHSEED` 0/1/42: rank-1, selected symbol and score changes were **NOT REPRODUCED**; two States (#30, #31) showed element-order differences in `live_equity_symbol_excluded_symbols` and the related event digests. This is pre-existing BASE behavior (string-hash iteration order of a set-derived list), P2. No ranking logic or production hash seed was changed here; no claim is made that trading selection varies with the hash seed. The freeze pins `PYTHONHASHSEED=0` because telemetry/event digests are order-sensitive. A follow-up could sort that list at its producer, which needs its own authorization and parity run.

## 4. Remaining

T4-A.1 IMPLEMENTED / PENDING independent Codex audit. T4-B BLOCKED until ACCEPT. REAL_REPORT_PARITY_BLOCKED OPEN. NTFS mtime causality P2 OPEN. T5 and Wave D NOT STARTED.

## 5. CI

Run **38648709904 on `f6a52ea` SUCCESS**: Linux `regression` (T4-A structural gate + frozen contract with the portable same-host pinned-BASE oracle, T3.5 gates, historical/current gates) and the required `windows-harness-smoke` (native T4-A replay with 8/8 named contract tests accounted as PASSED, P156 containment/security gate unchanged).
