"""P1.5.2 R3 evidence tool: pytest plugin recording (name, arg-hash, result-hash) of moved façade functions per test.

Offline only. Run the SAME test list in a baseline tree and a feature tree with
`-p p152_r3_call_recorder` (PYTHONPATH=scripts/refactor), env R3_NAMES (moved-name json) and R3_LOG (output json),
then diff the two logs. R3_KEEP=<n> additionally stores the first n chars of normalised args.
"""
import hashlib, importlib, json, os, re, sys
_P1=re.compile(r"[A-Za-z]:[\\/][^\"'\s,\]\}]*")
_P2=re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?")
_P3=re.compile(r"(pytest-of-[^\/]+|pytest-\d+|test_[A-Za-z0-9_]+\d*)")
def _s(x):
    x=_P1.sub("<PATH>",x)
    x=_P2.sub("<TS>",x)
    return x

NAMES = json.load(open(os.environ["R3_NAMES"], encoding="utf-8"))
LOG = os.environ["R3_LOG"]
CUR = [None]
CALLS = {}
OUT = {}


def norm(o, depth=0, seen=None):
    seen = seen or set()
    if depth > 12:
        return "<deep>"
    if isinstance(o, str):
        return _s(o)
    if o is None or isinstance(o, (bool, int)):
        return o
    if isinstance(o, float):
        return repr(o)
    if id(o) in seen:
        return "<cycle>"
    seen = seen | {id(o)}
    if isinstance(o, dict):
        return {"d": sorted(([repr(norm(k, depth + 1, seen)), norm(v, depth + 1, seen)] for k, v in o.items()), key=lambda x: x[0])}
    if isinstance(o, (list, tuple)):
        return [type(o).__name__] + [norm(v, depth + 1, seen) for v in o]
    if isinstance(o, (set, frozenset)):
        return {"s": sorted(repr(norm(v, depth + 1, seen)) for v in o)}
    return "<%s>" % type(o).__qualname__


def h(o):
    return hashlib.sha256(json.dumps(norm(o), sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:16]


def pytest_configure(config):
    for modname, names in NAMES.items():
        mod = importlib.import_module(modname)
        for n in names:
            orig = getattr(mod, n)

            def make(orig, n, modname):
                def wrapper(*a, **k):
                    rec = CALLS.setdefault(CUR[0], [])
                    ah = h([a, k])
                    try:
                        r = orig(*a, **k)
                    except BaseException as e:  # noqa
                        rec.append([modname.rsplit(".", 1)[-1] + "." + n, ah, "EXC:%s:%s" % (type(e).__name__, str(e)[:80])])
                        raise
                    rec.append([modname.rsplit(".", 1)[-1] + "." + n, ah, h(r)] + ([json.dumps(norm([a,k]),ensure_ascii=False,default=str)[:int(os.environ.get("R3_KEEP","600"))]] if os.environ.get("R3_KEEP") else []))
                    return r
                wrapper.__name__ = orig.__name__
                return wrapper
            setattr(mod, n, make(orig, n, modname))


def pytest_runtest_protocol(item, nextitem):
    CUR[0] = item.nodeid
    return None


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        OUT[report.nodeid] = report.outcome


def pytest_sessionfinish(session, exitstatus):
    json.dump({"outcomes": OUT, "calls": CALLS}, open(LOG, "w", encoding="utf-8"))
