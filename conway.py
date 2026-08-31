"""
conway.py
A Python implementation of Conway's Game of Life with a pattern census.

The grid is toroidal (edges wrap). Each generation an isolated copy of a
known still life, oscillator, or spaceship is counted and written to a report.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from patterns import PATTERN_NAMES, all_patterns

ON = 1
OFF = 0

ROOT = Path(__file__).resolve().parent


def random_grid(n, p_on=0.2, rng=None):
    """Return an n x n grid with the given probability of a live cell."""
    rng = np.random.default_rng(rng)
    return rng.choice([ON, OFF], size=(n, n), p=[p_on, 1.0 - p_on]).astype(np.int8)


def add_glider(grid, i=1, j=1):
    """Place a south-east glider with top-left cell at (i, j)."""
    glider = np.array([[0, 1, 0],
                       [0, 0, 1],
                       [1, 1, 1]], dtype=np.int8)
    grid[i:i + 3, j:j + 3] = glider
    return grid


def load_input(path):
    """Load width, height, generation count, and live cells from an input file.

    Format:
        <width> <height>
        <generations>
        <row> <col>
        ...
    """
    path = Path(path)
    with path.open() as fh:
        lines = [line.strip() for line in fh if line.strip()]

    if len(lines) < 2:
        raise ValueError(f"{path}: expected at least a size line and a generation count")

    try:
        width, height = (int(x) for x in lines[0].split())
        generations = int(lines[1])
    except ValueError as exc:
        raise ValueError(f"{path}: invalid header") from exc

    if width <= 0 or height <= 0:
        raise ValueError(f"{path}: grid size must be positive")
    if generations < 0:
        raise ValueError(f"{path}: generation count cannot be negative")

    grid = np.zeros((width, height), dtype=np.int8)
    for line in lines[2:]:
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"{path}: expected 'row col', got {line!r}")
        i, j = int(parts[0]), int(parts[1])
        if not (0 <= i < width and 0 <= j < height):
            raise ValueError(f"{path}: cell ({i}, {j}) is outside {width}x{height}")
        grid[i, j] = ON
    return grid, generations


def next_generation(grid):
    """Apply the B3/S23 rule on a toroidal grid."""
    neighbors = sum(
        np.roll(np.roll(grid, di, 0), dj, 1)
        for di in (-1, 0, 1)
        for dj in (-1, 0, 1)
        if (di, dj) != (0, 0)
    )
    survive = (grid == ON) & ((neighbors == 2) | (neighbors == 3))
    born = (grid == OFF) & (neighbors == 3)
    return np.where(survive | born, ON, OFF).astype(np.int8)


def count_patterns(grid):
    """Count isolated copies of each known pattern on the current grid.

    A match requires the pattern cells plus a one-cell dead border, so objects
    that share a neighborhood are not counted as several overlapping patterns.
    """
    g = np.asarray(grid, dtype=np.int8)
    rows, cols = g.shape
    occupied = np.zeros((rows, cols), dtype=bool)
    counts = {name: 0 for name in PATTERN_NAMES}
    windows_by_shape = {}

    for pattern in all_patterns:
        for padded in pattern.variants:
            ph, pw = padded.shape
            if ph > rows or pw > cols:
                continue
            key = (ph, pw)
            if key not in windows_by_shape:
                windows_by_shape[key] = np.lib.stride_tricks.sliding_window_view(g, key)
            matches = np.all(windows_by_shape[key] == padded, axis=(2, 3))
            if not matches.any():
                continue
            for i, j in np.argwhere(matches):
                region = occupied[i:i + ph, j:j + pw]
                if region.any():
                    continue
                counts[pattern.name] += 1
                region[:] = True
    return counts


def format_iteration(iteration, counts):
    """Render one census block in the report format."""
    total = sum(counts.values())
    lines = [f"iteration: {iteration}"]
    for name in PATTERN_NAMES:
        val = counts[name]
        percent = (float(val) / total * 100.0) if total else 0.0
        lines.append(
            f"|{name.ljust(24)}|\t{str(val).ljust(6)}\t|\t{percent:.5f}\t|"
        )
    lines.append(f"|{'total'.ljust(24)}|\t{str(total).ljust(6)}\t|\t{'':<7}\t|")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_report(path, history):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for iteration, counts in enumerate(history, start=1):
            fh.write(format_iteration(iteration, counts))


def simulate(grid, generations):
    """Run `generations` recorded iterations, starting from the initial grid.

    Iteration 1 is the initial configuration. Each subsequent iteration is one
    Game of Life step. Returns (final_grid, list of per-iteration counts).
    """
    grid = np.array(grid, dtype=np.int8, copy=True)
    history = []
    steps = max(int(generations), 0)
    for iteration in range(steps):
        history.append(count_patterns(grid))
        if iteration + 1 < steps:
            grid = next_generation(grid)
    return grid, history


def _has_display():
    import os
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def animate(grid, generations, interval, output=None):
    """Show (or save) a matplotlib animation while writing the census report."""
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    grid = np.array(grid, dtype=np.int8, copy=True)
    history = []
    steps = max(int(generations), 0)
    state = {"grid": grid, "iteration": 0}

    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation="nearest", vmin=0, vmax=1, cmap="binary")
    ax.set_xticks([])
    ax.set_yticks([])
    title = ax.set_title("generation 0")

    def update(_frame):
        if state["iteration"] >= steps:
            return img,

        history.append(count_patterns(state["grid"]))
        state["iteration"] += 1
        title.set_text(f"generation {state['iteration'] - 1}")
        img.set_data(state["grid"])

        if state["iteration"] < steps:
            state["grid"] = next_generation(state["grid"])
        elif output:
            write_report(output, history)
        return img,

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=max(steps, 1),
        interval=interval,
        blit=False,
        repeat=False,
        cache_frame_data=False,
    )
    plt.show()
    # If the window closed before the last frame flushed the report:
    if output and len(history) < steps:
        remaining = steps - len(history)
        for _ in range(remaining):
            history.append(count_patterns(state["grid"]))
            state["grid"] = next_generation(state["grid"])
        write_report(output, history[:steps])
    return ani


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run Conway's Game of Life and census known patterns."
    )
    parser.add_argument(
        "-i", "--input",
        default=str(ROOT / "inputs" / "input1.in"),
        help="initial configuration file",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="census report path (default: reports/<input-stem>.txt)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=50,
        help="animation interval in milliseconds",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="skip the animation window and only write the report",
    )
    parser.add_argument(
        "--random",
        type=int,
        metavar="N",
        default=None,
        help="ignore --input and start from an NxN random grid",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=None,
        help="override the generation count from the input file",
    )
    parser.add_argument(
        "--glider",
        action="store_true",
        help="seed a glider on an empty 50x50 grid (or --random size)",
    )
    return parser.parse_args(argv)


def default_report_path(input_path):
    stem = Path(input_path).stem
    name = stem.replace("input", "report") if stem.startswith("input") else f"{stem}.txt"
    if not name.endswith(".txt"):
        name += ".txt"
    return ROOT / "reports" / name


def main(argv=None):
    args = parse_args(argv)

    if args.glider:
        n = args.random or 50
        grid = np.zeros((n, n), dtype=np.int8)
        add_glider(grid)
        generations = args.generations if args.generations is not None else 40
        input_label = "glider"
    elif args.random:
        grid = random_grid(args.random)
        generations = args.generations if args.generations is not None else 50
        input_label = f"random{args.random}"
    else:
        grid, generations = load_input(args.input)
        if args.generations is not None:
            generations = args.generations
        input_label = args.input

    output = args.output or str(default_report_path(input_label))
    headless = args.no_display or not _has_display()

    if headless:
        _, history = simulate(grid, generations)
        write_report(output, history)
        print(f"wrote {len(history)} iterations to {output}")
        return 0

    animate(grid, generations, args.interval, output=output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
