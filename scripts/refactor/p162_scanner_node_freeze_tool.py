"""T4-A: BASE-frozen deterministic contract for `graphs/nodes/scanner_node.py::scanner_node` (offline).

  generate <capture.jsonl> <outdir>      freeze BASE (run on the unmodified BASE tree)
  verify   <outdir> [sample_mod]         native replay (golden generated on this OS)
  compute  <outdir> <sample_mod> <out>   digests of the implementation importable NOW (same-host BASE oracle)

A replay executes the REAL scanner node under: a constant clock, scrubbed scanner env knobs, a disposable cwd/reports
root, effect functions wrapped call-through (ordered `effects` evidence: name + digest of the arguments at call time)
and a recording event logger. The frozen observable is: final State (canonical JSON, key order kept), the ordered
effect list, the exception (if any) and whether the returned object is the input State.
"""
from __future__ import annotations

import contextlib
import copy
import gzip
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time as _time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p161_agent_output_freeze as F  # noqa: E402
import p162_scanner_capture_plugin as CAP  # noqa: E402

FROZEN_EPOCH = int(F.FROZEN_BASE.timestamp())
EFFECT_FUNCS = ("_emit_scanner_event", "_log_scanner_summary", "append_decision_trace", "record_decision_bridge",
                "record_raw_input", "write_scanner_artifact", "_remember_selected_symbol", "_maybe_hydrate_scanner_skill_results")
ENV_PREFIXES = ("SCANNER_", "M22_", "TOP_N", "MIN_VOLUME", "MIN_TRADING", "EXCLUDE_", "ENABLE_THEME", "REPORTS_ROOT",
                "KIWOOM_", "STRATEGIST_", "COMMANDER_", "MONITOR_")
VARIANTS_PER_RECORD = 24
_BS = chr(92)
_PATH_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._:-/<>~" + _BS)


def sha(obj) -> str:
    return hashlib.sha256(F.canonical(obj).encode("utf-8")).hexdigest()


def safe(o):
    opaque = []
    return CAP._enc(o, "x", opaque)


def decode(o):
    return F.decode(o)


def _scrub(o, roots):
    """Replace the (random) disposable replay root inside any string by a stable placeholder."""
    if isinstance(o, str):
        for r in roots:
            if r in o:
                o = o.replace(r, "<REPLAY_ROOT>")
        return o
    if isinstance(o, list):
        return [_scrub(x, roots) for x in o]
    if isinstance(o, dict):
        return {_scrub(k, roots): _scrub(v, roots) for k, v in o.items()}
    return o


class RecLogger:
    def __init__(self, sink, roots=()):
        self._sink = sink
        self._roots = roots

    def log(self, *a, **k):
        self._sink.append(["logger.log", sha(_scrub(safe([list(a), k]), self._roots))])

    def __getattr__(self, name):
        def noop(*a, **k):
            self._sink.append([f"logger.{name}", sha(_scrub(safe([list(a), k]), self._roots))])
        return noop


class _TimeShim:
    def __getattr__(self, name):
        return getattr(_time, name)

    @staticmethod
    def time():
        return float(FROZEN_EPOCH)


def _make_frozen_datetime(real):
    class _Meta(type(real)):
        def __instancecheck__(cls, inst):
            return isinstance(inst, real)

        def __subclasscheck__(cls, sub):
            return issubclass(sub, real)

    class FrozenDT(real, metaclass=_Meta):
        @classmethod
        def now(cls, tz=None):
            return F.FROZEN_BASE.astimezone(tz) if tz is not None else F.FROZEN_BASE.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return F.FROZEN_BASE.replace(tzinfo=None)

    return FrozenDT


@contextlib.contextmanager
def _freeze_globals():
    """Constant wall clock for every loaded repo module (also lazily imported ones), deterministic uuid4/random,
    and a network guard."""
    import datetime as _dtmod
    import random
    import socket
    import uuid
    real = _dtmod.datetime
    frozen = _make_frozen_datetime(real)
    _dtmod.datetime = frozen
    orig_connect = socket.socket.connect

    def _no_net(self, *a, **k):
        raise OSError("network disabled during T4-A replay")
    socket.socket.connect = _no_net
    swapped = []
    for name, mod in list(sys.modules.items()):
        if mod is None or not (name.startswith("libs.") or name.startswith("graphs.")):
            continue
        if getattr(mod, "datetime", None) is real:
            mod.datetime = frozen
            swapped.append(mod)
    counter = {"n": 0}
    orig_uuid4 = uuid.uuid4

    def fake_uuid4():
        counter["n"] += 1
        return uuid.UUID(int=counter["n"])
    uuid.uuid4 = fake_uuid4
    state = random.getstate()
    random.seed(0)
    try:
        yield
    finally:
        uuid.uuid4 = orig_uuid4
        random.setstate(state)
        socket.socket.connect = orig_connect
        _dtmod.datetime = real
        for mod in swapped:
            mod.datetime = real


