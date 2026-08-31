"""Generate a random Game of Life input file."""

from __future__ import annotations

import argparse
from pathlib import Path
import random


def generate(width, height, generations, cells, seed=None):
    rng = random.Random(seed)
    seen = set()
    max_cells = width * height
    n = min(cells, max_cells)
    while len(seen) < n:
        seen.add((rng.randrange(width), rng.randrange(height)))
    return width, height, generations, sorted(seen)


def write_input(path, width, height, generations, coords):
    path = Path(path)
    with path.open("w") as fh:
        fh.write(f"{width} {height}\n")
        fh.write(f"{generations}\n")
        for i, j in coords:
            fh.write(f"{i} {j}\n")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Random Game of Life input generator")
    parser.add_argument("-o", "--output", default="input.txt", help="output path")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--cells", type=int, default=1000, help="number of unique live cells")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    width, height, generations, coords = generate(
        args.width, args.height, args.generations, args.cells, seed=args.seed
    )
    write_input(args.output, width, height, generations, coords)
    print(f"wrote {len(coords)} cells to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
