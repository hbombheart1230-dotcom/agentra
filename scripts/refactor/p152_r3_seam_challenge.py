"""P1.5.2 R3 evidence tool: direct synthetic differential + call-time seam challenge (offline, no LLM/broker).

FAIL-CLOSED (P15-R3-AUDIT-HARNESS-GUARDS-006). Never infers the tree from the working directory:

    $env:PYTHONDONTWRITEBYTECODE = "1"
    Set-Location <isolated clone>          # cwd MUST equal --root
    python -I -B scripts/refactor/p152_r3_seam_challenge.py --root <abs isolated clone> `
        --moved-free <abs input json> --out <abs NEW output json outside the clone> [--protected-root <abs>]

Env alternatives: R3_MOVED_FREE (module->{function->[facade globals]}), R3_OUT, R3_PROTECTED_ROOTS (os.pathsep list).
`C:\\Agentra` and everything below it is always refused (no stat/list/import of it). Scenarios patch facade
globals before the call and from inside a callback during the call.
"""
import argparse, importlib, inspect, json, os, re, sys

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


def norm(o):
    if isinstance(o, dict):
        return {str(k): norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)):
        return [norm(v) for v in o]
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    return "<%s>" % type(o).__qualname__



def run(root, moved_free_path, out_path):
    from unittest.mock import MagicMock

    sys.path.insert(0, root)
    with open(moved_free_path, encoding="utf-8") as fh:
        MOVED = json.load(fh)  # {module: {name: [free names]}}
    out = {"direct": {}, "seam": {}}
    # ---- Part A: direct synthetic differential for the 2 functions no recorded test exercised
    md = importlib.import_module("libs.reporting.trade_report_markdown_clean")
    ai = importlib.import_module("libs.reporting.trade_report_ai")
    for mod_ in (md, ai):  # defence in depth: the imported code must come from the validated root
        if not _is_under(_lex(os.path.abspath(mod_.__file__)), _lex(root), os.sep):
            raise GuardError("imported %s from outside the validated root: %r" % (mod_.__name__, mod_.__file__))
    cases = []
    vals = [None, "", "x", 0, 1, 3, 0.5, -2, {}, {"count": 2}, [1, 2], True]
    names = [None, "", "win_rate", "stop_loss", "momentum", "late_entry", "overextended", "mean_reversion", "손절", "추격매수"]
    for n in names:
        for d in (None, "", "detail text", "반복 손실", {"k": 1}):
            for v in (None, "", 0, 3, 0.25, "high", {"x": 1}):
                try:
                    r = md._humanize_reporter_pattern(n, d, v)
                except Exception as e:  # noqa
                    r = "EXC:%s:%s" % (type(e).__name__, str(e)[:60])
                cases.append(["humanize", repr((n, d, v)), r])
    stories = [
        {}, None, {"symbol": "005930"}, {"trade_id": "t1", "day": "2026-10-12", "symbol": "005930", "action": "BUY"},
        {"execution": {"action": "BUY", "qty": 3, "avg_price": 71000}, "strategist": {"selected_symbol": "005930"}},
        {"trade_lifecycle": {"entry": {"price": 70000, "qty": 2}, "exit": {"price": 71500, "qty": 2, "reason": "take_profit"}},
         "scanner": {"selected_symbol": "000660"}, "monitor": {"pnl_pct": 1.2}},
        {"execution": {"action": "SELL", "fills": [{"price": 70000, "qty": 1}, {"price": 70100, "qty": 1}]}},
    ]
    for s in stories:
        try:
            r = norm(ai.resolve_shared_trade_facts(s))
        except Exception as e:  # noqa
            r = "EXC:%s:%s" % (type(e).__name__, str(e)[:60])
        cases.append(["shared_facts", json.dumps(norm(s), sort_keys=True, default=str), r])
    out["direct"] = cases

    # ---- Part B: call-time seam challenge (patch before call / within call via callback)
    for modname, funcs in MOVED.items():
        mod = importlib.import_module(modname)
        for fname, free in funcs.items():
            fn = getattr(mod, fname)
            sig = inspect.signature(fn)
            req = [p for p in sig.parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
            kwreq = [p for p in sig.parameters.values() if p.default is p.empty and p.kind == p.KEYWORD_ONLY]
            targets = [n for n in free if n != fname and callable(getattr(mod, n, None)) and not inspect.ismodule(getattr(mod, n))
                       and not isinstance(getattr(mod, n), type)]
            rec_by_scenario = {}
            for label, mk in (("empty_dict", lambda: {}), ("mock", lambda: MagicMock()), ("text", lambda: "abc")):
                for scenario in ("pre_call", "within_call"):
                    orig = {n: getattr(mod, n) for n in targets}
                    events = []
                    state = {"switched": False}

                    def make(n, ver):
                        def stub(*a, **k):
                            events.append("%s:%s" % (ver, n))
                            if scenario == "within_call" and ver == "v1" and not state["switched"]:
                                state["switched"] = True
                                for m in targets:
                                    setattr(mod, m, make(m, "v2"))
                            return MagicMock()
                        return stub
                    for n in targets:
                        setattr(mod, n, make(n, "v1"))
                    try:
                        try:
                            fn(*[mk() for _ in req], **{p.name: mk() for p in kwreq})
                            res = "ok"
                        except Exception as e:  # noqa
                            res = "EXC:" + type(e).__name__
                    finally:
                        for n, v in orig.items():
                            setattr(mod, n, v)
                    rec_by_scenario["%s/%s" % (label, scenario)] = [res, events]
            out["seam"]["%s.%s" % (modname.rsplit(".", 1)[-1], fname)] = {"targets": len(targets), "runs": rec_by_scenario,
                                                                           "recursive": fname in free}
    with open(out_path, "x", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print("done", len(out["direct"]), len(out["seam"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="absolute path of the isolated Git clone (required; cwd must equal it)")
    ap.add_argument("--moved-free", help="absolute input json (or env R3_MOVED_FREE)")
    ap.add_argument("--out", help="absolute NEW output json outside the clone (or env R3_OUT)")
    ap.add_argument("--protected-root", action="append", default=[], help="extra protected absolute root")
    a = ap.parse_args(argv)
    env = os.environ
    try:
        cfg = validate_environment(
            a.root, os.getcwd(), env,
            inputs={"R3_MOVED_FREE": a.moved_free or env.get("R3_MOVED_FREE", "")},
            outputs={"R3_OUT": a.out or env.get("R3_OUT", "")},
            extra_protected=list(a.protected_root) + _extra_protected_from_env(env),
        )
    except GuardError as exc:
        sys.stderr.write("R3-GUARD-FAIL: %s\n" % exc)
        return 2
    try:
        run(cfg["root"], cfg["inputs"]["R3_MOVED_FREE"], cfg["outputs"]["R3_OUT"])
    except GuardError as exc:
        sys.stderr.write("R3-GUARD-FAIL: %s" % exc + chr(10))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
