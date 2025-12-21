# Von Neumann Self-Replicating Automata Simulator

## Overview

This Python implementation provides interactive visualizations of several types of self-replicating cellular automata, inspired by John von Neumann's pioneering work on artificial self-reproduction.

## Theoretical Background

### Von Neumann's Original Work (1940s-1950s)
Von Neumann's self-replicating automaton was designed to prove that machines could theoretically reproduce themselves. His system included:
- **29 cell states** in a 2D cellular grid
- **Universal constructor**: Could build any pattern based on instructions
- **Tape/memory**: Stored the "genome" or construction instructions
- **Copier**: Duplicated the instructions for offspring

### Key Insight
Von Neumann solved the paradox: "How can something create something as complex as itself?" by using a two-fold approach:
1. Instructions used as **data** (interpreted to build the offspring)
2. Instructions used as **passive information** (copied blindly to offspring)

This predates and parallels the discovery of DNA's dual role!

## Implementations in This Simulator

### 1. Langton's Self-Replicating Loop
- **Simplified version** of von Neumann's idea (uses only 8 states)
- Creates a closed loop that extends an "arm" to replicate
- Much more practical than original 29-state system
- **Historical note**: Published in 1984, 40 years after von Neumann's work

### 2. Evolving Loop (Evoloops)
- Based on Sayama's 1999 breakthrough
- Can undergo **Darwinian evolution** through:
  - Spontaneous mutations
  - Natural selection
  - Inheritable variation
- First CA system to demonstrate true evolution of self-reproducing organisms

### 3. Von Neumann Universal Constructor
- Simplified demonstration of universal construction principles
- Shows:
  - Instruction tape (genome)
  - Construction arm
  - Signal propagation
  - Pattern assembly

### 4. Wire World
- Not a replicator, but demonstrates **signal propagation**
- Important for understanding how information flows in self-replicating systems
- Shows electron-like signals moving through conductors

## Requirements

```bash
pip install numpy matplotlib
```

## Usage

### Basic Usage
```bash
python self_replicating_automata.py
```

Then select from the menu:
1. Langton's Loop
2. Evolving Loop (with mutation)
3. Von Neumann Constructor
4. Wire World
5. Compare all side-by-side

### Programmatic Usage

```python
from self_replicating_automata import LangtonLoop, AutomatonVisualizer

# Create automaton
automaton = LangtonLoop(width=150, height=150)

# Create visualizer
viz = AutomatonVisualizer(automaton)

# Animate
viz.animate(frames=500, interval=50)

# Or save animation
viz.animate(frames=500, interval=50, save_path='output.gif')

# Save snapshot
viz.save_snapshot('snapshot.png')
```

### Customization Examples

```python
# Evolving loop with high mutation rate
from self_replicating_automata import EvolvingLoop
automaton = EvolvingLoop(width=200, height=200, mutation_rate=0.01)

# Create custom visualization
viz = AutomatonVisualizer(automaton)
viz.animate(frames=1000, interval=30)
```

## Understanding the Output

### Langton's Loop
- **White**: Structure/sheath
- **Red**: Core/genetic information
- **Blue**: Growing arm
- **Yellow**: Signal carriers
- Watch for: Loop extending arm, arm forming new loop

### Evolving Loop
- **Multiple colors**: Different genetic variants
- **Mutations**: Color changes indicate genetic variation
- Watch for: Loops of different sizes, faster/slower replicators

### Von Neumann Constructor
- **Gray**: Structural elements
- **Red/Orange/Yellow**: Different instructions on tape
- **Blue/Cyan**: Signals and construction arm
- Watch for: Arm reading tape, extending based on instructions

### Wire World
- **Yellow**: Wire/conductor
- **Blue**: Electron head
- **Red**: Electron tail
- Watch for: Electrons circulating, signals propagating

## Current Research Directions (2024-2025)

1. **Open-Ended Evolution**: Creating systems that evolve indefinitely with increasing complexity
2. **Continuous Cellular Automata**: Moving beyond discrete states
3. **Computational Complexity**: Understanding minimum complexity for self-reproduction
4. **Physical Implementation**: Nano-scale and molecular self-replicators

## Extending the Code

### Create Your Own Automaton

```python
from self_replicating_automata import CellularAutomaton

class MyAutomaton(CellularAutomaton):
    def __init__(self, width=100, height=100):
        super().__init__(width, height, num_states=6)
        # Initialize your pattern
        
    def step(self):
        new_grid = self.grid.copy()
        # Implement your transition rules
        # Access neighbors with self.get_neighborhood(x, y)
        self.grid = new_grid
        self.generation += 1
```

### Experiment Ideas

1. **Vary mutation rates** in EvolvingLoop (0.0001 to 0.1)
2. **Change initial patterns** in constructors
3. **Add new cell states** and transition rules
4. **Implement competitive environments** (multiple replicators)
5. **Track statistics**: replication rate, survival time, population

## Key Concepts to Observe

1. **Self-Description**: The system contains a description of itself
2. **Universal Construction**: Building arbitrary patterns from instructions
3. **Information Duplication**: Copying genetic information to offspring
4. **Emergence**: Complex behavior from simple rules
5. **Evolution**: Variation and selection over generations

## Performance Notes

- Grid size 100x100: Real-time performance
- Grid size 200x200: Slower but more detail
- Grid size 500x500: Good for screenshots, slow animation

## References

- von Neumann, J. (1966). Theory of Self-Reproducing Automata
- Langton, C. (1984). Self-reproduction in cellular automata
- Sayama, H. (1999). Introduction of structural dissolution into Langton's self-reproducing loop
- Sayama, H. & Nehaniv, C.L. (2025). Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops

## Tips for Visualization

- **Start small**: Begin with smaller grids (100x100) to see behavior clearly
- **Increase frames**: Run longer simulations (1000+ frames) to see full replication cycles
- **Save animations**: Use `save_path` parameter to create GIFs for presentations
- **Compare**: Use option 5 to see all automata simultaneously
- **Experiment**: Modify transition rules to create hybrid systems

## License

This implementation is for educational purposes, demonstrating the principles described in von Neumann's Theory of Self-Reproducing Automata.

---

**Note**: These are simplified demonstrations. von Neumann's original 29-state automaton is far more complex and truly universal - it can construct any pattern, including a complete copy of itself with arbitrary complexity.
