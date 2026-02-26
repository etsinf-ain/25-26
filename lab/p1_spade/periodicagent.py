# Código para el sistema con dos agentes: 
# uno envía mensajes periódicamente y el otro los recibe

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
import asyncio

class PeriodicSenderAgent(Agent):
    class SendPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            ### Añadid vuestro login como parte del JID del agente
            msg = Message(to="receiver@localhost")  # Asegúrate de reemplazar esto con el JID correcto del receptor
            msg.set_metadata("performative", "inform")
            msg.body = "Mensaje periódico del agente emisor"

            await self.send(msg)
            print("Mensaje enviado.")

    async def setup(self):
        # Ejemplo: enviar un mensaje cada 5 segundos
        periodic_behaviour = self.SendPeriodicBehaviour(period=1)
        self.add_behaviour(periodic_behaviour)

class ReceiverAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Espera por un mensaje por 10 segundos
            if msg:
                print("Mensaje recibido:", msg.body)
            else:
                print("Tiempo de espera excedido sin recibir mensaje.")

    async def setup(self):
        self.add_behaviour(self.ReceiveBehaviour())

async def main():
    sender = PeriodicSenderAgent("sender@localhost", "1234")
    receiver = ReceiverAgent("receiver@localhost", "1234")
    await receiver.start()
    await sender.start()
    
    # Mantener el programa corriendo
    print("Agentes iniciados. Presiona Ctrl+C para detener.")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await sender.stop()
        await receiver.stop()
        print("\nAgentes detenidos.")

if __name__ == "__main__":
    spade.run(main())