import asyncio
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, FSMBehaviour, State
from spade.message import Message

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
                print(f"[SEMÁFORO] Coche recibido: {msg.body}")
                self.agent.cars_waiting += 1

    # -------- FSM --------
    class RedState(State):
        async def run(self):
            print(f"🔴 ROJO | coches esperando: {self.agent.cars_waiting}")
            
            await asyncio.sleep(self.agent.red_time)
            self.set_next_state(GREEN)

    class RedStateAdapt(State):
        async def run(self):            
            # ACTIVIDAD 3: adapta el tiempo rojo según el número de coches.
            default_red = self.agent.total_cycle_time / 2
            if self.agent.cars_waiting > 0:
                # disminuye el tiempo rojo si hay coches esperando
                self.agent.red_time = max(1, self.agent.red_time - 1)
            else:
                # recupera el tiempo rojo cuando no hay coches
                self.agent.red_time = min(default_red, self.agent.red_time + 1)
            print(f"🔴 ROJO | coches esperando: {self.agent.cars_waiting}, wt: {self.agent.red_time}")
          
            await asyncio.sleep(self.agent.red_time)
            self.set_next_state(GREEN)


    class GreenState(State):
        async def run(self):
            print(f"🟢 VERDE | coches esperando: {self.agent.cars_waiting}")
            
            # pasan coches
            if self.agent.cars_waiting > 0:
                self.agent.cars_waiting -= 1
            
            await asyncio.sleep(self.agent.green_time)
            self.set_next_state(YELLOW)
            
    class GreenStateQueue(State):
        async def run(self):
            print(f"🟢 VERDE | coches esperando: {self.agent.cars_waiting}")
            
            # ACTIVIDAD 2: pasa 1 coche por segundo.
            cars_passing = min(self.agent.green_time, self.agent.cars_waiting)
            self.agent.cars_waiting -= cars_passing
            
            await asyncio.sleep(self.agent.green_time)
            self.set_next_state(YELLOW)

    class GreenStateAdapt(State):
        async def run(self):
            
            # ACTIVIDAD 3: adapta el tiempo verde según el número de coches.
            default_green = self.agent.total_cycle_time / 2
            if self.agent.cars_waiting > 0:
                # aumenta el tiempo verde si hay coches esperando
                self.agent.green_time = min(self.agent.total_cycle_time - self.agent.red_time, self.agent.green_time + 1)
            else:
                # recupera el tiempo verde hacia el valor por defecto cuando no hay coches
                self.agent.green_time = max(default_green, self.agent.green_time - 1)
            print(f"🟢 VERDE | coches esperando: {self.agent.cars_waiting}, wt: {self.agent.green_time}")

            cars_passing = min(self.agent.green_time, self.agent.cars_waiting)
            self.agent.cars_waiting -= cars_passing
            
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
        # original
        fsm.add_state(name=RED, state=self.RedState(), initial=True)
        # actividad 3:
        # fsm.add_state(name=RED, state=self.RedStateAdapt(), initial=True)
        # original
        fsm.add_state(name=GREEN, state=self.GreenState())
        # actividad 2:
        # fsm.add_state(name=GREEN, state=self.GreenStateQueue())
        # actividad 3:
        # fsm.add_state(name=GREEN, state=self.GreenStateAdapt())
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
# AGENTE CONTROLADOR. ACTIVIDAD 4
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

            print(f"[CTRL] cola={light.cars_waiting} | 🔴 {light.red_time}s  🟢 {light.green_time}s")
            await asyncio.sleep(2)

            # Alternativa: usar mensajes para ajustar los tiempos 
            # desde el controlador en lugar de acceder directamente 
            # al semáforo

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
    # el controlador necesita una referencia al semáforo para ajustar los tiempos
    controller.traffic_light = light
    await controller.start()

    # lanzar varios coches
    for i in range(30):
        car = CarAgent(f"car{i}@localhost", password)
        car.traffic_light_jid = jid_light
        await car.start()
        await asyncio.sleep(1)

    await asyncio.sleep(20)
    await light.stop()
    await controller.stop()

if __name__ == "__main__":
    asyncio.run(main())