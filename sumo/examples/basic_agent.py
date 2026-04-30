import traci
import asyncio
import spade
import sys
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class SumoManager:
    """
    Clase estándar de Python para gestionar la infraestructura de SUMO.
    Encapsula toda la lógica de TraCI.
    """
    def __init__(self, port=8813):
        self.port = port

    def connect(self):
        print(f"[Infra] Conectando a SUMO en puerto {self.port}...")
        traci.init(port=self.port)
        # El Dashboard es el Cliente 1, nosotros somos el Cliente 2
        traci.setOrder(2)
        print("[Infra] Conexión establecida como Cliente 2.")

    def step(self):
        """Avanza un paso la simulación."""
        traci.simulationStep()

    def is_active(self):
        """Comprueba si la simulación debe continuar en SUMO."""
        try:
            return traci.simulation.getMinExpectedNumber() > 0
        except (traci.exceptions.FatalTraCIError, traci.exceptions.TraCIException):
            return False

    def close(self):
        print("[Infra] Cerrando conexión con SUMO...")
        try:
            traci.close()
        except:
            pass

class TrafficLightAgent(Agent):
    """
    Agente SPADE con responsabilidades mínimas.
    Solo se encarga de muestrear el estado del semáforo.
    """
    class SampleBehaviour(CyclicBehaviour):
        async def run(self):
            # El agente asume que la infraestructura ya está lista
            tl_id = "center"
            try:
                state = traci.trafficlight.getRedYellowGreenState(tl_id)
                t = traci.simulation.getTime()
                print(f"[Agente] Tiempo: {t}s | Estado '{tl_id}': {state}")
            except Exception as e:
                # Si falla la lectura, probablemente la conexión se ha cerrado
                pass
            
            # Frecuencia de muestreo propia del agente (independiente del step de SUMO)
            await asyncio.sleep(0.5)

    async def setup(self):
        print(f"[{self.jid}] Agente iniciado y listo para muestrear.")
        self.add_behaviour(self.SampleBehaviour())

async def main():
    # 1. Configuración de la Infraestructura (App)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8813
    sim = SumoManager(port=port)
    
    try:
        sim.connect()
    except Exception as e:
        print(f"[Error] No se pudo conectar con SUMO: {e}")
        print("Pista: Asegúrate de que el Dashboard está en Start con 'Enable External Connection' ON.")
        return

    # 2. Lanzamiento del Agente
    agent = TrafficLightAgent("hello_agent@localhost", "password")
    await agent.start()
    
    print("\n--- Simulación en marcha ---")
    print("El control del tiempo lo lleva la App, el agente solo observa.")
    
    # 3. Bucle de Control de la Aplicación
    try:
        while sim.is_active():
            sim.step()
            # IMPORTANTE: Ceder control al bucle de eventos para que SPADE trabaje
            await asyncio.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[App] Interrupción detectada.")
    finally:
        # 4. La App limpia todo al terminar
        print("[App] Deteniendo agentes y cerrando entorno...")
        if agent.is_alive():
            await agent.stop()
        sim.close()
        print("[App] Proceso finalizado.")

if __name__ == "__main__":
    # Ejecutamos el bucle principal de SPADE
    spade.run(main())
