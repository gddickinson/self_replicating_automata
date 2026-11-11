# Session log

## 2026-11-11 -- Web interface and static GitHub Pages site (branch `web-interface`)
- Added a FastAPI web app (`web/`, `run_web.py`, port 8140) and a no-build ES-module front end that is also the static
  GitHub Pages site (`scripts/build_static.py`, `.github/workflows/pages.yml`). Pages: home, lab, automata, background,
  about.
- Ported all four automaton classes (`step()` and each constructor's initial pattern) to JS
  (`web/static/automata_engine.js`, `automata_init.js`), including numpy's legacy MT19937 `randint` so Brian's Brain's
  random start matches `np.random.seed(seed)`. `scripts/make_engine_fixtures.py` writes Python reference grids
  (24 initial grids over sizes 50-300 and seeds, 13 run cases); the node test reproduces all of them exactly and
  `tests/test_web.py` checks the fixtures are still current (runs through POST /api/run).
- Factored the GUIs' colour lists into `automata_colors.py` (both GUIs import it; checked both still build under Agg,
  `test_automata.py` 30 passed).
- Added `.gitignore` (`site/`, `__pycache__/`, `.DS_Store`). `.DS_Store` is still tracked from before; left as is.
- Issues found in existing code, not changed (worked around or documented on the site):
  - `SimplifiedLangtonLoop`: the default loop never changes (no neighbourhood matches any of its 12 rules), as the
    repo's own diagnostics report already flags ("Grid is static"). Shown honestly on the site.
  - Desktop GUIs draw with `imshow(vmin=0, vmax=num_states-1)` on short colour lists, so the colours do not map state
    i to colour i: Langton's sheath (state 1) is drawn black like the background, Life's live cells white rather than
    gray, Brian's Brain yellow/purple. The lab offers both "i-th colour" and "as the desktop draws" schemes.
  - `BriansBrain` accepts `mutation_rate` but ignores it (commented in the code); `EvolvingLoop` and
    `VonNeumannConstructor` are aliases for Brian's Brain and Life, unlike the descriptions in README_automata.md.
  - README_automata.md documents `AutomatonVisualizer` and a command-line menu in `self_replicating_automata.py`;
    neither exists. README.md lists four snapshot PNGs that are not in the repo.
  - `WireWorld(w, h)` with w or h below 49 raises IndexError (the 25-cell branches are not bounds-checked). The GUIs'
    slider starts at 50; the web lab offers 50-300 only.
