"""Versioned ownership allowlist of the HYBRID-7 V3 agent packages created by the migration batches.

A new package may appear ONLY by adding an entry here together with the batch's own contract test; the per-batch
discipline tests compare the actual directory set for equality (no unrestricted subset), so a stray package fails."""
AGENT_PACKAGES = {"scanner": "V1-052", "strategist": "S1-057"}
SCANNER_PACKAGES = {"context": "V2-053", "projections": "V3-055", "policy": "V4-056"}
STRATEGIST_PACKAGES = {"context": "S1-057", "output": "S1-057"}


def actual_dirs(path):
    return {p.name for p in path.iterdir() if p.is_dir() and p.name != "__pycache__"}
