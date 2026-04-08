# Von Neumann Self-Replicating Automata -- Roadmap

## Current State
A functional cellular automata simulator with four automaton types (Langton Loop,
WireWorld, Game of Life Replicator, Brian's Brain). Has three GUI options
(matplotlib interactive, tkinter, quick-start launcher) and diagnostic tools.
Code is spread across 6 Python files with no package structure, no tests, and
significant overlap between `automata_interactive_gui.py` and `automata_gui.py`.
The core `self_replicating_automata.py` contains all automaton classes in a single
file with class aliases at the bottom for backward compatibility.

## Short-term Improvements
- [x] Add unit tests for each automaton's `step()` method -- verify known patterns
      (e.g., WireWorld clock, glider gun output) produce expected states
- [ ] Extract automaton classes into a proper package (`automata/langton.py`,
      `automata/wireworld.py`, etc.) instead of one monolith file
- [ ] Remove the dead `enhanced_character_NEW.py`-style aliases at the bottom of
      `self_replicating_automata.py` -- use `__init__.py` re-exports instead
- [ ] Add type hints to `automata_gui.py` and `automata_interactive_gui.py`
- [ ] Add input validation (grid size bounds, mutation rate range) in all GUIs
- [ ] Replace bare `print()` calls with `logging` throughout
- [x] Add `requirements.txt` or `pyproject.toml`

## Feature Enhancements
- [ ] Implement a true Langton Loop with the full 219-rule transition table
      (current `SimplifiedLangtonLoop` is an approximation)
- [ ] Add rule-table import from RLE/Golly format so users can load community
      patterns
- [ ] Support saving/loading simulation state (grid + generation) as `.npz`
- [ ] Add a generation counter and population graph panel to the interactive GUI
- [ ] Implement toroidal vs. bounded edge options (currently hardcoded toroidal)
- [ ] GPU-accelerated step via CuPy for large grids (300x300+)
- [ ] Add color map selection for each automaton type

## Long-term Vision
- [ ] Web-based viewer using WebAssembly (pyodide) or a JS frontend
- [ ] Plugin architecture: users drop a `.py` file defining `step()` and a color
      map and the GUI auto-discovers it
- [ ] Quantitative analysis tools: replication rate, population dynamics, entropy
- [ ] Research mode: parameter sweeps with CSV/HDF5 output for batch runs
- [ ] Compare simulated replication dynamics to biological data (PIEZO1 clustering)

## Technical Debt
- [ ] `automata_gui.py` and `automata_interactive_gui.py` share ~40% identical
      code -- extract shared logic into a `gui_common.py` module
- [ ] `display_diagnostic.py` and `automaton_diagnostic.py` overlap -- merge into
      a single diagnostic script
- [ ] The `diagnostics/` directory exists but its contents are unclear -- document
      or remove
- [x] No `.gitignore` -- snapshot PNGs and `__pycache__` are likely tracked
- [ ] Matplotlib backend selection is done ad-hoc in multiple files -- centralize
