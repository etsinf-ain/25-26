import asyncio
import traci
import spade
from spade.agent import Agent
from spade_artifact import Artifact, ArtifactMixin

class E2SensorArtifact(Artifact):
    async def setup(self):
        self.sensor_id = "e2_west"
        self.lock = asyncio.Lock()

    async def run(self):
        while True:
            try:
                async with self.lock:
                    # E2: Podemos obtener muchos datos. 
                    total_vehicles = traci.lanearea.getLastStepVehicleNumber(self.sensor_id)
                    jam_length = traci.lanearea.getJamLengthVehicle(self.sensor_id)
                    mean_speed = traci.lanearea.getLastStepMeanSpeed(self.sensor_id)
                    
                    # Publicamos el estado completo del área
                    await self.publish(f"area_status({self.sensor_id}, {total_vehicles}, {jam_length}, {mean_speed:.2f})")
                    print(f"[Artefacto E2] {self.sensor_id}: Total={total_vehicles}, Cola={jam_length}, Vel={mean_speed:.1f}")
            except Exception as e:
                print(f"[Error Artefacto E2] ¡Algo ha fallado!: {e}")
                break
            await asyncio.sleep(1)

class E2Agent(ArtifactMixin, Agent):
    async def setup(self):
        print(f"[Agente E2] Monitorizando el área del carril...")
        await self.artifacts.focus(str(self.artifact_jid), self.on_sensor_data)

    def on_sensor_data(self, jid, value):
        # El valor viene como area_status(id, jam, speed)
        print(f"[Agente E2] Datos de área: {value}")

async def main():
    try:
        traci.init(port=8813)
        traci.setOrder(2)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Artefacto del Sensor
    artifact = E2SensorArtifact("e2_art@localhost", "1234")
    await artifact.start()

    # Agente que escucha al sensor
    agent = E2Agent("e2_observer@localhost", "password")
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
