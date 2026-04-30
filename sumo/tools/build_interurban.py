"""
build_interurban.py
Generates an irregular road network using random nodes to simulate rural or secondary roads.
Simulates high-speed single-lane roads connecting towns.
"""
import subprocess
import sys
import os

def create_interurban_network(seed=None):
    if seed is None:
        seed = 42
        
    print(f"Generating irregular interurban network (seed {seed})...")
    
    # We use SUMO's netgenerate to create a purely random and irregular network
    # simulating secondary and national roads connecting small towns.
    subprocess.run([
        "netgenerate", 
        "--rand", 
        "--rand.iterations", "40",            # Number of nodes/towns
        "--rand.bidi-probability", "1.0",     # 100% two-way roads
        "--rand.max-distance", "600",         # Maximum distance between towns
        "--rand.min-distance", "200",         # Minimum distance
        "--default.speed", "25.0",            # 90 km/h
        "--default.lanenumber", "1",          # 1 lane per direction (allows passing by invading opposite lane)
        "--no-turnarounds", "true",           # No U-turns in the middle of the road
        "--seed", str(seed),
        "--output-file", "scenarios/interurban/interurban.net.xml"
    ])
    
    print("Generating interurban traffic...")
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("La variable de entorno SUMO_HOME no está definida. Por favor, configúrala para apuntar a tu instalación de SUMO.")
        
    script_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    cmd_rt = [
        sys.executable, script_path,
        "-n", "scenarios/interurban/interurban.net.xml",
        "-e", "150", "-p", "1.5",
        "-o", "scenarios/interurban/interurban.trips.xml",
        "-r", "scenarios/interurban/interurban.rou.xml",
        "--seed", str(seed)
    ]
    subprocess.run(cmd_rt)
    
    cfg_content = """<configuration>
    <input>
        <net-file value="interurban.net.xml"/>
        <route-files value="interurban.rou.xml"/>
    </input>
</configuration>"""
    with open("scenarios/interurban/interurban.sumocfg", "w") as f:
        f.write(cfg_content)
        
    print("Generation complete! (scenarios/interurban/interurban.sumocfg)")

if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    create_interurban_network(seed)
