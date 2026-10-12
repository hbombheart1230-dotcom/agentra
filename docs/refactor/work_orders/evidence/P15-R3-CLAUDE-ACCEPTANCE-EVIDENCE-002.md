# P15-R3-ACCEPTANCE-EVIDENCE-002 — Claude evidence report

Pinned feature: `e41d42d754dba9d538fba0fa2dda969d6ea83f02` (runtime == `321eabb5`; docs-only handoff commits up to `05dbb5f52e5180d54e82391c9b532d6f9f631b59` were the tested tree). Baseline `ba6618d483e6d617f4ee56b2cb5647392c777071`.
All runs: project venv (`C:\Agentra\venv`, Python 3.14.2), scrubbed environment (no credentials, git on PATH), isolated local clones under `C:\AgentraEvidence` (`r3_diff_base`@ba6618d, `r3_diff_feat`@05dbb5f, `r3_full_clone`@05dbb5f). No LLM/broker/Docker/live report access. No runtime Python changed. Raw logs are outside Git; sha256 prefixes below.

## Step 1 — Codex audit provenance (reconciled)
- `C:\AgentraEvidence\p152_r3_audit_focused_e41d42d.log` (sha256 `0c54a9d01a8e86c5…`, UTF-16): `197 passed, 1 skipped in 14.51s`. Audit clone `p152_r3_audit_e41d42d` HEAD == `e41d42d…`, only `branch_output/` untracked. Exact command line is NOT in the log (not independently reproducible as written). Only the 197/1 focused slice has a log; owner-parity/consumer-scan/write-audit/LOC claims have no saved log.
- Earlier full-suite log `p152_full_clone_02d6671.log` stops mid-run at ~50% with no summary (no exit/last-test record).
- Not evidenced by Codex: synthetic differential, entry-vs-use-time binding, naming/responsibility, Story LOC discrepancy → covered below.

## Step 2 — Synthetic differential (baseline vs feature, same fixtures)
Method: pytest plugin `scripts/refactor/p152_r3_call_recorder.py` wraps the 57 moved façade functions and records per test `(name, hash(normalised args), hash(result))` (paths/ISO timestamps normalised; ordered, unicode-safe). Same 51 test files (all p152 + 42 façade-consumer files, incl. LLM-mock/retry/timeout/fallback tests) in both trees.
- Outcomes: 625 passed / 1 skipped in both; per-test outcomes identical.
- Recorded calls: **47,092 vs 47,092; 47,091 identical** args+result hashes. The single difference (`_attach_report_status_matrix` in `test_ai_trade_report_hard_timeout_override_stops_slow_call`) is a wall-clock `latency_ms` field; reproduced as 111 vs 114 on baseline-vs-baseline and 113 vs 103 feature-vs-feature → nondeterministic timing, not a code difference.
- 55/57 moved functions exercised by recorded tests. The remaining two (`_humanize_reporter_pattern`, `resolve_shared_trade_facts`) were compared by direct harness (`p152_r3_seam_challenge.py`): 357 synthetic cases (incl. Korean text/None/dict/list/odd types), results identical in both trees.
- Scope limit: mocks/fixtures only; this is synthetic parity, not real-data parity. Prompt/provider/retry/timeout routing in the LLM path was not moved and its mock-based tests are inside the 47k-call comparison.

## Step 3 — Call-time seam challenge
Harness patches every callable façade global a moved function uses (a) before the call and (b) from inside a callback during the call (3 arg shapes), baseline vs feature.
| Scenario | Result |
|---|---|
| Patched before the call (the supported monkeypatch/test usage) | **identical for all 57** functions |
| Patched from a callback *within* the call | **differs for 36 of 57** (21 identical; 5 have no patchable callable global) |
| Recursion | none of the 57 is self-recursive |
Classification: **FAIL for strict use-time (lazy) equivalence under mid-call mutation**, as predicted (owner binds former façade globals at entry; baseline resolved lazily). Example: `build_trade_story_input_from_bundle` — baseline calls the *new* `build_trade_story_input` after the callback patches it; feature calls the entry-time one. Mitigating facts: no non-test code under `libs/ apps/ scripts/ graphs/` assigns or `setattr`s these three façade modules (grep), so the difference is reachable only by a test/caller that patches a façade global from inside a call. Not accepted silently: decision for GPT/user — accept documented entry-binding, or authorize a follow-up that keeps use-time resolution (e.g. facade-injected thin accessors) in a new implementation task.

