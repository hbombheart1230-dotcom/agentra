"""Generate / verify the T3.5 golden fixtures for `libs/contracts/agent_outputs.py` (offline).

  generate  <capture.jsonl> <outdir>   freeze BASE outputs (run on the unmodified BASE tree)
  verify    <outdir>                    replay on the current tree and compare byte-for-byte (used by the test)

Golden content: for every selected captured input the full canonical output (key order preserved), the builder's
use-time runtime dependency call trace, and the digest of every deterministic variant.
"""
from __future__ import annotations

import collections
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p161_agent_output_freeze as F  # noqa: E402
import p161_agent_output_variants as V  # noqa: E402

BUILDERS = ("build_strategist_output_artifact", "build_scanner_output_artifact", "build_monitor_output_artifact",
            "build_commander_output_artifact", "build_commander_shadow_artifact", "build_supervisor_output_artifact",
            "build_executor_output_artifact")
LIMITS = {"build_strategist_output_artifact": 16, "build_scanner_output_artifact": 20,
          "build_monitor_output_artifact": 22, "build_commander_output_artifact": 46,
          "build_commander_shadow_artifact": 24, "build_supervisor_output_artifact": 10,
          "build_executor_output_artifact": 10}
RUNTIME_DEPS = ("build_entry_blocker_surface", "build_commander_route_observability_surface",
                "build_monitor_no_trade_surface", "build_scanner_monitor_handoff_surface",
                "build_strategist_policy_resolution_surface", "build_monitor_commander_memory_application_trace",
                "build_scanner_commander_memory_application_trace", "build_strategist_explanation_fields",
                "build_strategist_memory_packet_visibility", "kst_day_str", "to_kst")


def digest(obj) -> str:
    return hashlib.sha256(F.canonical(F.encode(obj)).encode("utf-8")).hexdigest()


def _call(ao, name, args, kwargs, trace=None):
    """Run one builder on deep copies under the frozen clock; returns (kind, payload, mutated)."""
    a, k = copy.deepcopy(args), copy.deepcopy(kwargs)
    saved = {}
    if trace is not None:
        for dep in RUNTIME_DEPS:
            orig = getattr(ao, dep)
            saved[dep] = orig

            def make(d, o):
                def w(*x, **y):
                    trace.append(d)
                    return o(*x, **y)
                return w
            setattr(ao, dep, make(dep, orig))
    try:
        with F.frozen_clock(ao):
            try:
                out = getattr(ao, name)(*a, **k)
                kind, payload = "result", out
            except Exception as exc:  # noqa: BLE001 - exceptions are part of the frozen contract
                kind, payload = "exception", {"type": type(exc).__name__, "message": str(exc)[:200]}
    finally:
        for dep, orig in saved.items():
            setattr(ao, dep, orig)
    mutated = F.canonical(F.encode(a)) != F.canonical(F.encode(args)) or F.canonical(F.encode(k)) != F.canonical(F.encode(kwargs))
    return kind, payload, mutated


def _import_ao():
    import libs.contracts.agent_outputs as ao
    return ao


