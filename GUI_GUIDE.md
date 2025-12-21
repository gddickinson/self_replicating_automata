# Von Neumann Automata Simulator - GUI Guide

## Understanding the Display Refresh Issue

The refresh issue you experienced (where the display only updates when resizing the window) is a common problem with matplotlib animations. It typically happens due to:

1. **Backend issues**: Some matplotlib backends don't handle event loops properly
2. **Animation framework**: The `FuncAnimation` approach can have timing/refresh issues
3. **Display server**: X11/Wayland configuration or remote display setups

## Available GUI Versions

I've created **two different GUI implementations** to solve this problem:

### 1. Interactive Matplotlib GUI (RECOMMENDED)
**File:** `automata_interactive_gui.py`

**Features:**
- Uses matplotlib's widget system with proper event-driven updates
- Radio buttons for automaton type selection
- Play/Pause/Step/Reset controls
- Real-time speed adjustment slider
- Grid size control
- Mutation rate control (for Evolving Loop)
- Live statistics display
- Save snapshot functionality
- **Fixes the refresh issue** by using `FuncAnimation` with `blit=False` and proper event handling

**Usage:**
```bash
python automata_interactive_gui.py
```

**Why this works:**
- Uses `cache_frame_data=False` to prevent caching issues
- Implements `blit=False` for more reliable screen updates
- Event-driven architecture ensures proper display refresh
- Works with standard matplotlib backends

**Requirements:**
- matplotlib
- numpy
- Python 3.6+

---

### 2. Tkinter GUI (Full-Featured)
**File:** `automata_gui.py`

**Features:**
- Professional GUI with tkinter framework
- Threaded simulation for smooth performance
- More sophisticated layout
- Progress bars for animation saving
- Better file dialog integration
- More polished look and feel

**Usage:**
```bash
python automata_gui.py
```

**Requirements:**
- matplotlib
- numpy
- tkinter (python3-tk)
- Python 3.6+

**Note:** This version requires tkinter to be installed. If you get `ModuleNotFoundError: No module named 'tkinter'`, install it with:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (via Homebrew)
brew install python-tk
```

---

## Comparison

| Feature | Interactive Matplotlib | Tkinter GUI |
|---------|----------------------|-------------|
| Refresh handling | ✅ Excellent | ✅ Excellent |
| Dependencies | Minimal | Requires tkinter |
| Performance | Good | Excellent (threaded) |
| UI Polish | Good | Professional |
| Animation export | Via matplotlib | With progress bar |
| Easy setup | ✅ Works out of box | Needs tkinter install |
| **Recommendation** | **Use this first** | Use if tkinter available |

---

## Quick Start Guide

### Step 1: Run the Interactive GUI
```bash
python automata_interactive_gui.py
```

### Step 2: Select Automaton Type
- Click on the radio buttons to choose:
  - **Langton Loop**: Classic self-replicating loop
  - **Evolving Loop**: Loop with mutations (adjustable rate)
  - **Von Neumann**: Universal constructor demonstration  
  - **Wire World**: Signal propagation system

### Step 3: Control the Simulation
- **▶ Play**: Start the simulation
- **⏸ Pause**: Pause at current state
- **⏭ Step**: Advance one generation at a time
- **🔄 Reset**: Create fresh automaton

### Step 4: Adjust Parameters
- **Speed slider**: Control update rate (10-500 ms)
- **Grid Size slider**: Change grid dimensions (50-300)
- **Mutation Rate slider**: Adjust evolution speed (Evolving Loop only)

### Step 5: Monitor Statistics
The statistics panel shows:
- **Generation**: Current time step
- **Active Cells**: Non-empty cell count
- **Density**: Percentage of active cells
- **Complexity**: Shannon entropy measure
- **Running**: Simulation status

### Step 6: Save Your Work
- Click **📸 Save Snapshot** to save the current state
- Snapshots are saved to `/mnt/user-data/outputs/`

---

## Technical Details: Fixing the Refresh Issue

The key changes that fix the display refresh problem:

### 1. Proper FuncAnimation Setup
```python
self.animation = FuncAnimation(
    self.fig, 
    self._animation_update,
    interval=self.speed_ms,
    blit=False,              # Critical: disables blitting
    cache_frame_data=False   # Prevents frame caching
)
```

### 2. Event-Driven Updates
Instead of manually calling `canvas.draw()` repeatedly, the GUI uses matplotlib's event system:
- Button clicks trigger immediate updates
- Slider changes refresh the display
- Animation loop handles periodic updates

### 3. Proper Canvas Refresh
```python
self.fig.canvas.draw_idle()  # Schedule update, don't force immediate draw
```

This tells matplotlib to update "when convenient" rather than forcing immediate redraws which can cause conflicts.

---

## Advanced Usage

### Programmatic Control

You can also control the simulators programmatically:

```python
from automata_interactive_gui import InteractiveAutomatonGUI