@contextlib.contextmanager
def _env_scrub():
    saved = {k: v for k, v in os.environ.items() if k.startswith(ENV_PREFIXES)}
    for k in saved:
        os.environ.pop(k, None)
    try:
        yield
    finally:
        for k in list(os.environ):
            if k.startswith(ENV_PREFIXES):
                os.environ.pop(k, None)
        os.environ.update(saved)


def replay(state_enc):
    """-> dict(final_state_sha, effects_sha, effects(name list), exception, returned_is_state, state_enc)."""
    import graphs.nodes.scanner_node as sn
    state = decode(state_enc)
    if isinstance(state.get("event_logger"), dict) and "__opaque__" in state["event_logger"]:
        state.pop("event_logger")
    effects = []
    originals = {}
    saved_time, saved_dt, saved_mk = sn.time, sn.datetime, sn._make_event_logger
    tmp = Path(tempfile.mkdtemp(prefix="t4a_replay_"))
    roots = sorted({str(tmp), tmp.as_posix(), str(tmp.resolve()), tmp.resolve().as_posix()}, key=len, reverse=True)
    cwd = os.getcwd()
    exc = None
    returned = None
    try:
        for name in EFFECT_FUNCS:
            fn = getattr(sn, name)
            originals[name] = fn

            def make(n, f):
                def w(*a, **k):
                    effects.append([n, sha(_scrub(safe([list(a), k]), roots))])
                    return f(*a, **k)
                return w
            setattr(sn, name, make(name, fn))
        sn.time = _TimeShim()
        sn.datetime = _make_frozen_datetime(saved_dt)
        sn._make_event_logger = lambda s: RecLogger(effects, roots)
        with _env_scrub(), _freeze_globals():
            os.environ["REPORTS_ROOT"] = str(tmp / "reports")
            os.environ["SCANNER_FEATURE_SEED_WITH_YF"] = "0"  # explicit pins: no network seeding / auto skill hydration
            os.environ["SCANNER_AUTO_SKILL_HYDRATION"] = "0"
            os.chdir(tmp)
            real_time = _time.time
            _time.time = lambda: float(FROZEN_EPOCH)
            try:
                try:
                    returned = sn.scanner_node(state)
                except Exception as e:  # noqa: BLE001 - exceptions are part of the frozen contract
                    exc = {"type": type(e).__name__, "message": str(e)[:200]}
            finally:
                _time.time = real_time
                os.chdir(cwd)
    finally:
        sn.time, sn.datetime, sn._make_event_logger = saved_time, saved_dt, saved_mk
        for name, fn in originals.items():
            setattr(sn, name, fn)
        shutil.rmtree(tmp, ignore_errors=True)
    final = _scrub(safe(state), roots)
    return {"state": final, "state_sha": sha(final), "effects": effects, "effects_sha": sha(effects), "exception": exc,
            "returned_is_state": returned is state}


def _variants(state_enc, rid, *, ids_only=False):
    """Deterministic single-key perturbations (bounded): drop / none / empty of top-level keys, hash-selected."""
    keys = [k for k in state_enc if k != "event_logger"]
    out = []
    for k in keys:
        for kind in ("drop", "none", "empty"):
            vid = f"{kind}:{k}"
            out.append((hashlib.sha256((rid + vid).encode()).hexdigest(), vid, kind, k))
    out.sort()
    res = []
    for _h, vid, kind, k in out[:VARIANTS_PER_RECORD]:
        if ids_only:
            res.append((vid, None))
        else:
            s = copy.deepcopy(state_enc)
            if kind == "drop":
                s.pop(k, None)
            elif kind == "none":
                s[k] = None
            else:
                v = s[k]
                s[k] = {} if isinstance(v, dict) else [] if isinstance(v, list) else "" if isinstance(v, str) else (0 if isinstance(v, (int, float)) and not isinstance(v, bool) else None)
            res.append((vid, s))
    res.extend(_scenarios(state_enc, ids_only=ids_only))
    return res


