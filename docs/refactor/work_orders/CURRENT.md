# ACTIVE — P1.5.2 Reporting façade LOC 010 safe reduction

**State:** LOC_008_CODEX_PASS_WITH_FINDINGS; LOC_010_AUTHORIZED; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.
**ONE active task:** [P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md](P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md).
**Rules:** [COMMON_RULES.md](COMMON_RULES.md).
**Roles:** Claude implements one measured cohesive slice → Codex independently audits pinned SHA → GPT/user decides.
**ONLY refactor branch:** `refactor/p1.5`. No feature/task/ZIP branches. `main` frozen.
**Start HEAD:** `119c68f58cfcd44b64c48ce8383edbc1311b2d5e`. **Audited LOC 008 runtime:** `3d85085011de8ed2cbeb720ddce8e55cf7a60d9d`.
**Safety:** work only in a separate isolated clone, never touch live `C:\Agentra`, Q12 dirty worktrees, broker, real LLM or production report/data.

## LOC 008 audited and accepted WITH FINDINGS
- Independent Codex result (user supplied) **PASS_WITH_FINDINGS** for `3d85085`: nine map use-time tests **55 PASS**, 66 moved-body+ABI+UI-note focused **359 PASS**, selected `p152` **711 PASS / 1 SKIP**; 436 ABI, 66 moved ledger, import/Owner boundaries PASS, isolated write-audit 0.
- Markdown façade **1891 → 1678 physical LOC (-213)**; new cohesive `markdown_clean_dependency_maps.py` **268 LOC**. Three façade sum **4411 → 4198** with all 436 callable definitions retained; no runtime-authority changes.
- Nonblocking: pytest `cache_dir` unknown-option warning (one). No mandatory LOC 008 corrective changes. Codex's narrower 711-test selection and Claude's previously reported 1041-test selection are NOT equivalent coverage claims.
- Evidence: [P15-R3-CODEX-LOC-008-AUDIT-009.md](evidence/P15-R3-CODEX-LOC-008-AUDIT-009.md).

## Next
- **LOC 010 is IMPLEMENTATION-AUTHORIZED** under the single linked task. Continue **maximum meaningful safety-preserving** façade reduction: measure candidate benefit, extract **one** next coherent, highest-value and provably safe domain slice, then stop for Codex audit.
- `SIZE_DEFERRED` is remaining size debt, not an indefinite exemption. Preserve 436 API/monkeypatch use-time behavior and honest LOC after extraction. Never reduce LOC by minification/hidden API magic.

## Still not done
- Real frozen Markdown/JSON/JSONL and LLM call/prompt/retry/timeout parity **BLOCKED / NOT RUN**.
- `controlled_mock_lanes` full-suite test-write isolation **OPEN**; historical isolated full suite 5115 PASS / 35 FAIL / 2 ERROR, 37 failure/error nodes baseline-identical.
- Numbered `bodies_01..05` Owner domain cohesion OPEN; public façade sizes SIZE_DEFERRED (AI 1958, Markdown 1678, Story 562).
- **P1.5.2 final PASS, main merge, live rollout and P1.5.3 NOT AUTHORIZED.**
