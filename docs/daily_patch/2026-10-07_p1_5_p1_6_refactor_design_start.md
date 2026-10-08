# 2026-10-07 P1.5 / P1.6 Refactor Design Start

## Summary

Started the formal design branch for Agentra structural refactoring and orchestration modernization.

This change is documentation/preparation only. No runtime, trading, execution, strategy, LLM, broker, or safety semantics were changed.

## Branch

- Branch: `design/p1.5-p1.6-modernization`
- Created from: `codex/observability-20260824`
- Base SHA at creation: `b67934a5baa95f4d329ccf345c14ed591a126a0f`

## Added design authority

- `docs/refactor/README.md`
- `docs/refactor/p1_5_p1_6_master_plan.md`
- `docs/refactor/p1_5_refactor_constitution.md`
- `docs/refactor/p1_5_strategist_decomposition.md`

## Decisions frozen for planning

- P1.5 is behavior-preserving structural refactoring.
- Each agent should become an explicit, independently callable component with typed input/output boundaries.
- Production topology is unchanged during P1.5.
- LLM decision roles remain Strategist + Reporter only.
- Development milestone names such as M10/M11/M13 are cleanup targets in runtime naming; domain/program IDs such as UEF/Q10/Q12/Q100 remain.
- Test architecture cleanup is performed incrementally with each subsystem.
- Successful test temporary artifacts must be automatically cleaned; failed evidence uses bounded retention.
- Codex Cloud is the implementation + pytest worker.
- Claude Cloud is the independent audit + pytest verifier.
- P1.6 evaluates custom runtime vs LangGraph 1.x vs pydantic-graph only after P1.5 freeze.

## Implementation gate

No P1.5 runtime implementation is authorized by this design branch.

The actual implementation branch must be cut from the future P1.2/P1.3 frozen baseline after:
- P1.2 freeze
- P1.3 freeze
- full regression GREEN
- production-write leakage NONE
- trading-authority leakage NONE
- baseline SHA/tag recorded

## Next

Complete the Strategist deep decomposition and produce the first implementation packet:
- function ownership
- dependency/call map
- state read/write map
- target package tree
- contract design
- naming map
- test relocation map
- Codex implementation prompt
- Claude audit prompt
