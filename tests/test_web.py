"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific API tests -----------------------------------------------------------------------------------
import json  # noqa: E402

import numpy as np  # noqa: E402

import self_replicating_automata as sra  # noqa: E402
from web import catalogue as cat  # noqa: E402
from web.grid_codec import decode, encode  # noqa: E402

FIX = json.loads((ROOT / "tests" / "fixtures" / "engine_fixtures.json").read_text())


def test_catalogue_covers_every_automaton_class():
    autos = client.get("/api/automata").json()
    classes = {c for c in vars(sra).values()
               if isinstance(c, type) and issubclass(c, sra.CellularAutomaton) and c is not sra.CellularAutomaton}
    assert {a["class"] for a in autos} == {c.__name__ for c in classes}
    for a in autos:
        assert getattr(sra, a["alias"]).__name__ == a["class"]          # aliases at the bottom of the module
        assert len(a["colors"]) == len(a["state_names"]) == a["num_states"]
        assert "def step" in a["step_source"] and a["doc"]


def test_gui_labels_are_the_guis_own():
    """The labels shown on the site are the strings the two desktop GUIs use."""
    interactive = (ROOT / "automata_interactive_gui.py").read_text()
    tk = (ROOT / "automata_gui.py").read_text()
    for a in cat.AUTOMATA.values():
        assert f"'{a['interactive']}'" in interactive or f'"{a["interactive"]}"' in interactive
        assert f'"{a["tk"]}"' in tk


def test_info_counts():
    info = client.get("/api/info").json()
    assert info["automata"] == 4 and info["max_states"] == 8
    assert info["langton_rules"] == 219
    assert info["gun_cells"] == int(sra.GameOfLifeReplicator(50, 50).grid.sum())


def test_fixture_constants_current():
    assert FIX["rules"] == cat.langton_rules() and FIX["gun"] == cat.gosper_gun() and FIX["sizes"] == cat.SIZES


@pytest.mark.parametrize("case", FIX["inits"], ids=[f"{c['key']}:{c['size']}:{c['seed']}" for c in FIX["inits"]])
def test_init_fixture_current(case):
    """The constructor grids the JS initialisers are tested against still match the Python classes."""
    g = cat.make(case["key"], case["size"], case["size"], case["seed"] if case["seed"] is not None else 0).grid.ravel()
    nz = np.flatnonzero(g)
    assert [[int(i), int(g[i])] for i in nz] == case["nonzero"]


@pytest.mark.parametrize("case", FIX["runs"], ids=[f"{c['key']}:{c['label']}" for c in FIX["runs"]])
def test_run_reproduces_fixture(case):
    """The run fixtures still match the Python step() (through the real API)."""
    r = client.post("/api/run", json={"key": case["key"], "width": case["width"], "height": case["height"],
                                      "cells": case["start"], "steps": case["steps"]} | case["params"])
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["cells"] == case["end"] and out["generation"] == case["generation"]


def test_run_rejects_bad_input():
    ok = {"key": "game_of_life", "width": 4, "height": 4, "cells": "0" * 16, "steps": 1}
    assert client.post("/api/run", json=ok).status_code == 200
    assert client.post("/api/run", json=ok | {"key": "nope"}).status_code == 404
    assert client.post("/api/run", json=ok | {"cells": "0" * 15}).status_code == 400
    assert client.post("/api/run", json=ok | {"cells": "2" + "0" * 15}).status_code == 400   # state 2 in a 2-state CA
    big = {"width": 300, "height": 300, "cells": "0" * 90000, "steps": 100}
    assert client.post("/api/run", json=ok | big).status_code == 400


def test_run_stats_match_gui_formula():
    out = client.post("/api/run", json={"key": "wireworld", "width": 2, "height": 2, "cells": "0110", "steps": 0}).json()
    assert out["stats"]["active_cells"] == 2 and abs(out["stats"]["complexity"] - 1) < 1e-6


def test_codec_round_trip():
    g = np.arange(36, dtype=np.int32).reshape(4, 9)
    assert (decode(encode(g), 9, 4) == g).all()


def test_web_colours_match_desktop_rendering():
    """The lab draws each state with exactly the colour the desktop GUIs' cmap/norm give it."""
    from matplotlib.colors import to_hex

    from automata_colors import colormap_and_norm
    for a in client.get("/api/automata").json():
        cmap, norm = colormap_and_norm(a["alias"], a["num_states"])
        assert a["colors"] == [to_hex(cmap(norm(i))) for i in range(a["num_states"])]
