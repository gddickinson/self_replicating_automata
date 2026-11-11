"""Langton's self-reproducing loop (1984): published rule table, standard loop, and a daughter loop by generation 151.

Run: python -m pytest -q tests/test_langton_loop.py
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import self_replicating_automata as sra  # noqa: E402
from langton_rules import LANGTON_INITIAL_LOOP, LANGTON_RULES_CNESWC, build_rule_table  # noqa: E402


def components(grid):
    """Sizes of the 4-connected groups of nonzero cells (no wrap; the loops stay clear of the edges here)."""
    seen = np.zeros(grid.shape, bool)
    sizes = []
    h, w = grid.shape
    for y0, x0 in zip(*np.nonzero(grid)):
        if seen[y0, x0]:
            continue
        seen[y0, x0] = True
        q, n = deque([(y0, x0)]), 0
        while q:
            y, x = q.popleft()
            n += 1
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and grid[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        sizes.append(n)
    return sorted(sizes)


def test_published_table_has_219_rules_over_8_states():
    assert len(LANGTON_RULES_CNESWC) == 219 == len(set(LANGTON_RULES_CNESWC))
    assert all(len(r) == 6 and set(r) <= set("01234567") for r in LANGTON_RULES_CNESWC)


def test_rule_table_is_rotation_symmetric_and_consistent():
    table = build_rule_table()
    for (c, n, e, s, w), v in table.items():
        assert table[(c, w, n, e, s)] == v
    assert sra.LangtonsLoop(50, 50).rules == table


def test_aliases_point_at_langtons_loop():
    assert sra.LangtonLoop is sra.LangtonsLoop and sra.SimplifiedLangtonLoop is sra.LangtonsLoop


def test_standard_initial_loop():
    ll = sra.LangtonsLoop(60, 60)
    assert ll.num_states == 8 and np.count_nonzero(ll.grid) == 85
    ys, xs = np.nonzero(ll.grid)
    assert (ys.max() - ys.min() + 1, xs.max() - xs.min() + 1) == (len(LANGTON_INITIAL_LOOP), max(map(len, LANGTON_INITIAL_LOOP)))


@pytest.fixture(scope="module")
def run_151():
    ll = sra.LangtonsLoop(80, 80)
    table = ll.rules
    unmatched = 0
    sizes = {}
    for t in range(1, 152):
        g = ll.grid
        p = np.pad(g, 1, mode="wrap")
        keys = zip(g.ravel(), p[:-2, 1:-1].ravel(), p[1:-1, 2:].ravel(), p[2:, 1:-1].ravel(), p[1:-1, :-2].ravel())
        unmatched += sum(1 for k in keys if any(k) and tuple(int(v) for v in k) not in table)
        ll.step()
        if t in (1, 100, 151):
            sizes[t] = components(ll.grid)
    return ll, sizes, unmatched


def test_daughter_loop_by_generation_151(run_151):
    """One loop until the daughter forms; by generation 151 there are two separate loops of about 86 cells."""
    _, sizes, _ = run_151
    assert len(sizes[1]) == 1 and len(sizes[100]) == 1
    assert len(sizes[151]) == 2 and all(80 <= n <= 90 for n in sizes[151]), sizes[151]


def test_every_transition_is_in_the_table(run_151):
    """The published table covers every non-quiescent neighbourhood the loop meets while reproducing."""
    assert run_151[2] == 0
