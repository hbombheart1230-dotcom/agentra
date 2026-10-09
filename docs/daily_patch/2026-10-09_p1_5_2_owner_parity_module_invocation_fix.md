# P1.5.2 parity gate import-root fix

Failed commit 2261030c2e9f2bb658cdc4e3addb1c18bb806868, run https://github.com/hbombheart1230-dotcom/agentra/actions/runs/37877155363
Original error: ModuleNotFoundError: libs, because running script as file made Python sys.path start in scripts/refactor.
Fix: invoke with python -m scripts.refactor.p152_owner_parity to resolve repo root.
Static parity mapping, LOC caps and runtime remain unchanged. Re-run the same CI.
