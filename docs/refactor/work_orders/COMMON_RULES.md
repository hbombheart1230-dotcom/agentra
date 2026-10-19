# Agentra P1.5 — supplementary rules, not a second D00

**Primary rules:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [trading safety](../../ground_rules/AGENT_RULES.md). Do NOT copy contradictory D00 policies here.

- Working integration: `integration/p1.5`; `main` is the existing operations baseline, NOT physically GitHub-protected unless checked. Do not create new developer branches before operator DOC_FREEZE approval.
- Read [CURRENT](CURRENT.md), the latest #20, actual remote SHA and ONLY newly activated role Issue. All 2026-10-12/17 Reporter/Monitor/R3 previous tasks, historical static classifier loops and deleted branches are inert.
- The scoped `a50d6e47` Strategist/Operator UI source changes are already independently audited and selectively integrated; new code work must not restart them.
- Only operator-authorized isolated CLI invocation can run a worker (`claude -p`, `codex exec` where configured); GitHub comments cannot wake terminated processes. Bound calls and retries; fail closed.
- Any approved tracked changes update BOTH UI patch-notes JSON+MD. Changed-files-only ZIP, no secrets/production data. Preserve pinned golden/test/ABI, Step5C/UNKNOWN/UEF; temporary tests isolated with bounded failure retention.
- Auditor gives exact-SHA `PASS / PASS_WITH_FINDINGS / REWORK / BLOCKED`, test evidence and NOT_RUN. No self-audit code write or automatic widening of scope. GPT selectively composes only approved source changes, verifies new HEAD and #20.

Handoff: `TASK | OWNER | BASE_SHA | CHANGED_PATHS | TESTS | SHA_MATCHED_CI | REVIEW_VERDICT | NOT_RUN | NEXT_ACTION`.
