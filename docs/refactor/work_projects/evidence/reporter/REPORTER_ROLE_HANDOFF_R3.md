# Reporter whole-role — R-3 (PARTIAL WITH BLOCKERS; ready for one Codex audit)

BASE d773709. Commits after R-2 (674759c): Phase A+B 984ed99, C1 (news split), C2 9067a5e, Phase E/F evidence (this commit).

## Done
- Phase A: register corrected (two moved modules removed from the OUT_OF_ROLE row).
- Phase B: `trade_report_symbol_metadata` (377) -> `read_models/symbol_metadata_{fallbacks,text,sources,name_inference,resolution}` (43-97 LOC).
- Phase C: `trade_story_pipeline_news` (433) -> `narrative/news_{text,headlines,scanner_contribution}`; `trade_story_pipeline_scanner` (392) -> `narrative/scanner_{basis,selection_trace,evidence_fit}`.
  Tool: `scripts/refactor/work_reporter_split.py` (verbatim line-range copy, per-owner import filtering, import-only facade).
- Phase D: no further movable read-model/evidence owner (see register: T1-gated, I/O-mixed, already relocated).
- Phase E: report inventory extended with deploy/config/.github/apps/script-file grep: only run_ai_trade_report_batch is referenced (CI regression workflows); no in-repo scheduler wiring for any producer, so OS/external scheduling stays UNVERIFIED.
- Phase F: register, notes, handoff updated.

## Equivalence proof
Per decomposition: every BASE top-level definition AST-identical in exactly one owner; the legacy facade has no definitions and re-exports the same objects; owners <=350 LOC; BASE-first replay (archive of d773709 vs FINAL) 2565/2565 identical; earlier fixture prefix (1216 -> 1463 -> 1919 -> 2318) preserved at every step. Late binding: news/scanner bodies call siblings only via `_facade` (trade_story_pipeline), unchanged.
Known surface delta: legacy `trade_story_pipeline_scanner` no longer exposes unused imported helpers `clip/format_pct/safe_float/safe_int` (no importer in repo).

## Tests (Python 3.13.14, local)
Role test 67 PASS (67 PASS under -O). Focused: 1810 PASS (Phase B consumers), 1021 PASS (C1), 1112 PASS (C2: facade symbol ledger/ABI, R3 moved bodies, new-owner dependency gate, T1/T3 gates, story pipeline consumers, trade_report_ai). FAIL: the 4 known shared agent-package equality gates (Work). NOT RUN: tests needing fastapi (operator_ui), hosted CI, full pytest, Python 3.14, real LLM/persisted parity.

## Blockers (Work / separate scope)
Shared-ledger-pinned facades (trade_story_pipeline, trade_report_ai, trade_report_markdown_clean) and T1-gated modules; I/O-mixed oversize modules; controlled_mock_lane_report ownership; truth precedence owners; agent-package registration + CI wiring.

## Resume point
All bulk-approved safe structural work is exhausted under current shared gates. Next: Work updates shared ledgers/allowlist -> then split the pinned facades with the same tool; one Codex audit of the final SHA.