def _scenarios(state_enc, *, ids_only=False):
    """Deterministic candidate-pool scenarios (ties, rank-1 flip, order, duplicates, single/empty pool)."""
    out = []
    cands = state_enc.get("candidates")
    mock = state_enc.get("mock_scan_results")
    if isinstance(cands, list) and len(cands) >= 2:
        if ids_only:
            out.append(("scenario:reverse_candidates", None))
        else:
            s = copy.deepcopy(state_enc)
            s["candidates"] = list(reversed(cands))
            out.append(("scenario:reverse_candidates", s))
        if ids_only:
            out.append(("scenario:rotate_candidates", None))
        else:
            s = copy.deepcopy(state_enc)
            s["candidates"] = cands[1:] + cands[:1]
            out.append(("scenario:rotate_candidates", s))
        if ids_only:
            out.append(("scenario:duplicate_first_candidate", None))
        else:
            s = copy.deepcopy(state_enc)
            s["candidates"] = cands[:1] + cands
            out.append(("scenario:duplicate_first_candidate", s))
        if ids_only:
            out.append(("scenario:single_candidate", None))
        else:
            s = copy.deepcopy(state_enc)
            s["candidates"] = cands[:1]
            out.append(("scenario:single_candidate", s))
    if isinstance(cands, list):
        if ids_only:
            out.append(("scenario:empty_candidates", None))
        else:
            s = copy.deepcopy(state_enc)
            s["candidates"] = []
            out.append(("scenario:empty_candidates", s))
    if isinstance(mock, dict) and len(mock) >= 2 and all(isinstance(v, dict) for v in mock.values()):
        keys = list(mock)
        if ids_only:
            out.append(("scenario:all_scores_tied", None))
        else:
            s = copy.deepcopy(state_enc)
            first = {k: v for k, v in s["mock_scan_results"][keys[0]].items() if k in ("score", "confidence", "risk_score")}
            for k in keys:
                s["mock_scan_results"][k].update(first)
            out.append(("scenario:all_scores_tied", s))
        if ids_only:
            out.append(("scenario:swap_top_two_scores", None))
        else:
            s = copy.deepcopy(state_enc)
            a, b = s["mock_scan_results"][keys[0]], s["mock_scan_results"][keys[1]]
            for f in ("score", "confidence", "risk_score"):
                if f in a and f in b:
                    a[f], b[f] = b[f], a[f]
            out.append(("scenario:swap_top_two_scores", s))
        if ids_only:
            out.append(("scenario:no_mock_rows", None))
        else:
            s = copy.deepcopy(state_enc)
            s["mock_scan_results"] = {}
            out.append(("scenario:no_mock_rows", s))
    return out


