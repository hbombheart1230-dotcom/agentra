from __future__ import annotations

import ast
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.routing import Mount, Route
import pytest

from apps.api.main import create_app

API_ROOT = Path(__file__).resolve().parents[3] / "apps" / "api"
FORBIDDEN_IMPORT_PREFIXES = (
    "apps.operator_ui",
    "graphs",
    "libs",
    "scripts",
)
FORBIDDEN_SIDE_EFFECT_MODULES = (
    "httpx",
    "requests",
    "subprocess",
    "urllib.request",
    "websocket",
)
FORBIDDEN_WRITE_METHODS = {
    "mkdir",
    "rename",
    "replace",
    "rmdir",
    "touch",
    "unlink",
    "write_bytes",
    "write_text",
}


def _import_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_api_has_no_core_or_side_effect_imports() -> None:
    violations: list[str] = []
    for path in API_ROOT.rglob("*.py"):
        for imported in _import_names(path):
            forbidden = FORBIDDEN_IMPORT_PREFIXES + FORBIDDEN_SIDE_EFFECT_MODULES
            if imported.startswith(forbidden):
                violations.append(f"{path.relative_to(API_ROOT)}: {imported}")

    assert violations == []


def test_api_source_has_no_filesystem_write_calls() -> None:
    violations: list[str] = []
    for path in API_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr in FORBIDDEN_WRITE_METHODS:
                violations.append(
                    f"{path.relative_to(API_ROOT)}:{node.lineno}:{node.func.attr}"
                )

    assert violations == []


def _get_only_endpoints(app):
    """Traverse verified router metadata, including FastAPI lazy included routers.

    Unknown route shapes, cycles, empty routers and duplicate paths fail closed.
    OpenAPI's generated Starlette GET/HEAD route is explicitly checked too.
    """
    endpoints = {}

    def visit(routes, prefix="", ancestors=frozenset()):
        if id(routes) in ancestors:
            raise AssertionError("route cycle: " + prefix)
        ancestors = ancestors | {id(routes)}
        if not routes:
            raise AssertionError("empty route set: " + prefix)
        for route in routes:
            kind = type(route)
            if kind.__module__ == "fastapi.routing" and kind.__name__ == "_IncludedRouter":
                router = getattr(route, "original_router", None)
                context = getattr(route, "include_context", None)
                if not isinstance(router, APIRouter) or not isinstance(getattr(context, "prefix", None), str):
                    raise AssertionError("unverified included router: " + repr(route))
                visit(router.routes, prefix + context.prefix, ancestors)
            elif isinstance(route, Mount):
                visit(route.routes, prefix + route.path, ancestors)
            elif isinstance(route, (APIRoute, Route)):
                path = prefix + route.path
                methods = route.methods
                metadata = (type(route) is Route and path == app.openapi_url and
                            route.name == "openapi" and route.endpoint.__module__ == "fastapi.applications")
                expected = {"GET", "HEAD"} if metadata else {"GET"}
                if methods != expected:
                    raise AssertionError(f"non-GET endpoint: {path} {methods} ({kind.__name__})")
                if path in endpoints:
                    raise AssertionError("duplicate endpoint: " + path)
                endpoints[path] = route
            else:
                raise AssertionError(f"unrecognized route: {prefix} {kind.__module__}.{kind.__name__}")

    visit(app.routes)
    if not endpoints:
        raise AssertionError("no endpoints discovered")
    return endpoints


def test_api_routes_are_get_only(api_settings) -> None:
    app = create_app(api_settings)
    endpoints = _get_only_endpoints(app)
    # OpenAPI is an independent public enumeration of the mounted API paths.
    assert set(endpoints) == set(app.openapi()["paths"]) | {app.openapi_url}
    assert app.routes is app.router.routes


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize("mounted", [False, True])
def test_included_or_mounted_mutating_route_is_rejected(method, mounted):
    app = FastAPI(openapi_url=None)
    nested = APIRouter()
    nested.add_api_route("/bad", lambda: {}, methods=[method])
    outer = APIRouter()
    outer.include_router(nested, prefix="/nested")
    child = FastAPI(openapi_url=None)
    child.include_router(outer, prefix="/outer")
    if mounted:
        app.mount("/mounted", child)
    else:
        app.include_router(outer, prefix="/outer")
    with pytest.raises(AssertionError, match="non-GET endpoint"):
        _get_only_endpoints(app)


def test_nested_get_path_is_not_lost():
    app = FastAPI(openapi_url=None)
    inner = APIRouter()
    inner.add_api_route("/ok", lambda: {}, methods=["GET"])
    outer = APIRouter()
    outer.include_router(inner, prefix="/inner")
    child = FastAPI(openapi_url=None)
    child.include_router(outer, prefix="/outer")
    app.mount("/mounted", child)
    assert set(_get_only_endpoints(app)) == {"/mounted/outer/inner/ok"}


def test_unknown_route_and_cycle_fail_closed():
    app = FastAPI(openapi_url=None)
    app.router.routes.append(object())
    with pytest.raises(AssertionError, match="unrecognized"):
        _get_only_endpoints(app)
    app.router.routes.clear()
    app.mount("/cycle", app)
    with pytest.raises(AssertionError, match="cycle"):
        _get_only_endpoints(app)
