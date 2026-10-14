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
import os
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


def platform_bound(obj):
    """True when a captured input embeds a Windows drive path string (`C:` + separator): path functions applied to it
    by runtime code (e.g. `Path(x).name`) give different results on a POSIX host, so the committed golden output of such
    a record is only authoritative on the platform that generated it."""
    if isinstance(obj, str):
        return len(obj) > 2 and obj[1] == ":" and obj[0].isalpha() and obj[2] in (_BS, "/")
    if isinstance(obj, dict):
        return any(platform_bound(k) or platform_bound(v) for k, v in obj.items())
    if isinstance(obj, (list, tuple, set, frozenset)):
        return any(platform_bound(x) for x in obj)
    return False


_HEX64 = frozenset("0123456789abcdef")


def exact_sha(enc) -> str:
    """Exact canonical output digest: key order, types, values and path separators all participate."""
    return hashlib.sha256(F.canonical(enc).encode("utf-8")).hexdigest()


def validate_base_digests(golden_records, base_digests):
    """Fail-closed validation of the same-host pinned-BASE evidence. Returns a list of error tuples (empty == valid)."""
    errors = []
    if not isinstance(base_digests, dict):
        return [("*", "base_digests_not_a_dict")]
    gold_ids = [r["id"] for r in golden_records]
    if set(base_digests) != set(gold_ids):
        errors.append(("*", "record_ids_inconsistent",
                       sorted(set(gold_ids) ^ set(base_digests))[:5]))
    for rid in gold_ids:
        e = base_digests.get(rid)
        if not isinstance(e, dict):
            errors.append((rid, "base_record_missing"))
            continue
        sha = e.get("result_sha")
        if not (isinstance(sha, str) and len(sha) == 64 and set(sha) <= _HEX64):
            errors.append((rid, "base_result_sha_invalid"))
        if e.get("kind") not in ("result", "exception"):
            errors.append((rid, "base_kind_invalid"))
        if not isinstance(e.get("trace"), list) or not isinstance(e.get("mutated"), bool) \
                or not isinstance(e.get("variants"), dict) or not isinstance(e.get("bound"), bool):
            errors.append((rid, "base_shape_invalid"))
    return errors


def golden_integrity(golden_records, base_digests):
    """Separate golden-integrity accounting (NOT part of the BASE<->FEATURE oracle). Returns (errors, n_checked,
    n_bound): for non-bound records the committed golden must equal the pinned BASE executed here modulo the symmetric
    path-separator reading; platform-bound records are authoritative only against same-host BASE (not checked here)."""
    errors, checked, bound = [], 0, 0
    for rec in golden_records:
        e = base_digests[rec["id"]]
        if e["bound"]:
            bound += 1
            continue
        checked += 1
        want = hashlib.sha256(F.canonical(norm_seps(rec["result"])).encode("utf-8")).hexdigest()
        if e["result_norm"] != want:
            errors.append((rec["id"], first_diff(e["result_norm_json"], norm_seps(rec["result"]))))
        if e["trace"] != rec["dependency_trace"]:
            errors.append((rec["id"], "dependency_trace"))
    return errors, checked, bound


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
        entry = {"kind": kind, "result_norm_json": norm_seps(enc), "bound": platform_bound([args, kwargs]),
                 "result_sha": hashlib.sha256(F.canonical(enc).encode()).hexdigest(),
                 "result_norm": hashlib.sha256(F.canonical(norm_seps(enc)).encode()).hexdigest(),
                 "mutated": mutated, "trace": trace, "variants": {}}
        for vid, va, vk in V.variants(rec["builder"], args, kwargs):
            if not _sampled(rec["id"], vid, sample_mod):
                continue
            k2, p2, m2 = _call(ao, rec["builder"], va, vk)
            entry["variants"][vid] = [k2, digest(p2), m2]
        res[rec["id"]] = entry
    return res


def first_diff(a, b, path=""):
    """First differing JSON path between two decoded values (diagnostic only; short snippets)."""
    if type(a) is not type(b):
        return f"{path}: type {type(a).__name__} != {type(b).__name__}"
    if isinstance(a, dict):
        ka, kb = list(a), list(b)
        if ka != kb:
            return (f"{path}: keys/order differ: only_a={[k for k in ka if k not in b][:3]} "
                    f"only_b={[k for k in kb if k not in a][:3]}")
        for k in ka:
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return ""
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: len {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return ""
    return "" if a == b else f"{path}: {str(a)[:80]!r} != {str(b)[:80]!r}"


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
    Portable mode (golden generated on another OS): the ORACLE is the pinned BASE tree executed on this very host.
    For EVERY record FEATURE must equal that BASE evidence exactly (canonical output SHA-256 with key order, types,
    values and path separators; exception kind; input mutation; use-time dependency trace) and every sampled variant
    digest must equal BASE's. No normalisation is ever applied to the BASE<->FEATURE comparison. Golden integrity is a
    separate check (`golden_integrity`). Missing or malformed BASE evidence fails closed."""
    ao = _import_ao()
    base, variants = load(outdir)
    bad = []
    if portable:
        sel = [r for r in base if not only_builders or r["builder"] in only_builders]
        bad.extend(validate_base_digests(sel, base_digests))
        if bad:
            return bad
    for rec in base:
        if only_builders and rec["builder"] not in only_builders:
            continue
        args, kwargs = F.decode(rec["args"]), F.decode(rec["kwargs"])
        trace = []
        kind, payload, mutated = _call(ao, rec["builder"], args, kwargs, trace)
        enc = F.encode(payload) if kind == "result" else payload
        if portable:
            ref = base_digests[rec["id"]]
            if kind != ref["kind"]:
                bad.append((rec["id"], "kind", kind, ref["kind"]))
                continue
            if exact_sha(enc) != ref["result_sha"]:
                bad.append((rec["id"], "output_bytes", "FEATURE != pinned BASE on this host (exact canonical SHA-256)"))
            if mutated != ref["mutated"]:
                bad.append((rec["id"], "input_mutation"))
            if trace != ref["trace"]:
                bad.append((rec["id"], "dependency_trace", trace, ref["trace"]))
        else:
            if kind != rec["kind"]:
                bad.append((rec["id"], "kind", kind, rec["kind"]))
                continue
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
                want_v = base_digests[rec["id"]]["variants"].get(vid)
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
        import libs.contracts.agent_outputs as _ao
        prov = {"module_file": str(Path(_ao.__file__).resolve()), "cwd": os.getcwd(), "python": sys.version.split()[0],
                "platform": sys.platform, "agent_outputs_sha256": hashlib.sha256(Path(_ao.__file__).read_bytes()).hexdigest()}
        Path(sys.argv[4]).write_text(json.dumps({"provenance": prov, "records": out}), encoding="utf-8")
        print("COMPUTED", len(out))
    elif cmd == "verify":
        b = verify(sys.argv[2], sample_mod=int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        print("MISMATCHES", len(b))
        for x in b[:20]:
            print(x)
        sys.exit(1 if b else 0)
