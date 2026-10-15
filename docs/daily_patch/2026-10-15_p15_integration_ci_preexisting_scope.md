# Integration CI initial run — known Linux test scope
Date: 2026-10-15; integration commit b93218068ef03361a42f2e00bb5eeed658721b50.
Initial cross-branch Reporting compatibility run 38712163372: **346 passed, 2 failed**.
1. `test_patch_notes_json_parses_and_is_internally_consistent` rejected status `in_progress` in the newly appended version. Corrected only that new entry to the accepted `current` enum.
2. `test_operator_brief_input_paths_fallback_to_trade_root_not_reports_dir` fails under Linux for Windows-literal `C:\\repo\\...` paths; preexisting T4 workflow already explicitly deselects the exact test in the Linux Operator UI gate. The integrated Reporting job now uses that same named Linux-only exclusion, retaining the test source and the native Windows T4 replay. **This test is NOT claimed PASS on Linux**. The original behavior is still a P2/inherited environment compatibility item.
No broad skips, code runtime changes, live IO or reduced T4 contract gates.
