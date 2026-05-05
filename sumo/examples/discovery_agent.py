import asyncio
import traci
import sys
import os
import spade
from spade.agent import Agent
from spade_artifact import Artifact, ArtifactMixin

class DiscoveryArtifact(Artifact):
    async def run(self):
        # En este ejemplo no necesitamos bucle, solo una ejecución
        async with self.lock:
            print("\n" + "="*40)
            print(" EXPLORACIÓN DEL ESCENARIO SUMO")
            print("="*40)
            
            # 1. Semáforos
            tls = traci.trafficlight.getIDList()
            print(f"\n[MAPA] Semáforos ({len(tls)}): {tls}")
            for tl in tls:
                lanes = traci.trafficlight.getControlledLanes(tl)
                print(f"  - {tl} controla los carriles: {list(set(lanes))}")

            # 2. Carriles
            lanes = traci.lane.getIDList()
            print(f"\n[MAPA] Carriles totales: {len(lanes)}")

            # 3. Sensores E1 (Induction Loops)
            e1_sensors = traci.inductionloop.getIDList()
            print(f"\n[MAPA] Sensores E1 (Espiras) ({len(e1_sensors)}): {e1_sensors}")

            # 4. Sensores E2 (Lane Area Detectors)
            e2_sensors = traci.lanearea.getIDList()
            print(f"\n[MAPA] Sensores E2 (Área) ({len(e2_sensors)}): {e2_sensors}")
            
            print("\n" + "="*40 + "\n")
        
        # Después de explorar, el artefacto puede terminar
        await self.stop()

class DiscoveryAgent(ArtifactMixin, Agent):
    async def setup(self):
        print(f"[Agente] {self.jid} listo para explorar.")
        await self.artifacts.focus(str(self.artifact.jid), self.on_artifact_update)

    def on_artifact_update(self, jid, value):
        pass # No esperamos actualizaciones en este ejemplo

async def main():
    # Conexión estándar a SUMO
    port = 8813
    try:
        traci.init(port=port)
        traci.setOrder(2)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Creamos el artefacto de descubrimiento
    artifact = DiscoveryArtifact("discovery_art@localhost", "1234")
    artifact.lock = asyncio.Lock() # Compartimos el lock para TraCI
    await artifact.start()

    # Creamos el agente
    agent = DiscoveryAgent("explorer@localhost", "password")
    agent.artifact = artifact
    await agent.start()

    # Ejecutamos un paso para que TraCI se active
    async with artifact.lock:
        traci.simulationStep()
    
    # Damos tiempo a que el artefacto imprima
    await asyncio.sleep(2)

    await agent.stop()
    await artifact.stop()
    traci.close()

if __name__ == "__main__":
    spade.run(main())
