// Home page: hero, counts from /api/info, one card per automaton class, and how the site is built.
import { route, api, app, esc, list, tags, isStatic } from './core.js';

export const swatches = colors =>
  `<div class="swatches" aria-hidden="true">${list(colors, c => `<i style="background:${esc(c)}"></i>`)}</div>`;

route('home', async () => {
  const [info, autos] = await Promise.all([api('/info'), api('/automata')]);
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">von Neumann · Langton · Conway</p>
    <h1 class="glow">Self-Replicating Automata</h1>
    <p class="lead">Interactive visualizations of several types of self-replicating cellular automata, inspired by John
    von Neumann's pioneering work on artificial self-reproduction. Every automaton in the Python simulator runs here, in
    your browser: press play, draw on the grid, change the size.</p>
    <a class="btn" href="#/lab/game_of_life">Open the lab</a><a class="btn alt" href="#/automata">Browse the automata</a>
    <a class="btn alt" href="#/background">Background</a>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.automata}</b><span>automaton classes</span></div>
    <div class="tile"><b>${info.max_states}</b><span>states in the largest (the loop)</span></div>
    <div class="tile"><b>${info.langton_rules}</b><span>rules in Langton's published table</span></div>
    <div class="tile"><b>${info.gun_cells}</b><span>live cells in the Gosper glider gun</span></div>
    <div class="tile"><b>${info.sizes[0]}–${info.sizes.at(-1)}</b><span>grid sizes (as the desktop slider)</span></div>
  </div>
  <h2>Automata</h2>
  <div class="grid cards-ca">${list(autos, a => `
    <a class="card" href="#/lab/${esc(a.key)}">
      <b>${esc(a.label)}</b><small><code>${esc(a.class)}</code> · alias <code>${esc(a.alias)}</code></small>
      <span>${esc(a.doc.split('\n')[0])}</span>
      <div>${tags([`${a.num_states} states`, a.neighbourhood], 'c')}</div>
      ${swatches(a.colors)}
    </a>`)}</div>
  <h2>How this site works</h2>
  <div class="flow">
    <div>Names, states, colours, docstrings and source code are read from the Python classes in
      <code>self_replicating_automata.py</code> and the colour lists the desktop GUIs use.</div>
    <div>Each class's <code>step()</code> and its initial pattern are ported to a small JavaScript engine, so the grid runs
      in the browser with no server. Brian's Brain's random start uses a port of numpy's generator, so a seed gives the
      same grid as <code>np.random.seed(seed)</code> in Python.</div>
    <div>Node tests require the JS engine to reproduce grids computed by the Python code exactly: every starting
      pattern at every grid size, and runs of up to 120 generations.</div>
    <div>${isStatic() ? 'Run the app locally (see About) and' : 'Here, in the local app, you can'} press "Check with Python"
      in the lab to step your own grid through the real Python class and compare.</div>
  </div>`;
});
