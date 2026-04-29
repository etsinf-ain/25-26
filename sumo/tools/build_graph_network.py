"""
build_graph_network.py
Reads an OpenStreetMap (.osm) file and converts it into a clean, topological graph for SUMO.
Simplifies geometry by drawing straight lines between intersections.
"""
import osmnx as ox
import networkx as nx
import xml.etree.ElementTree as ET
import subprocess
import sys
import os

def create_sumo_graph_network(map_name=None, seed=None):
    if not map_name:
        map_name = "map"
        
    osm_file = f"assets/{map_name}.osm"
    if map_name == "map":
        output_prefix = "scenarios/graph/graph"
    else:
        output_prefix = f"scenarios/{map_name}/{map_name}"
        
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    
    print(f"Reading OSM file ({osm_file}) with OSMnx...")
    # Convert pure map into a topological mathematical graph
    G = ox.graph_from_xml(osm_file, simplify=True)
    
    # Keep only the largest connected component
    largest_cc = max(nx.strongly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()
    
    # Optional: Filter small streets if we want it even simpler (main streets only)
    edges_to_keep = []
    for u, v, k, data in G.edges(keys=True, data=True):
        highway = data.get('highway', '')
        if type(highway) == list: highway = highway[0]
        # Keep only medium-high level ways
        if highway in ['primary', 'secondary', 'tertiary', 'trunk', 'motorway']:
            edges_to_keep.append((u, v, k))
            
    G_simple = G.edge_subgraph(edges_to_keep).copy()
    largest_cc_simple = max(nx.strongly_connected_components(G_simple), key=len)
    G_simple = G_simple.subgraph(largest_cc_simple).copy()
    
    nodes_file = f"{output_prefix}.nod.xml"
    edges_file = f"{output_prefix}.edg.xml"
    
    print("Exporting topological Nodes to SUMO...")
    nodes = ET.Element('nodes')
    for node_id, data in G_simple.nodes(data=True):
        # In the graph, the node is an exact point (intersection)
        node_attrs = {
            'id': str(node_id),
            'x': str(data['x']),
            'y': str(data['y'])
        }
        # Retrieve traffic signals if OSM indicates it
        hw = data.get('highway', '')
        if 'traffic_signals' in (hw if isinstance(hw, list) else [hw]):
            node_attrs['type'] = 'traffic_light'
            
        ET.SubElement(nodes, 'node', node_attrs)
        
    tree = ET.ElementTree(nodes)
    tree.write(nodes_file)
    
    print("Exporting topological Edges to SUMO...")
    edges = ET.Element('edges')
    for u, v, k, data in G_simple.edges(keys=True, data=True):
        edge_id = f"{u}_{v}_{k}"
        
        # Extract speed
        speed = data.get('maxspeed', 50)
        if isinstance(speed, list): speed = speed[0]
        try: speed_float = float(speed) / 3.6
        except: speed_float = 13.89 # 50 km/h
            
        # Extract lanes
        lanes = data.get('lanes', 1)
        if isinstance(lanes, list): lanes = lanes[0]
        try: lanes_int = int(lanes)
        except: lanes_int = 1
            
        # IMPORTANT: We do not include the "shape" attribute that gives curves to streets.
        # By defining only from and to, SUMO will draw a perfect straight line.
        attrs = {
            'id': edge_id,
            'from': str(u),
            'to': str(v),
            'speed': str(speed_float),
            'numLanes': str(lanes_int)
        }
        ET.SubElement(edges, 'edge', attrs)
                      
    tree = ET.ElementTree(edges)
    tree.write(edges_file)
    
    print("Compiling SUMO network in Graph mode...")
    # --no-internal-links: Removes internal geometries of intersections
    subprocess.run([
        "netconvert", 
        "--node-files", nodes_file, 
        "--edge-files", edges_file, 
        "--output-file", f"{output_prefix}.net.xml",
        "--proj.utm", "true", # Converts lat/lon to meters
        "--no-internal-links", "true", 
        "--tls.guess-signals", "true", # Activate automatic traffic lights
        "--tls.join", "true" # Group nearby traffic lights
    ])
    
    print("Generating test traffic...")
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("La variable de entorno SUMO_HOME no está definida. Por favor, configúrala para apuntar a tu instalación de SUMO.")
        
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    cmd_rt = [
        sys.executable, script_path,
        "-n", f"{output_prefix}.net.xml",
        "-e", "200", "-p", "1.0",
        "-o", f"{output_prefix}.trips.xml",
        "-r", f"{output_prefix}.rou.xml"
    ]
    if seed is not None:
        cmd_rt.extend(["--seed", str(seed)])
        
    subprocess.run(cmd_rt)
 
    print("Creating configuration file...")
    base_name = os.path.basename(output_prefix)
    cfg = f"""<configuration>
    <input>
        <net-file value="{base_name}.net.xml"/>
        <route-files value="{base_name}.rou.xml"/>
    </input>
    <time><begin value="0"/><end value="1000"/></time>
    <report><no-step-log value="true"/><no-warnings value="true"/></report>
</configuration>"""
    with open(f"{output_prefix}.sumocfg", "w") as f:
        f.write(cfg)
        
    print(f"Done! Select {output_prefix}.sumocfg in the Dashboard.")

if __name__ == "__main__":
    import sys
    map_name = sys.argv[1] if len(sys.argv) > 1 else None
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
    create_sumo_graph_network(map_name=map_name, seed=seed)
