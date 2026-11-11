// Subtle animated background: a coarse Brian's Brain (the same JS engine as the lab) drawn behind the page.
// Static single frame under prefers-reduced-motion; paused while the tab is hidden; reseeded if it dies out.
import { makeState, step } from './automata_engine.js';
import { rng } from './core.js';

const CELL = 10;
const PALETTE = [[0, 0, 0], [255, 210, 63], [63, 169, 255]].map(c => c.map(v => Math.round(v * 0.5)));

export function background(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let s = null, img = null, seed = 3;
  const reset = () => {
    const w = Math.min(200, Math.ceil(innerWidth / CELL)), h = Math.min(130, Math.ceil(innerHeight / CELL));
    canvas.width = w; canvas.height = h;
    const r = rng(seed++);
    s = makeState('brians_brain', w, h, Array.from({ length: w * h }, () => (r() < 0.1 ? 1 : 0)));
    img = ctx.createImageData(w, h);
  };
  const draw = () => {
    const d = img.data;
    for (let i = 0; i < s.cells.length; i++) {
      const [r, g, b] = PALETTE[s.cells[i]];
      d[i * 4] = r; d[i * 4 + 1] = g; d[i * 4 + 2] = b; d[i * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  };
  reset(); draw();
  addEventListener('resize', () => { reset(); draw(); });
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  setInterval(() => {
    if (document.hidden) return;
    step(s);
    if (!s.cells.some(v => v)) reset();
    draw();
  }, 160);
}
