"""
Comprehensive Automaton Diagnostic Tool
========================================

Tests all automaton types and generates detailed output for debugging.
Creates visual snapshots and detailed text reports showing exactly what's happening.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import sys
import os
from datetime import datetime

# Import automaton classes
from self_replicating_automata import (
    LangtonLoop, EvolvingLoop, VonNeumannConstructor,
    WireWorld, CellularAutomaton
)


class AutomatonDiagnostic:
    """Diagnostic tool for testing and visualizing automaton behavior"""

    def __init__(self, output_dir="./diagnostics"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.report = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log(self, message):
        """Log message to report and print"""
        self.report.append(message)
        print(message)

    def analyze_grid(self, automaton, label=""):
        """Analyze grid state and return statistics"""
        grid = automaton.grid

        # Count cells by state
        unique, counts = np.unique(grid, return_counts=True)
        state_counts = dict(zip(unique, counts))

        # Calculate metrics
        total_cells = grid.size
        active_cells = np.count_nonzero(grid)
        density = (active_cells / total_cells) * 100

        # Calculate entropy
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

        stats = {
            'label': label,
            'generation': automaton.generation,
            'grid_shape': grid.shape,
            'total_cells': total_cells,
            'active_cells': active_cells,
            'density': density,
            'entropy': entropy,
            'state_counts': state_counts,
            'unique_states': len(unique),
            'grid_min': grid.min(),
            'grid_max': grid.max()
        }

        return stats

    def print_stats(self, stats):
        """Print statistics in readable format"""
        self.log(f"\n{stats['label']}")
        self.log(f"  Generation: {stats['generation']}")
        self.log(f"  Grid Shape: {stats['grid_shape']}")
        self.log(f"  Total Cells: {stats['total_cells']:,}")
        self.log(f"  Active Cells: {stats['active_cells']:,}")
        self.log(f"  Density: {stats['density']:.2f}%")
        self.log(f"  Entropy: {stats['entropy']:.3f}")
        self.log(f"  Unique States: {stats['unique_states']} (min={stats['grid_min']}, max={stats['grid_max']})")
        self.log(f"  State Counts:")
        for state, count in sorted(stats['state_counts'].items()):
            self.log(f"    State {state}: {count:,} cells ({count/stats['total_cells']*100:.2f}%)")

    def visualize_evolution(self, automaton, colormap, num_steps=20, name="automaton"):
        """Create visualization showing evolution over time"""
        self.log(f"\n{'='*60}")
        self.log(f"Testing {name}")
        self.log(f"{'='*60}")

        # Create figure with multiple subplots showing evolution
        fig, axes = plt.subplots(2, 5, figsize=(20, 8))
        fig.suptitle(f'{name} Evolution: Generations 0-{num_steps*2}',
                     fontsize=14, fontweight='bold')
        axes = axes.flatten()

        # Store initial state
        initial_stats = self.analyze_grid(automaton, f"{name} - Initial State")
        self.print_stats(initial_stats)

        # Capture states at different generations
        states_to_capture = [0, 2, 4, 6, 8, 10, 15, 20, 30, 50]
        captured_states = []

        for i in range(max(states_to_capture) + 1):
            if i in states_to_capture:
                # Capture current state
                state_data = {
                    'generation': automaton.generation,
                    'grid': automaton.grid.copy(),
                    'stats': self.analyze_grid(automaton, f"{name} - Gen {automaton.generation}")
                }
                captured_states.append(state_data)

                # Print stats for key generations
                if i in [0, 10, 20, 30, 50]:
                    self.print_stats(state_data['stats'])

            # Step the automaton
            if i < max(states_to_capture):
                automaton.step()

        # Plot captured states
        for idx, state_data in enumerate(captured_states):
            if idx < len(axes):
                ax = axes[idx]
                ax.imshow(state_data['grid'], cmap=colormap,
                         interpolation='nearest', vmin=0,
                         vmax=automaton.num_states-1)
                ax.set_title(f"Gen {state_data['generation']}", fontsize=10)
                ax.axis('off')

        # Hide unused subplots
        for idx in range(len(captured_states), len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()

        # Save figure
        filename = f"{self.output_dir}/{name.replace(' ', '_')}_{self.timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()

        self.log(f"\n  Visualization saved: {filename}")

        return captured_states

    def show_grid_details(self, automaton, name="automaton"):
        """Show detailed grid information for debugging"""
        self.log(f"\n{'-'*60}")
        self.log(f"Grid Details for {name}")
        self.log(f"{'-'*60}")

        grid = automaton.grid

        # Show a small section of the grid (center 10x10)
        h, w = grid.shape
        center_y, center_x = h // 2, w // 2
        section = grid[max(0, center_y-5):center_y+5, max(0, center_x-5):center_x+5]

        self.log(f"\nCenter 10x10 section of grid:")
        self.log(f"(showing states, 0=empty)")
        for row in section:
            self.log("  " + " ".join(f"{int(val):2d}" for val in row))

        # Check for patterns
        self.log(f"\nPattern Analysis:")

        # Check if grid is all zeros
        if np.all(grid == 0):
            self.log("  ⚠️  WARNING: Grid is entirely empty (all zeros)!")

        # Check if grid has stuck in one state
        if len(np.unique(grid)) == 1:
            self.log(f"  ⚠️  WARNING: Grid has only one state: {np.unique(grid)[0]}")

        # Check if pattern is static
        old_grid = grid.copy()
        automaton.step()
        if np.array_equal(old_grid, automaton.grid):
            self.log("  ⚠️  WARNING: Grid is static (no changes after step)!")
            automaton.grid = old_grid  # Restore
        else:
            # Count changed cells
            changed = np.sum(old_grid != automaton.grid)
            self.log(f"  ✓ Grid is active: {changed} cells changed in one step")
            automaton.grid = old_grid  # Restore
            automaton.generation -= 1

    def test_automaton(self, automaton_class, colormap, name, **kwargs):
        """Test a specific automaton type"""
        self.log(f"\n\n{'#'*60}")
        self.log(f"# Testing: {name}")
        self.log(f"{'#'*60}")

        try:
            # Create automaton
            automaton = automaton_class(**kwargs)
            self.log(f"\n✓ {name} created successfully")
            self.log(f"  Class: {automaton.__class__.__name__}")
            self.log(f"  Grid size: {automaton.grid.shape}")
            self.log(f"  Number of states: {automaton.num_states}")

            # Show initial grid details
            self.show_grid_details(automaton, name)

            # Visualize evolution
            captured_states = self.visualize_evolution(automaton, colormap, name=name)

            # Analyze behavior
            self.log(f"\nBehavior Analysis:")

            # Check if pattern is growing
            densities = [s['stats']['density'] for s in captured_states]
            if len(densities) > 1:
                density_change = densities[-1] - densities[0]
                if density_change > 5:
                    self.log(f"  ✓ Pattern is GROWING (+{density_change:.2f}% density)")
                elif density_change < -5:
                    self.log(f"  ⚠️  Pattern is SHRINKING ({density_change:.2f}% density)")
                else:
                    self.log(f"  ~ Pattern is STABLE ({density_change:.2f}% density change)")

            # Check entropy change
            entropies = [s['stats']['entropy'] for s in captured_states]
            if len(entropies) > 1:
                entropy_change = entropies[-1] - entropies[0]
                self.log(f"  Complexity change: {entropy_change:+.3f} (entropy)")

            # Check if states are being used
            final_states = captured_states[-1]['stats']['state_counts']
            unused_states = automaton.num_states - len(final_states)
            if unused_states > 0:
                self.log(f"  Note: {unused_states} states never used")

            self.log(f"\n✓ {name} test completed")
            return True

        except Exception as e:
            self.log(f"\n✗ ERROR testing {name}:")
            self.log(f"  {type(e).__name__}: {str(e)}")
            import traceback
            self.log("\nTraceback:")
            for line in traceback.format_exc().split('\n'):
                self.log(f"  {line}")
            return False

    def run_all_tests(self):
        """Run tests on all automaton types"""
        self.log("="*60)
        self.log("AUTOMATON DIAGNOSTIC TEST SUITE")
        self.log("="*60)
        self.log(f"Timestamp: {self.timestamp}")
        self.log(f"Output directory: {self.output_dir}")

        results = {}

        # Test 1: Langton's Loop
        results['LangtonLoop'] = self.test_automaton(
            LangtonLoop,
            ListedColormap(['black', 'white', 'red', 'blue', 'yellow']),
            "Langton's Loop",
            width=100,
            height=100
        )

        # Test 2: Evolving Loop
        results['EvolvingLoop'] = self.test_automaton(
            EvolvingLoop,
            ListedColormap(['black', 'white', 'red', 'orange', 'yellow',
                           'green', 'blue', 'purple']),
            "Evolving Loop",
            width=100,
            height=100,
            mutation_rate=0.001
        )

        # Test 3: Von Neumann Constructor
        results['VonNeumannConstructor'] = self.test_automaton(
            VonNeumannConstructor,
            ListedColormap(['black', 'gray', 'red', 'orange', 'yellow',
                           'green', 'blue', 'cyan', 'magenta', 'white']),
            "Von Neumann Constructor",
            width=120,
            height=120
        )

        # Test 4: Wire World
        results['WireWorld'] = self.test_automaton(
            WireWorld,
            ListedColormap(['black', 'yellow', 'blue', 'red']),
            "Wire World",
            width=100,
            height=100
        )

        # Generate summary
        self.generate_summary(results)

        # Save report
        self.save_report()

        return results

    def generate_summary(self, results):
        """Generate summary of all tests"""
        self.log("\n\n" + "="*60)
        self.log("DIAGNOSTIC SUMMARY")
        self.log("="*60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        self.log(f"\nTests Passed: {passed}/{total}")
        self.log("\nIndividual Results:")
        for name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            self.log(f"  {status}: {name}")

        self.log(f"\nOutput Location: {self.output_dir}")
        self.log(f"  - Visualizations: *_{self.timestamp}.png")
        self.log(f"  - Text Report: diagnostic_report_{self.timestamp}.txt")

    def save_report(self):
        """Save text report to file"""
        report_file = f"{self.output_dir}/diagnostic_report_{self.timestamp}.txt"

        with open(report_file, 'w') as f:
            f.write('\n'.join(self.report))

        self.log(f"\n✓ Report saved: {report_file}")


def main():
    """Main entry point"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "Automaton Diagnostic Tool" + " "*23 + "║")
    print("╚" + "="*58 + "╝\n")

    print("This tool will:")
    print("  1. Test all automaton types")
    print("  2. Generate visual evolution diagrams")
    print("  3. Analyze behavior and statistics")
    print("  4. Create detailed text report")
    print("  5. Identify any issues\n")

    print("Output will be saved to: ./diagnostics/")
    print("-"*60 + "\n")

    # Run diagnostics
    diagnostic = AutomatonDiagnostic()
    results = diagnostic.run_all_tests()

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE!")
    print("="*60)
    print("\nPlease review:")
    print("  1. Visual outputs in diagnostics folder")
    print("  2. Text report for detailed information")
    print("  3. Console output above")
    print("\nShare the report and images to help debug issues.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
