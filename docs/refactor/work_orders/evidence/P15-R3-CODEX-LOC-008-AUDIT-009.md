# P15-R3-CODEX-LOC-008-AUDIT-009 — independently reported result

**Source/provenance:** Codex independent audit as pasted by user on 2026-10-12; GPT did not rerun it locally.
**Reviewed implementation SHA:** `3d85085011de8ed2cbeb720ddce8e55cf7a60d9d`.
**Verdict:** **PASS_WITH_FINDINGS**; **no required LOC 008 remediation**.

| Independent check | Reported result |
|---|---|
| 9 dependency-map call-time tests | **55 passed** |
| 66 moved-body + 436 ABI + patch-note core set | **359 passed** |
| All selected `p152` tests | **711 passed / 1 skipped** |
| ABI and moved ledger | **436 PASS; 66 symbols PASS** |
| Markdown public façade | **1891 → 1678 physical LOC, -213** |
| Owner `markdown_clean_dependency_maps.py` | **268 physical LOC** |
| All 9 maps use-time `facade.NAME` | **PASS** |
| Reporting import/Owner boundary | **PASS** |
| Runtime authority changes | **None** |
| Isolated clone write-audit | **0** |
| Pytest warning | One `cache_dir` unknown config option, NONBLOCKING |

The 711-test selected group is **not the same** as the earlier Claude 1041-test selected suite; do not conflate. Codex did not independently run all of Claude's 96,565-call differential in the submitted result; mark that comparison as **Claude evidence only**.

**Residual gates:** genuine frozen reports / LLM parity BLOCKED / NOT RUN; `controlled_mock_lanes` test write isolation OPEN; remaining façade LOC SIZE_DEFERRED and numbered Owner cohesion OPEN. Full native pytest NOT RUN in this audit.

**Decision:** accept only LOC 008 at PASS_WITH_FINDINGS; authorize bounded LOC 010 extraction and new independent audit. **P1.5.2 OPEN, P1.5.3 NOT AUTHORIZED; main unchanged.**
