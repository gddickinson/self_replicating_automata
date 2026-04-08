"""
Von Neumann Self-Replicating Automata Simulator - Interactive GUI
=================================================================

Interactive matplotlib-based GUI with controls for exploring self-replicating
cellular automata. This version uses matplotlib's widget system for compatibility.

Features:
- Play/Pause/Reset/Step controls
- Speed adjustment
- Real-time statistics
- Multiple automaton types with easy switching
- Save snapshots
- Proper display refresh handling

Author: George Dickinson's Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, RadioButtons, TextBox
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
import time

# Import the automaton classes
from self_replicating_automata import (
    LangtonLoop, EvolvingLoop, VonNeumannConstructor,
    WireWorld, CellularAutomaton
)


class InteractiveAutomatonGUI:
    """Interactive GUI for cellular automaton simulation using matplotlib widgets"""

    def __init__(self):
        # Create figure with subplots for controls and visualization
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Von Neumann Self-Replicating Automata Simulator',
                         fontsize=16, fontweight='bold')

        # Layout: main plot + control panels
        gs = self.fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3,
                                   left=0.05, right=0.95, top=0.93, bottom=0.05)

        # Main visualization (takes up most of the space)
        self.ax_main = self.fig.add_subplot(gs[:, 1:])

        # Control panels on the left
        self.ax_type = self.fig.add_subplot(gs[0, 0])
        self.ax_controls = self.fig.add_subplot(gs[1, 0])
        self.ax_stats = self.fig.add_subplot(gs[2, 0])

        # Turn off axes for control panels
        for ax in [self.ax_type, self.ax_controls, self.ax_stats]:
            ax.axis('off')

        # Simulation state
        self.automaton = None
        self.running = False
        self.animation = None
        self.speed_ms = 50
        self.grid_size = 150
        self.mutation_rate = 0.001
        self.current_type = "LangtonLoop"

        self._setup_controls()
        self._create_automaton()
        self._update_display()
        self._start_animation()

    def _setup_controls(self):
        """Setup all interactive controls"""

        # === Automaton Type Selection ===
        ax_radio = plt.axes([0.02, 0.70, 0.15, 0.18])
        ax_radio.set_title('Automaton Type', fontsize=10, fontweight='bold')
        self.radio = RadioButtons(ax_radio,
                                  ('Simple Loop', "Brian's Brain",
                                   'Game of Life', 'Wire World'),
                                  active=0)
        self.radio.on_clicked(self._on_type_change)

        # === Playback Controls ===
        # Play button
        ax_play = plt.axes([0.02, 0.58, 0.07, 0.04])
        self.btn_play = Button(ax_play, '▶ Play', color='lightgreen')
        self.btn_play.on_clicked(self._play)

        # Pause button
        ax_pause = plt.axes([0.10, 0.58, 0.07, 0.04])
        self.btn_pause = Button(ax_pause, '⏸ Pause', color='lightcoral')
        self.btn_pause.on_clicked(self._pause)

        # Step button
        ax_step = plt.axes([0.02, 0.53, 0.07, 0.04])
        self.btn_step = Button(ax_step, '⏭ Step', color='lightblue')
        self.btn_step.on_clicked(self._step)

        # Reset button
        ax_reset = plt.axes([0.10, 0.53, 0.07, 0.04])
        self.btn_reset = Button(ax_reset, '🔄 Reset', color='lightyellow')
        self.btn_reset.on_clicked(self._reset)

        # === Speed Control ===
        ax_speed = plt.axes([0.02, 0.46, 0.15, 0.03])
        self.slider_speed = Slider(ax_speed, 'Speed', 10, 500,
                                   valinit=50, valstep=10,
                                   color='steelblue')
        self.slider_speed.on_changed(self._on_speed_change)
        self.slider_speed.label.set_text('Speed (ms)')

        # === Grid Size Control ===
        ax_grid = plt.axes([0.02, 0.40, 0.15, 0.03])
        self.slider_grid = Slider(ax_grid, 'Grid', 50, 300,
                                 valinit=150, valstep=50,
                                 color='teal')
        self.slider_grid.on_changed(self._on_grid_change)
        self.slider_grid.label.set_text('Grid Size')

        # === Mutation Rate (for Evolving Loop) ===
        ax_mutation = plt.axes([0.02, 0.34, 0.15, 0.03])
        self.slider_mutation = Slider(ax_mutation, 'Mutation', 0.0001, 0.01,
                                      valinit=0.001, valfmt='%.4f',
                                      color='purple')
        self.slider_mutation.on_changed(self._on_mutation_change)
        self.slider_mutation.label.set_text('Mutation Rate')
        self.slider_mutation.ax.set_visible(False)  # Hide initially

        # === Save Snapshot Button ===
        ax_save = plt.axes([0.02, 0.26, 0.15, 0.04])
        self.btn_save = Button(ax_save, '📸 Save Snapshot', color='lavender')
        self.btn_save.on_clicked(self._save_snapshot)

        # === Statistics Display ===
        self.ax_stats.set_xlim(0, 1)
        self.ax_stats.set_ylim(0, 1)

        self.text_stats = self.ax_stats.text(0.05, 0.9, '',
                                            transform=self.ax_stats.transAxes,
                                            verticalalignment='top',
                                            fontfamily='monospace',
                                            fontsize=9)

        # Add title to stats area
        self.ax_stats.text(0.05, 0.98, 'Statistics',
                          transform=self.ax_stats.transAxes,
                          fontsize=10, fontweight='bold',
                          verticalalignment='top')

    def _create_automaton(self):
        """Create new automaton based on current selection"""
        type_map = {
            'Simple Loop': 'LangtonLoop',
            "Brian's Brain": 'EvolvingLoop',
            'Game of Life': 'VonNeumannConstructor',
            'Wire World': 'WireWorld'
        }

        automaton_type = type_map.get(self.current_type, 'WireWorld')
        size = int(self.grid_size)

        if automaton_type == "LangtonLoop":
            self.automaton = LangtonLoop(size, size)
            self.colormap = ListedColormap(['black', 'white', 'red', 'blue', 'yellow'])
        elif automaton_type == "EvolvingLoop":
            self.automaton = EvolvingLoop(size, size, mutation_rate=self.mutation_rate)
            self.colormap = ListedColormap(['black', 'white', 'red', 'orange',
                                           'yellow', 'green', 'blue', 'purple'])
        elif automaton_type == "VonNeumannConstructor":
            self.automaton = VonNeumannConstructor(size, size)
            self.colormap = ListedColormap(['black', 'gray', 'red', 'orange',
                                           'yellow', 'green', 'blue', 'cyan',
                                           'magenta', 'white'])
        elif automaton_type == "WireWorld":
            self.automaton = WireWorld(size, size)
            self.colormap = ListedColormap(['black', 'yellow', 'blue', 'red'])

    def _update_display(self):
        """Update the visualization"""
        if self.automaton is None:
            return

        self.ax_main.clear()
        self.ax_main.imshow(self.automaton.grid, cmap=self.colormap,
                           interpolation='nearest', vmin=0,
                           vmax=self.automaton.num_states-1)
        self.ax_main.set_title(f'{self.automaton.__class__.__name__} - Generation {self.automaton.generation}',
                              fontsize=12, pad=10)
        self.ax_main.axis('off')

        # Update statistics
        self._update_statistics()

    def _update_statistics(self):
        """Update statistics display"""
        if self.automaton is None:
            return

        generation = self.automaton.generation
        active_cells = np.count_nonzero(self.automaton.grid)
        total_cells = self.automaton.grid.size
        density = (active_cells / total_cells) * 100

        # Calculate complexity (Shannon entropy)
        unique, counts = np.unique(self.automaton.grid, return_counts=True)
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

        stats_text = f"""
