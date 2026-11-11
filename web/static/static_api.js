// Static-site data layer: answers api() GETs from the JSON files exported by scripts/build_static.py
// (api/info.json, api/automata.json). POST /run needs the Python classes, so it is refused here; the lab shows a
// "needs the local app" notice instead of calling it.
const files = new Map();
function file(rel) {
  if (!files.has(rel)) {
    files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  }
  return files.get(rel);
}

export async function staticApi(path, body) {
  const clean = path.split('?')[0].replace(/^\/+/, '');
  if (body || clean === 'run') throw new Error('Running the Python engine needs the local app (python run_web.py).');
  return file(clean);
}
