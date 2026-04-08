"""
Unit tests for cellular automata classes.

Smoke tests verifying that each automaton initializes correctly,
steps without errors, and produces expected state transitions.
"""

import unittest
import numpy as np
from self_replicating_automata import (
    CellularAutomaton,
    WireWorld,
    GameOfLifeReplicator,
    SimplifiedLangtonLoop,
    BriansBrain,
    LangtonLoop,
    EvolvingLoop,
    VonNeumannConstructor,
)


class TestCellularAutomatonBase(unittest.TestCase):
    """Tests for the CellularAutomaton base class."""

    def test_init_creates_grid(self):
        ca = CellularAutomaton(50, 40, 3)
        self.assertEqual(ca.grid.shape, (40, 50))
        self.assertEqual(ca.num_states, 3)
        self.assertEqual(ca.generation, 0)

    def test_grid_is_all_zeros(self):
        ca = CellularAutomaton(10, 10, 2)
        self.assertTrue(np.all(ca.grid == 0))

    def test_get_neighborhood_toroidal(self):
        ca = CellularAutomaton(5, 5, 2)
        ca.grid[0, 0] = 1  # top-left corner
        neighbors = ca.get_neighborhood(0, 0)
        self.assertEqual(neighbors['center'], 1)
        # North wraps to bottom row
        self.assertEqual(neighbors['north'], ca.grid[4, 0])
        # West wraps to rightmost column
        self.assertEqual(neighbors['west'], ca.grid[0, 4])

    def test_get_moore_neighborhood(self):
        ca = CellularAutomaton(5, 5, 2)
        ca.grid[2, 2] = 1
        moore = ca.get_moore_neighborhood(2, 2)
        self.assertEqual(moore.shape, (3, 3))
        self.assertEqual(moore[1, 1], 1)  # center

    def test_step_not_implemented(self):
        ca = CellularAutomaton(5, 5, 2)
        with self.assertRaises(NotImplementedError):
            ca.step()


class TestWireWorld(unittest.TestCase):
    """Tests for WireWorld automaton."""

    def test_init(self):
        ww = WireWorld(50, 50)
        self.assertEqual(ww.num_states, 4)
        self.assertEqual(ww.generation, 0)

    def test_step_increments_generation(self):
        ww = WireWorld(50, 50)
        ww.step()
        self.assertEqual(ww.generation, 1)

    def test_electron_head_becomes_tail(self):
        """Electron head (2) must become tail (3)."""
        ww = WireWorld(50, 50)
        ww.grid[:] = 0
        ww.grid[5, 5] = 2  # electron head
        ww.step()
        self.assertEqual(ww.grid[5, 5], 3)

    def test_electron_tail_becomes_wire(self):
        """Electron tail (3) must become wire (1)."""
        ww = WireWorld(50, 50)
        ww.grid[:] = 0
        ww.grid[5, 5] = 3  # electron tail
        ww.step()
        self.assertEqual(ww.grid[5, 5], 1)

    def test_empty_stays_empty(self):
        ww = WireWorld(50, 50)
        ww.grid[:] = 0
        ww.step()
        self.assertTrue(np.all(ww.grid == 0))

    def test_wire_with_one_head_becomes_head(self):
        """Wire cell with exactly 1 adjacent electron head becomes head."""
        ww = WireWorld(50, 50)
        ww.grid[:] = 0
        ww.grid[5, 5] = 1  # wire
        ww.grid[5, 6] = 2  # electron head neighbor
        ww.step()
        self.assertEqual(ww.grid[5, 5], 2)

    def test_multiple_steps_no_crash(self):
        ww = WireWorld(50, 50)
        for _ in range(10):
            ww.step()
        self.assertEqual(ww.generation, 10)


