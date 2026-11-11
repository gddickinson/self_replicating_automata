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

## 2026-11-11 -- Bug fixes approved by George (branch `web-interface`, after the web merge)
One commit per fix, each with regression tests in `tests/test_regressions.py` that failed first:
1. Desktop GUI colours: `automata_colors.colormap_and_norm()` (ListedColormap + BoundaryNorm) replaces
   `imshow(vmin, vmax)` in both GUIs and `automaton_diagnostic.py`; state i = colour i, Langton's sheath is white.
   Web lab's "desktop colours" switch removed.
2. `SimplifiedLangtonLoop`: the 12 rules are kept and each family generalised to every neighbour arrangement over
   states 0-2 (`_generalised_rule`), plus an arm-opening rule (sheath with one data neighbour and empty space opposite
   -> data). The default loop now grows sheathed arms north and south that branch and fill the grid (40 rules). This
   is a design choice made to give the rules' stated intent ("extension", "propagation", "growth") something to act
   on; it does not make a true self-copying Langton loop (still ROADMAP work).
3. `BriansBrain(mutation_rate, seed)`: after each step each cell, with probability `mutation_rate`, gets a random
   state from the automaton's own `np.random.RandomState(seed)`; rate 0 draws nothing; rates outside [0, 1] raise.
   The interactive GUI shows its mutation slider for Brian's Brain (desktop GUIs default to 0.001, so mutations are
   now on by default there).
4. Docs (README_automata, README, GUI_GUIDE, Tk GUI labels/info) say EvolvingLoop = Brian's Brain with optional
   mutations and VonNeumannConstructor = Game of Life with Gosper's glider gun.
5. `WireWorld` initial cells go through `_set()` (bounds-checked): grids below 49 cells work; unchanged at 50-300.
6. README_automata's AutomatonVisualizer/CLI menu replaced by real usage; README.md's 4 missing PNGs replaced by
   `docs/img/` and `diagnostics/`.
7. `.DS_Store` untracked (.gitignore already covered it).
- JS engine updated (generated Langton table, RandomState `random_sample`/`randint` mutations, bounds-checked
  WireWorld init); fixtures regenerated (29 initial grids incl. WireWorld 5-45, 15 run cases incl. mutations);
  `/api/run` takes `mutation_rate`/`seed`; lab has a mutation slider. CI now runs `pytest tests test_automata.py`.
- Note: `diagnostics/` still holds the 2025-12-21 report/PNGs made with the old rules and colours.

## 2026-11-11 -- Langton's published loop replaces the reduced-rule loop (approved by George)
- New `langton_rules.py`: the 219 published rules (CNESWC'), cited (Langton, Physica D 10, 1984; table as in
  Golly's `Langtons-Loops.rule`, from H. Sayama's `loops.java`), the standard initial loop, and
  `build_rule_table()` (rotate4; 857 distinct neighbourhoods, no conflicts).
- `LangtonsLoop` replaces the reduced/generalised rules entirely (no variant kept); `LangtonLoop` and
  `SimplifiedLangtonLoop` are aliases of it. Loop placed at the grid centre. Colours: Sayama/Golly's 8 colours.
  Interactive GUI label "Simple Loop" -> "Langton's Loop".
- Tests (`tests/test_langton_loop.py`): 219 rules, rotation symmetry, 85-cell standard loop, one loop until the
  daughter forms and two ~86-cell loops at generation 151, and no unmatched neighbourhood in 151 generations.
- Web: `web/static/langton_table.js` (same table, same rotation order), init ported, fixtures regenerated (adds a
  70x70 run to generation 151), catalogue/automata/background/home text and README_automata, README, GUI_GUIDE,
  ROADMAP (219-rule item ticked), INTERFACE updated; screenshots refreshed (lab_langton_loop shows both loops).
