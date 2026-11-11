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
