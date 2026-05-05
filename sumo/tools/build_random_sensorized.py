import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import random

def build_random_sensorized(seed=None):
    if seed is not None: random.seed(seed)
    else: random.seed(42)
    
    grid_size = 5
    length = 150
    path = "scenarios/random_sensorized"
    if not os.path.exists(path): os.makedirs(path)

    # 1. NODOS
    avenue_rows = random.sample(range(grid_size), 2)
    avenue_cols = random.sample(range(grid_size), 2)
    
    nodes = ET.Element('nodes')
    for y in range(grid_size):
        for x in range(grid_size):
            node_type = "traffic_light" if (y in avenue_rows or x in avenue_cols) else "priority"
            ET.SubElement(nodes, 'node', {'id': f"n_{x}_{y}", 'x': str(x*length), 'y': str(y*length), 'type': node_type})
    ET.ElementTree(nodes).write(f"{path}/rs.nod.xml")
    
    # 2. EDGES (Horizontales y Verticales)
    edges = ET.Element('edges')
    # Horizontales
    for y in range(grid_size):
        is_avenue = (y in avenue_rows)
        for x in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x+1}_{y}"
            if is_avenue:
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
            else:
                if y % 2 == 0: ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
                else: ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
    # Verticales
    for x in range(grid_size):
        is_avenue = (x in avenue_cols)
        for y in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x}_{y+1}"
            if is_avenue:
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
            else:
                if x % 2 == 0: ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
                else: ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
    ET.ElementTree(edges).write(f"{path}/rs.edg.xml")

    # 3. COMPILAR RED
    subprocess.run(["netconvert", "--node-files", f"{path}/rs.nod.xml", "--edge-files", f"{path}/rs.edg.xml", "--output-file", f"{path}/rs.net.xml", "--no-turnarounds", "true"])
    
    # 4. TRAFICO
    sumo_home = os.environ.get("SUMO_HOME")
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    subprocess.run([sys.executable, script_path, "-n", f"{path}/rs.net.xml", "-e", "150", "-o", f"{path}/rs.trips.xml", "-r", f"{path}/rs.rou.xml"])

    # 5. GENERAR DETECTORES
    detector_tool = os.path.join(sumo_home, "tools", "output", "generateTLSE2Detectors.py")
    subprocess.run([sys.executable, detector_tool, "-n", f"{path}/rs.net.xml", "-l", "50", "-d", "0.1", "-o", f"{path}/rs.add.xml"])
    
    # 6. CONFIGURACION
    cfg = f"""<configuration><input><net-file value="rs.net.xml"/><route-files value="rs.rou.xml"/><additional-files value="rs.add.xml"/></input></configuration>"""
    with open(f"{path}/random_sensorized.sumocfg", "w") as f: f.write(cfg)
    print(f"Escenario sensorizado completo generado en {path}")

if __name__ == "__main__":
    build_random_sensorized(int(sys.argv[1]) if len(sys.argv) > 1 else None)
