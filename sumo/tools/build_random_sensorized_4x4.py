import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import random

"""
Generador de escenario basado en random_sensorized pero:
- rejilla 4x4
- avenidas (calles anchas) con 2 carriles (si hubiera 4 se reducen a 2)
- detectores: para calles de unea sola dirección que llegan a un semáforo, usar e1output.xml
- mayor flujo de vehículos (periodo menor)
Genera el escenario en scenarios/random_sensorized_4x4
"""

def build_random_sensorized_4x4(seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(42)

    grid_size = 4
    length = 150
    path = "scenarios/random_sensorized_4x4"
    if not os.path.exists(path):
        os.makedirs(path)

    # NODOS
    avenue_rows = random.sample(range(grid_size), 2)
    avenue_cols = random.sample(range(grid_size), 2)

    nodes = ET.Element('nodes')
    for y in range(grid_size):
        for x in range(grid_size):
            node_type = "traffic_light" if (y in avenue_rows or x in avenue_cols) else "priority"
            ET.SubElement(nodes, 'node', {'id': f"n_{x}_{y}", 'x': str(x*length), 'y': str(y*length), 'type': node_type})
    ET.ElementTree(nodes).write(f"{path}/rs.nod.xml")

    # EDGES
    edges = ET.Element('edges')
    edge_list = []  # Guardar referencias para post-procesamiento
    
    # Horizontales - direcciones al azar
    for y in range(grid_size):
        is_avenue = (y in avenue_rows)
        for x in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x+1}_{y}"
            if is_avenue:
                # avenidas con 1 carril por dirección (bidireccionales: 2 edges, 1 carril cada uno)
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "13.89", 'priority': "3"})
                edge_list.append((f"E_{u}_{v}", u, v, True))
                edge_list.append((f"E_{v}_{u}", v, u, True))
            else:
                # calles unidireccionales - dirección al azar
                direction = random.choice([True, False])  # True: u→v, False: v→u
                if direction:
                    edge_elem = ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((f"E_{u}_{v}", u, v, False))
                else:
                    edge_elem = ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((f"E_{v}_{u}", v, u, False))
    
    # Verticales - direcciones al azar
    for x in range(grid_size):
        is_avenue = (x in avenue_cols)
        for y in range(grid_size - 1):
            u, v = f"n_{x}_{y}", f"n_{x}_{y+1}"
            if is_avenue:
                # avenidas con 1 carril por dirección (bidireccionales: 2 edges, 1 carril cada uno)
                ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "13.89", 'priority': "3"})
                ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "13.89", 'priority': "3"})
                edge_list.append((f"E_{u}_{v}", u, v, True))
                edge_list.append((f"E_{v}_{u}", v, u, True))
            else:
                # calles unidireccionales - dirección al azar
                direction = random.choice([True, False])  # True: u→v, False: v→u
                if direction:
                    edge_elem = ET.SubElement(edges, 'edge', {'id': f"E_{u}_{v}", 'from': u, 'to': v, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((f"E_{u}_{v}", u, v, False))
                else:
                    edge_elem = ET.SubElement(edges, 'edge', {'id': f"E_{v}_{u}", 'from': v, 'to': u, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((f"E_{v}_{u}", v, u, False))
    
    # Post-procesamiento: detectar nodos con todas entradas o todas salidas en calles no-avenida
    # Construir grafo de entrada/salida para nodos (SOLO calles unidireccionales)
    incoming = {f"n_{x}_{y}": [] for x in range(grid_size) for y in range(grid_size)}
    outgoing = {f"n_{x}_{y}": [] for x in range(grid_size) for y in range(grid_size)}
    
    # Contar también si un nodo tiene conexiones de avenida (bidireccionales)
    avenue_connected = {f"n_{x}_{y}": 0 for x in range(grid_size) for y in range(grid_size)}
    
    for edge_id, from_node, to_node, is_avenue_edge in edge_list:
        if is_avenue_edge:
            # Registrar la conexión de avenida en ambos nodos
            avenue_connected[from_node] += 1
            avenue_connected[to_node] += 1
        else:
            # Solo contar calles unidireccionales en los contadores de entrada/salida
            outgoing[from_node].append((edge_id, to_node))
            incoming[to_node].append((edge_id, from_node))
    
    # Buscar nodos problemáticos: que tengan SOLO calles unidireccionales 
    # y todas sean entradas O todas sean salidas. No tocar nodos que tengan
    # alguna conexión de avenida (bidireccional).
    diagonals_added = []
    for node_id in incoming:
        # Omitir nodos que estén conectados a una avenida (no deben modificarse)
        if avenue_connected.get(node_id, 0) > 0:
            continue

        x, y = int(node_id.split('_')[1]), int(node_id.split('_')[2])
        in_count = len(incoming[node_id])
        out_count = len(outgoing[node_id])
        
        # Procesar solo si el nodo tiene conexiones unidireccionales y todas son entradas O todas son salidas
        if in_count > 0 and out_count == 0:  # Solo entradas en unidireccionales
            # Crear una salida hacia un vecino
            candidates = []
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    neighbor = f"n_{nx}_{ny}"
                    candidates.append(neighbor)
            
            if candidates:
                target = random.choice(candidates)
                diagonal_id = f"E_{node_id}_{target}"
                
                # Evitar crear diagonal si ya existe cualquier arista entre los nodos
                existing_ids = {eid for eid, _, _, _ in edge_list}
                if diagonal_id not in existing_ids:
                    ET.SubElement(edges, 'edge', {'id': diagonal_id, 'from': node_id, 'to': target, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((diagonal_id, node_id, target, False))
                    diagonals_added.append((node_id, diagonal_id))
        
        elif out_count > 0 and in_count == 0:  # Solo salidas en unidireccionales
            # Crear una entrada desde un vecino
            candidates = []
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    neighbor = f"n_{nx}_{ny}"
                    candidates.append(neighbor)
            
            if candidates:
                target = random.choice(candidates)
                diagonal_id = f"E_{target}_{node_id}"
                
                # Evitar crear diagonal si ya existe cualquier arista entre los nodos
                existing_ids = {eid for eid, _, _, _ in edge_list}
                if diagonal_id not in existing_ids:
                    ET.SubElement(edges, 'edge', {'id': diagonal_id, 'from': target, 'to': node_id, 'numLanes': "1", 'speed': "8.33", 'priority': "1", 'oneway': "true"})
                    edge_list.append((diagonal_id, target, node_id, False))
                    diagonals_added.append((node_id, diagonal_id))

    ET.ElementTree(edges).write(f"{path}/rs.edg.xml")

    # Compilar red
    subprocess.run(["netconvert", "--node-files", f"{path}/rs.nod.xml", "--edge-files", f"{path}/rs.edg.xml", "--output-file", f"{path}/rs.net.xml", "--no-turnarounds", "true"]) 

    # Trafico: aumentar flujo reduciendo periodo
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        print("SUMO_HOME no definido; asegúrate de tener SUMO instalado y SUMO_HOME en el entorno")
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py") if sumo_home else "randomTrips.py"
    # periodo 0.5 => más vehículos
    subprocess.run([sys.executable, script_path, "-n", f"{path}/rs.net.xml", "-e", "150", "-o", f"{path}/rs.trips.xml", "-r", f"{path}/rs.rou.xml", "-p", "0.5"])
    
    # Post-procesar rou.xml para añadir tipo de vehículo con velocidades variables
    rou_path = f"{path}/rs.rou.xml"
    try:
        rou_tree = ET.parse(rou_path)
        rou_root = rou_tree.getroot()
        
        # Crear elemento root si no existe
        if rou_root.tag != 'routes':
            rou_root = ET.Element('routes')
        
        # Insertar vType al principio con speedDev para variabilidad
        vtype = ET.Element('vType')
        vtype.set('id', 'passenger')
        vtype.set('accel', '0.8')
        vtype.set('decel', '4.5')
        vtype.set('sigma', '0.1')
        vtype.set('length', '5.0')
        vtype.set('maxSpeed', '15.0')
        vtype.set('speedDev', '0.2')
        rou_root.insert(0, vtype)
        
        # Asignar tipo a todos los vehículos
        for vehicle in rou_root.findall('vehicle'):
            vehicle.set('type', 'passenger')
        
        # Escribir con indentación
        if hasattr(ET, 'indent'):
            ET.indent(rou_root, space="    ")
        rou_tree.write(rou_path, encoding='UTF-8', xml_declaration=True)
    except Exception as e:
        print(f"Advertencia al post-procesar rou.xml: {e}") 

    # Generar detectores (por defecto genera detectores e2)
    detector_tool = os.path.join(sumo_home, "tools", "output", "generateTLSE2Detectors.py") if sumo_home else "generateTLSE2Detectors.py"
    subprocess.run([sys.executable, detector_tool, "-n", f"{path}/rs.net.xml", "-l", "50", "-d", "0.1", "-o", f"{path}/rs.add.xml"]) 

    # Post-procesar: cargar nodos y edges para crear detectores e1 (inductionLoop) en calles unidireccionales que llegan a semáforo
    # 1) Cargar nodos y edges generados para decidir detectores
    nod_tree = ET.parse(f"{path}/rs.nod.xml")
    nod_root = nod_tree.getroot()
    node_type = {n.attrib['id']: n.attrib.get('type','') for n in nod_root.findall('node')}

    edg_tree = ET.parse(f"{path}/rs.edg.xml")
    edg_root = edg_tree.getroot()
    edge_oneway = {e.attrib['id']: e.attrib.get('oneway','false') == 'true' for e in edg_root.findall('edge')}
    edge_to = {e.attrib['id']: e.attrib.get('to') for e in edg_root.findall('edge')}

    # 2) Construir set de edges con oneway=true que llegan a semáforo (para e1)
    edges_to_e1 = set()
    for edge_id, is_oneway in edge_oneway.items():
        if is_oneway:
            to_node = edge_to.get(edge_id)
            if to_node and node_type.get(to_node) == 'traffic_light':
                edges_to_e1.add(edge_id)
    
    # 3) Procesar rs.add.xml: convertir laneAreaDetector a inductionLoop para edges e1
    add_path = f"{path}/rs.add.xml"
    try:
        add_tree = ET.parse(add_path)
        add_root = add_tree.getroot()
        
        # Procesar todos los laneAreaDetector
        detectors_to_convert = []
        for det in list(add_root.findall('laneAreaDetector')):
            lane_attr = det.attrib.get('lane','')
            if lane_attr:
                # Extraer edge id: remover últimos 2 caracteres (_X donde X es índice de carril)
                if len(lane_attr) > 2 and lane_attr[-2] == '_':
                    possible_edge = lane_attr[:-2]
                else:
                    possible_edge = lane_attr
                
                # Si el edge es e1, preparar conversión
                if possible_edge in edges_to_e1:
                    detectors_to_convert.append(det)
        
        # Reemplazar laneAreaDetector con inductionLoop
        for det in detectors_to_convert:
            det_id = det.attrib.get('id','').replace('e2det_', 'e1det_')
            lane = det.attrib.get('lane','')
            pos_value = det.attrib.get('pos','')
            
            # Crear inductionLoop
            induction = ET.Element('inductionLoop')
            induction.set('id', det_id)
            induction.set('lane', lane)
            induction.set('pos', pos_value)
            induction.set('freq', '60')
            induction.set('file', 'e1output.xml')
            
            # Reemplazar en el árbol
            idx = list(add_root).index(det)
            add_root.remove(det)
            add_root.insert(idx, induction)
        
        # Escribir con indentación
        ET.indent(add_root, space="    ") if hasattr(ET, 'indent') else None
        add_tree.write(add_path, encoding='UTF-8', xml_declaration=True)
    except FileNotFoundError:
        pass

    # 4) Escribir archivo de configuración
    cfg = f"""<configuration><input><net-file value="rs.net.xml"/><route-files value="rs.rou.xml"/><additional-files value="rs.add.xml"/></input></configuration>"""
    with open(f"{path}/random_sensorized_4x4.sumocfg", "w") as f:
        f.write(cfg)

    print(f"Escenario sensorizado 4x4 generado en {path}")


if __name__ == '__main__':
    build_random_sensorized_4x4(int(sys.argv[1]) if len(sys.argv) > 1 else None)