'''
Un agente pide a otros tres agentes que le envíen un dato 
(un valor aleatorio). El agente almacena los valores 
y cuando los ha recibido todos, seleciona el mayor
y comunica al agente que lo ha enviado que ha sido elegido
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
            ### Añade tu login como parte del JID de los agentes
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
            self.agent.responses = {}
            for _ in range(len(receivers)):
                response = await self.receive(timeout=10)
                if response:
                    self.agent.responses[response.sender] = response.body
            print("Respuestas recibidas:", self.agent.responses)

            # Seleccionar el mayor valor
            max_value = max(int(v) for v in self.agent.responses.values())
            max_agent = next(k for k, v in self.agent.responses.items() if int(v) == max_value)
            print(f"El agente {max_agent} ha sido elegido con valor {max_value}")

            # Enviar mensaje al agente elegido
            msg = spade.message.Message(
                to=f"{max_agent}",
                body=f"Has sido elegido con valor {max_value}",
                metadata={"performative": "inform"}
            )
            await self.send(msg)

    async def setup(self):
        print(f"{self.name} iniciado")
        self.add_behaviour(self.ProposeBehaviour())


class ReceiverAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                number = str(random.randint(1, 100))
                reply = msg.make_reply()
                reply.body = number
                await self.send(reply)
                print(f"{self.agent.name} respondió con {number}")

    class WaitForInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata["performative"] == "inform":
                print(f"{self.agent.name} recibió mensaje de selección: {msg.body}")

    async def setup(self):
        print(f"{self.name} iniciado")
        self.add_behaviour(self.ReceiveBehaviour())
        self.add_behaviour(self.WaitForInformBehaviour())


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