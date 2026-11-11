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
