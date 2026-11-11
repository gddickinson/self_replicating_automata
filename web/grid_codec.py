"""Compact text encoding of CA grids shared by the API, the fixtures and the JS engine (ca_engine.js decode/encode).

A grid of shape (h, w) with states 0..35 is written row-major as one base-36 character per cell ('0'-'9', 'a'-'z').
The automata here have at most 8 states, so one character always suffices.
"""
import numpy as np

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
_LOOKUP = {c: i for i, c in enumerate(DIGITS)}


def encode(grid: np.ndarray) -> str:
    """Encode an int grid as a base-36 string (row-major)."""
    flat = np.asarray(grid).ravel()
    if flat.size and (flat.min() < 0 or flat.max() >= len(DIGITS)):
        raise ValueError("cell states must be in 0..35")
    return "".join(DIGITS[int(v)] for v in flat)


def decode(text: str, width: int, height: int) -> np.ndarray:
    """Decode a base-36 string back to an int32 grid of shape (height, width)."""
    if len(text) != width * height:
        raise ValueError(f"expected {width * height} cells, got {len(text)}")
    try:
        vals = [_LOOKUP[c] for c in text.lower()]
    except KeyError as e:
        raise ValueError(f"invalid cell character {e}") from None
    return np.array(vals, dtype=np.int32).reshape(height, width)
