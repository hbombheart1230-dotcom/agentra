# 2026-10-08 — P1.5.2 Reporting responsibility-minimal design revision

## Reason
The user reaffirmed the original P1.5 contract: minimum responsibilities in façades and one canonical implementation owner. Existing R2-A/B/C extraction was completed, but façade ownership, remaining compatibility surfaces and test architecture must be assessed before P1.5.2 is accepted as a program batch.

## Source authority
- Original frozen design: docs/refactor/p1_5_reporting_implementation_packet_v1_0.md
- Revised execution guide: docs/refactor/p1_5_reporting_implementation_packet_v1_1.md
- Constitution: docs/refactor/p1_5_refactor_constitution.md
- Current observed implementation: fbfab9b3f56152f08a2ce50e69cc8173496fde7d, not the design-branch runtime tree

## Measured state
| Façade | Pre-refactor LOC | Observed LOC | Original target |
|---|---:|---:|---:|
| trade_report_ai.py | 8,354 | 3,040 | 300–600 |
| trade_report_markdown_clean.py | 5,862 | 3,044 | 300–500 |
| trade_story_pipeline.py | 4,527 | 949 | 250–450 |

R2-A/B/C extraction outcomes are retained as COMPLETE; the target range is a review gate, not justification for unsafe removal of required wrappers. Total 18,743 -> 7,033. The prior 337-test CI and separate 12-test seam/UI check passed; full-suite, independent audit and formal P1.5.2 acceptance are not yet established.

## Revised deliverables
1. Classify each remaining definition as KEEP, MOVE, WRAPPER, DEAD or SAFETY-LOCK with callers, owner and consumer migration evidence.
2. Audit remaining AI/Markdown/Story responsibilities using existing owners rather than duplicate modules.
3. Migrate tests in responsibility-based unit/integration/regression groups without deleting historical regression.
4. Use explicit consumer-backed compatibility exception/handoff to P1.5.10 only where necessary.
5. Verify full pytest/LLM/truth/UEF/authority locks and independent audit before claiming P1.5.2 acceptance.

## Design-only scope
Runtime Python changes: NONE.
Production write/broker operations: NONE.
Existing design v1.0: retained.
P1.5 master stage sequence: unchanged.
UI patch-note canonical pair: append-only revised.
