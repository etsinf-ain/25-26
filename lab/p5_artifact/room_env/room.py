import asyncio
import spade
from spade_bdi.bdi import BDIAgent

# modelo del entorno: una puerta
class Door():
    #  recibe la lista con todos los agentes en la habitación
    def __init__(self, aglist):
        self.seenby = aglist

   # los métodos de lock/unlock actualizan las creencias de los agentes 
    def lock(self):
        print("[door] update beliefs (lock)")
        for ag in self.seenby:
            ag.bdi.remove_belief("unlocked")
            ag.bdi.set_belief("locked")

    def unlock(self):
        print("[door] update beliefs (unlock)")
        for ag in self.seenby:
            ag.bdi.remove_belief("locked")
            ag.bdi.set_belief("unlocked")           


# agente con acciones externas para manejar la puerta (lock/unlock)
class RoomAgent(BDIAgent):

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
    paranoid = BDIAgent("paranoid@localhost", "1234", "paranoid.asl")
    claust = BDIAgent("claustrophobic@localhost", "1234", "claust.asl")
    porter = RoomAgent("porter@localhost", "1234", "porter.asl")
    # se registran los agentes que pueden percibir la puerta  
    theDoor = Door([paranoid, claust, porter])
    # se asocia el agente porter con el recurso que maneja (la puerta)  
    porter.controls(theDoor)

    print("Start agents")
    await porter.start()
    await paranoid.start()
    await claust.start()
    # estado inicial: door locked  
    theDoor.lock()

    await asyncio.sleep(1)
    print("**porter final beliefs")
    porter.bdi.print_beliefs()
    print("**claustr final beliefs")
    claust.bdi.print_beliefs()
    print("**paranoid final beliefs")
    paranoid.bdi.print_beliefs()
    print("Stopping agents...")
    await paranoid.stop()
    await claust.stop()
    await porter.stop()



if __name__ == "__main__":
    spade.run(main())