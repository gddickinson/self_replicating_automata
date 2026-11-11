"""Regression tests for bugs fixed after the web-interface review (each failed before its fix).

Run: python -m pytest -q tests/test_regressions.py
"""
import os
import sys
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("MPLBACKEND", "Agg")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import self_replicating_automata as sra  # noqa: E402
from automata_colors import COLORMAP_COLORS  # noqa: E402

GUI_TYPES = {  # interactive GUI radio label -> (alias, num_states)
    "Simple Loop": ("LangtonLoop", 8), "Brian's Brain": ("EvolvingLoop", 3),
    "Game of Life": ("VonNeumannConstructor", 2), "Wire World": ("WireWorld", 4),
}


def _hex(c):
    from matplotlib.colors import to_hex
    return to_hex(c)


# --- 1. desktop GUIs draw state i with the i-th colour of the list ------------------------------------------------
def _assert_image_colours(im, alias, n):
    names = COLORMAP_COLORS[alias]
    for i in range(min(n, len(names))):
        assert _hex(im.cmap(im.norm(i))) == _hex(names[i]), (alias, i)


@pytest.mark.parametrize("label", list(GUI_TYPES))
def test_interactive_gui_colours_state_i_is_colour_i(label):
    import matplotlib.pyplot as plt
    from automata_interactive_gui import InteractiveAutomatonGUI
    gui = InteractiveAutomatonGUI()
    gui._on_type_change(label)
    alias, n = GUI_TYPES[label]
    _assert_image_colours(gui.ax_main.images[-1], alias, n)
    plt.close(gui.fig)


def test_langton_sheath_visible_in_gui():
    import matplotlib.pyplot as plt
    from automata_interactive_gui import InteractiveAutomatonGUI
    gui = InteractiveAutomatonGUI()
    gui._on_type_change("Simple Loop")
    im = gui.ax_main.images[-1]
    assert _hex(im.cmap(im.norm(1))) != _hex(im.cmap(im.norm(0)))   # sheath differs from background
    plt.close(gui.fig)


def test_tk_gui_colours_state_i_is_colour_i():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display for Tk")
    root.withdraw()
    try:
        from automata_gui import AutomatonGUI
        app = AutomatonGUI(root)
        for alias, n in GUI_TYPES.values():
            app.automaton_var.set(alias)
            app._create_automaton()
            app._update_display()
            _assert_image_colours(app.ax.images[-1], alias, n)
    finally:
        root.destroy()


# --- 2. SimplifiedLangtonLoop: the default loop evolves -----------------------------------------------------------
def test_langton_default_loop_evolves():
    """Before the fix none of the 12 rules matched any neighbourhood of the default loop, so it never changed."""
    ll = sra.SimplifiedLangtonLoop(50, 50)
    for t in range(12):
        before = ll.grid.copy()
        ll.step()
        assert not np.array_equal(before, ll.grid), f"grid did not change at step {t + 1}"
    assert ll.grid.max() <= 2


def test_langton_loop_extends_sheathed_arm():
    """The data (2) leaves the loop through the sheath and is wrapped in sheath (1) as it grows (an 'arm')."""
    ll = sra.SimplifiedLangtonLoop(50, 50)
    cx, cy = 50 // 4, 50 // 4
    for _ in range(3):
        ll.step()
    assert ll.grid[cy - 2, cx + 2] == 2 and ll.grid[cy - 1, cx + 1] == 1 and ll.grid[cy - 1, cx + 3] == 1


def test_langton_keeps_original_rules():
    """The 12 hand-written rules are still in the table with their original results."""
    original = {(0, 1, 1, 1, 0): 1, (0, 1, 1, 0, 1): 1, (0, 1, 0, 1, 1): 1, (0, 0, 1, 1, 1): 1,
                (2, 2, 0, 0, 0): 2, (2, 0, 2, 0, 0): 2, (2, 0, 0, 2, 0): 2, (2, 0, 0, 0, 2): 2,
                (0, 2, 1, 0, 0): 1, (0, 0, 2, 1, 0): 1, (0, 0, 0, 2, 1): 1, (0, 1, 0, 0, 2): 1}
    rules = sra.SimplifiedLangtonLoop(50, 50).rules
    assert all(rules.get(k) == v for k, v in original.items())


def test_langton_rules_rotation_symmetric():
    rules = sra.SimplifiedLangtonLoop(50, 50).rules
    for (c, n, e, s, w), v in rules.items():
        assert rules.get((c, w, n, e, s)) == v


