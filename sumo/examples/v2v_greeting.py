import asyncio
import traci
import spade
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from spade_artifact import Artifact, ArtifactMixin

# El artefacto actua como un Broker de descubrimiento
class AntennaArtifact(Artifact):
    async def setup(self):
        self.junction_id = "n_2_2" # Nodo central en el escenario autonomous
        self.lock = asyncio.Lock()

    async def run(self):
        while True:
            try:
                async with self.lock:
                    # En este ejemplo, asumimos que si un coche existe en SUMO, 
                    # tiene un agente con JID: veh_ID@localhost
                    all_vehicles = traci.vehicle.getIDList()
                    nearby_jids = [f"veh_{vid}@localhost" for vid in all_vehicles]
                    
                    if nearby_jids:
                        await self.publish(f"neighbors({nearby_jids})")
            except Exception:
                break
            await asyncio.sleep(1)

# El comportamiento para recibir saludos de otros coches
class ReceiveGreeting(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=5)
        if msg:
            print(f"[{self.agent.jid}] He recibido un saludo de {msg.sender}: {msg.body}")

# El agente que representa a un coche inteligente
class SmartCarAgent(ArtifactMixin, Agent):
    async def setup(self):
        self.known_neighbors = set()
        self.add_behaviour(ReceiveGreeting())
        await self.artifacts.focus(str(self.artifact_jid), self.on_nearby_discovery)

    def on_nearby_discovery(self, jid, value):
        # El valor es algo como neighbors(['veh_0@localhost', 'veh_1@localhost'])
        # Extrar jids de forma simple para el ejemplo
        import re
        found_jids = re.findall(r"[\w\d_]+@[\w\d.]+", value)
        
        for neighbor in found_jids:
            if neighbor != str(self.jid) and neighbor not in self.known_neighbors:
                self.known_neighbors.add(neighbor)
                # Enviamos el saludo V2V
                asyncio.create_task(self.say_hello(neighbor))

    async def say_hello(self, to_jid):
        print(f"[{self.jid}] Enviando saludo V2V a {to_jid}")
        msg = Message(to=to_jid)
        msg.body = "Hola vecino, soy un coche inteligente."
        await self.send(msg)

async def main():
    # Para este ejemplo necesitamos tener SUMO funcionando (escenario autonomous)
    try:
        traci.init(port=8813)
        traci.setOrder(2)
    except Exception:
        print("Error: No se pudo conectar a SUMO. ¿Esta el Dashboard en marcha?")
        return

    # 1. Iniciamos la antena
    antena = AntennaArtifact("antena@localhost", "1234")
    await antena.start()

    # 2. Iniciamos un par de coches de prueba (simulando veh_0 y veh_1 de SUMO)
    coche0 = SmartCarAgent("veh_0@localhost", "password")
    coche0.artifact_jid = antena.jid
    
    coche1 = SmartCarAgent("veh_1@localhost", "password")
    coche1.artifact_jid = antena.jid

    await coche0.start()
    await coche1.start()

    print("SISTEMA V2V LISTO. Esperando detecciones en SUMO...")
    try:
        while True:
            async with antena.lock:
                traci.simulationStep()
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        await coche0.stop()
        await coche1.stop()
        await antena.stop()
        traci.close()

if __name__ == "__main__":
    spade.run(main())
