"""Web interface for self_replicating_automata (FastAPI + static ES-module front end; also the GitHub Pages site).

Contents:
    app.py        -- FastAPI app: /api/info, /api/automata, POST /api/run; STATIC_ENDPOINTS for the static export
    catalogue.py  -- catalogue(), entry(), colours(), langton_rules(), gosper_gun(), make(), run(): all via the repo's classes
    grid_codec.py -- encode()/decode(): base-36 one-character-per-cell grid text (shared with the JS engine)
    static/       -- the front end (see INTERFACE.md)
"""
