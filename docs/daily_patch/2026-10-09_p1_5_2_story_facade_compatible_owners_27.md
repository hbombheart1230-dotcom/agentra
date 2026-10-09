# P1.5.2 — Story Façade Compatible Owners 27 (2026-10-09)

- Base source SHA: `f381772d2118aca6444108fab429e4a0e0fba056`, current `refactor/p1.5` only.
- Extracted implementation bodies from four existing callable symbols without removing/renaming public function names: `_raw_strategist_evidence`, `_strategist_trace_source`, `_build_strategist_evidence_trace`, `build_filters_human`.
- Strat evidence owner: `libs/reporting/trade_story_facade_parts/strategist_evidence.py`, 103 physical LOC. Filter checklist owner: `libs/reporting/trade_story_facade_parts/filter_checklist.py`, 73 LOC. Each <=350.
- Story façade 948 -> 826 physical LOC. All 45 top-level function declarations remain in same order; 436-symbol three-façade ledger start/end lines refreshed; none designated DEAD.
- Pinned original function AST bodies are checked against moved Owner body suffixes in CI, with synthetic output comparison and call-time monkeypatch alias tests. Static consumer evidence: `build_filters_human` has direct/report consumers, `_build_strategist_evidence_trace` direct test callers. Keep wrappers.
- No trading decisions, original report truth precedence, Supervisor/Executor/Broker, UEF/R6.2, Step5C/D, Docker, Q12, LLM call or file writes touched. Windows real-report/LLM and independent full acceptance NOT RUN; P1.5.2 OPEN.
