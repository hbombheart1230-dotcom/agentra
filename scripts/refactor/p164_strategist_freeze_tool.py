"""T4-C: BASE-frozen deterministic contract for the Strategist node (offline, zero external calls).

Target (record `target`): strategist_node  graphs.nodes.strategist_node.strategist_node(state) -> final State + ordered effects.
The frame LLM entry `_run_strategist_frame_llm`, news collection and the global-sentiment provider are replaced by recording
fakes in scenarios (mock LLM ok/error/timeout/raises/strict, news and global exceptions); baseline records call the real
functions under a scrubbed environment with the network disabled.

  generate <capture.jsonl> <outdir>      freeze BASE (unmodified tree, PYTHONHASHSEED=0)
  compute  <outdir> <sample_mod> <out>   digests of the implementation importable NOW
  verify   <outdir> [sample_mod]         native replay + conservation (golden generated on this OS)
  diagnose <outdir> [n]                  bounded first-difference report

Frozen observable per record: final State (canonical JSON, key order kept), the ordered effect/event list (name + digest of
arguments at call time, including the LLM call count and request payload digests), the exception and returned-object identity.
Strict variant conservation (T4-A.1): inventory re-derived, expected sampled IDs == BASE IDs == FEATURE IDs, manifest totals.
"""
from __future__ import annotations

import contextlib
import copy
import gzip
import hashlib
import importlib
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

# heavy optional libraries are imported BEFORE the replay freezes `datetime`/`time` (their C extensions abort on a
# patched datetime class when first imported lazily inside the frozen window)
for _heavy in ("numpy", "pandas"):
    try:
        importlib.import_module(_heavy)
    except Exception:  # noqa: BLE001
        pass
import p162_scanner_capture_plugin as CAP  # noqa: E402

FROZEN_EPOCH = int(F.FROZEN_BASE.timestamp())
TARGETS = {
    "strategist_node": ("graphs.nodes.strategist_node", "strategist_node", "state"),
}
NODE_MODULE = "graphs.nodes.strategist_node"
EFFECT_FUNCS = ("_emit_strategist_event", "_log_strategist_summary", "_log_strategist_llm_result", "append_decision_trace",
                "record_decision_bridge", "record_raw_input", "write_strategist_artifact", "collect_news_items",
                "compute_global_sentiment_signal", "_load_strategy_memory_advisory", "_load_reporter_feedback_packet",
                "_load_recent_strategy_feedback", "_load_deterministic_read_models", "resolve_fallback_symbols",
                "_run_strategist_frame_llm")
ENV_PREFIXES = ("EXIT_POLICY_", "KIWOOM_", "M22_", "MONITOR_", "OPENING_", "QUANT_", "RISK_", "USE_EXIT_POLICY",
                "SCANNER_", "REPORTS_ROOT", "STRATEGIST_", "COMMANDER_", "LLM_", "OPENROUTER", "OPENAI", "DRY_RUN",
                "NEWS_", "THEME_", "GLOBAL_", "MARKET_", "STRATEGY_", "REPORTER_", "TOP_N", "UNIVERSE_", "CANDIDATE_")
VARIANTS_PER_RECORD = 24
_BS = chr(92)
_PATH_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._:-/<>~" + _BS)
_HEX = frozenset("0123456789abcdef")


def sha(obj) -> str:
    return hashlib.sha256(F.canonical(obj).encode("utf-8")).hexdigest()


def safe(o):
    return CAP._enc(o, "x", [])


