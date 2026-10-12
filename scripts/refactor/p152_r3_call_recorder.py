"""P1.5.2 R3 evidence tool: pytest plugin recording (name, arg-hash, result-hash) of moved façade functions per test.

FAIL-CLOSED (P15-R3-AUDIT-HARNESS-GUARDS-006): requires explicit absolute env R3_ROOT (isolated Git clone), cwd == R3_ROOT,
PYTHONDONTWRITEBYTECODE=1, absolute R3_NAMES (existing input) and R3_LOG (NEW output outside the clone); optional
R3_PROTECTED_ROOTS. `C:\\Agentra` and descendants are always refused. Validation runs at plugin import (pytest
`-p` plugins load before conftest/collection), before any Reporting import. R3_KEEP=<n> stores n chars of normalised args.

    $env:PYTHONDONTWRITEBYTECODE = "1"; $env:PYTHONPATH = "<clone>\\scripts\\refactor"
    $env:R3_ROOT = "<clone>"; $env:R3_NAMES = "<abs json>"; $env:R3_LOG = "<abs NEW json outside clone>"
    Set-Location <clone>; python -B -m pytest -p p152_r3_call_recorder -p no:cacheprovider <tests>
"""
import hashlib, importlib, json, os, re, sys

# ---------------------------------------------------------------------------------------------
# Fail-closed root/path guard (P15-R3-AUDIT-HARNESS-GUARDS-006). IDENTICAL in the seam script and
# the recorder plugin (tests/test_p152_r3_harness_guards.py asserts they behave the same).
# Pure lexical checks run BEFORE any filesystem access; the live checkout is never stat'ed/listed.
# ---------------------------------------------------------------------------------------------
import ntpath
import stat as _stat

LIVE_ROOT = "C:\\Agentra"
_SHORT_NAME = re.compile(r"^[^.]{1,8}~\d+(\..*)?$")


class GuardError(Exception):
    """Raised before any production import, pytest collection or output open."""


def _strip_prefix(p):
    for pre in ("\\\\?\\UNC\\", "\\\\?\\", "\\\\.\\", "\\??\\"):
        if p.startswith(pre):
            return ("\\\\" + p[len(pre):]) if pre.endswith("UNC\\") else p[len(pre):]
    return p


def _lex(p, pm=os.path):
    """Lexical, case-normalised, separator-normalised form. No filesystem access."""
    if pm is ntpath:
        p = _strip_prefix(p)
    return pm.normcase(pm.normpath(p))


def _is_under(child, parent, sep):
    return child == parent or child.startswith(parent.rstrip(sep) + sep)


def _require_absolute(value, label, pm=os.path):
    if not isinstance(value, str) or not value.strip():
        raise GuardError("%s must be an explicit absolute path (missing/empty)" % label)
    if "\x00" in value:
        raise GuardError("%s contains NUL" % label)
    if pm is ntpath:
        drive, rest = ntpath.splitdrive(_strip_prefix(value))
        if not drive or not rest.startswith(("\\", "/")):
            raise GuardError("%s must be an absolute path with a drive/UNC root: %r" % (label, value))
    elif not pm.isabs(value):
        raise GuardError("%s must be an absolute path: %r" % (label, value))
    parts = re.split(r"[\\/]+", value)
    if ".." in parts:
        raise GuardError("%s must not contain '..' components: %r" % (label, value))
    for part in parts:
        if _SHORT_NAME.match(part):
            raise GuardError("%s contains an ambiguous 8.3 short-name component %r" % (label, part))
    return value


def _protected_forms(extra, pm):
    forms = {_lex(LIVE_ROOT, ntpath)}
    for item in list(extra or ()):  # LIVE_ROOT is a Windows path string: always handled lexically via ntpath above
        _require_absolute(item, "protected root", pm)
        forms.add(_lex(item, pm))
        forms.add(_lex(item, ntpath))
    return forms


def _check_not_protected(value, label, protected, pm, allow_ancestor=False):
    cand = {_lex(value, pm), _lex(value, ntpath)}
    for c in cand:
        for prot in protected:
            for sep in ("\\", "/"):
                if _is_under(c, prot, sep):
                    raise GuardError("%s is the protected live root or inside it: %r" % (label, value))
                if not allow_ancestor and _is_under(prot, c, sep):
                    raise GuardError("%s contains a protected live root: %r" % (label, value))


def _reject_reparse_components(path, label, fs=os, pm=os.path):
    """lstat every component of an already-lexically-cleared path; reject symlink/junction/reparse."""
    path = pm.normpath(path)
    drive, rest = pm.splitdrive(path)
    cur = drive + (pm.sep if rest.startswith(pm.sep) else "")
    for part in [x for x in rest.split(pm.sep) if x]:
        cur = pm.join(cur, part)
        try:
            st = fs.lstat(cur)
        except OSError as exc:
            raise GuardError("%s component not accessible (%s): %r" % (label, exc.__class__.__name__, cur))
        if _stat.S_ISLNK(st.st_mode) or (getattr(st, "st_file_attributes", 0) & 0x400):
            raise GuardError("%s traverses a symlink/junction/reparse point: %r" % (label, cur))


