"""Shared feature detection without evaluating requirement environment markers."""

from __future__ import annotations

import ast

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def uses_package(root, manifest_path, manifest, safe_path, package):
    # Do not evaluate markers on the checker's OS/Python: every declared target
    # environment remains part of the integration's support scope.
    if any(
        canonicalize_name(Requirement(req).name) == canonicalize_name(package)
        for req in manifest.get("requirements", [])
    ):
        return True
    for path in manifest_path.parent.rglob("*.py"):
        safe_path(root, path.relative_to(root))
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name.split(".")[0] == package for alias in node.names
            ):
                return True
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and (node.module or "").split(".")[0] == package
            ):
                return True
    return False


def matches(condition, data, root=None, manifest_path=None, safe_path=None):
    """Evaluate a named contract condition using confirmed input and real imports.

    Library requirement markers are intentionally not evaluated on this host.
    Import inspection, when requested, uses the same detector as both checkers.
    """
    from .contract import CONDITIONS

    if condition not in CONDITIONS:
        raise ValueError(f"Unsupported condition: {condition}")
    if condition == "always":
        return True
    if condition == "ui":
        return data["configuration"]["value"] == "ui"
    if condition == "platforms":
        return bool(data["platforms"]["value"])
    if condition in {"imagespec", "blesession"}:
        manifest = data["manifest"]["value"]
        if root is not None:
            if manifest_path is None or safe_path is None:
                raise ValueError("Import detection requires manifest_path and safe_path")
            return uses_package(root, manifest_path, manifest, safe_path, condition)
        return any(
            canonicalize_name(Requirement(req).name) == canonicalize_name(condition)
            for req in manifest.get("requirements", [])
        )
    return data["features"]["value"][condition]
