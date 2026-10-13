"""Static call-closure purity checker for Reporter/agent extraction candidates (tri-state, fail-closed).

STATUS: ADVISORY. A PURE verdict is *necessary* evidence for "no hidden I/O/clock/env/lock in the call closure"; it is
never sufficient on its own. AST moved-body equivalence and baseline/feature differential parity remain mandatory,
independent evidence. UNKNOWN means "extraction NOT PROVEN SAFE".

Verdicts
  PURE     every call in the closure resolved to project code that was analysed recursively, to a builtin / stdlib
           function from the explicit KNOWN_PURE table, or to a container/string method from KNOWN_PURE_METHODS, and
           no impure finding was recorded.
  IMPURE   a call in the closure reaches file I/O, env, clock, randomness, logging, process/network, locks, etc.
  UNKNOWN  at least one call could not be resolved (unknown name, dynamic dispatch, subscript/lambda call, external
           import not in the table, unknown method, facade without a supplied module, recursion depth exhausted,
           source not parseable). Uncertainty is never converted to PURE.

Usage (the repository root is always explicit; nothing is hard-coded)
    python scripts/refactor/p158_static_purity_closure.py --root <repo> --module libs/x.py --function main \
        --lines 1545 1557 [--facade-module libs/x.py] [--max-depth 64]
"""
from __future__ import annotations

import argparse
import ast
import builtins
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

PURE, IMPURE, UNKNOWN = "PURE", "IMPURE", "UNKNOWN"

# builtins that are NOT pure
IMPURE_BUILTINS = {"open", "print", "input", "exec", "eval", "compile", "breakpoint", "__import__", "exit", "quit",
                   "globals", "locals", "vars", "setattr", "delattr", "getattr"}
# explicit, reviewed stdlib function table: (module, attr) -> pure. Everything else outside the project is UNKNOWN/IMPURE.
KNOWN_PURE = {
    ("json", "dumps"), ("json", "loads"), ("re", "sub"), ("re", "match"), ("re", "search"), ("re", "findall"),
    ("re", "compile"), ("re", "split"), ("re", "fullmatch"), ("math", "floor"), ("math", "ceil"), ("math", "sqrt"),
    ("math", "isnan"), ("math", "isinf"), ("math", "fabs"), ("math", "log"), ("math", "exp"), ("math", "pow"),
    ("copy", "deepcopy"), ("copy", "copy"), ("hashlib", "sha256"), ("hashlib", "sha1"), ("hashlib", "md5"),
    ("os.path", "join"), ("os.path", "basename"), ("os.path", "dirname"), ("os.path", "splitext"),
    ("os.path", "normpath"), ("os.path", "normcase"), ("string", "capwords"), ("textwrap", "shorten"),
    ("datetime", "fromisoformat"), ("datetime", "strptime"), ("datetime", "fromtimestamp"),
    ("datetime", "utcfromtimestamp"), ("datetime", "combine"), ("collections", "OrderedDict"),
    ("collections", "defaultdict"), ("collections", "Counter"), ("collections", "deque"), ("typing", "cast"),
    ("itertools", "chain"), ("itertools", "islice"), ("functools", "partial"), ("decimal", "Decimal"),
    ("pathlib", "Path"), ("pathlib", "PurePath"),
}
# methods that are pure regardless of receiver type
KNOWN_PURE_METHODS = {
    "get", "items", "keys", "values", "copy", "strip", "lstrip", "rstrip", "lower", "upper", "title", "split",
    "rsplit", "splitlines", "join", "startswith", "endswith", "format", "index", "count", "isdigit", "isalpha",
    "isalnum", "isspace", "encode", "decode", "casefold", "zfill", "ljust", "rjust", "center", "partition",
    "rpartition", "union", "intersection", "difference", "issubset", "issuperset", "isoformat", "strftime",
    "timestamp", "total_seconds", "hexdigest", "group", "groups", "groupdict", "span", "start", "end", "sub",
    "match", "search", "findall", "fullmatch", "finditer", "as_posix", "with_suffix", "with_name", "relative_to",
    "joinpath", "to_dict", "asdict", "_asdict", "_replace", "is_integer", "bit_length",
}
# Methods whose meaning depends on the receiver type. `replace` is str.replace (pure) / datetime.replace (pure) /
# Path.replace (FILESYSTEM RENAME = I/O); it is therefore decided ONLY by a proven receiver kind, never by name.
RECEIVER_DEPENDENT_METHODS = {"replace"}
# In-place mutators: they perform no I/O, but they change the receiver. "Purity" in this checker means *no I/O, clock,
# env, lock or logging in the call closure* - it is NOT input immutability. A mutator on a receiver that is not proven
# to be a locally created fresh container is UNKNOWN ("input mutation not excluded"); on a proven fresh local
# container it is PURE (the mutation cannot be observed by the caller).
MUTATING_METHODS = {"append", "extend", "update", "setdefault", "pop", "popitem", "clear", "insert", "remove", "sort",
                    "reverse", "add", "discard", "appendleft", "popleft"}
