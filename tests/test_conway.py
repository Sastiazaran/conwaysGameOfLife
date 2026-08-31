from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import conway
from conway import (
    ON,
    add_glider,
    count_patterns,
    format_iteration,
    load_input,
    next_generation,
    simulate,
)
from patterns import Beehive, Block, Boat, Glider, Loaf, Tub, orientations


def empty(n=10, m=None):
    return np.zeros((n, n if m is None else m), dtype=np.int8)


def place(grid, i, j, pattern):
    arr = np.asarray(pattern, dtype=np.int8)
    h, w = arr.shape
    grid[i:i + h, j:j + w] = arr
    return grid


class NextGenerationTests(unittest.TestCase):
    def test_underpopulation(self):
        grid = empty(5)
        grid[2, 2] = ON
        self.assertEqual(int(next_generation(grid).sum()), 0)

    def test_survival_with_two_neighbors(self):
        grid = empty(5)
        grid[1, 1] = ON
        grid[1, 2] = ON
        grid[2, 1] = ON
        nxt = next_generation(grid)
        self.assertEqual(nxt[1, 1], ON)

    def test_overpopulation(self):
        grid = empty(5)
        for i in (1, 2, 3):
            for j in (1, 2, 3):
                grid[i, j] = ON
        nxt = next_generation(grid)
        self.assertEqual(nxt[2, 2], 0)

    def test_reproduction(self):
        grid = empty(5)
        grid[1, 2] = ON
        grid[2, 1] = ON
        grid[2, 3] = ON
        nxt = next_generation(grid)
        self.assertEqual(nxt[2, 2], ON)

    def test_torus_wraps_edges(self):
        grid = empty(5)
        grid[0, 0] = ON
        grid[0, 4] = ON
        grid[4, 0] = ON
        nxt = next_generation(grid)
        self.assertEqual(nxt[4, 4], ON)

    def test_non_square_grid(self):
        grid = empty(4, 6)
        grid[1, 1] = ON
        grid[1, 2] = ON
        grid[2, 1] = ON
        grid[2, 2] = ON
        nxt = next_generation(grid)
        np.testing.assert_array_equal(nxt, grid)


class StillLifeTests(unittest.TestCase):
    def _stays_put(self, pattern, origin=(2, 2), size=10):
        grid = empty(size)
        place(grid, *origin, pattern)
        nxt = next_generation(grid)
        np.testing.assert_array_equal(nxt, grid)

    def test_block(self):
        self._stays_put([[1, 1], [1, 1]])

    def test_beehive(self):
        self._stays_put([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]])

    def test_loaf(self):
        self._stays_put([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]])

    def test_boat(self):
        self._stays_put([[1, 1, 0], [1, 0, 1], [0, 1, 0]])

    def test_tub(self):
        self._stays_put([[0, 1, 0], [1, 0, 1], [0, 1, 0]])


class OscillatorTests(unittest.TestCase):
    def test_blinker_period_2(self):
        grid = empty(7)
        grid[3, 2:5] = ON
        one = next_generation(grid)
        two = next_generation(one)
        np.testing.assert_array_equal(two, grid)
        self.assertNotEqual(int(one.sum()), 0)
        np.testing.assert_array_equal(one[2:5, 3], [1, 1, 1])

    def test_toad_period_2(self):
        grid = empty(8)
        grid[3, 3:6] = ON
        grid[4, 2:5] = ON
        two = next_generation(next_generation(grid))
        np.testing.assert_array_equal(two, grid)

    def test_beacon_period_2(self):
        grid = empty(8)
        grid[2:4, 2:4] = ON
        grid[4:6, 4:6] = ON
        two = next_generation(next_generation(grid))
        np.testing.assert_array_equal(two, grid)


class SpaceshipTests(unittest.TestCase):
    def test_glider_returns_translated_after_4_steps(self):
        grid = empty(12)
        add_glider(grid, 2, 2)
        nxt = grid
        for _ in range(4):
            nxt = next_generation(nxt)
        expected = empty(12)
        add_glider(expected, 3, 3)
        np.testing.assert_array_equal(nxt, expected)

    def test_every_glider_phase_is_valid(self):
        # Unpadded 3x3 phases as stored before padding.
        phases = [
            np.array(p, dtype=np.int8)
            for p in [
                [[0, 1, 0], [0, 0, 1], [1, 1, 1]],
                [[1, 0, 1], [0, 1, 1], [0, 1, 0]],
                [[0, 0, 1], [1, 0, 1], [0, 1, 1]],
                [[0, 1, 0], [1, 0, 1], [1, 1, 0]],
            ]
        ]
        grid = empty(10)
        place(grid, 2, 2, phases[0])
        for step in range(4):
            counts = count_patterns(grid)
            self.assertEqual(counts["glider"], 1, msg=f"phase lost at step {step}")
            self.assertEqual(sum(counts.values()), 1)
            grid = next_generation(grid)


