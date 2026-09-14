from __future__ import annotations

import argparse
from pathlib import Path

from .engine import adjudicate, write_adjudications
from .money import instant


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="freight-audit")
    parser.add_argument("--input", default="examples/input")
    parser.add_argument("--output", default="build/adjudications.jsonl")
    parser.add_argument("--as-of")
    args = parser.parse_args(argv)
    as_of = instant(args.as_of) if args.as_of else None
    rows = adjudicate(Path(args.input), as_of)
    write_adjudications(rows, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