STR_RETURNING_METHODS = {"strip", "lstrip", "rstrip", "lower", "upper", "title", "join", "format", "replace",
                         "casefold", "zfill", "ljust", "rjust", "center", "removeprefix", "removesuffix",
                         "capitalize", "swapcase", "expandtabs"}
PATH_RETURNING_METHODS = {"with_suffix", "with_name", "relative_to", "joinpath", "resolve", "expanduser",
                          "absolute", "with_stem"}
FRESH_CALLS = {"dict", "list", "set", "sorted", "tuple", "defaultdict", "OrderedDict", "deque", "Counter"}
# methods / names that perform I/O, locking or clock access
IMPURE_METHODS = {
    "read_text", "write_text", "read_bytes", "write_bytes", "exists", "is_file", "is_dir", "open", "mkdir",
    "unlink", "iterdir", "glob", "rglob", "stat", "lstat", "rename", "touch", "rmdir", "chmod", "readlines",
    "readline", "read", "write", "writelines", "flush", "close", "seek", "truncate", "acquire", "release",
    "now", "utcnow", "today", "sleep", "info", "warning", "error", "exception", "debug", "critical", "log",
    "send", "recv", "connect", "request", "post", "put", "commit", "execute", "executemany", "fetchall",
    "fetchone", "dump", "load", "getenv", "listdir", "makedirs", "system", "popen", "run", "Popen", "symlink_to",
    "hardlink_to", "write_through", "samefile", "owner", "group_name", "expanduser_io",
}
IMPURE_ROOTS = {"os", "shutil", "subprocess", "socket", "sqlite3", "requests", "tempfile", "logging", "time",
                "random", "uuid", "secrets", "threading", "multiprocessing", "urllib", "http", "ctypes", "signal",
                "sys", "importlib", "pickle", "fcntl", "msvcrt", "psutil"}
IMPURE_DATETIME_ATTRS = {"now", "utcnow", "today"}


@dataclass
class Finding:
    kind: str  # IMPURE | UNKNOWN
    detail: str
    chain: Tuple[str, ...]

    def as_dict(self):
        return {"kind": self.kind, "detail": self.detail, "chain": list(self.chain)}


@dataclass
class Result:
    verdict: str
    findings: List[Finding] = field(default_factory=list)
    visited: int = 0

    def as_dict(self):
        return {"verdict": self.verdict, "visited_functions": self.visited,
                "findings": [f.as_dict() for f in self.findings]}


class _Module:
    def __init__(self, rel, tree):
        self.rel = rel
        self.funcs: Dict[str, ast.FunctionDef] = {}
        self.classes: Dict[str, ast.ClassDef] = {}
        self.stars: List[str] = []  # modules imported with `from m import *`
        self.aliases: Dict[str, str] = {}  # module-level `name = other_name` re-bindings
        self.imports: Dict[str, Tuple[str, Optional[str]]] = {}  # local -> (module, attr|None)
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs[n.name] = n
            elif isinstance(n, ast.ClassDef):
                self.classes[n.name] = n
            elif (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                  and isinstance(n.value, ast.Name)):
                self.aliases[n.targets[0].id] = n.value.id
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.imports[(a.asname or a.name).split(".")[0]] = (a.name if a.asname else a.name.split(".")[0], None)
            elif isinstance(n, ast.ImportFrom) and (n.module or n.level):
                mod_name = n.module or ""
                if n.level:  # relative import: resolve against this module's package
                    pkg = self.rel.replace("\\", "/").rsplit("/", 1)[0].split("/") if "/" in self.rel else []
                    if n.level > 1:
                        pkg = pkg[: len(pkg) - (n.level - 1)]
                    mod_name = ".".join([x for x in pkg + ([n.module] if n.module else []) if x])
                for a in n.names:
                    if a.name == "*":
                        self.stars.append(mod_name)
                    else:
                        self.imports.setdefault(a.asname or a.name, (mod_name, a.name))
        self.tree = tree