def _scrub(o, roots):
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
        self._sink, self._roots = sink, roots

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
    import datetime as _dtmod
    import random
    import socket
    import uuid
    real = _dtmod.datetime
    frozen = _make_frozen_datetime(real)
    _dtmod.datetime = frozen
    orig_connect = socket.socket.connect

    def _no_net(self, *a, **k):
        raise OSError("network disabled during T4-C replay")
    socket.socket.connect = _no_net
    http_guard = []
    try:  # uniform offline answer independent of whether `requests` is installed on the host
        from libs.core import http_client as _hc
        _orig_init = _hc.HttpClient.__init__

        def _no_http(self, *a, **k):
            raise _hc.HttpClientError("offline replay: HttpClient disabled")
        _hc.HttpClient.__init__ = _no_http
        http_guard.append((_hc.HttpClient, _orig_init))
    except Exception:  # noqa: BLE001
        pass
    curl_guard = []
    try:  # curl_cffi (used by yfinance) bypasses the Python socket layer: block its request entry point as well
        from curl_cffi.requests import session as _curl_session
        _orig_req = _curl_session.Session.request

        def _no_curl(self, *a, **k):
            raise OSError("network disabled during T4-C replay")
        _curl_session.Session.request = _no_curl
        curl_guard.append((_curl_session.Session, _orig_req))
    except Exception:  # noqa: BLE001
        pass
    swapped = []
    for name, mod in list(sys.modules.items()):
        if mod is not None and (name.startswith("libs.") or name.startswith("graphs.")) \
                and getattr(mod, "datetime", None) is real:
            mod.datetime = frozen
            swapped.append(mod)
    counter = {"n": 0}
    orig_uuid4 = uuid.uuid4

    def fake_uuid4():
        counter["n"] += 1
        return uuid.UUID(int=counter["n"])
    uuid.uuid4 = fake_uuid4
    rstate = random.getstate()
    random.seed(0)
    real_time = _time.time
    _time.time = lambda: float(FROZEN_EPOCH)
    try:
        yield
    finally:
        _time.time = real_time
        uuid.uuid4 = orig_uuid4
        random.setstate(rstate)
        socket.socket.connect = orig_connect
        for _cls, _req in curl_guard:
            _cls.request = _req
        for _cls, _init in http_guard:
            _cls.__init__ = _init
        _dtmod.datetime = real
        for mod in swapped:
            mod.datetime = real


@contextlib.contextmanager
def _env_scrub(tmp):
    saved = {k: v for k, v in os.environ.items() if k.startswith(ENV_PREFIXES)}
    for k in saved:
        os.environ.pop(k, None)
    os.environ["REPORTS_ROOT"] = "reports"  # relative: resolved in the disposable cwd, keeps ids path independent
    os.environ["OPENING_RANK1_CONTROLLED_PROBE_LOG_ROOT"] = str(tmp / "probe")
    os.environ["OPENING_ALPHA_RANK_OBSERVATION_ROOT"] = str(tmp / "obs")
    os.environ["M22_AUTO_SKILL_RUNNER"] = "0"
    try:
        yield
    finally:
        for k in list(os.environ):
            if k.startswith(ENV_PREFIXES):
                os.environ.pop(k, None)
        os.environ.update(saved)


def _wrap_effects(mod, effects, roots):
    originals = {}
    for name in EFFECT_FUNCS:
        fn = getattr(mod, name, None)
        if not callable(fn):
            continue
        originals[name] = fn

        def make(n, f):
            def w(*a, **k):
                effects.append([n, sha(_scrub(safe([list(a), k]), roots))])
                return f(*a, **k)
            return w
        setattr(mod, name, make(name, fn))
    return originals


_PLAYBOOK_OK = {"playbook": "pullback", "themes": ["AI"], "avoid_themes": ["BIO"], "scanner_bias": "momentum",
                "risk_tone": "neutral", "monitor_guidance": "hold_discipline"}


