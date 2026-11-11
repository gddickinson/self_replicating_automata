# Self-Replicating Automata -- Interface Map

## Core Simulation
- **`self_replicating_automata.py`** -- All automaton classes
  - `CellularAutomaton` -- Base class (grid, step, neighborhood helpers)
  - `WireWorld` -- 4-state wire/electron simulation
  - `GameOfLifeReplicator` -- Conway's Life with Gosper glider gun
  - `SimplifiedLangtonLoop` -- Reduced-rule Langton loop (12 hand-written rules generalised by `_generalised_rule`)
  - `BriansBrain` -- 3-state birth/dying/dead automaton; `mutation_rate` + `seed` (own RandomState), `_mutate()`
  - Aliases: `LangtonLoop`, `EvolvingLoop`, `VonNeumannConstructor`

- **`automata_colors.py`** -- `COLORMAP_COLORS` (colour list per alias), `state_colors()`, `colormap_and_norm()`
  (ListedColormap + BoundaryNorm so state i is drawn with colour i); used by both GUIs, the diagnostic and the web

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
- **`tests/test_regressions.py`** -- Regression tests for the fixed bugs (GUI colours, Langton loop, mutations,
  small WireWorld grids, docs, .gitignore)
- **`tests/test_web.py`** -- Web API tests, static build, fixture-currency checks (inits + runs via POST /api/run), node test
- **`tests/fixtures/engine_fixtures.json`** -- Python reference grids for the JS engine (do not edit; regenerate)

## Web Interface (FastAPI + static ES-module front end; also the GitHub Pages site)
- **`run_web.py`** -- start the local web app on 127.0.0.1:8140 (imports `web.app:app`)
- **`requirements-web.txt`** -- pinned web/test dependencies
- **`web/app.py`** -- FastAPI app: `/api/info`, `/api/automata`, POST `/api/run`; `STATIC_ENDPOINTS`
- **`web/catalogue.py`** -- `AUTOMATA` (key -> class, alias, GUI labels, state names), `catalogue()`, `entry()`,
  `colours()`, `langton_rules()`, `gosper_gun()`, `make()`, `run()`: everything read from the Python classes
- **`web/grid_codec.py`** -- `encode()`/`decode()`: base-36 one-char-per-cell grid text (shared with the JS engine)
- **`web/static/`** -- front end, no build step
  - `index.html`, `style.css` (shared kit theme), `style_app.css` (accents + page styles), `core.js` (kit router/helpers)
  - `main.js` (lazy pages, footer mode), `static_api.js` (answers `api()` from exported JSON; refuses POST /run)
  - `automata_engine.js` -- `STEP` (one port per class's `step()`), Brian's Brain mutations, `makeState()`, `step()`, `run()`, codec, `stats()`
  - `automata_init.js` -- `INIT` (ports of each initialiser), `initialCells()`, `LANGTON_RULES`, `GUN`,
    `mt19937()` + `randint()` + `randomSample()` (numpy legacy RandomState, so seeds match Python)
  - `automata_engine.test.mjs` -- node test: JS == Python fixtures
  - pages: `home.js`, `lab.js` (+ `lab_view.js` canvas/drawing, `lab_check.js` Python cross-check), `automata.js`,
    `background.js` (README_automata.md theory), `about.js`; `bg.js` animated Brian's Brain background
- **`scripts/build_static.py`** -- export the static site to `site/`
- **`scripts/screenshots.py`** -- Playwright smoke test of routes + README PNGs in `docs/img/`
- **`scripts/make_engine_fixtures.py`** -- regenerate `tests/fixtures/engine_fixtures.json`
- **`.github/workflows/pages.yml`** -- test, build and publish the static site on push to main

Data flow: `self_replicating_automata.py` classes -> `web/catalogue.py` -> `/api/*` (JSON, exported for the static
site) -> pages; the grid itself is stepped in the browser by `automata_engine.js`, verified against the fixtures.

## Data
- **`diagnostics/`** -- Generated diagnostic PNGs and text reports

## Dependencies
- numpy, matplotlib (see `requirements.txt`); web: `requirements-web.txt`
