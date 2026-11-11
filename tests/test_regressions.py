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