def validate_environment(root, cwd, env, inputs, outputs, extra_protected=(), pm=os.path, fs=os):
    """Return normalised config or raise GuardError. Order: lexical (no fs) -> cwd -> env -> fs on non-live paths."""
    protected = _protected_forms(extra_protected, pm)
    # 1. lexical checks only (never touches the live tree)
    _require_absolute(root, "--root/R3_ROOT", pm)
    _check_not_protected(root, "root", protected, pm)
    _require_absolute(cwd, "process cwd", pm)
    if _lex(cwd, pm) != _lex(root, pm):
        raise GuardError("process cwd must equal the supplied root (cwd=%r root=%r)" % (cwd, root))
    flag = (env or {}).get("PYTHONDONTWRITEBYTECODE", "")
    if flag.strip() not in ("1", "true", "True", "yes"):
        raise GuardError("PYTHONDONTWRITEBYTECODE=1 must be set before starting Python")
    norm_in, norm_out = {}, {}
    for label, value in list(inputs.items()) + list(outputs.items()):
        _require_absolute(value, label, pm)
        _check_not_protected(value, label, protected, pm, allow_ancestor=True)
    lroot = _lex(root, pm)
    for label, value in outputs.items():
        if _is_under(_lex(value, pm), lroot, pm.sep):
            raise GuardError("%s must be outside the audited root: %r" % (label, value))
    seen = {}
    for label, value in list(inputs.items()) + list(outputs.items()):
        k = _lex(value, pm)
        if k in seen:
            raise GuardError("%s collides with %s (input overwrite/duplicate path)" % (label, seen[k]))
        seen[k] = label
    # 2. filesystem checks, only on paths already proven non-live
    _reject_reparse_components(root, "root", fs, pm)
    git = pm.join(root, ".git")
    if not fs.path.isdir(git) or fs.path.islink(git) or not fs.path.isfile(pm.join(git, "HEAD")):
        raise GuardError("root must be an isolated, separate Git clone (a real .git directory with HEAD): %r" % root)
    for label, value in inputs.items():
        _reject_reparse_components(value, label, fs, pm)
        if not fs.path.isfile(value):
            raise GuardError("%s must be an existing file: %r" % (label, value))
        norm_in[label] = pm.normpath(value)
    for label, value in outputs.items():
        parent = pm.dirname(value)
        _reject_reparse_components(parent, label + " parent", fs, pm)
        if not fs.path.isdir(parent):
            raise GuardError("%s parent directory must exist: %r" % (label, parent))
        if fs.path.lexists(value):
            raise GuardError("%s already exists (refusing to overwrite): %r" % (label, value))
        norm_out[label] = pm.normpath(value)
    return {"root": pm.normpath(root), "inputs": norm_in, "outputs": norm_out}


def _extra_protected_from_env(env):
    raw = (env or {}).get("R3_PROTECTED_ROOTS", "")
    return [x for x in raw.split(os.pathsep) if x.strip()]
# ---------------------------------------------------------------------------------------------

_P1=re.compile(r"[A-Za-z]:[\\/][^\"'\s,\]\}]*")
_P2=re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}[:-]\d{2}[:-]\d{2}(\.\d+|-\d{2}-\d{2})?(Z|[+-]\d{2}:?\d{2})?")
_P3=re.compile(r"(pytest-of-[^\/]+|pytest-\d+|test_[A-Za-z0-9_]+\d*)")
_P4=re.compile(r"[0-9a-f]{20,64}")
def _s(x):
    x=_P1.sub("<PATH>",x)
    x=_P2.sub("<TS>",x)
    x=_P4.sub("<HEX>",x)
    return x

NAMES = {}
LOG = None
_ACTIVE = False
CUR = [None]
CALLS = {}
OUT = {}


def norm(o, depth=0, seen=None):
    seen = seen or set()
    if depth > 12:
        return "<deep>"
    if isinstance(o, str):
        return _s(o)
    if isinstance(o, bool) or o is None:
        return o
    if isinstance(o, (int, float)):
        # wall-clock epochs (seconds / milliseconds) are run-specific, not behaviour
        if 1.4e9 <= o <= 2.2e9:
            return "<EPOCH>"
        if 1.4e12 <= o <= 2.2e12:
            return "<EPOCH_MS>"
        return o if isinstance(o, int) else repr(o)
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
    if not _ACTIVE:
        return
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
    if not _ACTIVE:
        return None
    CUR[0] = item.nodeid
    return None


def pytest_runtest_logreport(report):
    if not _ACTIVE:
        return
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        OUT[report.nodeid] = report.outcome


def pytest_sessionfinish(session, exitstatus):
    if not _ACTIVE:
        return
    with open(LOG, "x", encoding="utf-8") as fh:
        json.dump({"outcomes": OUT, "calls": CALLS}, fh)


def activate(env=None, cwd=None, pm=os.path, fs=os):
    """Validate (fail-closed) and arm the plugin. Called at import unless R3_RECORDER_INERT=1 (tests only:
    the plugin then stays inert -- no wrapping, no output)."""
    global NAMES, LOG, _ACTIVE
    env = os.environ if env is None else env
    cfg = validate_environment(
        env.get("R3_ROOT", ""), os.getcwd() if cwd is None else cwd, env,
        inputs={"R3_NAMES": env.get("R3_NAMES", "")}, outputs={"R3_LOG": env.get("R3_LOG", "")},
        extra_protected=_extra_protected_from_env(env), pm=pm, fs=fs,
    )
    sys.path.insert(0, cfg["root"])
    with open(cfg["inputs"]["R3_NAMES"], encoding="utf-8") as fh:
        NAMES = json.load(fh)
    LOG = cfg["outputs"]["R3_LOG"]
    _ACTIVE = True
    return cfg


if os.environ.get("R3_RECORDER_INERT") != "1":
    try:
        activate()
    except GuardError as _exc:  # fail before conftest import / collection / any production import
        import pytest

        raise pytest.UsageError("R3-GUARD-FAIL: %s" % _exc)