## Step 4 — LOC / responsibility
- **Correction:** my evidence 001 listed the Story Owner as 271 LOC; that number came from an aborted first generator pass. Actual `trade_story_facade_r3_parts/bodies_01.py` = **102** physical lines (3 functions; `git show 33031d5 --stat` agrees). All 11 R3 Owners: 102 / 261,252,262,251,63 / 245,252,275,228,84 (<=350).
- `bodies_01..05` are **source-order buckets, not named responsibilities** (e.g. Markdown `bodies_01` mixes renderers, a hold-duration helper and market-context resolution). Compatible with the GPT decision but weak against "meaningful responsibility units". Recommended next slice only if wanted: re-group the 54 moved bodies by domain (render / exit-lifecycle / market-context / reporter-evaluation / provenance / scanner-selection / strategist-refresh) under named modules, same bodies, same gate test. Not done here.

## Step 5 — Full native pytest, one diagnostic run
`python -m pytest -v -p no:cacheprovider -m "not heavy and not docker and not benchmark"` in `r3_full_clone`@05dbb5f: **exit 1, `35 failed, 5115 passed, 27 skipped, 9 deselected, 2 errors in 341.51s`**, summary printed (not terminated; first attempt with a PATH lacking git was aborted by me and discarded, its log is `…_aborted_nogit.log`).
- All 37 failing/error nodes lie in 8 files: `test_uef5_2_historical_recompute` (12F+2E), `test_uef2a_forward_policy_contract` (8), `test_step5b_fix4` (8), `test_uef6c_historical_validation` (2), `test_uef5_1_clean_evidence_registry` (2), `test_uef9_formal_authority` (1), `test_scanner_rank_plumbing_fix` (1), `apps/api/test_isolation::test_api_routes_are_get_only` (1).
- The same 8 files run on baseline `ba6618d` give the **identical 37-node set** (35F+2E): feature adds no failure; **no Reporting/p152/façade test failed**. Out-of-scope API/Scanner/UEF/Step5B, not touched.
- **Write audit fired once** in this host-less clone (no live loops exist there): `CREATED data/logs` → `data/logs/controlled_mock_lanes/2026-10-12/lane_evaluations.json`. This is a test-suite-originated write (`libs/runtime/controlled_mock_lanes/ledger.py` `DEFAULT_ROOT=Path("data/logs/controlled_mock_lanes")` is CWD-relative). The culprit test is NOT identified (targeted run of the 532 tests that mention commander/lane code on baseline created nothing; no more blind reruns). Pre-existing, outside R3 (runtime scope diff is `libs/reporting` only), but it contradicts conftest's comment that such a file can only come from the live host — the exclusion list should not be trusted as "external". Treated as **write-isolation finding, FAIL for a zero-write full-suite gate**; the Reporting-focused runs (focused 810/1 and the 625/1 differential) produced zero writes.

## Step 6 — Real-data provenance gate
Searched only immutable authorized sources: tracked repo files (`git ls-files` patterns for trade_report/llm_trace/before-after/frozen), `C:\AgentraEvidence`, `C:\AgentraWorktrees`. Found only narrative plan/example docs and Codex zips/logs; no genuine historical Markdown/JSON/JSONL pre/post pair and no captured LLM trace. Live `reports/`/`data/` were not read. **BLOCKED / NOT RUN** — nothing fabricated, no gate weakened.

## Gate summary
| Gate | Status |
|---|---|
| 436 ABI / signatures / 57 moved-body AST | PASS (unchanged from 001; re-verified by tests in 810/1 and by the differential run) |
| Synthetic differential | PASS (47,091/47,092 identical; 1 = wall-clock latency; +357 direct cases) |
| Seam: patch before call | PASS (57/57) |
| Seam: patch within call | FAIL for 36/57 — documented entry-binding difference, needs decision |
| Responsibility naming | FINDING (source-order buckets) |
| Full native pytest | COMPLETED: 35F+2E, all identical to baseline and out of scope; 1 write-isolation FINDING |
| Real-data / LLM parity | BLOCKED / NOT RUN |
| Façade LOC | SIZE_DEFERRED (562/1891/1958) |
P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no merge to `refactor/p1.5`/main.

## Log provenance (sha256 prefixes)
`r3_full_pytest_05dbb5f.log` 3333878854f2afc0 · `r3_diff_base.json` bf4aeab4e767c21d · `r3_diff_feat.json` c17b983e33b0ee2e · `r3_harness_base.json` ad487b193208ab1c · `r3_harness_feat.json` 62522b5bc2fd72af · `r3_oos_base.log` 7090d482c3bd3f60 · `r3_bisect_base.log` 3fd066507c43b88e. Tools: `scripts/refactor/p152_r3_call_recorder.py`, `scripts/refactor/p152_r3_seam_challenge.py`; inputs `evidence/p152_r3_moved_{names,free_names}.json`.
