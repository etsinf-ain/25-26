import xml.etree.ElementTree as ET
import subprocess
import random
import sys
import os

def create_mixed_city(seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(42)
    
    grid_size = 5
    length = 150
    
    # 0. Definir avenidas (igual que en random)
    avenue_rows = random.sample(range(grid_size), 2)
    avenue_cols = random.sample(range(grid_size), 2)
    
    # 1. NODOS
    nodes = ET.Element('nodes')
    for y in range(grid_size):
        for x in range(grid_size):
            node_type = "traffic_light" if (y in avenue_rows or x in avenue_cols) else "priority"
            ET.SubElement(nodes, 'node', {'id': f"n_{x}_{y}", 'x': str(x*length), 'y': str(y*length), 'type': node_type})
    ET.ElementTree(nodes).write("scenarios/mixed/mixed.nod.xml")
    
    # 2. EDGES (Logica de avenidas y calles de un solo sentido)
    edges = ET.Element('edges')
    for y in range(grid_size):
        is_row_avenue = (y in avenue_rows)
        for x in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x+1}_{y}"
            if is_row_avenue:
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
            else:
                if y % 2 == 0: # Filas pares hacia el este, impares hacia el oeste
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
                else:
                    ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})

    for x in range(grid_size):
        is_col_avenue = (x in avenue_cols)
        for y in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x}_{y+1}"
            if is_col_avenue:
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "2", 'speed': "13.89", 'priority': "3"})
            else:
                if x % 2 == 0: # Columnas pares hacia el norte, impares hacia el sur
                    ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
                else:
                    ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1"})
    ET.ElementTree(edges).write("scenarios/mixed/mixed.edg.xml")
    
    # 3. COMPILAR RED
    subprocess.run(["netconvert", "--node-files", "scenarios/mixed/mixed.nod.xml", "--edge-files", "scenarios/mixed/mixed.edg.xml", "--output-file", "scenarios/mixed/mixed.net.xml", "--no-turnarounds", "true"])
    
    # 4. TRAFICO
    sumo_home = os.environ.get("SUMO_HOME")
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    subprocess.run([sys.executable, script_path, "-n", "scenarios/mixed/mixed.net.xml", "-e", "200", "-p", "1.2", "-o", "scenarios/mixed/mixed.trips.xml", "-r", "scenarios/mixed/mixed.rou.xml"])

    # 5. ASIGNAR TIPOS
    tree = ET.parse("scenarios/mixed/mixed.rou.xml")
    for veh in tree.getroot().findall('vehicle'):
        veh.set('type', 'intelligent' if random.random() < 0.3 else 'normal')
    tree.write("scenarios/mixed/mixed.rou.xml")

    # 6. CFG
    cfg = """<configuration><input><net-file value="mixed.net.xml"/><route-files value="mixed.rou.xml"/><additional-files value="vtypes.add.xml"/></input></configuration>"""
    with open("scenarios/mixed/mixed.sumocfg", "w") as f: f.write(cfg)
    print("Escenario MIXED generado (clon de random) en scenarios/mixed/")

if __name__ == "__main__":
    create_mixed_city(int(sys.argv[1]) if len(sys.argv) > 1 else None)
