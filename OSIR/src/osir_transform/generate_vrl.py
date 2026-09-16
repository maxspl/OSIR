#!/usr/bin/env python3
"""Generate ECS normalization VRL scripts from OSIR transform YAML files.

Usage:
    python3 generate_vrl.py                  # regenerate every file listed in MAPPING
    python3 generate_vrl.py --check          # exit 1 if a VRL is out of sync with its YAML
    python3 generate_vrl.py <in.yml> <out.vrl>
"""
import argparse
import difflib
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
DEPENDENCIES = SRC.parent / "configs" / "dependencies"
sys.path[:0] = [str(SRC / "osir_transform"), str(SRC / "osir_lib")]

from osir_transform.OsirTransform import OsirTransform  # noqa: E402

MAPPING = {
    "transform/windows/evtx.yml": "ecs_normalize/evtx.vrl",
}


def generate(yml: Path, vrl: Path, check: bool) -> bool:
    content = OsirTransform.from_yaml(str(yml)).to_vrl()
    current = vrl.read_text(encoding="utf-8") if vrl.exists() else ""
    if content == current:
        print(f"[OK]      {vrl}")
        return True
    if check:
        print(f"[OUTDATED] {vrl} (from {yml})")
        sys.stdout.writelines(list(difflib.unified_diff(
            current.splitlines(keepends=True), content.splitlines(keepends=True),
            str(vrl), "generated", n=1))[:40])
        return False
    vrl.write_text(content, encoding="utf-8")
    print(f"[WRITTEN] {vrl}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("yml", nargs="?", type=Path, help="transform YAML file")
    parser.add_argument("vrl", nargs="?", type=Path, help="output VRL file")
    parser.add_argument("--check", action="store_true", help="only verify that VRL files are up to date")
    args = parser.parse_args()

    if bool(args.yml) != bool(args.vrl):
        parser.error("give both <in.yml> and <out.vrl>, or none")
    pairs = [(args.yml, args.vrl)] if args.yml else [
        (DEPENDENCIES / yml, DEPENDENCIES / vrl) for yml, vrl in MAPPING.items()
    ]
    results = [generate(yml, vrl, args.check) for yml, vrl in pairs]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
