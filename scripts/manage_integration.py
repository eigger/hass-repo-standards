"""Inspect and plan central integration changes. apply is not implemented yet."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from standards import inventory, planning


def output_path(value, target):
    path = Path(value).absolute()
    resolved = path.resolve()
    target = Path(target).resolve()
    if resolved == target or resolved.is_relative_to(target):
        raise ValueError("Inventory/plan output must be outside the target repository")
    # No output symlink/junction traversal, even when its resolved destination is outside target.
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
            raise ValueError("Output cannot traverse a symlink or junction")
    if resolved.exists() and not resolved.is_file():
        raise ValueError("Output must be a regular JSON file")
    if not resolved.parent.is_dir():
        raise ValueError("Output parent directory must already exist")
    return resolved


def write_output(path, data):
    content = planning.canonical_json(data).encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=".hass-standards-", suffix=".json", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = commands.add_parser(
        "inspect", help="Read metadata and unresolved observations"
    )
    inspect_parser.add_argument("target", type=Path)
    inspect_parser.add_argument("--output", type=Path, required=True)
    plan_parser = commands.add_parser(
        "plan", help="Create a deterministic JSON plan without applying it"
    )
    plan_parser.add_argument("target", type=Path)
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--mode", choices=("create", "adopt"), required=True)
    plan_parser.add_argument("--input", type=Path, required=True)
    plan_parser.add_argument("--standards-ref", required=True)
    args = parser.parse_args(argv)
    try:
        output = output_path(args.output, args.target)
        if args.command == "inspect":
            result = inventory.inspect(args.target)
        else:
            if output == args.input.resolve():
                raise ValueError("Plan output cannot overwrite its input")
            result = planning.plan(
                args.target, args.mode, inventory.load_json(args.input), args.standards_ref
            )
        # Recheck after inspection in case output ancestors were concurrently changed.
        output = output_path(output, args.target)
        write_output(output, result)
        return 2 if result["conflicts"] else 0
    except (ValueError, OSError, KeyError, SyntaxError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
