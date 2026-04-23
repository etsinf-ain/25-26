import asyncio
import spade
import logging
from loguru import logger
from spade_bdi.bdi import BDIAgent
from spade_artifact import Artifact, ArtifactMixin

# modelo del entorno: una puerta
class Door(Artifact):
   # los métodos de lock/unlock publican el estado de la puerta 
    def lock(self):
        print("[door] update beliefs (lock)")
        asyncio.create_task(self.publish(f"locked"))

    def unlock(self):
        print("[door] update beliefs (unlock)")
        asyncio.create_task(self.publish(f"unlocked"))


# Agente que percibe la puerta
class SituatedAgent(ArtifactMixin,BDIAgent):
    def __init__(self, *args, artifact_jid: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.artifact_jid = artifact_jid
        
    # callback que genera creencia sobre el estado de la puerta
    def door_callback(self, artifact, state):
        # Eliminar la creencia door con cualquier argumento antes de añadir la nueva
        # para que el trigger +door(...) siempre se dispare
        self.bdi.remove_belief("door", "locked")
        self.bdi.remove_belief("door", "unlocked")
        # Añadir la nueva: el trigger +door(State) se disparará siempre
        self.bdi.set_belief("door", state)
    
    async def setup(self):
        await self.artifacts.focus(self.artifact_jid, self.door_callback)
        logger.info(f"{self.name} situated agent ready")


# agente con acciones externas para manejar la puerta (lock/unlock)
class RoomAgent(SituatedAgent):

   # hay que sobreescribir este métoido para añadir todas las acciones externas 
    def add_custom_actions(self, actions):
        # acción para cerrar (lock), invoca al método correspondiente de la puerta 
        @actions.add(".lock", 0)
        def _m_lock(agent, term, intention):
            print("[room agent] locking")
            self.door.lock()
            yield #para la gestión del iterador 
       # lo mismo para abrir 
        @actions.add(".unlock", 0)
        def _m_unlock(agent, term, intention):
            print("[room agent] unlocking")
            self.door.unlock() 
            yield

    def controls(self, d):
        self.door = d



async def main():
    paranoid = SituatedAgent(jid="paranoid@localhost", password="1234", asl="paranoid.asl", artifact_jid="door@localhost")
    claust = SituatedAgent(jid="claustrophobic@localhost", password="1234", asl="claust.asl", artifact_jid="door@localhost")
    porter = RoomAgent(jid="porter@localhost", password="1234", asl="porter.asl", artifact_jid="door@localhost")
    theDoor = Door("door@localhost","1234")
    # se registran los agentes que pueden percibir la puerta  
    # se asocia el agente porter con el recurso que maneja (la puerta)  
    porter.controls(theDoor)

    print("Start agents")
    await theDoor.start()
    await porter.start()
    await paranoid.start()
    await claust.start()
    # estado inicial: door locked  
    theDoor.lock()

    await asyncio.sleep(1)
    
    await paranoid.stop()
    await claust.stop()
    await porter.stop()
    # print final state of the agents
    print("**porter final beliefs")
    porter.bdi.print_beliefs()
    print("**claustr final beliefs")
    claust.bdi.print_beliefs()
    print("**paranoid final beliefs")
    paranoid.bdi.print_beliefs()
    print("Stopping agents...")


if __name__ == "__main__":
    spade.run(main())