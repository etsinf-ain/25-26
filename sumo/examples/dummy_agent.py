import traci
import time
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8813
print(f"Conectando al simulador en el puerto {port}...")
traci.init(port=port)
traci.setOrder(2) # Nos registramos como el Cliente 2 (Agentes)

print("¡Conectado! Controlando el paso del tiempo...")
while traci.simulation.getMinExpectedNumber() > 0:
    # Avanzamos un paso de la simulación. 
    # El visualizador de Streamlit (Cliente 1) no puede avanzar sin nosotros.
    traci.simulationStep()
    t = traci.simulation.getTime()
    
    # Aquí es donde iría la lógica del agente leyendo colas y cambiando luces:
    # ids_semaforos = traci.trafficlight.getIDList()
    
    print(f"Paso de tiempo completado: {t}", end="\r")
    time.sleep(0.1) # Simulamos que el agente tarda un poco en procesar

traci.close()
print("\nSimulación finalizada.")
