"""FastAPI web app for Self-Replicating Automata: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8140, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
POST /api/run (the real Python classes stepping a grid) is server-only; the static site steps in JS instead.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from web import catalogue as cat

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Self-Replicating Automata")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    autos = cat.catalogue()
    return {
        "title": "Self-Replicating Automata",
        "automata": len(autos), "max_states": max(a["num_states"] for a in autos),
        "langton_rules": len(cat.langton_rules()), "gun_cells": cat.gosper_gun()["cells"],
        "sizes": cat.SIZES, "default_size": cat.DEFAULT_SIZE,
    }


@app.get("/api/automata")
def automata():
    """Every automaton class: names, states, colours, docstrings and source of step() / the initialiser."""
    return cat.catalogue()


class RunRequest(BaseModel):
    key: str
    width: int = Field(gt=0, le=300)
    height: int = Field(gt=0, le=300)
    cells: str
    steps: int = Field(ge=0, le=5000)
    mutation_rate: float = Field(0.0, ge=0, le=1)   # Brian's Brain only
    seed: int = Field(0, ge=0, le=2**32 - 1)        # Brian's Brain mutation RandomState seed


@app.post("/api/run")
def run(req: RunRequest):
    """Step a grid N times with the real Python class (used to cross-check the browser engine)."""
    try:
        return cat.run(req.key, req.cells, req.width, req.height, req.steps, req.mutation_rate, req.seed)
    except KeyError:
        raise HTTPException(404, f"unknown automaton {req.key}") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/automata"]
