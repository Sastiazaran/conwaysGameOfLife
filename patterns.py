"""Named Game of Life patterns used for census / detection.

Each pattern stores every distinct rotation, reflection, and (for oscillators
and spaceships) phase so isolated copies can be recognized regardless of
orientation.
"""

from __future__ import annotations

import numpy as np

ON = 1
OFF = 0


def _as_array(pattern):
    return np.asarray(pattern, dtype=np.int8)


def orientations(pattern):
    """Return unique rotations and reflections of a 2-D pattern."""
    arr = _as_array(pattern)
    seen = set()
    variants = []
    for flipped in (arr, np.fliplr(arr)):
        for k in range(4):
            rot = np.rot90(flipped, k)
            key = (rot.shape, rot.tobytes())
            if key not in seen:
                seen.add(key)
                variants.append(rot)
    return variants


class Pattern:
    """A named Life object with one or more phases."""

    def __init__(self, name, phases):
        self.name = name
        seen = set()
        variants = []
        for phase in phases:
            for orient in orientations(phase):
                padded = np.pad(_as_array(orient), 1)
                key = (padded.shape, padded.tobytes())
                if key not in seen:
                    seen.add(key)
                    variants.append(padded)
        # Prefer larger templates first so a big object is not counted as
        # several smaller ones that share its bounding box.
        variants.sort(key=lambda a: int(np.count_nonzero(a)), reverse=True)
        self.variants = variants

    @property
    def live_cells(self):
        return max(int(np.count_nonzero(v)) for v in self.variants)


# ---------------------------------------------------------------------------
# Still lifes
# ---------------------------------------------------------------------------

block = [[ON, ON],
         [ON, ON]]
Block = Pattern("block", [block])

beehive = [[OFF, ON, ON, OFF],
           [ON, OFF, OFF, ON],
           [OFF, ON, ON, OFF]]
Beehive = Pattern("beehive", [beehive])

loaf = [[OFF, ON, ON, OFF],
        [ON, OFF, OFF, ON],
        [OFF, ON, OFF, ON],
        [OFF, OFF, ON, OFF]]
Loaf = Pattern("loaf", [loaf])

boat = [[ON, ON, OFF],
        [ON, OFF, ON],
        [OFF, ON, OFF]]
Boat = Pattern("boat", [boat])

tub = [[OFF, ON, OFF],
       [ON, OFF, ON],
       [OFF, ON, OFF]]
Tub = Pattern("tub", [tub])

# ---------------------------------------------------------------------------
# Oscillators
# ---------------------------------------------------------------------------

blinker_phases = [
    [[ON],
     [ON],
     [ON]],
    [[ON, ON, ON]],
]
Blinker = Pattern("blinker", blinker_phases)

toad_phases = [
    [[OFF, OFF, ON, OFF],
     [ON, OFF, OFF, ON],
     [ON, OFF, OFF, ON],
     [OFF, ON, OFF, OFF]],
    [[OFF, ON, ON, ON],
     [ON, ON, ON, OFF]],
]
Toad = Pattern("toad", toad_phases)

beacon_phases = [
    [[ON, ON, OFF, OFF],
     [ON, ON, OFF, OFF],
     [OFF, OFF, ON, ON],
     [OFF, OFF, ON, ON]],
    [[ON, ON, OFF, OFF],
     [ON, OFF, OFF, OFF],
     [OFF, OFF, OFF, ON],
     [OFF, OFF, ON, ON]],
]
Beacon = Pattern("beacon", beacon_phases)

# ---------------------------------------------------------------------------
# Spaceships (canonical phases; orientations() covers direction)
# ---------------------------------------------------------------------------

# Four phases of a south-east glider. The previous repo listed only three
# frames and one of them was not a glider.
glider_phases = [
    [[OFF, ON, OFF],
     [OFF, OFF, ON],
     [ON, ON, ON]],
    [[ON, OFF, ON],
     [OFF, ON, ON],
     [OFF, ON, OFF]],
    [[OFF, OFF, ON],
     [ON, OFF, ON],
     [OFF, ON, ON]],
    [[OFF, ON, OFF],
     [ON, OFF, ON],
     [ON, ON, OFF]],
]
Glider = Pattern("glider", glider_phases)

lwss_phases = [
    [[ON, OFF, OFF, ON, OFF],
     [OFF, OFF, OFF, OFF, ON],
     [ON, OFF, OFF, OFF, ON],
     [OFF, ON, ON, ON, ON]],
    [[OFF, OFF, ON, ON, OFF],
     [ON, ON, OFF, ON, ON],
     [ON, ON, ON, ON, OFF],
     [OFF, ON, ON, OFF, OFF]],
    [[OFF, ON, ON, ON, ON],
     [ON, OFF, OFF, OFF, ON],
     [OFF, OFF, OFF, OFF, ON],
     [ON, OFF, OFF, ON, OFF]],
    [[OFF, ON, ON, OFF, OFF],
     [ON, ON, ON, ON, OFF],
     [ON, ON, OFF, ON, ON],
     [OFF, OFF, ON, ON, OFF]],
]
Lwss = Pattern("light-weight spaceship", lwss_phases)

still = [Block, Beehive, Loaf, Boat, Tub]
oscillators = [Blinker, Toad, Beacon]
spaceships = [Glider, Lwss]

# Larger objects first so an isolated LWSS is not also read as smaller debris.
all_patterns = sorted(
    still + oscillators + spaceships,
    key=lambda p: p.live_cells,
    reverse=True,
)

PATTERN_NAMES = [
    "block",
    "beehive",
    "loaf",
    "boat",
    "tub",
    "blinker",
    "toad",
    "beacon",
    "glider",
    "light-weight spaceship",
]

# Backwards-compatible aliases used by older snippets.
allPatterns = all_patterns
oscilators = oscillators
stillList = still
counters = {name: 0 for name in PATTERN_NAMES}
patterns = Pattern
