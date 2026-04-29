"""
show_map.py
Parses a SUMO network file (.net.xml) and renders a static PNG overview of the streets.
Saves the rendered image inside the 'assets/' directory.
"""
import sumolib
import matplotlib.pyplot as plt
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/show_map.py <file.net.xml>")
        return

    net_file = sys.argv[1]
    print(f"Reading network: {net_file}...")
    
    try:
        net = sumolib.net.readNet(net_file)
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Draw each lane
        for edge in net.getEdges():
            for lane in edge.getLanes():
                shape = lane.getShape()
                x, y = zip(*shape)
                ax.plot(x, y, color="gray", linewidth=1)
        
        ax.set_aspect("equal")
        ax.set_title(f"Map: {os.path.basename(net_file)}")
        ax.axis("off")
        
        os.makedirs("assets", exist_ok=True)
        # Extract name without extensions
        base_name = os.path.basename(net_file).replace(".net.xml", "").replace(".xml", "")
        output = os.path.join("assets", f"{base_name}.png")
        
        plt.savefig(output, dpi=150, bbox_inches='tight')
        print(f"Image saved as {output}")
        # plt.show() # Disabled for non-GUI environments
        
    except Exception as e:
        print(f"Error reading the map: {e}")

if __name__ == "__main__":
    main()
