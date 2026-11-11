"""Automaton catalogue and Python stepping for the web API, read from the repo's own classes.

Nothing here re-implements a rule: state counts, docstrings, source code, the Langton rule table and the Gosper gun
come from `self_replicating_automata`, colours from `automata_colors` (shared with the desktop GUIs), and every step
is the class's own `step()`. The browser engine (static/automata_engine.js) is checked against `run()`.
"""
import inspect
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import to_hex

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import self_replicating_automata as sra  # noqa: E402
from automata_colors import COLORMAP_COLORS, state_colors  # noqa: E402

from web.grid_codec import decode, encode  # noqa: E402

DEFAULT_SIZE = 150                         # constructor default (width=150, height=150) and the GUIs' start value
SIZES = list(range(50, 301, 50))           # the GUIs' grid-size slider: 50..300 in steps of 50
MAX_WORK = 1_000_000                       # cap on width * height * steps for one /run request (pure-Python loops)

# key -> class, alias (bottom of self_replicating_automata.py), labels in automata_interactive_gui.py ("interactive")
# and automata_gui.py ("tk"), the initialiser method the constructor calls, neighbourhood used by step(), and the
# state meanings given in the class docstrings / code comments.
AUTOMATA = {
    "langton_loop": dict(cls=sra.SimplifiedLangtonLoop, alias="LangtonLoop", interactive="Simple Loop",
                         tk="Langton's Loop", init="_initialize_loop", neighbourhood="von Neumann (4 neighbours)",
                         states=["background", "sheath", "core/data", "signal / constructor", "signal / constructor",
                                 "signal / constructor", "signal / constructor", "signal / constructor"]),
    "brians_brain": dict(cls=sra.BriansBrain, alias="EvolvingLoop", interactive="Brian's Brain",
                         tk="Evolving Loop (Brian's Brain)", init="_initialize_random", neighbourhood="Moore (8 neighbours)",
                         states=["dead", "alive", "dying"]),
    "game_of_life": dict(cls=sra.GameOfLifeReplicator, alias="VonNeumannConstructor", interactive="Game of Life",
                         tk="Von Neumann Constructor (Game of Life)", init="_initialize_glider_gun",
                         neighbourhood="Moore (8 neighbours)", states=["dead", "alive"]),
    "wireworld": dict(cls=sra.WireWorld, alias="WireWorld", interactive="Wire World", tk="Wire World",
                      init="_initialize_wire", neighbourhood="Moore (8 neighbours)",
                      states=["empty", "wire (conductor)", "electron head", "electron tail"]),
}


def _probe(cls):
    """A small instance (numpy seeded, so the random initialiser is reproducible)."""
    np.random.seed(0)
    return cls(DEFAULT_SIZE, DEFAULT_SIZE)


def colours(key: str) -> dict:
    """State colours: state i gets the i-th colour of the GUI's list (grey beyond it), exactly as the desktop GUIs
    draw them (automata_colors.colormap_and_norm) and as the colour key in README_automata.md describes."""
    alias = AUTOMATA[key]["alias"]
    n = _probe(AUTOMATA[key]["cls"]).num_states
    return {"color_names": COLORMAP_COLORS[alias][:n], "colors": [to_hex(c) for c in state_colors(alias, n)]}


def _source(fn) -> str:
    return inspect.cleandoc("\n" + inspect.getsource(fn)) if fn else ""


def langton_rules() -> list:
    """The SimplifiedLangtonLoop rule table as [C, N, E, S, W, new] rows, in definition order."""
    return [[int(v) for v in k] + [int(new)] for k, new in _probe(sra.SimplifiedLangtonLoop).rules.items()]


def gosper_gun() -> dict:
    """The pattern GameOfLifeReplicator._initialize_glider_gun writes, read back from a fresh grid."""
    g = _probe(sra.GameOfLifeReplicator).grid
    ys, xs = np.nonzero(g)
    y0, x0 = int(ys.min()), int(xs.min())
    block = g[y0:ys.max() + 1, x0:xs.max() + 1]
    return {"origin": [x0, y0], "rows": ["".join("O" if v else "." for v in row) for row in block],
            "cells": int(block.sum())}


def entry(key: str) -> dict:
    a = AUTOMATA[key]
    cls = a["cls"]
    probe = _probe(cls)
    out = {
        "key": key, "class": cls.__name__, "alias": a["alias"], "label": a["interactive"], "tk_label": a["tk"],
        "num_states": probe.num_states, "state_names": a["states"][:probe.num_states],
        "neighbourhood": a["neighbourhood"], "doc": inspect.getdoc(cls) or "",
        "init_doc": inspect.getdoc(getattr(cls, a["init"])) or "", "init_method": a["init"],
        "step_source": _source(cls.step), "init_source": _source(getattr(cls, a["init"])),
        "default_active": int(np.count_nonzero(probe.grid)),
        **colours(key),
    }
    if key == "langton_loop":
        out["rules"] = langton_rules()
        out["rules_source"] = _source(cls._create_rule_table)
    if key == "game_of_life":
        out["gun"] = gosper_gun()
    return out


def catalogue() -> list:
    """Every automaton the repo implements, in the order of the interactive GUI's radio buttons."""
    return [entry(k) for k in AUTOMATA]


def make(key: str, width: int, height: int, seed: int | None = 0, mutation_rate: float = 0.0,
         mutation_seed: int = 0):
    """The class's own constructor at this size (numpy seeded first, for Brian's Brain's random start; Brian's Brain
    also takes its mutation rate and the seed of its own mutation RandomState)."""
    if seed is not None:
        np.random.seed(seed)
    if key == "brians_brain":
        return AUTOMATA[key]["cls"](width, height, mutation_rate=mutation_rate, seed=mutation_seed)
    return AUTOMATA[key]["cls"](width, height)


def run(key: str, cells: str, width: int, height: int, steps: int, mutation_rate: float = 0.0, seed: int = 0) -> dict:
    """Step a grid with the real Python class and return the encoded result."""
    if key not in AUTOMATA:
        raise KeyError(key)
    if width * height * max(steps, 1) > MAX_WORK:
        raise ValueError(f"too much work: width*height*steps must be <= {MAX_WORK}")
    a = make(key, max(width, 50), max(height, 50), 0, mutation_rate, seed)
    grid = decode(cells, width, height)
    if grid.max(initial=0) >= a.num_states:
        raise ValueError("cell state out of range for this automaton")
    a.width, a.height = width, height
    a.grid = grid
    a.generation = 0
    for _ in range(steps):
        a.step()
    n = a.grid.size
    vals, counts = np.unique(a.grid, return_counts=True)
    p = counts / counts.sum()
    return {"key": key, "width": width, "height": height, "generation": a.generation, "cells": encode(a.grid),
            "stats": {"active_cells": int(np.count_nonzero(a.grid)), "total_cells": int(n),
                      "density": float(np.count_nonzero(a.grid) / n * 100),
                      "complexity": float(-np.sum(p * np.log2(p + 1e-10)))}}
