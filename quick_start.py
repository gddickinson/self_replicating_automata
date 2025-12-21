#!/usr/bin/env python3
"""
Quick Start - Self-Replicating Automata
========================================

The simplest way to run the simulator with proper display refresh.
Just run this script and everything should work!
"""

import sys
import os

def main():
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 5 + "Von Neumann Self-Replicating Automata" + " " * 14 + "║")
    print("║" + " " * 20 + "Quick Start" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    print("This script will launch the interactive GUI with proper")
    print("display refresh handling.")
    print()
    print("Controls once launched:")
    print("  • Radio buttons: Select automaton type")
    print("  • ▶ Play: Start simulation")
    print("  • ⏸ Pause: Pause simulation")  
    print("  • ⏭ Step: Advance one generation")
    print("  • 🔄 Reset: Create new automaton")
    print("  • Sliders: Adjust speed, grid size, mutation rate")
    print("  • 📸 Save: Save current snapshot")
    print()
    print("Statistics panel shows:")
    print("  • Generation count")
    print("  • Active cells")
    print("  • Pattern density")
    print("  • Complexity measure")
    print()
    print("-" * 60)
    
    # Check if the GUI module exists
    try:
        from automata_interactive_gui import InteractiveAutomatonGUI
        print("✓ Interactive GUI module loaded successfully")
    except ImportError as e:
        print(f"✗ Error loading GUI module: {e}")
        print("\nMake sure you have:")
        print("  1. automata_interactive_gui.py in the same directory")
        print("  2. self_replicating_automata.py in the same directory")
        print("  3. matplotlib and numpy installed")
        return 1
    
    print("✓ All dependencies available")
    print()
    print("Launching GUI...")
    print("-" * 60)
    print()
    
    try:
        # Create and show GUI
        gui = InteractiveAutomatonGUI()
        gui.show()
        
        print("\n" + "=" * 60)
        print("GUI closed. Thanks for using the simulator!")
        print("=" * 60)
        return 0
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user (Ctrl+C)")
        return 0
    except Exception as e:
        print(f"\n✗ Error running GUI: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that matplotlib backend supports interactive display")
        print("  2. Try running: python -c 'import matplotlib; print(matplotlib.get_backend())'")
        print("  3. If backend is 'agg', try setting a different one:")
        print("     export MPLBACKEND=Qt5Agg")
        print("  4. Run the diagnostic tool: python display_diagnostic.py")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