class Checker:
    def __init__(self, root: str, max_depth: int = 64, facade_module: Optional[str] = None):
        self.root = os.path.abspath(root)
        self.max_depth = max_depth
        self.facade_module = facade_module
        self._modules: Dict[str, Optional[_Module]] = {}
        self._memo: Dict[Tuple[str, str], List[Finding]] = {}
        self._stack: Set[Tuple[str, str]] = set()
        self.visited = 0

    # ---- module loading ------------------------------------------------------------------------------------------
    def _path_for(self, dotted: str) -> Optional[str]:
        base = os.path.join(self.root, *dotted.split("."))
        for cand in (base + ".py", os.path.join(base, "__init__.py")):
            if os.path.isfile(cand):
                return os.path.relpath(cand, self.root).replace("\\", "/")
        return None

    def load(self, rel: str) -> Optional[_Module]:
        if rel not in self._modules:
            try:
                src = open(os.path.join(self.root, rel), encoding="utf-8-sig").read()
                self._modules[rel] = _Module(rel, ast.parse(src))
            except (OSError, SyntaxError, ValueError):
                self._modules[rel] = None
        return self._modules[rel]

    # ---- analysis ------------------------------------------------------------------------------------------------
    def function(self, rel: str, name: str, depth: int, chain: Tuple[str, ...]) -> List[Finding]:
        key = (rel, name)
        if key in self._memo:
            return self._memo[key]
        if key in self._stack:  # cycle: contributes no new information (its findings are collected at the entry)
            return []
        if depth > self.max_depth:
            return [Finding(UNKNOWN, f"recursion depth {self.max_depth} exhausted at {rel}::{name}", chain)]
        mod = self.load(rel)
        if mod is None:
            return [Finding(UNKNOWN, f"source of {rel} unavailable or unparseable", chain)]
        fn = mod.funcs.get(name)
        if fn is None:
            cls = mod.classes.get(name)
            if cls is not None:
                return self._class(mod, cls, depth, chain + (f"{rel}::{name}",))
            # re-export chains: `from x import name`, `name = other`, `from x import *`
            if name in mod.aliases and mod.aliases[name] != name:
                return self.function(rel, mod.aliases[name], depth + 1, chain)
            if name in mod.imports:
                m, attr = mod.imports[name]
                target = self._path_for(m)
                if target and target != rel:
                    return self.function(target, attr or name, depth + 1, chain)
            for m in mod.stars:
                target = self._path_for(m)
                if target and target != rel:
                    tmod = self.load(target)
                    if tmod is not None and (name in tmod.funcs or name in tmod.classes or name in tmod.imports
                                             or name in tmod.aliases or tmod.stars):
                        res = self.function(target, name, depth + 1, chain)
                        if not any(f.kind == UNKNOWN and "not defined" in f.detail for f in res):
                            return res
            return [Finding(UNKNOWN, f"function {name} not defined in {rel}", chain)]
        self._stack.add(key)
        self.visited += 1
        try:
            out = self._calls_in(mod, [fn], depth, chain + (f"{rel}::{name}",))
        finally:
            self._stack.discard(key)
        self._memo[key] = out
        return out

    def _class(self, mod, cls, depth, chain):
        out = []
        for st in cls.body:
            if isinstance(st, ast.FunctionDef) and st.name in ("__init__", "__post_init__"):
                out += self._calls_in(mod, [st], depth + 1, chain)
        return out

    def statements(self, rel: str, stmts: Sequence[ast.stmt], chain=("<run>",)) -> Result:
        mod = self.load(rel)
        if mod is None:
            return Result(UNKNOWN, [Finding(UNKNOWN, f"source of {rel} unavailable", chain)])
        found = self._calls_in(mod, list(stmts), 0, chain)
        return self._result(found)

    def _result(self, found: List[Finding]) -> Result:
        seen, uniq = set(), []
        for f in found:
            k = (f.kind, f.detail)
            if k not in seen:
                seen.add(k)
                uniq.append(f)
        verdict = IMPURE if any(f.kind == IMPURE for f in uniq) else (UNKNOWN if uniq else PURE)
        return Result(verdict, uniq, self.visited)

    def _calls_in(self, mod: _Module, nodes, depth: int, chain) -> List[Finding]:
        local_defs = set()
        for n in nodes:
            for x in ast.walk(n):
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x is not n:
                    local_defs.add(x.name)
        assigned: Set[str] = set()
        for n in nodes:
            for x in ast.walk(n):
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store):
                    assigned.add(x.id)
                if isinstance(x, ast.arg):
                    assigned.add(x.arg)
        env = self._infer_env(mod, nodes)
        out: List[Finding] = []
        for n in nodes:
            for c in ast.walk(n):
                if isinstance(c, (ast.Await, ast.Yield, ast.YieldFrom)):
                    out.append(Finding(UNKNOWN, "await/yield in closure", chain))
                if isinstance(c, ast.Call):
                    out += self._call(mod, c, depth, chain, local_defs, assigned, env)
        return out

    # ---- minimal receiver-kind inference (str / Path / fresh container); anything else is None -> UNKNOWN ------------
    def _is_pathlib_path(self, mod, func) -> bool:
        if isinstance(func, ast.Name):
            return mod.imports.get(func.id) == ("pathlib", "Path")
        if isinstance(func, ast.Attribute) and func.attr == "Path" and isinstance(func.value, ast.Name):
            rn = func.value.id
            if rn == "facade" and self.facade_module:
                fm = self.load(self.facade_module)
                return fm is not None and fm.imports.get("Path") == ("pathlib", "Path")
            return rn in mod.imports and mod.imports[rn][0] == "pathlib" and mod.imports[rn][1] is None
        return False

    def _kind(self, mod, e, env) -> Optional[str]:
        if isinstance(e, ast.Constant):
            return "str" if isinstance(e.value, str) else None
        if isinstance(e, ast.JoinedStr):
            return "str"
        if isinstance(e, (ast.Dict, ast.List, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
            return "fresh"
        if isinstance(e, ast.Name):
            return env.get(e.id)
        if isinstance(e, ast.BinOp):
            left, right = self._kind(mod, e.left, env), self._kind(mod, e.right, env)
            if isinstance(e.op, (ast.Add, ast.Mod)) and "str" in (left, right) and {left, right} <= {"str", None}:
                return "str"
            if isinstance(e.op, ast.Div) and "path" in (left, right) and {left, right} <= {"path", "str"}:
                return "path"
            return None
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name):
                if f.id in ("str", "repr") and f.id not in mod.imports and f.id not in mod.funcs:
                    return "str"
                if f.id in FRESH_CALLS and f.id not in mod.funcs and f.id not in mod.imports:
                    return "fresh"
            if self._is_pathlib_path(mod, f):
                return "path"
            if isinstance(f, ast.Attribute):
                recv = self._kind(mod, f.value, env)
                if recv == "str" and f.attr in STR_RETURNING_METHODS:
                    return "str"
                if recv == "path" and f.attr in PATH_RETURNING_METHODS:
                    return "path"
            return None
        if isinstance(e, ast.Attribute) and e.attr == "parent" and self._kind(mod, e.value, env) == "path":
            return "path"
        return None

    def _infer_env(self, mod, nodes) -> Dict[str, str]:
        """name -> kind, only for names with exactly one plain assignment (or an annotated parameter) in the analysed
        statements. Re-assigned, loop/with/augmented targets and unpacked names get no kind (-> UNKNOWN)."""
        counts: Dict[str, int] = {}
        values: Dict[str, ast.AST] = {}
        poisoned: Set[str] = set()
        env: Dict[str, str] = {}
        for n in nodes:
            for x in ast.walk(n):
                if isinstance(x, ast.Assign):
                    for t in x.targets:
                        if isinstance(t, ast.Name) and len(x.targets) == 1:
                            counts[t.id] = counts.get(t.id, 0) + 1
                            values[t.id] = x.value
                        else:
                            for y in ast.walk(t):
                                if isinstance(y, ast.Name):
                                    poisoned.add(y.id)
                elif isinstance(x, ast.AnnAssign) and isinstance(x.target, ast.Name) and x.value is not None:
                    counts[x.target.id] = counts.get(x.target.id, 0) + 1
                    values[x.target.id] = x.value
                elif isinstance(x, (ast.For, ast.AugAssign, ast.comprehension, ast.NamedExpr)):
                    for y in ast.walk(x.target):
                        if isinstance(y, ast.Name):
                            poisoned.add(y.id)
                elif isinstance(x, ast.With):
                    for it in x.items:
                        if it.optional_vars is not None:
                            for y in ast.walk(it.optional_vars):
                                if isinstance(y, ast.Name):
                                    poisoned.add(y.id)
                elif isinstance(x, ast.arg):
                    ann = x.annotation
                    if isinstance(ann, ast.Name) and ann.id == "str":
                        env[x.arg] = "str"
                    elif ann is not None and self._is_pathlib_path(mod, ann):
                        env[x.arg] = "path"
        for name, cnt in counts.items():
            if cnt == 1 and name not in poisoned and name not in env:
                k = self._kind(mod, values[name], env)
                if k:
                    env[name] = k
        for name in poisoned:
            env.pop(name, None)
        return env

    def _call(self, mod, call: ast.Call, depth, chain, local_defs, assigned, env=None) -> List[Finding]:
        f = call.func
        if isinstance(f, ast.Name):
            return self._name_call(mod, f.id, depth, chain, local_defs, assigned)
        if isinstance(f, ast.Attribute):
            return self._attr_call(mod, f, depth, chain, env or {})
        return [Finding(UNKNOWN, f"dynamic call target ({type(f).__name__}) at line {call.lineno}", chain)]

    def _name_call(self, mod, name, depth, chain, local_defs, assigned):
        if name in IMPURE_BUILTINS:
            return [Finding(IMPURE, f"call {name}()", chain)]
        if name in mod.funcs or name in mod.classes:
            return self.function(mod.rel, name, depth + 1, chain)
        if name in local_defs:
            return []  # nested def: its body is part of the analysed statements
        if name in mod.imports:
            m, attr = mod.imports[name]
            target = self._path_for(m)
            if target:
                return self.function(target, attr or name, depth + 1, chain)
            root = m.split(".")[0]
            if attr and (m, attr) in KNOWN_PURE or attr and (root, attr) in KNOWN_PURE:
                return []
            if root in IMPURE_ROOTS:
                return [Finding(IMPURE, f"call {m}.{attr or name}() (impure stdlib root {root})", chain)]
            return [Finding(UNKNOWN, f"external import {m}.{attr or name}() not in the known-pure table", chain)]
        if hasattr(builtins, name):
            return []
        if name in assigned:
            return [Finding(UNKNOWN, f"call through local variable {name}() (dynamic dispatch)", chain)]
        return [Finding(UNKNOWN, f"unresolved call target {name}()", chain)]

    def _attr_call(self, mod, f: ast.Attribute, depth, chain, env=None):
        env = env or {}
        root = f
        parts = []
        while isinstance(root, ast.Attribute):
            parts.append(root.attr)
            root = root.value
        parts.reverse()
        attr = parts[-1]
        if isinstance(root, ast.Name):
            rn = root.id
            if rn == "facade":
                return self._facade_call(parts[0] if len(parts) == 1 else None, parts, depth, chain)
            if rn in mod.imports:
                m, a = mod.imports[rn]
                dotted = m if a is None else f"{m}.{a}"
                target = self._path_for(dotted) or (self._path_for(m) if a is None else None)
                if target and len(parts) == 1:
                    return self.function(target, attr, depth + 1, chain)
                if target:
                    return [Finding(UNKNOWN, f"nested attribute call {rn}.{'.'.join(parts)}()", chain)]
                base = dotted.split(".")[0]
                if (dotted, attr) in KNOWN_PURE or (m, attr) in KNOWN_PURE or (base, attr) in KNOWN_PURE:
                    return []
                if base == "datetime" and attr not in IMPURE_DATETIME_ATTRS:
                    return []
                if base in IMPURE_ROOTS or attr in IMPURE_METHODS:
                    return [Finding(IMPURE, f"call {rn}.{'.'.join(parts)}() ({dotted})", chain)]
                return [Finding(UNKNOWN, f"external call {rn}.{'.'.join(parts)}() not in the known-pure table", chain)]
            if rn in ("self", "cls"):
                return [Finding(UNKNOWN, f"method call on {rn}.{attr}()", chain)]
        # method call on an arbitrary expression (variable, subscript, call result ...)
        if attr in IMPURE_METHODS:
            return [Finding(IMPURE, f"method .{attr}() (I/O, lock or clock)", chain)]
        recv = f.value
        if isinstance(recv, ast.Name) and recv.id in ("str", "bytes") and recv.id not in mod.imports \
                and recv.id not in mod.funcs:
            return []  # unbound builtin type method, e.g. str.replace(s, a, b)
        kind = self._kind(mod, recv, env)
        if attr in RECEIVER_DEPENDENT_METHODS:
            if kind == "str":
                return []
            if kind == "path":
                return [Finding(IMPURE, f"Path.{attr}() renames/moves a filesystem entry", chain)]
            return [Finding(UNKNOWN, f".{attr}() on a receiver of unproven type (str.replace is pure, "
                                     f"Path.replace is filesystem I/O)", chain)]
        if attr in MUTATING_METHODS:
            if kind == "fresh":
                return []  # mutation of a locally created container is not observable by the caller
            return [Finding(UNKNOWN, f".{attr}() mutates a receiver that is not proven to be a fresh local "
                                     f"container (input mutation not excluded)", chain)]
        if attr in KNOWN_PURE_METHODS:
            return []
        return [Finding(UNKNOWN, f"method .{attr}() on an unresolved receiver", chain)]

    def _facade_call(self, name, parts, depth, chain):
        if self.facade_module is None:
            return [Finding(UNKNOWN, f"facade.{'.'.join(parts)}() dynamic dispatch without a facade module", chain)]
        if name is None:  # facade.os.getenv(...), facade.json.dumps(...): module attribute of the facade module
            fm = self.load(self.facade_module)
            head = parts[0]
            if fm is not None and head in fm.imports:
                m, a = fm.imports[head]
                if (m, parts[-1]) in KNOWN_PURE:
                    return []
                if m.split(".")[0] in IMPURE_ROOTS:
                    return [Finding(IMPURE, f"call facade.{'.'.join(parts)}() ({m})", chain)]
            return [Finding(UNKNOWN, f"facade.{'.'.join(parts)}() not resolvable", chain)]
        fm = self.load(self.facade_module)
        if fm is None:
            return [Finding(UNKNOWN, f"facade module {self.facade_module} unavailable", chain)]
        if name in fm.funcs or name in fm.classes:
            return self.function(self.facade_module, name, depth + 1, chain)
        if name in fm.imports:
            m, attr = fm.imports[name]
            target = self._path_for(m)
            if target:
                return self.function(target, attr or name, depth + 1, chain)
            if (m, attr) in KNOWN_PURE:
                return []
            if m.split(".")[0] in IMPURE_ROOTS:
                return [Finding(IMPURE, f"call facade.{name}() ({m}.{attr})", chain)]
        return [Finding(UNKNOWN, f"facade.{name}() not resolvable in {self.facade_module}", chain)]


# ---- public helpers -------------------------------------------------------------------------------------------------
def check_function(root, module, function, *, max_depth=64, facade_module=None) -> Result:
    c = Checker(root, max_depth, facade_module)
    found = c.function(module, function, 0, ())
    return c._result(found)


def check_lines(root, module, function, start, end, *, max_depth=64, facade_module=None) -> Result:
    """Statements of `function` whose lines lie within [start, end] (outermost matching statements only)."""
    c = Checker(root, max_depth, facade_module)
    mod = c.load(module)
    if mod is None:
        return Result(UNKNOWN, [Finding(UNKNOWN, f"source of {module} unavailable", ())])
    fn = mod.funcs.get(function)
    if fn is None:
        return Result(UNKNOWN, [Finding(UNKNOWN, f"function {function} not found in {module}", ())])
    picked = []

    def visit(body):
        for st in body:
            if start <= st.lineno and st.end_lineno <= end:
                picked.append(st)
            else:
                for field_name in ("body", "orelse", "finalbody", "handlers"):
                    sub = getattr(st, field_name, None)
                    if isinstance(sub, list):
                        visit([x for x in sub if isinstance(x, ast.stmt)] if field_name != "handlers"
                              else [y for h in sub for y in h.body])

    visit(fn.body)
    if not picked:
        return Result(UNKNOWN, [Finding(UNKNOWN, f"no statements of {function} within lines {start}-{end}", ())])
    return c.statements(module, picked, (f"{module}::{function}[{start}-{end}]",))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", required=True, help="repository root (explicit; no default)")
    ap.add_argument("--module", required=True)
    ap.add_argument("--function", required=True)
    ap.add_argument("--lines", nargs=2, type=int)
    ap.add_argument("--facade-module")
    ap.add_argument("--max-depth", type=int, default=64)
    a = ap.parse_args(argv)
    if a.lines:
        r = check_lines(a.root, a.module, a.function, a.lines[0], a.lines[1], max_depth=a.max_depth,
                        facade_module=a.facade_module)
    else:
        r = check_function(a.root, a.module, a.function, max_depth=a.max_depth, facade_module=a.facade_module)
    print(json.dumps(r.as_dict(), indent=1, ensure_ascii=False))
    return 0 if r.verdict == PURE else 2


if __name__ == "__main__":
    sys.exit(main())
