// Automata catalogue: every class in self_replicating_automata.py with its names, states, colours, rules and the
// docstrings and source code it is built from. Notes are facts from the repo's code, comments and diagnostics report.
import { route, api, app, esc, list, tags } from './core.js';

const legend = (a, key) => `<div class="legend">${list(a[key].map((c, i) => [c, i]),
  ([c, i]) => `<span><i style="background:${esc(c)}"></i>${i} ${esc(a.state_names[i])}</span>`)}</div>`;

const NOTES = {
  langton_loop: a => `<div class="callout">The class docstring calls this a "Simplified Langton Loop with working rule table";
    its rule table holds ${a.rules.length} rules, and a cell whose (centre, north, east, south, west) neighbourhood matches no
    rule keeps its state. In the repo's own diagnostics report (<code>diagnostics/diagnostic_report_20251221_112706.txt</code>)
    the default loop is flagged "Grid is static (no changes after step)": none of its neighbourhoods match a rule. Random soups
    of states 0-2 do trigger the rules; try "Random soup" in the lab.</div>
    <h3>Rule table (<code>_create_rule_table</code>)</h3>
    <div class="scroll"><table class="rules"><thead><tr><th>C</th><th>N</th><th>E</th><th>S</th><th>W</th><th>→ new</th></tr></thead>
    <tbody>${list(a.rules, r => `<tr>${list(r.slice(0, 5), v => `<td>${v}</td>`)}<td><b>${r[5]}</b></td></tr>`)}</tbody></table></div>`,
  brians_brain: () => `<div class="callout">The constructor accepts <code>mutation_rate</code> but, as its comment says, does
    not use it ("Accept but don't use (for compatibility)"). The start is random: 10% of width x height random (x, y) draws set
    alive (repeats overlap). The desktop GUIs do not seed numpy, so each reset differs; the lab exposes the seed.</div>`,
  game_of_life: a => `<div class="callout a">Its docstring: "Conway's Game of Life variant with a self-replicating pattern".
    The constructor writes Gosper's Glider Gun (${a.gun.cells} live cells) with its top-left corner at
    (${a.gun.origin.join(', ')}); the grid wraps around, so the gliders it emits eventually come back.</div>
    <h3>Gosper's glider gun (<code>gun_pattern</code>)</h3><pre class="gun">${esc(a.gun.rows.join('\n'))}</pre>`,
  wireworld: () => `<div class="callout a">The starting circuit: a radius-20 circle of wire around the grid centre, three
    25-cell branches (east, south and west of the centre) and two electrons (head + tail), one placed 20 rows above the centre (the top of the circle) and one on the
    east branch. README_automata.md: "Not a replicator, but demonstrates signal propagation".</div>`,
};

route('automata', async () => {
  const autos = await api('/automata');
  app().innerHTML = `
  <p class="kicker">Catalogue</p>
  <h1>Automata</h1>
  <p class="lead">The ${autos.length} automaton classes in <code>self_replicating_automata.py</code>, each a subclass of
  <code>CellularAutomaton</code> (a <code>(height, width)</code> int grid with wrap-around edges and a <code>step()</code>
  that writes into a copy of the grid). The desktop GUIs reach them through the aliases at the bottom of the module.</p>
  <div class="toc" role="navigation" aria-label="Automata">${list(autos, a => `<a class="tag a" href="#/automata" data-jump="a-${esc(a.key)}">${esc(a.label)}</a>`)}</div>
  <div class="scroll"><table>
    <thead><tr><th>Class</th><th>Alias</th><th>Interactive GUI</th><th>Tkinter GUI</th><th>States</th></tr></thead>
    <tbody>${list(autos, a => `<tr><td><code>${esc(a.class)}</code></td><td><code>${esc(a.alias)}</code></td>
      <td>${esc(a.label)}</td><td>${esc(a.tk_label)}</td><td>${a.num_states}</td></tr>`)}</tbody></table></div>
  ${list(autos, a => `
  <section class="panel auto" id="a-${esc(a.key)}">
    <h2>${esc(a.label)} <span class="small mute"><code>${esc(a.class)}</code></span></h2>
    <p>${esc(a.doc.split('\n\n')[0].split('\n').join('. '))}.</p>
    <div>${tags([`${a.num_states} states`, `${a.neighbourhood}`, 'wrap-around edges'], 'c')}
      ${tags([`alias ${a.alias}`, `"${a.tk_label}" in automata_gui.py`], 'b')}</div>
    <h3>States and colours</h3>
    ${legend(a, 'colors')}
    ${NOTES[a.key](a)}
    <p><a class="btn" href="#/lab/${esc(a.key)}">Open in the lab</a></p>
    <details class="src"><summary>Python source: <code>step()</code> and <code>${esc(a.init_method)}()</code></summary>
      <pre class="doc">${esc(a.step_source)}</pre><pre class="doc">${esc(a.init_source)}</pre></details>
  </section>`)}`;
  app().querySelectorAll('[data-jump]').forEach(el => el.addEventListener('click', e => {
    e.preventDefault();
    document.getElementById(el.dataset.jump).scrollIntoView({ behavior: 'smooth' });
  }));
});
