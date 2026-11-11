// Entry point: animated background, lazy page modules, footer mode, router.
import { start, lazy, route, app, isStatic, $ } from './core.js';
import { background } from './bg.js';

const PAGES = { 'home.js': ['home'], 'lab.js': ['lab'], 'automata.js': ['automata'], 'background.js': ['background'], 'about.js': ['about'] };
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic()
  ? 'static site: every automaton runs in your browser'
  : 'local app: browser engine + Python engine at /api';
background($('#bg'));
start();
