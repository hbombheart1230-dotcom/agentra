# 2026-10-15 - Scripts Inventory and Safe Example Relocation

- Classify 212 baseline Scripts files; 216 after adding three canonical examples and one package marker while retaining old entrypoints.
- Move M22 skill flow, M22 hydration graph and M7 dry-run implementation to scripts/examples; old paths remain module/CLI wrappers.
- Business logic unchanged. Only bootstrap path correction (+7/-2) plus wrappers/package marker.
- Related pytest: 20 passed before and after. Offline original CLI: 34 cases; legacy/canonical relocated CLI: 68 equivalent cases, with six explicit clock-only fields normalized.
- Config 8/8 KEEP; YAML/JSON exam manifests differ in report paths and locked keys. Dynamic skills glob remains intact. No deletion, config/strategy/trading policy change or broker order submission.
- Reporting Batch 3 remains paused. Changed code/T4 overlap is zero; the two shared UI patch-note files are explicitly approved append-only exceptions. Existing JSON entries/order and Markdown prefix are preserved; future integration must retain both branches’ histories and check duplicates.
- Full per-file reference evidence and exclusions: docs/refactor/2026-10-15_scripts_config_inventory.json.
- Full report: docs/refactor/2026-10-15_scripts_config_migration.md.
- Final approved publication check: combined targeted pytest **26 passed**, one dependency warning; only the two approved shared changelog paths overlap T4.
