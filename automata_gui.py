"""
Von Neumann Self-Replicating Automata Simulator - GUI Version
==============================================================

Comprehensive GUI interface with controls for exploring self-replicating cellular automata.

Features:
- Play/Pause/Reset controls
- Speed adjustment
- Step-by-step execution
- Real-time statistics
- Multiple automaton types
- Save snapshots and animations

Author: George Dickinson's Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Optional

# Import the automaton classes from the original script
from self_replicating_automata import (
    LangtonLoop, EvolvingLoop, VonNeumannConstructor, 
    WireWorld, CellularAutomaton
)


class AutomatonGUI:
    """Comprehensive GUI for cellular automaton simulation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Von Neumann Self-Replicating Automata Simulator")
        self.root.geometry("1400x900")
        
        # Simulation state
        self.automaton: Optional[CellularAutomaton] = None
        self.running = False
        self.simulation_thread = None
        self.speed = 50  # milliseconds between updates
        self.grid_size = 150
        
        # Statistics
        self.stats = {
            'generation': 0,
            'population': 0,
            'active_cells': 0,
            'complexity': 0.0
        }
        
        self._setup_ui()
        self._create_default_automaton()
        
    def _setup_ui(self):
        """Create the user interface"""
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel - Visualization
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._create_control_panel(left_panel)
        self._create_visualization_panel(right_panel)
        
    def _create_control_panel(self, parent):
        """Create control panel with buttons and settings"""
        
        # Title
        title_label = ttk.Label(parent, text="Control Panel", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Automaton Selection
        selection_frame = ttk.LabelFrame(parent, text="Automaton Type", padding=10)
        selection_frame.pack(fill=tk.X, pady=5)
        
        self.automaton_var = tk.StringVar(value="LangtonLoop")
        automaton_types = [
            ("Langton's Loop", "LangtonLoop"),
            ("Evolving Loop", "EvolvingLoop"),
            ("Von Neumann Constructor", "VonNeumannConstructor"),
            ("Wire World", "WireWorld")
        ]
        
        for text, value in automaton_types:
            ttk.Radiobutton(selection_frame, text=text, 
                           variable=self.automaton_var, value=value,
                           command=self._on_automaton_change).pack(anchor=tk.W)
        
        # Grid Size
        grid_frame = ttk.LabelFrame(parent, text="Grid Size", padding=10)
        grid_frame.pack(fill=tk.X, pady=5)
        
        self.grid_size_var = tk.IntVar(value=150)
        ttk.Label(grid_frame, text="Size:").pack(side=tk.LEFT)
        grid_sizes = [50, 100, 150, 200, 300]
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_size_var,
                                 values=grid_sizes, width=8, state='readonly')
        grid_combo.pack(side=tk.LEFT, padx=5)
        grid_combo.bind('<<ComboboxSelected>>', self._on_grid_size_change)
        
        # Mutation Rate (for EvolvingLoop)
        self.mutation_frame = ttk.LabelFrame(parent, text="Mutation Rate", padding=10)
        self.mutation_frame.pack(fill=tk.X, pady=5)
        
        self.mutation_var = tk.DoubleVar(value=0.001)
        ttk.Label(self.mutation_frame, text="Rate:").pack(side=tk.LEFT)
        mutation_entry = ttk.Entry(self.mutation_frame, textvariable=self.mutation_var, width=10)
        mutation_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.mutation_frame, text="(0.0001-0.1)").pack(side=tk.LEFT)
        
        self.mutation_frame.pack_forget()  # Hide initially
        
        # Playback Controls
        control_frame = ttk.LabelFrame(parent, text="Playback Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        btn_frame1 = ttk.Frame(control_frame)
        btn_frame1.pack(fill=tk.X, pady=2)
        
        self.play_btn = ttk.Button(btn_frame1, text="▶ Play", 
                                   command=self._play, width=12)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(btn_frame1, text="⏸ Pause", 
                                    command=self._pause, width=12, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        btn_frame2 = ttk.Frame(control_frame)
        btn_frame2.pack(fill=tk.X, pady=2)
        
        ttk.Button(btn_frame2, text="⏭ Step", 
                  command=self._step, width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame2, text="🔄 Reset", 
                  command=self._reset, width=12).pack(side=tk.LEFT, padx=2)
        
        # Speed Control
        speed_frame = ttk.LabelFrame(parent, text="Simulation Speed", padding=10)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Slow").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(speed_frame, from_=10, to=500, 
                               variable=self.speed_var, orient=tk.HORIZONTAL,
                               command=self._on_speed_change)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(speed_frame, text="Fast").pack(side=tk.LEFT)
        
        self.speed_label = ttk.Label(speed_frame, text="50 ms")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.gen_label = ttk.Label(stats_frame, text="Generation: 0")
        self.gen_label.pack(anchor=tk.W)
        
        self.pop_label = ttk.Label(stats_frame, text="Active Cells: 0")
        self.pop_label.pack(anchor=tk.W)
        
        self.density_label = ttk.Label(stats_frame, text="Density: 0.0%")
        self.density_label.pack(anchor=tk.W)
        
        self.complexity_label = ttk.Label(stats_frame, text="Complexity: 0.0")
        self.complexity_label.pack(anchor=tk.W)
        
        # File Operations
        file_frame = ttk.LabelFrame(parent, text="File Operations", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="📸 Save Snapshot", 
                  command=self._save_snapshot).pack(fill=tk.X, pady=2)
        
        ttk.Button(file_frame, text="🎬 Save Animation (GIF)", 
                  command=self._save_animation).pack(fill=tk.X, pady=2)
        
        # Info
        info_frame = ttk.LabelFrame(parent, text="Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        info_text = tk.Text(info_frame, wrap=tk.WORD, height=8, width=30)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert('1.0', self._get_info_text())
        info_text.config(state=tk.DISABLED)
        
    def _create_visualization_panel(self, parent):
        """Create matplotlib visualization panel"""
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 10), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbar frame
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)
        
        ttk.Label(toolbar_frame, text="Zoom: Use mouse scroll | Pan: Click and drag", 
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
    def _create_default_automaton(self):
        """Create default automaton"""
        self._create_automaton()
        self._update_display()
        
    def _create_automaton(self):
        """Create new automaton based on current selection"""
        automaton_type = self.automaton_var.get()
        size = self.grid_size_var.get()
        
        if automaton_type == "LangtonLoop":
            self.automaton = LangtonLoop(size, size)
            self.colormap = ListedColormap(['black', 'white', 'red', 'blue', 'yellow'])
        elif automaton_type == "EvolvingLoop":
            mutation_rate = self.mutation_var.get()
            self.automaton = EvolvingLoop(size, size, mutation_rate=mutation_rate)
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
            
        self._update_statistics()
        
    def _update_display(self):
        """Update the matplotlib display"""
        if self.automaton is None:
            return
            
        self.ax.clear()
        self.ax.imshow(self.automaton.grid, cmap=self.colormap, 
                      interpolation='nearest', vmin=0, 
                      vmax=self.automaton.num_states-1)
        self.ax.set_title(f'{self.automaton.__class__.__name__} - Generation {self.automaton.generation}',
                         fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
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
        
        self.gen_label.config(text=f"Generation: {generation}")
        self.pop_label.config(text=f"Active Cells: {active_cells:,}")
        self.density_label.config(text=f"Density: {density:.2f}%")
        self.complexity_label.config(text=f"Complexity: {entropy:.3f}")
        
    def _simulation_loop(self):
        """Main simulation loop (runs in separate thread)"""
        while self.running:
            if self.automaton is not None:
                self.automaton.step()
                
                # Update display and statistics on main thread
                self.root.after(0, self._update_display)
                self.root.after(0, self._update_statistics)
                
            time.sleep(self.speed / 1000.0)
            
    def _play(self):
        """Start simulation"""
        if not self.running:
            self.running = True
            self.play_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            
            # Start simulation in separate thread
            self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.simulation_thread.start()
            
    def _pause(self):
        """Pause simulation"""
        self.running = False
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        
    def _step(self):
        """Advance simulation by one step"""
        if self.automaton is not None:
            self.automaton.step()
            self._update_display()
            self._update_statistics()
            
    def _reset(self):
        """Reset simulation"""
        was_running = self.running
        if was_running:
            self._pause()
            
        self._create_automaton()
        self._update_display()
        
        if was_running:
            self.root.after(100, self._play)
            
    def _on_automaton_change(self):
        """Handle automaton type change"""
        # Show/hide mutation rate control
        if self.automaton_var.get() == "EvolvingLoop":
            self.mutation_frame.pack(fill=tk.X, pady=5, after=self.automaton_var.master.master)
        else:
            self.mutation_frame.pack_forget()
            
        self._reset()
        
    def _on_grid_size_change(self, event=None):
        """Handle grid size change"""
        self._reset()
        
    def _on_speed_change(self, value):
        """Handle speed slider change"""
        self.speed = int(float(value))
        self.speed_label.config(text=f"{self.speed} ms")
        
    def _save_snapshot(self):
        """Save current state as image"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"{self.automaton.__class__.__name__}_gen_{self.automaton.generation}.png"
        )
        
        if filename:
            self.fig.savefig(filename, bbox_inches='tight', dpi=150)
            messagebox.showinfo("Success", f"Snapshot saved to:\n{filename}")
            
    def _save_animation(self):
        """Save animation as GIF"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
            initialfile=f"{self.automaton.__class__.__name__}_animation.gif"
        )
        
        if filename:
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Creating Animation")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="Creating animation...", 
                     font=('Arial', 12)).pack(pady=20)
            
            progress_var = tk.IntVar()
            progress_bar = ttk.Progressbar(progress_window, variable=progress_var, 
                                          maximum=200, length=300)
            progress_bar.pack(pady=10)
            
            status_label = ttk.Label(progress_window, text="Frame 0/200")
            status_label.pack(pady=5)
            
            def create_animation():
                from matplotlib.animation import PillowWriter
                
                # Store current state
                current_grid = self.automaton.grid.copy()
                current_gen = self.automaton.generation
                
                # Reset automaton
                self._create_automaton()
                
                # Create animation
                fig_temp = Figure(figsize=(8, 8))
                ax_temp = fig_temp.add_subplot(111)
                
                im = ax_temp.imshow(self.automaton.grid, cmap=self.colormap,
                                   interpolation='nearest', vmin=0,
                                   vmax=self.automaton.num_states-1)
                ax_temp.axis('off')
                
                writer = PillowWriter(fps=20)
                
                with writer.saving(fig_temp, filename, dpi=100):
                    for i in range(200):
                        self.automaton.step()
                        im.set_array(self.automaton.grid)
                        ax_temp.set_title(f'Generation {self.automaton.generation}')
                        writer.grab_frame()
                        
                        # Update progress
                        progress_var.set(i + 1)
                        status_label.config(text=f"Frame {i+1}/200")
                        progress_window.update()
                
                plt.close(fig_temp)
                
                # Restore state
                self.automaton.grid = current_grid
                self.automaton.generation = current_gen
                self._update_display()
                
                progress_window.destroy()
                messagebox.showinfo("Success", f"Animation saved to:\n{filename}")
            
            # Run in thread
            threading.Thread(target=create_animation, daemon=True).start()
            
    def _get_info_text(self):
        """Get information text for current automaton"""
        return """Von Neumann Self-Replicating Automata

Select an automaton type and click Play to watch self-replication in action!

• Langton's Loop: Simplified self-replicator
• Evolving Loop: Includes mutations
• Von Neumann Constructor: Shows construction process
• Wire World: Signal propagation

Use the controls to adjust speed, step through, or reset."""


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set icon and style
    style = ttk.Style()
    style.theme_use('clam')  # Modern looking theme
    
    app = AutomatonGUI(root)
    
    # Handle window close
    def on_closing():
        app.running = False
        if app.simulation_thread and app.simulation_thread.is_alive():
            app.simulation_thread.join(timeout=1.0)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
