// Browser engine: a pure-JS port of the four automata in self_replicating_automata.py (no DOM; runs in node too).
// A state is { key, w, h, cells: Int32Array (row-major, cells[y * w + x]), gen, mutation_rate, seed, rng }.
// Each step() mirrors the Python class's step() exactly: toroidal wrap-around, a fresh copy of the grid as the output, and cells that no rule
// touches keep their value. automata_engine.test.mjs checks it against grids produced by the Python code
// (tests/fixtures/engine_fixtures.json).
import { LANGTON_RULES, mt19937, randint, randomSample } from './automata_init.js';

// Langton rule lookup: (C, N, E, S, W) with states 0..7 -> index in base 8; -1 = no rule (cell unchanged).
const LT = new Int8Array(8 ** 5).fill(-1);
for (const [c, n, e, s, w, v] of LANGTON_RULES) LT[(((c * 8 + n) * 8 + e) * 8 + s) * 8 + w] = v;

// Count Moore neighbours (8, wrapping) of cell (x, y) whose state equals `want`, or the sum of their states if want < 0.
function moore(src, w, h, x, y, want) {
  let n = 0;
  for (let dy = -1; dy <= 1; dy++) {
    const row = ((y + dy + h) % h) * w;
    for (let dx = -1; dx <= 1; dx++) {
      if (!dy && !dx) continue;
      const v = src[row + (x + dx + w) % w];
      n += want < 0 ? v : (v === want ? 1 : 0);
    }
  }
  return n;
}

export const STEP = {
  // WireWorld.step: 2 -> 3, 3 -> 1, 1 -> 2 when 1 or 2 Moore neighbours are electron heads (2); 0 stays 0.
  wireworld(src, dst, w, h) {
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x, c = src[i];
      if (c === 2) dst[i] = 3;
      else if (c === 3) dst[i] = 1;
      else if (c === 1) { const k = moore(src, w, h, x, y, 2); if (k === 1 || k === 2) dst[i] = 2; }
    }
  },
  // GameOfLifeReplicator.step: neighbours = sum of the 8 neighbours' values; alive dies outside 2..3, dead with 3 is born.
  game_of_life(src, dst, w, h) {
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x, n = moore(src, w, h, x, y, -1);
      if (src[i] === 1) { if (n < 2 || n > 3) dst[i] = 0; } else if (n === 3) dst[i] = 1;
    }
  },
  // SimplifiedLangtonLoop.step: look up (center, north, east, south, west) in the rule table; no match = unchanged.
  langton_loop(src, dst, w, h) {
    for (let y = 0; y < h; y++) {
      const yn = ((y - 1 + h) % h) * w, ys = ((y + 1) % h) * w, yc = y * w;
      for (let x = 0; x < w; x++) {
        const c = src[yc + x], n = src[yn + x], e = src[yc + (x + 1) % w], s = src[ys + x], wv = src[yc + (x - 1 + w) % w];
        if (c > 7 || n > 7 || e > 7 || s > 7 || wv > 7) continue;
        const v = LT[(((c * 8 + n) * 8 + e) * 8 + s) * 8 + wv];
        if (v >= 0) dst[yc + x] = v;
      }
    }
  },
  // BriansBrain.step: dead with exactly 2 alive (1) neighbours is born; alive -> dying (2); dying -> dead.
  brians_brain(src, dst, w, h) {
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x, c = src[i];
      if (c === 0) { if (moore(src, w, h, x, y, 1) === 2) dst[i] = 1; } else if (c === 1) dst[i] = 2; else if (c === 2) dst[i] = 0;
    }
  },
};
export const KEYS = Object.keys(STEP);

// opts (Brian's Brain): mutation_rate and seed, as BriansBrain(..., mutation_rate, seed); rng = RandomState(seed).
export function makeState(key, w, h, cells = null, { mutation_rate = 0, seed = 0 } = {}) {
  return { key, w, h, cells: cells ? Int32Array.from(cells) : new Int32Array(w * h), gen: 0,
    mutation_rate, seed, rng: mt19937(seed) };
}

// BriansBrain._mutate: mask = random_sample(shape) < rate (row-major), then randint(0, num_states) per masked cell.
const NUM_STATES = { brians_brain: 3 };
function mutate(s, dst) {
  if (!(s.mutation_rate > 0) || !NUM_STATES[s.key]) return;
  const hit = [];
  for (let i = 0; i < dst.length; i++) if (randomSample(s.rng) < s.mutation_rate) hit.push(i);
  for (const i of hit) dst[i] = randint(s.rng, NUM_STATES[s.key]);
}

export function step(s) {
  const dst = Int32Array.from(s.cells);   // new_grid = self.grid.copy()
  STEP[s.key](s.cells, dst, s.w, s.h);
  mutate(s, dst);
  s.cells = dst;
  s.gen += 1;
  return s;
}

export function run(s, n) {
  for (let i = 0; i < n; i++) step(s);
  return s;
}

// --- base-36 grid text (mirrors web/grid_codec.py) ---------------------------------------------------------------
export function decode(text, w, h) {
  if (text.length !== w * h) throw new Error(`expected ${w * h} cells, got ${text.length}`);
  const out = new Int32Array(w * h);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(text[i], 36);
  return out;
}
export function encode(cells) {
  let s = '';
  for (let i = 0; i < cells.length; i++) s += cells[i].toString(36);
  return s;
}

// --- statistics (mirrors InteractiveAutomatonGUI._update_statistics) ---------------------------------------------
export function stats(s) {
  const counts = new Map();
  let active = 0;
  for (const v of s.cells) { counts.set(v, (counts.get(v) || 0) + 1); if (v) active++; }
  const n = s.cells.length;
  let complexity = 0;
  for (const c of counts.values()) { const p = c / n; complexity -= p * Math.log2(p + 1e-10); }
  return { generation: s.gen, active_cells: active, total_cells: n, density: active / n * 100, complexity,
    counts: Object.fromEntries([...counts].sort((a, b) => a[0] - b[0])) };
}
