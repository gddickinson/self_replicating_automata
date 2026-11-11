// Canvas view for the lab: draws a CA state one pixel per cell (scaled up with crisp edges) and turns pointer
// drags into cell edits. Left button paints the selected state; right button or Shift paints state 0.

export function hexToRgb(hex) {
  const h = hex.replace('#', '');
  return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
}

export function makeView(stage, { label, onPaint }) {
  const canvas = document.createElement('canvas');
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', label);
  stage.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  let img = null, colors = [[0, 0, 0]], w = 0, h = 0;

  function render(s) {
    if (s.w !== w || s.h !== h) {
      w = canvas.width = s.w; h = canvas.height = s.h;
      img = ctx.createImageData(w, h);
    }
    const d = img.data;
    for (let i = 0; i < s.cells.length; i++) {
      const c = colors[s.cells[i]] || [128, 128, 128];
      d[i * 4] = c[0]; d[i * 4 + 1] = c[1]; d[i * 4 + 2] = c[2]; d[i * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  }

  // pointer -> cell, with a straight line between successive samples so fast drags leave no gaps
  let last = null, erase = false;
  const cellAt = e => {
    const r = canvas.getBoundingClientRect();
    return [Math.floor((e.clientX - r.left) / r.width * w), Math.floor((e.clientY - r.top) / r.height * h)];
  };
  const paintTo = (x, y) => {
    const [x0, y0] = last || [x, y];
    const n = Math.max(Math.abs(x - x0), Math.abs(y - y0), 1);
    for (let k = 0; k <= n; k++) {
      const cx = Math.round(x0 + (x - x0) * k / n), cy = Math.round(y0 + (y - y0) * k / n);
      if (cx >= 0 && cy >= 0 && cx < w && cy < h) onPaint(cx, cy, erase);
    }
    last = [x, y];
  };
  canvas.addEventListener('contextmenu', e => e.preventDefault());
  canvas.addEventListener('pointerdown', e => {
    erase = e.button === 2 || e.shiftKey;
    last = null;
    canvas.setPointerCapture(e.pointerId);
    paintTo(...cellAt(e));
  });
  canvas.addEventListener('pointermove', e => { if (canvas.hasPointerCapture(e.pointerId)) paintTo(...cellAt(e)); });
  canvas.addEventListener('pointerup', () => { last = null; });

  return {
    canvas, render,
    setColors(hexes) { colors = hexes.map(hexToRgb); },
  };
}
