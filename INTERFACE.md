# Self-Replicating Automata -- Interface Map

## Core Simulation
- **`self_replicating_automata.py`** -- All automaton classes
  - `CellularAutomaton` -- Base class (grid, step, neighborhood helpers)
  - `WireWorld` -- 4-state wire/electron simulation
  - `GameOfLifeReplicator` -- Conway's Life with Gosper glider gun
  - `SimplifiedLangtonLoop` -- Reduced-rule Langton loop
  - `BriansBrain` -- 3-state birth/dying/dead automaton
  - Aliases: `LangtonLoop`, `EvolvingLoop`, `VonNeumannConstructor`

## GUI Frontends
- **`automata_gui.py`** -- Tkinter + matplotlib GUI (`AutomatonGUI`)
  - Full control panel, file save, animation export
- **`automata_interactive_gui.py`** -- Pure matplotlib widget GUI (`InteractiveAutomatonGUI`)
  - RadioButtons, sliders, FuncAnimation-based loop
- **`quick_start.py`** -- Launcher that imports `InteractiveAutomatonGUI`

## Diagnostics
- **`automaton_diagnostic.py`** -- `AutomatonDiagnostic` class
  - Tests all automata, generates evolution PNGs and text report in `diagnostics/`
- **`display_diagnostic.py`** -- Matplotlib backend/refresh diagnostic
  - Tests animation, interactive mode, generates recommendations

## Tests
- **`test_automata.py`** -- Unit tests for all automaton classes (pytest)

## Data
- **`diagnostics/`** -- Generated diagnostic PNGs and text reports

## Dependencies
- numpy, matplotlib (see `requirements.txt`)
