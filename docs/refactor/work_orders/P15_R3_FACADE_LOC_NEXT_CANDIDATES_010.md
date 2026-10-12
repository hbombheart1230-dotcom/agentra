# P15-R3-FACADE-LOC-NEXT-CANDIDATES-010 — QUEUED ONLY

**NOT AUTHORIZED for code change until Codex LOC-008 audit and GPT/user stage decision.**
**Direction:** Continue maximum **meaningful, behavior-preserving** reduction of all three Reporting façades on the single `refactor/p1.5` branch. Do not stop merely because `SIZE_DEFERRED` was recorded.
**Current after LOC-008:** AI `1958`, Markdown `1678`, Story `562` = **4198** LOC; 436 façade declarations remain. Original was 18743 LOC.

## Ranked next candidate proposals from Claude's dry-run
- Markdown narrative/translation builders: approximately **93 LOC net** potential reduction (owner 159 LOC)
- AI/Story dependency maps: each approximately **75 LOC** potential, independently verify true net effect/use-time parity
- Markdown memory/policy phase: approximately **65 LOC**, check truth-policy and patch seams carefully
- Markdown numeric/format primitive: approximately **55 LOC**, hot path and many small functions — high behavioral proof burden
- Time/duration: approximately **38 LOC**
Potential numbers are *estimates*, not achieved or approved results.

## Next slice rule
Following independent acceptance of LOC-008, Claude must measure all remaining non-delegating implementation/dependency map functions and choose ONE highest safe cohesive owner-based slice with verified net positive façade reduction, preserving **all 436 current ABI**, dynamic monkeypatch timing, imports, Unicode, LLM prompt/call/timeout/retry and unchanged truth precedence. New Owner ≤350 LOC, no `bodies_06` or giant catchall. Consumer-proven façade symbol retirement is separate P1.5.10 scope.
Record before/after LOC, candidate comparison, exact gate counts and any blocked reasons; Codex audits each pinned SHA. No bulk unsafe refactor, main merge, live-run tests or P1.5.3.

**Separate acceptance debts:** immutable actual report/LLM parity BLOCKED; full-suite `controlled_mock_lanes` test-write finding OPEN; façade LOC targets unmet and existing numbered Owner cohesion OPEN.
