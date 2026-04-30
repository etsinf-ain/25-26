"""
build_random_city.py
Generates a structured grid with main avenues (fast, multi-lane) and secondary streets.
Includes traffic lights on avenue intersections to evaluate urban routing logic.
"""
import xml.etree.ElementTree as ET
import subprocess
import random
import sys
import os

def create_random_city(seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(42) # Default value
    grid_size = 5
    length = 150
    
    # Randomly choose 2 horizontal streets and 2 vertical ones to be continuous "Avenues"
    avenue_rows = random.sample(range(grid_size), 2)
    avenue_cols = random.sample(range(grid_size), 2)
    
    nodes = ET.Element('nodes')
    for y in range(grid_size):
        for x in range(grid_size):
            # If the node touches any avenue, we put a traffic light. Otherwise, basic priority.
            node_type = "priority"
            if y in avenue_rows or x in avenue_cols:
                node_type = "traffic_light"
                
            ET.SubElement(nodes, 'node', {'id': f"n_{x}_{y}", 'x': str(x*length), 'y': str(y*length), 'type': node_type})
            
    tree = ET.ElementTree(nodes)
    tree.write("scenarios/random/random.nod.xml")
    
    edges = ET.Element('edges')
    
    def add_edge(u, v, is_avenue):
        if is_avenue:
            # Avenues are two-way and have 2 high-capacity lanes
            ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
            ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
        else:
            # Secondary streets have alternating one-way and 1 low-capacity lane
            u_x, u_y = int(u.split('_')[1]), int(u.split('_')[2])
            v_x, v_y = int(v.split('_')[1]), int(v.split('_')[2])
            
            if u_x == v_x: # vertical street
                go_north = (u_x % 2 == 0) # Even columns go north, odd columns go south
                if (u_y < v_y and go_north) or (u_y > v_y and not go_north):
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
            elif u_y == v_y: # horizontal street
                go_east = (u_y % 2 == 0) # Even rows go east, odd rows go west
                if (u_x < v_x and go_east) or (u_x > v_x and not go_east):
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})

    # Generate all horizontal segments
    for y in range(grid_size):
        is_avenue = (y in avenue_rows)
        for x in range(grid_size - 1):
            add_edge(f"n_{x}_{y}", f"n_{x+1}_{y}", is_avenue)
            if not is_avenue:
                add_edge(f"n_{x+1}_{y}", f"n_{x}_{y}", is_avenue)

    # Generate all vertical segments
    for x in range(grid_size):
        is_avenue = (x in avenue_cols)
        for y in range(grid_size - 1):
            add_edge(f"n_{x}_{y}", f"n_{x}_{y+1}", is_avenue)
            if not is_avenue:
                add_edge(f"n_{x}_{y+1}", f"n_{x}_{y}", is_avenue)

    tree = ET.ElementTree(edges)
    tree.write("scenarios/random/random.edg.xml")
    
    print("Compiling random network...")
    subprocess.run([
        "netconvert", 
        "--node-files", "scenarios/random/random.nod.xml", 
        "--edge-files", "scenarios/random/random.edg.xml", 
        "--output-file", "scenarios/random/random.net.xml",
        "--no-turnarounds", "true"
    ])
    
    print("Generating random traffic...")
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("SUMO_HOME environment variable not set, and couldn't locate SUMO tools directory.")
        
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    cmd_rt = [
        sys.executable, script_path,
        "-n", "scenarios/random/random.net.xml",
        "-e", "250", "-p", "1.2",
        "-o", "scenarios/random/random.trips.xml",
        "-r", "scenarios/random/random.rou.xml"
    ]
    if seed is not None:
        cmd_rt.extend(["--seed", str(seed)])
        
    subprocess.run(cmd_rt)
    print("Generation complete!")

if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    create_random_city(seed)
