// About page: what the project is, how to run the desktop apps, the web app and the static site, and credits (README).
import { route, app, isStatic } from './core.js';

route('about', () => {
  app().innerHTML = `
  <p class="kicker">About</p>
  <h1>Self-Replicating Automata</h1>
  <p class="lead">A Python simulator with interactive visualizations of several types of self-replicating cellular
  automata, inspired by John von Neumann's pioneering work on artificial self-reproduction. The automaton classes live in
  <code>self_replicating_automata.py</code>; two desktop GUIs (matplotlib widgets and Tkinter) and diagnostic scripts are
  built on them.</p>

  <h2>This web version</h2>
  <p>The site is a working lab. All four automaton classes, and the starting pattern each constructor builds, are ported
  to a small JavaScript engine (<code>automata_engine.js</code>, <code>automata_init.js</code>). Node tests require it to
  reproduce grids computed by the Python code exactly: every starting pattern at every grid size the desktop slider offers
  (50 to 300), Brian's Brain's numpy-seeded random start, and runs of up to 120 generations. The local app can also step
  any grid you draw through the real Python class to compare.</p>
  <div class="callout">The classes are run exactly as written, including their simplifications (see
  <a href="#/automata">Automata</a> and <a href="#/background">Background</a>). The colours follow the lists in
  <code>automata_colors.py</code>, shared with the desktop GUIs: state i is drawn with the i-th colour of the list.</div>
  ${isStatic() ? '<p class="static-note">You are on the static site: everything runs in your browser; only the "Check with Python" button needs the local app.</p>' : ''}

  <h2>Run the desktop app</h2>
  <pre>pip install numpy matplotlib
python quick_start.py               # launches the interactive matplotlib GUI
python automata_interactive_gui.py  # the same GUI directly
python automata_gui.py              # Tkinter GUI (needs python3-tk)</pre>
  <p>Diagnostics: <code>python automaton_diagnostic.py</code> (tests every automaton and writes PNGs and a text report to
  <code>diagnostics/</code>) and <code>python display_diagnostic.py</code> (matplotlib backend and refresh checks).
  Unit tests: <code>python -m pytest test_automata.py</code>.</p>

  <h2>Run the web app</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8140</pre>
  <p>Build the static site (what GitHub Pages serves) with <code>python scripts/build_static.py</code>; run the web tests with
  <code>python -m pytest -q tests/test_web.py</code> (includes the node engine test).</p>

  <h2>Credits</h2>
  <ul>
    <li>Based on: von Neumann, J. (1966). <i>Theory of Self-Reproducing Automata</i></li>
    <li>Langton, C. (1984): self-reproducing loops; Sayama, H. (1999): evoloops</li>
    <li>Created for George Dickinson's lab</li>
  </ul>
  <p>MIT licence. Built with AI assistance from <a href="https://claude.com/" target="_blank" rel="noopener">Claude (Anthropic)</a>.
  Source: <a href="https://github.com/gddickinson/self_replicating_automata" target="_blank" rel="noopener">github.com/gddickinson/self_replicating_automata</a>.</p>`;
});