# --- 3. BriansBrain.mutation_rate is used (seeded) ------------------------------------------------------------------
def _empty_brain(rate, seed):
    bb = sra.BriansBrain(30, 30, mutation_rate=rate, seed=seed)
    bb.grid[:] = 0
    return bb


def test_brians_brain_mutations_happen():
    """An empty grid stays empty under the rules alone; with mutations, cells appear."""
    bb = _empty_brain(0.05, seed=1)
    bb.step()
    assert np.count_nonzero(bb.grid) > 0


def test_brians_brain_mutations_seeded():
    a, b = _empty_brain(0.02, seed=7), _empty_brain(0.02, seed=7)
    c = _empty_brain(0.02, seed=8)
    for _ in range(5):
        a.step(); b.step(); c.step()
    assert np.array_equal(a.grid, b.grid) and not np.array_equal(a.grid, c.grid)


def test_brians_brain_mutation_rate_magnitude():
    bb = _empty_brain(0.1, seed=3)
    bb.step()
    # a mutated cell gets a random state 0..2, so about rate * 2/3 of cells end up nonzero
    assert 0.03 < np.count_nonzero(bb.grid) / bb.grid.size < 0.1


def test_brians_brain_zero_rate_unchanged_rules():
    np.random.seed(0)
    a = sra.BriansBrain(30, 30)
    np.random.seed(0)
    b = sra.BriansBrain(30, 30, mutation_rate=0.0, seed=5)
    for _ in range(5):
        a.step(); b.step()
    assert np.array_equal(a.grid, b.grid)


@pytest.mark.parametrize("rate", [-0.1, 1.5])
def test_brians_brain_rejects_bad_rate(rate):
    with pytest.raises(ValueError):
        sra.BriansBrain(30, 30, mutation_rate=rate)


def test_interactive_gui_shows_mutation_slider_for_brians_brain():
    import matplotlib.pyplot as plt
    from automata_interactive_gui import InteractiveAutomatonGUI
    gui = InteractiveAutomatonGUI()
    gui._on_type_change("Brian's Brain")
    assert gui.slider_mutation.ax.get_visible()
    assert gui.automaton.mutation_rate == gui.mutation_rate
    gui._on_type_change("Wire World")
    assert not gui.slider_mutation.ax.get_visible()
    plt.close(gui.fig)


# --- 4. docs say what the EvolvingLoop / VonNeumannConstructor aliases really are --------------------------------
ALIAS_DOCS = ["README.md", "README_automata.md", "GUI_GUIDE.md", "automata_gui.py"]


@pytest.mark.parametrize("doc", ALIAS_DOCS)
def test_docs_name_the_real_automata_behind_aliases(doc):
    text = (ROOT / doc).read_text()
    assert "Brian's Brain" in text and "Game of Life" in text, doc


def test_docs_do_not_claim_evoloops_or_universal_construction():
    text = (ROOT / "README_automata.md").read_text()
    assert "First CA system to demonstrate true evolution of self-reproducing organisms" not in text
    assert "Simplified demonstration of universal construction principles" not in text
    tk = (ROOT / "automata_gui.py").read_text()
    assert "Shows construction process" not in tk
    for doc in ("README.md", "GUI_GUIDE.md"):
        assert "Universal constructor demo" not in (ROOT / doc).read_text()


# --- 5. WireWorld below 49 cells ----------------------------------------------------------------------------------
@pytest.mark.parametrize("size", [5, 10, 20, 30, 39, 40, 45, 48, 49])
def test_wireworld_small_grids(size):
    """Used to raise IndexError below 49 cells (the 25-cell branches were not bounds-checked)."""
    ww = sra.WireWorld(size, size)
    assert np.count_nonzero(ww.grid) > 0
    ww.step()
    assert ww.generation == 1


def test_wireworld_small_grid_does_not_wrap_electrons():
    """Cells outside the grid are skipped, not wrapped round by negative indexing."""
    ww = sra.WireWorld(30, 30)          # cy - radius = -5 would have hit row 25
    assert ww.grid[25, 15] != 2 and ww.grid[26, 15] != 3


def test_wireworld_unchanged_at_gui_sizes():
    """Bounds checks must not change the pattern at the sizes the GUIs use."""
    ww = sra.WireWorld(100, 100)
    assert (ww.grid == 2).sum() == 2 and (ww.grid == 3).sum() == 2