def _install_injection(nodemod, mode, effects, roots):
    """Recording fakes (zero external calls). Returns a restore callable."""
    saved = {}

    def put(name, fn):
        saved[name] = getattr(nodemod, name, None)
        setattr(nodemod, name, fn)

    def rec(name, a, k):
        effects.append([name, sha(_scrub(safe([list(a), k]), roots))])

    # Offline providers: with mock data present the real functions run; otherwise a deterministic offline answer replaces the
    # live market/news fetch (yfinance), so no replay can reach the network. Same behavior in BASE and FEATURE.
    if mode != "news_raises":
        real_news = getattr(nodemod, "collect_news_items", None)

        def offline_news(symbols, *a, state=None, **k):
            if isinstance(state, dict) and state.get("mock_news_items") is not None and real_news is not None:
                return real_news(symbols, *a, state=state, **k)
            rec("collect_news_items", [symbols, *a], k)
            return {str(s): [] for s in (symbols or [])}
        if real_news is not None:
            put("collect_news_items", offline_news)
    if mode != "global_raises":
        real_global = getattr(nodemod, "compute_global_sentiment_signal", None)

        def offline_global(*a, state=None, **k):
            if isinstance(state, dict) and state.get("mock_global_sentiment") is not None and real_global is not None:
                return real_global(*a, state=state, **k)
            rec("compute_global_sentiment_signal", a, k)
            return nodemod.make_signal(score=0.0, status=nodemod.SIGNAL_STATUS_FALLBACK, source="offline_replay",
                                       reason="network_disabled", ts=FROZEN_EPOCH)
        if real_global is not None:
            put("compute_global_sentiment_signal", offline_global)

    if mode in ("llm_ok", "llm_error", "llm_timeout", "llm_raises", "llm_error_strict"):
        def fake_llm(*a, **k):
            rec("_run_strategist_frame_llm", a, k)
            if mode == "llm_ok":
                return dict(_PLAYBOOK_OK), {"enabled": True, "status": "ok", "model": "mock-model", "latency_ms": 7,
                                            "attempts": 1, "repair_used": False}
            if mode == "llm_raises":
                raise RuntimeError("mock llm client crashed")
            status = "timeout" if mode == "llm_timeout" else "error"
            return {}, {"enabled": True, "status": status, "reason": "mock_" + status, "model": "mock-model",
                        "latency_ms": 15000 if mode == "llm_timeout" else 3, "attempts": 2, "error_type": "MockError",
                        "recovery_method": "deterministic_fallback"}
        put("_run_strategist_frame_llm", fake_llm)
    elif mode == "global_raises":
        def boom_g(*a, **k):
            rec("compute_global_sentiment_signal", a, k)
            raise RuntimeError("mock global sentiment provider failed")
        put("compute_global_sentiment_signal", boom_g)
    elif mode == "news_raises":
        def boom_n(*a, **k):
            rec("collect_news_items", a, k)
            raise RuntimeError("mock news provider failed")
        put("collect_news_items", boom_n)

    def restore():
        for n, f in saved.items():
            if f is not None:
                setattr(nodemod, n, f)
    return restore


