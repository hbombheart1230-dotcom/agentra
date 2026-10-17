# Reporter — whole-role refactoring project (AUTHORIZED, WORKER_NOT_STARTED)

Assigned implementation: Claude. Independent audit: Codex. Integration/technical judgment: Work. User activation: 2026-10-17 11:09 KST, "진행시켜". Preceding implementation cycle is handed off; its recorded findings remain open. Read ACTIVATION.md before executing. Preparation BASE: d773709ba2f70471fad9badba4f92400f7818319; refresh at activation.

## Outcome and responsibility coverage
One coherent Reporter responsibility surface under the frozen V3 layout, with existing callers and report artifacts preserved. Cover the whole reporting path in the responsibility register: entry/facade -> facts/read model -> evidence/provenance -> narrative/deterministic fallback -> Markdown/JSON/LLM payload formatting -> artifact delivery and feedback seams. Classification is whole-role; relocation is only where semantics and ownership are proven. Eight seed files are the first internal batch, not the project ceiling or completion definition.

| Responsibility / current anchor | Planned treatment |
|---|---|
| Narrative helpers (first four Reporter seed pairs) | Populate `libs/agents/reporter/narrative/` with exact bodies and strict legacy identity shims |
| Read-model helpers (last four seed pairs) | Populate `libs/agents/reporter/read_models/`; controlled_mock_lane_report requires Reporter vs Research disposition first |
| `trade_story_pipeline.py`, `trade_story_pipeline_*`, `reasoning_trace.py` | Reuse existing decomposition; trace only relevant consumers; register pure narrative/evidence owners and mixed facades |
| `trade_read_model.py`, `trade_read_model_parts/`, `trade_memory_surface.py`, `trade_memory_application_surface.py` | Separate pure read projections from truth-source selection, persisted memory and feedback effects; no truth-precedence change |
| `trade_report_ai.py`, `trade_report_ai_compact_input.py`, `trade_report_ai_deterministic.py`, `trade_report_markdown_clean.py`, `trade_report/` | Reuse existing owner/ABI ledgers; identify actual pure role ownership and exact text/payload contracts; retain stable facades where coupled |
| `graphs/nodes/reporter_node.py`, reporter entry/service consumers | Read-only consumer/contract checks; no graph or service rewrite in this draft |
| `live_execution_bundle_runner.py`, `reporter_bundle_runtime_parts/`, report writers/queue/lock and Commander feedback | KEEP_WITH_REASON / SAFETY_LOCK; mock contract coverage, no physical/effect migration |
| `libs/reporting/evaluation/**`, research/backtests/Q10/Q12/UEF | OUT_OF_ROLE or SHARED with exact evidence; no wholesale move for folder symmetry |

All additional owners need exact path/blob/consumer registration under operating rules. Pure Reporter-only owners may enter approved internal batches; ambiguous shared facilities stay where they are with their seam recorded. The target tree remains V3; Work records canonical subpackage choices from actual ownership before worker edits.

## Report proliferation review
Record report kind, producer, UI/API/CLI/scheduler/external consumer, artifact contract, cost and proposed KEEP/CONSOLIDATE/STOP decision. Existing inventory and consumer references are the starting point, not a new global scan. No consumer found is UNVERIFIED until scheduler/external consumption is checked. This structural project does not disable, delete or consolidate live reports. Such behavior/cost changes need a separately named change with consumer evidence and activation; they must not be hidden in byte-identical moves.

## Continuous internal work
1. Refresh the existing inventory's Reporter rows and the eight seed blobs at approved BASE; create full responsibility dispositions and producer-consumer boundary map. Do not re-inventory the repository.
2. Perform seed batch, then approved pure narrative/read-model/formatting owner batches continuously. Each batch has exact pairs, isolated BASE oracle and focused proof; unsafe modules do not block unrelated work.
3. Register all remaining facades, effects, shared owners and Research exclusions, including explicit unresolved work. Propose follow-up scope for genuine decomposition rather than marking all kept code completed.
4. Submit pinned role SHA to Codex. Work serially reconciles shared tests/UI notes and validates combined CI after Monitor integration when applicable.

## Tests and completion evidence
Reuse relevant `test_reporter_node.py`, `test_reporter_service.py`, `test_reporter_agent_trade_entrypoint.py`, `test_reporter_analysis_report.py`, `test_reporter_feedback.py`, `test_reporter_commander_hooks.py`, `test_reporter_script_wrappers.py`, `test_trade_story_pipeline_enrichment.py`, `test_trade_report_ai.py`, `test_trade_report_ai_separated_adapter.py`, `tests/apps/api/test_trade_reports.py`. This is an initial candidate selection, not a claim all gates are enumerated; finalize with actual consumers. Include owner/facade ABI and protected-scope contracts from existing ledgers; Work owns shared gate edits.

Verify UTF-8/Markdown/JSON bytes and line endings, key order, missing-data fallback, exceptions, mutable aliases, source precedence, LLM input/call/retry/timeout contracts with fakes, and absence of new queue/lock/write/feedback effects. Genuine report/LLM parity absent => BLOCKED, not a synthetic substitute.

Role completion requires every identified responsibility dispositioned; approved moves/decompositions done; consumer/ABI/output proof attached; audit P0/P1 closed; protected effect boundaries unchanged; shared UI notes synchronized and combined required CI PASS at final SHA. Unfinished in-scope items keep the role PARTIAL unless reduced scope is explicitly accepted. No main merge or real deployment.

Worker-owned paths: exact approved Reporter legacy/canonical pairs; unique `tests/test_work_reporter_*`, `tests/fixtures/work_reporter/**`, `scripts/refactor/work_reporter_*` if needed, unique Reporter evidence. These are reserved names, not instructions to create empty files. No Monitor/scanner/strategist, graph, config, deployment, shared test/workflow or official note edits.
