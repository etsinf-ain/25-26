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
        print(f"[ART {self.name}] Tiempos actualizados: 🔴 {self.red_time}s  🟢 {self.green_time}s")

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
        self.cars_waiting_1 = 0
        self.cars_waiting_2 = 0
        self.artifact1 = None
        self.artifact2 = None

    class InitBehaviour(OneShotBehaviour):
        async def run(self):
            print("Inicializando agente semáforo para el cruce...")

    class CarMonitorBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                if "street1" in msg.body:
                    self.agent.cars_waiting_1 += 1
                elif "street2" in msg.body:
                    self.agent.cars_waiting_2 += 1

    class RedState(State):
        async def run(self):
            print(f"🔴 S1 ROJO ({self.agent.cars_waiting_1}) | 🟢 S2 VERDE ({self.agent.cars_waiting_2})")
            await self.agent.artifact1.set_red()
            await self.agent.artifact2.set_green()
            
            cars_passing = min(self.agent.artifact2.green_time, self.agent.cars_waiting_2)
            self.agent.cars_waiting_2 -= cars_passing
            
            await asyncio.sleep(self.agent.artifact1.red_time)
            self.set_next_state(GREEN)

    class GreenState(State):
        async def run(self):
            print(f"🟢 S1 VERDE ({self.agent.cars_waiting_1}) | 🔴 S2 ROJO ({self.agent.cars_waiting_2})")
            await self.agent.artifact1.set_green()
            await self.agent.artifact2.set_red()
            
            cars_passing = min(self.agent.artifact1.green_time, self.agent.cars_waiting_1)
            self.agent.cars_waiting_1 -= cars_passing
            
            await asyncio.sleep(self.agent.artifact1.green_time)
            self.set_next_state(YELLOW)

    class YellowState(State):
        async def run(self):
            print("🟡 S1 AMARILLO | 🔴 S2 ROJO")
            await self.agent.artifact1.set_yellow()
            await self.agent.artifact2.set_red()
            await asyncio.sleep(self.agent.artifact1.yellow_time)
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
        self.street = None

    def color_callback(self, artifact, state):
        if state == "GREEN":
            self.cross_event.set()

    class DriveBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.traffic_light_agent_jid)
            msg.body = f"car arrived {self.agent.street}"
            await self.send(msg)
            print(f"[COCHE {self.agent.name}] esperando en {self.agent.street}")
            
            await self.agent.cross_event.wait()
            print(f"[COCHE {self.agent.name}] cruzando el semáforo de {self.agent.street} en verde")
            await asyncio.sleep(0.5)
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
            art1 = light_agent.artifact1
            art2 = light_agent.artifact2
            
            default_red = art1.total_cycle_time / 2
            default_green = art1.total_cycle_time / 2

            if light_agent.cars_waiting_1 > light_agent.cars_waiting_2:
                new_red = max(1, art1.red_time - 1)
                new_green = min(art1.total_cycle_time - new_red, art1.green_time + 1)
            elif light_agent.cars_waiting_2 > light_agent.cars_waiting_1:
                new_green = max(1, art1.green_time - 1)
                new_red = min(art1.total_cycle_time - new_green, art1.red_time + 1)
            else:
                new_red = default_red
                new_green = default_green

            await art1.set_times(new_red, new_green)
            await art2.set_times(new_green, new_red)
            print(f"[CTRL] colas: S1={light_agent.cars_waiting_1} S2={light_agent.cars_waiting_2}")
            await asyncio.sleep(2)

    def __init__(self, *args, artifact_jid=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.traffic_light_jid = artifact_jid

    def callback(self, artifact, state):
        pass

    async def setup(self):
        self.add_behaviour(self.ControlBehaviour())


# ======================
# MAIN
# ======================
async def main():
    import sys
    import os
    sys.path.insert(0, os.path.abspath("../spade_fixes"))

    light_art1 = TrafficLight("light_art1@localhost", "1234")
    light_art2 = TrafficLight("light_art2@localhost", "1234")

    light_agent = TrafficLightAgent("light_agent@localhost", "1234")
    light_agent.artifact1 = light_art1
    light_agent.artifact2 = light_art2

    controller = TrafficController("controller@localhost", "1234", artifact_jid="light_art1@localhost")
    controller.traffic_light_agent = light_agent
    
    await light_art1.start()
    await light_art2.start()
    await light_agent.start()
    await controller.start()

    print("INICIANDO SIMULACIÓN")
    for i in range(10):
        car = CarAgent(f"car{i}@localhost", "1234")
        if i % 2 == 0:
            car.street = "street1"
            car.traffic_light_jid = "light_art1@localhost"
        else:
            car.street = "street2"
            car.traffic_light_jid = "light_art2@localhost"
            
        car.traffic_light_agent_jid = "light_agent@localhost"
        await car.start()
        await asyncio.sleep(0.5)

    await asyncio.sleep(15)
    print("DETNIENDO SIMULACIÓN")
    await light_agent.stop()
    await controller.stop()
    await light_art1.stop()
    await light_art2.stop()

if __name__ == "__main__":
    spade.run(main())