def replay(target, inp):
    """inp: {"state": enc} for monitor_node, {"args": enc, "kwargs": enc} for kw targets.
    -> dict(out(encoded result/state), out_sha, effects, effects_sha, exception, returned_is_input, mutated_sha)"""
    modname, attr, kind = TARGETS[target]
    mod = importlib.import_module(modname)
    fn = getattr(mod, attr)
    effects, exc, returned = [], None, None
    tmp = Path(tempfile.mkdtemp(prefix="t4c_replay_"))
    roots = sorted({str(tmp), tmp.as_posix(), str(tmp.resolve()), tmp.resolve().as_posix()}, key=len, reverse=True)
    cwd = os.getcwd()
    nodemod = importlib.import_module(NODE_MODULE)
    saved_time, saved_dt = getattr(nodemod, "time", None), getattr(nodemod, "datetime", None)
    saved_mk = getattr(nodemod, "_make_event_logger", None)
    originals = _wrap_effects(nodemod, effects, roots)
    if kind == "state":
        state = F.decode(inp["state"])
        inject = inp.get("inject") or ""
        if isinstance(state.get("event_logger"), dict) and "__opaque__" in state["event_logger"]:
            state.pop("event_logger")
        call = lambda: fn(state)  # noqa: E731
        inputs_obj = state
    else:
        a, k = F.decode(inp["args"]), F.decode(inp["kwargs"])
        call = lambda: fn(*a, **k)  # noqa: E731
        inputs_obj = [a, k]
    try:
        if saved_time is not None:
            nodemod.time = _TimeShim()
        if saved_dt is not None:
            nodemod.datetime = _make_frozen_datetime(saved_dt)
        if saved_mk is not None:
            nodemod._make_event_logger = lambda s: RecLogger(effects, roots)
        restore_inj = lambda: None  # noqa: E731
        with _env_scrub(tmp), _freeze_globals():
            os.chdir(tmp)
            if kind == "state":
                restore_inj = _install_injection(nodemod, inject, effects, roots)
            try:
                try:
                    returned = call()
                except Exception as e:  # noqa: BLE001
                    exc = {"type": type(e).__name__, "message": str(e)[:200]}
            finally:
                os.chdir(cwd)
                restore_inj()
    finally:
        if saved_time is not None:
            nodemod.time = saved_time
        if saved_dt is not None:
            nodemod.datetime = saved_dt
        if saved_mk is not None:
            nodemod._make_event_logger = saved_mk
        for name, f in originals.items():
            setattr(nodemod, name, f)
        shutil.rmtree(tmp, ignore_errors=True)
    out = _scrub(safe(inputs_obj if kind == "state" else {"result": returned, "inputs": inputs_obj}), roots)
    return {"out": out, "out_sha": sha(out), "effects": effects, "effects_sha": sha(effects), "exception": exc,
            "returned_is_input": (returned is inputs_obj) if kind == "state" else False}


def _variants(target, inp, rid):
    """Deterministic bounded perturbations: key drop/none/empty (State for the node, kwargs for the functions)."""
    kind = TARGETS[target][2]
    base = inp["state"] if kind == "state" else inp["kwargs"]
    keys = [k for k in base if k != "event_logger"]
    cand = []
    for k in keys:
        kinds = ("drop", "none", "empty") if kind == "state" else ("none", "empty")
        for knd in kinds:
            vid = f"{knd}:{k}"
            cand.append((hashlib.sha256((rid + vid).encode()).hexdigest(), vid, knd, k))
    cand.sort()
    res = []
    for _h, vid, knd, k in cand[:VARIANTS_PER_RECORD]:
        d = copy.deepcopy(inp)
        tgt = d["state"] if kind == "state" else d["kwargs"]
        if knd == "drop":
            tgt.pop(k, None)
        elif knd == "none":
            tgt[k] = None
        else:
            v = tgt[k]
            tgt[k] = {} if isinstance(v, dict) else [] if isinstance(v, list) else "" if isinstance(v, str) else \
                (0 if isinstance(v, (int, float)) and not isinstance(v, bool) else None)
        res.append((vid, d))
    return res + _scenarios(target, inp)


def _scenarios(target, inp):
    """Strategist deterministic scenarios built from the captured State (mock LLM / news / global modes)."""
    out = []
    st = inp["state"]
    pol = st.get("policy") if isinstance(st.get("policy"), dict) else {}
    for mode in ("llm_ok", "llm_error", "llm_timeout", "llm_raises", "llm_error_strict"):
        d = copy.deepcopy(inp)
        if not isinstance(d["state"].get("policy"), dict):
            d["state"]["policy"] = {}
        d["state"]["policy"]["strategist_frame_use_llm"] = True
        if mode == "llm_error_strict":
            d["state"]["policy"]["strategist_frame_llm_strict"] = True
        d["inject"] = mode
        out.append((f"scenario:{mode}", d))
    for mode in ("global_raises", "news_raises"):
        d = copy.deepcopy(inp)
        d["inject"] = mode
        if mode == "news_raises":
            if not isinstance(d["state"].get("policy"), dict):
                d["state"]["policy"] = {}
            d["state"]["policy"]["use_news_analysis"] = True
        out.append((f"scenario:{mode}", d))
    cs = st.get("candidate_symbols")
    d = copy.deepcopy(inp)
    d["state"]["candidate_symbols"] = []
    out.append(("scenario:empty_candidates", d))
    if isinstance(cs, list) and cs:
        d = copy.deepcopy(inp)
        d["state"]["candidate_symbols"] = list(cs) + list(cs)
        out.append(("scenario:duplicate_candidates", d))
    d = copy.deepcopy(inp)
    d["state"]["candidate_symbols"] = []
    for key in ("universe", "mock_rank_symbols", "watchlist_symbols"):
        d["state"].pop(key, None)
    out.append(("scenario:fallback_universe", d))
    d = copy.deepcopy(inp)
    d["state"]["policy"] = dict(pol, strategist_frame_use_llm=False, use_news_analysis=True)
    out.append(("scenario:news_analysis_on", d))
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


