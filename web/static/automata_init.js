// Starting grids: JS ports of each class's initialiser in self_replicating_automata.py, plus numpy's legacy random
// generator (MT19937 + RandomState.randint) so Brian's Brain's random start matches `np.random.seed(seed);
// BriansBrain(w, h)` exactly. The Langton rule table and the Gosper gun follow the Python source;
// automata_engine.test.mjs checks them, and every initialiser at every lab size, against the Python fixtures.

// SimplifiedLangtonLoop._create_rule_table: [C, N, E, S, W, new_state]. First the 12 hand-written rules, then the
// generalised families (_generalised_rule) for every (C, N, E, S, W) over states 0-2, in itertools.product order.
const ORIGINAL_RULES = [
  [0, 1, 1, 1, 0, 1], [0, 1, 1, 0, 1, 1], [0, 1, 0, 1, 1, 1], [0, 0, 1, 1, 1, 1],   // extend sheath
  [2, 2, 0, 0, 0, 2], [2, 0, 2, 0, 0, 2], [2, 0, 0, 2, 0, 2], [2, 0, 0, 0, 2, 2],   // signal propagation
  [0, 2, 1, 0, 0, 1], [0, 0, 2, 1, 0, 1], [0, 0, 0, 2, 1, 1], [0, 1, 0, 0, 2, 1],   // growth signals
];
function generalisedRule(c, nb) {
  const sheath = nb.filter(v => v === 1).length, data = nb.filter(v => v === 2).length;
  if (c === 0 && data === 0 && sheath === 3) return 1;   // extend sheath
  if (c === 0 && data === 1 && sheath === 1) return 1;   // growth: sheath wraps the arm
  if (c === 0 && data === 1 && sheath === 0) return 2;   // propagation: the arm tip advances
  if (c === 2 && data === 1 && sheath === 0) return 2;   // (original signal family, all arrangements)
  if (c === 1 && data === 1 && nb[(nb.indexOf(2) + 2) % 4] === 0) return 2;   // arm opening through the sheath
  return null;
}
export const LANGTON_RULES = (() => {
  const out = ORIGINAL_RULES.map(r => [...r]), seen = new Set(out.map(r => r.slice(0, 5).join()));
  for (let k = 0; k < 3 ** 5; k++) {
    const key = [4, 3, 2, 1, 0].map(p => Math.floor(k / 3 ** p) % 3);
    const v = generalisedRule(key[0], key.slice(1));
    if (v !== null && !seen.has(key.join())) out.push([...key, v]);
  }
  return out;
})();

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

export const MIN_SIZE = 50;   // WireWorld's branches reach 25 cells from the centre (the GUIs' smallest grid is 50)

const fl = n => Math.floor(n / 2);
export const INIT = {
  // WireWorld._initialize_wire: a radius-20 circle of wire (120 angles), three 25-cell branches, two electrons
  wireworld(g, w, h) {
    const cx = fl(w), cy = fl(h), radius = 20, N = 120, stepA = (2 * Math.PI) / (N - 1);
    for (let k = 0; k < N; k++) {
      const a = k === N - 1 ? 2 * Math.PI : k * stepA;              // np.linspace(0, 2*pi, 120)
      const x = Math.trunc(cx + radius * Math.cos(a)), y = Math.trunc(cy + radius * Math.sin(a));
      if (x >= 0 && x < w && y >= 0 && y < h) g[y * w + x] = 1;
    }
    for (let i = 0; i < 25; i++) { g[cy * w + cx + i] = 1; g[(cy + i) * w + cx] = 1; g[cy * w + cx - i] = 1; }
    g[(cy - radius) * w + cx] = 2; g[(cy - radius + 1) * w + cx] = 3;
    g[cy * w + cx + 5] = 2; g[cy * w + cx + 6] = 3;
  },
  // GameOfLifeReplicator._initialize_glider_gun
  game_of_life(g, w, h) {
    const cx = 10, cy = 10;
    GUN.forEach((row, dy) => [...row].forEach((c, dx) => {
      if (cy + dy < h && cx + dx < w) g[(cy + dy) * w + cx + dx] = c === 'O' ? 1 : 0;
    }));
  },
  // SimplifiedLangtonLoop._initialize_loop: a 5x5 ring of sheath (1) at (w//4, h//4) with three core (2) cells
  langton_loop(g, w, h) {
    const cx = Math.floor(w / 4), cy = Math.floor(h / 4);
    for (let i = 0; i < 5; i++) {
      g[cy * w + cx + i] = 1; g[(cy + 4) * w + cx + i] = 1; g[(cy + i) * w + cx] = 1; g[(cy + i) * w + cx + 4] = 1;
    }
    for (const dy of [2, 1, 3]) g[(cy + dy) * w + cx + 2] = 2;
  },
  // BriansBrain._initialize_random: int(w*h*0.1) draws of (x, y) = randint(0, w), randint(0, h), each set alive
  brians_brain(g, w, h, seed = 0) {
    const next = mt19937(seed), n = Math.trunc(w * h * 0.1);
    for (let k = 0; k < n; k++) { const x = randint(next, w), y = randint(next, h); g[y * w + x] = 1; }
  },
};

// The grid the Python constructor builds at this size (Brian's Brain: after np.random.seed(seed)).
export function initialCells(key, w, h, seed = 0) {
  if (w < MIN_SIZE || h < MIN_SIZE) throw new Error(`grids smaller than ${MIN_SIZE} x ${MIN_SIZE} are not supported`);
  const g = new Int32Array(w * h);
  INIT[key](g, w, h, seed);
  return g;
}
