'''
Un agente pide a otros tres agentes que le envíen un dato 
(un valor aleatorio). El agente almacena los valores 
y cuando los ha recibido todos los muestra por pantalla.
'''

import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import random

class ProposerAgent(Agent):
    
    class ProposeBehaviour(OneShotBehaviour):
        async def run(self):
            ### Añadid vuestro login como parte del JID de los agentes
            receivers = ["receiver1@localhost", "receiver2@localhost", "receiver3@localhost"]
            for receiver in receivers:
                msg = spade.message.Message(
                    to=receiver,
                    body="propuesta",
                    metadata={"performative": "propose"}
                )
                await self.send(msg)
                print(f"Propuesta enviada a {receiver}")

            # Esperar y recoger respuestas
            self.agent.responses = []
            for _ in range(3):
                response = await self.receive(timeout=10)
                if response:
                    self.agent.responses.append(response.body)
            print("Respuestas recibidas:", self.agent.responses)

    async def setup(self):
        print(f"{self.name} iniciado")
        self.add_behaviour(self.ProposeBehaviour())


class ReceiverAgent(Agent):
    async def setup(self):
        print(f"{self.name} iniciado")
        self.add_behaviour(self.ReceiveBehaviour())

    class ReceiveBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                number = str(random.randint(1, 100))
                reply = msg.make_reply()
                reply.body = number
                await self.send(reply)
                print(f"{self.agent.name} respondió con {number}")


async def main():
    proposer = ProposerAgent("proposer@localhost", "1234")
    receiver1 = ReceiverAgent("receiver1@localhost", "1234")
    receiver2 = ReceiverAgent("receiver2@localhost", "1234")
    receiver3 = ReceiverAgent("receiver3@localhost", "1234")

    await receiver1.start()
    await receiver2.start()
    await receiver3.start()
    await proposer.start()

    await asyncio.sleep(10)

    await proposer.stop()
    await receiver1.stop()
    await receiver2.stop()
    await receiver3.stop()

if __name__ == "__main__":
    spade.run(main())