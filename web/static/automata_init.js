// Starting grids: JS ports of each class's initialiser in self_replicating_automata.py, plus numpy's legacy random
// generator (MT19937 + RandomState.randint) so Brian's Brain's random start matches `np.random.seed(seed);
// BriansBrain(w, h)` exactly. Langton's table (langton_table.js) and the Gosper gun follow the Python source;
// automata_engine.test.mjs checks them, and every initialiser at every lab size, against the Python fixtures.

import { LANGTON_RULES, LANGTON_INITIAL_LOOP } from './langton_table.js';
export { LANGTON_RULES };

// GameOfLifeReplicator._initialize_glider_gun: gun_pattern, written with its top-left corner at (10, 10).
export const GUN = [
  '........................O...........',
  '......................O.O...........',
  '............OO......OO............OO',
  '...........O...O....OO............OO',
  'OO........O.....O...OO..............',
  'OO........O...O.OO....O.O...........',
  '..........O.....O.......O...........',
  '...........O...O....................',
  '............OO......................',
];

// --- numpy legacy RandomState: np.random.seed(int) = init_genrand; randint(0, n) = masked rejection on 32-bit draws
export function mt19937(seed) {
  const mt = new Uint32Array(624);
  let i = 624;
  mt[0] = seed >>> 0;
  for (let k = 1; k < 624; k++) { const p = mt[k - 1] ^ (mt[k - 1] >>> 30); mt[k] = (Math.imul(1812433253, p) + k) >>> 0; }
  const twist = () => {
    for (let k = 0; k < 624; k++) {
      const y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7fffffff);
      mt[k] = mt[(k + 397) % 624] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
    }
    i = 0;
  };
  return () => {
    if (i >= 624) twist();
    let y = mt[i++];
    y ^= y >>> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >>> 18;
    return y >>> 0;
  };
}
export function randint(next, n) {           // np.random.randint(0, n), n <= 2**32
  const rng = n - 1;
  if (rng === 0) return 0;
  let mask = rng;
  mask |= mask >>> 1; mask |= mask >>> 2; mask |= mask >>> 4; mask |= mask >>> 8; mask |= mask >>> 16;
  let v;
  while ((v = (next() & mask) >>> 0) > rng);
  return v;
}

export function randomSample(next) {        // RandomState.random_sample(): 53-bit double from two 32-bit draws
  const a = next() >>> 5, b = next() >>> 6;
  return (a * 67108864 + b) / 9007199254740992;
}

export const MIN_SIZE = 50;   // the GUIs' smallest grid; WireWorld (bounds-checked) also works on smaller grids

const fl = n => Math.floor(n / 2);
export const INIT = {
  // WireWorld._initialize_wire: a radius-20 circle of wire (120 angles), three 25-cell branches, two electrons
  wireworld(g, w, h) {
    const cx = fl(w), cy = fl(h), radius = 20, N = 120, stepA = (2 * Math.PI) / (N - 1);
    const set = (x, y, v) => { if (x >= 0 && x < w && y >= 0 && y < h) g[y * w + x] = v; };   // WireWorld._set
    for (let k = 0; k < N; k++) {
      const a = k === N - 1 ? 2 * Math.PI : k * stepA;              // np.linspace(0, 2*pi, 120)
      const x = Math.trunc(cx + radius * Math.cos(a)), y = Math.trunc(cy + radius * Math.sin(a));
      set(x, y, 1);
    }
    for (let i = 0; i < 25; i++) { set(cx + i, cy, 1); set(cx, cy + i, 1); set(cx - i, cy, 1); }
    set(cx, cy - radius, 2); set(cx, cy - radius + 1, 3);
    set(cx + 5, cy, 2); set(cx + 6, cy, 3);
  },
  // GameOfLifeReplicator._initialize_glider_gun
  game_of_life(g, w, h) {
    const cx = 10, cy = 10;
    GUN.forEach((row, dy) => [...row].forEach((c, dx) => {
      if (cy + dy < h && cx + dx < w) g[(cy + dy) * w + cx + dx] = c === 'O' ? 1 : 0;
    }));
  },
  // LangtonsLoop._initialize_loop: the standard 10 x 14 loop at the centre; cells off the grid are skipped
  langton_loop(g, w, h) {
    const y0 = fl(h) - fl(LANGTON_INITIAL_LOOP.length), x0 = fl(w) - 7;
    LANGTON_INITIAL_LOOP.forEach((row, dy) => [...row].forEach((ch, dx) => {
      const y = y0 + dy, x = x0 + dx;
      if (ch !== ' ' && y >= 0 && y < h && x >= 0 && x < w) g[y * w + x] = +ch;
    }));
  },
  // BriansBrain._initialize_random: int(w*h*0.1) draws of (x, y) = randint(0, w), randint(0, h), each set alive
  brians_brain(g, w, h, seed = 0) {
    const next = mt19937(seed), n = Math.trunc(w * h * 0.1);
    for (let k = 0; k < n; k++) { const x = randint(next, w), y = randint(next, h); g[y * w + x] = 1; }
  },
};

// The grid the Python constructor builds at this size (Brian's Brain: after np.random.seed(seed)).
export function initialCells(key, w, h, seed = 0) {
  if (key !== 'wireworld' && (w < MIN_SIZE || h < MIN_SIZE)) throw new Error(`grids smaller than ${MIN_SIZE} x ${MIN_SIZE} are not supported`);
  const g = new Int32Array(w * h);
  INIT[key](g, w, h, seed);
  return g;
}
