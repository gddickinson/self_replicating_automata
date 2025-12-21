"""
Display Refresh Diagnostic Tool
================================

This script helps diagnose and fix matplotlib display refresh issues.
It tests different backends and animation settings to find what works best.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys

def check_backend():
    """Check current matplotlib backend"""
    print("=" * 60)
    print("Matplotlib Configuration")
    print("=" * 60)
    print(f"Backend: {matplotlib.get_backend()}")
    print(f"Matplotlib version: {matplotlib.__version__}")
    print(f"Interactive mode: {matplotlib.is_interactive()}")
    print()

def test_basic_animation():
    """Test basic animation with different settings"""
    print("=" * 60)
    print("Testing Animation Refresh")
    print("=" * 60)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Animation Refresh Test - Watch for Updates')
    
    # Test data
    data1 = np.random.rand(50, 50)
    data2 = np.random.rand(50, 50)
    
    im1 = ax1.imshow(data1, cmap='viridis')
    ax1.set_title('With blit=True (may not refresh)')
    
    im2 = ax2.imshow(data2, cmap='plasma')
    ax2.set_title('With blit=False (should refresh)')
    
    counter = [0]
    
    def update(frame):
        counter[0] += 1
        
        # Update data
        new_data1 = np.random.rand(50, 50)
        new_data2 = np.random.rand(50, 50)
        
        im1.set_data(new_data1)
        ax1.set_title(f'With blit=True - Frame {counter[0]}')
        
        im2.set_data(new_data2)
        ax2.set_title(f'With blit=False - Frame {counter[0]}')
        
        return [im1, im2]
    
    from matplotlib.animation import FuncAnimation
    
    # Create two animations with different settings
    anim = FuncAnimation(fig, update, interval=200, blit=False, 
                        cache_frame_data=False)
    
    print("\nAnimation started. If the display doesn't update automatically,")
    print("this confirms the refresh issue.")
    print("\nBoth panels should update every 200ms.")
    print("If only updating on window resize, the issue is confirmed.")
    print("\nClose the window to continue...\n")
    
    try:
        plt.show()
        print("✓ Test completed")
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")
    
def test_recommended_settings():
    """Test with recommended settings for reliable refresh"""
    print("\n" + "=" * 60)
    print("Testing Recommended Settings")
    print("=" * 60)
    
    # Use recommended settings
    plt.rcParams['animation.html'] = 'jshtml'
    
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.suptitle('Recommended Settings Test')
    
    data = np.random.rand(100, 100)
    im = ax.imshow(data, cmap='viridis', interpolation='nearest')
    ax.axis('off')
    
    counter = [0]
    
    def update(frame):
        counter[0] += 1
        new_data = np.random.rand(100, 100)
        im.set_data(new_data)
        ax.set_title(f'Frame {counter[0]} - Should update smoothly')
        
        # Force canvas update
        fig.canvas.draw_idle()
        
        return [im]
    
    from matplotlib.animation import FuncAnimation
    
    anim = FuncAnimation(
        fig, 
        update, 
        interval=100,
        blit=False,  # Critical for reliable refresh
        cache_frame_data=False,  # Prevent caching issues
        repeat=True
    )
    
    print("\nThis test uses the RECOMMENDED settings:")
    print("  - blit=False")
    print("  - cache_frame_data=False")
    print("  - fig.canvas.draw_idle() in update function")
    print("\nThe display should update smoothly every 100ms.")
    print("Close the window when satisfied...\n")
    
    try:
        plt.show()
        print("✓ Recommended settings test completed")
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")

def test_interactive_mode():
    """Test interactive plotting mode"""
    print("\n" + "=" * 60)
    print("Testing Interactive Mode")
    print("=" * 60)
    
    plt.ion()  # Turn on interactive mode
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title('Interactive Mode Test')
    
    data = np.random.rand(100, 100)
    im = ax.imshow(data, cmap='viridis', interpolation='nearest')
    ax.axis('off')
    
    plt.show(block=False)
    plt.pause(0.1)
    
    print("\nUpdating plot 20 times with plt.pause()...")
    print("Each update should be visible immediately.\n")
    
    for i in range(20):
        new_data = np.random.rand(100, 100)
        im.set_data(new_data)
        ax.set_title(f'Interactive Mode - Update {i+1}/20')
        
        # Update the figure
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        plt.pause(0.2)
        
        print(f"  Update {i+1}/20", end='\r')
    
    print("\n\n✓ Interactive mode test completed")
    print("Close the window to continue...")
    
    plt.ioff()  # Turn off interactive mode
    plt.show()

def generate_report():
    """Generate diagnostic report"""
    print("\n" + "=" * 60)
    print("Diagnostic Report")
    print("=" * 60)
    
    print("\n📊 SUMMARY:")
    print("-" * 60)
    
    backend = matplotlib.get_backend()
    
    print(f"\nCurrent backend: {backend}")
    
    if backend == 'agg':
        print("⚠️  WARNING: 'agg' backend is non-interactive")
        print("   Recommendation: Use 'Qt5Agg', 'TkAgg', or 'GTK3Agg'")
        print("   Set with: matplotlib.use('Qt5Agg') before importing pyplot")
    else:
        print("✓  Backend should support interactive display")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 60)
    print("\n1. For BEST results, use the Interactive Matplotlib GUI:")
    print("   python automata_interactive_gui.py")
    print("\n2. Key settings to use:")
    print("   - blit=False in FuncAnimation")
    print("   - cache_frame_data=False in FuncAnimation")
    print("   - fig.canvas.draw_idle() to update display")
    print("\n3. If issues persist, try different backend:")
    print("   matplotlib.use('Qt5Agg')  # or 'TkAgg', 'GTK3Agg'")
    print("\n4. For tkinter GUI, ensure python3-tk is installed:")
    print("   sudo apt-get install python3-tk")
    
    print("\n" + "=" * 60)

def main():
    """Run all diagnostic tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Display Refresh Diagnostic Tool" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Check configuration
    check_backend()
    
    print("\nThis tool will run several tests to diagnose display refresh issues.")
    print("Press Ctrl+C at any time to skip a test.\n")
    
    try:
        input("Press Enter to start basic animation test...")
        test_basic_animation()
        
        input("\nPress Enter to test recommended settings...")
        test_recommended_settings()
        
        input("\nPress Enter to test interactive mode...")
        test_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    
    # Generate final report
    generate_report()
    
    print("\n✓ Diagnostic complete!\n")

if __name__ == "__main__":
    main()
