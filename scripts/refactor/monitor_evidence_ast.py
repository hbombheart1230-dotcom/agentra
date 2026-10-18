"""Frozen CPython 3.14 evidence dump profile for the existing Monitor inventory.

Python 3.12 dumps empty list fields; 3.13+ omit them. Only schema-declared
empty lists and optional None fields are omitted here. All remaining fields,
constants and contexts are serialized; this does not compare runtime bodies.
Historical inventory bytes and expected hashes must remain unchanged.
"""
import ast

# CPython 3.14 ASDL profile, frozen independently of the running interpreter.
_LIST_FIELDS = {'Assign': ('targets',),
 'AsyncFor': ('body', 'orelse'),
 'AsyncFunctionDef': ('body', 'decorator_list', 'type_params'),
 'AsyncWith': ('items', 'body'),
 'BoolOp': ('values',),
 'Call': ('args', 'keywords'),
 'ClassDef': ('bases', 'keywords', 'body', 'decorator_list', 'type_params'),
 'Compare': ('ops', 'comparators'),
 'Delete': ('targets',),
 'Dict': ('keys', 'values'),
 'DictComp': ('generators',),
 'ExceptHandler': ('body',),
 'For': ('body', 'orelse'),
 'FunctionDef': ('body', 'decorator_list', 'type_params'),
 'FunctionType': ('argtypes',),
 'GeneratorExp': ('generators',),
 'Global': ('names',),
 'If': ('body', 'orelse'),
 'Import': ('names',),
 'ImportFrom': ('names',),
 'Interactive': ('body',),
 'JoinedStr': ('values',),
 'List': ('elts',),
 'ListComp': ('generators',),
 'Match': ('cases',),
 'MatchClass': ('patterns', 'kwd_attrs', 'kwd_patterns'),
 'MatchMapping': ('keys', 'patterns'),
 'MatchOr': ('patterns',),
 'MatchSequence': ('patterns',),
 'Module': ('body', 'type_ignores'),
 'Nonlocal': ('names',),
 'Set': ('elts',),
 'SetComp': ('generators',),
 'TemplateStr': ('values',),
 'Try': ('body', 'handlers', 'orelse', 'finalbody'),
 'TryStar': ('body', 'handlers', 'orelse', 'finalbody'),
 'Tuple': ('elts',),
 'TypeAlias': ('type_params',),
 'While': ('body', 'orelse'),
 'With': ('items', 'body'),
 'arguments': ('posonlyargs', 'args', 'kwonlyargs', 'kw_defaults', 'defaults'),
 'comprehension': ('ifs',),
 'match_case': ('body',)}
_OPTIONAL_FIELDS = {'AnnAssign': ('value',),
 'Assert': ('msg',),
 'Assign': ('type_comment',),
 'AsyncFor': ('type_comment',),
 'AsyncFunctionDef': ('returns', 'type_comment'),
 'AsyncWith': ('type_comment',),
 'Constant': ('kind',),
 'ExceptHandler': ('type', 'name'),
 'For': ('type_comment',),
 'FormattedValue': ('format_spec',),
 'FunctionDef': ('returns', 'type_comment'),
 'ImportFrom': ('module', 'level'),
 'Interpolation': ('format_spec',),
 'MatchAs': ('pattern', 'name'),
 'MatchMapping': ('rest',),
 'MatchStar': ('name',),
 'ParamSpec': ('default_value',),
 'Raise': ('exc', 'cause'),
 'Return': ('value',),
 'Slice': ('lower', 'upper', 'step'),
 'TypeVar': ('bound', 'default_value'),
 'TypeVarTuple': ('default_value',),
 'With': ('type_comment',),
 'Yield': ('value',),
 'alias': ('asname',),
 'arg': ('annotation', 'type_comment'),
 'arguments': ('vararg', 'kwarg'),
 'keyword': ('arg',),
 'match_case': ('guard',),
 'withitem': ('optional_vars',)}


def evidence_dump(node):
    if isinstance(node, ast.AST):
        name = type(node).__name__
        fields = []
        for field in node._fields:
            if not hasattr(node, field):
                continue
            value = getattr(node, field)
            if value is None and field in _OPTIONAL_FIELDS.get(name, ()):
                continue
            if isinstance(value, list) and not value and field in _LIST_FIELDS.get(name, ()):
                continue
            fields.append(field + "=" + evidence_dump(value))
        return name + "(" + ", ".join(fields) + ")"
    if isinstance(node, list):
        return "[" + ", ".join(evidence_dump(value) for value in node) + "]"
    return repr(node)