Generation: {generation:,}
Active Cells: {active_cells:,}
Total Cells: {total_cells:,}
Density: {density:.2f}%
Complexity: {entropy:.3f}
Running: {'Yes' if self.running else 'No'}
Speed: {self.speed_ms} ms
        """

        self.text_stats.set_text(stats_text.strip())

    def _animation_update(self, frame):
        """Animation update function"""
        if self.running and self.automaton is not None:
            self.automaton.step()
            self._update_display()
        return []

    def _start_animation(self):
        """Start the animation loop"""
        # Use FuncAnimation with blit=False for better compatibility
        self.animation = FuncAnimation(
            self.fig,
            self._animation_update,
            interval=self.speed_ms,
            blit=False,
            cache_frame_data=False
        )

    def _play(self, event):
        """Start simulation"""
        self.running = True
        self._update_statistics()

    def _pause(self, event):
        """Pause simulation"""
        self.running = False
        self._update_statistics()

    def _step(self, event):
        """Advance by one step"""
        if self.automaton is not None:
            self.automaton.step()
            self._update_display()

    def _reset(self, event):
        """Reset simulation"""
        was_running = self.running
        self.running = False
        self._create_automaton()
        self._update_display()
        if was_running:
            self.running = True

    def _on_type_change(self, label):
        """Handle automaton type change"""
        self.current_type = label

        # Hide mutation slider (not used in corrected versions)
        self.slider_mutation.ax.set_visible(False)

        self._reset(None)
        self.fig.canvas.draw_idle()

    def _on_speed_change(self, val):
        """Handle speed change"""
        self.speed_ms = int(val)
        if self.animation:
            self.animation.event_source.interval = self.speed_ms
        self._update_statistics()

    def _on_grid_change(self, val):
        """Handle grid size change"""
        self.grid_size = int(val)
        # Don't auto-reset, let user decide

    def _on_mutation_change(self, val):
        """Handle mutation rate change"""
        self.mutation_rate = float(val)

    def _save_snapshot(self, event):
        """Save current state"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"automata_snapshot_{self.automaton.__class__.__name__}_{timestamp}.png"

        # Save to current directory
        filepath = f"./{filename}"
        self.fig.savefig(filepath, bbox_inches='tight', dpi=150)
        print(f"Snapshot saved: {filepath}")

        # Also update button text temporarily
        original_label = self.btn_save.label.get_text()
        self.btn_save.label.set_text('✓ Saved!')
        self.fig.canvas.draw_idle()

        # Reset button text after a moment
        def reset_label():
            time.sleep(1)
            self.btn_save.label.set_text(original_label)
            self.fig.canvas.draw_idle()

        import threading
        threading.Thread(target=reset_label, daemon=True).start()

    def show(self):
        """Display the GUI"""
        plt.show()


def main():
    """Main entry point"""
    print("=" * 60)
    print("Von Neumann Self-Replicating Automata Simulator")
    print("=" * 60)
    print("\nControls:")
    print("  - Select automaton type from radio buttons")
    print("  - Use Play/Pause/Step/Reset buttons")
    print("  - Adjust speed and grid size with sliders")
    print("  - Save snapshots to outputs directory")
    print("\nPress Ctrl+C or close window to exit")
    print("=" * 60)
    print()

    # Create and show GUI
    gui = InteractiveAutomatonGUI()
    gui.show()


if __name__ == "__main__":
    main()
