# Agentra P1.5 — BATCH02: two substantial independently-owned code work packets

**Status:** `OPERATOR_TASK_INSTRUCTION_AUTHORIZED` (explicit operator: “이어서 작업지시해줘 그럼 CI를 다 하고 해야돼?” on 2026-10-20). **Execution:** The operator's *existing* Windows primary Claude/Codex developer sessions only; GitHub does not start a local CLI. **No new branches, clones, worktrees, daemons, monitors or code workspaces.** Each developer reuses its already-owned `work/p15-*` branch and isolated clean workspace, checks its exact HEAD and reads this work order via fetched `origin/integration/p1.5`. Do NOT merge/rebase the integration docs commit into the developer branch just to read the order. The operator may need to resume an ended CLI manually; never imply GPT has done that.

**Integration docs SHA at order creation:** `8345fdaec4543871b5571d1225fa36aa5f5fb4ca` (documentation only; its five CI workflows were 2 PASS, 3 RUNNING at decision time). The order recording SHA is newer; check its own CI separately. `main` stays untouched. Previous CODE BATCH01 candidates remain separate integration units:
- **CLAUDE_DEV_A** `ad4eed21d8303d4d8cb99f4097b4812cf2522f97` on `work/p15-a-reporter-analysis-projection-20261020`. First Codex review REWORK at `7d647493`; changed `exists()` evaluation order repaired; second peer PASS reported. Two historical Reporter guard tests fail (candidate-only); **NOT INTEGRATION_READY**.
- **CODEX_DEV_B** `c0c3f808967dc921a956d01a879fe489674cad71` on `work/p15-b-operator-live-overview-20261020`. Peer Claude initial+supplemental PASS reported; **INTEGRATION_PENDING**.

## Fundamental CI policy: development does NOT wait for every CI

- **Developer execution can proceed concurrently** with the prior docs-only CI: focused real BASE vs CANDIDATE tests and opposite-CLI independent review are local development gates.
- **Every failed required workflow is a pre-integration triage gate.** A pre-existing red cannot be rebranded PASS; establish whether it applies to the exact changed boundary or to environment/history and resolve the cause. No bypass to meet a deadline. On a docs-only `8345fda` baseline, final acceptance requires its required CI actually finish; new work-order commit CI is separately tracked.
- **Selected code changes are not INTEGRATED** until picked onto `integration/p1.5`, after reconciliation of the paired UI JSON/MD notes, and the appropriate required workflow matrix finishes successfully on **that exact new composed code SHA**. Any full pytest, production goldens, 24 real-data SKIPs, UI visuals and Docker acceptance remain separate later stage gates. No need to rerun entire matrix in every child review.

## Lane A — CLAUDE_DEV_A: Reporter original-contract versioned transition (coherent 60–120-min-class assignment)

**Start exactly from** branch `work/p15-a-reporter-analysis-projection-20261020@ad4eed21d8303d4d8cb99f4097b4812cf2522f97`. Do not discard its peer-PASS production code or rewrite the older 313 historical R7 moves. The blocker is **historical strict inventory/facade restoration contracts vs a legitimately new source owner**. This is not permission to relax arbitrary test or safety oracles.

**New exact allowed modifications (plus the common paired UI notes):**
1. `tests/test_work_reporter_seed_migration.py`
2. `tests/test_shared_reporter_facade_guard.py`
3. `scripts/refactor/reporter_facade_guard.py`
4. `scripts/refactor/shared_role_contracts.py` **only if required for exact Reporter delta**, preserve Monitor/Strategist/Safety unmodified semantics
5. `tests/test_shared_role_contracts.py` **only if needed to test new versioned Reporter contract**
6. NEW `tests/test_p15_reporter_contract_transition.py`
7. `tests/test_p15_reporter_analysis_projection.py` **only to strengthen parity if real gap found**
8. Original A source `libs/reporting/reporter_analysis.py` and `libs/agents/reporter/read_models/analysis_report_projection.py` **only for a concrete peer-identified implementation defect**, not cosmetic cleanup.
9. `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md` (truthful paired note). No other files.

**Multiple linked outcomes / actual implementation scope:**

A1. Reproduce both pre-existing guard failures precisely on A SHA and their PASS behavior at the pinned frozen baseline, using real local Git history (hydrate missing immutable object IDs or report `BLOCKED`, never invent historical bytes). Identify exactly the old Reader directory inventory, R7 AST facade reconstruction, and `shared_role_contracts.verify_runtime` whole-tree scope and any relevant CI consumers. Distinguish currently required contracts from historical stage proofs.

A2. Implement a **versioned, fail-closed incremental Reporter contract**, admitting **only this owner path and function refactor** while keeping old explicit `REGISTRY`, `R4_OWNER_FILES`, R7 `313` movement contract, original SHA-bound code/oracles and all prior forbidden-surface checks effective. Don't make `verify_tree` always succeed, exempt arbitrary `libs/reporting/**` or `libs/agents/**`, or modify safety/error checks. Must reject extra fake Reporter owners, changed original moved-body bytes, facade ABI/helper timing changes, new Broker/LLM/effectful imports, and an unauthorized additional altered source. A local `git diff` with a candidate allowlist must be anchored to a pinned accepted SHA and must reject unexpected runtime files, not merely check broad directory names. If a legacy test cannot safely accept current V2 semantics, provide a distinct strict current-stage test while proving the old historical-stage assertion still runs on its exact original SHA; do not skip/xfail/deselect to get green.

A3. Prove both formerly failing tests or their explicit stage-separated equivalent are green on the actual new A SHA **and** negative mutations fail on normal and `python -O`. Also execute targeted `tests/test_p15_reporter_analysis_projection.py`, `tests/test_reporter_analysis_report.py`, `tests/test_shared_role_contracts.py` when historical blobs present, and relevant patchnote schema/API tests. State what still cannot be run (e.g. missing local history). No full-repo tests or production state writes just for this task.

