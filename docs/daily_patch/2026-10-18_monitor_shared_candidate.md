# Monitor / shared candidate checkpoint

Inputs: Monitor 4bc4250844093050438d8a9c29f5842991ad1c3a; Reporter 443f90362ad5970a4731685311a45e8e0f6b55e4.
359 retained definitions have explicit exclusions with bounded syntactic references, writes and control flow. No runtime/source move. Independent review pending.
Initial sandbox pytest: 24 setup ERROR (WinError 5), not PASS. Retried outside sandbox using isolated TEMP.

Monitor local checkpoint: Windows Python 3.14.2 / FastAPI 0.142.2; 24 PASS in 6.29s, exit 0 (retained exclusions, original scope accounting, M9 persisted/negative tests). Earlier in-flight pre-correction run was interrupted after a retained-count failure; no runtime source changed. Linux 3.12 and hosted CI NOT_RUN. Local safe scope frozen; independent review pending. Next: shared integration.

