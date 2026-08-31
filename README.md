# Conway's Game of Life

Python implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
with a census of common still lifes, oscillators, and spaceships.

The universe is a **toroidal** (wrap-around) grid. Each recorded iteration
counts isolated copies of known objects and appends them to a report file.

## Setup

```bash
pip install -r requirements.txt
```

## Input format

```
<width> <height>
<generations>
<row> <col>
...
```

Rows and columns are 0-based. `generations` is the number of iterations to
record, starting with the initial configuration.

## Usage

```bash
# Headless census (writes reports/report3.txt)
python conway.py -i inputs/input3.in --no-display

# Animate when a display is available
python conway.py -i inputs/input1.in

# Seed a glider on an empty grid
python conway.py --glider --generations 40 --no-display -o reports/glider.txt

# Random soup
python conway.py --random 80 --generations 50 --no-display
```

Generate a new random input:

```bash
python inputs/rand.py -o inputs/custom.in --width 100 --height 100 --cells 800 --generations 120
```

## Patterns detected

| Still lifes | Oscillators | Spaceships |
| --- | --- | --- |
| block, beehive, loaf, boat, tub | blinker, toad, beacon | glider, light-weight spaceship |

Rotations, reflections, and oscillator/spaceship phases are recognized.
An object is counted only when it has a one-cell dead border, so overlapping
debris is not reported as several smaller patterns.

## Tests

```bash
python -m unittest discover -s tests -v
```
