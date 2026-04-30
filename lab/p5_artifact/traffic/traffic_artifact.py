import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, FSMBehaviour, State
from spade.message import Message
from spade_artifact import Artifact, ArtifactMixin

RED = "RED"
GREEN = "GREEN"
YELLOW = "YELLOW"

# ======================
# 1. ARTEFACTO SEMÁFORO
# ======================
class TrafficLight(Artifact):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = RED
        self.total_cycle_time = 6
        self.red_time = self.total_cycle_time / 2
        self.green_time = self.total_cycle_time / 2
        self.yellow_time = 1

    async def setup(self):
        await self.publish(self.state)

    async def set_times(self, red, green):
        self.red_time = red
        self.green_time = green
        print(f"[ART] Tiempos actualizados: 🔴 {self.red_time}s  🟢 {self.green_time}s")

    async def set_red(self):
        self.state = RED
        print("[ART] Semáforo cambia a ROJO")
        await self.publish(self.state)

    async def set_green(self):
        self.state = GREEN
        print("[ART] Semáforo cambia a VERDE")
        await self.publish(self.state)

    async def set_yellow(self):
        self.state = YELLOW
        print("[ART] Semáforo cambia a AMARILLO")
        await self.publish(self.state)


# ======================
# 2. AGENTE SEMÁFORO (FSM)
# ======================
class TrafficLightAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cars_waiting = 0

    class InitBehaviour(OneShotBehaviour):
        async def run(self):
            print("Inicializando agente semáforo...")

    class CarMonitorBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print(f"[SEMÁFORO] Coche recibido: {msg.body}")
                self.agent.cars_waiting += 1

    class RedState(State):
        async def run(self):
            print(f"🔴 ROJO | coches esperando: {self.agent.cars_waiting}")
            await self.agent.artifact.set_red()
            await asyncio.sleep(self.agent.artifact.red_time)
            self.set_next_state(GREEN)

    class GreenState(State):
        async def run(self):
            print(f"🟢 VERDE | coches esperando: {self.agent.cars_waiting}")
            await self.agent.artifact.set_green()
            cars_passing = min(self.agent.artifact.green_time, self.agent.cars_waiting)
            self.agent.cars_waiting -= cars_passing
            await asyncio.sleep(self.agent.artifact.green_time)
            self.set_next_state(YELLOW)

    class YellowState(State):
        async def run(self):
            print("🟡 AMARILLO")
            await self.agent.artifact.set_yellow()
            await asyncio.sleep(self.agent.artifact.yellow_time)
            self.set_next_state(RED)

    async def setup(self):
        fsm = FSMBehaviour()
        fsm.add_state(name=RED, state=self.RedState(), initial=True)
        fsm.add_state(name=GREEN, state=self.GreenState())
        fsm.add_state(name=YELLOW, state=self.YellowState())

        fsm.add_transition(RED, GREEN)
        fsm.add_transition(GREEN, YELLOW)
        fsm.add_transition(YELLOW, RED)

        self.add_behaviour(self.InitBehaviour())
        self.add_behaviour(self.CarMonitorBehaviour())
        self.add_behaviour(fsm)


# ======================
# AGENTE COCHE
# ======================
class CarAgent(ArtifactMixin, Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cross_event = asyncio.Event()
        self.traffic_light_jid = None
        self.traffic_light_agent_jid = None

    def color_callback(self, artifact, state):
        if state == "GREEN":
            self.cross_event.set()

    class DriveBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.traffic_light_agent_jid)
            msg.body = "car arrived"
            await self.send(msg)
            print(f"[COCHE {self.agent.name}] esperando en el cruce")
            
            await self.agent.cross_event.wait()
            print(f"[COCHE {self.agent.name}] cruzando el semáforo en verde")
            await asyncio.sleep(0.5)
            # desuscribe al coche de los cambios del semáforo
            await self.agent.artifacts.ignore(self.agent.traffic_light_jid)
            await self.agent.stop()

    async def setup(self):
        await self.artifacts.focus(self.traffic_light_jid, self.color_callback)
        self.add_behaviour(self.DriveBehaviour())


# ======================
# 3. AGENTE CONTROLADOR
# ======================
class TrafficController(ArtifactMixin, Agent):

    class ControlBehaviour(CyclicBehaviour):
        async def run(self):
            light_agent = self.agent.traffic_light_agent
            light_art = light_agent.artifact
            
            default_red = light_art.total_cycle_time / 2
            default_green = light_art.total_cycle_time / 2

            if light_agent.cars_waiting > 0:
                new_red = max(1, light_art.red_time - 1)
                new_green = min(light_art.total_cycle_time - new_red, light_art.green_time + 1)
            else:
                new_red = min(default_red, light_art.red_time + 1)
                new_green = max(default_green, light_art.green_time - 1)

            await light_art.set_times(new_red, new_green)
            print(f"[CTRL] cola={light_agent.cars_waiting} | 🔴 {light_art.red_time}s  🟢 {light_art.green_time}s")
            await asyncio.sleep(2)


    def __init__(self, *args, artifact_jid=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.traffic_light_jid = artifact_jid

    def callback(self, artifact, state):
        print(f"[CTRL] Semáforo observable en: {state}")

    async def setup(self):
        self.add_behaviour(self.ControlBehaviour())
        await self.artifacts.focus(self.traffic_light_jid, self.callback)


# ======================
# MAIN
# ======================
async def main():
    light_art = TrafficLight("light_art@localhost", "1234")

    light_agent = TrafficLightAgent("light_agent@localhost", "1234")
    light_agent.artifact = light_art

    controller = TrafficController("controller@localhost", "1234", artifact_jid="light_art@localhost")
    controller.traffic_light_agent = light_agent
    await light_art.start()
    await light_agent.start()
    await controller.start()

    print("INICIANDO SIMULACIÓN")
    for i in range(10):
        car = CarAgent(f"car{i}@localhost", "1234")
        car.traffic_light_jid = "light_art@localhost"
        car.traffic_light_agent_jid = "light_agent@localhost"
        await car.start()
        await asyncio.sleep(0.5)

    await asyncio.sleep(15)
    print("DETNIENDO SIMULACIÓN")
    await light_agent.stop()
    await controller.stop()
    await light_art.stop()

if __name__ == "__main__":
    spade.run(main())