class TestGameOfLifeReplicator(unittest.TestCase):
    """Tests for Game of Life variant."""

    def test_init(self):
        gol = GameOfLifeReplicator(50, 50)
        self.assertEqual(gol.num_states, 2)

    def test_step_increments_generation(self):
        gol = GameOfLifeReplicator(50, 50)
        gol.step()
        self.assertEqual(gol.generation, 1)

    def test_empty_grid_stays_empty(self):
        gol = GameOfLifeReplicator(10, 10)
        gol.grid[:] = 0
        gol.step()
        self.assertTrue(np.all(gol.grid == 0))

    def test_blinker_oscillates(self):
        """A horizontal line of 3 should become vertical and back."""
        gol = GameOfLifeReplicator(10, 10)
        gol.grid[:] = 0
        # Horizontal blinker
        gol.grid[5, 4] = 1
        gol.grid[5, 5] = 1
        gol.grid[5, 6] = 1
        gol.step()
        # Should be vertical now
        self.assertEqual(gol.grid[4, 5], 1)
        self.assertEqual(gol.grid[5, 5], 1)
        self.assertEqual(gol.grid[6, 5], 1)
        self.assertEqual(gol.grid[5, 4], 0)
        self.assertEqual(gol.grid[5, 6], 0)

    def test_glider_gun_produces_activity(self):
        """Default init (glider gun) should produce nonzero cells after steps."""
        gol = GameOfLifeReplicator(50, 50)
        initial_active = np.count_nonzero(gol.grid)
        for _ in range(50):
            gol.step()
        self.assertGreater(np.count_nonzero(gol.grid), 0)

    def test_multiple_steps_no_crash(self):
        gol = GameOfLifeReplicator(50, 50)
        for _ in range(20):
            gol.step()
        self.assertEqual(gol.generation, 20)


class TestSimplifiedLangtonLoop(unittest.TestCase):
    """Tests for Simplified Langton Loop."""

    def test_init(self):
        ll = SimplifiedLangtonLoop(50, 50)
        self.assertEqual(ll.num_states, 8)

    def test_has_initial_pattern(self):
        ll = SimplifiedLangtonLoop(50, 50)
        self.assertGreater(np.count_nonzero(ll.grid), 0)

    def test_step_no_crash(self):
        ll = SimplifiedLangtonLoop(50, 50)
        ll.step()
        self.assertEqual(ll.generation, 1)

    def test_multiple_steps(self):
        ll = SimplifiedLangtonLoop(50, 50)
        for _ in range(10):
            ll.step()
        self.assertEqual(ll.generation, 10)


class TestBriansBrain(unittest.TestCase):
    """Tests for Brian's Brain automaton."""

    def test_init(self):
        bb = BriansBrain(50, 50)
        self.assertEqual(bb.num_states, 3)

    def test_alive_becomes_dying(self):
        """Alive (1) always becomes dying (2)."""
        bb = BriansBrain(10, 10)
        bb.grid[:] = 0
        bb.grid[5, 5] = 1
        bb.step()
        self.assertEqual(bb.grid[5, 5], 2)

    def test_dying_becomes_dead(self):
        """Dying (2) always becomes dead (0)."""
        bb = BriansBrain(10, 10)
        bb.grid[:] = 0
        bb.grid[5, 5] = 2
        bb.step()
        self.assertEqual(bb.grid[5, 5], 0)

    def test_birth_with_two_neighbors(self):
        """Dead cell with exactly 2 alive neighbors becomes alive."""
        bb = BriansBrain(10, 10)
        bb.grid[:] = 0
        bb.grid[4, 5] = 1  # alive neighbor
        bb.grid[6, 5] = 1  # alive neighbor
        bb.step()
        self.assertEqual(bb.grid[5, 5], 1)

    def test_multiple_steps(self):
        bb = BriansBrain(30, 30)
        for _ in range(10):
            bb.step()
        self.assertEqual(bb.generation, 10)


class TestAliases(unittest.TestCase):
    """Tests that backward-compatible aliases work."""

    def test_langton_loop_alias(self):
        self.assertIs(LangtonLoop, SimplifiedLangtonLoop)

    def test_evolving_loop_alias(self):
        self.assertIs(EvolvingLoop, BriansBrain)

    def test_von_neumann_constructor_alias(self):
        self.assertIs(VonNeumannConstructor, GameOfLifeReplicator)


if __name__ == "__main__":
    unittest.main()
