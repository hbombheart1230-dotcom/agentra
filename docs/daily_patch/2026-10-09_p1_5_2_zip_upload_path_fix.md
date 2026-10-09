# 2026-10-09 P1.5.2 ZIP upload path fix

Previous run: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/37877680337
All code checks PASS: 38 AST-equal functions, 26 owner modules within <=350 physical LOC, 337 Reporting tests and 12 seam/UI tests. ZIP pack step did create branch_output/p152_refactor_modified_only.zip, but upload-artifact still pointed at the old filename and thus failed.
Change only CI upload path. No changes to runtime Python, validation, Q12, Docker, R6.2 or UEF.
