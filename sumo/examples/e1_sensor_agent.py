import asyncio
import traci
import spade
from spade.agent import Agent
from spade_artifact import Artifact, ArtifactMixin

class E1SensorArtifact(Artifact):
    async def setup(self):
        self.sensor_id = "e1_north"
        self.lock = asyncio.Lock()

    async def run(self):
        while True:
            try:
                async with self.lock:
                    # EXPLICACIÓN PARA ALUMNOS: 
                    # El sensor E1 (espira) es VOLÁTIL. Solo informa de los coches que pasan 
                    # en el EXACTO paso de simulación actual (normalmente 0.1s).
                    # Si el agente espera demasiado entre lecturas (ej: 0.5s), se perderá 
                    # los coches que pasaron en los 4 pasos intermedios que no miró.
                    count = traci.inductionloop.getLastStepVehicleNumber(self.sensor_id)
                    if count > 0:
                        await self.publish(f"car_passed({self.sensor_id}, {count})")
                        print(f"[Sensor E1] ¡Detección! {count} coche(s) en {self.sensor_id}")
            except Exception:
                break
            
            # Para no perder datos, el tiempo de espera debe ser MENOR o IGUAL 
            # al paso de simulación de SUMO (step-length, por defecto 0.1s).
            # await asyncio.sleep(0.5) # <-- CÓDIGO ANTERIOR: Perdía datos
            await asyncio.sleep(0.05)   # Escaneamos cada 0.05s para asegurar capturar cada paso

class E1Agent(ArtifactMixin, Agent):
    async def setup(self):
        print(f"[Agente E1] Esperando datos de la espira...")
        # Nos suscribimos al artefacto del sensor
        await self.artifacts.focus(str(self.artifact_jid), self.on_sensor_data)

    def on_sensor_data(self, jid, value):
        print(f"[Agente E1] Recibida percepción: {value}")

async def main():
    try:
        traci.init(port=8813)
        traci.setOrder(2)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Artefacto del Sensor
    artifact = E1SensorArtifact("e1_art@localhost", "1234")
    await artifact.start()

    # Agente que escucha al sensor
    agent = E1Agent("e1_observer@localhost", "password")
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
