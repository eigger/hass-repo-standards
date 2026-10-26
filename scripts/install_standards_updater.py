"""Bootstrap a consumer once using operator workflow-write authority."""

import argparse
import json
from pathlib import Path

from standards import update


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--release", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    new = update.attest_release(args.release)
    template = Path(__file__).resolve().parents[1] / "templates/integration" / update.CALLER
    changes = update.bootstrap_changes(args.root, new, template.read_text())
    print(json.dumps({"standards": new, "files": sorted(changes)}, indent=2))
    if args.write:
        for relative, text in changes.items():
            path = args.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
