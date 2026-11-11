// The lab: pick an automaton and a starting grid (the Python constructor's pattern at any of the desktop GUI's
// sizes, an empty grid, or a random soup), play / pause / step, set the speed in ms per step like the desktop slider,
// draw on the grid, and (in the local app) check against the Python class.
import { route, api, app, esc, list, go, slider, animate, onLeave, rng } from './core.js';
import { makeState, step, stats } from './automata_engine.js';
import { initialCells } from './automata_init.js';
import { makeView } from './lab_view.js';
import { checkPanel } from './lab_check.js';

const PRESETS = [
  ['default', 'Constructor default'],
  ['empty', 'Empty grid (draw your own)'],
  ['soup', 'Random soup (lab tool)'],
];

route('lab', async (args, query) => {
  const [info, autos] = await Promise.all([api('/info'), api('/automata')]);
  const a = autos.find(x => x.key === args[0]) || autos.find(x => x.key === 'game_of_life');
  const sizes = info.sizes;
  let size = sizes.includes(+query.size) ? +query.size : info.default_size;
  let preset = PRESETS.some(p => p[0] === query.preset) ? query.preset : 'default';
  let seed = Number.isInteger(+query.seed) && +query.seed >= 0 ? +query.seed : 0;
  let s = null, playing = false, speedMs = 50, brush = 1, dirty = true, density = 0.3, soupSeed = 1;
  let mutationRate = isFinite(+query.mutation) && query.mutation !== undefined ? Math.min(0.01, Math.max(0, +query.mutation)) : 0.001;
  const isBrain = a.key === 'brians_brain';

  app().innerHTML = `
  <p class="kicker">Lab · <code>${esc(a.class)}</code> (alias <code>${esc(a.alias)}</code>)</p>
  <h1>${esc(a.label)}</h1>
  <p class="lead">${esc(a.doc.split('\n\n')[0].split('\n').join('. '))}.</p>
  <div class="lab">
    <div class="panel controls">
      <label for="sel-auto">Automaton</label>
      <select id="sel-auto">${list(autos, x => `<option value="${esc(x.key)}"${x.key === a.key ? ' selected' : ''}>${esc(x.label)} (${esc(x.class)})</option>`)}</select>
      <label for="sel-preset">Starting grid</label>
      <select id="sel-preset">${list(PRESETS, ([k, t]) => `<option value="${k}"${k === preset ? ' selected' : ''}>${esc(t)}</option>`)}</select>
      <div id="seed-row" class="${isBrain ? '' : 'hidden'}">
        <label for="in-seed">Seed (start: <code>np.random.seed</code>; mutations: <code>seed=</code>)</label>
        <input id="in-seed" type="number" min="0" max="4294967295" step="1" value="${seed}">
        <div id="mutation"></div>
      </div>
      <div id="soup-row" class="hidden"><div id="density"></div></div>
      <label for="sel-size">Grid size (cells)</label>
      <select id="sel-size">${list(sizes, n => `<option value="${n}"${n === size ? ' selected' : ''}>${n} x ${n}</option>`)}</select>
      <div class="bar">
        <button id="b-play" type="button">Play</button><button id="b-step" type="button" class="alt">Step</button>
        <button id="b-reset" type="button" class="alt">Reset</button><button id="b-clear" type="button" class="alt">Clear</button>
      </div>
      <div id="speed"></div>
      <label>Draw with state</label>
      <div class="palette" id="palette" role="radiogroup" aria-label="Drawing state"></div>
      <p class="hint">Click or drag on the grid to paint; right-click or Shift-drag erases. Keys: Space play/pause, S step.</p>
      <div class="readout" id="readout" aria-live="off"></div>
    </div>
    <div class="view"><div class="stage ca" id="stage"></div></div>
    <div class="extra">
      <div class="legend" id="legend"></div>
      <p class="small mute" id="scheme-note"></p>
      <div class="panel" id="check"></div>
      <details class="src panel"><summary>The Python source this page runs (<code>${esc(a.class)}.step</code> and <code>${esc(a.init_method)}</code>)</summary>
        <pre class="doc">${esc(a.step_source)}</pre><pre class="doc">${esc(a.init_source)}</pre></details>
    </div>
  </div>`;
  const $ = sel => app().querySelector(sel);

  const view = makeView($('#stage'), {
    label: `${a.label} grid: click or drag to draw cells`,
    onPaint(x, y, erase) { s.cells[y * s.w + x] = erase ? 0 : brush; dirty = true; },
  });

  function url() {
    const q = new URLSearchParams({ size, preset });
    if (isBrain) { q.set('seed', seed); q.set('mutation', mutationRate); }
    if (playing) q.set('play', 1);
    history.replaceState(null, '', `#/lab/${a.key}?${q}`);
  }

  function load() {
    const opts = { mutation_rate: isBrain ? mutationRate : 0, seed };
    if (preset === 'default') s = makeState(a.key, size, size, initialCells(a.key, size, size, seed), opts);
    else if (preset === 'empty') s = makeState(a.key, size, size, null, opts);
    else {
      const r = rng(soupSeed), n = a.num_states;
      s = makeState(a.key, size, size, Array.from({ length: size * size }, () => (r() < density ? 1 + Math.floor(r() * (n - 1)) : 0)), opts);
    }
    $('#soup-row').classList.toggle('hidden', preset !== 'soup');
    url(); dirty = true;
  }

  function colours() { return a.colors; }
  function buildPalette() {
    const c = colours();
    view.setColors(c);
    $('#palette').innerHTML = list(c.map((col, i) => [col, i]), ([col, i]) => `<button type="button" role="radio"
      aria-checked="${i === brush}" class="${i === brush ? 'on' : ''}" data-s="${i}" style="background:${esc(col)}"
      title="State ${i}: ${esc(a.state_names[i])}" aria-label="State ${i}: ${esc(a.state_names[i])}">${i}</button>`);
    $('#legend').innerHTML = `<span class="mute small">States:</span>` + list(c.map((col, i) => [col, i]),
      ([col, i]) => `<span><i style="background:${esc(col)}"></i>${i} ${esc(a.state_names[i])}</span>`);
    $('#scheme-note').textContent = `Colours: ${a.color_names.join(', ')} (automata_colors.py: the same colours the desktop GUIs draw, as the colour key in README_automata.md describes)` +
        (a.color_names.length < a.num_states ? `; states ${a.color_names.length}-${a.num_states - 1} have no colour in the list and are grey.` : '.');
    dirty = true;
  }
  $('#palette').addEventListener('click', e => {
    const b = e.target.closest('button');
    if (!b) return;
    brush = +b.dataset.s;
    $('#palette').querySelectorAll('button').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-checked', x === b); });
  });

  // controls
  $('#sel-auto').onchange = e => go('#/lab/' + e.target.value + `?size=${size}`);
  $('#sel-preset').onchange = e => { preset = e.target.value; load(); };
  $('#sel-size').onchange = e => { size = +e.target.value; load(); };
  $('#in-seed').onchange = e => { seed = Math.max(0, Math.min(4294967295, Math.trunc(+e.target.value) || 0)); e.target.value = seed; load(); };
  const setPlaying = on => { playing = on; $('#b-play').textContent = on ? 'Pause' : 'Play'; url(); };
  const once = () => { step(s); dirty = true; };
  $('#b-play').onclick = () => setPlaying(!playing);
  $('#b-step').onclick = () => { setPlaying(false); once(); };
  $('#b-reset').onclick = () => { setPlaying(false); load(); };
  $('#b-clear').onclick = () => { s = makeState(a.key, s.w, s.h, null, { mutation_rate: s.mutation_rate, seed }); dirty = true; };
  if (isBrain) {
    slider($('#mutation'), { id: 'mutation', label: 'Mutation rate (per cell per step)', min: 0, max: 0.01, step: 0.0001,
      value: mutationRate, fmt: v => v.toFixed(4) }, v => { mutationRate = v; s.mutation_rate = v; url(); });
  }
  slider($('#speed'), { id: 'speed', label: 'Speed (ms per step)', min: 10, max: 500, step: 10, value: speedMs, unit: ' ms' }, v => { speedMs = v; });
  slider($('#density'), { id: 'density', label: 'Soup density', min: 0.05, max: 1, step: 0.05, value: density, fmt: v => v.toFixed(2) },
    v => { density = v; soupSeed++; load(); });

  if (query.play) playing = true;   // #/lab/<key>?play=1 starts running (shareable links, screenshots)
  $('#b-play').textContent = playing ? 'Pause' : 'Play';
  checkPanel($('#check'), { key: a.key, state: () => s, params: () => (isBrain ? { mutation_rate: s.mutation_rate, seed } : {}) });
  load(); buildPalette();

  // animation loop: one step per `speedMs`, at most 8 steps per frame
  let lastT = 0, acc = 0, lastStats = 0;
  const stop = animate(t => {
    const dt = lastT ? Math.min(t - lastT, 250) : 0;
    lastT = t;
    if (playing) {
      acc += dt;
      let n = Math.min(8, Math.floor(acc / speedMs));
      acc = n === 8 ? 0 : acc - n * speedMs;
      while (n-- > 0) once();
    }
    if (dirty) { view.render(s); dirty = false; }
    if (t - lastStats > 200) { lastStats = t; readout(); }
  });
  const keys = e => {
    if (e.target.closest('input, select, textarea') || e.metaKey || e.ctrlKey) return;
    if (e.key === ' ') { e.preventDefault(); setPlaying(!playing); } else if (e.key === 's' || e.key === 'S') { setPlaying(false); once(); }
  };
  document.addEventListener('keydown', keys);
  onLeave(() => { stop(); document.removeEventListener('keydown', keys); });

  // the desktop GUI's statistics panel: generation, active / total cells, density, complexity (Shannon entropy)
  function readout() {
    const st = stats(s);
    $('#readout').innerHTML = [['Generation', st.generation.toLocaleString()], ['Grid', `${s.w} x ${s.h}`],
      ['Active cells', st.active_cells.toLocaleString()], ['Total cells', st.total_cells.toLocaleString()],
      ['Density', st.density.toFixed(2) + ' %'], ['Complexity', st.complexity.toFixed(3)],
      ['Running', playing ? 'Yes' : 'No'], ['Speed', speedMs + ' ms']]
      .map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('');
  }
});