_BASETEMP = __import__("re").compile(r"^(?:[A-Za-z]:)?[\\/].*?basetemp-\d+[\\/][^\\/]+(?:[\\/](.*))?$")


def relocate(o):
    """Captured absolute pytest tmp paths -> paths relative to the disposable replay cwd (no host writes, portable)."""
    if isinstance(o, str):
        m = _BASETEMP.match(o)
        if m:
            rest = (m.group(1) or "").replace(chr(92), "/")
            return rest or "."
        return o
    if isinstance(o, list):
        return [relocate(x) for x in o]
    if isinstance(o, dict):
        return {relocate(k): relocate(v) for k, v in o.items()}
    return o


def _inp_of(rec):
    return rec["input"]


def generate(capture, outdir, per_target_limit=50):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    recs, seen, counts = [], set(), {}
    for line in Path(capture).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        tgt = r["target"]
        if any(str(x) != "args[].event_logger" for x in r["opaque_paths"]):
            continue  # only the injected event logger (replaced by the recorder) may be opaque
        kind = TARGETS[tgt][2]
        if kind == "state":
            if r["args"] and r["args"][0:1] != [] and len(r["args"]) > 1:
                continue
            inp = {"state": r["args"][0] if r["args"] else r["kwargs"].get("state")}
            if inp["state"] is None:
                continue
            inp = relocate(inp)
        else:
            if r["args"]:
                continue
            inp = {"args": [], "kwargs": r["kwargs"]}
        h = sha([tgt, inp])
        if h in seen or counts.get(tgt, 0) >= per_target_limit:
            continue
        seen.add(h)
        counts[tgt] = counts.get(tgt, 0) + 1
        rid = f"{tgt}#{counts[tgt]:02d}"
        a = replay(tgt, inp)
        b = replay(tgt, inp)
        if a["out_sha"] != b["out_sha"] or a["effects_sha"] != b["effects_sha"]:
            counts[tgt] -= 1
            continue  # not deterministic under the frozen environment: not a usable fixture
        v = {}
        for vid, d in _variants(tgt, inp, rid):
            x = replay(tgt, d)
            v[vid] = [x["out_sha"], x["effects_sha"], x["exception"], x["returned_is_input"]]
        recs.append({"id": rid, "target": tgt, "source_test": r["test"], "input": inp,
                     "bound": platform_bound(inp), "golden": a, "variants": v})
    with gzip.open(outdir / "strategist_golden.json.gz", "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(recs, fh, ensure_ascii=False)
    man = {"records": len(recs), "variants": sum(len(r["variants"]) for r in recs),
           "by_target": {t: sum(1 for r in recs if r["target"] == t) for t in TARGETS},
           "exceptions": sum(1 for r in recs if r["golden"]["exception"]),
           "bound": sum(1 for r in recs if r["bound"]),
           "effects_total": sum(len(r["golden"]["effects"]) for r in recs)}
    (outdir / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    return man


def load(outdir):
    with gzip.open(Path(outdir) / "strategist_golden.json.gz", "rt", encoding="utf-8") as fh:
        return json.load(fh)


def _sampled(rid, vid, mod):
    return mod <= 1 or int(hashlib.sha256((rid + "|" + vid).encode()).hexdigest()[:8], 16) % mod == 0


def compute(outdir, sample_mod=4):
    out = {}
    for rec in load(outdir):
        a = replay(rec["target"], rec["input"])
        v = {}
        for vid, d in _variants(rec["target"], rec["input"], rec["id"]):
            if _sampled(rec["id"], vid, sample_mod):
                x = replay(rec["target"], d)
                v[vid] = [x["out_sha"], x["effects_sha"], x["exception"], x["returned_is_input"]]
        out[rec["id"]] = {"out_sha": a["out_sha"], "out_norm": sha(norm_seps(a["out"])), "out_norm_full": norm_seps(a["out"]),
                          "effects": a["effects"],
                          "effects_sha": a["effects_sha"], "exception": a["exception"],
                          "returned_is_input": a["returned_is_input"], "bound": rec["bound"], "variants": v}
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


# ---- strict variant conservation (T4-A.1 design) --------------------------------------------------------------------
def variant_inventory(rec):
    return [vid for vid, _d in _variants(rec["target"], rec["input"], rec["id"])]


def expected_sample_ids(rec, sample_mod):
    return {vid for vid in variant_inventory(rec) if _sampled(rec["id"], vid, sample_mod)}


def _row_ok(v):
    return (isinstance(v, list) and len(v) == 4 and isinstance(v[0], str) and len(v[0]) == 64 and set(v[0]) <= _HEX
            and isinstance(v[1], str) and len(v[1]) == 64 and set(v[1]) <= _HEX and isinstance(v[3], bool))


def inventory_errors(golden, manifest=None):
    errs, total = [], 0
    ids = [r["id"] for r in golden]
    if len(ids) != len(set(ids)):
        errs.append(("*", "duplicate_record_ids"))
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
            errs.append((rec["id"], "golden_variant_inventory_mismatch", sorted(set(inv) ^ set(got))[:3]))
        for vid, v in got.items():
            if not _row_ok(v):
                errs.append((rec["id"], "golden_variant_row_malformed", vid))
    if manifest is not None:
        if manifest.get("records") != len(golden):
            errs.append(("*", "manifest_record_count"))
        if manifest.get("variants") != total:
            errs.append(("*", "manifest_variant_count"))
    return errs


def _variant_errors(rid, vdict, expected, label):
    if not isinstance(vdict, dict):
        return [(rid, f"{label}_variants_not_a_dict")]
    errs = []
    got = set(vdict)
    if got != expected:
        errs.append((rid, f"{label}_variant_ids_ne_expected_sample",
                     {"missing": sorted(expected - got)[:3], "extra": sorted(got - expected)[:3]}))
    for vid, v in vdict.items():
        if not _row_ok(v):
            errs.append((rid, f"{label}_variant_row_malformed", vid))
    return errs


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
        for k in ("out_sha", "effects_sha"):
            v = e.get(k)
            if not (isinstance(v, str) and len(v) == 64 and set(v) <= _HEX):
                errs.append((r["id"], f"{k}_invalid"))
        if not isinstance(e.get("effects"), list) or not isinstance(e.get("variants"), dict) \
                or not isinstance(e.get("returned_is_input"), bool):
            errs.append((r["id"], "shape_invalid"))
    return errs


def _row(e):
    return [e["out_sha"], e["effects_sha"], e["exception"], e["returned_is_input"]]


def compare_native(golden, computed, sample_mod, manifest=None):
    bad = list(inventory_errors(golden, manifest))
    if bad:
        return bad
    if not isinstance(computed, dict) or set(computed) != {r["id"] for r in golden}:
        return [("*", "computed_record_ids_inconsistent")]
    for rec in golden:
        c, g = computed[rec["id"]], rec["golden"]
        if c["out_sha"] != g["out_sha"]:
            bad.append((rec["id"], "result_or_mutation"))
        if c["effects_sha"] != g["effects_sha"]:
            bad.append((rec["id"], "effects_order_or_args"))
        if c["exception"] != g["exception"]:
            bad.append((rec["id"], "exception"))
        if c["returned_is_input"] != g["returned_is_input"]:
            bad.append((rec["id"], "returned_object_identity"))
        errs = _variant_errors(rec["id"], c.get("variants"), expected_sample_ids(rec, sample_mod), "feature")
        bad.extend(errs)
        if not errs:
            for vid, got in c["variants"].items():
                if rec["variants"][vid] != got:
                    bad.append((rec["id"], "variant", vid))
    return bad


def compare_portable(golden, computed, oracle, sample_mod, manifest=None):
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
        exp = expected_sample_ids(rec, sample_mod)
        errs = _variant_errors(rec["id"], o.get("variants"), exp, "base") + \
            _variant_errors(rec["id"], c.get("variants"), exp, "feature")
        bad.extend(errs)
        if not errs:
            for vid, got in c["variants"].items():
                if o["variants"][vid] != got:
                    bad.append((rec["id"], "variant", vid))
    return bad


def golden_integrity(golden, oracle):
    errors, checked, bound = [], 0, 0
    for rec in golden:
        if rec["bound"]:
            bound += 1
            continue
        checked += 1
        if oracle[rec["id"]]["out_norm"] != sha(norm_seps(rec["golden"]["out"])):
            full = oracle[rec["id"]].get("out_norm_full")
            first = first_diff(norm_seps(rec["golden"]["out"]), full)[:260] if full is not None else ""
            errors.append((rec["id"], "golden_vs_base_host_out", first))
        if [e[0] for e in oracle[rec["id"]]["effects"]] != [e[0] for e in rec["golden"]["effects"]]:
            errors.append((rec["id"], "golden_vs_base_host_effect_names"))
    return errors, checked, bound


def verify(outdir, sample_mod=1):
    golden = load(outdir)
    mf = Path(outdir) / "manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else None
    return compare_native(golden, compute(outdir, sample_mod), sample_mod, manifest)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if os.environ.get("PYTHONHASHSEED") != "0" and cmd in ("generate", "compute", "verify", "diagnose"):
        raise SystemExit("run with PYTHONHASHSEED=0")
    if cmd == "generate":
        print(json.dumps(generate(sys.argv[2], sys.argv[3])))
    elif cmd == "verify":
        b = verify(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        print("MISMATCHES", len(b))
        for x in b[:20]:
            print(x)
        sys.exit(1 if b else 0)
    elif cmd == "compute":
        res = compute(sys.argv[2], int(sys.argv[3]))
        import graphs.nodes.strategist_node as _mn
        Path(sys.argv[4]).write_text(json.dumps({"sample_mod": int(sys.argv[3]),
                                                 "provenance": {"module_file": str(Path(_mn.__file__).resolve()),
                                                                "cwd": os.getcwd(), "python": sys.version.split()[0]},
                                                 "records": res}), encoding="utf-8")
        print("COMPUTED", len(res))
    elif cmd == "diagnose":
        import platform
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        print("CONTEXT", json.dumps({"python": platform.python_version(), "os": platform.platform(),
                                      "tmp": tempfile.gettempdir(), "cwd": os.getcwd()}))
        shown = 0
        for rec in load(sys.argv[2]):
            a = replay(rec["target"], rec["input"])
            g = rec["golden"]
            if a["out_sha"] == g["out_sha"] and a["effects_sha"] == g["effects_sha"]:
                continue
            d = first_diff(a["out"], g["out"])
            ei = next((i for i, (u, v) in enumerate(zip(a["effects"], g["effects"])) if u != v), None)
            print("DIFF", rec["id"], d[:260], "| effects idx", ei, "| exc", a["exception"])
            shown += 1
            if shown >= k:
                break
        print("DIAGNOSE_DONE", shown)
