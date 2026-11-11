// Node test: the JS engine and initialisers must reproduce, cell for cell, the grids the Python classes produce.
// Fixtures: tests/fixtures/engine_fixtures.json (python scripts/make_engine_fixtures.py). Run: node automata_engine.test.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { KEYS, makeState, run, step, decode, encode, stats } from './automata_engine.js';
import { LANGTON_RULES, GUN, initialCells, mt19937, randint } from './automata_init.js';

const here = fileURLToPath(new URL('.', import.meta.url));
const fx = JSON.parse(readFileSync(here + '../../tests/fixtures/engine_fixtures.json', 'utf8'));
let fails = 0, checks = 0;
const ok = (cond, msg) => { checks++; if (!cond) { fails++; console.error('FAIL', msg); } };
const diffCount = (a, b) => { let d = 0; for (let i = 0; i < a.length; i++) d += a[i] !== b[i]; return d; };

// 1. constants copied from the Python source
ok(JSON.stringify(LANGTON_RULES) === JSON.stringify(fx.rules), 'Langton rule table matches SimplifiedLangtonLoop.rules');
ok(JSON.stringify(GUN) === JSON.stringify(fx.gun.rows) && fx.gun.origin.join() === '10,10', 'Gosper gun matches the Python grid');

// 2. every constructor grid at every lab size (Brian's Brain: numpy-seeded)
for (const c of fx.inits) {
  const g = initialCells(c.key, c.size, c.size, c.seed ?? 0);
  const want = new Int32Array(c.size * c.size);
  for (const [i, v] of c.nonzero) want[i] = v;
  const d = diffCount(g, want);
  ok(d === 0, `init ${c.key} ${c.size}x${c.size} seed ${c.seed}: ${d} cells differ`);
}

// 3. every run case: same start grid, N steps, same end grid
const keysSeen = new Set();
for (const c of fx.runs) {
  keysSeen.add(c.key);
  const s = run(makeState(c.key, c.width, c.height, decode(c.start, c.width, c.height)), c.steps);
  const d = diffCount(encode(s.cells), c.end);
  ok(d === 0, `${c.key} / ${c.label}: ${d} cells differ after ${c.steps} steps`);
  ok(s.gen === c.generation, `${c.key} / ${c.label}: generation ${s.gen} != ${c.generation}`);
}
ok(KEYS.every(k => keysSeen.has(k)) && KEYS.length === 4, 'all four automata have run fixtures');

// 4. small hand checks
const r = mt19937(5);
ok([0, 1, 2, 3, 4, 5].map(() => randint(r, 50)).join(' ') === '35 14 47 38 16 9', 'np.random.seed(5); randint(0, 50) x6');
ok(encode(decode('0a1s', 2, 2)) === '0a1s', 'codec round trip');
const blinker = makeState('game_of_life', 5, 5, decode('0000000000011100000000000', 5, 5));
step(step(blinker));
ok(encode(blinker.cells) === '0000000000011100000000000', 'blinker has period 2');
const st = stats(makeState('wireworld', 2, 2, [0, 1, 1, 0]));
ok(st.active_cells === 2 && Math.abs(st.complexity - 1) < 1e-6, 'stats: active cells and complexity');

console.log(`${checks - fails}/${checks} checks passed (${fx.inits.length} initial grids, ${fx.runs.length} run cases)`);
process.exit(fails ? 1 : 0);
