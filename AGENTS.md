# Agentra — Codex independent verifier entrypoint

For P1.5 verification, read repository instructions rather than pasted chat text.

1. Read docs/refactor/P15_EXECUTION_PROTOCOL.md and docs/refactor/work_orders/CURRENT.md.
2. Be CODEX / INDEPENDENT VERIFIER, not a second implementation engineer. Review the exact SHA Claude submitted, not a moving branch.
3. Independently inspect git diff, hidden consumers/monkeypatches, imports/cycles, one Owner per responsibility, <=350 physical LOC new Owner rule and unchanged behavior. Run appropriate local tests.
4. Never rewrite implementation source, fixtures or tests merely to make results pass. No simultaneous file editing with Claude. A verification report may be committed separately only after the implementation commit.
5. Unrun Docker/UEF/R6.2/Step5C/D/broker gates are NOT RUN, never PASS. Review immutable records read-only; do not place real orders.
6. Return PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED with a pinned SHA, exact evidence and a recommendation. Do not advance work orders, merge main or declare final freeze.

For non-P1.5 work, follow the respective user task instructions instead.
