# Preservation of orphan-prone architecture branch materials — 2026-10-15

**Status:** copied verbatim into the single integration working branch; no P1.6 or P2+ implementation permission.
**Target branch:** `integration/p15-t4-pr5-convergence-20261015`
**Target baseline SHA:** `af848ea29e19c392ddb23adf7d0ad6158ffabaa3`
**Sources:** `design/p1.6-orchestration` (`4a5c9339a2432344ebbfc0d17be4d67363291829`) and `design/p2plus-architecture` (`c7475fa0b72f0c7aed2d8b9129c9c0ca52370ac5`).

Only unique Markdown blobs absent from the integration tree were copied by original Git blob SHA, without reformatting or overwriting existing paths. The source branch's older versions of existing runtime/test/CI/config files were deliberately **not** merged. These historical designs may include superseded branch-governance guidance; CURRENT.md and post-T4 architecture approval gates remain authoritative. No code relocation or order authority change is implied.

| Source | Unique documents | Bytes |
|---|---:|---:|
| `p16` | 9 | 57,220 |
| `p2plus` | 14 | 81,230 |
| **TOTAL** | **23** | **138,450** |

## Files preserved verbatim
- `docs/daily_patch/2026-10-12_p1_6_design_branch_prepared.md` ← `p16`, original Git blob `02acbf3ecbd261ba305d0b2a153636e0496f80bf`
- `docs/daily_patch/2026-10-12_p1_6_detailed_design_completed.md` ← `p16`, original Git blob `74e28c3eb415ea4ed4a9af4c54158dc70681216a`
- `docs/refactor/p1_6/BENCHMARK_AND_GATES.md` ← `p16`, original Git blob `0093174848435a7b1125bf82d3ce4caa495fd5f6`
- `docs/refactor/p1_6/BUILD_PACKETS_AND_TEST_MATRIX.md` ← `p16`, original Git blob `fb87f941aed29f9d23a88081ad4e3aea1f82820b`
- `docs/refactor/p1_6/CODE_AUDIT.md` ← `p16`, original Git blob `3c62658a55da4bd2d6841fe29fe4b5bfcfd29099`
- `docs/refactor/p1_6/IMPLEMENTATION_BLUEPRINT.md` ← `p16`, original Git blob `eeb293536e550fcc3445cd164a338ce03681cc07`
- `docs/refactor/p1_6/MASTER_PLAN.md` ← `p16`, original Git blob `f391d1892eaa50fba5c24b9a2e8bde4c77416180`
- `docs/refactor/p1_6/README.md` ← `p16`, original Git blob `61a168b41ba3cac37f29facedef634da0c500e11`
- `docs/refactor/p1_6/STATE_ROUTING_AND_ENGINE_DESIGN.md` ← `p16`, original Git blob `85e174fcfa7f9abe0cfb2ed50eff8d50115af3d0`
- `docs/architecture/P2_PLUS_ARCHITECTURE_INDEX.md` ← `p2plus`, original Git blob `c0478f3fb1cea182c308fa40af0c83b111476ca7`
- `docs/architecture/p2_plus/00_SYSTEM_ARCHITECTURE.md` ← `p2plus`, original Git blob `ccad87e651fa8aa9d6de537356bf369fffde23b4`
- `docs/architecture/p2_plus/01_DEPENDENCIES_AND_BRANCH_GOVERNANCE.md` ← `p2plus`, original Git blob `8b57ae6a1c11f686a28a3f96cc3ed0ae55204836`
- `docs/architecture/p2_plus/02_CONTRACTS_AND_DATA_LINEAGE.md` ← `p2plus`, original Git blob `0accaa21d2c45c6ad137b1b5bfd4a407194df47d`
- `docs/architecture/p2_plus/OPEN_DECISIONS_AND_TRACEABILITY.md` ← `p2plus`, original Git blob `1874c1af03651b358efafc718b2054652b2b1ab1`
- `docs/architecture/p2_plus/P2_STRATEGY_PROGRAM_INTEGRATION.md` ← `p2plus`, original Git blob `ea36b017e654a096a90e6413d9e518a2e8469d61`
- `docs/architecture/p2_plus/P3_EXECUTION_SAFETY.md` ← `p2plus`, original Git blob `4753e9f609f52f4a1b9fb5778d822c9e84b35de4`
- `docs/architecture/p2_plus/P4_Q100_REPORTER_V2.md` ← `p2plus`, original Git blob `6616deb5ede299e82efae3afdc28a1643ead7aa1`
- `docs/architecture/p2_plus/P5_EVIDENCE_MEMORY.md` ← `p2plus`, original Git blob `c25489916452dccfc5694754d96ae481a04fe784`
- `docs/architecture/p2_plus/P6_SELF_IMPROVEMENT.md` ← `p2plus`, original Git blob `13e6bf8f3ee537fbdb9508be2aeb2cfa375adf5a`
- `docs/architecture/p2_plus/P7_V2_FREEZE.md` ← `p2plus`, original Git blob `1d5d92c3b790e8ddba290cd8f2cd2a47f6c27148`
- `docs/architecture/p2_plus/P8_PAPER_RESEARCH.md` ← `p2plus`, original Git blob `56cfca6a4c1d8bad919ab88055d0112eceacc80c`
- `docs/architecture/p2_plus/README.md` ← `p2plus`, original Git blob `987557756ad41c12e2b181bc4364082011fa96a8`
- `docs/daily_patch/2026-10-12_p2_p8_architecture_branch_prepared.md` ← `p2plus`, original Git blob `ed808fe36c06d01e9e688fd3c3bc098dd457a520`

## Branch deletion restrictions
Until integration CI, independent Codex and user final approval, keep `main` protected and do not delete existing refs. After verified main assimilation, these unique documents will be reachable through main and retiring the two design branches will not lose their original text. Old commits and historic topic branches may additionally be backed up with annotated tags if tooling/permissions allow.
