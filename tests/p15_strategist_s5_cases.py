"""Deterministic offline cases for the eight S5 helper moves (stdlib only; imported inside the observation child)."""
NAN, INF = float("nan"), float("inf")


class FloatBoom:
    def __float__(self):
        raise ValueError("boom")

    def __str__(self):
        raise RuntimeError("str boom")


class Rebind:
    """Rebinds a facade global DURING the call (when the helper converts / stringifies the value)."""

    def __init__(self, node, name, fake):
        self.node, self.name, self.fake = node, name, fake

    def __float__(self):
        setattr(self.node, self.name, self.fake)
        return 0.75

    def __bool__(self):
        return True

    def __str__(self):
        setattr(self.node, self.name, self.fake)
        return "a,b"


class RebindThenRaise(Rebind):
    """__float__ rebinds the facade global and then fails, so the helper takes its except branch and must look the name up afresh."""

    def __float__(self):
        setattr(self.node, self.name, self.fake)
        raise ValueError("rebound then failed")


class Rec:
    def __init__(self, **funcs):
        for k, v in funcs.items():
            setattr(self, k, v)


CASES = []


def add(cid, fn, *args):
    CASES.append({"id": f"{fn}.{cid}", "fn": fn, "setup": lambda node, log, a=args: list(a)})


def add_setup(cid, fn, setup):
    CASES.append({"id": f"{fn}.{cid}", "fn": fn, "setup": setup})


def many(fn, rows):
    for i, a in enumerate(rows):
        add(f"v{i}", fn, *a)


many("_clamp", [(5, 0, 10), (-1, 0, 10), (11, 0, 10), (0, 0, 0), (NAN, 0, 1), (INF, 0, 1), (-INF, 0, 1), (1, "a", "b"), (True, 0, 1),
                ("b", "a", "c"), (0.5, 1, 0), (-0.0, 0, 1), (10 ** 30, 0, 10), (0.5, 0.0, 1.0), (3, 3.0, 3)])
many("_to_float", [("1.5",), ("1.5", 9), (None, 2), (None, "x"), ("nan",), ("inf", 1), (" 3 ", 0), (b"2", 0), ([], 5), (FloatBoom(), 4),
                   (True, 0), ("１２", 0), (None, None), (None, 7), ("1_000", 0), (10 ** 400, 1)])
many("_to_int", [("3.9", 1), (None, 5), ("nan", 7), ("inf", 7), (1e30, 0), (" 12 ", 0), ("abc", "z"), (True, 0), (-2.9, 0), ("1e3", 0),
                 (None, 2.9), (FloatBoom(), 3), ("0x10", 6), (b"5", 0)])
many("_round_optional", [(1.23456,), (1.5, 0), ("x",), (None,), (NAN, 2), (2.5, 0), (1.005, 2), ("1.2345", "a"), (INF, 2), (INF, 0),
                         (1.23456, 2.9), (123456.789, -2), ("3.14159", 3), (FloatBoom(),), (True, 1)])
many("_unit_score", [(0.5,), (2,), (-3,), ("0.3",), (None, 0.7), (None, 5), (NAN,), ("x", "y"), (None, None), (True,), (INF,), (-INF,),
                     (1e-320,), ("0.25", 0.9)])


def unit_before(node, log):
    node._clamp = lambda x, lo, hi: (log.append(["clamp", repr(x), repr(lo), repr(hi)]), 0.25)[1]
    return [0.4]


def unit_mid(node, log):
    fake = lambda x, lo, hi: (log.append(["clamp_mid", repr(x)]), 0.125)[1]  # noqa: E731
    return [Rebind(node, "_clamp", fake)]


def unit_default_path(node, log):
    node._clamp = lambda x, lo, hi: (log.append(["clamp_default", repr(x), repr(lo), repr(hi)]), 0.5)[1]
    return ["bad", 0.9]


def unit_mid_default(node, log):
    fake = lambda x, lo, hi: (log.append(["clamp_mid_default", repr(x)]), 0.375)[1]  # noqa: E731
    return [RebindThenRaise(node, "_clamp", fake), 0.9]


add_setup("patched_clamp_mid_default_branch", "_unit_score", unit_mid_default)
add_setup("patched_clamp_before", "_unit_score", unit_before)
add_setup("patched_clamp_mid", "_unit_score", unit_mid)
add_setup("patched_clamp_in_default_branch", "_unit_score", unit_default_path)

many("_is_trueish", [(None,), ("Yes",), (" ON ",), (1,), (0,), (True,), (False,), ("y",), ("2",), ([],), ("TRUE\n",), ("tRuE",), (b"1",),
                     ("1.0",), ("١",), (FloatBoom(),), ("off",), ("",)])
many("_strip_fenced_block", [('```json\n{"a":1}\n```',), ("```\nx",), ("plain",), (None,), ("```",), ("  ```py\r\ncode\r\n```  ",),
                             ("```a\n```\n```",), (123,), ("```\n\n```",), ("```\n한글\n```",), ("```x\nmid ```tail",),
                             ("```x\n  ```  \n",), ("\n```\nz\n```\n",), ("```\r\nA\r\nB\r\n```",), (FloatBoom(),)])
many("_parse_text_list_fragment", [(None,), ([" a ", None, "b", ""],), (("x",),), ({"q"},), ("",), ("   ",), ('["a", "b", ""]',),
                                   ("['a', 'b']",), ("{'a','b'}",), ("a,b;c|d\ne",), ("single",), ("[1,2",), ('"quoted"',), ("1,2",),
                                   ("(1)",), ("[]",), (5,), ("5",), ("a,, b ;; c",), ("한,글",), ("[None, 'x']",), ("null",),
                                   ("{'k': 1}",), (FloatBoom(),), (0,), (b"a,b",), ('["a\\/b"]',)])


def text_json_fails(node, log):
    def loads(s):
        log.append(["json.loads", s])
        raise ValueError("fake json")
    node.json = Rec(loads=loads)
    return ["['p', 'q']"]


def text_ast_fake(node, log):
    def literal_eval(s):
        log.append(["ast.literal_eval", s])
        return ["from-fake-ast"]

    def loads(s):
        raise ValueError("x")
    node.json = Rec(loads=loads)
    node.ast = Rec(literal_eval=literal_eval)
    return ["anything"]


def text_re_before(node, log):
    def split(pat, s):
        log.append(["re.split", pat, s])
        return ["X", "", " Y "]
    node.re = Rec(split=split)
    return ["a,b"]


def text_re_mid(node, log):
    def split(pat, s):
        log.append(["re.split_mid", pat, s])
        return ["M1", "M2"]
    return [Rebind(node, "re", Rec(split=split))]


add_setup("json_patched_before", "_parse_text_list_fragment", text_json_fails)
add_setup("ast_patched_before", "_parse_text_list_fragment", text_ast_fake)
add_setup("re_patched_before", "_parse_text_list_fragment", text_re_before)
add_setup("re_patched_mid", "_parse_text_list_fragment", text_re_mid)
