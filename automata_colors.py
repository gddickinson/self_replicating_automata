"""Colour lists for each automaton type, shared by the desktop GUIs and the web interface.

Keys are the automaton names used by the GUIs (the aliases at the bottom of self_replicating_automata.py).
automata_gui.py and automata_interactive_gui.py build their ListedColormap from these lists; web/catalogue.py
reads them for the browser lab. Pure data: no matplotlib or GUI imports.
"""

COLORMAP_COLORS = {
    "LangtonLoop": ['black', 'white', 'red', 'blue', 'yellow'],
    "EvolvingLoop": ['black', 'white', 'red', 'orange',
                     'yellow', 'green', 'blue', 'purple'],
    "VonNeumannConstructor": ['black', 'gray', 'red', 'orange',
                              'yellow', 'green', 'blue', 'cyan',
                              'magenta', 'white'],
    "WireWorld": ['black', 'yellow', 'blue', 'red'],
}

FALLBACK = "#808080"   # grey for states beyond a colour list (e.g. LangtonLoop states 5-7)


def state_colors(alias: str, num_states: int) -> list:
    """One colour per state: state i gets the i-th colour of the list (grey when the list is shorter)."""
    names = COLORMAP_COLORS[alias]
    return [names[i] if i < len(names) else FALLBACK for i in range(num_states)]


def colormap_and_norm(alias: str, num_states: int):
    """(ListedColormap, BoundaryNorm) for imshow(grid, cmap=..., norm=...) so state i is drawn with colour i.

    imshow(vmin=0, vmax=num_states-1) on a list of a different length would spread the list over the states instead
    (e.g. LangtonLoop's sheath, state 1, came out black like the background).
    """
    import numpy as np
    from matplotlib.colors import BoundaryNorm, ListedColormap
    cmap = ListedColormap(state_colors(alias, num_states))
    return cmap, BoundaryNorm(np.arange(num_states + 1) - 0.5, num_states)
