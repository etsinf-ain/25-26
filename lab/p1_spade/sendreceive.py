import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

class SenderAgent(Agent):
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            # recuerda añadir el login al nombre
            msg = Message(to="receiver@localhost")  # Destinatario
            msg.set_metadata("performative", "inform")  # Tipo de mensaje
            msg.body = "Hola desde el agente emisor!"
            await self.send(msg)
            print("Mensaje enviado!")

    async def setup(self):
        self.add_behaviour(self.SendBehaviour())

class ReceiverAgent(Agent):
    class ReceiveBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Espera al mensaje 10 segundos
            if msg:
                print("Mensaje recibido:", msg.body)
            else:
                print("No se recibió ningún mensaje.")

    async def setup(self):
        self.add_behaviour(self.ReceiveBehaviour())


async def main():
    sender = SenderAgent("sender@localhost", "1234")
    receiver = ReceiverAgent("receiver@localhost", "1234")
    await receiver.start()
    await sender.start()

if __name__ == "__main__":
    spade.run(main())