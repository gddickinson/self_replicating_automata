// Lab side panel: step the current grid through the real Python class (POST /api/run, local app only) and compare
// with the browser engine; plus a JSON download of the grid that works everywhere.
import { api, esc, isStatic, needsServer, download } from './core.js';
import { makeState, run, encode } from './automata_engine.js';

const MAX_WORK = 1_000_000;   // same cap as web/catalogue.py MAX_WORK

export function checkPanel(host, ctx) {
  // ctx: { key, state(), params() }  (params: Brian's Brain mutation_rate and seed)
  host.innerHTML = `<h3>Check against Python</h3>
    ${isStatic() ? needsServer('Stepping your grid through the Python class')
      : `<p class="small mute">Runs the current grid through the class's own <code>step()</code> on the server and compares
        it, cell for cell, with this page's JavaScript engine.</p>
      <div class="row"><div><label for="chk-n">Generations</label><input id="chk-n" type="number" min="1" max="500" value="10"></div>
      <div><button id="chk-go" type="button">Check with Python</button></div></div>`}
    <p id="chk-out" class="small" aria-live="polite"></p>
    <button id="chk-dl" type="button" class="alt">Download grid (JSON)</button>`;
  const out = host.querySelector('#chk-out');
  host.querySelector('#chk-dl').onclick = () => {
    const s = ctx.state();
    download(`automaton_${ctx.key}_gen${s.gen}.json`, JSON.stringify({
      automaton: ctx.key, ...ctx.params(), width: s.w, height: s.h, generation: s.gen,
      encoding: 'base-36 digit per cell, row-major (grid[y][x] = cells[y * width + x])', cells: encode(s.cells),
    }), 'application/json');
  };
  const go = host.querySelector('#chk-go');
  if (!go) return;
  go.onclick = async () => {
    const s = ctx.state(), n = Math.max(1, Math.min(500, Math.trunc(+host.querySelector('#chk-n').value) || 1));
    if (s.w * s.h * n > MAX_WORK) {
      out.className = 'small err';
      out.textContent = `Too much work for the pure-Python loops: width x height x generations must be at most ${MAX_WORK.toLocaleString()}.`;
      return;
    }
    go.disabled = true;
    out.className = 'small mute';
    out.textContent = 'Running the Python class...';
    try {
      const t0 = performance.now();
      const params = ctx.params();
      const py = await api('/run', { body: { key: ctx.key, width: s.w, height: s.h, cells: encode(s.cells), steps: n, ...params } });
      const ms = performance.now() - t0;
      const js = run(makeState(ctx.key, s.w, s.h, s.cells, params), n);
      const a = encode(js.cells);
      let diff = 0;
      for (let i = 0; i < a.length; i++) diff += a[i] !== py.cells[i];
      out.className = diff ? 'small err' : 'small ok';
      out.innerHTML = diff
        ? `${diff} of ${a.length} cells differ after ${n} generations.`
        : `Identical: all ${a.length.toLocaleString()} cells match after ${n} generations (Python took ${Math.round(ms)} ms;
          ${py.stats.active_cells} active cells, complexity ${py.stats.complexity.toFixed(3)}).`;
    } catch (e) {
      out.className = 'small err';
      out.textContent = e.message;
    } finally {
      go.disabled = false;
    }
  };
}
