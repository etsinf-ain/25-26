import asyncio
import traci
import spade
import math
from spade.agent import Agent
from spade_artifact import Artifact, ArtifactMixin

class V2IArtifact(Artifact):
    async def setup(self):
        # Intentamos buscar un nodo central segun el escenario
        async with asyncio.Lock(): # Temporal para el setup
            all_juncs = traci.junction.getIDList()
            if "center" in all_juncs:
                self.junction_id = "center"
            elif "n_2_2" in all_juncs:
                self.junction_id = "n_2_2"
            elif all_juncs:
                self.junction_id = all_juncs[len(all_juncs)//2] # El nodo de la mitad de la lista
            else:
                self.junction_id = "unknown"
        
        self.range = 50            # Radio de detección (metros)
        self.lock = asyncio.Lock()
        print(f"[V2I Artifact] Monitorizando el cruce: {self.junction_id}")

    async def run(self):
        while True:
            try:
                async with self.lock:
                    # 1. Obtenemos la posición del cruce
                    junc_pos = traci.junction.getPosition(self.junction_id)
                    
                    # 2. Obtenemos todos los coches de la simulación
                    all_vehicles = traci.vehicle.getIDList()
                    
                    detected_cars = []
                    for veh_id in all_vehicles:
                        veh_pos = traci.vehicle.getPosition(veh_id)
                        # Calculamos distancia euclídea
                        dist = math.sqrt((veh_pos[0]-junc_pos[0])**2 + (veh_pos[1]-junc_pos[1])**2)
                        
                        if dist < self.range:
                            speed = traci.vehicle.getSpeed(veh_id)
                            detected_cars.append({"id": veh_id, "dist": round(dist, 1), "speed": round(speed, 1)})
                    
                    # 3. Publicamos la lista de coches detectados por proximidad (V2I)
                    if detected_cars:
                        await self.publish(f"detected_nearby({len(detected_cars)}, {detected_cars})")
                        print(f"[V2I] Detectados {len(detected_cars)} coches cerca del cruce {self.junction_id}")
            except Exception as e:
                print(f"[Error V2I] {e}")
                break
            await asyncio.sleep(1)

class FCDAgent(ArtifactMixin, Agent):
    async def setup(self):
        print(f"[Agente FCD] Iniciado. Escuchando mensajes de vehículos cercanos...")
        await self.artifacts.focus(str(self.artifact_jid), self.on_v2i_data)

    def on_v2i_data(self, jid, value):
        # Aquí el agente recibe la lista de coches como si fuera una red inalámbrica
        print(f"[Agente FCD] Recibido de la infraestructura: {value}")

async def main():
    # Este ejemplo funciona perfectamente con el escenario 'autonomous'
    try:
        traci.init(port=8813)
        traci.setOrder(2)
    except Exception as e:
        print(f"Error: {e}")
        return

    artifact = V2IArtifact("v2i_art@localhost", "1234")
    await artifact.start()

    agent = FCDAgent("v2i_observer@localhost", "password")
    agent.artifact_jid = artifact.jid
    await agent.start()

    try:
        while True:
            async with artifact.lock:
                traci.simulationStep()
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        await agent.stop()
        await artifact.stop()
        traci.close()

if __name__ == "__main__":
    spade.run(main())
