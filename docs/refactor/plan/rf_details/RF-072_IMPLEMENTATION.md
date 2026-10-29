# RF-072 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Codex B (tests code only, no oracle edits); peer read-only. 33 exclusive historical paths.

Golden fixture provenance/hash: 33 files; do not regenerate historical expected bytes.

## Callable mapping: KEEP, not MOVE


Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/fixtures/p1_5_p058_repeat_guard/cases.json` | `tests/fixtures/p1_5_p058_repeat_guard/cases.json` | `d39186b00977` / 224767 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_strategist_s1_057/cases.json` | `tests/fixtures/p1_5_strategist_s1_057/cases.json` | `3fdeab76d230` / 130843 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t35_agent_outputs/golden_inputs_outputs.json.gz` | `tests/fixtures/p1_5_t35_agent_outputs/golden_inputs_outputs.json.gz` | `aa8457e0813f` / 1692348 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t35_agent_outputs/golden_variant_digests.json.gz` | `tests/fixtures/p1_5_t35_agent_outputs/golden_variant_digests.json.gz` | `8bdf04b36ffe` / 269312 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t35_agent_outputs/manifest.json` | `tests/fixtures/p1_5_t35_agent_outputs/manifest.json` | `0b1999512f80` / 59851 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t35_agent_outputs/public_surface.json` | `tests/fixtures/p1_5_t35_agent_outputs/public_surface.json` | `2155de0ed4f3` / 1664 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4a_scanner_node/FREEZE_COMMIT.txt` | `tests/fixtures/p1_5_t4a_scanner_node/FREEZE_COMMIT.txt` | `7e7a4483e283` / 41 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4a_scanner_node/manifest.json` | `tests/fixtures/p1_5_t4a_scanner_node/manifest.json` | `0fe7f71e6e37` / 1213 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz` | `tests/fixtures/p1_5_t4a_scanner_node/scanner_node_golden.json.gz` | `226560b5ef6c` / 1136427 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4b_monitor/FREEZE_COMMIT.txt` | `tests/fixtures/p1_5_t4b_monitor/FREEZE_COMMIT.txt` | `19d499e10ea4` / 41 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4b_monitor/manifest.json` | `tests/fixtures/p1_5_t4b_monitor/manifest.json` | `c564630d1b59` / 181 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4b_monitor/monitor_golden.json.gz` | `tests/fixtures/p1_5_t4b_monitor/monitor_golden.json.gz` | `7ff642ddc848` / 3148427 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4c_strategist/FREEZE_COMMIT.txt` | `tests/fixtures/p1_5_t4c_strategist/FREEZE_COMMIT.txt` | `26bae96dc488` / 41 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4c_strategist/manifest.json` | `tests/fixtures/p1_5_t4c_strategist/manifest.json` | `1dcef7695694` / 137 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4c_strategist/strategist_golden.json.gz` | `tests/fixtures/p1_5_t4c_strategist/strategist_golden.json.gz` | `9bbbc2c6f30f` / 1688749 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4d_commander_ui/FREEZE_COMMIT.txt` | `tests/fixtures/p1_5_t4d_commander_ui/FREEZE_COMMIT.txt` | `1549b8fadf69` / 41 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4d_commander_ui/commander_ui_golden.json.gz` | `tests/fixtures/p1_5_t4d_commander_ui/commander_ui_golden.json.gz` | `9a4e917b0ae3` / 2899692 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_t4d_commander_ui/manifest.json` | `tests/fixtures/p1_5_t4d_commander_ui/manifest.json` | `ec4ab7ed8ae9` / 264 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_v1052_candidate_risk/cases.json` | `tests/fixtures/p1_5_v1052_candidate_risk/cases.json` | `465f210b7d48` / 44260 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_v2053_scanner_context/cases.json` | `tests/fixtures/p1_5_v2053_scanner_context/cases.json` | `c532d0a29b6a` / 60936 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_v3055_scanner_projections/cases.json` | `tests/fixtures/p1_5_v3055_scanner_projections/cases.json` | `9fb9d8d7c2bb` / 6512156 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/p1_5_v4056_scanner_policy/cases.json` | `tests/fixtures/p1_5_v4056_scanner_policy/cases.json` | `59e584e6de05` / 191074 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/uef9_synthetic/.gitattributes` | `tests/fixtures/uef9_synthetic/.gitattributes` | `9c18c9ccd2a6` / 32 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/uef9_synthetic/reports_inputs.json` | `tests/fixtures/uef9_synthetic/reports_inputs.json` | `6eca7a1e95ea` / 2290 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/contracts.json` | `tests/fixtures/work_monitor/contracts.json` | `17df032c56a9` / 150031 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m001.json` | `tests/fixtures/work_monitor/m001.json` | `442d1101fcb0` / 26164 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m002.json` | `tests/fixtures/work_monitor/m002.json` | `b861b6cd806a` / 18283 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m003.json` | `tests/fixtures/work_monitor/m003.json` | `47ca612536d3` / 3839 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m004.json` | `tests/fixtures/work_monitor/m004.json` | `a9851ba46015` / 23034 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m005.json` | `tests/fixtures/work_monitor/m005.json` | `2c4a651e9cb2` / 39747 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_monitor/m008.json` | `tests/fixtures/work_monitor/m008.json` | `d14612752d61` / 33345 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_reporter/seed_cases.json.gz` | `tests/fixtures/work_reporter/seed_cases.json.gz` | `a232726dc7be` / 56805 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |
| `tests/fixtures/work_reporter/seed_cases.provenance.json` | `tests/fixtures/work_reporter/seed_cases.provenance.json` | `a7670c232cb3` / 671 | KEEP_GOLDEN_HASH: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
