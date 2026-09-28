#!/usr/bin/env python3
"""
Test runner for the OSIR test suite ("handler" entry point).

Runs every package test folder and prints a per-package summary:

    python tests/run_all.py            # whole suite
    python tests/run_all.py -k active  # pytest -k filter
    python tests/run_all.py osir_api   # only one package folder

Exit code is non-zero if any package fails.
"""
import argparse
import subprocess
import sys
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent

# One entry per package, in a stable order. The label is shown in the
# summary; the path is the folder pytest runs.
PACKAGES = [
    ("osir_lib",     TESTS_ROOT / "osir_lib"),
    ("osir_service", TESTS_ROOT / "osir_service"),
    ("osir_api",     TESTS_ROOT / "osir_api"),
    ("osir_client",  TESTS_ROOT / "osir_client"),
    ("osir_vrl",     TESTS_ROOT / "osir_vrl"),
]


def run_package(name: str, path: Path, extra_args: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "pytest", str(path), "-q", "--no-header"]
    if extra_args:
        cmd += extra_args
    return subprocess.run(cmd, cwd=TESTS_ROOT.parent, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the whole OSIR test suite, package by package.")
    parser.add_argument("packages", nargs="*", help="optional subset of package names (e.g. osir_api)")
    parser.add_argument("-k", dest="keyword", default=None, help="pytest -k expression")
    parser.add_argument("-v", "--verbose", action="store_true", help="show pytest output live")
    args = parser.parse_args()

    selected = [(n, p) for n, p in PACKAGES if not args.packages or n in args.packages]
    unknown = set(args.packages) - {n for n, _ in PACKAGES}
    if unknown:
        parser.error(f"unknown package(s): {sorted(unknown)} — choose among {[n for n, _ in PACKAGES]}")

    extra = []
    if args.keyword:
        extra += ["-k", args.keyword]
    if args.verbose:
        extra += ["-v"]

    print("=" * 62)
    print("OSIR test suite")
    print("=" * 62)

    failures = {}
    for name, path in selected:
        if not path.is_dir():
            print(f"\n[{name}] no test folder, skipped")
            continue
        print(f"\n[{name}] running {path.relative_to(TESTS_ROOT)} ...")
        result = run_package(name, path, extra)
        if args.verbose:
            print(result.stdout)
        # Extract pytest's own one-line summary (last non-empty line of stdout).
        summary = [line for line in result.stdout.splitlines() if line.strip()]
        print(f"    -> {summary[-1] if summary else 'no output'}")
        if result.returncode != 0:
            failures[name] = result.stdout + result.stderr

    print("\n" + "=" * 62)
    print("Summary")
    print("-" * 62)
    status = True
    for name, _ in selected:
        if name in failures:
            print(f"  {name:14} FAIL")
            status = False
        else:
            print(f"  {name:14} PASS")
    print("=" * 62)

    if failures:
        print("\nFailing details:\n")
        for name, output in failures.items():
            print(f"--- {name} " + "-" * 50)
            print(output)
        return 1
    print("All packages passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
