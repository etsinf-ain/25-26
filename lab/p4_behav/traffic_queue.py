import asyncio
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, FSMBehaviour, State
from spade.message import Message

# ======================
# VISUALIZACIÓN DE COLA
# ======================
MAX_QUEUE = 20

def queue_bar(n, max_n=MAX_QUEUE):
    filled = min(n, max_n)
    empty = max_n - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {n:>3} coches"

# ======================
# ESTADOS DEL SEMÁFORO
# ======================
RED = "RED"
GREEN = "GREEN"
YELLOW = "YELLOW"

# ======================
# AGENTE SEMÁFORO
# ======================
class TrafficLightAgent(Agent):

    class InitBehaviour(OneShotBehaviour):
        async def run(self):
            print("Inicializando semáforo...")
            self.agent.cars_waiting = 0
            # ACTIVIDAD 2-4
            # establece el tiempo de rojo, verde y amarillo (en segundos)
            self.agent.total_cycle_time = 6
            self.agent.red_time = self.agent.total_cycle_time / 2
            self.agent.green_time = self.agent.total_cycle_time / 2
            self.agent.yellow_time = 1

    class TrafficMonitor(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                self.agent.cars_waiting += 1
                print(f"->  {queue_bar(self.agent.cars_waiting)}")

    # -------- FSM --------
    class RedState(State):
        async def run(self):
            print(f"🔴 ROJO (t={int(self.agent.red_time)}s) | {queue_bar(self.agent.cars_waiting)}")
            await asyncio.sleep(self.agent.red_time)
            self.set_next_state(GREEN)

    class GreenStateQueue(State):
        async def run(self):
            print(f"🟢 VERDE (t={int(self.agent.green_time)}s)")
            cars_passing = int(min(self.agent.green_time, self.agent.cars_waiting))
            for _ in range(cars_passing):
                self.agent.cars_waiting -= 1
                print(f"<-  {queue_bar(self.agent.cars_waiting)}")
            await asyncio.sleep(self.agent.green_time)
            self.set_next_state(YELLOW)

    class YellowState(State):
        async def run(self):
            print("🟡 AMARILLO")
            await asyncio.sleep(self.agent.yellow_time)
            self.set_next_state(RED)


    class TrafficFSM(FSMBehaviour):
        async def on_start(self):
            print("FSM iniciada")

    async def setup(self):
        print("Semáforo arrancado")

        self.add_behaviour(self.InitBehaviour())
        self.add_behaviour(self.TrafficMonitor())

        fsm = self.TrafficFSM()
        fsm.add_state(name=RED, state=self.RedState(), initial=True)
        fsm.add_state(name=GREEN, state=self.GreenStateQueue())
        fsm.add_state(name=YELLOW, state=self.YellowState())

        fsm.add_transition(RED, GREEN)
        fsm.add_transition(GREEN, YELLOW)
        fsm.add_transition(YELLOW, RED)

        self.add_behaviour(fsm)


# ======================
# AGENTE COCHE
# ======================
class CarAgent(Agent):

    class SendArrival(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.traffic_light_jid)
            msg.body = "car arrived"
            await self.send(msg)
            print(f"[COCHE {self.agent.name}] enviado")

            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.SendArrival())

# ======================
# AGENTE CONTROLADOR
# ======================

class TrafficController(Agent):

    class ControlBehaviour(CyclicBehaviour):
        async def run(self):
            light = self.agent.traffic_light
            default_red = light.total_cycle_time / 2
            default_green = light.total_cycle_time / 2

            if light.cars_waiting > 0:
                light.red_time = max(1, light.red_time - 1)
                light.green_time = min(light.total_cycle_time - light.red_time, light.green_time + 1)
            else:
                light.red_time = min(default_red, light.red_time + 1)
                light.green_time = max(default_green, light.green_time - 1)

            print(f"[CTRL] 🔴 {int(light.red_time)}s  🟢 {int(light.green_time)}s")
            await asyncio.sleep(2)

    async def setup(self):
        self.add_behaviour(self.ControlBehaviour())


# ======================
# MAIN
# ======================
async def main():
    # Credenciales ficticias (usar XMPP real si se ejecuta)
    jid_light = "light@localhost"
    jid_controller = "controller@localhost"
    password = "test"

    light = TrafficLightAgent(jid_light, password)
    await light.start()

    controller = TrafficController(jid_controller, password)
    controller.traffic_light = light
    await controller.start()

    # lanzar varios coches
    for i in range(30):
        car = CarAgent(f"car{i}@localhost", password)
        car.traffic_light_jid = jid_light
        await car.start()
        await asyncio.sleep(1)

    # esperar hasta que no queden coches en cola
    while light.cars_waiting > 0:
        await asyncio.sleep(1)
    print("Todos los coches procesados. Fin de la simulación.")
    await light.stop()
    await controller.stop()

if __name__ == "__main__":
    asyncio.run(main())