def generate(capture, outdir):
    ao = _import_ao()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    seen, per = set(), collections.Counter()
    base, variants_out, manifest = [], {}, {"records": [], "counts": {}}
    out_seen = collections.defaultdict(set)
    for line in Path(capture).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        b = r["builder"]
        if b not in LIMITS or "exception" in r and False:
            continue
        key = (b, digest([F.decode(r["args"]), F.decode(r["kwargs"])]))
        if key in seen or per[b] >= LIMITS[b]:
            continue
        # prefer diverse outputs for the (numerous) shadow records
        od = digest(r.get("result", r.get("exception")))
        if b == "build_commander_shadow_artifact" and od in out_seen[b]:
            continue
        out_seen[b].add(od)
        seen.add(key)
        per[b] += 1
        args, kwargs = F.decode(r["args"]), F.decode(r["kwargs"])
        trace = []
        kind, payload, mutated = _call(ao, b, args, kwargs, trace)
        rid = f"{b}#{per[b]:02d}"
        base.append({"id": rid, "builder": b, "args": r["args"], "kwargs": r["kwargs"], "kind": kind,
                     "result": F.encode(payload) if kind == "result" else payload, "input_mutated": mutated,
                     "dependency_trace": trace, "source_test": r.get("test", "")})
        vd = {}
        for vid, va, vk in V.variants(b, args, kwargs):
            k2, p2, m2 = _call(ao, b, va, vk)
            vd[vid] = [k2, digest(p2) if k2 == "result" else digest(p2), m2]
        variants_out[rid] = vd
        manifest["records"].append({"id": rid, "source_test": r.get("test", ""), "kind": kind, "variants": len(vd),
                                    "result_digest": digest(payload), "dependency_trace": trace})
    manifest["counts"] = {b: per[b] for b in LIMITS}
    manifest["variant_total"] = sum(len(v) for v in variants_out.values())
    with gzip.open(outdir / "golden_inputs_outputs.json.gz", "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(base, fh, ensure_ascii=False)
    with gzip.open(outdir / "golden_variant_digests.json.gz", "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(variants_out, fh, ensure_ascii=False, sort_keys=True)
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    return manifest


_BS = chr(92)
_PATH_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._:-/" + _BS)


def norm_seps(obj):
    """Portable-replay normalisation (POSIX hosts only, applied SYMMETRICALLY to the committed golden and to the
    replayed output): a path-like string made only of path characters has `\\` read as `/`. The committed golden bytes
    are never modified; nothing but the separator of such strings is considered equal."""
    if isinstance(obj, str):
        if _BS in obj and len(obj) < 400 and set(obj) <= _PATH_CHARS:
            return obj.replace(_BS, "/")
        return obj
    if isinstance(obj, list):
        return [norm_seps(x) for x in obj]
    if isinstance(obj, dict):
        return {norm_seps(k): norm_seps(v) for k, v in obj.items()}
    return obj


def compute_digests(outdir, sample_mod=16, only_builders=None):
    """Digests of what the implementation importable NOW produces for every frozen input (used on the pinned BASE tree
    to obtain platform-correct BASE evidence on a host other than the one that generated the golden files)."""
    ao = _import_ao()
    base, _variants = load(outdir)
    res = {}
    for rec in base:
        if only_builders and rec["builder"] not in only_builders:
            continue
        args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
        trace = []
        kind, payload, mutated = _call(ao, rec["builder"], args, kwargs, trace)
        enc = F.encode(payload) if kind == "result" else payload
        entry = {"kind": kind, "result_norm": hashlib.sha256(F.canonical(norm_seps(enc)).encode()).hexdigest(),
                 "mutated": mutated, "trace": trace, "variants": {}}
        for vid, va, vk in V.variants(rec["builder"], args, kwargs):
            if not _sampled(rec["id"], vid, sample_mod):
                continue
            k2, p2, m2 = _call(ao, rec["builder"], va, vk)
            entry["variants"][vid] = [k2, digest(p2), m2]
        res[rec["id"]] = entry
    return res


def load(outdir):
    outdir = Path(outdir)
    with gzip.open(outdir / "golden_inputs_outputs.json.gz", "rt", encoding="utf-8") as fh:
        base = json.load(fh)
    with gzip.open(outdir / "golden_variant_digests.json.gz", "rt", encoding="utf-8") as fh:
        variants = json.load(fh)
    return base, variants


def _sampled(rid, vid, mod):
    return mod <= 1 or int(hashlib.sha256((rid + "|" + vid).encode()).hexdigest()[:8], 16) % mod == 0


def verify(outdir, only_builders=None, sample_mod=1, portable=False, base_digests=None):
    """Returns a list of mismatch descriptions (empty == byte parity).

    Native mode (default, same platform as the golden): exact committed golden bytes and variant digests.
    Portable mode (golden generated on another OS): outputs are compared with the committed golden after a symmetric
    path-separator normalisation, and variant digests are compared with `base_digests` computed from the PINNED BASE
    tree on this very platform (immutable BASE evidence); input mutation and dependency traces stay exact."""
    ao = _import_ao()
    base, variants = load(outdir)
    bad = []
    for rec in base:
        if only_builders and rec["builder"] not in only_builders:
            continue
        args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
        trace = []
        kind, payload, mutated = _call(ao, rec["builder"], args, kwargs, trace)
        if kind != rec["kind"]:
            bad.append((rec["id"], "kind", kind, rec["kind"]))
            continue
        enc = F.encode(payload) if kind == "result" else payload
        if portable:
            got, want = F.canonical(norm_seps(enc)), F.canonical(norm_seps(rec["result"]))
        else:
            got, want = F.canonical(enc), F.canonical(rec["result"])
        if got != want:
            bad.append((rec["id"], "output_bytes", first_diff(json.loads(got), json.loads(want))))
        if mutated != rec["input_mutated"]:
            bad.append((rec["id"], "input_mutation"))
        if trace != rec["dependency_trace"]:
            bad.append((rec["id"], "dependency_trace", trace, rec["dependency_trace"]))
        for vid, va, vk in V.variants(rec["builder"], args, kwargs):
            if not _sampled(rec["id"], vid, sample_mod):
                continue
            k2, p2, m2 = _call(ao, rec["builder"], va, vk)
            if portable:
                want_v = ((base_digests or {}).get(rec["id"], {}).get("variants") or {}).get(vid)
            else:
                want_v = variants[rec["id"]].get(vid)
            if want_v is None or [k2, digest(p2), m2] != want_v:
                bad.append((rec["id"], "variant", vid))
        if set(variants[rec["id"]]) != {v[0] for v in V.variants(rec["builder"], args, kwargs)}:
            bad.append((rec["id"], "variant_set"))
    return bad


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "generate":
        m = generate(sys.argv[2], sys.argv[3])
        print(json.dumps(m["counts"]), m["variant_total"])
    elif cmd == "compute":
        out = compute_digests(sys.argv[2], sample_mod=int(sys.argv[3]))
        Path(sys.argv[4]).write_text(json.dumps(out), encoding="utf-8")
        print("COMPUTED", len(out))
    elif cmd == "verify":
        b = verify(sys.argv[2], sample_mod=int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        print("MISMATCHES", len(b))
        for x in b[:20]:
            print(x)
        sys.exit(1 if b else 0)