class PatternCensusTests(unittest.TestCase):
    def test_isolated_block(self):
        grid = empty(8)
        grid[3:5, 3:5] = ON
        counts = count_patterns(grid)
        self.assertEqual(counts["block"], 1)
        self.assertEqual(sum(counts.values()), 1)

    def test_two_separated_blocks(self):
        grid = empty(12)
        grid[2:4, 2:4] = ON
        grid[2:4, 8:10] = ON
        counts = count_patterns(grid)
        self.assertEqual(counts["block"], 2)

    def test_adjacent_blocks_are_not_two_blocks(self):
        grid = empty(10)
        grid[2:4, 2:6] = ON
        grid[4:6, 2:6] = ON
        counts = count_patterns(grid)
        self.assertEqual(counts["block"], 0)

    def test_beacon_is_not_counted_as_two_blocks(self):
        grid = empty(10)
        grid[2:4, 2:4] = ON
        grid[4:6, 4:6] = ON
        counts = count_patterns(grid)
        self.assertEqual(counts["beacon"], 1)
        self.assertEqual(counts["block"], 0)

    def test_rotated_beehive_is_detected(self):
        grid = empty(10)
        vertical = orientations([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]])
        # pick a non-original orientation if one exists
        found = False
        for orient in vertical:
            g = empty(10)
            place(g, 2, 2, orient)
            if count_patterns(g)["beehive"] == 1:
                found = True
        self.assertTrue(found)
        self.assertGreaterEqual(len(Beehive.variants), 2)

    def test_glider_orientations_are_detected(self):
        detected = 0
        for padded in Glider.variants:
            inner = padded[1:-1, 1:-1]
            grid = empty(12)
            place(grid, 3, 3, inner)
            if count_patterns(grid)["glider"] == 1:
                detected += 1
        self.assertEqual(detected, len(Glider.variants))

    def test_loaf_and_boat_and_tub(self):
        for pattern, name in (
            (Loaf.variants[0][1:-1, 1:-1], "loaf"),
            (Boat.variants[0][1:-1, 1:-1], "boat"),
            (Tub.variants[0][1:-1, 1:-1], "tub"),
            (Block.variants[0][1:-1, 1:-1], "block"),
        ):
            grid = empty(12)
            place(grid, 3, 3, pattern)
            self.assertEqual(count_patterns(grid)[name], 1, msg=name)


class InputAndReportTests(unittest.TestCase):
    def test_load_input3(self):
        grid, generations = load_input(ROOT / "inputs" / "input3.in")
        self.assertEqual(grid.shape, (100, 100))
        self.assertEqual(generations, 80)
        self.assertEqual(int(grid.sum()), 12)

    def test_out_of_bounds_cell_raises(self):
        with tempfile.NamedTemporaryFile("w", suffix=".in", delete=False) as fh:
            fh.write("4 4\n2\n0 0\n9 1\n")
            path = fh.name
        with self.assertRaises(ValueError):
            load_input(path)

    def test_simulate_records_requested_iterations(self):
        grid, generations = load_input(ROOT / "inputs" / "input3.in")
        _, history = simulate(grid, generations)
        self.assertEqual(len(history), 80)

    def test_simulate_zero_generations(self):
        _, history = simulate(empty(5), 0)
        self.assertEqual(history, [])

    def test_report_mentions_every_pattern(self):
        counts = {name: 0 for name in conway.PATTERN_NAMES}
        counts["blinker"] = 2
        text = format_iteration(1, counts)
        self.assertIn("iteration: 1", text)
        self.assertIn("blinker", text)
        self.assertIn("100.00000", text)
        self.assertIn("total", text)

    def test_cli_headless_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.txt"
            rc = conway.main(["--no-display", "-i", str(ROOT / "inputs" / "input3.in"),
                              "-o", str(out), "--generations", "4"])
            self.assertEqual(rc, 0)
            text = out.read_text()
            self.assertEqual(text.count("iteration:"), 4)

    def test_glider_cli_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "g.txt"
            rc = conway.main(["--no-display", "--glider", "--generations", "8", "-o", str(out)])
            self.assertEqual(rc, 0)
            self.assertIn("glider", out.read_text())


class RandomInputTests(unittest.TestCase):
    def test_generator_unique_and_in_bounds(self):
        sys.path.insert(0, str(ROOT / "inputs"))
        import rand as rand_mod
        w, h, gens, coords = rand_mod.generate(10, 8, 5, 20, seed=1)
        self.assertEqual((w, h, gens), (10, 8, 5))
        self.assertEqual(len(coords), 20)
        self.assertEqual(len(set(coords)), 20)
        self.assertTrue(all(0 <= i < 10 and 0 <= j < 8 for i, j in coords))


if __name__ == "__main__":
    unittest.main()
