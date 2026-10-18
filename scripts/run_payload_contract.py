"""Run installed-library contracts; missing/inactive packages never count as coverage."""

from __future__ import annotations

import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def main():
    root = Path(os.environ["PAYLOAD_REPOSITORY"]).resolve()
    domain = os.environ["PAYLOAD_DOMAIN"]
    manifest = json.loads((root / "custom_components" / domain / "manifest.json").read_text())
    selected = [
        Requirement(r)
        for r in manifest.get("requirements", [])
        if canonicalize_name(Requirement(r).name) == "imagespec"
    ]
    try:
        installed = importlib.metadata.version("imagespec")
    except importlib.metadata.PackageNotFoundError:
        inactive = bool(selected) and all(
            r.marker is not None and not r.marker.evaluate() for r in selected
        )
        condition = (
            "All declared imagespec markers are inactive in this matrix"
            if inactive
            else "The runtime requirement is missing from this resolved environment"
        )
        raise SystemExit(
            f"{condition}; no payload coverage was produced. Use a supported active current/minimum environment or resolve an explicitly approved central contract adaptation. Do not install a marker-disabled library or raise support minima to hide this failure."
        )
    for requirement in selected:
        if (
            (requirement.marker is None or requirement.marker.evaluate())
            and requirement.specifier
            and installed not in requirement.specifier
        ):
            raise SystemExit(
                f"Installed imagespec {installed} does not satisfy actual manifest {requirement}"
            )
    print(f"Executing payload contract with actual installed imagespec {installed}", flush=True)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "hass_standards_payload",
            f"tests/components/{domain}/test_payload_examples.py",
            "-v",
        ],
        cwd=root,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