# Create GUI
gui = InteractiveAutomatonGUI()

# Access the automaton directly
automaton = gui.automaton

# Run specific number of steps
for _ in range(100):
    automaton.step()
    gui._update_display()

# Show the GUI
gui.show()
```

### Customizing the Display

Modify the colormap for different visual styles:

```python
from matplotlib.colors import ListedColormap

# Create custom colormap
custom_colors = ['#000000', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
gui.colormap = ListedColormap(custom_colors)
```

### Batch Processing

Run simulations without GUI for analysis:

```python
from self_replicating_automata import LangtonLoop
import numpy as np

# Create automaton
automaton = LangtonLoop(200, 200)

# Collect statistics over time
stats = []
for gen in range(1000):
    automaton.step()
    active = np.count_nonzero(automaton.grid)
    stats.append({'generation': gen, 'active_cells': active})

# Analyze results
import pandas as pd
df = pd.DataFrame(stats)
print(df.describe())
```

---

## Troubleshooting

### Display Still Not Updating?

If you still experience refresh issues:

1. **Try different matplotlib backend:**
```python
import matplotlib
matplotlib.use('Qt5Agg')  # or 'TkAgg', 'GTK3Agg'
import matplotlib.pyplot as plt
```

2. **Check your matplotlib configuration:**
```bash
python -c "import matplotlib; print(matplotlib.get_backend())"
```

3. **Update matplotlib:**
```bash
pip install --upgrade matplotlib
```

### Performance Issues?

If simulation is slow:

1. **Reduce grid size** (use slider or set to 50-100)
2. **Increase speed interval** (move slider to "Slow" end)
3. **Use smaller automaton types** (Wire World is fastest)

### Can't Save Snapshots?

Make sure the output directory exists and is writable:
```bash
ls -la /mnt/user-data/outputs/
```

---

## Understanding the Statistics

### Complexity (Shannon Entropy)
Measures information content of the grid:
- **0.0**: Uniform grid (all same state)
- **~1.0**: Low diversity
- **~2.5**: High diversity
- **Higher**: More complex patterns

Formula: H = -Σ(p_i × log₂(p_i))

### Density
Percentage of non-empty cells:
- Tracks growth/replication progress
- Self-replicators typically maintain steady density
- Sudden changes indicate replication events

---

## Integration with Your Research

Since you work with microscopy analysis and FLIKA plugins, you might find these parallels interesting:

### Similar Patterns
- **Cellular automata grids** ↔ **Microscopy images**
- **State transitions** ↔ **Particle tracking**
- **Pattern detection** ↔ **Cell segmentation**
- **Evolution tracking** ↔ **Time-lapse analysis**

### Potential Applications
- Model PIEZO1 channel clustering dynamics
- Simulate calcium wave propagation
- Test edge detection algorithms
- Develop particle interaction models

### Code Reusability
The modular structure follows similar patterns to your FLIKA work:
- Base classes for extensibility
- Visualization frameworks
- Real-time data processing
- GUI controls for parameters

---

## Next Steps

1. **Experiment with parameters**: Try different mutation rates, grid sizes
2. **Extend the code**: Create hybrid automata or new rule sets
3. **Analyze patterns**: Export data and analyze replication dynamics
4. **Integrate with research**: Adapt concepts to your microscopy work

---

## References

- von Neumann, J. (1966). *Theory of Self-Reproducing Automata*
- Langton, C. (1984). Self-reproduction in cellular automata
- Sayama, H. (1999). Introduction of structural dissolution into Langton's loop
- Matplotlib Animation Tutorial: https://matplotlib.org/stable/api/animation_api.html

---

## Support

If you encounter any issues or have questions:
1. Check the error message carefully
2. Verify all dependencies are installed
3. Try the alternative GUI version
4. Experiment with different matplotlib backends

Happy simulating! 🔬✨
