"""
build_autonomous_city.py
Generates a 5x5 grid network where all nodes are priority intersections (no traffic lights).
Optimized for testing collaborative driving and autonomous intersection management.
"""
import xml.etree.ElementTree as ET
import subprocess
import random
import sys
import os

def create_autonomous_city(seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(42) # Same default value as logical_city
    grid_size = 5
    length = 150
    
    # Randomly choose 2 main horizontal streets and 2 main vertical ones
    main_rows = random.sample(range(grid_size), 2)
    main_cols = random.sample(range(grid_size), 2)
    
    nodes = ET.Element('nodes')
    for y in range(grid_size):
        for x in range(grid_size):
            # No traffic lights in the autonomous city, all nodes are priority intersections
            ET.SubElement(nodes, 'node', {'id': f"n_{x}_{y}", 'x': str(x*length), 'y': str(y*length), 'type': "priority"})
            
    tree = ET.ElementTree(nodes)
    tree.write("scenarios/autonomous/auto.nod.xml")
    
    edges = ET.Element('edges')
    
    def add_edge(u, v, is_main):
        if is_main:
            # Main streets are two-way, but ONLY 1 lane per direction
            ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "13.89", 'priority': "2"})
            ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "13.89", 'priority': "2"})
        else:
            # Secondary streets have alternating one-way and 1 lane
            u_x, u_y = int(u.split('_')[1]), int(u.split('_')[2])
            v_x, v_y = int(v.split('_')[1]), int(v.split('_')[2])
            
            if u_x == v_x: # vertical street
                go_north = (u_x % 2 == 0)
                if (u_y < v_y and go_north) or (u_y > v_y and not go_north):
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
            elif u_y == v_y: # horizontal
                go_east = (u_y % 2 == 0)
                if (u_x < v_x and go_east) or (u_x > v_x and not go_east):
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})

    # Generate all horizontal segments
    for y in range(grid_size):
        is_main = (y in main_rows)
        for x in range(grid_size - 1):
            add_edge(f"n_{x}_{y}", f"n_{x+1}_{y}", is_main)
            if not is_main: add_edge(f"n_{x+1}_{y}", f"n_{x}_{y}", False)

    # Generate all vertical segments
    for x in range(grid_size):
        is_main = (x in main_cols)
        for y in range(grid_size - 1):
            add_edge(f"n_{x}_{y}", f"n_{x}_{y+1}", is_main)
            if not is_main: add_edge(f"n_{x}_{y+1}", f"n_{x}_{y}", False)

    tree = ET.ElementTree(edges)
    tree.write("scenarios/autonomous/auto.edg.xml")
    
    print("Compiling autonomous network...")
    subprocess.run([
        "netconvert", 
        "--node-files", "scenarios/autonomous/auto.nod.xml", 
        "--edge-files", "scenarios/autonomous/auto.edg.xml", 
        "--output-file", "scenarios/autonomous/autonomous.net.xml",
        "--no-turnarounds", "true"
    ])
    
    print("Generating autonomous traffic...")
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("La variable de entorno SUMO_HOME no está definida. Por favor, configúrala para apuntar a tu instalación de SUMO.")
        
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    cmd_rt = [
        sys.executable, script_path,
        "-n", "scenarios/autonomous/autonomous.net.xml",
        "-e", "100", "-p", "2.0",  # Fewer cars to not collapse SPADE
        "-o", "scenarios/autonomous/autonomous.trips.xml",
        "-r", "scenarios/autonomous/autonomous.rou.xml"
    ]
    if seed is not None:
        cmd_rt.extend(["--seed", str(seed)])
        
    subprocess.run(cmd_rt)
    
    cfg_content = """<configuration>
    <input>
        <net-file value="autonomous.net.xml"/>
        <route-files value="autonomous.rou.xml"/>
    </input>
</configuration>"""
    with open("scenarios/autonomous/autonomous.sumocfg", "w") as f:
        f.write(cfg_content)
        
    print("Generation complete! (scenarios/autonomous/autonomous.sumocfg)")

if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    create_autonomous_city(seed)
