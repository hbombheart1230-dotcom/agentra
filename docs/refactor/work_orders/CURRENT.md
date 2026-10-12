# ACTIVE — P1.5.2 LOC 008 Codex independent audit

**State:** LOC_008_CLAUDE_SUBMITTED; CODEX_INDEPENDENT_AUDIT_PENDING; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.
**ONE active task:** [P15_R3_CODEX_LOC_008_AUDIT_009.md](P15_R3_CODEX_LOC_008_AUDIT_009.md).
**Next queued, NOT authorized:** [P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md](P15_R3_FACADE_LOC_NEXT_CANDIDATES_010.md).
**Rules:** [COMMON_RULES.md](COMMON_RULES.md).
**Agentra roles:** Claude implements → Codex independently audits → GPT/user decides.
**ONLY refactor branch:** `refactor/p1.5`; `main` frozen. No feature/task/ZIP branches.
**Pinned implementation SHA:** `3d85085011de8ed2cbeb720ddce8e55cf7a60d9d` (previous `6760ab4abaf1a9bc6ec168f6c1daf9a727e19dfb`).
**Safety:** isolated clone ONLY, never test against live `C:\Agentra` or dirty Q12 worktrees; no real orders, LLM, Docker restarts or production file access.

## LOC 008 submitted — not yet independently accepted
- Nine Markdown dependency-map factories moved into one named **268-LOC Owner**; Markdown façade `1,891 → 1,678` (**-213 physical LOC**). AI `1,958`, Story `562`, façade sum `4,411 → 4,198`. Ledger now records 66 moved symbols (57 existing + 9 maps); 436 facade callable declarations kept.
- Claude evidence: [P15-R3-CLAUDE-LOC-008.md](evidence/P15-R3-CLAUDE-LOC-008.md). Claims: baseline differential **96,564/96,565** calls same (1 wall-clock latency); 49,473 map calls across nine factories; focused **1,041 PASS / 1 SKIP**, write audit 0, 436 ABI/cycle/Owner size gates PASS. **Independent Codex audit required**, not a blanket ACCEPTED verdict.
- **SIZE_DEFERRED is unpaid debt, not a waiver to stop shrinking.** Measure & pursue every positive-value, consumer-safe cohesive candidate with use-time facade-global resolution intact, not formatting tricks. Queue 010 only after this audit.
- Prior R3 seam **PASS_WITH_FINDINGS**; Guard 007 **PASS_WITH_FINDINGS**. Invalid live-root comparison excluded.

## Separate unresolved gates
Frozen real Markdown/JSON/JSONL and LLM parity **BLOCKED / NOT RUN**. Full-suite `controlled_mock_lanes` write-isolation OPEN (previous baseline-matched 35F+2E). Numbered Owners `bodies_01..05` cohesion OPEN. **P1.5.2 OPEN**, no `main` merge or P1.5.3.
