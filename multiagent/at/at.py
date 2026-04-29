import asyncio
import spade
import agentspeak
import datetime
import re
from ast import literal_eval
from spade.behaviour import TimeoutBehaviour
from spade_bdi.bdi import BDIAgent
from spade.message import Message


    
class TimedAgent(BDIAgent):
    # Crea un comportamiento tipo Oneshot dentro de s segundos
    class TimeOut(TimeoutBehaviour):   
       # el constructor recibe el evento y el instante de tiempo 
        def __init__(self, start_at, event):
            super().__init__(start_at)
            print("complete", event)
            self.add = True if event[0] == '+' else False
            event = event[1:]
            print("event", event)
            if event[0] == '!':
                self.is_intent = True
                event = event[1:]
            else:
                self.is_intent = False
            self.event = event
            print("final", event, "intention",self.is_intent,"add",self.add)
        
        def ilf_type(self):
            if self.add:
                if self.is_intent:
                    return "achieve"
                else:
                    return "tell"
            else:
                if self.is_intent:
                    return "unachieve"
                else:
                    return "untell"

        async def run(self):
            print(f"TimeoutSenderBehaviour running at {datetime.datetime.now().time()}")
            print(f"event: {self.event}")
            # crea un mensaje para añadir una creencia
            ilf = self.ilf_type()
            mdata = {
                    "performative": "BDI",
                    "ilf_type": ilf,
            }
            msg = Message(to=str(self.agent.jid), 
                          body=str(self.event), 
                          metadata=mdata)
            print("msg:", msg)
            # envia un mensaje tell -> genera una creencia    
            self.agent.submit(self.send(msg))


    def add_custom_actions(self, actions):
        # implementacion de .at como una función externa 
        @actions.add(".at", 2)
        def _m_at(agent, term, intention):
            print(f"TimeoutSenderAgent started at {datetime.datetime.now().time()}")
            args = agentspeak.grounded(term.args, intention.scope)
            secs = args[0]
            intention = args[1]
            print(f"TimedAgent: {secs} seconds")
            print(f"TimedAgent: {intention}")
            # establece cuándo se va a lanzar la tarea   
            start_at = datetime.datetime.now() + datetime.timedelta(seconds=secs)
            # crea un comportamiento, lo programa y lo añade al agente  
            b = self.TimeOut(start_at=start_at, event=intention)
            self.add_behaviour(b)
            yield 


async def main():
    at = TimedAgent("at@localhost", "1234", "at.asl")
    
    print("Starting agents...")
    await at.start()
    await asyncio.sleep(5)
    # wait for the agents to finish
    print("Waiting for agents to finish...")
    at.bdi.print_beliefs()
    await at.stop()     

if __name__ == "__main__":
    spade.run(main())