def platform_bound(obj) -> bool:
    if isinstance(obj, str):
        return len(obj) > 2 and obj[1] == ":" and obj[0].isalpha() and obj[2] in (_BS, "/")
    if isinstance(obj, dict):
        return any(platform_bound(k) or platform_bound(v) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return any(platform_bound(x) for x in obj)
    return False


def norm_seps(obj):
    if isinstance(obj, str):
        if _BS in obj and len(obj) < 400 and set(obj) <= _PATH_CHARS:
            return obj.replace(_BS, "/")
        return obj
    if isinstance(obj, list):
        return [norm_seps(x) for x in obj]
    if isinstance(obj, dict):
        return {norm_seps(k): norm_seps(v) for k, v in obj.items()}
    return obj


def generate(capture, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    recs, seen = [], set()
    for line in Path(capture).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["opaque_paths"] or r["args"] or r["kwargs"]:
            continue
        h = sha(r["state"])
        if h in seen:
            continue
        seen.add(h)
        rid = f"scanner_node#{len(recs) + 1:02d}"
        a = replay(r["state"])
        b = replay(r["state"])
        assert a["state_sha"] == b["state_sha"] and a["effects_sha"] == b["effects_sha"], ("non-deterministic replay", rid)
        v = {}
        for vid, s in _variants(r["state"], rid):
            x = replay(s)
            v[vid] = [x["state_sha"], x["effects_sha"], x["exception"], x["returned_is_state"]]
        recs.append({"id": rid, "source_test": r["test"], "state_in": r["state"], "bound": platform_bound(r["state"]),
                     "golden": a, "variants": v})
    with gzip.open(outdir / "scanner_node_golden.json.gz", "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(recs, fh, ensure_ascii=False)
    man = {"records": len(recs), "variants": sum(len(r["variants"]) for r in recs),
           "exceptions": sum(1 for r in recs if r["golden"]["exception"]),
           "bound": sum(1 for r in recs if r["bound"]),
           "effects_total": sum(len(r["golden"]["effects"]) for r in recs),
           "sources": sorted({r["source_test"].split("::")[0] for r in recs})}
    (outdir / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    return man


def load(outdir):
    with gzip.open(Path(outdir) / "scanner_node_golden.json.gz", "rt", encoding="utf-8") as fh:
        return json.load(fh)


def _sampled(rid, vid, mod):
    return mod <= 1 or int(hashlib.sha256((rid + "|" + vid).encode()).hexdigest()[:8], 16) % mod == 0


def compute(outdir, sample_mod=4):
    out = {}
    for rec in load(outdir):
        a = replay(rec["state_in"])
        v = {}
        for vid, s in _variants(rec["state_in"], rec["id"]):
            if _sampled(rec["id"], vid, sample_mod):
                x = replay(s)
                v[vid] = [x["state_sha"], x["effects_sha"], x["exception"], x["returned_is_state"]]
        out[rec["id"]] = {"state_sha": a["state_sha"], "state_norm": sha(norm_seps(a["state"])),
                          "state_norm_json": norm_seps(a["state"]),
                          "effects": a["effects"], "effects_sha": a["effects_sha"], "exception": a["exception"],
                          "returned_is_state": a["returned_is_state"], "bound": rec["bound"], "variants": v}
    return out


def first_diff(a, b, path=""):
    if type(a) is not type(b):
        return f"{path}: type {type(a).__name__} != {type(b).__name__}"
    if isinstance(a, dict):
        if list(a) != list(b):
            return f"{path}: keys/order differ only_a={[k for k in a if k not in b][:3]} only_b={[k for k in b if k not in a][:3]}"
        for k in a:
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


_HEX = frozenset("0123456789abcdef")


def validate_oracle(golden, oracle):
    errs = []
    if not isinstance(oracle, dict):
        return [("*", "oracle_not_dict")]
    if set(oracle) != {r["id"] for r in golden}:
        errs.append(("*", "record_ids_inconsistent"))
    for r in golden:
        e = oracle.get(r["id"])
        if not isinstance(e, dict):
            errs.append((r["id"], "missing"))
            continue
        for k in ("state_sha", "effects_sha"):
            v = e.get(k)
            if not (isinstance(v, str) and len(v) == 64 and set(v) <= _HEX):
                errs.append((r["id"], f"{k}_invalid"))
        if not isinstance(e.get("effects"), list) or not isinstance(e.get("variants"), dict) \
                or not isinstance(e.get("returned_is_state"), bool):
            errs.append((r["id"], "shape_invalid"))
    return errs


def _row(e):
    return [e["state_sha"], e["effects_sha"], e["exception"], e["returned_is_state"]]


def _inventory_ids_safe(value):
    """Fast metadata path only for plain JSON trees; alias/custom inputs use legacy materialization."""
    pending, seen = [value], set()
    while pending:
        obj = pending.pop()
        if type(obj) in (dict, list):
            identity = id(obj)
            if identity in seen:
                return False
            seen.add(identity)
            if type(obj) is dict:
                if any(type(k) is not str for k in obj):
                    return False
                pending.extend(obj.values())
            else:
                pending.extend(obj)
        elif type(obj) not in (str, int, float, bool, type(None)):
            return False
    return True


def variant_inventory(rec):
    value = rec["state_in"]
    fast = type(value) is dict and type(rec["id"]) is str and _inventory_ids_safe(value)
    return [vid for vid, _s in _variants(value, rec["id"], ids_only=fast)]


def expected_sample_ids(rec, sample_mod):
    """IDs that MUST be executed for `sample_mod` (the existing deterministic `_sampled` selection)."""
    return {vid for vid in variant_inventory(rec) if _sampled(rec["id"], vid, sample_mod)}


def _row_ok(v):
    return (isinstance(v, list) and len(v) == 4 and isinstance(v[0], str) and len(v[0]) == 64 and set(v[0]) <= _HEX
            and isinstance(v[1], str) and len(v[1]) == 64 and set(v[1]) <= _HEX and isinstance(v[3], bool))


def inventory_errors(golden, manifest=None):
    """Conservation of the COMMITTED golden: every record's variant ID set equals the deterministic inventory, no
    duplicates, well-formed rows, and (when given) record/variant totals equal the manifest. Independent of sampling."""
    errs = []
    ids = [r["id"] for r in golden]
    if len(ids) != len(set(ids)):
        errs.append(("*", "duplicate_record_ids"))
    total = 0
    for rec in golden:
        inv = variant_inventory(rec)
        if len(inv) != len(set(inv)):
            errs.append((rec["id"], "duplicate_variant_ids_in_inventory"))
        got = rec.get("variants")
        if not isinstance(got, dict):
            errs.append((rec["id"], "variants_not_a_dict"))
            continue
        total += len(got)
        if set(got) != set(inv):
            errs.append((rec["id"], "golden_variant_inventory_mismatch",
                         sorted(set(inv) ^ set(got))[:3]))
        for vid, v in got.items():
            if not _row_ok(v):
                errs.append((rec["id"], "golden_variant_row_malformed", vid))
    if manifest is not None:
        if manifest.get("records") != len(golden):
            errs.append(("*", "manifest_record_count", manifest.get("records"), len(golden)))
        if manifest.get("variants") != total:
            errs.append(("*", "manifest_variant_count", manifest.get("variants"), total))
    return errs


def _computed_variant_errors(rid, vdict, expected, label):
    errs = []
    if not isinstance(vdict, dict):
        return [(rid, f"{label}_variants_not_a_dict")]
    got = set(vdict)
    if got != expected:
        errs.append((rid, f"{label}_variant_ids_ne_expected_sample",
                     {"missing": sorted(expected - got)[:3], "extra": sorted(got - expected)[:3]}))
    for vid, v in vdict.items():
        if not _row_ok(v):
            errs.append((rid, f"{label}_variant_row_malformed", vid))
    return errs


def compare_native(golden, computed, sample_mod, manifest=None):
    """Committed golden (same OS) vs implementation digests (`computed` from `compute` run with `sample_mod`). Exact.
    Variant conservation: the executed ID set must equal the deterministic expected sample (no silent omission), the
    golden inventory must be complete, and manifest totals must match."""
    bad = list(inventory_errors(golden, manifest))
    if bad:
        return bad
    if not isinstance(computed, dict) or set(computed) != {r["id"] for r in golden}:
        return [("*", "computed_record_ids_inconsistent")]
    for rec in golden:
        c = computed[rec["id"]]
        g = rec["golden"]
        if c["state_sha"] != g["state_sha"]:
            bad.append((rec["id"], "final_state"))
        if c["effects_sha"] != g["effects_sha"]:
            bad.append((rec["id"], "effects_order_or_args"))
        if c["exception"] != g["exception"]:
            bad.append((rec["id"], "exception"))
        if c["returned_is_state"] != g["returned_is_state"]:
            bad.append((rec["id"], "returned_object_identity"))
        errs = _computed_variant_errors(rec["id"], c.get("variants"), expected_sample_ids(rec, sample_mod), "feature")
        bad.extend(errs)
        if errs:
            continue
        for vid, got in c["variants"].items():
            if rec["variants"][vid] != got:
                bad.append((rec["id"], "variant", vid))
    return bad


def compare_portable(golden, computed, oracle, sample_mod, manifest=None):
    """Same-host pinned-BASE oracle vs implementation digests, exact for every record and sampled variant (no
    normalisation). The expected sample, the BASE IDs and the FEATURE IDs must be exactly equal; fail closed on
    missing/extra/duplicate/malformed variant or oracle evidence."""
    bad = list(inventory_errors(golden, manifest))
    bad.extend(validate_oracle(golden, oracle))
    if bad:
        return bad
    if not isinstance(computed, dict) or set(computed) != {r["id"] for r in golden}:
        return [("*", "computed_record_ids_inconsistent")]
    for rec in golden:
        c, o = computed[rec["id"]], oracle[rec["id"]]
        if _row(c) != _row(o):
            bad.append((rec["id"], "feature_ne_base_on_this_host"))
        if c["effects"] != o["effects"]:
            bad.append((rec["id"], "effect_order_or_args"))
        expected = expected_sample_ids(rec, sample_mod)
        errs = _computed_variant_errors(rec["id"], o.get("variants"), expected, "base")
        errs += _computed_variant_errors(rec["id"], c.get("variants"), expected, "feature")
        bad.extend(errs)
        if errs:
            continue
        for vid, got in c["variants"].items():
            if o["variants"][vid] != got:
                bad.append((rec["id"], "variant", vid))
    return bad


def golden_integrity(golden, oracle):
    """Separate accounting: non-bound records - committed golden == same-host BASE modulo the symmetric separator
    reading; bound records (Windows drive paths in the captured State) are authoritative only against BASE-here."""
    errors, checked, bound = [], 0, 0
    for rec in golden:
        if rec["bound"]:
            bound += 1
            continue
        checked += 1
        if oracle[rec["id"]]["state_norm"] != sha(norm_seps(rec["golden"]["state"])):
            errors.append((rec["id"], "golden_vs_base_host_state",
                           first_diff(oracle[rec["id"]]["state_norm_json"], norm_seps(rec["golden"]["state"]))[:220]))
        if [e[0] for e in oracle[rec["id"]]["effects"]] != [e[0] for e in rec["golden"]["effects"]]:
            errors.append((rec["id"], "golden_vs_base_host_effect_names"))
    return errors, checked, bound


def verify(outdir, sample_mod=1, portable=False, oracle=None):
    """In-process convenience wrapper (run with PYTHONHASHSEED=0)."""
    golden = load(outdir)
    computed = compute(outdir, sample_mod)
    mf = Path(outdir) / "manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else None
    return (compare_portable(golden, computed, oracle, sample_mod, manifest) if portable
            else compare_native(golden, computed, sample_mod, manifest))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd in ("generate", "compute", "diagnose") and os.environ.get("PYTHONHASHSEED") != "0":
        raise SystemExit("run with PYTHONHASHSEED=0 (BASE scanner ranking depends on string-hash order)")
    if cmd == "generate":
        print(json.dumps(generate(sys.argv[2], sys.argv[3])))
    elif cmd == "verify":
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise SystemExit("run with PYTHONHASHSEED=0 (BASE scanner ranking depends on string-hash order)")
        b = verify(sys.argv[2], sample_mod=int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        print("MISMATCHES", len(b))
        for x in b[:20]:
            print(x)
        sys.exit(1 if b else 0)
    elif cmd == "diagnose":
        import platform
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        print("CONTEXT", json.dumps({"python": platform.python_version(), "os": platform.platform(),
                                      "tmp": tempfile.gettempdir(), "cwd": os.getcwd(),
                                      "hashseed": os.environ.get("PYTHONHASHSEED")}))
        shown = 0
        for rec in load(sys.argv[2]):
            a = replay(rec["state_in"])
            g = rec["golden"]
            if a["state_sha"] == g["state_sha"] and a["effects_sha"] == g["effects_sha"]:
                continue
            d = first_diff(a["state"], g["state"])
            ei = next((i for i, (u, v) in enumerate(zip(a["effects"], g["effects"])) if u != v), None)
            print("DIFF", rec["id"], "state:", d[:260], "| effects first diff idx:", ei,
                  (a["effects"][ei][0] if ei is not None else ""), "| exc:", a["exception"])
            print("   q9_result:", json.dumps((a["state"].get("q9_scanner_snapshot_result") or {}))[:300])
            print("   golden_q9:", json.dumps((g["state"].get("q9_scanner_snapshot_result") or {}))[:200])
            shown += 1
            if shown >= k:
                break
        print("DIAGNOSE_DONE", shown)
    elif cmd == "compute":
        res = compute(sys.argv[2], int(sys.argv[3]))
        import graphs.nodes.scanner_node as _sn
        Path(sys.argv[4]).write_text(json.dumps({"sample_mod": int(sys.argv[3]),
                                                 "provenance": {"module_file": str(Path(_sn.__file__).resolve()),
                                                                 "cwd": os.getcwd(), "python": sys.version.split()[0]},
                                                 "records": res}), encoding="utf-8")
        print("COMPUTED", len(res))
