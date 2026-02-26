import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

# Hereda de Agent para crear un nuevo agente SPADE
class DummyAgent(Agent):
    # Hereda de CyclicBehaviour para crear un nuevo comportamiento cíclico
    class MyBehav(CyclicBehaviour):
        # on_start se ejecuta al iniciar el comportamiento (solo una vez)
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counter = 0

        # ejecución del comportamiento
        async def run(self):
            # imprime el valor actual del contador y lo incrementa
            print("Counter: {}".format(self.counter))
            self.counter += 1
            # mata el comportamiento cuando el contador llega a 3
            if self.counter > 3:
                self.kill(exit_code=10)
                return
            # se suspende durante 1 segundo
            await asyncio.sleep(1)

        # on_end se ejecuta al finalizar el comportamiento (solo una vez)
        async def on_end(self):
            print("Behaviour finished with exit code {}.".format(self.exit_code))

    # En el icio, se crea una instancia del comportamiento y se añade al agente
    async def setup(self):
        print("Agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

### Añade tu login como parte del JID del agente
async def main():
    dummy = DummyAgent("counter@localhost", "1234")
    await dummy.start()
    # Espera a que el comportamiento termine (se puede hacer de otras formas, pero esta es sencilla)
    while not dummy.my_behav.is_killed():
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    assert dummy.my_behav.exit_code == 10
    await dummy.stop()   

if __name__ == "__main__":
    spade.run(main())