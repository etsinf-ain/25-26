import traci
import sumolib
import matplotlib.pyplot as plt
import os
import sys
import time

# Configuración
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET_FILE = os.path.join(BASE_DIR, "scenarios", "cross", "cross.net.xml")  
SUMO_CFG = os.path.join(BASE_DIR, "scenarios", "cross", "cross.sumocfg")

if not os.path.exists(NET_FILE):
    print(f"Error: No se encuentra {NET_FILE}")
    sys.exit(1)

# 1. Cargamos la red
net = sumolib.net.readNet(NET_FILE)
xmin, ymin, xmax, ymax = net.getBoundary()

# Margen para que no colapse la vista
margin = 20
xmin -= margin; xmax += margin; ymin -= margin; ymax += margin

traci.start(["sumo", "-c", SUMO_CFG, "--no-step-log", "--no-warnings"])

plt.ion()
fig, ax = plt.subplots(figsize=(10, 8))

# 2. Dibujamos el mapa (estático)
print("Dibujando mapa...")
for edge in net.getEdges():
    for lane in edge.getLanes():
        shape = lane.getShape()
        x_coords = [p[0] for p in shape]
        y_coords = [p[1] for p in shape]
        ax.plot(x_coords, y_coords, color="silver", linewidth=2, zorder=1)

# Puntos de los vehículos
v_dots = ax.scatter([], [], color="red", s=50, zorder=2, edgecolors='black')

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_facecolor('#f0f0f0')

print(f"Simulando {SUMO_CFG}. Observa la ventana de Matplotlib.")

try:
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        veh_ids = traci.vehicle.getIDList()
        positions = [traci.vehicle.getPosition(v) for v in veh_ids]
        
        # Debug: ver coordenadas reales
        if step % 20 == 0 and veh_ids:
            v0 = veh_ids[0]
            x, y = traci.vehicle.getPosition(v0)
            lane = traci.vehicle.getLaneID(v0)
            print(f"Paso {step} | Coche {v0} en {lane}: x={x:.1f}, y={y:.1f}", flush=True)

        if positions:
            v_dots.set_offsets(positions)
        else:
            v_dots.set_offsets(os.sys.modules['numpy'].empty((0, 2)))
            
        ax.set_title(f"Tiempo: {traci.simulation.getTime()}s | Vehículos: {len(positions)}")
        
        # Forzar el refresco y pequeña pausa
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.02) 
        step += 1
        
except KeyboardInterrupt:
    pass
finally:
    try:
        traci.close()
    except:
        pass
    plt.ioff()
    print("Simulación terminada. La ventana permanecerá abierta.")
    plt.show() # Esto bloquea y deja la ventana abierta al final