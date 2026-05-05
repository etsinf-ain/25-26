import asyncio
import traci
import sys
import os
import spade
from spade.agent import Agent
from spade_bdi.bdi import BDIAgent
from spade_artifact import Artifact, ArtifactMixin

# Añadir el directorio raíz al path para poder importar sim_engine
sys.path.append(os.getcwd())

class TrafficLightArtifact(Artifact):
    async def setup(self):
        self.tl_id = "center"
        self.lanes = ["n2c_0", "w2c_0"] # IDs de carril en basic_cross
        self.lock = asyncio.Lock()

    async def switch_phase(self):
        """Método para cambiar el estado del semáforo (Thread-safe)."""
        async with self.lock:
            current_state = traci.trafficlight.getRedYellowGreenState(self.tl_id)
            # Lógica de cambio de fase: fase 0 (N-S verde), fase 2 (W-E verde)
            if "G" in current_state[0]: # Si el primer carril (N-S) está en verde
                new_phase = 2 
                new_state = "red" # (Desde el punto de vista del carril N-S)
            else:
                new_phase = 0
                new_state = "green"
                
            traci.trafficlight.setPhase(self.tl_id, new_phase)
            print(f"[Artefacto] Semáforo {self.tl_id} cambiado a {new_state}")

    async def run(self):
        while True:
            try:
                # Protegemos las lecturas de TraCI con el lock
                async with self.lock:
                    # Obtenemos el estado RYG (ej: "Gr")
                    state = traci.trafficlight.getRedYellowGreenState(self.tl_id)
                    # print(f"[Debug] Estado crudo de SUMO: {state}") # Descomenta para ver la cadena real
                    
                    # Mapeamos: buscamos 'g' o 'G' en la cadena de estado
                    # n2c_0 suele ser el primer link (o los primeros si hay varios carriles)
                    n_state = "green" if 'g' in state[0:len(state)//2].lower() else "red"
                    w_state = "green" if 'g' in state[len(state)//2:].lower() else "red"
                    
                    asyncio.create_task(self.publish(f'light_state("n2c_0", "{n_state}")'))
                    asyncio.create_task(self.publish(f'light_state("w2c_0", "{w_state}")'))

                    for lane in self.lanes:
                        count = traci.lane.getLastStepVehicleNumber(lane)
                        # Publicamos con comillas para el carril para que AgentSpeak lo trate como string
                        asyncio.create_task(self.publish(f'cars_waiting("{lane}", {count})'))
            except Exception:
                break
            await asyncio.sleep(1)


class BDIControllerAgent(ArtifactMixin, BDIAgent):
    def __init__(self, *args, artifact_jid: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.artifact_jid = artifact_jid

    def add_custom_actions(self, actions):
        """Registro de acciones para AgentSpeak."""
        @actions.add(".switch_phase", 0)
        def _switch_phase(agent, term, intention):
            print('[controller] switching traffic light phase')
            """EXPLICAR ESTO"""
            asyncio.run_coroutine_threadsafe(self.artifact.switch_phase(), self.loop)
            yield

    async def setup(self):
        print(f"[Agente] {self.jid} iniciándose...", flush=True)
        # await super().setup()
        # El callback ahora sí procesa las creencias
        await self.artifacts.focus(self.artifact.jid, self.on_artifact_update)

    # callback que se ejecuta cuando el artefacto publica un cambio
    def on_artifact_update(self, jid, value):
        """Actualiza las creencias del agente recibiendo el literal tal cual."""
        from spade_bdi.bdi import parse_literal
        print(f"[Agente] Recibido del artefacto: {value}")
        try:
            functor, args = parse_literal(value)
            # Desempaquetamos la tupla interna que devuelve parse_literal
            self.bdi.set_belief(functor, *args[0])
        except Exception:
            self.bdi.set_belief(value)


async def main():
    # 1. Configuración de la Infraestructura (App)
    # Se inicia SUMO con una conexión externa
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8813
    try:
        traci.init(port=port)
        traci.setOrder(2)
    except Exception as e:
        print(f"Error conexión SUMO: {e}", flush=True)
        return

    # 1. Crear el artefacto y el agente
    artifact = TrafficLightArtifact("tl_artifact@localhost", "1234")
    controller = BDIControllerAgent("tl_agent@localhost", "password", "traffic.asl", 
                                artifact_jid="tl_artifact@localhost")
    controller.artifact = artifact
    await artifact.start()
    await controller.start()
    print("\n--- Sistema Iniciado ---", flush=True)
    
    # Ejecuta la simulación hasta que se detenga manualmente
    try:
        while True:
            # Protegemos el paso de simulación con el mismo lock
            async with artifact.lock:
                traci.simulationStep()
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n** creencias finales del controlador:")
        if controller.bdi:
            controller.bdi.print_beliefs()
            
        await controller.stop()
        await artifact.stop()
        
        # 3. Cerramos SUMO al final de todo
        try:
            traci.close()
        except:
            pass
        print("[App] Simulación finalizada.")

if __name__ == "__main__":
    spade.run(main())