A4. Implement + test + commit and push the **new** A SHA, then call a **fresh read-only Codex CLI** peer against `ad4eed21..NEW_A_SHA` **and** review the effective aggregate from common BASE; announce actual review request, text findings, owner response and real exit/verdict in the visible primary Claude conversation. On real REWORK, make a new SHA and repeat; no forced second review on PASS. If the global shared-role checker requires a safety-sensitive semantic change that cannot preserve old negative gates, **STOP as BLOCKED** and ask GPT to arbitrate, not silently bypass. Receipt: candidate SHA, exact path diff, guard outcomes, hostile mutation outcomes and peer PASS/REWORK/BLOCKED.

**This task explicitly authorizes the exact guard contract files above for versioned contract maintenance**, not wholesale frozen-oracle relaxation; all old source replay fixtures and trading safety authority remain immutable. Do not claim the A source was integrated merely because its guard candidate locally passes.

## Lane B — CODEX_DEV_B: Operator UI trade-link/index plus run-detail read-only projections (coherent 60–120-min-class assignment)

**Start exactly from** branch `work/p15-b-operator-live-overview-20261020@c0c3f808967dc921a956d01a879fe489674cad71`; preserve BATCH01 `data_access_overview_projection.py` and prior regression proofs. No new B branch.

**New exact allowed modifications (plus paired UI notes):**
1. `apps/operator_ui/data_access_core.py`
2. NEW `apps/operator_ui/data_access_trade_index_projection.py`
3. NEW `apps/operator_ui/data_access_run_detail_projection.py`
4. NEW `tests/test_p15_operator_trade_index_projection.py`
5. NEW `tests/test_p15_operator_run_detail_projection.py`
6. `tests/test_operator_ui.py` and `tests/test_operator_ui_data_access_phase2.py` **only if needed for touched behavior**
7. `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md`.
**No other code/source paths.** In particular never edit A's Reporter files, Monitor's 11 immutable moved-body modules, `graphs/nodes/monitor_node.py`, any real Executor/Supervisor/trading guard, Operator UI cache writers, `_load_operator_brief`, `_load_operator_brief_with_cache`, or existing BATCH01 read-model module.

**Linked substantive outcomes:**

B1. In `_trade_report_index` (original core ~608–835), separate pure linked-run/story-record composition from **file traversal/read/stat/path existence and mtime ordering**. The new owner receives explicit pre-read inputs and preserves the exact original candidate ordering, `lifecycle_bundle` vs `aggregated_execution_bundle` `_path_priority`, `>=` timestamp tie rule, story/run aliases, lifecycle linked run IDs and evidence/health/report metadata paths. No additional disk read/scan, write, or permission to reinterpret Broker/Monitor provenance.

B2. In `load_run_detail` (original core ~2308–2581), separate the already-read event/evidence canonical preference, deterministic decision-trace selection/fallback and 7-role presentation into a pure or effect-free projection. All `_iter_jsonl`, `load_run_canonical_sources`, `load_recent_trades_for_day`, `load_symbol_run_chain`, `_trade_report_meta_for_run` and `_load_operator_brief_with_cache` **remain in caller** at the same effective evaluation points and counts. LLM route, cache/artifact writes and exception timing unchanged. Candidate must preserve public `load_run_detail(config,run_id)` field names, insertion order, full JSON bytes and cold-import/monkeypatch effects.

B3. Add direct comparison to original `c0c3f808` functions with synthetic evidence and safe temporary file fixtures: missing/duplicate run, lifecycle vs aggregate priority, same-timestamp ties, out-of-order events, missing canonical inputs, stale linked reports, absent reporter, NOOP/blocked payload and side-effect ordering. Preserve exact failure-path behavior; hostile negative mutations must fail. No real accounts, broker data, production artifact writes or live LLM.

B4. Run relevant existing Operator UI/core/API offline tests plus new focused tests in normal and `python -O`, commit/push new B SHA and call a **fresh read-only `claude -p`** peer. The primary Codex visible conversation must show questions/results and real REWORK if any; reviewer never writes/recurses. Report changed-path ownership, reader call-order and artifacts parity, residual NOT_RUN, and independent verdict. If dynamic monkeypatch or effect-order equivalence cannot be proven, report BLOCKED instead of moving writers.

## Inter-part and GPT integration sequence (parallel throughput, no premature PASS)

- Both existing primary sessions may execute A/B work **concurrently** while baseline workflow runs finish. Primary CLI's user-visible step narration is required; no extra status tool. A/B code and tests are disjoint other than the **two UI patchnote files**. Each appends its own traceable note; preserve all history; Tech Lead reconstructs entries serially.
- **GPT integration responsibility:** first evaluate BATCH01 B `c0c3f808` for selective pick from its immutable SHA (without accidentally picking in-flight BATCH02 changes); handle conflict-free note append against current integration docs 320. Then assess A and versioned guard candidate, preserving base and original historical contracts. Workflows must run on every **composed integration SHA**; never claim the prior docs SHA CI proves code candidate. Move on to BATCH02 only at their exact peer-PASS SHAs.
- Candidate SHA `PASS` is not `INTEGRATED`; a CI failure must be triaged by exact job and touched contract. Full stage acceptance remains owner-approved. No main push, protected-main promotion, production run, Docker or real trading.
- No forced run duration, artificial reviewer rounds, unapproved new branches/workspaces or unsafe permission flags. If scope completes unexpectedly in <60 minutes, explain actual engineering result and remaining authorized scope, do not create synthetic work.
